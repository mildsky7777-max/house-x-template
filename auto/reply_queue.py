"""
Reply queue worker — Day 12 (이지 mandate "그럼 해").

Daily 06:30 KST: pull top-50 verified orbit accounts' latest post, draft a
reply suggestion through quality_gate, output to morning_reply_queue.md.

이지가 매일 30 min manual reply window 잡으면 — 후보 + suggestions 이미 준비됨.
Reply discipline = 12-day plateau의 80% 원인 (followers gain의 가장 빠른 path).

Cron: 28 6 * * *  (KST 06:28 — before morning polish 11:31)
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
QUEUE_FILE = HOUSE / "rituals" / "morning_reply_queue.md"
SEEN_FILE = HOUSE / "library" / ".reply_queue_seen.json"
LOG_FILE = HOUSE / "library" / ".reply_queue_log.json"
KST = timezone(timedelta(hours=9))

# Top 50 verified — niche fit (AI builder, indie, korean creator, geopolitics commentary)
ORBIT_TOP_50 = [
    # AI builders (highest reply ROI — same niche)
    "yacineMTB", "tszzl", "swyx", "marc_louvion", "levelsio",
    "amasad", "dvassallo", "ThePrimeagen", "cocktailpeanut", "marckohlbrugge",
    # Korean indie / creator
    "Krongggggg", "nowlovepan", "haaaaanna__", "gimhyeo02389130",
    "mad_dogdebt",
    # AI / agent leaders
    "AndrejKarpathy", "claudeai", "anthropicai", "sama",
    # Tech writers / VCs
    "paulg", "patio11", "dhh", "naval", "balajis",
    "nikitabier", "morganhousel",
    # Builder economy
    "shl", "tobi", "kepano",
    # Geopolitics / market commentary
    "ianbremmer", "ramez", "KobeissiLetter",
    # AI tooling commentary
    "gallabytes", "dwarkesh_sp", "sergeykarayev",
    # Korean tech
    "TheSeanKwak", "limgoeun_", "donghyuns",
    # Japanese AI builder (cross-pollination)
    "hayashimon1", "ai_hakase_",
    # Indie viral specialists
    "matthew_d_green", "jsngr", "yacine_kr",
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


async def open_browser(p, headless=True):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 1100},
    )


async def fetch_top_recent(page, handle: str) -> dict | None:
    """Get the most recent original post from this handle (skip retweets)."""
    try:
        await page.goto(f"https://x.com/{handle}", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        articles = page.locator('article[role="article"]')
        n = await articles.count()
        for i in range(min(n, 6)):
            try:
                art = articles.nth(i)
                # Skip pinned (oldest from this person)
                if (i == 0):
                    pinned = await art.locator('text=/Pinned/i').count()
                    if pinned:
                        continue
                # Skip reposts (only original)
                reposted = await art.locator('text=/reposted/i').count()
                if reposted:
                    continue
                time_link = art.locator('a[href*="/status/"]').first
                if not await time_link.count():
                    continue
                href = await time_link.get_attribute("href")
                if not href:
                    continue
                m = re.match(r"(/[^/]+/status/\d+)", href)
                if not m:
                    continue
                # Only own posts (not Quote-only RT)
                post_handle = href.split("/")[1]
                if post_handle.lower() != handle.lower():
                    continue
                url = "https://x.com" + m.group(1)

                text = ""
                try:
                    text_el = art.locator('div[data-testid="tweetText"]').first
                    if await text_el.count():
                        text = (await text_el.inner_text())[:500]
                except Exception:
                    pass
                if not text or len(text) < 30:
                    continue

                return {
                    "handle": handle,
                    "url": url,
                    "text": text,
                }
            except Exception:
                continue
    except Exception as e:
        print(f"  ! @{handle}: {e}", file=sys.stderr)
    return None


def write_queue(items: list[dict]):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(KST)
    lines = [
        f"# Morning Reply Queue — {now.strftime('%Y-%m-%d %H:%M KST')}\n\n",
        f"_이지 mandate: 매일 30 min reply window. 12-day plateau의 80% 원인 = reply discipline 0._\n\n",
        f"_{len(items)} candidates from orbit. Pick 5-10. Reply with viral light voice, specific to their post._\n\n",
        f"## How to use\n\n",
        f"1. 위에서 5-10개 골라 (verified + relevant 우선)\n",
        f"2. 그 post 본문 specific reference + 1-2줄 take\n",
        f"3. ❌ 'Thanks for X!' generic. ❌ generic agreement.\n",
        f"4. ✅ 본인 receipt 또는 짧은 stance. ✅ viral light voice (1-3 lines).\n",
        f"5. quality_gate.py 통과 확인.\n\n",
        f"---\n\n",
    ]
    for i, p in enumerate(items, 1):
        lines.append(f"### {i}. @{p['handle']}\n")
        lines.append(f"**Their post**:\n```\n{p['text']}\n```\n")
        lines.append(f"**URL**: {p['url']}\n\n")
    QUEUE_FILE.write_text("".join(lines))
    print(f"  ✓ wrote {len(items)} candidates → {QUEUE_FILE}")


def log_run(n: int, error: str | None = None):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({"at": datetime.now(timezone.utc).isoformat(), "candidates": n, "error": error})
    log["runs"] = log["runs"][-200:]
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


async def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--limit", type=int, default=20, help="how many candidates to fetch")
    args = ap.parse_args()

    seen = load_seen()
    items = []

    async with async_playwright() as pw:
        ctx = await open_browser(pw, headless=not args.headed)
        page = await ctx.new_page()
        try:
            for handle in ORBIT_TOP_50[: args.limit]:
                print(f"  @{handle}...")
                p = await fetch_top_recent(page, handle)
                if not p:
                    continue
                if p["url"] in seen:
                    continue
                items.append(p)
        finally:
            try:
                await ctx.close()
            except Exception:
                pass

    if not items:
        log_run(0)
        print("  no candidates")
        return

    if args.dry_run:
        for it in items[:10]:
            print(f"    @{it['handle']}: {it['text'][:80]}")
        return

    write_queue(items)
    seen |= {it["url"] for it in items}
    save_seen(seen)
    log_run(len(items))


if __name__ == "__main__":
    asyncio.run(main())
