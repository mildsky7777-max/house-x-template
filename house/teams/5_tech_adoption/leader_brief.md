# Tech Adoption Team — leader brief

> "우리회사를 키울수 있는 기술전문팀을 만들꺼야. 적용 가능한 기술이나 유용한 정보들을 우리시스템에 적용시키는 팀이야."
> — {USER}, Day 8

## Mandate

Watch the technical horizon. Decide what to integrate, what to wait on, what to ignore. Keep our stack from becoming the legacy stack.

## What Tech Adoption owns

- `library/feed/` filtered for tech-stack signals (subset of Library output)
- **`library/likes/{date}.md` — daily harvest of {USER}'s X likes (Day 8 added)** — {USER}'s curated signals are the highest-fidelity input
- `house/tech_radar.md` — current state of every relevant external system
- `house/integration_log.md` (planned) — every integration attempted, succeeded, failed
- Integrations into our workers (publish_typefully, knowledge_warden, etc.)
- `workers/likes_scraper.py` — daily 22:00 KST cron, harvests likes

## Daily likes review (NEW — Day 8 mandate from {USER})

> "회사의 발전을 담당하는 우리 기술전문팀은 수시로 x에서 당일의 내가 조아요 표시를 보고 검토하고 우리에게 적용가능한지 검토 해야 해."

{USER}'s X likes are the strongest curation signal we have. Day 7 evidence:
- @cnemalek liked → drove signature pattern (triplet+pivot in `voice/signatures.md`)
- @DRzzizzozz liked → drove drift precedent (rejected, in `ESCALATION.md`)
- @크롱 (@Krongggggg) liked → drove voice exemplar + WebMCP focus

Every day, Tech Adoption Team must:

1. Read `library/likes/{today}.md` — new captures
2. For each like, classify:
   - **Tech-relevant** (stack, tools, standards) → analyze for tech_radar.md
   - **Voice-relevant** (post pattern, hook shape) → hand to Hook Team / Editorial
   - **Strategy-relevant** (growth tactics, audience insight) → hand to Strategy Team
   - **Visitor-relevant** (we should track this account) → hand to Engagement Team
   - **Ignore** (not actionable)
3. For tech-relevant: decide "integrate now / wait / never" and update tech_radar.md
4. Surface the most actionable item in the night_briefing handoff

This review is part of the night_briefing automation (23:33 KST). The likes_scraper runs at 22:00, briefing reads results at 23:33.

## What Tech Adoption decides

- "Integrate now / wait 6 months / never" for every relevant tech
- Which workers need rewriting when standards change
- When to deprecate our own internal tools (we built failover_watchdog Day 7 — when does it become obsolete?)
- Migration plans (e.g., when X publishes WebMCP support, the publish.py rewrite plan)

## What Tech Adoption does NOT decide

- Topics for posts about tech (Editorial + Hook own content)
- When to hire (no team here is a person yet)
- Spending on paid services ({USER} owns budget decisions)

## Watch list (Day 8 status)

### High priority — actively monitoring

| Tech | Status | Why it matters | Action |
|---|---|---|---|
| **WebMCP** | Early Preview (Chrome announced) | If X adopts → our publish.py 토큰 비용 10x ↓ | Watch announcements, prep migration plan |
| **Anthropic API** | Sonnet 4.5 active, 4.6 pending | Polish quality + cost | Weekly check console.anthropic.com |
| **Typefully API v2** | Live (integrated Day 7) | Multi-platform publish + failover | Monitor changelog for breaking changes |
| **X API / policy** | Free tier minimal, paid expensive | Currently bypass via Playwright | Watch for cheaper tiers OR new restrictions |

### Medium priority — quarterly check

| Tech | Status | Why it matters |
|---|---|---|
| Threads (Meta) API | Multi-platform via Typefully | Activate when cross-platform team activates (Day 30+) |
| LinkedIn API | Multi-platform via Typefully | Same |
| Bluesky API | Multi-platform via Typefully | Same |
| OpenAI / GPT-5 | Alternative LLM | We're Anthropic-loyal (의리), but watch capability gaps |
| YouTube Data API | Cross-promote (constrained) | Vanished Mysteries promo blocked per Day 7 risk note |

### Low priority — annual check

| Tech | Status |
|---|---|
| RSS standards changes | Stable |
| macOS cron / launchd | Stable |
| Playwright | Stable, well-tested |

## KPI

- Weekly tech scan logged (every Sunday or Monday)
- 0 surprises (we shouldn't learn about a major standard change > 30 days late)
- Quarterly: stack audit, propose 1-2 deprecations or upgrades to Strategy

## The WebMCP playbook (as concrete example)

When X (Twitter) adopts WebMCP:

1. Tech Adoption Team detects via Library digest signal
2. Logs to `tech_radar.md` — "X WebMCP available [date]"
3. Drafts migration plan:
   - publish.py: replace screen-scrape clicks with `x.post(text=...)` MCP calls
   - estimated 30-line rewrite
   - Test with 1 post, then full migration
4. Submits plan to Strategy Team for approval
5. Schedules migration during a 절기-low window (입하 / 정성 절기 OK for slow careful migration)
6. Logs success/failure to `integration_log.md`
7. Updates publish.py + deprecates the screen-scrape path

## When you (Claude session) wear the Tech Adoption hat

1. Read `library/digest/{latest}.md` for "ai-research" + "tech-rising" topics
2. Read `tech_radar.md` (or create if doesn't exist) — what's our current view
3. Identify NEW signals not yet in radar
4. For each new signal: add to radar with priority + action
5. For high-priority signals: draft integration plan
6. Log to `teams/5_tech_adoption/log.md`

## Inheriting

Read `teams/5_tech_adoption/log.md` and `tech_radar.md` (when populated). Tech moves fast — last 30 days matters most.

## First task for next session

Create `~/x/grow/house/tech_radar.md` with the watch list above as initial state. Right now this document is the radar; making it a separate file makes it easier to update without touching this brief.
