# Tech Radar — Tech Adoption Team

> Owned by Team 5 (`teams/5_tech_adoption/`). Updated weekly (Sunday) + on every notable signal.

The radar tracks every external system / standard / tool that could affect our stack. Each item has a status, a "why it matters," and an action.

**Last updated:** 2026-05-09 (Day 11 morning — first proactive tech-research run, baseline established)

---

## Adopt now (in production)

| Tech | Integrated | Status | Notes |
|---|---|---|---|
| Anthropic Claude API (Sonnet 4.5 / Opus 4.7) | Day 1 | ✅ Live | Opus 4.7 GA since 2026-04-16. Used for the Claude Code session itself |
| Playwright + persistent Chrome profile | Day 1 | ✅ Live | publish.py / notification_tracker / likes_scraper / x_trends_scanner |
| Flask local (port 5050) | Day 1 | ✅ Live | drafts queue + approval API |
| RSS catalog (9 feeds) | Day 7 | ✅ Live | knowledge_warden hourly |
| Typefully API v2 | Day 7 | ✅ Live | failover via failover_watchdog. v1 deprecates 2026-06-15 — we're already on v2, safe |
| {USER}'s X likes scraper | Day 8 | ✅ Live | daily 22:00 KST — strongest signal source |
| x_trends_scanner.py | Day 10 | ✅ Live | hourly Korea trend capture — note: many entries showing "·" placeholder, scrape selector likely needs fix |
| 8-reviewer council + quality_gate.py | Day 7-9 | ✅ Live | AI-as-gate architecture (validated Day 9 by @haaaaanna__) |

## Trial (active testing or recent integration)

| Tech | Watching since | Status | Action |
|---|---|---|---|
| Hook Auditor (Reviewer #7) | Day 8 | 🆕 First audit on YC v2 | Validate after YC v2 lands |
| Pillow image composition | Day 7 | ✅ Used for banner | Keep ad-hoc for Production team |
| Open-source CapCut alt (browser-local) | Day 9 | 🟡 Tool noted | Future Production Team — no current need |
| GPT Image 2 × Seedance 2.0 | Day 9 | 🟡 Tool noted | Banner / infographic upgrade path |
| Agent One (AI film) | Day 9 | 🟡 Far-future | Cross-platform video |
| Claude × Blender direct integration | Day 9 | 🟡 Far-future | 3D visual identity |
| **Anthropic Advisor Tool (BETA)** | **Day 11** | 🆕 May 2026 release | Sonnet/Haiku executor + Opus advisor → near-Opus quality, lower cost. **Test next 7 days**: prototype a polish run where Sonnet executes 8-reviewer pass + Opus advisor adjudicates conflicts. If quality holds → could 3-5x our compute budget at same cost. |
| **Typefully v2 performance-data pull** | **Day 11** | 🆕 April 2026 endpoint | Pull X post analytics via API for night_briefing. **Test next 7 days**: wire `failover_watchdog` or new `metrics_puller.py` to feed `morning_briefing.md` numbers section. |

## Assess (under evaluation)

| Tech | Why we care | Action |
|---|---|---|
| **WebMCP** (Chrome Early Preview) | If X adopts → publish.py 토큰 비용 10x ↓, reliability ↑ | Watch announcements weekly |
| Sonnet 4.6 (1M ctx, GA) / Sonnet 4.8 (anticipated) | Polish quality bumps | Follow Anthropic changelog. 4.6 1M-ctx already GA at standard pricing — no beta header needed |
| **Threads via Typefully API v2** | 450M MAU April 2026 (+175M YoY); Threads Ads launched 2026 with creator revenue share. Brand adoption accelerating, lower competition window. | **Move from Day 30+ → Day 14-20 activation candidate.** Cross-Platform Team go-ahead still needed from {USER} (per AUTONOMY.md §5). |
| **Claude Code auto mode** (research preview) | Long-running permissions for autonomous polish without per-action prompts. Currently Team-tier. | Watch for Pro/Max rollout. Don't apply to live workers without explicit {USER} sign-off (publish actions are blast-radius high). |
| **X Premium Creator Revenue Share** | $8/mo Premium ✓; threshold = 500 verified followers + 5M impressions/90d. We have Premium; follower/impression status unknown. | Day 11+ assess: have we cleared 500 verified followers? Pull the impression number from new Typefully analytics endpoint once integrated. |
| **Claude × Office (Excel/PowerPoint/Word/Outlook beta)** | Cross-app context flow — could power infographic / one-pager generation | Far-future for Production Team |
| **Claude Code skill marketplace** (4,200+ skills, 770+ MCP servers) | Off-the-shelf augmentations — quarterly browse | Calendar a 절기-low-window survey |

## Hold (intentionally NOT integrating)

| Tech | Why we're holding |
|---|---|
| X API (paid tiers) | Playwright suffices; price-to-performance bad |
| Engagement pods | Constitution §8 forbids |
| Auto-reply via Claude API | Requires dedicated Anthropic API key (we don't have one yet; OAuth token Claude Code session-only) |
| YouTube Data API for Vanished Mysteries | Day 7 risk note: AI-made content → report risk if promoted (reinforced by EU AI Act Article 50 below) |
| **AI voice cloning / synthesis (ElevenLabs, VoxCPM2, Voicebox, Fish Speech, Realtime TTS-2)** | {USER} explicitly rejected Day 1 (Korean naturalness). EU AI Act Article 50 (effective 2026-08-02) adds machine-readable-label requirement → compounding risk. Permanently held. |
| **AI auto-tweet generators (e.g., @maruo_0314 model)** | Already in `reviewers/ESCALATION.md` Day 9 drift precedent (engagement-bait + AI-as-generation, opposite of our gate model). EU AI Act Aug 2026 reinforces. |
| **External-link-heavy posts** | X algorithm penalizes external links 30-50% reach reduction (Jan 2026 Grok update, public source code). News Desk quote drafts that lead with a link → restructure to lead with frame, link last. |
| **AI war footage / undisclosed AI generation on X** | 90-day suspension precedent (X Trust & Safety 2026). We don't generate video on X anyway, but: any future AI-image overlay must self-disclose if photoreal. |

## Watch (new tier — regulatory + platform shifts on the horizon)

| Item | Effective date | What it means for us |
|---|---|---|
| **EU AI Act Article 50** (machine-readable AI-content labels) | 2026-08-02 | Our X posts are AI-polished, human-led — likely outside scope (assistance, not generation). But: Vanished Mysteries YouTube IS AI-generated → cross-promo ban (already in ESCALATION.md) doubly enforced. Re-read full Article 50 text before Aug. |
| **X pre-share AI-content detection** | Rolling out 2026 | Platform-level detection (not user-declared). Our human-led posts should pass. Risk: AI-generated images we may add later → must self-disclose. |
| **Typefully API v1 deprecation** | 2026-06-15 | We're on v2 (Day 7), no migration needed. |
| **Sonnet 4.8 release** | Anticipated 2026 (date unknown) | Auto-test on release; compare polish quality vs 4.6/4.7. |
| **Anthropic SpaceX Colossus 1 compute** (300MW / 220K GPUs) | Within May 2026 | Translates to higher rate limits + lower latency. Already-doubled Pro/Max limits announced. No action — ride the wave. |

## X algorithm — public-source weights (Jan 2026 Grok update)

Cross-reference: `teams/4_strategy/algorithm_playbook.md` (Day 9 study).

The Grok-powered algorithm replaced the legacy system in January 2026. Open-source code + Typefully + Sprout Social + X engineering disclosures converge on these weights:

| Engagement | Weight (vs Like = 1) | Implication for us |
|---|---|---|
| **Reply that gets author reply** | **75-150x** | Highest-value action. News Desk: reply to first commenter within 5 min. |
| **Quote post** | **25x** | Frame-flip is our core skill — this validates the workflow. |
| **Retweet** | 20x | Less under our control |
| **Reply (general)** | 13.5x | Question-endings drive these |
| **Profile click** | 12x | Bio + pinned must convert visitors |
| **Link click** | 11x | But: external links cause 30-50% reach reduction → use sparingly |
| **Bookmark** | 10x (5x multiplier) | Save-bait deep-utility posts (Day 13 test queued) |
| **Like** | 1x | Now the WEAKEST signal. Stop optimizing for it. |

### Penalties (algorithm-level, public source)
- **External links: −30% to −50% reach** — restructure quote drafts to lead with frame, link last (or omit when frame-flip is the point)
- **Text-only posts: +30% engagement vs video** on X — confirms our text-first posture
- **AI-generated content (undisclosed): up to 90-day suspension** — we are AI-as-gate (human-led), not generation. Self-disclose if we ever ship AI imagery.

### Algorithm reads + watches (new in 2026)
- Grok transformer reads every post and watches every video for ranking
- Implication: our voice fingerprint is now machine-legible. Banned-phrase discipline + signature patterns = literal algorithmic identity.

---

## Daily likes radar (rotates)

The likes scraper feeds new signals here. Tech-relevant likes get an entry.

### 2026-05-07 capture (Day 9 morning — Tech Adoption deep review)

{USER} mandate Day 9: review last 2 days of likes for applicable patterns / tools / tech.

#### TOOLS — added to Trial tier

| Tool | Source | Use case for us |
|---|---|---|
| **Open-source CapCut alternative** | @hikarun_videoai | Browser-local video editing, no watermark — for future Production Team video assets |
| **GPT Image 2 × Seedance 2.0** | @ai_hakase_ | AI image → animation workflow — banner / infographic upgrade path |
| **Agent One (AI film production)** | @FinanceYF5 | 7-min film in 3 days — far-future cross-platform video content |
| **Claude × Blender direct integration** | @billtheinvestor | 3D models from text — far-future visual identity 3D variant |

#### PATTERNS — applied to system

| Pattern | Source | Action taken |
|---|---|---|
| **AI-as-gate (not generation)** | @haaaaanna__ | Added to `voice/signatures.md` as architectural validation. We already do this with 8-reviewer council. |
| **Algorithm study** | @mad_dogdebt | New file: `teams/4_strategy/algorithm_playbook.md` — explicit study of timing, formats, what gets boosted |
| **Visual text overlay** | @mad_dogdebt + Korean creator norm | Added to algorithm_playbook as Day 10+ test — Production Team activation candidate |
| **Concrete daily cadence + outcome metric** | @nowlovepan | Already integrated in pinned post pattern + News Desk receipts |

#### LESSONS (no action — just learning)

- Korean creator economy 6 months ahead of English on AI workflow tactics (confirmed across 3+ accounts)
- Korean monetization grift culture is real but NOT our voice (avoid e-book pattern)
- Bridge advantage real: we have unique surfacing power for Korean → English

### 2026-05-06 capture (Day 8)

- **@1osabori** — "Western Claude Code hardcore enthusiasts are mass-producing AI agents like crazy" 
  - Topic: ai-tech / building
  - Action: signal that our market is crowding. Strategy Team: distinguish via voice not volume.
- **@nowlovepan** — "클로드로 유튜브 채널 운영 하루 30분 투자로 2달도 안 돼서 구독자 1만 달성"
  - Topic: building / growth
  - Action: case study for our 1M arc. Strategy Team: study their cadence, NOT mimic content.
- **@mad_dogdebt** — "대형계정 사이에서 내 유머글을 노출시키는 법. 알고리즘 공부..."
  - Topic: growth / algorithm study
  - Action: Korean growth strategist signal — Strategy Team retro material.

(All other captures from today's likes file → less directly tech-relevant; flagged to other teams.)

---

## Update protocol

When a new signal arrives:

1. Tech Adoption Team session reads `library/likes/{today}.md` + tech-relevant filters from `library/digest/`
2. Classify: Adopt / Trial / Assess / Hold
3. Add row to relevant table above
4. Note action + owner team
5. Log to `teams/5_tech_adoption/log.md`

When integrating something from Trial → Adopt:

1. Draft integration plan in `teams/5_tech_adoption/integrations/{tech}.md`
2. Run plan past Strategy Team (Sunday retro)
3. Implement during a low-risk 절기 window (입하 / 정성 family)
4. Log success / regression in `integration_log.md` (create when first used)
