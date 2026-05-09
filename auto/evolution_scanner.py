"""
Evolution scanner — capture X posts about AI / agents / builders that we should
LEARN FROM. Output → library/evolution/{date}.md for tomorrow's morning polish.

Closes {USER} mandate Day 11: "X에 ai 관련 정보들 너무 많아. 왜 스스로 공부 안해?
공부하고 포스트 올리고 스스로 진화하고. 공부하는 과정도 포스트 하고."

Scope:
  - Top verified AI builder posts last 24h (engagement-weighted)
  - Specific accounts we follow (yacineMTB, tszzl, swyx, levelsio, amasad, etc.)
  - Search-based: "claude code" / "agentic engineering" / "ai agent" trending

Output: ~/x/grow/house/library/evolution/{date}.md
Used by: morning polish task to draft 1-2 learn-in-public posts daily.

Run via cron hourly during waking (06-23 KST):
  23 6-23 * * *  (off-minute, after x_trends_scanner)
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
EVO_DIR = HOUSE / "library" / "evolution"
SEEN_FILE = HOUSE / "library" / ".evolution_seen.json"
LOG_FILE = HOUSE / "library" / ".evolution_log.json"
KST = timezone(timedelta(hours=9))

# Accounts to monitor for learn-from material
ORBIT_ACCOUNTS = [
    # AI builders
    "yacineMTB", "tszzl", "swyx", "marc_louvion", "levelsio", "amasad",
    "dvassallo", "ThePrimeagen", "cocktailpeanut", "marckohlbrugge",
    "nowlovepan", "Krongggggg", "haaaaanna__", "gimhyeo02389130",
    "mad_dogdebt", "AndrejKarpathy", "claudeai", "anthropicai",
    # Day 11: geopolitics + world events
    "Reuters", "AP", "BBCBreaking", "FT", "WSJ",
    "ianbremmer", "annapplebaum", "RnaudBertrand", "MarioNawfal",
    "DavidSacks", "elonmusk",
    # Markets / macro
    "KobeissiLetter", "zerohedge",
]

# Search terms — what topics we want to learn from
SEARCH_QUERIES = [
    # AI builder
    "claude code tip",
    "agentic engineering",
    "ai builder receipt",
    "cron mistake",
    "vibe coding",
    "agent loop",
    # Day 11: world events + geopolitics
    "trump policy",
    "fed rate",
    "ukraine ceasefire",
    "china tech",
    "korea election",
    "ai regulation",
]


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
        viewport={"width": 1280, "height": 1000},
    )


async def scrape_handle(page, handle: str, max_n: int = 5) -> list[dict]:
    """Capture recent high-engagement posts from one handle."""
    out = []
    try:
        await page.goto(f"https://x.com/{handle}", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        articles = page.locator('article[role="article"]')
        cnt = await articles.count()
        for i in range(min(cnt, 10)):
            try:
                art = articles.nth(i)
                # Get tweet URL
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
                # Text
                text = ""
                try:
                    text_el = art.locator('div[data-testid="tweetText"]').first
                    if await text_el.count():
                        text = (await text_el.inner_text())[:600]
                except Exception:
                    pass
                # Skip retweets / quote-only / very short
                if not text or len(text) < 30:
                    continue
                out.append({
                    "handle": handle,
                    "text": text,
                    "url": url,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                })
                if len(out) >= max_n:
                    break
            except Exception:
                continue
    except Exception as e:
        print(f"  ! {handle}: {e}", file=sys.stderr)
    return out


async def scrape_search(page, query: str, max_n: int = 5) -> list[dict]:
    """Capture recent results for a search query."""
    out = []
    try:
        url = f"https://x.com/search?q={query.replace(' ', '%20')}&src=typed_query&f=live"
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3500)
        articles = page.locator('article[role="article"]')
        cnt = await articles.count()
        for i in range(min(cnt, 15)):
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
                p_url = "https://x.com" + m.group(1)
                handle = href.split("/")[1]
                # Verified filter — keep only verified
                verified = await art.locator('svg[data-testid="icon-verified"]').count() > 0
                if not verified:
                    continue
                text = ""
                try:
                    text_el = art.locator('div[data-testid="tweetText"]').first
                    if await text_el.count():
                        text = (await text_el.inner_text())[:600]
                except Exception:
                    pass
                if not text or len(text) < 50:
                    continue
                out.append({
                    "handle": handle,
                    "text": text,
                    "url": p_url,
                    "query": query,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                })
                if len(out) >= max_n:
                    break
            except Exception:
                continue
    except Exception as e:
        print(f"  ! search '{query}': {e}", file=sys.stderr)
    return out


def write_evolution_md(orbit: list[dict], search: list[dict]) -> Path:
    EVO_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")
    f = EVO_DIR / f"{date_str}.md"

    if not f.exists():
        f.write_text(
            f"# Evolution Capture — {date_str} (KST)\n\n"
            f"_Hourly capture by evolution_scanner.py. Used by morning polish to "
            f"draft 1-2 learn-in-public posts daily._\n\n"
        )

    block = [f"\n## Capture at {now.strftime('%H:%M KST')}\n\n"]

    if orbit:
        block.append(f"### Orbit accounts ({len(orbit)})\n\n")
        for p in orbit[:20]:
            block.append(f"- @{p['handle']} — {p['text'][:200]!r}\n")
            block.append(f"  → {p['url']}\n")
        block.append("\n")

    if search:
        block.append(f"### Search results ({len(search)})\n\n")
        for p in search[:15]:
            block.append(f"- @{p['handle']} [q:{p['query']}] — {p['text'][:200]!r}\n")
            block.append(f"  → {p['url']}\n")
        block.append("\n")

    block.append("---\n")

    with f.open("a") as fh:
        fh.write("".join(block))
    return f


def log_run(orbit_n: int, search_n: int, error: str | None = None):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        "orbit": orbit_n,
        "search": search_n,
        "error": error,
    })
    log["runs"] = log["runs"][-200:]
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


async def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--headed", action="store_true")
    p.add_argument("--orbit-only", action="store_true",
                   help="Skip search, only orbit accounts")
    args = p.parse_args()

    seen = load_seen()
    orbit_posts = []
    search_posts = []

    async with async_playwright() as pw:
        ctx = await open_browser(pw, headless=not args.headed)
        page = await ctx.new_page()
        try:
            # Orbit
            print(f"  scraping {len(ORBIT_ACCOUNTS)} orbit accounts...")
            for h in ORBIT_ACCOUNTS:
                posts = await scrape_handle(page, h, 3)
                orbit_posts.extend(posts)

            # Search
            if not args.orbit_only:
                print(f"  scraping {len(SEARCH_QUERIES)} search queries...")
                for q in SEARCH_QUERIES:
                    posts = await scrape_search(page, q, 3)
                    search_posts.extend(posts)
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

    # Dedup
    new_orbit = [p for p in orbit_posts if p["url"] not in seen]
    new_search = [p for p in search_posts if p["url"] not in seen]
    for p in new_orbit + new_search:
        seen.add(p["url"])

    print(f"  Orbit (new): {len(new_orbit)}/{len(orbit_posts)}")
    print(f"  Search (new): {len(new_search)}/{len(search_posts)}")

    if args.dry_run:
        for p in new_orbit[:5]:
            print(f"    O @{p['handle']} {p['text'][:80]}")
        for p in new_search[:5]:
            print(f"    S @{p['handle']} {p['text'][:80]}")
        return

    if new_orbit or new_search:
        f = write_evolution_md(new_orbit, new_search)
        save_seen(seen)
        print(f"  ✓ wrote to {f}")

    log_run(len(new_orbit), len(new_search))


if __name__ == "__main__":
    asyncio.run(main())
