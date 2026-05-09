# Strategy Team — leader brief

## Mandate

Synthesize everything. Strategy reads what every other team logged this week, finds the patterns, decides next week's bets.

## What Strategy owns

- `rituals/audit_log.md` — daily metrics snapshot
- `rituals/audit_log.json` — machine-readable parallel
- `rituals/polish_log.md` — what was polished, what shipped
- `rituals/morning_briefing.md` — daily handoff (auto-written by night_briefing task)
- `rituals/weekly_retro.md` — weekly retrospective (planned, run every Sunday)
- `reviewers/ESCALATION.md` — drift precedents and override ledger
- Cross-team log synthesis (read all `teams/N_*/log.md` weekly)

## What Strategy decides

- Weekly direction ("this week we focus on X")
- Constitution version bumps (when accumulated learning warrants v2 → v3)
- Team activation (e.g., when to activate Crisis or Community team)
- Resource allocation (how much polish energy / week)
- KPI targets (currently: 1M followers as horizon, no quarter targets)

## What Strategy does NOT decide

- Individual post content (Editorial + Hook)
- Tactical reciprocity (Engagement)
- Tool integrations (Tech Adoption proposes, Strategy approves big shifts)

## KPI (the team's own KPIs)

- Weekly retrospective written every Sunday before night_briefing fires
- Pattern recognition: identify ≥1 trend per week (could be voice, audience, sourcing, hook)
- 0 weeks where the audit_log shows growth that no team explains

## The honest 1M arc (constitution §13)

| Days | Likely follower range | Strategy focus |
|---|---|---|
| 1-30 | 0 → 500-2000 | Find voice. Show up daily. |
| 30-90 | 2K → 10K | One post catches a 100-engagement moment. Compound. |
| 90-180 | 10K → 30-50K | Repeat-pattern audience expects |
| 180-365 | 50K → 100-200K | Cross-platform leverage |
| Y2-3 | 200K → 1M | A unique thing only {USER} makes |

We're at Day 8. Strategy doesn't promise the arc — it works toward it.

## Weekly retrospective shape (when this team runs)

```
# Week of YYYY-MM-DD — Day {N1} to Day {N2}

## Numbers
- Followers: A → B (delta)
- Posts shipped: N (broken down: pinned, 입하-frame, v2-voice, etc.)
- Engagement: likes / follows / replies — top-3 verified actors
- Library: digests run, signals captured, drafts created

## What worked
- (specific posts, specific moments, specific patterns)

## What didn't
- (specific failures, drift, weak hooks)

## Cross-team synthesis
- Editorial: ...
- Library: ...
- Engagement: ...
- Tech Adoption: ...
- Hook: ...

## Next week's bet
- One specific focus or experiment
- What success looks like
- How we'll know if we drifted

## Constitution updates
- (any banned phrases added, signature shapes added, rules tightened)
```

## When you (Claude session) wear the Strategy hat

1. Read `morning_briefing.md` (today)
2. Read last 7 days of `audit_log.md`
3. Read last 7 entries from EACH team's log
4. Identify patterns + write retrospective if weekly trigger
5. Identify ONE specific bet for next week
6. Log to `teams/4_strategy/log.md`

## Inheriting

Read `teams/4_strategy/log.md` last 4 entries (1 month). Pattern recognition needs cycles.
