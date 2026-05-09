"""
Receipt ledger — daily honest audit of @YOUR_HANDLE.

The 30-day public audit is meaningless without an audit log. This worker
builds one. Reads the live data sources, computes daily metrics,
appends to an append-only markdown log + parallel JSON snapshot.

Sources read:
- ~/x/grow/auto/drafts.json           (posts, scaffolds, statuses)
- ~/x/grow/auto/engagement.json       (incoming likes / follows / replies)
- ~/x/grow/auto/auto_engaged.json     (our reactive follow-back / like-back)
- ~/x/grow/auto/followed_blitz.json   (strategic follows)
- ~/x/grow/auto/curated.json          (quote drafts auto_curator made)
- ~/x/grow/auto/targets.json          (last trend scan)
- ~/x/grow/house/article_curator_log.json (RSS scaffolds)
- ~/x/grow/house/almanac/almanac_log.json (절기 drops)

Outputs:
- ~/x/grow/house/rituals/audit_log.md    (append-only, human-readable)
- ~/x/grow/house/rituals/audit_log.json  (machine-readable parallel)

Run via cron at 23:00 KST daily (just before bed): `0 14 * * *`

Honest about what it can't see:
- Follower count (X doesn't expose without auth scraping; manual entry via --followers)
- Impressions (would require scraping per-tweet — out of scope for v1)
- Reply text quality (judgment, not metrics)

The ledger is honest by being incomplete. It records what the workers know.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime, date, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]              # ~/x/grow/house
AUTO = ROOT.parent / "auto"
RITUALS = ROOT / "rituals"
RITUALS.mkdir(parents=True, exist_ok=True)

LEDGER_MD = RITUALS / "audit_log.md"
LEDGER_JSON = RITUALS / "audit_log.json"

DAY_ZERO = date(2026, 4, 29)  # Day 1 of the 30-day audit
KST = timezone(timedelta(hours=9))


def load_json(p: Path, default):
    if not p.exists():
        return default
    try:
        return json.load(p.open())
    except Exception:
        return default


def in_window(iso_str: str, day: date) -> bool:
    """True if iso_str is within KST `day` (calendar day)."""
    if not iso_str:
        return False
    try:
        ts = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except Exception:
        return False
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    kst_d = ts.astimezone(KST).date()
    return kst_d == day


def audit_day_num(d: date) -> int:
    return (d - DAY_ZERO).days + 1


def compute_snapshot(today: date, manual_followers: int | None) -> dict:
    snap = {"date": today.isoformat(), "audit_day": audit_day_num(today)}

    # --- Drafts ---
    drafts = load_json(AUTO / "drafts.json", {"drafts": []}).get("drafts", [])
    by_status: Counter = Counter()
    published_today = []
    pending_now = []
    scaffolds_created_today = 0
    almanac_drops_today = 0
    for d in drafts:
        by_status[d.get("status", "?")] += 1
        if d.get("status") == "published" and in_window(d.get("published_at", ""), today):
            published_today.append({
                "id": d["id"],
                "type": d.get("type"),
                "head": d.get("text", "")[:60].replace("\n", " "),
                "url": d.get("url"),
            })
        if d.get("status") == "pending":
            pending_now.append({
                "id": d["id"], "scheduled_at": d.get("scheduled_at"),
                "head": d.get("text", "")[:50].replace("\n", " "),
            })
        # Count by creation date regardless of current status (honest count of
        # workflow output — supersedes/polishes shouldn't hide what was made)
        if in_window(d.get("created_at", ""), today):
            tags = d.get("tags", [])
            if d.get("status") in ("scaffold", "superseded", "ai-polished"):
                scaffolds_created_today += 1
            if "almanac-scaffold" in tags:
                almanac_drops_today += 1

    snap["drafts_status_counts"] = dict(by_status)
    snap["published_today"] = published_today
    snap["pending_now"] = pending_now
    snap["scaffolds_created_today"] = scaffolds_created_today
    snap["almanac_drops_today"] = almanac_drops_today

    # --- Incoming engagement ---
    engagement = load_json(AUTO / "engagement.json", {"events": []})
    events = engagement.get("events", [])
    likes_today = []
    follows_today = []
    replies_today = []
    verified_actors_today = set()
    for ev in events:
        if not in_window(ev.get("first_seen_at", ""), today):
            continue
        actor = ev.get("actor_handle", "?")
        if ev.get("actor_verified"):
            verified_actors_today.add(actor)
        t = ev.get("type")
        if t == "like":
            likes_today.append(actor)
        elif t == "follow":
            follows_today.append(actor)
        elif t == "reply":
            replies_today.append({"actor": actor, "preview": ev.get("target_preview", "")[:80]})

    snap["incoming_today"] = {
        "likes": len(likes_today),
        "follows": len(follows_today),
        "replies": len(replies_today),
        "verified_actor_count": len(verified_actors_today),
        "verified_actor_handles": sorted(verified_actors_today)[:20],
    }

    # --- Reactive engagement (our follow-backs / like-backs) ---
    auto_engaged = load_json(AUTO / "auto_engaged.json", {"log": []})
    our_actions_today = [
        x for x in auto_engaged.get("log", [])
        if in_window(x.get("at", ""), today)
    ]
    snap["our_reactive_actions_today"] = {
        "count": len(our_actions_today),
        "by_action": dict(Counter(x.get("action", "?") for x in our_actions_today)),
    }

    # --- Strategic follows ---
    followed = load_json(AUTO / "followed_blitz.json", {"followed": []})
    snap["strategic_follows_today"] = sum(
        1 for x in followed.get("followed", [])
        if in_window(x.get("at", ""), today)
    )

    # --- Trend scan freshness ---
    targets = load_json(AUTO / "targets.json", {})
    if targets.get("scanned_at"):
        snap["last_trend_scan"] = targets["scanned_at"]
        snap["last_trend_targets"] = targets.get("after_filter", 0)

    # --- Article curator runs ---
    art_log = load_json(ROOT / "article_curator_log.json", {"runs": []})
    art_runs_today = [r for r in art_log.get("runs", [])
                      if in_window(r.get("at", ""), today)]
    snap["article_curator_runs_today"] = len(art_runs_today)
    snap["article_drafts_created_today"] = sum(r.get("drafts_created", 0)
                                               for r in art_runs_today)

    # --- Almanac runs ---
    alm_log = load_json(ROOT / "almanac" / "almanac_log.json", {"runs": []})
    alm_today = [r for r in alm_log.get("runs", [])
                 if in_window(r.get("at", ""), today)]
    snap["almanac_runs_today"] = len(alm_today)

    # --- Followers (manual or last known) ---
    if manual_followers is not None:
        snap["followers"] = manual_followers
        snap["followers_source"] = "manual"
    else:
        # Try to read last entry from existing JSON ledger
        prior = load_json(LEDGER_JSON, {"snapshots": []})
        last_with_followers = None
        for s in reversed(prior.get("snapshots", [])):
            if "followers" in s:
                last_with_followers = s
                break
        if last_with_followers:
            snap["followers"] = last_with_followers["followers"]
            snap["followers_source"] = f"carried-from-{last_with_followers['date']}"

    return snap


def render_md(snap: dict, prior: dict | None) -> str:
    """Return a markdown block for today's snapshot."""
    delta_line = ""
    if prior and "followers" in prior and "followers" in snap:
        d = snap["followers"] - prior["followers"]
        sign = "+" if d >= 0 else ""
        delta_line = f" (Δ {sign}{d} from Day {prior.get('audit_day', '?')})"

    pub = snap["published_today"]
    pending = snap["pending_now"]
    incoming = snap["incoming_today"]

    lines = []
    lines.append(f"## Day {snap['audit_day']} — {snap['date']}")
    lines.append("")
    if "followers" in snap:
        lines.append(f"**Followers:** {snap['followers']}{delta_line}  *(source: {snap.get('followers_source', '?')})*")
    else:
        lines.append("**Followers:** *(not recorded — pass --followers N to set)*")
    lines.append("")

    lines.append(f"**Posts published today:** {len(pub)}")
    for p in pub:
        url_part = f" — {p['url']}" if p.get("url") else ""
        lines.append(f"- `{p['id']}` ({p.get('type','?')}) — {p['head']}{url_part}")
    lines.append("")

    lines.append(f"**Pending in queue:** {len(pending)}")
    for p in pending[:10]:
        lines.append(f"- `{p['id']}` @ {p.get('scheduled_at','-')} — {p['head']}")
    lines.append("")

    lines.append(f"**Scaffolds created today:** {snap['scaffolds_created_today']} (of which almanac drops: {snap['almanac_drops_today']})")
    lines.append(f"**Article curator runs today:** {snap['article_curator_runs_today']} → {snap['article_drafts_created_today']} scaffolds")
    lines.append(f"**Almanac worker runs today:** {snap['almanac_runs_today']}")
    lines.append("")

    lines.append(f"**Incoming engagement today:** {incoming['likes']} likes, {incoming['follows']} follows, {incoming['replies']} replies")
    lines.append(f"  Verified actors: {incoming['verified_actor_count']}")
    if incoming['verified_actor_handles']:
        lines.append(f"  Sample: {', '.join('@' + h for h in incoming['verified_actor_handles'][:10])}")
    lines.append("")

    lines.append(f"**Our reactive actions today:** {snap['our_reactive_actions_today']['count']}  "
                 f"(by action: {snap['our_reactive_actions_today']['by_action']})")
    lines.append(f"**Strategic follows today:** {snap['strategic_follows_today']}")
    lines.append("")

    lines.append(f"**Drafts status distribution (all-time):**")
    for status, n in sorted(snap["drafts_status_counts"].items(), key=lambda x: -x[1]):
        lines.append(f"  - {status}: {n}")
    lines.append("")

    if "last_trend_scan" in snap:
        lines.append(f"*Last trend scan: {snap['last_trend_scan']} ({snap['last_trend_targets']} targets after filter)*")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def append_to_ledgers(snap: dict, md_block: str):
    # MD: prepend header if file new, then append block
    if not LEDGER_MD.exists():
        header = (
            "# Audit Log — @YOUR_HANDLE 30-day public audit\n\n"
            "*This is the receipt for the 30-day public audit.*\n"
            "*Auto-generated daily by `~/x/grow/house/workers/receipt_ledger.py`.*\n"
            "*Honest by being incomplete: only records what the workers know.*\n\n"
            "---\n\n"
        )
        LEDGER_MD.write_text(header + md_block)
    else:
        LEDGER_MD.open("a").write(md_block)

    # JSON: append snapshot to list
    data = load_json(LEDGER_JSON, {"snapshots": []})
    data["snapshots"].append(snap)
    LEDGER_JSON.open("w").write(json.dumps(data, indent=2, ensure_ascii=False))


def find_prior(today: date) -> dict | None:
    data = load_json(LEDGER_JSON, {"snapshots": []})
    yest = today - timedelta(days=1)
    for s in reversed(data.get("snapshots", [])):
        if s.get("date") == yest.isoformat():
            return s
    if data.get("snapshots"):
        return data["snapshots"][-1]
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", help="override KST date (YYYY-MM-DD)")
    p.add_argument("--followers", type=int, help="record current follower count manually")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--show", action="store_true", help="just print without appending")
    args = p.parse_args()

    today = date.fromisoformat(args.date) if args.date else datetime.now(KST).date()
    snap = compute_snapshot(today, args.followers)
    prior = find_prior(today)
    md = render_md(snap, prior)

    if args.dry_run or args.show:
        print(md)
        if args.dry_run:
            print("\n(dry-run — not appended)")
        return

    # Idempotency: if today is already in JSON, replace not duplicate
    data = load_json(LEDGER_JSON, {"snapshots": []})
    data["snapshots"] = [s for s in data.get("snapshots", []) if s.get("date") != today.isoformat()]
    data["snapshots"].append(snap)
    LEDGER_JSON.open("w").write(json.dumps(data, indent=2, ensure_ascii=False))

    # MD: full rewrite from JSON to keep it idempotent
    snapshots = sorted(data["snapshots"], key=lambda s: s["date"])
    header = (
        "# Audit Log — @YOUR_HANDLE 30-day public audit\n\n"
        "*This is the receipt for the 30-day public audit.*\n"
        "*Auto-generated daily by `~/x/grow/house/workers/receipt_ledger.py`.*\n"
        "*Honest by being incomplete: only records what the workers know.*\n\n"
        f"*Last run: {datetime.now(KST).isoformat(timespec='seconds')}*\n\n"
        "---\n\n"
    )
    body = []
    prior_s = None
    for s in snapshots:
        body.append(render_md(s, prior_s))
        prior_s = s
    LEDGER_MD.write_text(header + "".join(body))
    print(f"✓ {LEDGER_MD}")
    print(f"✓ {LEDGER_JSON}")
    print(f"  Day {snap['audit_day']} snapshot recorded.")


if __name__ == "__main__":
    main()
