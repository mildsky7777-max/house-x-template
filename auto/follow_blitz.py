"""
Strategic follow blitz — follow verified AI builder accounts likely to follow back.

Sources:
  1. trend scanner targets (handles from targets.json)
  2. engagement.json verified actors not yet followed
  3. Manually curated AI Twitter list

Rate limit: 60-90s between follows (safe under Premium 1000/day cap).

Usage:
    python follow_blitz.py --max 30
    python follow_blitz.py --status
"""
import asyncio
import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright, Page

ROOT = Path(__file__).parent
USER_DATA_DIR = ROOT / ".chrome-profile"
TARGETS_FILE = ROOT / "targets.json"
ENGAGEMENT_FILE = ROOT / "engagement.json"
FOLLOWED_LOG = ROOT / "followed_blitz.json"

MIN_DELAY = 60
MAX_DELAY = 90

# Curated tier-1 AI builder list — high follow-back probability
CURATED_HANDLES = [
    "swyx", "thsottiaux", "tszzl", "packyM", "aladagberk",
    "safishamsii", "ModengSir", "mweinbach", "jankaminski94",
    "BetterStackHQ", "CausalEngineer", "andyfang",
    "DotCSV", "ErikVoorhees", "FirstSquawk",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_log() -> dict:
    if not FOLLOWED_LOG.exists():
        return {"followed": [], "errors": []}
    with FOLLOWED_LOG.open() as f:
        return json.load(f)


def _save_log(data: dict):
    with FOLLOWED_LOG.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def collect_targets(max_targets: int) -> list[str]:
    """Build prioritized handle list from multiple sources."""
    log = _load_log()
    already = {x["handle"] for x in log["followed"]}

    handles = []  # ordered, dedup

    def add(h):
        if h and h not in handles and h.lower() not in {a.lower() for a in already}:
            if h.lower() != "YOUR_HANDLE":
                handles.append(h)

    # 1. Curated tier-1
    for h in CURATED_HANDLES:
        add(h)

    # 2. Trend scanner targets (verified handles from latest scan)
    if TARGETS_FILE.exists():
        with TARGETS_FILE.open() as f:
            tj = json.load(f)
        for t in tj.get("targets", []):
            if t.get("verified"):
                add(t["handle"])

    # 3. Engagement.json verified actors who liked us — already warm
    if ENGAGEMENT_FILE.exists():
        with ENGAGEMENT_FILE.open() as f:
            ej = json.load(f)
        for ev in ej.get("events", []):
            if ev.get("actor_verified"):
                add(ev.get("actor_handle", ""))

    return handles[:max_targets]


async def _open_browser(p):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=False,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )


async def follow_one(page: Page, handle: str) -> tuple[bool, str]:
    """Visit profile, click Follow button. Returns (ok, msg)."""
    try:
        await page.goto(f"https://x.com/{handle}", wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)
        # Follow button has data-testid="<id>-follow"
        # Check if already following: data-testid ends with "-unfollow"
        following = page.locator('[data-testid$="-unfollow"]').first
        if await following.count() > 0:
            return False, "already_following"
        follow_btn = page.locator('[data-testid$="-follow"]').first
        if await follow_btn.count() == 0:
            return False, "follow_button_missing"
        await follow_btn.click()
        await page.wait_for_timeout(1200)
        return True, "ok"
    except Exception as e:
        return False, f"exception:{type(e).__name__}:{str(e)[:80]}"


async def run(max_follows: int = 30):
    targets = collect_targets(max_follows)
    if not targets:
        print("No targets to follow.")
        return

    print(f"\n  Will follow up to {len(targets)} accounts:")
    for h in targets[:20]:
        print(f"    - @{h}")
    if len(targets) > 20:
        print(f"    ... and {len(targets) - 20} more")
    print()

    log = _load_log()
    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()
        for i, h in enumerate(targets, start=1):
            print(f"  [{i}/{len(targets)}] @{h}…", end=" ", flush=True)
            ok, msg = await follow_one(page, h)
            entry = {"handle": h, "at": _now(), "ok": ok, "msg": msg}
            if ok:
                log["followed"].append(entry)
                print("✓")
            else:
                log["errors"].append(entry)
                print(f"✗ {msg}")
            _save_log(log)

            if i < len(targets):
                delay = random.randint(MIN_DELAY, MAX_DELAY)
                print(f"      sleeping {delay}s…", flush=True)
                await asyncio.sleep(delay)
        await ctx.close()
    print(f"\n  ✓ Total followed: {len(log['followed'])}, errors: {len(log['errors'])}")


def status():
    log = _load_log()
    print(f"\n  Total followed: {len(log['followed'])}")
    print(f"  Errors:         {len(log['errors'])}")
    print(f"\n  Recent follows:")
    for e in log["followed"][-10:]:
        print(f"    @{e['handle']:30s} {e['at'][:19]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=30)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.status:
        status()
    else:
        asyncio.run(run(max_follows=args.max))
