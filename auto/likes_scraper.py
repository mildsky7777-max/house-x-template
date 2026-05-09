"""
Likes scraper — daily harvest of {USER}'s curated likes from X.

Why: {USER}'s likes are the highest-fidelity signal of what they find interesting.
Day 7 evidence: @cnemalek (signature pattern) + @DRzzizzozz (drift precedent)
+ @크롱 (voice exemplar / Tech Adoption WebMCP focus) all surfaced from likes.

This worker formalizes that pipeline:
  1. Daily 22:00 KST — scrape /YOUR_HANDLE/likes
  2. Dedup against ~/x/grow/house/library/likes_seen.json
  3. Save new likes to ~/x/grow/house/library/likes/{date}.md
  4. (next stage) night_briefing or daily-review Claude task analyzes

Output schema per like:
  - actor handle, display, verified
  - text (full where possible)
  - timestamp (relative like "4h" + absolute when scrapeable)
  - tweet URL
  - rough topic tag (heuristic)

Run:
  python likes_scraper.py            # scrape, save new
  python likes_scraper.py --dry-run  # show what would be saved
  python likes_scraper.py --max 30   # max likes to scan (default 20)

Cron: 0 22 * * * (daily 22:00 KST)
"""
import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from playwright.async_api import async_playwright, Page

ROOT = Path(__file__).parent
USER_DATA_DIR = ROOT / ".chrome-profile"
HOUSE = ROOT.parent / "house"
LIBRARY = HOUSE / "library"
LIKES_DIR = LIBRARY / "likes"
SEEN_FILE = LIBRARY / "likes_seen.json"
LOG_FILE = LIBRARY / "likes_scraper_log.json"

KST = timezone(timedelta(hours=9))
LIKES_URL = "https://x.com/YOUR_HANDLE/likes"


def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.load(SEEN_FILE.open()))
        except Exception:
            pass
    return set()


def save_seen(seen: set[str]):
    arr = list(seen)[-2000:]
    SEEN_FILE.open("w").write(json.dumps(arr, indent=2))


async def open_browser(p, headless: bool = True):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 1000},
        no_viewport=False,
    )


async def scrape_likes(page: Page, max_likes: int = 20) -> list[dict]:
    await page.goto(LIKES_URL, wait_until="domcontentloaded")
    await page.wait_for_timeout(4000)

    captured: list[dict] = []
    seen_urls_in_session = set()

    for scroll_i in range(6):  # up to 6 scrolls
        articles = page.locator('article[role="article"]')
        count = await articles.count()
        for i in range(count):
            if len(captured) >= max_likes:
                break
            try:
                art = articles.nth(i)
                # Get tweet URL — find the time anchor link
                time_link = art.locator('a[href*="/status/"]').first
                href = await time_link.get_attribute("href") if await time_link.count() else None
                if not href:
                    continue
                tweet_url = "https://x.com" + href if href.startswith("/") else href
                # Strip query params after /status/{id}
                m = re.match(r"(https?://x\.com/[^/]+/status/\d+)", tweet_url)
                tweet_url = m.group(1) if m else tweet_url
                if tweet_url in seen_urls_in_session:
                    continue
                seen_urls_in_session.add(tweet_url)

                # Extract handle from URL
                m_handle = re.match(r"https?://x\.com/([^/]+)/status/", tweet_url)
                handle = m_handle.group(1) if m_handle else "?"

                # Display name + verified
                user_link = art.locator('div[data-testid="User-Name"] a').first
                display = ""
                try:
                    display = (await user_link.inner_text()) if await user_link.count() else ""
                    display = display.split("\n")[0].strip()
                except Exception:
                    pass

                verified = False
                try:
                    verified = await art.locator('svg[data-testid="icon-verified"]').count() > 0
                except Exception:
                    pass

                # Tweet text
                text = ""
                try:
                    text_el = art.locator('div[data-testid="tweetText"]').first
                    if await text_el.count():
                        text = (await text_el.inner_text()).strip()
                except Exception:
                    pass

                # Relative time
                rel_time = ""
                try:
                    time_el = art.locator("time").first
                    if await time_el.count():
                        rel_time = await time_el.inner_text()
                except Exception:
                    pass

                captured.append({
                    "handle": handle,
                    "display": display,
                    "verified": verified,
                    "text": text[:600],
                    "url": tweet_url,
                    "rel_time": rel_time,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as e:
                print(f"  ! parse error idx={i}: {e}", file=sys.stderr)

        if len(captured) >= max_likes:
            break
        # Scroll down
        await page.evaluate("window.scrollBy(0, 1200)")
        await page.wait_for_timeout(1500)

    return captured


def heuristic_topic(text: str) -> str:
    """Quick topic tag based on keywords."""
    t = text.lower()
    if any(k in t for k in ["webmcp", "mcp", "agent", "claude", "anthropic", "openai", "gpt", "llm", "ai", "에이전트"]):
        return "ai-tech"
    if any(k in t for k in ["startup", "indie", "ship", "launch", "build", "founder", "yc"]):
        return "building"
    if any(k in t for k in ["korea", "korean", "한국", "YOUR_LOCATION", "서울"]):
        return "korea"
    if any(k in t for k in ["follower", "engagement", "viral", "post", "thread", "audience"]):
        return "growth"
    return "general"


def write_likes_md(today: date, items: list[dict]) -> Path:
    LIKES_DIR.mkdir(parents=True, exist_ok=True)
    f = LIKES_DIR / f"{today.isoformat()}.md"
    if not f.exists():
        f.write_text(f"# Likes captured — {today.isoformat()}\n\n*KST date. Scraped by likes_scraper.py.*\n\n")

    block = ["\n## Capture at " + datetime.now(KST).strftime("%H:%M KST") + "\n\n"]
    for it in items:
        verified = " ✓" if it["verified"] else ""
        topic = heuristic_topic(it["text"])
        block.append(f"### @{it['handle']} ({it['display']}{verified}) — {it['rel_time']}\n")
        block.append(f"**topic:** {topic}\n\n")
        if it["text"]:
            block.append(f"> {it['text']}\n\n")
        block.append(f"<{it['url']}>\n\n")
        block.append("---\n\n")

    with f.open("a") as fh:
        fh.write("".join(block))
    return f


def log_run(captured: int, new: int, error: str | None = None):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        "captured": captured,
        "new": new,
        "error": error,
    })
    log["runs"] = log["runs"][-100:]
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=20)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--headed", action="store_true", help="show browser (default headless)")
    args = p.parse_args()

    seen = load_seen()
    today = datetime.now(KST).date()

    async with async_playwright() as pw:
        ctx = await open_browser(pw, headless=not args.headed)
        page = await ctx.new_page()
        try:
            captured = await scrape_likes(page, max_likes=args.max)
        except Exception as e:
            log_run(0, 0, error=str(e))
            print(f"✗ scrape failed: {e}", file=sys.stderr)
            await ctx.close()
            sys.exit(1)
        finally:
            try:
                await ctx.close()
            except Exception:
                pass

    new_items = [it for it in captured if it["url"] not in seen]
    print(f"Scraped {len(captured)} likes; {len(new_items)} new.")

    if args.dry_run:
        for it in new_items:
            print(f"  + @{it['handle']} {it['rel_time']:>5s} — {it['text'][:80]}")
        return

    if new_items:
        f = write_likes_md(today, new_items)
        for it in new_items:
            seen.add(it["url"])
        save_seen(seen)
        print(f"  ✓ wrote {len(new_items)} new likes to {f}")
    log_run(len(captured), len(new_items))


if __name__ == "__main__":
    asyncio.run(main())
