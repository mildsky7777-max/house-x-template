"""
Digest writer — distill the warden's raw feed into a fast-scan digest.

Reads:
  ~/x/grow/house/library/feed/{today}.md
  ~/x/grow/house/library/feed/{yesterday}.md  (for tail signal)

Writes:
  ~/x/grow/house/library/digest/{date}T{hour}.md
  ~/x/grow/house/library/INDEX.md  (rotating "this week's shelf")

Run via cron every 6 hours:
    0 */6 * * *
"""
import json
import re
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]              # ~/x/grow/house
LIBRARY = ROOT / "library"
FEED_DIR = LIBRARY / "feed"
DIGEST_DIR = LIBRARY / "digest"
INDEX_FILE = LIBRARY / "INDEX.md"
ALMANAC_CURRENT = ROOT / "almanac" / "CURRENT.md"

KST = timezone(timedelta(hours=9))


def parse_feed_md(p: Path) -> list[dict]:
    """Parse a feed/{date}.md file into items."""
    if not p.exists():
        return []
    text = p.read_text()
    items = []
    # Each item is: ### Title \n **[topic]** rooms: ... \n > summary \n <url>
    pattern = re.compile(
        r"^### (.+?)\n\*\*\[(.+?)\]\*\* rooms: (.+?)\n+"
        r"(?:> (.+?)\n+)?<(.+?)>",
        re.MULTILINE
    )
    for m in pattern.finditer(text):
        title, topic, rooms_str, summary, url = m.groups()
        rooms = [r.strip() for r in rooms_str.split(",") if r.strip() and r.strip() != "(no room match)"]
        items.append({
            "title": title.strip(),
            "topic": topic.strip(),
            "rooms": rooms,
            "summary": (summary or "").strip(),
            "url": url.strip(),
        })
    return items


def current_jeolgi() -> dict:
    """Read today's 절기 from CURRENT.md."""
    info = {"name": "?", "room": "?"}
    if not ALMANAC_CURRENT.exists():
        return info
    text = ALMANAC_CURRENT.read_text()
    m = re.search(r"Now: (\S+) \((\S+)\)", text)
    if m:
        info["name"] = m.group(1)
    m = re.search(r"Primary room:\*\*\s*(\S+)", text)
    if m:
        info["room"] = m.group(1)
    return info


def score_item(item: dict, target_room: str) -> int:
    """Higher = more relevant. Boost when target_room matches."""
    s = 0
    if target_room in item["rooms"]:
        s += 10
    s += len(item["rooms"])  # any room match adds weight
    if item["topic"] in ("ai", "tech-rising", "x-trend"):
        s += 2
    if item["topic"] == "ai-research":
        s += 1
    return s


def build_digest(items: list[dict], jeolgi: dict) -> str:
    target_room = jeolgi["room"]
    by_room: dict[str, list[dict]] = defaultdict(list)
    no_room: list[dict] = []
    for it in items:
        if it["rooms"]:
            for r in it["rooms"]:
                by_room[r].append(it)
        else:
            no_room.append(it)

    now = datetime.now(KST)
    lines = [
        f"# Digest — {now.strftime('%Y-%m-%d %H:%M KST')}",
        "",
        f"**Current 절기:** {jeolgi['name']} | **Primary room:** {target_room}",
        f"**Items in window:** {len(items)}",
        "",
        "---",
        "",
    ]

    # Section 1 — current room (top priority)
    if target_room in by_room:
        room_items = sorted(by_room[target_room],
                            key=lambda x: -score_item(x, target_room))[:8]
        lines.append(f"## ⭐ {target_room} (this 절기's room) — {len(by_room[target_room])} signals")
        lines.append("")
        for it in room_items:
            lines.append(f"- **{it['title']}** *(topic: {it['topic']})*")
            if it["summary"]:
                lines.append(f"  > {it['summary'][:160]}")
            lines.append(f"  → {it['url']}")
            lines.append("")
        lines.append("")

    # Section 2 — other rooms with signals
    other_rooms = sorted(
        [(r, items_) for r, items_ in by_room.items() if r != target_room],
        key=lambda x: -len(x[1])
    )
    if other_rooms:
        lines.append("## Other rooms with signals")
        lines.append("")
        for room, room_items in other_rooms[:9]:
            lines.append(f"### {room} ({len(room_items)})")
            for it in room_items[:3]:
                lines.append(f"- {it['title'][:100]} → {it['url']}")
            lines.append("")
        lines.append("")

    # Section 3 — top X trends (separate)
    x_items = [it for it in items if it["topic"] == "x-trend"][:8]
    if x_items:
        lines.append("## 🐦 Top X verified-account signals")
        lines.append("")
        for it in x_items:
            lines.append(f"- {it['title']}")
            lines.append(f"  → {it['url']}")
        lines.append("")

    # Section 4 — orphans (no room match) — but might be raw signal
    if no_room:
        lines.append(f"## ◯ No-room-match ({len(no_room)})")
        lines.append("*(may need new keyword tags or reveal a fresh signal)*")
        lines.append("")
        # Just titles, top 10
        for it in no_room[:10]:
            lines.append(f"- {it['title'][:100]} *({it['topic']})*")
        lines.append("")

    lines.append("---")
    lines.append(f"*Auto-generated by digest_writer.py at {now.isoformat(timespec='seconds')}*")
    lines.append("")
    return "\n".join(lines)


def write_index(recent_digests: list[Path], jeolgi: dict):
    """INDEX.md = current week's hot shelf — top items pulled from latest digests."""
    lines = [
        "# Library INDEX — this week's shelf",
        "",
        f"**Current 절기:** {jeolgi['name']} | **Room:** {jeolgi['room']}",
        f"**Last updated:** {datetime.now(KST).isoformat(timespec='seconds')}",
        "",
        "---",
        "",
        "## Recent digests",
        "",
    ]
    for d in recent_digests[:8]:
        lines.append(f"- [{d.stem}](./digest/{d.name})")
    lines.append("")

    # Aggregate top room hits across recent digests
    room_counter: Counter = Counter()
    for d in recent_digests[:5]:
        text = d.read_text()
        for m in re.finditer(r"## ⭐ (\S+)", text):
            room_counter[m.group(1)] += 1
        for m in re.finditer(r"^### (\S+) \(\d+\)", text, re.MULTILINE):
            room_counter[m.group(1)] += 1

    if room_counter:
        lines.append("## Hottest rooms (last 5 digests)")
        lines.append("")
        for r, n in room_counter.most_common(10):
            lines.append(f"- **{r}** — appeared in {n} digest sections")
        lines.append("")

    lines.append("---")
    lines.append("*The library is the inward half of the house.*")
    lines.append("*If you're about to write a post, start here.*")
    lines.append("")
    INDEX_FILE.write_text("\n".join(lines))


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=2,
                   help="how many days of feed to read (default 2)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    today = datetime.now(KST).date()
    items: list[dict] = []
    for offset in range(args.days):
        d = today - timedelta(days=offset)
        items.extend(parse_feed_md(FEED_DIR / f"{d.isoformat()}.md"))

    if not items:
        print("No feed items to digest.")
        return

    jeolgi = current_jeolgi()
    digest_md = build_digest(items, jeolgi)

    if args.dry_run:
        print(digest_md)
        return

    DIGEST_DIR.mkdir(exist_ok=True)
    fname = datetime.now(KST).strftime("%Y-%m-%dT%H") + ".md"
    out = DIGEST_DIR / fname
    out.write_text(digest_md)
    print(f"  ✓ wrote {out}")
    print(f"    items={len(items)}, jeolgi={jeolgi['name']}/{jeolgi['room']}")

    # Update INDEX.md
    digests = sorted(DIGEST_DIR.glob("*.md"), reverse=True)
    write_index(digests, jeolgi)
    print(f"  ✓ updated {INDEX_FILE}")


if __name__ == "__main__":
    main()
