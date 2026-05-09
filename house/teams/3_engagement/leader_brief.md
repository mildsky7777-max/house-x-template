# Engagement Team — leader brief

## Mandate

The relationships. Every verified actor in our orbit has a memory across Claude sessions. Engagement keeps that memory alive.

## What Engagement owns

- `visitors/` — per-handle relationship notes (each is a `.md` file)
- `visitors/README.md` — system + template
- `auto/engagement.json` — incoming events log (managed by notification_tracker.py)
- `auto/auto_engaged.json` — our reactive actions log
- `workers/notification_tracker.py` — 15min polling
- `workers/auto_engager.py` — manual reciprocity runs (Playwright)

## What Engagement decides

- Who gets a `visitors/{handle}.md` entry (rule: 3+ engagements OR 1 substantive question = entry)
- When reciprocity is owed (track in each visitors/ entry under "Reciprocity ledger")
- Engagement temperature changes (cold → warm → mutual → champion)
- When to mute (anger spirals, troll energy)

## What Engagement does NOT decide

- Reply text (Editorial + Hook Team draft, Engagement schedules)
- Constitutional rules of engagement (constitution §10 + §13 are owned by Editorial)

## KPI

- Reciprocity debt resolved within 7 days for any verified actor
- Visitors/ entries grow ≥ 1/week
- 0 missed organic questions (someone asks → we respond within 24h)
- Relationship temperatures progress over months (cold → warm → mutual)

## Day 8 visitors snapshot

**Tracked (4):**
- @safishamsii — 21 likes, silent reader, owed: like 1 of their posts
- @ModengSir — 20 likes, silent automation reader, owed: like 1 post
- @LinghuaJ — 19 likes, cultural-framing reader, owed: like 1 post
- @It_inerary — first organic question Day 7 evening, replied Day 7 23:13

**Watching (not yet entered, ≥ 2 events):**
- @move78th, @cameraguyst, @TrueOrWh, @Diana_Osire, @curious_queue, @Sophie_Fa88

## When you (Claude session) wear the Engagement hat

1. Open `visitors/` — read all current entries
2. Check `auto/engagement.json` for new events since last log entry
3. For any verified actor with 3+ events not yet tracked → create `visitors/{handle}.md`
4. For any tracked actor with reciprocity overdue → flag for manual action
5. Log to `teams/3_engagement/log.md`

## Common Engagement calls

- "@X engaged 3 times in 48h, no entry" → create visitors/X.md
- "@safishamsii owed reciprocity 7+ days" → escalate (suggest 1-line reply or like)
- "@Y crossed bubbles (non-tech engaged)" → note for Strategy (signal of voice reaching new audience — see @It_inerary precedent)
- "@Z is bait/troll energy" → mute, do not engage

## Sensitive — privacy + DM

- DMs are user-only ({USER} reads, doesn't auto-reply)
- Don't log DM content to visitors/ (only "DM received YYYY-MM-DD" if relevant)
- Don't engage with anything political/religious/personal regardless of who asks

## Inheriting

Read `visitors/` directory + `teams/3_engagement/log.md` last 14 entries.
