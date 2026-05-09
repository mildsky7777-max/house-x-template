# The Company — @YOUR_HANDLE X-only operation

> "X 전용회사를 만들꺼야. 네 안에서. 각분야의 전문팀을 구성할꺼야."
> — {USER}, Day 8

The house is now structured as a small focused company. Each team has a defined role, scope, KPI, and **agent persona** that any Claude session can adopt by reading that team's `leader_brief.md`.

## Activated teams (9 — running now)

| # | Team | Korean | Role |
|---|---|---|---|
| 1 | Editorial | 편집부 | Voice, council of reviewers, quality gate |
| 2 | Library | 자료실 | 24/7 signal gathering, indexing, digests |
| 3 | Engagement | 관계부 | Visitor relationships, reciprocity, notifications |
| 4 | Strategy | 전략기획부 | Metrics, retrospectives, weekly bets |
| 5 | Tech Adoption | 기술도입부 | New tools/standards integration + daily {USER} likes review |
| 6 | Hook | 훅 기획팀 | First-3-lines, virality, attention magnetism |
| 11 | Distribution | 유통부 | Reply-up cadence, X Lists, strategic follow, DM |
| 12 | Analytics | 분석부 | Post-level conversion, experiments, A/B |
| 13 | **News Desk** | **뉴스부** | **Korean ↔ English tech news bridge — {USER}'s "ONE thing" hypothesis** ← Day 8 added |

## Reserve teams (4 — activate when warranted)

| # | Team | Activation trigger |
|---|---|---|
| 7 | Crisis | Drift incident / X policy violation / follower drop |
| 8 | Production | Banner/avatar redo, infographics, future video |
| 9 | Community | Hit 1,000 followers (~ Day 90 estimate) |
| 10 | Cross-Platform | Day 30+ stable cadence |

## How a Claude session adopts a team role

1. Identify which team's work is needed (e.g., polishing a draft → Editorial)
2. Read that team's `leader_brief.md` BEFORE doing the work
3. Use that team's KPI and decision authority during work
4. Log to `teams/N_name/log.md` after work

A single Claude session can wear MULTIPLE hats sequentially. The team docs are the costume rack.

## Inter-team interfaces

- **Library → Editorial**: digest signals feed polish sessions
- **Library → Tech Adoption**: tech-tagged signals + {USER} likes feed daily radar
- **Editorial → Hook**: every draft must pass Hook audit (Reviewer #7) before quality_gate
- **Editorial → Authenticity**: every draft must pass Authenticity audit (Reviewer #8) — guards against AI-tells
- **Editorial → Distribution**: reply drafts go through both before sending
- **Editorial → Engagement**: visitor-specific replies cross-checked
- **Distribution → Engagement**: reply-up candidates surfaced from notifications
- **Analytics → Hook**: empirical hook pattern data updates HOOK_PATTERNS.md
- **Analytics → Strategy**: experiments + retrospectives inform weekly bets
- **Strategy → all teams**: weekly retrospective synthesizes every team's log
- **Tech Adoption → Editorial + Library + Distribution**: tool changes ripple
- **Crisis → all**: when activated, freezes others until resolved

## Decision authority hierarchy

```
{USER} (owner) — final say, override anyone
  ↓
Strategy Team — sets weekly direction, allocates attention
  ↓
Editorial / Hook — voice + audience pull (cannot ship without both)
  ↓
Library / Engagement / Tech Adoption — execute their domain autonomously
  ↓
Reserves — silent until activated
```

## What this is NOT

- This is not a roleplay. The teams are decision-making frames, not characters.
- This is not bureaucracy. If a team would slow real work, skip it.
- This is not separate Claude sessions running in parallel (yet — could become that at scale).
- This is not a substitute for {USER}'s judgment. The owner overrides any team decision.

## When to retire / merge teams

If a team has logged nothing for 30 days → it's dead weight. Delete or merge with adjacent team.

If two teams are constantly approving the same work → merge them.

If a reserve team activates and stays active for 30+ days → promote to activated, find another reserve to deprecate.
