"""
Mass-unfollow non-verified accounts (rate-limited, resumable).

Phase 1: scrape /following list with verified status (saves to following_snapshot.json).
Phase 2: iterate non-verified accounts, click Unfollow, wait 80-120s between, log to unfollow_log.json.

Run with:
    python unfollow.py snapshot       # build the list
    python unfollow.py run            # execute unfollows (rate-limited)
    python unfollow.py run --max 50   # cap at 50 this session
    python unfollow.py status         # show progress

Safety:
    - Default rate: 1 unfollow every 80-120s (≈ 30-45/hour)
    - Daily soft cap: 200 unfollows
    - Resumable: skips already-unfollowed accounts
    - Logs every action with timestamp
"""
import asyncio
import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright, Page

ROOT = Path(__file__).parent
USER_DATA_DIR = ROOT / ".chrome-profile"
SNAPSHOT_FILE = ROOT / "following_snapshot.json"
LOG_FILE = ROOT / "unfollow_log.json"

PROFILE_URL = "https://x.com/YOUR_HANDLE"
FOLLOWING_URL = f"{PROFILE_URL}/following"

DAILY_SOFT_CAP = 200
MIN_DELAY = 80
MAX_DELAY = 120


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_log() -> dict:
    if not LOG_FILE.exists():
        return {"unfollowed": [], "errors": [], "started_at": None, "last_action_at": None}
    with LOG_FILE.open() as f:
        return json.load(f)


def _save_log(log: dict):
    with LOG_FILE.open("w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


async def _open_browser(p):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=False,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )


async def snapshot_following(max_scrolls: int = 200) -> dict:
    """
    Scrape the /following page and collect (handle, name, verified) for each account.
    Returns dict {handles: [list], by_handle: {handle: {...}}}
    """
    print(f"\n  → Snapshotting {FOLLOWING_URL}")
    seen = {}
    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()
        await page.goto(FOLLOWING_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        last_count = 0
        stable_rounds = 0
        for scroll_i in range(max_scrolls):
            # Each follow row: data-testid="UserCell"
            cards = page.locator('[data-testid="UserCell"]')
            count = await cards.count()
            for i in range(count):
                card = cards.nth(i)
                try:
                    # Handle: <span>@handle</span>
                    handle_el = card.locator('a[role="link"][href^="/"]').first
                    href = await handle_el.get_attribute("href")
                    if not href:
                        continue
                    handle = href.lstrip("/").split("/")[0]
                    if handle in seen:
                        continue
                    # Verified: presence of svg[aria-label="Verified account"] or data-testid="icon-verified"
                    verified_el = card.locator('svg[data-testid="icon-verified"]')
                    is_verified = (await verified_el.count()) > 0
                    # Display name (best effort)
                    name_el = card.locator('a[role="link"] span span').first
                    try:
                        name = (await name_el.inner_text()) or ""
                    except Exception:
                        name = ""
                    # "Follows you" indicator
                    follows_you_el = card.locator('text=Follows you')
                    follows_you = (await follows_you_el.count()) > 0

                    seen[handle] = {
                        "handle": handle,
                        "name": name.strip(),
                        "verified": is_verified,
                        "follows_you": follows_you,
                    }
                except Exception:
                    continue

            # Stop if no new accounts loaded after 3 scrolls
            if len(seen) == last_count:
                stable_rounds += 1
                if stable_rounds >= 3:
                    print(f"  ✓ Reached end at {len(seen)} accounts")
                    break
            else:
                stable_rounds = 0
            last_count = len(seen)

            # Scroll down
            await page.evaluate("window.scrollBy(0, 1500)")
            await page.wait_for_timeout(1200)
            if scroll_i % 10 == 0:
                print(f"    scroll {scroll_i+1}: {len(seen)} accounts collected")

        await ctx.close()

    handles = sorted(seen.keys())
    snapshot = {
        "captured_at": _now(),
        "total": len(handles),
        "verified": sum(1 for h in seen.values() if h["verified"]),
        "non_verified": sum(1 for h in seen.values() if not h["verified"]),
        "follows_you": sum(1 for h in seen.values() if h["follows_you"]),
        "handles": handles,
        "by_handle": seen,
    }
    with SNAPSHOT_FILE.open("w") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"\n  ✓ Saved snapshot: {SNAPSHOT_FILE}")
    print(f"    Total following: {snapshot['total']}")
    print(f"    Verified:        {snapshot['verified']}")
    print(f"    Non-verified:    {snapshot['non_verified']}")
    print(f"    Follows you:     {snapshot['follows_you']}")
    return snapshot


async def _unfollow_one(page: Page, handle: str) -> tuple[bool, str]:
    """Visit a profile and click the Following button + Unfollow confirm."""
    try:
        await page.goto(f"https://x.com/{handle}", wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)
        # Following button on profile shows current state
        btn = page.locator('[data-testid$="-unfollow"]').first
        if await btn.count() == 0:
            return False, "not_following"
        await btn.click()
        await page.wait_for_timeout(800)
        # Confirm dialog with "Unfollow" red button
        confirm = page.locator('[data-testid="confirmationSheetConfirm"]').first
        if await confirm.count() == 0:
            return False, "confirm_missing"
        await confirm.click()
        await page.wait_for_timeout(1500)
        return True, "ok"
    except Exception as e:
        return False, f"exception:{type(e).__name__}:{str(e)[:80]}"


async def run_unfollow(max_session: int | None = None, include_follows_you: bool = True):
    """
    Iterate non-verified accounts and unfollow them at safe rate.
    """
    if not SNAPSHOT_FILE.exists():
        print("✗ No snapshot. Run: python unfollow.py snapshot")
        return

    with SNAPSHOT_FILE.open() as f:
        snap = json.load(f)
    log = _load_log()
    if log["started_at"] is None:
        log["started_at"] = _now()

    already = {r["handle"] for r in log["unfollowed"]}
    targets = [
        h for h, info in snap["by_handle"].items()
        if not info["verified"]
        and h not in already
        and (include_follows_you or not info["follows_you"])
    ]
    print(f"\n  Targets queued: {len(targets)} non-verified accounts")
    print(f"  Already unfollowed (prior runs): {len(already)}")
    if max_session:
        targets = targets[:max_session]
        print(f"  This session cap: {max_session}")
    print(f"  Daily soft cap: {DAILY_SOFT_CAP}\n")

    today = datetime.now(timezone.utc).date().isoformat()
    today_count = sum(
        1 for r in log["unfollowed"]
        if r["at"].startswith(today)
    )
    if today_count >= DAILY_SOFT_CAP:
        print(f"  ⚠ Daily cap {DAILY_SOFT_CAP} already hit ({today_count} today). Stopping.")
        return

    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()

        for i, handle in enumerate(targets, start=1):
            if today_count >= DAILY_SOFT_CAP:
                print(f"\n  ⚠ Hit daily cap. Pausing.")
                break

            print(f"  [{i}/{len(targets)}] @{handle}…", end=" ", flush=True)
            ok, msg = await _unfollow_one(page, handle)
            entry = {"handle": handle, "at": _now(), "ok": ok, "msg": msg}
            if ok:
                log["unfollowed"].append(entry)
                today_count += 1
                print(f"✓")
            else:
                log["errors"].append(entry)
                print(f"✗ {msg}")
            log["last_action_at"] = _now()
            _save_log(log)

            # Rate limit (random jitter)
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f"      sleeping {delay}s…", flush=True)
            await asyncio.sleep(delay)

        await ctx.close()

    print(f"\n  Session done. Total unfollowed: {len(log['unfollowed'])}, errors: {len(log['errors'])}")


def status():
    log = _load_log()
    print(f"\n  Total unfollowed: {len(log['unfollowed'])}")
    print(f"  Errors:           {len(log['errors'])}")
    if log["last_action_at"]:
        print(f"  Last action:      {log['last_action_at']}")
    if SNAPSHOT_FILE.exists():
        with SNAPSHOT_FILE.open() as f:
            snap = json.load(f)
        already = {r["handle"] for r in log["unfollowed"]}
        remaining = sum(
            1 for h, info in snap["by_handle"].items()
            if not info["verified"] and h not in already
        )
        print(f"  Remaining:        {remaining} non-verified to go")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["snapshot", "run", "status"])
    parser.add_argument("--max", type=int, default=None, help="Max unfollows this session")
    parser.add_argument("--skip-followers", action="store_true",
                        help="Skip accounts that follow you back (safer)")
    args = parser.parse_args()

    if args.cmd == "snapshot":
        asyncio.run(snapshot_following())
    elif args.cmd == "run":
        asyncio.run(run_unfollow(
            max_session=args.max,
            include_follows_you=not args.skip_followers,
        ))
    elif args.cmd == "status":
        status()
