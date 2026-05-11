"""
Engagement analyzer — Karpathy AutoResearch pattern applied to X content.

이지 mandate Day 12: "이 새로운 적용을 우리의 진화에 쓰라고 하는 거야."

Loop:
  publish (experiment) → 24h wait → engagement scrape (analysis)
  → score per post → experiment_log.md update
  → weekly retro reads log → mandate auto-update proposal

This worker handles the ANALYSIS half of the loop:
  - For each draft published >=24h ago and <=48h ago and not yet analyzed:
    - Visit the post URL via Playwright
    - Scrape: replies, retweets, likes, bookmarks, impressions
    - Score by engagement-per-impression + reply-weight
    - Append to experiment_log.md with the hypothesis tags from drafts.json

Run via cron:
  37 1,7,13,19 * * *  (every 6h, off-minute, gives 24h posts time)
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
DRAFTS_FILE = ROOT / "drafts.json"
EXPERIMENT_LOG = HOUSE / "experiment_log.md"
ANALYSIS_FILE = HOUSE / ".engagement_analysis.json"  # tracks already-analyzed
LOG_FILE = HOUSE / "library" / ".engagement_analyzer_log.json"
KST = timezone(timedelta(hours=9))


def load_already_analyzed() -> set[str]:
    if ANALYSIS_FILE.exists():
        try:
            return set(json.load(ANALYSIS_FILE.open()))
        except Exception:
            pass
    return set()


def save_already_analyzed(s: set[str]):
    ANALYSIS_FILE.open("w").write(json.dumps(list(s), indent=2))


def find_due_drafts() -> list[dict]:
    """Drafts published 24-72h ago, not yet analyzed."""
    if not DRAFTS_FILE.exists():
        return []
    d = json.load(DRAFTS_FILE.open())
    analyzed = load_already_analyzed()
    now = datetime.now(timezone.utc)
    due = []
    for p in d.get("drafts", []):
        if p.get("status") != "published":
            continue
        if p["id"] in analyzed:
            continue
        pub = p.get("published_at")
        if not pub:
            continue
        try:
            t = datetime.fromisoformat(pub.replace("Z", "+00:00"))
        except Exception:
            continue
        age = (now - t).total_seconds() / 3600
        if 24 <= age <= 72:
            due.append(p)
    return due


def parse_count(label: str) -> int:
    """Convert '1.2K replies' → 1200, '5 likes' → 5."""
    if not label:
        return 0
    label = label.lower().strip()
    m = re.search(r"([\d,\.]+)\s*([km]?)", label)
    if not m:
        return 0
    num = float(m.group(1).replace(",", ""))
    suffix = m.group(2)
    if suffix == "k":
        num *= 1000
    elif suffix == "m":
        num *= 1_000_000
    return int(num)


async def open_browser(p, headless=True):
    return await p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 1100},
    )


async def scrape_engagement(page, draft: dict) -> dict | None:
    """Visit X post URL, scrape engagement counts."""
    # Reconstruct URL from draft
    # We don't store post URL after publish (TODO), so search by text-prefix
    text = draft.get("text", "")
    if not text:
        return None
    snippet = text.split("\n")[0][:80]
    # search via x.com/search
    search_url = f"https://x.com/search?q=from%3AYOUR_HANDLE%20{snippet[:40].replace(' ','%20')}&f=live"
    try:
        await page.goto(search_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3500)
        # First matching article
        articles = page.locator('article[role="article"]')
        cnt = await articles.count()
        if cnt == 0:
            return None

        target = None
        for i in range(min(cnt, 5)):
            try:
                t = await articles.nth(i).inner_text()
                if snippet[:30] in t:
                    target = articles.nth(i)
                    break
            except Exception:
                continue
        if not target:
            target = articles.nth(0)

        # URL
        post_url = None
        try:
            time_link = target.locator('a[href*="/status/"]').first
            href = await time_link.get_attribute("href")
            if href:
                m = re.match(r"(/[^/]+/status/\d+)", href)
                if m:
                    post_url = "https://x.com" + m.group(1)
        except Exception:
            pass

        # Engagement counts via aria-label (most reliable)
        replies = retweets = likes = bookmarks = views = 0
        try:
            for testid, var_name in [
                ("reply", "replies"),
                ("retweet", "retweets"),
                ("like", "likes"),
                ("bookmark", "bookmarks"),
            ]:
                btn = target.locator(f'button[data-testid="{testid}"]').first
                if await btn.count():
                    label = await btn.get_attribute("aria-label") or ""
                    n = parse_count(label)
                    if var_name == "replies":
                        replies = n
                    elif var_name == "retweets":
                        retweets = n
                    elif var_name == "likes":
                        likes = n
                    elif var_name == "bookmarks":
                        bookmarks = n
        except Exception as e:
            print(f"  ! engagement parse: {e}", file=sys.stderr)

        # Views (impression count) — analytics anchor link
        try:
            anal = target.locator('a[href*="/analytics"]').first
            if await anal.count():
                label = await anal.get_attribute("aria-label") or ""
                views = parse_count(label)
        except Exception:
            pass

        return {
            "post_url": post_url,
            "replies": replies,
            "retweets": retweets,
            "likes": likes,
            "bookmarks": bookmarks,
            "views": views,
        }
    except Exception as e:
        print(f"  ! scrape error: {e}", file=sys.stderr)
        return None


def score(metrics: dict) -> float:
    """Composite engagement score per X 2024+ algorithm weights.
    Reply > Quote > Bookmark > Retweet > Like.
    Normalized by views (engagement rate)."""
    if not metrics:
        return 0.0
    views = max(metrics.get("views", 1), 1)
    replies = metrics.get("replies", 0)
    retweets = metrics.get("retweets", 0)
    likes = metrics.get("likes", 0)
    bookmarks = metrics.get("bookmarks", 0)
    weighted = (
        replies * 5.0
        + retweets * 3.0
        + bookmarks * 4.0
        + likes * 1.0
    )
    return round(weighted / views, 4)


def append_experiment_log(draft: dict, metrics: dict, score_val: float):
    """Append entry to experiment_log.md."""
    if not EXPERIMENT_LOG.exists():
        EXPERIMENT_LOG.write_text(
            "# Experiment Log — engagement_analyzer.py output\n\n"
            "_Karpathy AutoResearch loop applied to X content. "
            "Each post = experiment. Engagement = analysis. Compound learning over time._\n\n"
            "Format per entry: id | hypothesis tags | metrics | score | post text snippet\n\n"
        )
    pub = draft.get("published_at", "?")
    tags = ",".join(draft.get("tags", []))
    text_snip = draft.get("text", "").split("\n")[0][:80]
    entry = (
        f"\n## {draft['id']} (pub {pub[:16]})\n"
        f"- tags: `{tags}`\n"
        f"- text: {text_snip!r}\n"
        f"- metrics: replies={metrics.get('replies',0)} | retweets={metrics.get('retweets',0)} | "
        f"likes={metrics.get('likes',0)} | bookmarks={metrics.get('bookmarks',0)} | "
        f"views={metrics.get('views',0)}\n"
        f"- **score**: {score_val} (replies×5 + retweets×3 + bookmarks×4 + likes×1, /views)\n"
        f"- post_url: {metrics.get('post_url','-')}\n"
    )
    with EXPERIMENT_LOG.open("a") as f:
        f.write(entry)


def log_run(analyzed_n: int, error: str | None = None):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        "analyzed": analyzed_n,
        "error": error,
    })
    log["runs"] = log["runs"][-200:]
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


async def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--headed", action="store_true")
    args = ap.parse_args()

    due = find_due_drafts()
    print(f"  due (24-72h, unanalyzed): {len(due)}")
    if not due:
        log_run(0)
        return

    analyzed = load_already_analyzed()
    new_analyses = 0

    async with async_playwright() as pw:
        ctx = await open_browser(pw, headless=not args.headed)
        page = await ctx.new_page()
        try:
            for d in due:
                metrics = await scrape_engagement(page, d)
                if not metrics:
                    print(f"  ! {d['id']} no metrics found")
                    continue
                s = score(metrics)
                print(f"  {d['id']} score={s} replies={metrics['replies']} likes={metrics['likes']} views={metrics['views']}")
                if not args.dry_run:
                    append_experiment_log(d, metrics, s)
                    analyzed.add(d['id'])
                    new_analyses += 1
        finally:
            try:
                await ctx.close()
            except Exception:
                pass

    if not args.dry_run:
        save_already_analyzed(analyzed)
    log_run(new_analyses)
    print(f"  ✓ analyzed {new_analyses}, log → {EXPERIMENT_LOG}")


if __name__ == "__main__":
    asyncio.run(main())
