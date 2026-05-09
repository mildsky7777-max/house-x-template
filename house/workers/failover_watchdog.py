"""
Failover watchdog — when scheduler.py's Playwright publish FAILS, push to Typefully.

Background:
  Day 7 13:00 KST fire (a3afd92a) failed with "No enabled tweet/reply button found"
  — likely a compose-dialog edge case from emoji + numbered list + 30+ lines.
  We had a paid Typefully Pro account but no integration. This worker bridges that.

Pattern:
  Every 5 minutes (cron), scan drafts.json for entries that:
    - status == "failed"
    - failed within the last hour (so we don't endlessly republish ancient failures)
    - NOT already pushed to Typefully (no `typefully_id` field)
  For each: push to Typefully with scheduled_date = now + 90 seconds.
  Then mark `failover_pushed_at` and `typefully_id` on the local draft.

Conservative:
  - Never republishes a post twice (idempotent on `typefully_id`)
  - Skips posts with no scheduled_at (manual approve only — those failures are session-driven)
  - Skips posts older than 1 hour failed (treat as deliberate cancellation)

Run via cron every 5 minutes:
    */5 * * * *

Logs to ~/x/grow/house/failover_log.json
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]              # ~/x/grow/house
sys.path.insert(0, str(ROOT / "workers"))

import publish_typefully as tf  # noqa: E402

DRAFTS_FILE = ROOT.parent / "auto" / "drafts.json"
LOG_FILE = ROOT / "failover_log.json"

MAX_AGE_HOURS = 1  # don't recover failures older than this
DELAY_SECONDS = 90  # how far in future to schedule the Typefully push


def parse_iso(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def log(entry: dict):
    data = {"events": []}
    if LOG_FILE.exists():
        try:
            data = json.load(LOG_FILE.open())
        except Exception:
            pass
    data["events"].append({**entry, "at": datetime.now(timezone.utc).isoformat()})
    data["events"] = data["events"][-200:]
    LOG_FILE.open("w").write(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    if not DRAFTS_FILE.exists():
        print("no drafts.json")
        return

    data = json.load(DRAFTS_FILE.open())
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=MAX_AGE_HOURS)

    rescued = 0
    for d in data["drafts"]:
        if d.get("status") != "failed":
            continue
        if d.get("typefully_id"):
            continue  # already pushed
        if not d.get("scheduled_at"):
            continue  # manual-only post; not our fight

        # Use last error timestamp if any, else fall back to scheduled_at
        ts = parse_iso(d.get("scheduled_at"))
        if ts and ts < cutoff:
            # Too old — treat as deliberate
            log({"id": d["id"], "skipped": "too_old", "scheduled_at": d.get("scheduled_at")})
            continue

        # Push to Typefully
        future = now + timedelta(seconds=DELAY_SECONDS)
        sched_iso = future.isoformat().replace("+00:00", "Z")

        text = d["text"]
        posts = None
        if d.get("type") == "thread" and "\n---\n" in text:
            posts = [p.strip() for p in text.split("\n---\n") if p.strip()]

        try:
            r = tf.create_draft(text, schedule_iso=sched_iso, posts=posts, platforms=["x"])
        except Exception as e:
            log({"id": d["id"], "error": str(e)})
            continue

        if "id" in r:
            d["typefully_id"] = r["id"]
            d["typefully_pushed_at"] = now.isoformat()
            d["status"] = "failover-pushed"
            d["failover_scheduled_at"] = sched_iso
            log({
                "id": d["id"], "typefully_id": r["id"],
                "scheduled": sched_iso, "ok": True,
            })
            rescued += 1
            print(f"  ✓ rescued {d['id']} → typefully {r['id']} @ {sched_iso}")
        else:
            log({"id": d["id"], "typefully_response": r})
            print(f"  ✗ rescue failed {d['id']}: {r.get('error') or r}")

    if rescued:
        DRAFTS_FILE.open("w").write(
            json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("no failed drafts to rescue.")


if __name__ == "__main__":
    main()
