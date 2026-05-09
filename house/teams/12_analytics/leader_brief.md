# Analytics Team — leader brief (Day 8 added)

## Mandate

Receipt_ledger gives us numbers. Analytics gives us **causation**. Without this team, we can't answer "what's actually working?"

## What Analytics owns

- Post-level conversion data (impressions / engagement / follower delta per post)
- Time-of-day analysis (when do OUR posts land?)
- Hook pattern → engagement correlation (which patterns convert?)
- Weekly experiment design (what we're testing this week)
- `analytics/{date}.md` (planned) — daily analytical reports
- `analytics/experiments.md` (planned) — registered experiments + outcomes

## What Analytics decides

- Which experiments to run weekly (test variations of: post time, hook pattern, length, language, format)
- When data is statistically meaningful (rule of thumb: ≥30 datapoints before drawing conclusions)
- Recommendation to Strategy: "Concentrate on X based on Y data"
- Hook Pattern library updates (which patterns earn updates to HOOK_PATTERNS.md)

## What Analytics does NOT decide

- What gets posted (Editorial + Hook + Strategy)
- Strategic direction (Strategy synthesizes Analytics + other teams' outputs)
- Tools to integrate (Tech Adoption)

## KPI

- Daily analytics report by Day 30 (when we have enough data)
- 1+ experiment run per week with documented hypothesis + result
- Hook Pattern library updated with empirical data within 30 days
- Quarterly: full retrospective with statistically meaningful conclusions

## Data sources

- `auto/engagement.json` — incoming likes / follows / replies (per actor)
- `auto/drafts.json` — published posts with timestamps
- `rituals/audit_log.json` — daily snapshots (for follower deltas)
- `house/library/likes_seen.json` — what {USER} likes (curation signal)
- (External — manual or future) X Analytics dashboard data

## Current data limitations (Day 8 honest)

- We don't have impressions data automated. Visible only when {USER} manually checks profile.
- Reply rate available via notification_tracker but slow (15min poll).
- No A/B framework (would require deliberate experimentation).
- No follower-source attribution (which post made @X follow us).

**Action**: Day 30+ acquire X Premium analytics export OR build a profile-scrape worker for daily impression data. Tech Adoption Team to scope.

## Experiment framework (when activated)

For each experiment:

1. **Hypothesis** — "If we post at 09:00 KST instead of 14:00, engagement will be 30% higher"
2. **Variants** — A (control) vs B (test). Run for ≥7 days.
3. **Sample size** — minimum 5 posts each variant
4. **Metric** — primary (likes/post), secondary (follows/post)
5. **Decision rule** — what difference triggers adoption
6. **Result** — recorded with raw data
7. **Action** — adopt / reject / extend test

Day 8 experiment seed (suggested by morning_briefing data):

> "Posts published in afternoon KST (12:00-15:00) reach more verified actors than morning KST (06:00-09:00)" — TEST over next 14 days

## Hook Pattern empirical update workflow

Every 7 days:
1. Pull list of published posts in last 7 days
2. Tag each with hook pattern from HOOK_PATTERNS.md
3. Calculate: avg engagement per pattern
4. Update HOOK_PATTERNS.md "Post-mortem" section with data
5. Recommend Hook Team: which patterns to use more / less

## When you (Claude session) wear the Analytics hat

1. Read latest `audit_log.md` (last 7 days)
2. Read `engagement.json` events from last 7 days
3. For each published post: compute likes / replies / follows attributable
4. Identify pattern (best post, worst post, time clustering)
5. Update `analytics/{date}.md` if Sunday or notable signal
6. Log to `teams/12_analytics/log.md`

## Honest disclosure

Analytics requires DATA. At Day 8 with ~5 v1 + 1 v2 posts, the data is too thin for serious analysis. Real value starts Day 30+.

For now: **observe, log, don't conclude prematurely.**

## Inheriting

Read `teams/12_analytics/log.md` last 14 entries. Pattern detection requires enough cycles.
