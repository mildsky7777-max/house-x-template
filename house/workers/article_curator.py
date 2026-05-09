"""
Article curator — pull trending tech/culture articles, scaffold drafts with
Korean-lens commentary slots.

Pattern:
  1. Pull RSS from a curated set of feeds (tech, AI, Korea, building)
  2. Score each item: freshness × signal keywords × topic mix
  3. Pick top N (default 3)
  4. Create scaffold draft with:
       - Article headline as first line
       - Article URL as last line (X auto-cards it)
       - Middle: a TAKE_PLACEHOLDER for Korean-lens commentary
  5. Queue as status="scaffold" (NOT pending) so scheduler does NOT auto-fire
  6. A Claude session (or you) polishes the take, runs quality_gate, flips to pending

This keeps the house honest: no AI-generated takes auto-published.
The scaffold reduces friction; the human (or alive Claude) writes the angle.

Usage:
    python article_curator.py                # pull, score, scaffold top 3
    python article_curator.py --max 5        # scaffold top 5
    python article_curator.py --dry-run      # print picks, don't write drafts
    python article_curator.py --topics ai    # filter to single topic
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]  # ~/x/grow/house
DRAFTS_FILE = Path.home() / "x" / "grow" / "auto" / "drafts.json"
LOG_FILE = ROOT / "article_curator_log.json"
SEEN_FILE = ROOT / "article_seen.json"

# Feed catalogue — diverse mix on purpose.
# Topic tag controls --topics filter.
FEEDS = [
    # AI & dev
    {"url": "https://hnrss.org/frontpage", "topic": "tech", "weight": 1.0},
    {"url": "https://techcrunch.com/feed/", "topic": "tech", "weight": 0.9},
    {"url": "https://www.theverge.com/rss/index.xml", "topic": "tech", "weight": 0.9},
    {"url": "https://www.technologyreview.com/feed/", "topic": "ai", "weight": 1.0},
    {"url": "https://daringfireball.net/feeds/main", "topic": "tech", "weight": 0.85},
    # Building / indie
    {"url": "https://www.indiehackers.com/feed.xml", "topic": "building", "weight": 0.9},
    # Korea / culture
    {"url": "https://www.koreaherald.com/rss/020000000000.xml", "topic": "korea", "weight": 0.7},
]

# Boost keywords — articles with these in title score higher
BOOST_KEYWORDS = [
    # AI/building signal
    "claude", "anthropic", "openai", "gpt", "agent", "llm",
    "indie", "solo", "faceless", "automation", "build", "ship",
    "youtube", "creator", "passive", "monetize",
    # Korea hooks (for our angle)
    "korea", "korean", "seoul", "samsung", "naver", "kakao",
    # Tension hooks (good for commentary)
    "vs", "killed", "replaced", "obsolete", "future", "lesson",
]

# Drop these — wasteful for our brand
SKIP_KEYWORDS = [
    "sponsored", "ad:", "advertisement",
    "horoscope", "celebrity gossip", "kpop scandal",
    "stock tip", "buy now", "deal:",
]


import ssl

_SSL_CTX = ssl.create_default_context()
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    # Fallback: don't verify (we're parsing public RSS, not auth flows)
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE


def fetch_feed(url: str, timeout: int = 15) -> str | None:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 article-curator"})
        with urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
            return r.read().decode("utf-8", errors="replace")
    except (URLError, Exception) as e:
        print(f"  ! feed fail {urlparse(url).netloc}: {e}", file=sys.stderr)
        return None


def _strip_tags(s: str) -> str:
    s = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", s, flags=re.DOTALL)
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def _decode_entities(s: str) -> str:
    import html
    return html.unescape(s)


def parse_feed(xml_text: str, topic: str, weight: float) -> list[dict]:
    """Regex-based RSS/Atom parser. Avoids xml.etree (Python 3.14 expat issue).
    Handles RSS 2.0 <item> and Atom <entry>."""
    items: list[dict] = []

    # RSS 2.0
    for m in re.finditer(r"<item\b[^>]*>(.*?)</item>", xml_text, re.DOTALL | re.IGNORECASE):
        chunk = m.group(1)
        t = re.search(r"<title\b[^>]*>(.*?)</title>", chunk, re.DOTALL | re.IGNORECASE)
        l = re.search(r"<link\b[^>]*>(.*?)</link>", chunk, re.DOTALL | re.IGNORECASE)
        d = re.search(r"<pubDate\b[^>]*>(.*?)</pubDate>", chunk, re.DOTALL | re.IGNORECASE)
        title = _decode_entities(_strip_tags(t.group(1))) if t else ""
        link = _decode_entities(_strip_tags(l.group(1))) if l else ""
        pub = _strip_tags(d.group(1)) if d else ""
        if title and link:
            items.append({"title": title, "link": link, "pub": pub,
                          "topic": topic, "weight": weight})

    # Atom <entry>
    for m in re.finditer(r"<entry\b[^>]*>(.*?)</entry>", xml_text, re.DOTALL | re.IGNORECASE):
        chunk = m.group(1)
        t = re.search(r"<title\b[^>]*>(.*?)</title>", chunk, re.DOTALL | re.IGNORECASE)
        # Atom: <link href="..." />
        l = re.search(r'<link\b[^>]*href="([^"]+)"', chunk, re.IGNORECASE)
        d = re.search(r"<(?:updated|published)\b[^>]*>(.*?)</(?:updated|published)>",
                      chunk, re.DOTALL | re.IGNORECASE)
        title = _decode_entities(_strip_tags(t.group(1))) if t else ""
        link = _decode_entities(l.group(1)) if l else ""
        pub = _strip_tags(d.group(1)) if d else ""
        if title and link:
            items.append({"title": title, "link": link, "pub": pub,
                          "topic": topic, "weight": weight})
    return items


def parse_pubdate(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)
    except Exception:
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def score_item(item: dict, now: datetime) -> float:
    title = item["title"].lower()
    if any(k in title for k in SKIP_KEYWORDS):
        return -1.0

    score = item["weight"]

    # Freshness — exponential decay over 48 hours
    pub = parse_pubdate(item["pub"])
    if pub:
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        age_h = (now - pub).total_seconds() / 3600
        if age_h < 0:
            age_h = 0
        if age_h > 72:
            return -1.0  # too old
        score *= max(0.1, 1.0 - age_h / 72)

    # Boost for signal keywords
    boosts = sum(1 for k in BOOST_KEYWORDS if k in title)
    score += 0.15 * boosts

    return score


def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.load(SEEN_FILE.open()))
        except Exception:
            pass
    return set()


def save_seen(seen: set[str]):
    # Keep last 500
    arr = list(seen)[-500:]
    json.dump(arr, SEEN_FILE.open("w"), indent=2)


def scaffold_text(item: dict) -> str:
    title = item["title"]
    return (
        f"{title}\n"
        f"\n"
        f"⸻\n"
        f"\n"
        f"[ TAKE: write 2-3 lines of Korean-lens commentary here.\n"
        f"  Patterns:\n"
        f"  - 'Western tech says X. Korea solved this with Y 30 years ago.'\n"
        f"  - 'This is a 가성비 / 깐깐함 / 빨리빨리 / 의리 problem.'\n"
        f"  - Specific receipt or counterpoint, not a hot take. ]\n"
        f"\n"
        f"⸻\n"
        f"\n"
        f"{item['link']}\n"
        f"\n"
        f"Korean builder, Day X."
    )


def post_draft(text: str, item: dict) -> dict | None:
    """Append to drafts.json with status=scaffold. Bypass server to avoid status restriction."""
    import uuid
    draft = {
        "id": str(uuid.uuid4())[:8],
        "type": "single",
        "text": text,
        "target_url": None,
        "media_path": None,
        "tags": ["article-scaffold", item["topic"]],
        "notes": f"Source: {urlparse(item['link']).netloc} — needs human take before flipping to pending",
        "status": "scaffold",
        "scheduled_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "published_at": None,
        "error": None,
        "source_link": item["link"],
        "source_title": item["title"],
    }
    try:
        if DRAFTS_FILE.exists():
            data = json.load(DRAFTS_FILE.open())
        else:
            data = {"drafts": []}
        data["drafts"].append(draft)
        json.dump(data, DRAFTS_FILE.open("w"), indent=2, ensure_ascii=False)
        return draft
    except Exception as e:
        print(f"  ! draft write fail: {e}", file=sys.stderr)
        return None


def log_run(picks: list[dict], drafts_created: int):
    entry = {
        "at": datetime.now(timezone.utc).isoformat(),
        "picks": [{"title": p["title"], "link": p["link"], "score": p.get("_score", 0)}
                  for p in picks],
        "drafts_created": drafts_created,
    }
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append(entry)
    log["runs"] = log["runs"][-50:]  # keep last 50
    json.dump(log, LOG_FILE.open("w"), indent=2, ensure_ascii=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=3)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--topics", help="comma-list of topics to include (tech,ai,building,korea)")
    args = p.parse_args()

    topic_filter = set(args.topics.split(",")) if args.topics else None
    feeds = [f for f in FEEDS if not topic_filter or f["topic"] in topic_filter]

    now = datetime.now(timezone.utc)
    all_items: list[dict] = []
    for f in feeds:
        print(f"  • {urlparse(f['url']).netloc} [{f['topic']}]")
        xml_text = fetch_feed(f["url"])
        if not xml_text:
            continue
        items = parse_feed(xml_text, f["topic"], f["weight"])
        all_items.extend(items)

    # Score + dedup
    seen = load_seen()
    fresh = []
    for it in all_items:
        if it["link"] in seen:
            continue
        s = score_item(it, now)
        if s < 0:
            continue
        it["_score"] = s
        fresh.append(it)

    # Diversify topics in top picks: round-robin by topic
    fresh.sort(key=lambda x: -x["_score"])
    by_topic: dict[str, list[dict]] = {}
    for it in fresh:
        by_topic.setdefault(it["topic"], []).append(it)

    picks: list[dict] = []
    while len(picks) < args.max and any(by_topic.values()):
        for t in list(by_topic.keys()):
            if not by_topic[t]:
                del by_topic[t]
                continue
            picks.append(by_topic[t].pop(0))
            if len(picks) >= args.max:
                break

    print(f"\n=== Top {len(picks)} picks ===")
    for i, it in enumerate(picks, 1):
        print(f"  {i}. [{it['topic']:8s}] {it['title'][:80]}")
        print(f"     {it['link']}")
        print(f"     score={it['_score']:.2f}")

    if args.dry_run:
        print("\n(dry-run — no drafts written)")
        return

    drafts_created = 0
    for it in picks:
        text = scaffold_text(it)
        d = post_draft(text, it)
        if d:
            print(f"\n  ✓ scaffold {d['id']} — {it['title'][:60]}")
            drafts_created += 1
            seen.add(it["link"])

    save_seen(seen)
    log_run(picks, drafts_created)
    print(f"\n=== {drafts_created} scaffold drafts created (status=scaffold) ===")
    print("Next: open queue UI, write the take, run quality_gate, flip to pending.")


if __name__ == "__main__":
    main()
