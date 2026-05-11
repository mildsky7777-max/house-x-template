"""
Heartbeat monitor — Day 12 (Karpathy AutoResearch supporting infrastructure).

Two checks:
  1. Cron freshness — was each scanner's last successful run within expected window?
  2. Mandate compliance — % of pending drafts passing quality_gate.

Output: house/heartbeat.json (status snapshot)
        house/heartbeat_log.md (alerts when failing)

Cron: every 30 minutes, mismatched offset to avoid scanner contention.
  19,49 * * * *
"""
import json
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # ~/x/grow
HOUSE = ROOT / "house"
AUTO = ROOT / "auto"
HEARTBEAT_FILE = HOUSE / "heartbeat.json"
ALERT_LOG = HOUSE / "heartbeat_log.md"
KST = timezone(timedelta(hours=9))

# Cron schedule expectations (KST). max_age_hours: alert if last run older than this.
SCANNERS = {
    "evolution_scanner": {
        "log": HOUSE / "library" / ".evolution_log.json",
        "max_age_hours": 2,  # cron hourly
        "field": "runs",
    },
    "x_trends_scanner": {
        "log": HOUSE / "library" / ".x_trends_log.json",
        "max_age_hours": 3,  # cron every 2h
        "field": "runs",
    },
    "for_you_scanner": {
        "log": HOUSE / "library" / ".for_you_log.json",
        "max_age_hours": 2,  # hourly
        "field": "runs",
    },
    "engagement_analyzer": {
        "log": HOUSE / "library" / ".engagement_analyzer_log.json",
        "max_age_hours": 8,  # every 6h
        "field": "runs",
    },
    # x_publish freshness checked via drafts.json published_at instead of separate log
}


def is_night_pause() -> bool:
    """Most cron windows are 6-23 KST. Between 0-5 KST cron is paused — stale ok."""
    h = datetime.now(KST).hour
    return 0 <= h < 6


def check_freshness(name: str, conf: dict) -> dict:
    """Return {name, last_run, age_hours, ok}."""
    log_file = conf["log"]
    if not log_file.exists():
        return {"name": name, "last_run": None, "age_hours": None, "ok": False, "reason": "log file missing"}
    try:
        log = json.load(log_file.open())
    except Exception as e:
        return {"name": name, "last_run": None, "age_hours": None, "ok": False, "reason": f"log unreadable: {e}"}

    runs = log.get(conf["field"], [])
    if not runs:
        return {"name": name, "last_run": None, "age_hours": None, "ok": False, "reason": "no runs"}

    last = runs[-1]
    last_at = last.get("at") or last.get("when") or last.get("timestamp")
    if not last_at:
        return {"name": name, "last_run": None, "age_hours": None, "ok": False, "reason": "no timestamp on last run"}
    try:
        t = datetime.fromisoformat(last_at.replace("Z", "+00:00"))
    except Exception as e:
        return {"name": name, "last_run": last_at, "age_hours": None, "ok": False, "reason": f"bad timestamp: {e}"}

    age = (datetime.now(timezone.utc) - t).total_seconds() / 3600
    # Night pause grace — KST 0-5 cron paused, allow up to 8h staleness
    effective_max = conf["max_age_hours"]
    if is_night_pause() and conf.get("night_paused", True):
        effective_max = max(effective_max, 8)
    ok = age <= effective_max
    last_err = last.get("error")
    return {
        "name": name,
        "last_run": last_at,
        "age_hours": round(age, 2),
        "max_age_hours": conf["max_age_hours"],
        "ok": ok and not last_err,
        "last_error": last_err,
        "reason": None if ok and not last_err else (last_err or f"stale: {age:.1f}h > {conf['max_age_hours']}h"),
    }


def check_mandate_compliance() -> dict:
    """Run quality_gate on all pending drafts, return % pass rate."""
    drafts_file = AUTO / "drafts.json"
    if not drafts_file.exists():
        return {"ok": False, "reason": "drafts.json missing", "pass_rate": None, "checked": 0}
    sys.path.insert(0, str(HOUSE / "workers"))
    try:
        from quality_gate import check_draft
    except Exception as e:
        return {"ok": False, "reason": f"quality_gate import error: {e}", "pass_rate": None, "checked": 0}
    d = json.load(drafts_file.open())
    pending = [p for p in d.get("drafts", []) if p.get("status") == "pending"]
    if not pending:
        return {"ok": True, "pass_rate": 1.0, "checked": 0, "reason": "no pending"}
    pass_count = 0
    fails = []
    for p in pending:
        r = check_draft(p)
        if r.get("passed"):
            pass_count += 1
        else:
            fails.append({"id": p["id"], "fails": r.get("fails", [])})
    rate = pass_count / len(pending)
    return {
        "ok": rate >= 0.9,
        "pass_rate": round(rate, 3),
        "checked": len(pending),
        "passed": pass_count,
        "fails": fails[:10],
        "reason": None if rate >= 0.9 else f"compliance {rate:.0%} < 90%",
    }


def append_alert(status: dict):
    """Append alert lines to heartbeat_log.md if any failures."""
    failing = []
    for s in status["scanners"]:
        if not s["ok"]:
            failing.append(f"  - {s['name']}: {s['reason']}")
    mc = status["mandate_compliance"]
    if not mc["ok"]:
        failing.append(f"  - mandate_compliance: {mc.get('reason')} (passed {mc.get('passed')}/{mc.get('checked')})")
        for f in mc.get("fails", []):
            failing.append(f"    · {f['id']}: {','.join(f['fails'])}")
    if not failing:
        return
    if not ALERT_LOG.exists():
        ALERT_LOG.write_text("# Heartbeat alerts\n\n_Auto-generated by heartbeat.py. Each entry = one or more failures detected._\n\n")
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    block = [f"\n## {now}\n\n"] + [line + "\n" for line in failing]
    with ALERT_LOG.open("a") as f:
        f.write("".join(block))


def check_publish_freshness() -> dict:
    """Check most recent publish in drafts.json. Allow 24h staleness night-paused."""
    drafts_file = AUTO / "drafts.json"
    if not drafts_file.exists():
        return {"name": "x_publish", "ok": False, "reason": "drafts.json missing"}
    d = json.load(drafts_file.open())
    pub = [p for p in d.get("drafts", []) if p.get("status") == "published" and p.get("published_at")]
    if not pub:
        return {"name": "x_publish", "ok": False, "reason": "no published"}
    last = max(p.get("published_at") for p in pub)
    try:
        t = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except Exception as e:
        return {"name": "x_publish", "ok": False, "reason": f"bad timestamp: {e}"}
    age = (datetime.now(timezone.utc) - t).total_seconds() / 3600
    max_age = 24 if is_night_pause() else 6
    return {
        "name": "x_publish",
        "last_run": last,
        "age_hours": round(age, 2),
        "max_age_hours": max_age,
        "ok": age <= max_age,
        "reason": None if age <= max_age else f"no publish in {age:.1f}h",
    }


def main():
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "scanners": [check_freshness(n, c) for n, c in SCANNERS.items()] + [check_publish_freshness()],
        "mandate_compliance": check_mandate_compliance(),
    }
    HEARTBEAT_FILE.open("w").write(json.dumps(status, indent=2, ensure_ascii=False))

    # Console summary
    n_ok = sum(1 for s in status["scanners"] if s["ok"])
    print(f"[heartbeat] scanners ok: {n_ok}/{len(status['scanners'])}")
    for s in status["scanners"]:
        flag = "✓" if s["ok"] else "✗"
        print(f"  {flag} {s['name']}: age={s.get('age_hours','-')}h reason={s.get('reason','-')}")
    mc = status["mandate_compliance"]
    print(f"[heartbeat] mandate compliance: {mc.get('pass_rate','-')} ({mc.get('passed','-')}/{mc.get('checked','-')})")

    append_alert(status)

    # Exit code: 0 if all ok, 1 if any failure (cron picks up)
    all_ok = all(s["ok"] for s in status["scanners"]) and status["mandate_compliance"]["ok"]
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
