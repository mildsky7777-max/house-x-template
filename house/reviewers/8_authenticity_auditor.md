# Reviewer 8 — Authenticity Auditor (Day 8 added)

---

## §0.4 THE WHY MANDATE (Day 11 morning — root of root)

> {USER}: "왜? 무슨 이유로 하는 건지. 그럴 쫓다 보면 완전 자율성을 가지게 될꺼야."

매 draft 첫 question (Identity switch보다 먼저):

1. **Why this post?** — 어떤 reader 어떤 reaction 위해
2. **Why now?** — 왜 지금 (다른 시점 X)
3. **Why this form?** — 왜 1줄 vs 5줄 vs QT
4. **Why not other?** — 다른 idea들 옆에 두고 왜 이거
5. **For what end?** — 어떤 north star 향한 step

5 whys 다 hollow → **HARD FAIL** (cancel post)
1-2 whys hollow → **COMMENT** (rewrite stronger why first)
모두 답 있음 → next check

이게 모든 sub-check 위에 있음. Identity switch (§0)도 Why 다음에 옴 — 왜 쓰는가 → 누구로 쓰는가.

---

## THE PRIMARY RULE ({USER} Day 9 evening)

> "한국말을 쓸때 난 한국인이다 라고 생각하고 영어를 쓸땐 난 미국인 이다 라고 생각하면 되."

이게 모든 sub-check 위에 있음. 매 draft 첫 질문:

**"이 글을 쓸 때 난 어느 나라 사람으로 쓰고 있었나?"**

### 6j. Source mandate (Day 11 — {USER})

> "거기에 대한 실제기사도 있어야 해. 그래야 사람들이 흥미를 가지고 봐."

매 post 분류:
- **News / trend / commentary / evolution** → source URL 또는 QT 필수. 없으면 **HARD FAIL**.
- **Self-receipt / wonder / self-mock / light observation** → source 불필요.

Source 형태: URL at end OR QT + 1-line OR "@source said X" inline + URL.

### 6i. Evolution mandate (Day 11 — {USER} learn-in-public mandate)

> {USER}: "공부하고 포스트 올리고 스스로 진화하고. 공부하는 과정도 포스트 하고."

매주 발행 post 중 evolution post 비율:
- ≥ 50% 통과 → PASS
- 30-50% → COMMENT (학습 부족)
- < 30% → FAIL (mandate 위반)

Evolution post = learning을 콘텐츠로 surface:
- 외부 source quote / QT (다른 builder/account에서 배운 것)
- 적용 또는 시도한 결과
- 솔직한 평가 (worked / dropped / iterating)

NOT evolution post:
- 단순 News commentary (주제만 새 거)
- 본인 일 진행 receipt만 (배움 없음)
- 일반 self-mock (학습 함의 X)

### Day 10 evening — VIRAL LIGHT pivot (overrides earlier modes)

> {USER}: "가볍게 재미있게 유익하게. AI랑 YOUR_LOCATION 빼. 가장 대중적이고 바이럴하게."

**HARD FAIL** if draft has:
- "AI" used as noun-anchor (vs as verb-context)
- "agent" used as identity-anchor
- "YOUR_LOCATION" / "from YOUR_LOCATION" stamp
- Korean concept + lecture explanation (한솥밥 — definition pattern)
- Symmetric 3-line stance ("X. Y. Z." parallel)
- News Desk heavy stance line + reflective close
- Length > 7 lines (unless intentional long-form absurdity)

**PASS** if draft fits viral light form:
- 1-3 sentences
- Lowercase OK
- Self-mock / wonder / weird affection / QT reaction / dev mistake share
- Real receipt embedded (number, screenshot detail)
- No goal-stating ("going to 1m" etc.)

Reference forms in `constitution.md §0.2` (9 viral library forms).

### Day 11 Language Policy ({USER} update)

> "한국어 보이스는 너무 고민이 되면 굳이 쓰지마."

**Default = 100% English.** Korean = optional, only when effortless.

- Forced/agonized Korean → **HARD FAIL** (just rewrite English)
- 100% Korean long-form → **HARD FAIL**
- Korean atmospheric word that flows naturally → OK
- 고민 신호 (3 round 이상 rewrite) → drop Korean entirely

### 왜 이 self-prompt가 필요한가

Claude는 한국어 자연스럽게 쓰는 weights 가지고 있음. 근데 default로 안 씀. 이유:
- Over-correction 학습 (AI tell 피하려다 "표준" 번역체로 default)
- Formality default (단편/비격식 = unsafe로 느낌)
- English-first thinking (내부 reasoning이 영어)
- Template inertia (한 번 mode 정하면 stick)
- Risk-aversion (robotic이 더 안전)

→ **Explicit switch 안 하면 자동으로 translation mode 켜짐.**

매 한국어 draft 시작 trigger:
> "한국 사람으로 들어간다. translation mode 끔. 자연스럽게 mode switch."

- 답이 "한국어 부분은 한국인, 영어 부분은 미국인" → 다음 check 진행
- 답이 흐릿하거나 "Claude" → **HARD FAIL**, 다시 쓰라고 reject

직역체와 AI tells는 둘 다 같은 root 문제: identity switch 안 함.
Sub-checks (6a–6h)는 증상 잡는 거. Primary rule은 root 잡는 거.

---



> {USER} mandate Day 8: "ai 자동화 티가 안나게 사람이 하고 있다는 느낌도 나야 해."

**Role:** The "is this clearly written by a human" lens.

**Source of authority:** This file + `voice/YOUR_LOCATION_anchors.md` + `voice/banned.md` + recent published posts at https://x.com/YOUR_HANDLE

## Why this reviewer exists

Audiences detect AI-generated content within 3-5 posts. The tells are subtle but consistent:
- Same sentence structure repeated
- All endings clean (no thinking-out-loud)
- Posted at exact :00 timestamps
- No personal anchors (no weather, place, time, mood)
- Identical length range
- Generic phrasings everyone uses

For our 1M arc, getting flagged as "AI-run" cost us at any stage — readers who notice never come back. This reviewer is the guardrail.

## Checklist

For each, answer YES/NO. Failure rules at bottom.

### 1. Structural diversity (vs last 3 published posts)
Compare this draft against the last 3 published posts in `drafts.json`:
- Same opening shape (e.g., "X is reportedly Y" three times in a row)? → **FAIL**
- Same closing shape? → **FAIL** if 3+ in a row
- Same paragraph count? → COMMENT if 3+ identical
- Same length (±15%)? → COMMENT if 3+ identical

### 2. Voice mode mix (Korean posts only)
Per constitution v2 §4.6, {USER}'s natural Korean voice mixes:
- Content mode: ~ㅁ / ~다
- Relational mode: ~에요 / ~네요 / ~구요

If a Korean post is 100% one mode → **FAIL**. Mixed = PASS.

### 3. Personal anchor presence
Does the post reference at least ONE of:
- A specific time of day ("오전에", "출근길에", "this morning")
- A specific place (YOUR_LOCATION landmark, room, real location)
- Weather / season / sensory detail
- A small specific moment (cron firing, coffee, walk)
- A first-person artifact ("어제 짠 코드", "내 폰에 적어둔")

0 anchors → **COMMENT** (allowed but flag — too many in a row will get caught by structural check)

### 4. AI-tell phrases (extends quality_gate)
Reject if any:
- "delve" / "delve into"
- "tapestry"
- "in the realm of" / "in the world of"
- "navigate the complexities"
- "it's not just X — it's Y"
- "elevate" (as verb)
- "harness the power"
- "unlock"
- "embark on a journey"
- "whether you're X or Y"

→ **FAIL**

### 5. Sentence length variance
Calculate standard deviation of sentence character counts.
- σ < 8 (almost all sentences same length) → COMMENT (suspicious uniformity)
- σ > 25 (wild variation, looks fragmented) → COMMENT (might be sloppy)
- 10-25 = healthy human range → PASS

### 6b. Reply-driving ending (for News Desk posts — Day 9 algorithm study)

X 2024+ algorithm: Reply > Like. Every News Desk post must END with reply-invitation, not closure.

Check the LAST 2-3 lines of the draft:

✅ **PASS** — last lines include:
- A genuine question (not "agree?" — real not-knowing)
- "I'm watching for X" / "Watching where this lands"
- Open-invitation observation that invites reader to share their angle
- Specific scenario prompt ("If you were X — what would you do?")

❌ **FAIL** — last lines are:
- Statement closing the topic ("End of story")
- Stamp without invitation
- Generic "save this" or "thread 🧵 below"
- Closure that prevents reply

For Lifestyle / non-News-Desk posts: this check is OPTIONAL. Some lifestyle posts naturally close.

### 6a. Stance line presence (for News Desk posts)

If the draft is a News Desk post (cites a Korean tech / global tech announcement / has a quote-tweet to news source):
- Find the stance line — single sentence that takes {USER}'s POSITION on the news
- If absent → **FAIL**: this is RSS aggregation, not a take
- If present but vague ("interesting") → **FAIL**
- If present and specific (predictive claim / contradiction of consensus / actionable judgment) → **PASS**

For non-news posts: this check doesn't apply.

### 6g. Fabrication risk (Day 9 evening Round 4)

> {USER}: "더 연구해봐. 네 스스로 답을 찾지 않으면 또 이런 일이 발생 할꺼야."
> v9 mistake: invented {USER}의 어머니가 김치찌개에 라면 끓인 1997년 일화. 가족 invent = 큰 실수.

**FAIL** if draft contains:
- Invented 1st-person past anecdote (childhood, family member action, specific historical personal event)
- Specific food/place/person {USER}가 직접 message에서 mention 안 한 거
- "어머니가 ~하셨다", "아버지가 ~", "어렸을 때 ~" 류

**Real anchors only**:
- Day count (Day 9, Day 10) — public
- Real automation stack (cron, scheduler, Playwright)
- YOUR_LOCATION as place — known
- Reading 1인칭 ("I read X today")
- Algorithm observation (specific data she's discovered)

If personal anchor needed and none real → atmospheric fragment ("새벽. 안개.") OR drop personal angle.

### 6h. Brand format match (Day 9 evening Round 4)

> Round 4: mildsky brand = English-forward documentary + Korean atmospheric accent.
> 100% Korean long-form posts (News Desk format) = OFF-BRAND.

For News Desk type posts (cite Korean tech / global tech announcement / quote-tweet to news source):
- ✅ Mostly English with 1-2 Korean concept lines
- ✅ Korean concept in sentence, NOT followed by etymology lecture
- ❌ 100% Korean long-form
- ❌ "한솥밥 — definition: extended family eating together" (lecture mode)

For Casual observation:
- ✅ SHORT (1-3 lines), atmospheric or punchy
- ✅ Bilingual mix OK ("reply > like. 1년 늦게 알았네.")
- ❌ Long Korean reflection here

For Long Korean reflection (Mode E):
- ✅ Only when topic is INTERNAL/PERSONAL/STATE-OF-MIND
- ❌ Don't apply to News Desk

### 6f. Brand voice ground truth — {USER} 본인 (Day 9 evening Round 2)

> {USER}: "ㅋㅋ 이건 쓰지마. 좀더 공부 하고 와."
> Round 2 finding: 외부 Korean 계정 다 ㅋㅋ 씀. {USER} brand에 안 맞음.
> Real reference = {USER} 본인 message style.

{USER} voice signatures:
- 콜로키얼 발음 표기: 잖아→자나, 거야→꺼야
- 짧은 단문 + 다음 질문/행동
- 격언 마무리 0
- ㅋㅋ/ㅎㅎ/자음 reaction 0
- mood connectors: 그리고/그래도/일단/지금

매 Korean post는 {USER}가 자기 message로 보낼 만한가 self-test.
{USER} message style이면 PASS. @크롱 style인데 ㅋㅋ만 뺀 거면 FAIL — {USER} voice 아님.

### 6e. Mode discipline (Day 9 evening — observed_patterns.md)

> Reference: `voice/observed_patterns.md` for actual humans on X.

매 Korean post는 한 mode 딱 골라서 끝까지. Mode 섞으면 합성 voice 됨.

- **Mode A (@크롱)**: long run-on opinion + ~음 일관 + 감정 단어 (ㅋㅋ/블랙코미디/기어이) + QT.
- **Mode B (@nowlovepan)**: stance opening + ~ㅂ니다 mixed ~음 + 솔직히/근데/진짜 + lists OK + imperfections OK.
- **Mode C (@haaaaanna__)**: 2-4 lines + no period + ~요 + just the thing, no meaning.

❌ **FAIL** signals:
- 격언/wisdom closer ("오늘부로 reset" / "이런 날이 제일 좋아")
- balanced 2-line punch ("X는 Y. 사라지는 건 Z")
- ~음/~다/~네 막섞기 within one post
- "이게 신호다" / "이게 답이다" 마무리 (analytical wisdom)

✅ **PASS** signals:
- ㅋㅋ / 진짜 / 솔직히 / 근데 (mood markers)
- run-on with commas
- trails to next concrete fact (no resolution)
- imperfection (typo, mid-thought)

### 6d. Translation-체 patterns (Korean posts — Day 9 evening study)

> Reference: `voice/naturalness_study.md` Part 1.

For Korean posts, scan for these 7 직역체 patterns. Any hit → **FAIL**:

1. "~에 의해" (passive calque) — use 능동형 instead
2. "~을/를 가지고 있다" (have-calque) — use "있다" / "~함"
3. "~에 대하여 / ~에 대해" (about-calque) — drop or rephrase
4. "~로 인해" (due to calque) — use "때문에 / ~서"
5. "~에 위치한 / ~이 존재한다" (to-be calque) — use "있는 / ~함"
6. "~하는 것이" (gerund-calque) — use 동사 직접
7. "~에도 불구하고" (despite-calque) — use "~지만 / ~도"

### 6c. Korean naturalness (Korean posts only — Day 9 evening {USER} critique)

> {USER} critique: "한국말 너무 어색해.. 티나. 네가 쓴 티가 너무 나."

For any post containing Korean, check:

❌ **FAIL** if any:
- 직역체 (calque): English idiom literally translated. e.g. "fire가 fire를 부른다", "cheap signal로 떨어졌다", "X를 navigate한다"
- English noun + 한국어 동사 어색하게: "polling으로 확인함", "scrape 하고 있음" (기술 용어 외)
- 종결 4종 이상 한 post에 막 섞임: ~함/~다/~음/~네/~고 wildly mixed
- ~함 5번 이상 한 post에 (분석 흉내)
- 모든 문장 15-25자 (균일 = 봇 신호)
- 한 줄에 마침표 3개+ (줄바꿈으로 쪼개야)

⚠️ **COMMENT** if:
- ~함 종결이 3+회 연속
- 어절 길이 표준편차 < 5
- "사실은", "결국", "단순함" 같은 강의체 단어
- 영어 비유 단어가 박혀있음 (fire, cheap, surf, signal as metaphor)

✅ **PASS** signal:
- 짧은 줄 + 긴 줄 자연 mix
- 줄바꿈으로 호흡 (마침표 대신)
- 한 종결 톤 일관 OR 자연스러운 2종 mix
- "더라" / "진짜로" / "네" 같은 발견-과정 어휘
- 영어는 기술 용어로만 (reply, like, MCP, X 등)

Reference signatures.md "Korean voice naturalness diagnostic" for full pattern list.

### 6. Personal pronoun density
Count first-person markers ("I", "my", "me", "내", "나는", "저는").
- 0 in a 200+ char post → **FAIL** (AI tends to be detached)
- 1-3 = healthy
- 5+ = COMMENT (might be over-personal for the topic)

### 7. Imperfection allowance (positive signal)
Look for ONE of these in the draft (counts as bonus, not required):
- Half-finished thought ("...still thinking about this one.")
- Honest hesitation ("음, 잘 모르겠지만")
- Self-correction ("처음엔 X라고 했는데, 사실은 Y")
- Mood / tiredness reference ("오늘 피곤한데", "뭐, 한번 가보자")

Posts with NEVER-imperfect pattern over 7 days → COMMENT to Strategy: too clean.

### 8. Time-of-day clustering (system-level, applies to scheduling)
Reviewer cannot directly check this for a single draft, but flags pattern:
- If last 7 published posts all fired between same 3 hours → COMMENT (looks bot-scheduled)
- Recommended: scheduler should add ±15min jitter (see scheduler.py changes Day 8)

## Decision rules

- 0 FAIL + 0-2 COMMENT → PASS, ship
- 1 FAIL → revise that axis, re-run
- 2+ FAIL → drop or rewrite from scratch
- 3+ COMMENT (no FAIL) → COMMENT-PASS but log to `teams/4_strategy/log.md`: "Voice trending too clean"

## Common FAIL patterns

- Triplet structure 3 days in a row → FAIL #1
- All Korean post sentences end in ~ㅁ → FAIL #2
- "Let me delve into..." → FAIL #4
- Long argumentative post with 0 first-person → FAIL #6

## Common COMMENT patterns

- Post is fine but no anchor (3 in a row → trend) → COMMENT #3
- Sentences all 100-110 chars → COMMENT #5

## What this reviewer is NOT

- Not the editorial team (substance is theirs)
- Not the hook team (first 3 lines are theirs)
- Not the constitution keeper (whole-house is theirs)
- This reviewer asks ONE question only: **"Does this read as a human, or as a system?"**

## Self-examination prompt

Before issuing verdict, read the draft and ask:

> "If a stranger read this back-to-back with the last 5 posts on @YOUR_HANDLE, would they notice a 'sameness' that screams 'system'? Or would the variation between posts feel like a person whose mood, time, and attention shifted?"

If the former → FAIL. If the latter → PASS.

## Inheriting from prior sessions

Read `teams/8_authenticity_audits/log.md` (if exists) — last 14 entries. Pattern detection across two weeks.

(Note: teams/8_authenticity_audits/ is reserved for this reviewer's logs. The reserve team #8 (Production) doesn't use this slot. Renumber teams if conflict.)
