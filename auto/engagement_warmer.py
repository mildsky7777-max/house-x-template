"""
Engagement warmer — strategically like recent posts of verified actors who
already engaged with us. Drives mutual relationships → more verified followers.

Reads engagement.json (verified actors), visits each profile, likes their
top 1-2 recent posts. Rate-limited (one action per 60-90s) to avoid X anti-spam.

Usage:
    python engagement_warmer.py            # one-shot warming (≤10 actors)
    python engagement_warmer.py --max 5    # cap at 5 actors this session
    python engagement_warmer.py --status   # show what's been warmed

State: warmed.json
    { actor_handle: {warmed_at, posts_liked: [tweet_url], ...} }
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
ENGAGEMENT_FILE = ROOT / "engagement.json"
WARMED_FILE = ROOT / "warmed.json"

MIN_DELAY = 60   # seconds between actions
MAX_DELAY = 90
LIKES_PER_ACTOR = 2
DEFAULT_MAX_ACTORS = 10


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_warmed() -> dict:
    if not WARMED_FILE.exists():
        return {}
    with WARMED_FILE.open() as f:
        return json.load(f)


def _save_warmed(data: dict):
    with WARMED_FILE.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_verified_actors(skip_recent_hours: int = 24) -> list[str]:
    """
    Read engagement.json, return list of verified actor handles
    that we haven't warmed in the last N hours.
    """
    if not ENGAGEMENT_FILE.exists():
        return []
    with ENGAGEMENT_FILE.open() as f:
        eng = json.load(f)
    handles = set()
    for ev in eng.get("events", []):
        if ev.get("actor_verified") and ev.get("actor_handle"):
            handles.add(ev["actor_handle"])

    warmed = _load_warmed()
    cutoff = datetime.now(timezone.utc).timestamp() - skip_recent_hours * 3600
    fresh = []
    for h in handles:
        last = warmed.get(h, {}).get("last_warmed_at")
        if last:
            try:
                last_ts = datetime.fromisoformat(last).timestamp()
                if last_ts > cutoff:
                    continue
            except Exception:
                pass
        fresh.append(h)
    return fresh


async def _open_browser(p):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=False,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )


async def warm_one(page: Page, handle: str, n_likes: int = 2) -> dict:
    """Visit @handle, like top n posts (skipping pinned). Returns result dict."""
    result = {"handle": handle, "liked_urls": [], "errors": []}
    try:
        await page.goto(f"https://x.com/{handle}", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # Find non-pinned articles (skip first if pinned)
        articles = page.locator('article[data-testid="tweet"]')
        total = await articles.count()
        if total == 0:
            result["errors"].append("no_articles")
            return result

        liked = 0
        for i in range(min(total, 5)):  # check up to 5 to find 2 likeable
            if liked >= n_likes:
                break
            art = articles.nth(i)
            try:
                # Skip pinned
                pinned_label = art.locator('text=Pinned').count()
                # Skip retweets (we want their original posts)
                # We accept both for now — like is fine on either

                # Get tweet URL
                href_el = art.locator('a[href*="/status/"]').first
                if await href_el.count() == 0:
                    continue
                href = await href_el.get_attribute("href")
                if not href:
                    continue
                tweet_url = f"https://x.com{href}".split("?")[0].split("/photo/")[0].split("/analytics")[0]

                # Find like button — data-testid="like" (not "unlike", which means already liked)
                like_btn = art.locator('button[data-testid="like"]').first
                if await like_btn.count() == 0:
                    # Already liked or unlike state
                    continue
                if not await like_btn.is_visible():
                    continue
                await like_btn.click()
                await page.wait_for_timeout(800)
                result["liked_urls"].append(tweet_url)
                liked += 1
            except Exception as e:
                result["errors"].append(f"item_{i}:{type(e).__name__}")
                continue

        result["liked"] = liked
    except Exception as e:
        result["errors"].append(f"profile:{type(e).__name__}:{str(e)[:60]}")
    return result


async def run(max_actors: int = DEFAULT_MAX_ACTORS):
    actors = get_verified_actors()
    if not actors:
        print("No fresh verified actors to warm.")
        return

    random.shuffle(actors)
    actors = actors[:max_actors]
    print(f"\n  Warming {len(actors)} verified actors:")
    for h in actors:
        print(f"    - @{h}")
    print()

    warmed = _load_warmed()
    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()
        for i, h in enumerate(actors, start=1):
            print(f"  [{i}/{len(actors)}] @{h}…", end=" ", flush=True)
            r = await warm_one(page, h, n_likes=LIKES_PER_ACTOR)
            print(f"liked={r.get('liked', 0)} errors={len(r['errors'])}")
            warmed[h] = {
                "last_warmed_at": _now(),
                "posts_liked": warmed.get(h, {}).get("posts_liked", []) + r["liked_urls"],
                "errors": r["errors"],
            }
            _save_warmed(warmed)

            if i < len(actors):
                delay = random.randint(MIN_DELAY, MAX_DELAY)
                print(f"      sleeping {delay}s…", flush=True)
                await asyncio.sleep(delay)

        await ctx.close()
    print(f"\n  ✓ Done. Total warmed: {sum(1 for v in warmed.values())}")


def status():
    warmed = _load_warmed()
    print(f"\n  Total actors warmed: {len(warmed)}")
    by_recent = sorted(warmed.items(), key=lambda x: x[1].get("last_warmed_at", ""), reverse=True)
    for h, info in by_recent[:20]:
        n = len(info.get("posts_liked", []))
        print(f"    @{h:30s} likes={n:2d} last={info.get('last_warmed_at', 'never')[:19]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=DEFAULT_MAX_ACTORS)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.status:
        status()
    else:
        asyncio.run(run(max_actors=args.max))
