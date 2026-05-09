"""
Knowledge warden — pulls signals into the Library.

Every 90 minutes:
  1. Pull RSS from a curated source list
  2. Pull recent X targets from trend_scanner's targets.json
  3. Tag each item with which Korean room it could feed
  4. Append to today's feed/ MD file (atomic, never overwrite)
  5. Skip already-seen items (dedup by URL)

Does NOT publish. Does NOT decide what's good. Just gathers and tags.

Run via cron every 90 min:
    */90 * * * *
"""
import json
import os
import re
import ssl
import sys
import html
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]              # ~/x/grow/house
LIBRARY = ROOT / "library"
FEED_DIR = LIBRARY / "feed"
SEEN_FILE = LIBRARY / ".warden_seen.json"
LOG_FILE = LIBRARY / ".warden_log.json"
TRENDS_FILE = ROOT.parent / "auto" / "targets.json"

KST = timezone(timedelta(hours=9))

_SSL_CTX = ssl.create_default_context()
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE


# Curated feed list — Day 8 evening: added world news feeds (tech-angle filter applies later)
FEEDS = [
    # Tech / AI / Building (existing)
    {"url": "https://hnrss.org/frontpage", "topic": "tech"},
    {"url": "https://hnrss.org/newest?points=50", "topic": "tech-rising"},
    {"url": "https://techcrunch.com/feed/", "topic": "tech"},
    {"url": "https://www.theverge.com/rss/index.xml", "topic": "tech"},
    {"url": "https://www.technologyreview.com/feed/", "topic": "ai"},
    {"url": "https://daringfireball.net/feeds/main", "topic": "tech"},
    {"url": "https://www.indiehackers.com/feed.xml", "topic": "building"},
    {"url": "https://www.koreaherald.com/rss/020000000000.xml", "topic": "korea"},
    {"url": "http://export.arxiv.org/rss/cs.AI", "topic": "ai-research"},
    {"url": "http://export.arxiv.org/rss/cs.CL", "topic": "ai-research"},
    # World news (Day 8 evening — for News Desk Tier 1 breaking + tech-angle filter)
    # We capture global headlines but POST only when tech/AI/chip/Korea-defense angle exists.
    # Pure geopolitics = SKIP per constitution §8 forbidden topics.
    {"url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "topic": "world-tech"},
    {"url": "https://www.aljazeera.com/xml/rss/all.xml", "topic": "world-news"},
    {"url": "https://feeds.npr.org/1019/rss.xml", "topic": "world-tech"},
    {"url": "https://www.theguardian.com/technology/rss", "topic": "world-tech"},
    {"url": "https://www.engadget.com/rss.xml", "topic": "world-tech"},
    {"url": "https://www.wired.com/feed/rss", "topic": "world-tech"},
    {"url": "https://feeds.feedburner.com/TechCrunch/startups", "topic": "startups"},
    # Korean tech (Day 9 — verified feeds)
    {"url": "https://www.aitimes.com/rss/allArticle.xml", "topic": "korea-tech-ai"},
    {"url": "https://www.etnews.com/rss/section/news.xml", "topic": "korea-tech"},
    # {"url": "https://www.bloter.net/feed", "topic": "korea-tech"},  # 404
    # {"url": "https://www.zdnet.co.kr/rss/", "topic": "korea-tech"},  # 404
]

# Room-keyword mapping (for tagging captures with the rooms they could feed)
ROOM_KEYWORDS: dict[str, list[str]] = {
    "가성비": ["price", "cost", "cheap", "tokens per dollar", "subscription", "pricing", "free tier",
               "rate limit", "deepseek", "value", "ratio", "cents", "$/", "per million"],
    "깐깐함": ["audit", "review", "quality", "rigor", "meticulous", "test", "lint",
               "type-safe", "constraint", "discipline"],
    "빨리빨리": ["shipped", "launched", "in production", "deployed", "minutes", "hours after",
                 "released", "fast", "speed run", "iteration"],
    "의리": ["loyal", "long-term", "decade", "stayed", "didn't pivot", "still using",
             "since 20", "year-long", "committed"],
    "한솥밥": ["cofounder", "early team", "first hire", "early user", "shipped together",
               "open source contributor", "maintainer"],
    "危機": ["crisis", "pivot", "shutdown", "deprecated", "killed", "replaced", "obsolete",
             "extinction", "moat collapse"],
    "복기": ["postmortem", "retrospective", "lesson", "what went wrong", "learned",
             "reflection", "looking back"],
    "눈치": ["context", "intent", "subtle", "between the lines", "implicit",
             "ambient", "nuance", "non-verbal"],
    "정성": ["craft", "slow", "patient", "iterations", "maintainer", "kept",
             "refined", "long-running"],
    "시작이 반이다": ["day 1", "first commit", "MVP", "started", "begin", "launch day",
                     "v0.1", "first try"],
}


def fetch_feed(url: str, timeout: int = 15) -> str | None:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 knowledge-warden"})
        with urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
            return r.read().decode("utf-8", errors="replace")
    except (URLError, Exception) as e:
        print(f"  ! {urlparse(url).netloc}: {e}", file=sys.stderr)
        return None


def _strip_tags(s: str) -> str:
    s = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", s, flags=re.DOTALL)
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def parse_feed(xml_text: str, topic: str) -> list[dict]:
    items = []
    # RSS
    for m in re.finditer(r"<item\b[^>]*>(.*?)</item>", xml_text, re.DOTALL | re.IGNORECASE):
        c = m.group(1)
        t = re.search(r"<title\b[^>]*>(.*?)</title>", c, re.DOTALL | re.IGNORECASE)
        l = re.search(r"<link\b[^>]*>(.*?)</link>", c, re.DOTALL | re.IGNORECASE)
        d = re.search(r"<description\b[^>]*>(.*?)</description>", c, re.DOTALL | re.IGNORECASE)
        title = html.unescape(_strip_tags(t.group(1))) if t else ""
        link = html.unescape(_strip_tags(l.group(1))) if l else ""
        desc = html.unescape(_strip_tags(d.group(1)))[:300] if d else ""
        if title and link:
            items.append({"title": title, "link": link, "summary": desc, "topic": topic})
    # Atom
    for m in re.finditer(r"<entry\b[^>]*>(.*?)</entry>", xml_text, re.DOTALL | re.IGNORECASE):
        c = m.group(1)
        t = re.search(r"<title\b[^>]*>(.*?)</title>", c, re.DOTALL | re.IGNORECASE)
        l = re.search(r'<link\b[^>]*href="([^"]+)"', c, re.IGNORECASE)
        s = re.search(r"<summary\b[^>]*>(.*?)</summary>", c, re.DOTALL | re.IGNORECASE)
        title = html.unescape(_strip_tags(t.group(1))) if t else ""
        link = html.unescape(l.group(1)) if l else ""
        summ = html.unescape(_strip_tags(s.group(1)))[:300] if s else ""
        if title and link:
            items.append({"title": title, "link": link, "summary": summ, "topic": topic})
    return items


def tag_rooms(item: dict) -> list[str]:
    """Return list of rooms this item plausibly fits."""
    text = (item.get("title", "") + " " + item.get("summary", "")).lower()
    matched = []
    for room, kws in ROOM_KEYWORDS.items():
        if any(kw in text for kw in kws):
            matched.append(room)
    return matched


def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.load(SEEN_FILE.open()))
        except Exception:
            pass
    return set()


def save_seen(seen: set[str]):
    arr = list(seen)[-2000:]  # keep last 2000
    SEEN_FILE.open("w").write(json.dumps(arr, indent=2))


def append_to_feed(today: date, items: list[dict]) -> int:
    """Append items to today's feed/{date}.md. Return count appended."""
    feed_file = FEED_DIR / f"{today.isoformat()}.md"
    new_section = []
    if not feed_file.exists():
        new_section.append(f"# Library feed — {today.isoformat()}\n")
        new_section.append(f"*KST date. Captured by knowledge_warden.py.*\n\n")

    pull_at = datetime.now(KST).strftime("%H:%M KST")
    new_section.append(f"\n## Pull at {pull_at}\n\n")
    for it in items:
        rooms = ", ".join(it.get("rooms", [])) or "(no room match)"
        topic = it.get("topic", "?")
        new_section.append(f"### {it['title']}\n")
        new_section.append(f"**[{topic}]** rooms: {rooms}\n\n")
        if it.get("summary"):
            new_section.append(f"> {it['summary']}\n\n")
        new_section.append(f"<{it['link']}>\n\n")
    new_section.append("---\n")

    with feed_file.open("a") as f:
        f.write("".join(new_section))
    return len(items)


def append_x_targets(today: date) -> int:
    """Read trend_scanner output and add X targets to today's feed."""
    if not TRENDS_FILE.exists():
        return 0
    try:
        data = json.load(TRENDS_FILE.open())
    except Exception:
        return 0
    targets = data.get("targets", [])
    if not targets:
        return 0

    seen = load_seen()
    new_items = []
    for t in targets[:20]:  # top 20 recent trends
        url = t.get("tweet_url")
        if not url or url in seen:
            continue
        title = f"@{t.get('handle','?')} ({t.get('display_name','?')}): {t.get('text','')[:120]}"
        item = {
            "title": title,
            "link": url,
            "summary": t.get("text", "")[:300],
            "topic": "x-trend",
        }
        item["rooms"] = tag_rooms(item)
        new_items.append(item)
        seen.add(url)

    if not new_items:
        return 0

    feed_file = FEED_DIR / f"{today.isoformat()}.md"
    section = []
    if not feed_file.exists():
        section.append(f"# Library feed — {today.isoformat()}\n\n")

    pull_at = datetime.now(KST).strftime("%H:%M KST")
    section.append(f"\n## X trend pull at {pull_at} (from trend_scanner)\n\n")
    for it in new_items:
        rooms = ", ".join(it.get("rooms", [])) or "(no room match)"
        section.append(f"### {it['title']}\n")
        section.append(f"**[x-trend]** rooms: {rooms}\n\n")
        if it.get("summary"):
            section.append(f"> {it['summary']}\n\n")
        section.append(f"<{it['link']}>\n\n")
    section.append("---\n")

    feed_file.open("a").write("".join(section))
    save_seen(seen)
    return len(new_items)


def log_run(captures: dict):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        **captures,
    })
    log["runs"] = log["runs"][-100:]
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--max-per-feed", type=int, default=10)
    args = p.parse_args()

    today = datetime.now(KST).date()
    seen = load_seen()
    all_new: list[dict] = []

    for feed in FEEDS:
        xml = fetch_feed(feed["url"])
        if not xml:
            continue
        items = parse_feed(xml, feed["topic"])
        fresh = [it for it in items if it["link"] not in seen][:args.max_per_feed]
        for it in fresh:
            it["rooms"] = tag_rooms(it)
            seen.add(it["link"])
        all_new.extend(fresh)
        print(f"  • {urlparse(feed['url']).netloc}: +{len(fresh)} fresh")

    print(f"\nTotal new items from RSS: {len(all_new)}")

    rss_count = 0
    if all_new and not args.dry_run:
        rss_count = append_to_feed(today, all_new)
        save_seen(seen)
        print(f"  ✓ wrote {rss_count} items to feed/{today.isoformat()}.md")

    x_count = 0
    if not args.dry_run:
        x_count = append_x_targets(today)
        if x_count:
            print(f"  ✓ wrote {x_count} X trends to feed/{today.isoformat()}.md")

    if not args.dry_run:
        log_run({"rss_captured": rss_count, "x_captured": x_count, "total_seen": len(seen)})


if __name__ == "__main__":
    main()
