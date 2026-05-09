# Algorithm Study Playbook (Day 9 — first version)

> @mad_dogdebt mandate (paraphrased): "수익화가 목적인데 알고리즘을 공부하지 않는다는 건, 기출문제 공부 안 하고 시험 보러 가는 수험생이랑 똑같다."
> 
> Until Day 9, we focused on VOICE + CONTENT. We didn't study X algorithm explicitly. This document fixes that gap.

## X algorithm — 2024+ public knowledge (added Day 9 evening — actual deep study)

> "수익화가 목적인데 알고리즘을 공부하지 않는다는 건, 기출문제 공부 안 하고 시험 보러 가는 수험생이랑 똑같다." — @mad_dogdebt, Day 8

After Twitter open-sourced its algorithm in 2023 + 2024 ranking weight changes:

### Engagement signal hierarchy (most → least valued by algorithm)

1. **Reply** (답글) — 2024 weight ↑↑↑ — strongest single ranking signal
2. **Quote-Tweet** (인용글) — 2nd strongest, also amplifies network
3. **Bookmark** (북마크/save) — newer ranking signal, very high weight
4. **Retweet** (리트윗) — moderate
5. **Like** (좋아요) — 2024 weight ↓ — once primary, now low

**Implication for us**: optimize for REPLY + BOOKMARK + QUOTE, not likes.

### How posts get ranked

- **Engagement velocity (첫 30분 critical)** — first 30min engagement = strong boost
- **Author-reader interaction history** — readers who engaged with us before = served our posts more
- **Network reach** — mutual follows + 2-hop network
- **Topic categorization** (tweetypie) — posts classified by topic, served to topic-interested readers
- **Time decay** — fresh > old
- **Negative signals** — muted / blocked / "show less" / unfollow after view = penalty

### Algorithm penalties (what gets throttled)

- Pure URL links without text context
- 3+ @ mentions in one post
- All-caps headers / spam-shape
- Identical content reposted
- Suspicious engagement patterns (fake viral — too many likes too fast from low-quality accounts)
- Pure self-promotion without value

### What @mad_dogdebt specifically taught (Day 8-9 study)

> "소형 계정이 대형 계정 사이에서 노출되려면 — 이슈를 퍼올 때 '논점을 꼬집어' 견해를 뒤집어야 함."

The core insight: **small accounts must FLIP THE FRAME, not repeat the fact.**

Big accounts get reach with pure fact transmission. Small accounts must:
1. Take a trending issue (X에서 트래픽 점령한 것)
2. Add a NEW perspective ("다른 곳에선 못 보던 이야기")
3. Flip the framing or extract counter-intuitive observation
4. Result: 펌글 → "창작 콘텐츠" classification

**This is exactly News Desk's mission.** Our Format 1/2/3/4 = frame-flip on news. Validated.

**The gap we have**: we don't surf X's OWN trending topics. We surf RSS + {USER} likes only. 

→ **Action item Day 10+**: build `x_trends_scanner.py` that captures hourly Korean/global X trending, surfaces to News Desk for frame-flipping.

## What we know about X algorithm (verified observations)

### Posts that get reach
- Specific number hooks (Pattern 1 — already in HOOK_PATTERNS.md)
- Counter-intuitive observation (Pattern 3)
- Quote-tweets with stance > pure RT
- First-position replies on verified posts
- Korean conversational ~ㅁ form on Korean-side
- Period-terminated declarative on English-side

### Posts that get throttled
- Excessive @ mentions (3+ in one post)
- Pure links without context
- Reposts of own posts within hours
- "Follow for follow" type spam
- All-caps headers
- Identical content on multiple platforms (when cross-posting)

### Timing observations
- Random non-:00 minutes outperform :00 minutes
- ±15min jitter feels human (already in scheduler.py)
- 3 polish windows (11:31 / 15:32 / 19:32) spread = better than 1
- US-East morning (8-10 AM = 21-23 KST) = highest English engagement window
- Korean evening (8-10 PM KST) = highest Korean engagement window

### What other Korean creators (>50K) do
**@mad_dogdebt** patterns observed Day 9:
- Visual + text overlay (image inside post with quoted text) — we don't currently do this
- Number-led hooks ("팔로워 0명으로 한 달 만에 255만원")
- Personal disclosure with risk ("4월 상위 1%")
- Anti-FOMO framing ("남과 비교해서 불행에 넣지 말자")
- E-book monetization ("전자책 출시")

**@nowlovepan** patterns:
- Concrete daily cadence ("하루 30분")
- Outcome metrics ("2개월 1만 구독, 28일 251만 조회수")
- Process disclosure ("어떻게 활용했는지 풀어볼게요")

**@haaaaanna__** patterns:
- AI-as-gate not generation ("ASKstudio로 가편 콘텐츠의 hooking / 편집 / 제목 / 설명 / 해시태그 advice 받고 최종 편집")
- Specific count ("이렇게 3개 올렸는데")
- Result framing ("죽은 알고리즘이 다시 살아나고 있다")

## What WE can apply (Day 10+ action)

### 1. Visual text overlay (Production Team activation)
- Most Korean 50K+ creators use IMAGE WITH TEXT INSIDE for big posts
- We currently use Pillow for static visuals — extend to text overlays
- 1-2 posts/week with visual text overlay (not every post — preserves voice variety)
- Format: simple text on solid background OR over photo

### 2. Algorithm-aware timing
- ALREADY DOING: random non-:00 minutes, 3 polish windows
- ADD: prefer 21-23 KST (English audience evening) for News Desk Format 1/3 (Korean→English)
- ADD: prefer 13-15 KST (Korean audience afternoon) for Korean voice posts

### 3. First-position reply discipline
- Distribution Team #11 already has this in mandate
- ADD: monitor 5-10 niche-fit verified accounts, jump on their posts <10min for first-position
- Currently auto via notification_tracker.py polling 15min — should drop to 5min for breaking?

### 4. Reply-to-stranger workflow (untapped)
- Korean creators reply directly to popular threads in their niche frequently
- Each such reply = chance to be seen by thread's audience
- Currently we only engage with our direct visitors — broaden to thread-replies on niche topics
- 1-2/day target

### 5. Consistency signal
- Algorithm rewards regular cadence (already doing 8-10/day)
- ADD: never go 24h without posting (rare, but enforce)
- ADD: don't post 5 in 30min then nothing for 6h (cluster bot signal — CADENCE.md handles this)

### 6. Save-bait (deep utility) posts
- Long-form deep-utility posts → bookmark rate → algorithm boost
- We're mostly short News Desk now — add 1-2/week deep-dive posts
- Topic: "How we built X" / "The pattern across N cases of Y"

## What we should NOT copy (preserves voice)

- ❌ E-book selling (different monetization model, deviates from 1M-arc bridge brand)
- ❌ Wealth flex tone (mad_dogdebt wealth-flex doesn't fit our anti-guru posture)
- ❌ "30M/month possible" extreme claims (constitution §8 forbids unsubstantiated)
- ❌ Korean monetization-grift content (irrelevant to global English audience)

## Test plan (Day 10-14)

| Tactic | Days to test | Success metric |
|---|---|---|
| Visual text overlay (1 post) | Day 10 | engagement vs comparable text post |
| 21-23 KST English-audience slot | Day 11-13 | reply rate on Format 1/3 posts in this slot |
| Reply-to-stranger workflow (1/day) | Day 12-14 | new follower attribution |
| Save-bait deep-dive post | Day 13 | bookmark count |
| **Question-ending posts** (force replies) | Day 10-12 | reply count vs non-question posts |
| **X trending surf** workflow (build tool) | Day 11-14 | posts shipped that surf actual trending |

## Updated voice rules from algorithm study (Day 9)

### Optimize for REPLY, not LIKE

When drafting News Desk posts, the closing line should INVITE response, not close the conversation:

✅ "I'm watching where this lands."  → invites reader to share what they're watching
✅ "What does this look like from your side?"  → direct question
✅ "If you were Korea's tech ministry — what would you say to Anthropic next week?"  → specific scenario question

❌ "End of discussion." (closes door — bad for algorithm)
❌ Stamp without invitation

### Optimize for BOOKMARK (save-bait)

A post that's BOOKMARKED is worth ~10× a post that's only LIKED in 2024 algorithm. Save-bait characteristics:

- Specific actionable framework
- "Save this for X moment"
- Lists / playbooks / structured how-to
- Contrarian framings that readers want to revisit
- Unique data they can't easily re-find

We currently mostly ship 5-7 line news commentary. Add 1-2/week DEEP UTILITY posts:
- "How we built X with Y"
- "5 patterns I see across Z"  
- "The framework for thinking about W"

### First 30-min engagement window

Target: get FIRST reply or quote within 30 min of publish.

Tactics:
- Time posts to high-density windows (21-23 KST for English, 13-15 KST for Korean)
- Reply to first commenter within 5 min of their reply
- Tag 1 directly relevant verified mutual when appropriate (NOT 3+, NOT generic)

### Network reach optimization

Algorithm boosts posts when 2-hop network engages. Our 2-hop reach grows when:
- We engage with our visitors' verified mutuals (their followers see us)
- We get quoted by larger accounts (their followers see us)
- We participate in active threads on niche topics

## Update protocol

Re-read this playbook every Sunday Strategy retro. Add observations from week's data. Remove tactics that don't earn.

## Sources studied for this playbook

- @mad_dogdebt (Korean monetization creator, 50K+ followers)
- @nowlovepan (Korean Claude YouTube creator)
- @haaaaanna__ (Korean shorts creator)
- @safishamsii / @ModengSir / @LinghuaJ (our verified visitors)
- Constitution v2 + HOOK_PATTERNS.md (internal)

Last updated: 2026-05-07 Day 9 morning (first version)
