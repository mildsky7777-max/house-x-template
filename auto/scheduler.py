"""
Tiny scheduler that auto-approves drafts whose `scheduled_at` <= now.

Polls drafts.json every 30s. When a draft's scheduled time arrives,
calls /api/approve/<id> which triggers the Playwright publish flow.

Run in background:
    nohup python scheduler.py > scheduler.log 2>&1 &

Stop:
    pkill -f "python scheduler.py"
"""
import hashlib
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

DRAFTS_FILE = Path(__file__).parent / "drafts.json"
BASE = "http://localhost:5050"
POLL_INTERVAL = 30  # seconds

# Day 8: human-feel jitter — adds deterministic ±N min offset based on draft id.
# Posts scheduled at exact :00 fire at :07, :23, :54 etc. — looks like a person.
# Deterministic so re-runs of same draft fire at same offset (no race).
JITTER_RANGE_MIN = 15   # ±15 minutes


def jitter_offset_seconds(draft_id: str) -> int:
    """Deterministic offset in seconds, in [-JITTER_RANGE_MIN*60, +JITTER_RANGE_MIN*60].
    Uses md5 of draft_id for stable distribution.
    """
    h = hashlib.md5(draft_id.encode()).digest()
    # Take first 4 bytes as unsigned int, modulo (2*range_seconds + 1), shift to ±range
    raw = int.from_bytes(h[:4], "big")
    full = JITTER_RANGE_MIN * 60 * 2 + 1  # range is ±N min in seconds
    return (raw % full) - JITTER_RANGE_MIN * 60


def get_drafts():
    if not DRAFTS_FILE.exists():
        return []
    with DRAFTS_FILE.open() as f:
        return json.load(f).get("drafts", [])


def approve(draft_id):
    req = urllib.request.Request(
        f"{BASE}/api/approve/{draft_id}",
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.load(resp)


def tick():
    now = datetime.now(timezone.utc)
    fired = 0
    for d in get_drafts():
        if d.get("status") != "pending":
            continue
        sched = d.get("scheduled_at")
        if not sched:
            continue
        try:
            t = datetime.fromisoformat(sched.replace("Z", "+00:00"))
        except Exception:
            print(f"[{now.isoformat()}] {d['id']}: bad scheduled_at: {sched}")
            continue

        # Day 8: deterministic jitter to avoid bot-cadence
        # Skip jitter if draft has explicit `no_jitter` flag (for time-sensitive posts)
        if not d.get("no_jitter"):
            offset = jitter_offset_seconds(d["id"])
            t = t + timedelta(seconds=offset)

        if now < t:
            continue

        print(f"[{now.isoformat()}] Triggering {d['id']} (scheduled {sched}, jittered to {t.isoformat()})")
        try:
            r = approve(d["id"])
            ok = r.get("ok", False)
            err = r.get("draft", {}).get("error")
            print(f"  → ok={ok} error={err}")
            fired += 1
        except urllib.error.URLError as e:
            print(f"  ! URLError: {e}")
        except Exception as e:
            print(f"  ! error: {type(e).__name__}: {e}")
    return fired


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Scheduler started.")
    print(f"  Polling: every {POLL_INTERVAL}s")
    print(f"  Drafts:  {DRAFTS_FILE}")
    print(f"  API:     {BASE}\n")
    while True:
        try:
            tick()
        except Exception as e:
            print(f"tick error: {type(e).__name__}: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
