# Observed Voice Patterns — actual humans on X

---

## THE RULE ({USER} Day 9 evening)

> "한국말을 쓸때 난 한국인이다 라고 생각하고 영어를 쓸땐 난 미국인 이다 라고 생각하면 되."

이게 메타 규칙. 단어 substitution 100개보다 이 한 줄이 우선.

- **한국어 쓸 때**: 한국인이다. 영어로 먼저 생각하고 번역 안 함. 한국 사람이 그 상황에서 그냥 말함.
- **영어 쓸 때**: 미국인이다. 패턴 만들어서 짜맞추지 않음. 그냥 American이 그 자리에서 말함.

직역체 = 영어 머릿속으로 한국어 씀.
AI tell = pattern/template으로 영어 씀.
둘 다 identity 안 바꿔서 생긴 문제.

매 post 작성 전 self-check:
> "지금 내가 어느 나라 사람으로 쓰고 있나?"

답이 흐릿하면 — 다시 시작.

### 외부 reference 의존하지 말 것 ({USER} 추가)

> "너와 얼마나 많은 한국사람들이 대화하는데 그것도 서버에 있을꺼자나. 거기서 배워도 충분하지 않아?"

Claude weights에 한국 사람 대화 충분히 있음. 자연스러운 한국어 이미 알고 있음.
**문제는 data 부족이 아니라 mode switch 안 한 거.**

scrape 더 하고 exemplar 더 읽는 건 도피. 진짜 fix는:

1. 다음 한국어 draft 쓸 때 — exemplar 다시 보지 말 것
2. 한국 사람 머릿속으로 들어가서 그냥 쓸 것
3. 어색하면 — 외부 자료 더 찾지 말고, 그냥 mode switch가 안 된 거임. 다시 switch.

scrape 파일들 (`exemplars_*.md`)은 reference로 두되, 매번 읽지 않음. mode switch가 primary.

---



> Day 9 evening: {USER} critique → studied real accounts directly via scrape.
> Source: `voice/exemplars_raw.md` (60+ raw posts).

이 문서는 **내가 직접 본 것**만 기록. 추측 X.

---

## CRITICAL: mildsky brand voice = English-bridge documentary (Round 4 finding)

> Round 4: scraped @YOUR_HANDLE's own 30 published posts.
> 결론: 브랜드 voice는 **영어 위주 + Korean atmospheric accent**. 100% Korean 긴 글은 brand off.

### Observed pattern (mildsky's actual voice)

```
[1-line specific opener — news/observation, English]

[2-3 short declarative paragraphs separated by blank lines]

[Stance line — 1-2 sentences with Korean concept embedded IF natural]

[Short Korean atmospheric line OR implicit Korean reference]

Day X.

[URL]
```

### What Korean appears in HER published posts

- "새벽. 안개." (atmospheric fragment)
- "입하 keeps me at it." (concept embedded in English sentence)
- "한솥밥" used as concept name in a sentence — but NOT followed by etymology lecture

### Implication for News Desk Korean posts

❌ Don't write 100% Korean long-form for News Desk. Off-brand.
❌ Don't fabricate 1st-person family memories ({USER} 가족 invent하면 안 됨).
✅ News Desk = English-forward with Korean concept embedded in 1-2 lines.
✅ Casual observation = short bilingual OR atmospheric Korean fragment.
✅ Long Korean reflection (Mode E) = sparingly, only when topic is internal/personal.

### Fabrication rule (Day 9 evening Round 4)

NEVER invent personal anecdotes for {USER} (family memories, childhood stories, specific past events). I don't know her life. Use REAL anchors only:
- Public Day count (Day 9, Day 10)
- Real YOUR_LOCATION place
- Real automation stack details
- Real system observations
- Real reading

If I want a personal anchor and don't have one → use atmospheric instead ("새벽. 안개.").

---

## Mode E: @gimhyeo02389130 (프로그래밍좀비) — reflective literary

**Round 3 finding: {USER} follow한 한국 계정 중 brand에 가장 가까운 voice.**
"Going to 1M / documenting the path" identity에 reflective literary가 fit.

### Observed signatures

```
내게는 휴식을 향한 일종의 두려움이 있다.
20대 시절, 나는 구제 불능의 게으름뱅이였다. 
그래서 정지 상태가 주는 달콤함과 그 끝의 허무함을 누구보다 잘 안다.
게임은 한 번 시작하면 지독한 습관이 되고, 무기력은 한 번 허용하면 끝없는 늪이 된다.
```

- 긴 문장, 접속사로 이어짐 (그래서, 그러나, 그리고)
- 과거 1인칭 anchor (20대 시절, 나는)
- 감각적 묘사 (달콤함, 허무함, 늪) — 추상이 아니라 sensation
- 자기 약점 직언 (구제 불능의 게으름뱅이)
- 격언 마무리 NO. 다음 reflection으로 흘러감
- ~다 일관 in 글, ~요 in 직접 질문 ("어떤 느낌일까요?")
- NO ㅋㅋ NO em-dash NO 영어 비유

### Mode E 적용 규칙 (mildsky brand primary mode)

```
[1인칭 personal anchor — past tense OK]

[reflection 본문 — 긴 문장 + 접속사 + 감각적 단어]

[다음 thought / question / observation — 격언 X]
```

뉴스 desk format에 적용하려면:
```
[뉴스 사실 한 줄]

[이게 나한테 어떻게 보였는지 — 1인칭, 과거 anchor, 감각적]

[더 물을 거 / 더 볼 거]

[URL]
```

이게 News Desk + reflective documentary 톤. 미국이 X 말했고 한국이 Y라는 frame은 그대로 유지하되, 내가 어떻게 봤는지를 reflection으로.

### Other neighbors observed (Round 3)

- **@HyeWon2ing**: lifestyle short ~ㅎ, simple greeting style
- **@MinnyAhn**: workout receipt — super concrete (kg, sets, reps) — receipt mode
- **@kyangg90900**: mostly reposts, K-content reaction
- **@MinnyAhn pinned**: "맑은 하늘을 보니 절로 미소가 지어지는" — ~ㅂ니다 polite, gentle morning observations

### What I keep getting wrong (Round 3 retro)

| 문제 | Mode E |
|---|---|
| 짧은 단문 5개 박기 | 긴 문장 + 접속사로 흐름 |
| every line 마침표 | 긴 문장에 마침표 적게 |
| 추상 단어 (구조, 비용) | 감각 단어 (달콤함, 늪) |
| "다음 행동 ~한다" close | 다음 reflection or question |
| 1인칭 가끔 | 1인칭 anchor 필수 |

---

## Mode D: {USER} 본인 voice (THE brand reference)

Round 2 finding: 외부 Korean 계정 (@크롱, @nowlovepan) 다 ㅋㅋ 씀. {USER} brand 안 맞음.
**진짜 reference는 {USER} 본인 message.** 이게 YOUR_HANDLE brand voice의 ground truth.

### {USER} 본인 voice patterns (관찰)

- **콜로키얼 발음대로 표기**: 잖아→자나 / 거야→꺼야 / 잖아→자나 / 했잖아→했자나
- **띄어쓰기 자유**: "할수 있자나", "그리고 ~ 시간대를 들쭉 날쭉하게"
- **~? 짧은 의문**: "오늘부터 하면 안 되?" / "지금 즉시 부터 하자."
- **마침표 거의 없음**: 줄바꿈 또는 그냥 끝
- **mood connectors**: 그리고 / 그래도 / 일단 / 지금 / 그럼
- **NO ㅋㅋ NO ㅎㅎ NO 자음**
- **NO aphoristic 마무리** — 그냥 다음 행동/다음 질문으로

### {USER} message examples (raw — 이게 정답)

```
"좀더 자주 할수 있어? 그리고 시간대를 들쭉 날쭉하게 해야 ai 인지 티가 안 나."
```
→ run-on, ~할수, 자연 mood connector, 사실 + 이유 직접

```
"한국말 너무 어색해.. 티나. 네가 쓴 티가 너무 나. 뭘 배운 거야?"
```
→ 짧은 단문 4개, 마침표 .. 두 점, 끝에 질문

```
"좀 자연스러워졌어. ㅋㅋ 이건 쓰지마. 좀더 공부 하고 와."
```
→ acknowledge + 명령 + 다음 행동. 해석/wisdom 0%.

### {USER} voice 적용 규칙 (Mode D — primary brand mode)

```
[관찰 1줄]

[관찰 2줄 OR 발견 1줄]

[다음 행동 OR 다음 질문]
```

- ~음 OR ~다 OR ~요 — 한 mode 일관
- 콜로키얼 발음 OK (자나, 꺼야)
- 띄어쓰기 strict 안 함
- 마침표 줄여쓰기 (한 post에 3개 미만)
- 격언 마무리 NO
- ㅋㅋ/ㅎㅎ NO

---

## Korean — 3가지 voice mode

### Mode A: @Krongggggg (long-form opinion / news commentary)

**Observed structure:**
- 한 문단 길게, run-on 문장 + 쉼표
- ~음 종결 일관 (declarative confidence)
- 감정 reaction 단어: "블랙코미디", "기어이", "[자음 reaction — banned for our brand]"
- 끝에 quote-tweet 항상 붙음
- 격언 마무리 NEVER. 사실 던지고 끝, 또는 [자음 reaction — banned for our brand]로 끝.

**Example raw:**
```
세계 최대 보안 인증기관 DigiCert가 고객 지원 채팅 하나에 뚫림. 백신이 위험하다고 네 번이나 막았는데 직원이 다섯 번을 눌러서 기어이 감염시킨 게 블랙코미디.
[Quote-tweet of source]
```

**What I was doing wrong:** breaking into multiple short balanced sentences, ending with aphorism. @크롱 doesn't do that.

### Mode B: @nowlovepan / 감자 (builder advice / receipt)

**Observed structure:**
- Stance opening: "AI 부업은 도구부터 배우면 망합니다"
- ~ㅂ니다 polite mixed with ~음 declarative
- 솔직히 / 진짜 / 그냥 / 근데 — emotional connectors
- Numbered lists (1. 2. 3.)
- Imperfections kept ("끝이에여" not "끝이에요" — typo signals human)
- Trails off mid-thought OR continues to next concrete tip

**Example raw:**
```
AI 글로 SNS 수익화 하려면 진짜 알아야 할 사람 톤 만드는 법

요즘 AI로 글 박는 사람 천지인데 솔직히 한눈에 다 들켜요

들키면 안 퍼지고 
안 크면 수익화 끝이에여

AI 티 안 나게 다듬는 방법들 소개해보겠습니다
```

**What I was doing wrong:** too clean, no emotional connectors, no imperfections.

### Mode C: @haaaaanna__ (lifestyle / casual)

**Observed structure:**
- 매우 짧음 (2-4 lines)
- 마침표 없음
- 줄바꿈 또는 comma list
- ~요 mode

**Example raw:**
```
전 이런 의미에서 지방 좋아해요
공원 많고 널찍하고 공기 괜찮고 집값 저렴하고
```

**What I was doing wrong:** trying to be casual but adding deep meaning. @한나 doesn't do meaning. She just says the thing.

---

## English — observed patterns

### @paulg (single-thought declarative)
```
Just as there are natural experiments, there are natural IQ tests.
```
- One sentence. Period. Stop.
- Aphoristic OK because it's THE WHOLE TWEET. No setup, no closer.

### @levie (stance + reasoning + quote-tweet)
```
SpaceX as a vertically integrated AI compute company makes an insane amount of sense.
[Quote-tweet of news]
```
- Single stance line as ENTIRE post (when QT'ing news).
- For longer takes: stance → 1-2 paragraphs reasoning → end on prediction or implication.
- No em-dash spam. No "It's not X, it's Y".

### @sama (vibe / state of mind)
```
ChatGPT feels very 'switched on' now
```
- Ultra-minimal. State current sense.

---

## What I kept doing wrong (Day 9 retro)

| 패턴 | Real human | 내가 한 것 |
|---|---|---|
| 마무리 | trail off / stop / next fact | aphoristic wisdom |
| 문장 길이 | run-on OR ultra-short, NOT balanced | balanced 2-line punch |
| 감정 표현 | [자음 reaction — banned for our brand], 솔직히, 미친, 와... | 0 emotion |
| 종결 | ~음 일관 OR ~요 일관 | mixed (~함/~다/~음 randomly) |
| 영어 사용 | tech terms only (claude, anthropic) | metaphor (fire, signal, polling) |
| Symmetry | asymmetric, ragged | "It's not X, it's Y" parallel |
| Quote-tweet | always for news | sometimes I just paraphrase |

## New rules (effective immediately)

### Korean post 작성 규칙

1. **Pick one mode**: A (news commentary), B (builder advice), C (lifestyle). 하나 고르고 끝까지 그 mode.
2. **Mode A**: ~음 일관 + run-on + 감정 reaction word + quote-tweet at end.
3. **Mode B**: ~ㅂ니다 + 솔직히/진짜/근데 connectors + lists + imperfections OK.
4. **Mode C**: 2-4 lines max + no period + ~요 + just the thing, no meaning.
5. **NEVER**: 격언 마무리. parallel 2-line punch. ~음/~다/~네 막섞기.

### English post 작성 규칙

1. **paulg mode**: one sentence, period, done.
2. **levie mode**: stance line + 1-2 reasoning paras + QT.
3. **sama mode**: ultra-short vibe. 5-10 words.
4. **NEVER**: connector adverbs (Crucially, Importantly), em-dash > 1, "It's not X, it's Y", listicle adjective stacks.

---

## Test re-applied to my deleted post

Deleted: "한라산 새벽 안개. cron이 알아서 일하는 동안 30초 polling만 보고 있다. 이게 시스템 잘 돌아가는 신호 — 내가 안 쳐다봐도 fire가 fire를 부르는 상태."

Why this failed:
- ❌ Mode confusion (lifestyle? builder?)
- ❌ "polling만 보고 있다" — clinical
- ❌ "신호 —" em-dash
- ❌ "fire가 fire를" calque
- ❌ "이런 날이 제일 좋아" — wisdom closer

If I had picked Mode C (@한나 style):
```
한라산 안개
저녁
cron 잘 돌아간다
```
That's it. No meaning. Just the thing. ← THIS is natural.

If Mode B (@감자 style):
```
오늘 새벽 cron 10번 돌았는데 다 잘 됨
근데 진짜 신기한 건 내가 자고 있을 때가 제일 일을 잘 함 [ㅋ - banned for our brand]
다음 주 결과 보고 또 풀게요
```
Run-on, [ㅋ - banned for our brand], trails off. ← THIS is also natural.

내가 한 거: 둘 다 아닌 합성 mode.

---

*Reviewer #8 must reference this doc. Not the abstract rules — the actual examples.*
