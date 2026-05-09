# 5_tech_adoption — log

Append-only record of team decisions and actions.

---

## 2026-05-06 (Day 8 morning) — Team formation

Team activated as part of the company structure. Leader brief at `leader_brief.md`.

---

## 2026-05-07 09:30 KST — Day 9 Tech Adoption Deep Review

{USER} mandate: "내 x에 이틀동안 조아요 표시 된 것중에 보면 우리 x에 적용 시킬 만 한 것들이 많아. 이것도 자율적으로 해야 해."

### Reviewed 2 days of likes (Day 8 + Day 9 = 13 likes total)

**Day 8 likes (4):**
- @1osabori — info-speed gap (already used in a598db85)
- @mad_dogdebt — algorithm study (NEW APPLICATION today)
- @nowlovepan — Claude YouTube case (already used in a4fd1bce)
- (1 atmospheric)

**Day 9 likes (7):**
- @Linhtailor2 — atmospheric voice
- @gagarotai200 — extreme hype claim (REJECTED for our voice)
- @haaaaanna__ — AI-as-gate (already used in 760e565b + ARCHITECTURAL VALIDATION today)
- @ai_hakase_ — GPT Image 2 × Seedance (TOOL added to radar)
- @billtheinvestor — Claude × Blender (already used in 07b92e86)
- @FinanceYF5 — Agent One AI film (TOOL added to radar)
- @hikarun_videoai — open-source CapCut (TOOL added to radar)

### Actions taken (autonomous)

1. **Added 4 tools to tech_radar.md Trial tier** (open-source CapCut alt, GPT Image 2 × Seedance, Agent One, Claude×Blender)
2. **Created `teams/4_strategy/algorithm_playbook.md`** — first explicit X algorithm study doc, drawing from @mad_dogdebt patterns
3. **Updated `voice/signatures.md`** — added "AI-as-gate" pattern from @haaaaanna__ as architectural confirmation of our 8-reviewer council
4. **Added Day 10-14 test plan** to algorithm_playbook (visual text overlay, English audience slot timing, reply-to-stranger workflow, save-bait deep-dive)

### What we learned (no immediate action — observation)

- Korean creator economy 6 months ahead of English on AI workflow tactics (confirmed across 3+ accounts)
- Korean monetization grift culture is real but NOT for our voice
- Bridge advantage real: surfacing power for Korean → English is unique to us
- Visual text overlay is a Korean creator norm we don't yet do — Day 10+ test

### What we explicitly did NOT apply

- @gagarotai200 "30M/month possible" extreme hype — constitution §8 forbids unsubstantiated claims
- @mad_dogdebt e-book monetization model — different brand, different audience
- Wealth flex tone — anti-guru posture forbids

### Day 9 Tech Adoption verdict

System is healthy. 4 tools queued for trial. 1 architectural validation. 1 strategic playbook (algorithm study). Day 10+ test plan ready.

Next deep review: Day 14 (weekly Tech Adoption cycle going forward).

---

## 2026-05-07 10:00 KST — Day 9 Algorithm DEEP study

{USER} follow-up: "x에 대해서 공부하는 거. 어느 트렌드로 가야 인기가 있는지. 그래서 알고리즘으로 분류가 되는지."

### Honestly admitted: first playbook was observation-based, not deep study.

Read @mad_dogdebt actual full algorithm post (status 2051930899856720248):
> "소형 계정이 대형 계정 사이에서 노출되려면 이슈를 퍼올 때 '논점을 꼬집어' 견해를 뒤집어야 함."

Core teaching extracted: **small accounts must FLIP THE FRAME, not repeat the fact.**

### Synthesized with public X algorithm knowledge (2024+)

Updated `algorithm_playbook.md` with:

1. **Engagement signal hierarchy** (post-2024 weights)
   - Reply > Quote > Bookmark > Retweet > Like
   - Like is now WEAKEST signal — once primary, now low-weight
   - **Implication**: optimize for REPLY + BOOKMARK + QUOTE

2. **First 30-min engagement window** is critical (algorithm boosts based on velocity)

3. **Save-bait deep utility** = ~10× value of like-bait
   - We need 1-2/week deep utility posts
   - Currently 100% news commentary (5-7 lines) — gap

4. **Frame-flip principle** (from mad_dogdebt) validates News Desk mission
   - We already do this with Format 1-4
   - GAP: we don't surf X's OWN trending topics, only RSS + likes

5. **Voice updates from algorithm study**:
   - Add question-endings to invite replies
   - Add reader-direct-address ("if you were X — what would you...")
   - Reply to first commenter within 5 min of their reply

### New action item: Build x_trends_scanner.py

Day 10+ — capture Korean/global X trending hourly, feed to News Desk for frame-flipping. This closes the mad_dogdebt gap.

### Test plan additions (Day 10-14)

- Question-ending posts test (force replies)
- X trending surf workflow test
- Save-bait deep dive post (now Day 13 with explicit deep-utility framing)

### Verdict

System voice was already well-aligned with mad_dogdebt's frame-flip teaching (we do this in News Desk). But:
- We were optimizing for likes (less valued in 2024)
- We weren't surfing X's own trending
- We had 0 save-bait deep utility posts

Three gaps now explicit. Day 10+ tests will reveal which gap closes most engagement.

---

## 2026-05-09 10:08 KST — Day 11 morning — first PROACTIVE tech-research run (baseline established)

{USER} mandate Day 9 evening: "우리의 기술전문팀은 이런걸 나보다 먼저 발견해서 스스로 발전 시켜 나가야 하자나."

This is the first run of `house-tech-research` scheduled task (every 3 days, 10:08 KST). Job: find what {USER} SHOULD know before they ask. No like-driven prompts — pure proactive scan.

### Patterns DISCOVERED (proactive — public web research, not waiting for {USER})

**1. X Grok algorithm — full weights now public (Jan 2026 update)**
- Reply-with-author-reply weighted **75-150x** like (varies by source; both Sprout Social and Typefully agree directionally)
- Quote = 25x, Retweet = 20x, Reply = 13.5x, Bookmark = 10x, Like = 1x
- **External links: 30-50% reach reduction** — News Desk quote drafts that link out are paying a heavy tax
- **Text-only posts +30% engagement vs video** on X — validates our text-first posture
- Algorithm reads every post AND watches every video (Grok transformer) → voice fingerprint is now literally machine-legible
- ACTION: tech_radar.md now has dedicated "X algorithm public weights" section + cross-ref to `algorithm_playbook.md`

**2. Anthropic Advisor Tool (BETA, May 2026 release)**
- Sonnet/Haiku executor + Opus advisor on demand → near-Opus quality at lower cost
- Direct relevance: 8-reviewer council currently runs at uniform model tier. Advisor pattern = run 8 reviewers with cheap model, escalate edge cases to Opus.
- ACTION: added to Trial tier with explicit "test next 7 days" date (Day 18 target)

**3. Typefully API v2 — April 2026 added performance-data pull**
- Endpoint exposes per-post analytics (impressions, engagement) for X posts published via Typefully
- Direct relevance: morning_briefing.md "Numbers" section currently scraped via Playwright. API endpoint = more reliable, more granular.
- ACTION: added to Trial tier; queued `metrics_puller.py` prototype for Day 13-15 절기 window

**4. EU AI Act Article 50 (effective 2026-08-02)**
- Machine-readable AI-content labels mandated where technically feasible
- Our posture: AI-as-gate (assistance, not generation) likely outside scope for X posts. But Vanished Mysteries YouTube IS AI-generated content → cross-promo ban (Day 7 risk note) doubly enforced after Aug 2.
- ACTION: added to new "Watch" tier in tech_radar; ESCALATION.md drift precedent reinforced

**5. X pre-share AI-content detection rolling out 2026**
- Platform-level detection (not user-declared); 90-day suspension precedent for undisclosed AI war footage
- ACTION: added to Watch tier; if we ever generate AI imagery, must self-disclose

**6. Threads 450M MAU (April 2026, +175M YoY) + Threads Ads with creator revenue share**
- Brand adoption accelerating; lower-competition window per multiple analyst sources
- ACTION: Cross-Platform Team activation candidate moved from Day 30+ to Day 14-20 in tech_radar Assess tier. Activation still requires {USER} approval per AUTONOMY.md §5.

**7. Faceless YouTube monetization 2026 (industry-wide)**
- Shorts threshold: 1K subs + 10M Shorts views in 90d
- Mystery/True Crime niche has long-watch advantage → Vanished Mysteries niche fit confirmed
- 38% of new creator monetization is faceless (vs 12% three years ago)
- ACTION: no immediate change — we already operate faceless. Noted as competitive landscape data.

**8. Claude Code skill marketplace (4,200+ skills, 770+ MCP, 2,500+ marketplaces)**
- Off-the-shelf augmentations available
- ACTION: added to Watch tier; calendar a 절기-low-window quarterly survey

### Patterns CONSIDERED but rejected

- **AI voice synthesis tools** (VoxCPM2, Voicebox, Fish Speech, Realtime TTS-2, ElevenLabs replacements): repeatedly featured in {USER}'s likes 5/6-5/8 but {USER} explicitly rejected Korean voice cloning Day 1. Compounded by EU AI Act Article 50. Permanent Hold.
- **AI YouTube auto-pipeline tools** (Gemini full video edit, HeyGen lip-sync): faceless production pipelines featured by @David_eficaz, @Alina_with_Ai, @genel_ai. Useful for far-future Production Team but not Vanished Mysteries Season 2 path. Filed under "Trial — far future."
- **Short-video arbitrage** (one long → 20 shorts → 5 platforms, @0xluffy_eth): "$2000+/mo, no filming" — engagement-bait monetization narrative, anti-guru violation per Constitution §8.
- **"30M/month from Claude Code" wealth flex** (@gagarotai200, @toro_minato, @girisimcihisler): same anti-guru frame. Already in spirit of Day 9 ESCALATION precedent.

### Drift precedents added to `reviewers/ESCALATION.md`

1. **External-link-heavy posts** — algorithm penalty 30-50%. Permanent rule for News Desk quote drafts.
2. **AI auto-pipeline narratives reinforced** — EU AI Act Article 50 (Aug 2, 2026) compounds the @maruo_0314 precedent. Any "AI generates content for you" frame doubly forbidden.

### Action items for next 3 days (Day 11 → Day 14)

| Action | Owner | Target |
|---|---|---|
| Prototype Anthropic Advisor Tool on a polish run | Tech Adoption + Council | Day 13 |
| Wire Typefully analytics endpoint into night_briefing | Tech Adoption + Production | Day 13-15 |
| Audit news_radar.md / News Desk for external-link-heavy posts; flag refactor candidates | Strategy | Day 12 |
| Read full EU AI Act Article 50 text (not summary) | Tech Adoption | Before Day 14 |
| Re-check x_trends_scanner.py — many "·" placeholder entries (selector bug?) | Production | Day 12 |

### What {USER} should know (surfaced to night_briefing via tech_adoption_findings.md)

Top 3:
1. Reply-with-author-reply weighted up to 150x like — News Desk reply discipline (5-min window) is our highest-leverage habit
2. Anthropic Advisor Tool BETA = lower-cost path to current polish quality; testing this week
3. Threads Ads launched with creator revenue share + 450M MAU — Cross-Platform Team activation moved up

### Next run

2026-05-12 10:08 KST. Will switch from baseline establishment to incremental update.

---
