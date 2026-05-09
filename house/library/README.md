# The Library — knowledge warehouse for @YOUR_HANDLE

> "우리집이 도서관 같은 지식의 창고가 되자. 누구보다 빠르게 찾고 전달 해야 해. 그리고 만들어야 해."
> — {USER}, Day 7

## What this is

The Library is the **inward** half of the house. The X account is the front yard (outward). The Library is the storeroom: where signals come in, get tagged, get cross-indexed, and become the fuel for future posts.

The Library never publishes. It collects, sorts, summarizes. Then a Claude session (or {USER}) reads the digest, picks the right thread, polishes a scaffold, schedules a post.

This separation is the constitution's quality_gate principle taken seriously: **collection ≠ publication**.

## Compliance with the 절기 calendar

The Library runs **every 절기**, but its **emphasis** rotates:

| 절기 | Library emphasis |
|---|---|
| 곡우 → 입하 → 소만 | gather widely, tag carefully, don't react |
| 망종 → 하지 | distill to actionable signals; this is when the harvest of the storeroom feeds posts |
| 소서 → 처서 | prune the library — what didn't lead anywhere, archive |
| 입추 → 추분 | re-index, audit which sources actually paid off |
| 한로 → 동지 | 정성 mode — slow re-reading of old captures, finding concept-level patterns |
| 소한 → 대한 | the year's deepest re-read; constitutional updates born here |

Right now: **입하 (May 5–20).** Library is in **gather widely** mode. Don't optimize for output; optimize for completeness of input.

## Directory structure

```
library/
├── feed/             # raw daily captures, one MD per date
│   └── 2026-05-05.md
├── by_room/          # cross-indexed by Korean concept (9 rooms)
│   ├── 가성비.md
│   ├── 깐깐함.md
│   └── ...
├── by_jeolgi/        # filtered by current 절기 fit
│   └── 입하.md
├── X_orbit/          # curated X accounts + their best takes (manual + auto)
│   ├── README.md
│   └── reading_list.json
├── digest/           # human-readable summaries (every 6 hours)
│   └── 2026-05-05T14.md
└── INDEX.md          # rotating "current shelf" — this week's hot signals
```

## Workers (planned + active)

| Worker | Cadence | Status | Purpose |
|---|---|---|---|
| `knowledge_warden.py` | 90 min | ✅ Day 7 | Pull RSS sources, tag, write to feed/ |
| `digest_writer.py` | 6 hours | ✅ Day 7 | Distill recent feed entries into a digest |
| `room_indexer.py` | daily 22:00 | ✅ Day 7 | Update by_room/, by_jeolgi/ files |
| (planned) `x_orbit_reader.py` | daily | — | Read curated X accounts' recent posts (later) |

## Sources (Day 7 starter set)

**RSS-based (no API, no auth):**
- Hacker News frontpage
- The Verge
- MIT Technology Review
- Daring Fireball
- IndieHackers
- Korea Herald (English)
- 한국 IT 매체 (planned: 디지털타임스, ZDnet Korea, Bloter — later)

**X-based (via existing trend_scanner output):**
- trend_scanner.py already finds Tier 1-2 verified posts in our queries
- Library hooks into its `targets.json` output → `X_orbit/`

**Visitors-based:**
- `~/x/grow/house/visitors/{handle}.md` — manual relationship notes
- High-engagement verified actors (@safishamsii, @ModengSir, @LinghuaJ, ...)

## Use pattern (for the next Claude session)

When you sit down to write a post:

1. Open `library/INDEX.md` — what's hot this week?
2. Open `library/by_jeolgi/{current}.md` — what fits this 절기?
3. Open `library/by_room/{room}.md` — what fits the room you want?
4. Pick a signal. Polish a scaffold around it. Run quality_gate. Schedule.

The library doesn't replace your judgment. It feeds it.
