"""
Auto engager — automatically react to incoming engagement.

Reads engagement.json for new events. For each new event from a verified actor:
  - "follow" → follow back (if not already)
  - "like"   → like one of their recent posts (if not already engaged)
  - "reply"  → like the reply (gentle reciprocity, no auto-reply)

State: auto_engaged.json (idempotent — won't re-engage same actor in 24h).
Rate-limited: 60-90s between actions.

Usage:
    python auto_engager.py            # one-shot
    python auto_engager.py --watch    # repeat every 20 min
"""
import asyncio
import argparse
import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from playwright.async_api import async_playwright, Page

ROOT = Path(__file__).parent
USER_DATA_DIR = ROOT / ".chrome-profile"
ENGAGEMENT_FILE = ROOT / "engagement.json"
STATE_FILE = ROOT / "auto_engaged.json"

MIN_DELAY = 60
MAX_DELAY = 90
SKIP_RECENT_HOURS = 24
LOOKBACK_MINUTES = 90  # only react to events seen in last N min
WATCH_INTERVAL_MIN = 20


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {"engaged": {}}
    with STATE_FILE.open() as f:
        return json.load(f)


def _save_state(s: dict):
    with STATE_FILE.open("w") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


def _load_events() -> list[dict]:
    if not ENGAGEMENT_FILE.exists():
        return []
    with ENGAGEMENT_FILE.open() as f:
        return json.load(f).get("events", [])


def _was_recently_engaged(state: dict, handle: str, action: str) -> bool:
    key = f"{handle}:{action}"
    last = state["engaged"].get(key)
    if not last:
        return False
    try:
        last_dt = datetime.fromisoformat(last)
        return (datetime.now(timezone.utc) - last_dt) < timedelta(hours=SKIP_RECENT_HOURS)
    except Exception:
        return False


def _mark_engaged(state: dict, handle: str, action: str, ok: bool, note: str = ""):
    key = f"{handle}:{action}"
    state["engaged"][key] = _now()
    state.setdefault("log", []).append({
        "handle": handle, "action": action, "at": _now(),
        "ok": ok, "note": note,
    })


def pick_targets(events: list[dict], state: dict) -> list[dict]:
    """Pick fresh verified events to engage with, deduped per (handle, action)."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=LOOKBACK_MINUTES)
    targets = []
    seen_pairs = set()
    for ev in events:
        if not ev.get("actor_verified"):
            continue
        h = ev.get("actor_handle", "")
        if not h or h.lower() == "YOUR_HANDLE":
            continue
        etype = ev.get("type", "")
        # Map to action
        if etype == "follow":
            action = "follow_back"
        elif etype == "like":
            action = "like_recent"
        elif etype == "reply":
            action = "like_reply"
        else:
            continue

        # Skip if recently engaged (same action)
        if _was_recently_engaged(state, h, action):
            continue
        # Skip duplicates within this batch
        pair = (h, action)
        if pair in seen_pairs:
            continue

        # Freshness check via seen_at
        try:
            ev_dt = datetime.fromisoformat(ev.get("first_seen_at", ""))
            if ev_dt < cutoff:
                continue
        except Exception:
            continue

        seen_pairs.add(pair)
        targets.append({**ev, "action": action})
    return targets


async def _open_browser(p):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=False,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )


async def do_follow_back(page: Page, handle: str) -> tuple[bool, str]:
    try:
        await page.goto(f"https://x.com/{handle}", wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)
        following = page.locator('[data-testid$="-unfollow"]').first
        if await following.count() > 0:
            return False, "already_following"
        follow_btn = page.locator('[data-testid$="-follow"]').first
        if await follow_btn.count() == 0:
            return False, "no_follow_button"
        await follow_btn.click()
        await page.wait_for_timeout(1000)
        return True, "ok"
    except Exception as e:
        return False, f"exc:{type(e).__name__}"


async def do_like_recent(page: Page, handle: str) -> tuple[bool, str]:
    try:
        await page.goto(f"https://x.com/{handle}", wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)
        articles = page.locator('article[data-testid="tweet"]')
        count = await articles.count()
        for i in range(min(count, 3)):  # try first 3
            art = articles.nth(i)
            like_btn = art.locator('button[data-testid="like"]').first
            if await like_btn.count() == 0:
                continue
            if not await like_btn.is_visible():
                continue
            await like_btn.click()
            await page.wait_for_timeout(800)
            return True, "ok"
        return False, "no_likeable_post"
    except Exception as e:
        return False, f"exc:{type(e).__name__}"


async def do_like_reply(page: Page, handle: str, target_preview: str) -> tuple[bool, str]:
    """Best-effort: visit replies to YOUR_HANDLE from this handle and like the most recent."""
    try:
        # Search for replies from this handle to us
        url = f"https://x.com/search?q=from%3A{handle}+to%3AYOUR_HANDLE&f=live"
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)
        articles = page.locator('article[data-testid="tweet"]')
        count = await articles.count()
        if count == 0:
            return False, "no_results"
        art = articles.nth(0)
        like_btn = art.locator('button[data-testid="like"]').first
        if await like_btn.count() == 0:
            return False, "no_like_button"
        if not await like_btn.is_visible():
            return False, "like_not_visible"
        await like_btn.click()
        await page.wait_for_timeout(800)
        return True, "ok"
    except Exception as e:
        return False, f"exc:{type(e).__name__}"


async def run_once():
    events = _load_events()
    state = _load_state()
    targets = pick_targets(events, state)
    if not targets:
        print("  No fresh verified events to react to.")
        return

    print(f"\n  Processing {len(targets)} targets:")
    for t in targets[:10]:
        print(f"    {t['action']:14s} @{t['actor_handle']}")
    print()

    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()
        for i, t in enumerate(targets, start=1):
            h = t["actor_handle"]
            a = t["action"]
            print(f"  [{i}/{len(targets)}] {a:14s} @{h}…", end=" ", flush=True)
            if a == "follow_back":
                ok, msg = await do_follow_back(page, h)
            elif a == "like_recent":
                ok, msg = await do_like_recent(page, h)
            elif a == "like_reply":
                ok, msg = await do_like_reply(page, h, t.get("target_preview", ""))
            else:
                ok, msg = False, "unknown_action"
            print(f"{'✓' if ok else '✗'} {msg}")
            _mark_engaged(state, h, a, ok, msg)
            _save_state(state)
            if i < len(targets):
                delay = random.randint(MIN_DELAY, MAX_DELAY)
                await asyncio.sleep(delay)
        await ctx.close()
    print(f"\n  Done. Total engaged actions logged: {len(state.get('log', []))}")


async def watch():
    while True:
        try:
            print(f"\n[{_now()}] auto_engager tick")
            await run_once()
        except Exception as e:
            print(f"  ! tick error: {type(e).__name__}: {e}")
        print(f"\n  Sleeping {WATCH_INTERVAL_MIN} min…\n")
        await asyncio.sleep(WATCH_INTERVAL_MIN * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.status:
        s = _load_state()
        print(f"Total engaged: {len(s.get('engaged', {}))}")
        for entry in (s.get('log', []) or [])[-10:]:
            print(f"  {entry['at'][:19]}  {entry['action']:14s} @{entry['handle']:25s} {entry['note']}")
    elif args.watch:
        asyncio.run(watch())
    else:
        asyncio.run(run_once())
