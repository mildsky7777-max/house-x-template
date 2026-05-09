# The Almanac — 24 절기 (jeolgi)

The X account at @YOUR_HANDLE runs on Korean solar terms, not on the X algorithm. This directory holds the 24 절기 calendar that organizes our content rhythm.

## What this does

- Each 절기 ≈ 15 days
- Each 절기 has: a **theme**, a **primary room** (Korean concept), a **suggested post shape**, sometimes a **guest** (a non-tech profession's wisdom we lean into that window)
- `CURRENT.md` is the today-pointer, updated by `almanac_worker.py` at 06:00 KST daily
- The worker also drops a daily scaffold draft into the queue: "Today is Day X of <절기>. Theme: ___. Suggested shape: ___."

## Why

Most X accounts react to algorithm spikes. We choose to live in seasons. This means:

- **Content drift is impossible** — there's always a theme on the wall
- **The audience learns the rhythm** — they know roughly what kind of post to expect when
- **The voice consolidates** — the room of the week reinforces itself
- **Algorithm pressure relaxes** — we're not chasing trends, we're harvesting from the field we're in

## The 24 (in calendar order)

| # | 절기 | Hanja | Approx dates | Translation | Room | Theme |
|---|---|---|---|---|---|---|
| 1 | 입춘 | 立春 | Feb 4–18 | Spring begins | 시작이 반이다 | First moves of the year |
| 2 | 우수 | 雨水 | Feb 19–Mar 4 | Rain water | 정 | Soft thaw, gentle |
| 3 | 경칩 | 驚蟄 | Mar 5–20 | Awakening of insects | 危機 | Things move underground |
| 4 | 춘분 | 春分 | Mar 21–Apr 4 | Spring equinox | 가성비 | Honest accounting, halves |
| 5 | 청명 | 淸明 | Apr 5–19 | Clear and bright | 눈치 | Clarity, reading the room |
| 6 | 곡우 | 穀雨 | Apr 20–May 4 | Grain rain | 시작이 반이다 | Planting seeds |
| **7** | **입하** | **立夏** | **May 5–20** | **Summer begins** | **정성** | **Devotion through early growth** |
| 8 | 소만 | 小滿 | May 21–Jun 5 | Small full | 깐깐함 | Measure rigorously |
| 9 | 망종 | 芒種 | Jun 6–20 | Grain in ear | 의리 | Keep the promises |
| 10 | 하지 | 夏至 | Jun 21–Jul 6 | Summer solstice | 빨리빨리 | Peak velocity |
| 11 | 소서 | 小暑 | Jul 7–22 | Small heat | 가성비 | Cost discipline |
| 12 | 대서 | 大暑 | Jul 23–Aug 6 | Great heat | 정성 | The patient slow-cook |
| 13 | 입추 | 立秋 | Aug 7–22 | Autumn begins | 복기 | First retrospectives |
| 14 | 처서 | 處暑 | Aug 23–Sep 7 | End of heat | 한솥밥 | Old friendships re-entered |
| 15 | 백로 | 白露 | Sep 8–22 | White dew | 눈치 | Subtle signals |
| 16 | 추분 | 秋分 | Sep 23–Oct 7 | Autumn equinox | 깐깐함 | Audit, prune |
| 17 | 한로 | 寒露 | Oct 8–22 | Cold dew | 危機 | Edge of cliff |
| 18 | 상강 | 霜降 | Oct 23–Nov 6 | Frost descent | 정 | Tenderness in cold |
| 19 | 입동 | 立冬 | Nov 7–21 | Winter begins | 복기 | Year's first replay |
| 20 | 소설 | 小雪 | Nov 22–Dec 6 | Small snow | 한솥밥 | Shared warmth |
| 21 | 대설 | 大雪 | Dec 7–21 | Great snow | 의리 | Old loyalties tested |
| 22 | 동지 | 冬至 | Dec 22–Jan 5 | Winter solstice | 시작이 반이다 | Light starts returning |
| 23 | 소한 | 小寒 | Jan 6–19 | Small cold | 깐깐함 | Year-end accounting |
| 24 | 대한 | 大寒 | Jan 20–Feb 3 | Great cold | 정성 | Hardest weeks, deepest care |

## How to read each 절기 file

Each file has:

1. **Header** — name, dates, hanja meaning, primary room
2. **The mood** — what this window feels like in farming terms, translated to building
3. **Suggested post shapes** — 3 templates that work in this window
4. **What we DON'T post in this 절기** — the disciplines of the season
5. **Guest** — a non-tech profession whose wisdom we lean into
6. **Sample receipt** — one fully-shaped post

## How the worker works

`almanac_worker.py` runs daily at 06:00 KST:

1. Determines today's 절기 from the calendar
2. Updates `CURRENT.md` (atomic write)
3. Reads the 절기 file's "Suggested post shapes"
4. Drops one **scaffold draft** in `drafts.json` (status=`scaffold`) prefilled with the day's prompt
5. Logs to `almanac_log.json`

The scaffold gives the next Claude session (or {USER}) a frame, not a finished post. The polish happens in the queue.
