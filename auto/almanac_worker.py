"""
Almanac worker — daily 절기 (jeolgi) clock for the X account.

The X account at @YOUR_HANDLE runs on Korean solar terms, not the algorithm.
This worker:
  1. Determines today's 절기 from the jeolgi calendar
  2. Updates ~/x/grow/house/almanac/CURRENT.md (atomic write)
  3. Reads the day's 절기 file to find the suggested post shapes
  4. Drops a single SCAFFOLD draft into drafts.json (status="scaffold")
     prefilled with the day's prompt — to be polished by a Claude session
  5. Logs the run

Run via cron at 06:00 KST daily:
    0 21 * * *    # 21:00 UTC = 06:00 KST (next day)
"""
import json
import sys
import uuid
from datetime import datetime, date, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "house"
ALMANAC_DIR = ROOT / "almanac"
DRAFTS_FILE = Path(__file__).parent / "drafts.json"
LOG_FILE = ALMANAC_DIR / "almanac_log.json"
CURRENT_FILE = ALMANAC_DIR / "CURRENT.md"
DAY_ZERO = date(2026, 4, 29)  # Day 1 of the 30-day audit
KST = timezone(timedelta(hours=9))

# 24 jeolgi: (number, name_kor, hanja, file_stem, room, theme, start_mm_dd)
# Approximate dates — the real 절기 dates shift ±1 day yearly. Refine via
# astronomical calculation if precision matters; ±1 day is fine for our purpose.
JEOLGI = [
    (1,  "입춘", "立春", "01_입춘", "시작이 반이다", "First moves of the year",       (2, 4)),
    (2,  "우수", "雨水", "02_우수", "정",            "Soft thaw, gentle warming",      (2, 19)),
    (3,  "경칩", "驚蟄", "03_경칩", "危機",          "Things move underground",        (3, 5)),
    (4,  "춘분", "春分", "04_춘분", "가성비",        "Honest accounting, halves",      (3, 21)),
    (5,  "청명", "淸明", "05_청명", "눈치",          "Clarity, reading the room",      (4, 5)),
    (6,  "곡우", "穀雨", "06_곡우", "시작이 반이다", "Planting seeds",                  (4, 20)),
    (7,  "입하", "立夏", "07_입하", "정성",          "Devotion through early growth",   (5, 5)),
    (8,  "소만", "小滿", "08_소만", "깐깐함",        "Measure rigorously",              (5, 21)),
    (9,  "망종", "芒種", "09_망종", "의리",          "Keep the promises",               (6, 6)),
    (10, "하지", "夏至", "10_하지", "빨리빨리",      "Peak velocity",                   (6, 21)),
    (11, "소서", "小暑", "11_소서", "가성비",        "Cost discipline",                 (7, 7)),
    (12, "대서", "大暑", "12_대서", "정성",          "The patient slow-cook",           (7, 23)),
    (13, "입추", "立秋", "13_입추", "복기",          "First retrospectives",            (8, 7)),
    (14, "처서", "處暑", "14_처서", "한솥밥",        "Old friendships re-entered",      (8, 23)),
    (15, "백로", "白露", "15_백로", "눈치",          "Subtle signals",                  (9, 8)),
    (16, "추분", "秋分", "16_추분", "깐깐함",        "Audit, prune",                    (9, 23)),
    (17, "한로", "寒露", "17_한로", "危機",          "Edge of cliff",                   (10, 8)),
    (18, "상강", "霜降", "18_상강", "정",            "Tenderness in cold",              (10, 23)),
    (19, "입동", "立冬", "19_입동", "복기",          "Year's first replay",             (11, 7)),
    (20, "소설", "小雪", "20_소설", "한솥밥",        "Shared warmth",                   (11, 22)),
    (21, "대설", "大雪", "21_대설", "의리",          "Old loyalties tested",            (12, 7)),
    (22, "동지", "冬至", "22_동지", "시작이 반이다", "Light starts returning",          (12, 22)),
    (23, "소한", "小寒", "23_소한", "깐깐함",        "Year-end accounting",             (1, 6)),
    (24, "대한", "大寒", "24_대한", "정성",          "Hardest weeks, deepest care",     (1, 20)),
]


def jeolgi_for(d: date) -> tuple:
    """Find the jeolgi window containing date d. Returns the JEOLGI tuple."""
    # Build start dates relative to year d.year — for 소한/대한 (Jan), they're in d.year
    candidates = []
    for j in JEOLGI:
        mm, dd = j[6]
        # Try this year and previous year (handles year-crossing)
        for y in (d.year, d.year - 1):
            try:
                start = date(y, mm, dd)
                if start <= d:
                    candidates.append((start, j))
            except ValueError:
                continue
    candidates.sort(key=lambda x: x[0])
    return candidates[-1][1]  # most recent start


def jeolgi_window_end(j: tuple, today: date) -> date:
    """End date of this jeolgi window (= start of next - 1 day)."""
    idx = JEOLGI.index(j)
    next_j = JEOLGI[(idx + 1) % len(JEOLGI)]
    mm, dd = next_j[6]
    for y in (today.year, today.year + 1):
        try:
            nxt = date(y, mm, dd)
            if nxt > today:
                return nxt - timedelta(days=1)
        except ValueError:
            continue
    return today + timedelta(days=15)  # fallback


def jeolgi_window_start(j: tuple, today: date) -> date:
    mm, dd = j[6]
    for y in (today.year, today.year - 1):
        try:
            s = date(y, mm, dd)
            if s <= today:
                return s
        except ValueError:
            continue
    return today


def audit_day(today: date) -> int:
    return (today - DAY_ZERO).days + 1


def jeolgi_day(j: tuple, today: date) -> int:
    return (today - jeolgi_window_start(j, today)).days + 1


def update_current(today: date, j: tuple, audit_d: int, jeolgi_d: int) -> str:
    num, name, hanja, stem, room, theme, _ = j
    end = jeolgi_window_end(j, today)
    start = jeolgi_window_start(j, today)
    weekday_kor = ["월", "화", "수", "목", "금", "토", "일"][today.weekday()]
    body = f"""# 오늘의 절기 — Day {audit_d} of the 30-day audit

**Date:** {today.isoformat()} ({weekday_kor})

## Now: {name} ({hanja}) — {theme}

- **Window:** {start.isoformat()} → {end.isoformat()}
- **You are on day {jeolgi_d} of this 절기** (window length: {(end - start).days + 1} days)
- **Primary room:** {room}
- **Read:** [`almanac/{stem}.md`](./{stem}.md) — full 절기 brief

## Audit context

- 30-day audit Day {audit_d} of 30
- Day Zero: {DAY_ZERO.isoformat()} (start of audit)

## What this 절기 wants from today

Open `almanac/{stem}.md` and read **Suggested post shapes** + **What we DON'T post**. The room is **{room}**. The forbidden moves are listed in the file.

## Quick reference

| field | value |
|---|---|
| 절기 | {name} ({hanja}) |
| 영문 | {theme} |
| 방 | {room} |
| 시작 | {start.isoformat()} |
| 끝 | {end.isoformat()} |
| audit Day | {audit_d} / 30 |

—

*Last updated: {datetime.now(KST).isoformat(timespec='seconds')} (almanac_worker.py)*
"""
    CURRENT_FILE.write_text(body)
    return body


def make_scaffold(today: date, j: tuple, audit_d: int, jeolgi_d: int) -> dict:
    num, name, hanja, stem, room, theme, _ = j
    text = f"""[ SCAFFOLD — almanac_worker.py drop. Polish before flipping to pending. ]

Today is Day {audit_d} of 30-day audit.
The 절기 is {name} ({hanja}) — {theme}.
The room is {room}.

[ TAKE: 2-4 lines that hold the room {room} against today's specific receipt.
  Read almanac/{stem}.md for shape templates and what NOT to write.
  The 절기 wants slowness OR rigor OR velocity OR keeping promises —
  match the post's mood to the file's brief. ]

⸻

[ ONE concrete receipt: a number, a code change, a small ship,
  a reader interaction. NOT a take. NOT an inspiration. A specific. ]

Korean builder, Day {audit_d}. Inside {name}.
"""
    return {
        "id": str(uuid.uuid4())[:8],
        "type": "single",
        "text": text,
        "target_url": None,
        "media_path": None,
        "tags": ["almanac-scaffold", name, room, f"day{audit_d}"],
        "notes": f"almanac_worker.py drop — {name} ({hanja}) Day {jeolgi_d}, audit Day {audit_d}",
        "status": "scaffold",
        "scheduled_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "published_at": None,
        "error": None,
        "almanac_jeolgi": name,
        "almanac_room": room,
        "almanac_audit_day": audit_d,
    }


def append_draft(draft: dict):
    if DRAFTS_FILE.exists():
        data = json.load(DRAFTS_FILE.open())
    else:
        data = {"drafts": []}
    data["drafts"].append(draft)
    DRAFTS_FILE.open("w").write(json.dumps(data, indent=2, ensure_ascii=False))


def log_run(today: date, j: tuple, audit_d: int, draft_id: str | None):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        "kst_date": today.isoformat(),
        "jeolgi": j[1],
        "audit_day": audit_d,
        "draft_id": draft_id,
    })
    log["runs"] = log["runs"][-100:]
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="don't write CURRENT or scaffold")
    p.add_argument("--no-scaffold", action="store_true", help="update CURRENT only, no draft")
    p.add_argument("--date", help="override date (YYYY-MM-DD) for testing")
    args = p.parse_args()

    if args.date:
        today = date.fromisoformat(args.date)
    else:
        today = datetime.now(KST).date()

    j = jeolgi_for(today)
    audit_d = audit_day(today)
    jeolgi_d = jeolgi_day(j, today)

    print(f"Today: {today} (KST) — audit Day {audit_d}")
    print(f"절기: {j[1]} ({j[2]}) — {j[5]}")
    print(f"  Room: {j[4]}")
    print(f"  Day {jeolgi_d} of this jeolgi window")
    print(f"  Window: {jeolgi_window_start(j, today)} → {jeolgi_window_end(j, today)}")

    if args.dry_run:
        print("\n(dry-run — no writes)")
        return

    body = update_current(today, j, audit_d, jeolgi_d)
    print(f"\n  ✓ wrote {CURRENT_FILE}")

    draft_id = None
    if not args.no_scaffold:
        draft = make_scaffold(today, j, audit_d, jeolgi_d)
        append_draft(draft)
        draft_id = draft["id"]
        print(f"  ✓ scaffold draft {draft_id} added to queue (status=scaffold)")

    log_run(today, j, audit_d, draft_id)
    print(f"  ✓ logged to {LOG_FILE}")


if __name__ == "__main__":
    main()
