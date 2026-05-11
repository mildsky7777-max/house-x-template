"""
For You feed scanner — captures personalized algorithmic recommendations.

이지 mandate Day 11: "내 x의 for you로 매뉴 보면 겁나 재밌고 유익한 정보들이 많아.
그것들처럼 똑같이 내 의견달고 포스트 해도 좋지 않을까?"

For You feed = X 알고리즘이 mildsky 본인 history+orbit+interests 기반 personalized 추천.
이게 가장 relevant content + viral signal 결합.

Output: ~/x/grow/house/library/for_you/{date}.md
Used by: morning/afternoon/evening polish — pick 1-2 high-signal posts, add stance, ship.

Run hourly off-minute:
  43 6-23 * * *
"""
import asyncio
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
USER_DATA_DIR = ROOT / ".chrome-profile"
HOUSE = ROOT.parent / "house"
FOR_YOU_DIR = HOUSE / "library" / "for_you"
SEEN_FILE = HOUSE / "library" / ".for_you_seen.json"
LOG_FILE = HOUSE / "library" / ".for_you_log.json"
KST = timezone(timedelta(hours=9))


def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.load(SEEN_FILE.open()))
        except Exception:
            pass
    return set()


def save_seen(seen: set[str]):
    SEEN_FILE.open("w").write(json.dumps(list(seen)[-2000:], indent=2))


async def open_browser(p, headless: bool = True):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 1100},
    )


async def scrape_for_you(page) -> list[dict]:
    """Scrape For You home feed."""
    out = []
    try:
        await page.goto("https://x.com/home", wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        # Make sure For You tab selected (vs Following)
        try:
            for_you_tab = page.locator('a[role="tab"]:has-text("For you"), a[role="tab"]:has-text("추천")').first
            if await for_you_tab.count():
                await for_you_tab.click()
                await page.wait_for_timeout(1500)
        except Exception:
            pass

        # Scroll + collect
        for _ in range(5):
            articles = page.locator('article[role="article"]')
            cnt = await articles.count()
            for i in range(min(cnt, 30)):
                try:
                    art = articles.nth(i)
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

                    # Skip own posts
                    if handle.lower() == "YOUR_HANDLE":
                        continue

                    # Text
                    text = ""
                    try:
                        text_el = art.locator('div[data-testid="tweetText"]').first
                        if await text_el.count():
                            text = (await text_el.inner_text())[:600]
                    except Exception:
                        pass

                    # Skip very short / RT / pure media
                    if not text or len(text) < 40:
                        continue

                    # Verified (likely higher quality / algorithm trust)
                    verified = await art.locator('svg[data-testid="icon-verified"]').count() > 0

                    # Engagement signals (engagement_count if visible)
                    engagement = ""
                    try:
                        replies = art.locator('button[data-testid="reply"]').first
                        if await replies.count():
                            label = await replies.get_attribute("aria-label") or ""
                            engagement = label[:60]
                    except Exception:
                        pass

                    out.append({
                        "handle": handle,
                        "verified": verified,
                        "text": text,
                        "url": url,
                        "engagement_hint": engagement,
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                    })
                except Exception:
                    continue
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(2000)
    except Exception as e:
        print(f"  ! for_you scrape: {e}", file=sys.stderr)
    return out


def write_for_you_md(items: list[dict]) -> Path:
    FOR_YOU_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")
    f = FOR_YOU_DIR / f"{date_str}.md"

    if not f.exists():
        f.write_text(
            f"# For You feed — {date_str} (KST)\n\n"
            f"_Hourly capture by for_you_scanner.py. mildsky's personalized X algorithmic recommendations._\n"
            f"_Used by polish tasks: pick 1-2 high-signal posts, add stance, ship._\n\n"
        )

    block = [f"\n## Capture at {now.strftime('%H:%M KST')}\n\n"]
    block.append(f"### {len(items)} posts (verified marked ✓)\n\n")

    for p in items[:25]:
        v = " ✓" if p["verified"] else ""
        block.append(f"- @{p['handle']}{v} — {p['text'][:200]!r}\n")
        block.append(f"  → {p['url']}\n")
    block.append("\n---\n")

    with f.open("a") as fh:
        fh.write("".join(block))
    return f


def log_run(n: int, error: str | None = None):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        "captured": n,
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
    posts = []

    async with async_playwright() as pw:
        ctx = await open_browser(pw, headless=not args.headed)
        page = await ctx.new_page()
        try:
            print("  scraping For You feed...")
            posts = await scrape_for_you(page)
        except Exception as e:
            log_run(0, error=str(e))
            print(f"✗ scrape error: {e}", file=sys.stderr)
            await ctx.close()
            sys.exit(1)
        finally:
            try:
                await ctx.close()
            except Exception:
                pass

    new_posts = [p for p in posts if p["url"] not in seen]
    for p in new_posts:
        seen.add(p["url"])

    print(f"  For You posts: {len(new_posts)} new / {len(posts)} total")

    if args.dry_run:
        for p in new_posts[:8]:
            v = "✓" if p["verified"] else " "
            print(f"    [{v}] @{p['handle']} {p['text'][:80]}")
        return

    if new_posts:
        f = write_for_you_md(new_posts)
        save_seen(seen)
        print(f"  ✓ wrote to {f}")

    log_run(len(new_posts))


if __name__ == "__main__":
    asyncio.run(main())
