"""
Target scanner — find fresh verified Tier 1-2 reply targets via X search.

Searches X with curated keyword queries (Latest tab, Verified accounts only),
filters tweets by sweet-spot criteria, ranks them.

Output: targets.json — list of candidate tweets with metadata.

Usage:
    python trend_scanner.py            # one-shot scan
    python trend_scanner.py --watch    # rescan every 60 min
"""
import asyncio
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright, Page
from urllib.parse import quote

ROOT = Path(__file__).parent
USER_DATA_DIR = ROOT / ".chrome-profile"
TARGETS_FILE = ROOT / "targets.json"

# Searches we run. filter:verified → Premium accounts. min_faves:50 → already-engaged.
# Latest tab + min_faves filters out unprovens, keeps fresh+proven sweet spot.
QUERY_BASE = "filter:verified -filter:replies min_faves:50 lang:en"
SEARCH_TOPICS = [
    "claude code", "OpenAI Codex", "AI agent", "Anthropic", "GPT-5.5",
    "DeepSeek", "agentic", "Cursor AI", "AI builder", "Sonnet",
]
SEARCH_QUERIES = [f"{topic} {QUERY_BASE}" for topic in SEARCH_TOPICS]

# Filtering thresholds
MIN_VIEWS = 3_000
MAX_VIEWS = 200_000
MAX_REPLIES = 100
MIN_LIKES = 30
MAX_AGE_HOURS = 12  # only fresh
TWEETS_PER_QUERY = 8


def _parse_count(s: str) -> int:
    if not s:
        return 0
    s = s.replace(",", "").strip()
    m = re.match(r"([\d.]+)\s*([KMB]?)", s, re.I)
    if not m:
        return 0
    n = float(m.group(1))
    suffix = m.group(2).upper()
    mult = {"": 1, "K": 1000, "M": 1_000_000, "B": 1_000_000_000}.get(suffix, 1)
    return int(n * mult)


async def _open_browser(p, headless: bool = False):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )


async def _safe_count(loc) -> int:
    try:
        if await loc.count() == 0:
            return 0
        t = await loc.first.inner_text()
        return _parse_count(t)
    except Exception:
        return 0


def _parse_age_hours(time_str: str) -> float | None:
    """Parse '5h', '23h', '1d', '2 May' etc. Returns hours or None if old date."""
    s = (time_str or "").strip().replace("·", "").strip()
    if not s:
        return None
    m = re.match(r"(\d+)\s*([smhd])$", s, re.I)
    if m:
        n = float(m.group(1))
        unit = m.group(2).lower()
        return n * {"s": 1/3600, "m": 1/60, "h": 1, "d": 24}[unit]
    return None


async def scrape_search_tweets(page: Page, query: str, limit: int = 8) -> list[dict]:
    """Run a search query (Latest tab) and extract tweets."""
    # Latest tab with min_faves:50 → fresh + proven engagement
    url = f"https://x.com/search?q={quote(query)}&src=typed_query&f=live"
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(3500)

    # Scroll a bit to load more
    for _ in range(2):
        await page.evaluate("window.scrollBy(0, 800)")
        await page.wait_for_timeout(1000)

    tweets = []
    articles = page.locator('article[data-testid="tweet"]')
    count = await articles.count()
    for i in range(min(count, limit)):
        art = articles.nth(i)
        try:
            user_el = art.locator('div[data-testid="User-Name"]').first
            user_text = await user_el.inner_text()
            parts = [p for p in user_text.split("\n") if p.strip()]
            display_name = parts[0] if parts else ""
            handle_part = next((p for p in parts if p.startswith("@")), "")
            handle = handle_part.lstrip("@")
            time_part = parts[-1] if len(parts) > 2 else ""

            verified = (
                await art.locator('svg[data-testid="icon-verified"]').count() > 0
            )

            # Tweet text
            try:
                text = await art.locator('div[data-testid="tweetText"]').first.inner_text()
            except Exception:
                text = ""

            # Permalink
            try:
                href = await art.locator('a[href*="/status/"]').first.get_attribute("href")
                tweet_url = f"https://x.com{href}" if href and href.startswith("/") else href
                # Strip query/anchor
                if tweet_url and "?" in tweet_url:
                    tweet_url = tweet_url.split("?")[0]
                if tweet_url and "/photo/" in tweet_url:
                    tweet_url = tweet_url.split("/photo/")[0]
                if tweet_url and "/analytics" in tweet_url:
                    tweet_url = tweet_url.split("/analytics")[0]
            except Exception:
                tweet_url = None

            replies_count = await _safe_count(art.locator('[data-testid="reply"] span span'))
            retweets_count = await _safe_count(art.locator('[data-testid="retweet"] span span'))
            likes_count = await _safe_count(art.locator('[data-testid="like"] span span'))

            views_count = 0
            try:
                view_el = art.locator('a[href$="/analytics"]').first
                if await view_el.count() > 0:
                    vt = await view_el.inner_text()
                    views_count = _parse_count(vt)
            except Exception:
                pass

            tweets.append({
                "handle": handle,
                "display_name": display_name,
                "verified": verified,
                "text": text[:300],
                "tweet_url": tweet_url,
                "time": time_part,
                "replies": replies_count,
                "retweets": retweets_count,
                "likes": likes_count,
                "views": views_count,
                "query": query,
            })
        except Exception:
            continue

    return tweets


def filter_targets(tweets: list[dict]) -> list[dict]:
    out = []
    seen_urls = set()
    for t in tweets:
        if not t.get("verified"):
            continue
        url = t.get("tweet_url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        age_h = _parse_age_hours(t.get("time", ""))
        if age_h is None or age_h > MAX_AGE_HOURS:
            continue
        if t["views"] < MIN_VIEWS or t["views"] > MAX_VIEWS:
            continue
        if t["replies"] > MAX_REPLIES:
            continue
        if t["likes"] < MIN_LIKES:
            continue
        # Skip our own
        if t["handle"].lower() == "YOUR_HANDLE":
            continue
        view_score = min(t["views"] / 50_000, 1.0)
        reply_room = max(0, (MAX_REPLIES - t["replies"]) / MAX_REPLIES)
        freshness = max(0, (MAX_AGE_HOURS - age_h) / MAX_AGE_HOURS)
        engagement = min(t["likes"] / 1000, 1.0)
        t["score"] = round(view_score * 0.3 + reply_room * 0.3 + freshness * 0.2 + engagement * 0.2, 3)
        t["age_hours"] = round(age_h, 1)
        out.append(t)
    out.sort(key=lambda x: -x["score"])
    return out


async def scan(verbose: bool = True) -> dict:
    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()
        try:
            if verbose:
                print(f"[{datetime.now(timezone.utc).isoformat()}] Scanning {len(SEARCH_QUERIES)} queries…")

            all_tweets = []
            for q in SEARCH_QUERIES:
                tweets = await scrape_search_tweets(page, q, limit=TWEETS_PER_QUERY)
                if verbose:
                    print(f"  → {len(tweets):2d} tweets from: {q[:50]}")
                all_tweets.extend(tweets)

            targets = filter_targets(all_tweets)
            result = {
                "scanned_at": datetime.now(timezone.utc).isoformat(),
                "total_seen": len(all_tweets),
                "after_filter": len(targets),
                "targets": targets,
                "raw_sample": all_tweets[:10],  # debug
            }
            with TARGETS_FILE.open("w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            if verbose:
                print(f"\n  ✓ {len(all_tweets)} seen → {len(targets)} ranked targets")
                print(f"  ✓ Top 5 candidates:\n")
                for t in targets[:5]:
                    print(f"  [{t['score']}] @{t['handle']} ({t['views']:,}v / {t['replies']}r / {t['age_hours']}h)")
                    print(f"      {t['text'][:140]}")
                    print(f"      {t['tweet_url']}\n")
            return result
        finally:
            await ctx.close()


async def watch(interval_min: int = 60):
    while True:
        try:
            await scan(verbose=True)
        except Exception as e:
            print(f"  ! scan error: {type(e).__name__}: {e}")
        print(f"\n  Sleeping {interval_min} min…\n")
        await asyncio.sleep(interval_min * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args()
    if args.watch:
        asyncio.run(watch(args.interval))
    else:
        asyncio.run(scan())
