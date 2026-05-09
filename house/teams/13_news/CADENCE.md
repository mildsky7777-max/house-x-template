# Cadence Rules — for News Desk + Editorial scheduling

> "좀더 자주 할수 있어? 그리고 시간대를 들쭉 날쭉하게 해야 ai 인지 티가 안 나."
> — {USER}, Day 8 evening

## The problem with fixed slots

Old slot guidance was: 06:00, 09:00, 13:00, 17:00, 21:00 KST.

That's **bot-detection signal**. Every account that posts at exact :00 hour daily looks automated. Even ±15min jitter is insufficient when the HOUR is always the same.

## New cadence rules (Day 8 evening)

### Active windows (not fixed slots)

Choose ONE window per scheduled post; randomize within:

| Window | KST range | Why |
|---|---|---|
| **Dawn** | 05:00 – 08:30 | early Korean readers + 새벽 posts (정성/입하 fit) |
| **Morning** | 08:30 – 11:00 | Korean morning + US East late evening prev day |
| **Lunch** | 11:30 – 14:30 | Korean lunch + US East morning |
| **Afternoon** | 14:30 – 17:30 | Korean afternoon + US East early morning |
| **Evening** | 18:00 – 21:00 | Korean evening + US East work day start |
| **Night** | 21:00 – 23:30 | Korean night + US East lunch |

### Random-minute rule (applies WITHIN a window)

When picking the actual fire time:

1. Pick a window (above)
2. Pick a random hour within that window
3. Pick a random minute that is **NOT** :00, :15, :30, :45 (these look scheduled)
4. Result examples: 07:23, 12:47, 16:09, 20:38

The scheduler.py adds another ±15min jitter on top — extra randomness.

### Daily volume target (revised Day 9 morning per {USER} mandate — spam concern not real)

> "많이 활동한다고 해서 spam으로 걸리는 건 아닌거 같아." — {USER}, Day 9 morning

X does NOT penalize high volume of quality posts. Top accounts (Mr Beast, Marc Andreessen, news commentators) post 5-15+/day routinely. Spam triggers are: identical reposts, mass @-tagging, follow churning, DM spam, bot timing patterns. **Volume alone is not a trigger.**

| Stage | Target | Heavy |
|---|---|---|
| Day 8-30 | **5-10 posts/day** baseline | up to 15 on news days |
| Day 30-90 | 7-12 posts/day | up to 20 |
| Day 90+ | 10-15 posts/day | up to 30 |

The constraint is QUALITY (council), not volume. The 8-reviewer council still gates every post. ZERO ships > weak ships rule unchanged.

### Day variation rules (revised)

- Variation still matters (avoid identical N every day)
- But: light days are RARE, not 2/7. Maybe 1/7.
- Rest days = OK if 진짜 nothing earned. Don't force.
- Heavy = NORMAL when news momentum + library digest is rich.

### What still gates volume

- Council pass rate — every post must pass 8 reviewers
- Quality_gate.py mechanical checks
- Source diversity rules (cooldowns)
- Format rotation
- Authenticity Auditor (Reviewer #8) — if voice drifts, cut volume immediately

### Two-in-a-row pattern (allowed)

Humans often post twice within an hour ("just thought of this..."). Allowed:
- Maximum 2 consecutive posts within 60 minutes
- Spaced at least 15 minutes apart
- Different topics or "follow-up" framing

### Forbidden patterns (look bot)

- ❌ Posting at exact :00 daily for 3+ days
- ❌ Same minute (e.g., :15) on consecutive days
- ❌ Post at the exact same hour (e.g., always 14:00) for 5+ days
- ❌ Identical N-posts-per-day for a week
- ❌ Posting AT polish task fire times (11:31 / 15:32 / 19:32 / 23:33) — too suspicious
- ❌ Rigid spacing (every 4 hours exactly)

## How polish tasks pick slots

When `house-daily-polish` (or `house-evening-polish`) drafts a post:

```python
import random
from datetime import datetime, time, timezone, timedelta

WINDOWS = [
    ("dawn",       5,  8.5),
    ("morning",    8.5, 11),
    ("lunch",      11.5, 14.5),
    ("afternoon",  14.5, 17.5),
    ("evening",    18, 21),
    ("night",      21, 23.5),
]

def pick_random_slot(target_date: date, prefer: str = None) -> datetime:
    """Pick a random KST datetime within an active window for target_date."""
    KST = timezone(timedelta(hours=9))
    window = next(w for w in WINDOWS if w[0] == prefer) if prefer else random.choice(WINDOWS)
    name, start_hr, end_hr = window
    # Random hour and minute
    hour = random.randint(int(start_hr), int(end_hr) - 1)
    # Avoid :00 :15 :30 :45 (looks scheduled)
    minute = random.choice([m for m in range(60) if m % 15 != 0])
    return datetime.combine(target_date, time(hour, minute), tzinfo=KST)
```

Polish task prompt should USE this function or replicate its logic.

### Checking history before scheduling

Before adding a new pending draft to drafts.json, the polish task must:
1. List the last 10 published / pending drafts
2. Look at their fire times (in KST)
3. AVOID picking a slot within ±30 minutes of any of the last 5
4. AVOID picking a slot at the same hour as 3+ recent posts

If the candidate slot fails these checks, re-roll.

## Verification — once a week

Strategy Team weekly retro must check:

- Posting time histogram (last 7 days) — should look scattered, not clustered
- Hour-of-day variance — std deviation > 4 hours
- Daily count variance — should vary
- Exact-time repeats — < 10% of posts at same hour

If patterns emerge that look bot-like → tighten randomness.

## Why this matters for 1M arc

Bot detection = shadowban risk + reader instinct. A reader scrolling and noticing "this account always posts at exactly 9:00" creates suspicion. Suspicion compounds.

Human-feel = trust = retention = compound growth.

This is part of the same discipline as Reviewer #8 Authenticity Auditor. Voice + Timing both must read as a person.
