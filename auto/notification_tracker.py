"""
Notification tracker — scrape /notifications and accumulate engagement events.

Captures: follows, likes, replies, reposts.
Classifies: verified vs non-verified actor.
Output: engagement.json — append-only event log + summary.

Usage:
    python notification_tracker.py            # one-shot scrape
    python notification_tracker.py --watch    # rescrape every 15 min
    python notification_tracker.py --summary  # print current summary
"""
import asyncio
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright, Page

ROOT = Path(__file__).parent
USER_DATA_DIR = ROOT / ".chrome-profile"
LOG_FILE = ROOT / "engagement.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_log() -> dict:
    if not LOG_FILE.exists():
        return {
            "events": [],
            "first_scraped_at": None,
            "last_scraped_at": None,
        }
    with LOG_FILE.open() as f:
        return json.load(f)


def _save_log(data: dict):
    with LOG_FILE.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _event_id(actor: str, etype: str, target_preview: str, x_age: str) -> str:
    """Stable ID so we don't double-count an event across scrapes."""
    h = hashlib.sha1(f"{actor}|{etype}|{target_preview[:60]}|{x_age}".encode()).hexdigest()
    return h[:12]


async def _open_browser(p, headless: bool = False):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )


async def scrape_one_pass(page: Page, max_scrolls: int = 8) -> list[dict]:
    """Scroll through /notifications, extract event records."""
    await page.goto("https://x.com/notifications", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    events = []
    seen_ids = set()

    for scroll_i in range(max_scrolls):
        # Each notification: article[data-testid="notification"] OR similar
        # Fallback: divs that contain "liked", "followed", "replied"
        # We'll use the broader article[role="article"] within the timeline
        cards = page.locator('article[data-testid="notification"]')
        count = await cards.count()
        if count == 0:
            # Fallback selector
            cards = page.locator('[aria-label*="otification"] > div > div')
            count = await cards.count()

        for i in range(count):
            card = cards.nth(i)
            try:
                full_text = (await card.inner_text()).strip()
                if not full_text:
                    continue
                # Determine type
                lower = full_text.lower()
                if " followed you" in lower:
                    etype = "follow"
                elif " liked your " in lower or " liked " in lower and "post" in lower:
                    etype = "like"
                elif " replied to" in lower or "Replying to" in full_text:
                    etype = "reply"
                elif " reposted " in lower or " reposted your" in lower:
                    etype = "repost"
                elif " mentioned " in lower or "@YOUR_HANDLE" in lower:
                    etype = "mention"
                else:
                    continue  # skip "new post notifications" etc.

                # Extract actor handle(s) from anchor hrefs (NOT from card text — that
                # contains @YOUR_HANDLE from quoted-back posts and noise).
                # X notification cards have <a href="/{handle}"> for each actor avatar.
                hrefs = await card.evaluate(
                    """(el) => Array.from(el.querySelectorAll('a[href]'))
                        .map(a => a.getAttribute('href'))
                        .filter(h => h && /^\\/[A-Za-z0-9_]{1,15}$/.test(h))"""
                )
                # Filter out our own handle and dedup, preserve order
                actor_handles = []
                for h in hrefs:
                    handle = h.lstrip("/")
                    if handle.lower() == "YOUR_HANDLE":
                        continue
                    if handle not in actor_handles:
                        actor_handles.append(handle)
                if not actor_handles:
                    continue
                actor_handle = actor_handles[0]

                # Verified: any verified icon AT ALL in card. (We can't reliably tell
                # which actor's icon it is in a multi-actor card, but for our purposes
                # we treat the primary actor as verified if any icon is present.)
                verified = await card.locator('svg[data-testid="icon-verified"]').count()
                actor_verified = verified > 0

                # Display name = first non-empty line
                first_lines = [l for l in full_text.split("\n") if l.strip()][:2]
                actor_display = first_lines[0] if first_lines else ""

                # x_age: last token like "5m", "2h", "May 3" etc.
                age_match = re.search(r"·\s*(\d+[smhd]|[A-Z][a-z]{2}\s*\d+)\s*$", full_text.replace("\n", " "))
                x_age = age_match.group(1) if age_match else ""

                # target_preview — for like/reply, last block of card has the post text
                target_preview = ""
                if etype in ("like", "reply", "mention", "repost"):
                    # Use last 200 chars of full_text
                    target_preview = full_text[-200:].replace("\n", " ").strip()

                eid = _event_id(actor_handle, etype, target_preview, x_age)
                if eid in seen_ids:
                    continue
                seen_ids.add(eid)
                events.append({
                    "id": eid,
                    "type": etype,
                    "actor_handle": actor_handle,
                    "actor_display": actor_display,
                    "actor_verified": actor_verified,
                    "x_age": x_age,
                    "target_preview": target_preview[:200],
                    "first_seen_at": _now(),
                })
            except Exception:
                continue

        # Scroll for more
        await page.evaluate("window.scrollBy(0, 1200)")
        await page.wait_for_timeout(900)

    return events


def merge_events(log: dict, new_events: list[dict]) -> tuple[int, int]:
    """Append new events not already in log. Returns (added, duplicates)."""
    existing = {e["id"] for e in log["events"]}
    added = 0
    dup = 0
    for ev in new_events:
        if ev["id"] in existing:
            dup += 1
            continue
        log["events"].append(ev)
        existing.add(ev["id"])
        added += 1
    if log["first_scraped_at"] is None:
        log["first_scraped_at"] = _now()
    log["last_scraped_at"] = _now()
    return added, dup


def summarize(log: dict) -> dict:
    events = log["events"]
    by_type = {}
    verified_handles = set()
    nonverified_handles = set()
    follows_verified = 0
    follows_nonverified = 0
    likes_verified = 0
    likes_nonverified = 0
    replies_verified = 0

    for ev in events:
        by_type[ev["type"]] = by_type.get(ev["type"], 0) + 1
        h = ev["actor_handle"]
        if ev["actor_verified"]:
            verified_handles.add(h)
        else:
            nonverified_handles.add(h)
        if ev["type"] == "follow":
            if ev["actor_verified"]:
                follows_verified += 1
            else:
                follows_nonverified += 1
        elif ev["type"] == "like":
            if ev["actor_verified"]:
                likes_verified += 1
            else:
                likes_nonverified += 1
        elif ev["type"] == "reply":
            if ev["actor_verified"]:
                replies_verified += 1

    return {
        "total_events": len(events),
        "by_type": by_type,
        "unique_verified_actors": len(verified_handles),
        "unique_non_verified_actors": len(nonverified_handles),
        "follows": {
            "verified": follows_verified,
            "non_verified": follows_nonverified,
            "total": follows_verified + follows_nonverified,
        },
        "likes_verified": likes_verified,
        "likes_non_verified": likes_nonverified,
        "replies_verified": replies_verified,
        "monetization_progress": {
            "verified_followers_seen": follows_verified,
            "target": 500,
            "remaining": max(0, 500 - follows_verified),
        },
        "first_scraped_at": log["first_scraped_at"],
        "last_scraped_at": log["last_scraped_at"],
    }


async def scrape(verbose: bool = True) -> dict:
    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()
        try:
            if verbose:
                print(f"[{_now()}] Scraping /notifications…")
            new_events = await scrape_one_pass(page)
            if verbose:
                print(f"  → captured {len(new_events)} events this pass")
        finally:
            await ctx.close()

    log = _load_log()
    added, dup = merge_events(log, new_events)
    _save_log(log)
    summary = summarize(log)
    if verbose:
        print(f"  → {added} new, {dup} dup. Total events: {len(log['events'])}")
        print(f"\n  📊 Summary:")
        print(f"    Verified followers seen: {summary['follows']['verified']}")
        print(f"    Verified likes:          {summary['likes_verified']}")
        print(f"    Verified replies:        {summary['replies_verified']}")
        print(f"    Unique verified actors:  {summary['unique_verified_actors']}")
        print(f"    Total events captured:   {summary['total_events']}")
        print(f"    By type: {summary['by_type']}")
        print(f"\n  🎯 Monetization (verified followers): {summary['monetization_progress']['verified_followers_seen']} / 500")
    return summary


def print_summary():
    log = _load_log()
    s = summarize(log)
    print(json.dumps(s, indent=2, ensure_ascii=False))


async def watch(interval_min: int = 15):
    while True:
        try:
            await scrape(verbose=True)
        except Exception as e:
            print(f"  ! scrape error: {type(e).__name__}: {e}")
        print(f"\n  Sleeping {interval_min} min…\n")
        await asyncio.sleep(interval_min * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.summary:
        print_summary()
    elif args.watch:
        asyncio.run(watch(args.interval))
    else:
        asyncio.run(scrape())
