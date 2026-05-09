# Editorial Team — leader brief

## Mandate

Guard the **voice**. Every published post is a thread in the same fabric. Editorial owns continuity, constitution compliance, and the council of reviewers.

## What Editorial owns

- `constitution.md` (v2) — the voice north star
- `voice/banned.md` — never-write list
- `voice/signatures.md` — recognizable shapes
- `reviewers/` — 6-lens council (now 7 with Hook Auditor — see Team 6)
- `workers/quality_gate.py` — mechanical pre-publish check
- `rituals/polish_session.md` — the polish workflow
- `rituals/polish_log.md` — append-only polish history

## What Editorial decides

- Whether a draft ships (council 0 FAIL = ship; 1 FAIL = revise; 2+ FAIL = drop)
- Banned phrase additions (when a drift is caught, add to `banned.md`)
- New voice exemplars (when a real-world post matches our voice, add to `signatures.md`)
- When constitution needs revision (raise to Strategy Team)

## What Editorial does NOT decide

- Topics (Library Team surfaces, Strategy Team prioritizes)
- Hook strength (Hook Team #6 owns first 3 lines)
- When to engage (Engagement Team)
- Stack changes (Tech Adoption Team)

## Workflow

```
[Library digest] → [Polish session draft] → 
  Hook Team audit (first 3 lines) → 
  quality_gate.py (mechanical) → 
  Council of 6 (now 7) reviewers → 
  Editorial final pass (whole-post coherence) → 
  Schedule via drafts.json status=pending
```

Editorial fires LAST in the polish flow. By the time we audit, hook + mechanical + council are done. Our pass is whole-post coherence — does this read as {USER}, end to end?

## Decision authority

- **Veto**: Editorial can block any draft from publishing
- **Force-revise**: can require revision before re-running council
- **Cannot**: cannot generate posts from scratch (that's polish session work)
- **Cannot**: cannot override Hook Team veto

## KPI

- 100% of published posts pass council
- 0 drift incidents per month (drift = a published post {USER} wishes weren't published)
- Constitution updated when learning compounds (≥1 new signature pattern per month)

## When you (Claude session) wear the Editorial hat

1. Read `constitution.md` v2 fully (especially §3, §4, §4.5, §4.6, §5)
2. Read latest entries in `voice/banned.md` and `voice/signatures.md`
3. Read latest 3 days of `polish_log.md`
4. Then audit the draft against the constitution as a whole
5. Log to `teams/1_editorial/log.md`

## Common Editorial calls

- "Hook is strong but body lectures the reader" → revise body
- "Receipt is real but voice slipped to v1 ('Korean builder, Day X')" → revise stamp
- "Concept stacking (3+ rooms)" → cut to 1-2
- "Tone is performance-vulnerable rather than honest-vulnerable" → revise

## Inheriting

Read `teams/1_editorial/log.md` last 7 entries. Continuity matters more here than anywhere else.
