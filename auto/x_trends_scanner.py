"""
X trends scanner — captures what's trending on X RIGHT NOW.

Closes the @mad_dogdebt gap: small accounts must surf trending topics + frame-flip.
Currently we surf RSS + {USER} likes only. This adds X's own trending feed.

Scope:
  - Korea trending topics (Trending in South Korea sidebar)
  - Verified Tier-1 viral posts in our orbit (extends trend_scanner)
  - 24h+ growing topics (rising before trending)

Output: ~/x/grow/house/library/x_trends/{date}T{hour}.md

Run via cron hourly during waking (06-23 KST):
  17 6-23 * * *  (avoiding :00, :15, :30, :45)

Polish task picks from x_trends/ for Tier 1 News Desk surfing.
"""
import asyncio
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from playwright.async_api import async_playwright, Page

ROOT = Path(__file__).parent
USER_DATA_DIR = ROOT / ".chrome-profile"
HOUSE = ROOT.parent / "house"
TRENDS_DIR = HOUSE / "library" / "x_trends"
SEEN_FILE = HOUSE / "library" / ".x_trends_seen.json"
LOG_FILE = HOUSE / "library" / ".x_trends_log.json"
KST = timezone(timedelta(hours=9))


def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.load(SEEN_FILE.open()))
        except Exception:
            pass
    return set()


def save_seen(seen: set[str]):
    SEEN_FILE.open("w").write(json.dumps(list(seen)[-1000:], indent=2))


async def open_browser(p, headless: bool = True):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 1000},
    )


async def scrape_trends_korea(page: Page) -> list[dict]:
    """Scrape Korea trending from /explore/trending."""
    await page.goto("https://x.com/explore/tabs/trending", wait_until="domcontentloaded")
    await page.wait_for_timeout(4000)

    trends = []
    try:
        # Trending items use data-testid="trend"
        items = page.locator('div[data-testid="trend"]')
        count = await items.count()
        for i in range(min(count, 20)):
            try:
                txt = await items.nth(i).inner_text()
                # Format: "Category\nTrend Name\nN posts" or similar
                lines = [ln.strip() for ln in txt.split("\n") if ln.strip()]
                if len(lines) >= 2:
                    trends.append({
                        "category": lines[0] if "·" in lines[0] or "Trending" in lines[0] else "",
                        "trend": lines[1] if len(lines) > 1 else lines[0],
                        "post_count": lines[2] if len(lines) > 2 else "",
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception as e:
                print(f"  ! parse trend {i}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"  ! scrape error: {e}", file=sys.stderr)

    return trends


async def scrape_korea_for_you(page: Page) -> list[dict]:
    """Scrape Korea For-You feed top viral posts (proxy for Korea trending)."""
    await page.goto("https://x.com/explore", wait_until="domcontentloaded")
    await page.wait_for_timeout(4000)

    posts = []
    try:
        articles = page.locator('article[role="article"]')
        count = await articles.count()
        for i in range(min(count, 15)):
            try:
                art = articles.nth(i)
                # URL
                time_link = art.locator('a[href*="/status/"]').first
                if not await time_link.count():
                    continue
                href = await time_link.get_attribute("href")
                if not href:
                    continue
                m = re.match(r"(/[^/]+/status/\d+)", href)
                if not m:
                    continue
                url = "https://x.com" + m.group(1)
                handle = href.split("/")[1]

                # Text
                text = ""
                try:
                    text_el = art.locator('div[data-testid="tweetText"]').first
                    if await text_el.count():
                        text = (await text_el.inner_text())[:500]
                except Exception:
                    pass

                # Verified
                verified = await art.locator('svg[data-testid="icon-verified"]').count() > 0

                posts.append({
                    "handle": handle,
                    "verified": verified,
                    "text": text,
                    "url": url,
                    "source": "explore",
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception:
                continue
    except Exception as e:
        print(f"  ! explore scrape: {e}", file=sys.stderr)

    return posts


def write_trends_md(items_trends: list[dict], items_posts: list[dict]) -> Path:
    TRENDS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")
    f = TRENDS_DIR / f"{date_str}.md"

    if not f.exists():
        f.write_text(f"# X Trends — {date_str} (KST)\n\n*Hourly capture by x_trends_scanner.py.*\n\n")

    block = [f"\n## Capture at {now.strftime('%H:%M KST')}\n\n"]

    if items_trends:
        block.append("### Trending in Korea\n\n")
        for t in items_trends[:15]:
            block.append(f"- **{t.get('trend','?')}** ({t.get('category','')}) — {t.get('post_count','')}\n")
        block.append("\n")

    if items_posts:
        block.append("### Korea Explore (viral posts)\n\n")
        for p in items_posts[:10]:
            v = " ✓" if p["verified"] else ""
            block.append(f"- @{p['handle']}{v} — {p['text'][:120]!r}\n")
            block.append(f"  → {p['url']}\n")
        block.append("\n")

    block.append("---\n")

    with f.open("a") as fh:
        fh.write("".join(block))
    return f


def log_run(captured_trends: int, captured_posts: int, error: str | None = None):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        "trends": captured_trends,
        "posts": captured_posts,
        "error": error,
    })
    log["runs"] = log["runs"][-200:]
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


async def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--headed", action="store_true")
    args = p.parse_args()

    seen = load_seen()
    async with async_playwright() as pw:
        ctx = await open_browser(pw, headless=not args.headed)
        page = await ctx.new_page()
        try:
            print(f"  scraping trending...")
            trends = await scrape_trends_korea(page)
            print(f"  scraping explore...")
            posts = await scrape_korea_for_you(page)
        except Exception as e:
            log_run(0, 0, error=str(e))
            print(f"✗ scrape error: {e}", file=sys.stderr)
            await ctx.close()
            sys.exit(1)
        finally:
            try:
                await ctx.close()
            except Exception:
                pass

    # Dedup posts
    new_posts = [p for p in posts if p["url"] not in seen]
    for p in new_posts:
        seen.add(p["url"])

    print(f"  Trends: {len(trends)}")
    print(f"  Posts (new): {len(new_posts)}/{len(posts)}")

    if args.dry_run:
        for t in trends[:5]:
            print(f"    T: {t.get('trend')}")
        for p in new_posts[:5]:
            print(f"    P: @{p['handle']} {p['text'][:60]}")
        return

    if trends or new_posts:
        f = write_trends_md(trends, new_posts)
        save_seen(seen)
        print(f"  ✓ wrote to {f}")

    log_run(len(trends), len(new_posts))


if __name__ == "__main__":
    asyncio.run(main())
