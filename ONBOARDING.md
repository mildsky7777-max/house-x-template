# X 자동운영 + Brand Voice System — Onboarding

> {USER}(@YOUR_HANDLE, YOUR_LOCATION 거주, Korean AI builder)가 Day 1–9 동안 Claude Code랑 같이 만든 시스템.
> "Going to 1M followers, documenting the path." — 채널을 집(House)처럼 짓는 운영 모델.
>
> 이 가이드는 그 시스템을 당신 brand로 fork해서 시작하는 법.

---

## §0. ROOT RULE — Identity Mode Switch

> Claude weights = 지식의 우주. 모든 직업·문화·언어·voice 다 들어있음. 데이터 부족이 아님.
>
> 문제는 default mode. Explicit identity switch 안 하면 "Claude that's writing a tweet" 켜짐 = generic / formal / translation-mode / hedging.

매 글·draft·견해 시작 전 명시:

| 상황 | Switch |
|---|---|
| 한국어 casual post | "YOUR_LOCATION 사는 한국 빌더" |
| 한국어 reflective | "긴 호흡 reflective 작가" |
| 영어 News Desk | "Documentary tech writer (Korean perspective)" |
| 우주 글 영어 | "NASA 천체물리학자" |

**한 줄 trigger** (한국어 쓸 때):
> "한국 사람으로 들어간다. translation mode 끔."

이게 시스템 모든 rule보다 위. Identity 안 바뀌면 그 아래 100개 rule 무용.

---

## 1. House 구조 — 핵심 폴더

```
~/your-x/
├── grow/
│   ├── house/                  ← The "집"
│   │   ├── constitution.md     ← §0 root rule + brand identity
│   │   ├── voice/
│   │   │   ├── banned.md       ← 절대 안 쓰는 표현
│   │   │   ├── signatures.md   ← 시그너처 표현 + voice 가이드
│   │   │   ├── observed_patterns.md  ← 관찰한 진짜 사람 voice
│   │   │   └── YOUR_LOCATION_anchors.md ← 본인 location/identity anchor
│   │   ├── reviewers/          ← 8 reviewer council
│   │   │   ├── 1_substance.md
│   │   │   ├── ...
│   │   │   ├── 7_hook.md
│   │   │   └── 8_authenticity.md ← AI tell 잡는 가장 중요한 reviewer
│   │   ├── teams/              ← 9 active + 4 reserve
│   │   │   ├── 1_editorial/
│   │   │   ├── 2_production/
│   │   │   ├── 3_growth/
│   │   │   ├── 4_strategy/
│   │   │   └── 5_tech_adoption/  ← 트렌드/도구/알고리즘 모니터링
│   │   ├── library/            ← News + likes + 트렌드 raw
│   │   └── workers/
│   │       └── quality_gate.py ← 발행 전 자동 헌법 체크
│   └── auto/                   ← 자동화 stack
│       ├── publish.py          ← Playwright X 발행
│       ├── scheduler.py        ← 30초 폴링 + 자동 fire
│       ├── trend_scanner.py    ← Verified Tier 1-2 발견
│       ├── x_trends_scanner.py ← Korean trending 시간별
│       ├── auto_engager.py     ← Verified engagement 답방
│       ├── notification_tracker.py
│       └── drafts.json         ← 큐
├── CLAUDE.md                   ← 이 시스템 사용 규칙 (당신 brand로 customize)
└── ONBOARDING.md               ← 이 파일
```

**Adapt 순서**:
1. `~/your-x/` 폴더 만들기
2. `CLAUDE.md` 본인 정보로 customize (handle, location, identity, 거부할 것)
3. `house/constitution.md` 본인 brand 적기 (정체성, 보이스, 룸, 의식)
4. `voice/observed_patterns.md` 비워두고 본인 reference 계정 모이는 대로 채우기

---

## 2. First Day — 30분 setup

**필요한 것:**
- Claude Code (이미 사용 중)
- Python 3.10+
- Playwright (`pip install playwright && playwright install chromium`)
- X account (Premium 권장 — Edit 기능)
- macOS (cron) 또는 Linux (systemd)

**Step 1: 초기 폴더**
```bash
mkdir -p ~/your-x/grow/{auto,house/{voice,reviewers,teams,library,workers}}
cd ~/your-x
```

**Step 2: CLAUDE.md** — 당신만의 사용 규칙. {USER}의 [CLAUDE.md](#claudemd-template) 참고해서 customize:
- 본인 X handle
- 거부 항목 ({USER}: AI 보이스 길게 X, 영상 촬영 X)
- 작업 톤 (간결, 자율 실행, 한국어/영어 등)
- 채널 컨셉

**Step 3: Constitution v1**
`house/constitution.md` 작성. 핵심 sections:
- §0 root rule (위에 박혀있음 — 그대로 복사)
- 정체성 1줄 ("Going to 1M / building X" 같은)
- Voice modes (Mode A 뉴스, Mode B 빌더, Mode C 캐주얼 등)
- 룸 (브랜드의 대표 토픽 영역들)
- 의식 (매일 / 매주 ritual)
- 절대 금지 (politics 등)

**Step 4: Quality Gate**
`house/workers/quality_gate.py` — 발행 전 자동 체크.
{USER}의 gate 복사해서 시작 (banned phrases, AI tells, 직역체, 종결 mix, em-dash, 격언 close 등 잡음).

**Step 5: 첫 발행 manual**
자동 stack 짓기 전에 `claude` 한 번 띄우고 직접 draft 1개 발행. Reviewer가 어떻게 작동하는지 체감.

---

## 3. Auto Stack — 점진적으로

처음부터 다 만들지 마. 한 worker씩.

**Day 1–3**: `publish.py` 1개. 수동 큐 + 직접 ship.

**Day 4–7**: `scheduler.py` + `drafts.json` 큐. Scheduled draft 자동 fire.

**Day 7+**: `trend_scanner.py` (verified 트렌드 발견) + `auto_curator.py` (트렌드→draft scaffold).

**Day 9+**: `auto_engager.py` (들어오는 verified engagement 자동 답방).

**Day 10+**: `notification_tracker.py` (15분 폴링 engagement 기록) + receipt ledger.

---

## 3.5. Auto-reply 자세히 ({USER} mandate Day 11)

X에서 follower 빠르게 늘리는 leverage = **reply discipline**. Auto-reply가 그 backbone.

### Two-layer reply system

**Layer 1 (auto): `auto_engager.py`**
- Cron으로 30-60분마다 fire
- Verified accounts (체크표시) 또는 top-tier followers가 본인 post에 reply/like/quote 했을 때 — 본인 timeline에서 그 사람 latest post에 자동 답방
- Generic reply 안 함 — 그 사람 post 내용 읽고 1-2줄 thoughtful reply
- Rate-limited (시간당 5-10 reply max)

**Layer 2 (manual): top 50 verified daily window**
- 매일 30-60분 — 본인 timeline + 핵심 niche keyword 검색 → 답글 5-10개 manual quality
- 자동 reply가 안 잡는 longer-form thought reply
- Network effect 만드는 layer

### auto_engager.py 작동 방식

```
1. notification_tracker.py 가 15분마다 X notifications 읽음
2. 새 verified engagement 발견 → engagement_log.json 적재
3. auto_engager.py 30-60분마다:
   - log 읽고 답방 안 한 verified accounts 골라
   - 그 사람 latest 1-2 post 본문 읽음
   - quality_gate 통과하는 reply 1-2줄 만듦
   - Playwright로 발행
   - reply_log.json 기록
4. notification_tracker가 그 reply의 새 engagement 또 추적
```

### Reply quality bar
- ❌ "Thanks for the like!" — 절대 X
- ❌ "Great post!" 같은 generic
- ❌ 같은 사람 5번 이상 reply
- ✅ 그 post 내용 specific reference
- ✅ 본인 receipt 또는 짧은 take 추가
- ✅ Reply도 viral light voice 적용 (1-3 lines)

### 지인이 첫 setup 시 권장 단계
1. 첫 1주: auto_engager.py 끄고 manual reply만 (voice 익숙해질 때까지)
2. 2주차: auto_engager.py 켜고 결과 검증 (rate-limit 5/hr)
3. 3주차: rate-limit up + monitor reply quality 비율
4. Reply 답방률 확인 — 본인 reply 받은 사람 중 다시 engage 비율

### 위험
- Auto reply 너무 많으면 spammy 인식
- X bot detection — manual + auto mix 필수
- Account suspension risk 만약 generic reply spam — quality bar 엄격

핵심: **각 worker는 1개 책임만.** Flask 1개 (port 5050)로 큐 + UI + API 통합.

---

## 4. Reviewer Council — 8 reviewers

각 draft는 8 reviewer를 통과해야 발행:

1. **Substance** — 진짜 받침 있는 말인가?
2. **Brand fit** — 우리 집에서 나올 만한 말인가?
3. **Hook (3-line)** — 첫 3줄에 사람 잡히는가?
4. **Risk** — 정치/종교/legal 위반?
5. **Cadence** — 발행 시간/빈도 의미 있는가?
6. **Receipt** — 받침되는 fact/숫자/source 있는가?
7. **Hook Auditor** — 첫 3줄 redo
8. **Authenticity Auditor** — AI 티 안 나는가? (가장 중요. §0 위반 잡는 reviewer)

각 reviewer는 `house/reviewers/N_name.md` 하나의 doc. Claude가 그 doc 기준으로 PASS/FAIL/COMMENT.

**Authenticity Auditor가 핵심**:
- 한국어 직역체 잡음 (~에 의해, ~가지고 있다, ~하는 것)
- AI tells 잡음 (delve, tapestry, "It's not X, it's Y", em-dash spam)
- ㅋㅋ/ㅎㅎ brand 정합성 체크
- Fabrication 잡음 (가족/과거 invent 금지)
- §0 root rule 적용 — identity switch self-test

{USER}의 [reviewers/8_authenticity_auditor.md](#reviewer-8-template) 그대로 복사 추천.

---

## 5. Voice 발견 — 외부 reference 깊이

**가장 중요한 단계**. 본인 voice 모르면 system 다 무용.

순서:
1. **본인이 follow하는 사람들** scrape (X following list) — 본인이 좋아하는 voice가 거기 있음
2. **본인이 like한 사람들** scrape — 더 narrow signal
3. **각 계정 raw post 보관** — `voice/exemplars_*.md`로 저장
4. **패턴 추출** — opener / transition / closer / 1인칭 anchor / 종결 / em-dash
5. **본인 voice = 그 사람들 mix + 본인 identity**

{USER}의 발견:
- @gimhyeo02389130 (프로그래밍좀비) = reflective literary 한국어 → mildsky brand에 가장 가까움
- @크롱 = run-on opinion + ~음 일관 + ㅋㅋ → mildsky brand에 안 맞음 (ㅋㅋ 안 씀)
- @nowlovepan (감자) = builder advice + ~ㅂ니다 mixed → 부분 차용

본인은 본인 reference 발견해야 함. 시간 들여서.

---

## 6. Scheduled Tasks (cron)

매일 폴리시 task — Claude가 자동으로 draft 짜고 큐에 채움:

```cron
31 11 * * *  morning polish (read library digest, draft 2-3 posts)
32 15 * * *  afternoon polish (lighter, fill midday gap)
32 19 * * *  evening polish (replies, late-day signals)
33 23 * * *  night briefing (daily performance report)
8 10 */3 * * tech research (proactive trend research, every 3 days)
0 22 * * 0   weekly retro (Sunday strategy synthesis)
```

각 task는 `~/.claude/scheduled-tasks/{name}/SKILL.md`로 저장. Claude가 그 prompt 따라 실행.

KST/UTC 주의 — macOS cron은 local time 기준.

---

## 6.5. Pro plan 라이트 버전 (사용량 절약)

{USER}의 풀 셋업 (매일 polish 3회 + night briefing + tech research)은 Claude Pro 5시간 window 한도를 빠르게 소진함. **Pro 사용자는 라이트 버전으로 시작.**

### 라이트 셋업 — 매일 task 1-2개만

```cron
# 매일 Morning Polish 1회만 (heaviest task)
31 11 * * * morning polish
# 매주 일요일 가벼운 retro 1회 (월간으로 줄여도 됨)
0 22 * * 0 weekly retro (light)
```

**뺀 것:**
- afternoon polish (불필요 — morning에 24h 분량 한 번에)
- evening polish (manual session으로 대체)
- daily night briefing (heavy — weekly retro로 통합)
- tech research every-3-days (heavy — 월 1회로)

### Manual session으로 보완

매일 자동 task 1회 + Claude Code interactive session 1-2회로 충분.

- 아침: Claude Code 열고 morning polish output 확인 + 본인 손으로 draft 1-2개 보강
- 저녁: 발행 결과 보면서 Claude한테 30분 retro

### Pro 사용량 견적 (라이트 셋업)

| Task | 빈도 | 1회 사용량 | 일/주 사용 |
|---|---|---|---|
| Morning polish | 매일 1회 | medium | 7회/주 |
| Weekly retro | 주 1회 | medium | 1회/주 |
| Manual session | 매일 1-2회 | varies | 7-14회/주 |

→ Pro 5h window: 매일 1-2 session OK. 한도 부족하면 Max 5x로 업그레이드.

### Auto stack 라이트

```
~/your-x/grow/auto/
├── publish.py             ← 필수
├── scheduler.py           ← 필수
├── quality_gate.py        ← 필수
├── trend_scanner.py       ← 선택 (light worker, Claude usage 안 씀)
└── x_trends_scanner.py    ← 선택 (Playwright만, Claude 안 씀)
```

**Claude usage 안 쓰는 worker는 다 OK** — Playwright/cron으로 도는 거. trend_scanner / x_trends_scanner / notification_tracker 등은 Pro 한도와 무관.

**Claude usage 쓰는 task만 줄임** — scheduled-tasks의 polish/briefing/retro/research.

### 업그레이드 timing

지인이 라이트로 시작 → 1주일 후 결과 보고 결정:
- "더 자주 발행하고 싶다" → afternoon polish 추가 → Pro 한도 넘으면 Max
- "현재로 충분" → Pro 유지

---

## 7. 가장 중요한 lessons ({USER}가 9일에 배운 거)

**Day 1**: 시스템 처음 짠 거 너무 자기검열적이었음. 더 자주 발행 + 시간대 jitter (AI 티 안 나게).

**Day 5**: News Desk 도입. 미국/세계 사람들이 본인 X로 정보 얻게 만드는 게 differentiator.

**Day 7 evening**: 정체성 reset. "Korean AI builder" → "lantern walker / Going to 1M".

**Day 8**: 8th reviewer (Authenticity Auditor) 추가. {USER}: "AI 자동화 티가 안 나게 사람이 하고 있다는 느낌도 나야 해."

**Day 9 morning**: CEO retrospective. Claude가 react만 하지 말고 PROACTIVE해야. Tech Adoption Team이 {USER}보다 먼저 발견.

**Day 9 evening**: Voice naturalness 깊은 reset.
1. ㅋㅋ brand off (다른 한국 계정 다 쓰지만 mildsky 안 씀)
2. 직역체 7가지 패턴 자동 detection (~에 의해, ~가지고 있다 등)
3. AI tells 50개+ 자동 detection (delve, tapestry, "It's not X, it's Y" 등)
4. **§0 root rule 발견**: identity switch가 모든 sub-rule 위. data 부족 아님 — Claude weights에 다 있음. mode switch가 핵심.

---

## 8. 처음 1주일 권장 흐름

| Day | Task |
|---|---|
| 1 | CLAUDE.md + constitution.md + 첫 manual draft |
| 2 | Voice 발견 — 본인 follow/like scrape |
| 3 | Quality gate.py 작성 |
| 4 | 8 reviewer doc 1개씩 작성 (Authenticity 우선) |
| 5 | publish.py + 첫 자동 발행 |
| 6 | scheduler.py + drafts.json 큐 |
| 7 | 첫 retro — 무엇이 작동했는가 |

매일 1개 post + 매일 system 1개 fix. 10일이면 자동 stack + voice system 완성.

---

## 9. 핵심 원칙 요약

1. **§0 Identity switch가 모든 것 위** — data 부족 아님, mode switch.
2. **집을 짓는 메타포** — 채널 = 손님 머무는 집. 결과는 부산물.
3. **8 reviewer 통과** — 발행 전 8각도 점검.
4. **Quality gate 자동** — 직역체/AI tell/em-dash spam/격언 close 자동 차단.
5. **Mode A/B/C/D/E 변신** — News commentary / Builder / Casual / 본인 message / Reflective.
6. **Fabrication 금지** — 가족/과거 invent 안 함. 현실 anchor만.
7. **Identity 흐릿하면 — 다시 시작.**

---

## 10. 막히면 어디 보나

- Voice 헷갈림 → `house/voice/observed_patterns.md` + 본인 follow scrape 다시
- 발행 실패 → `auto/drafts.json` + `auto/.x_publish_log.json`
- 너무 많이 발행됨 → `house/teams/4_strategy/log.md`
- 너무 robotic → §0 root rule 다시 + identity switch trigger
- 트렌드 놓침 → `house/library/x_trends/{date}.md`

---

## CLAUDE.md template

```markdown
# {당신 이름} X 프로젝트 — Claude 작업 규칙

## 사용자 프로필
- {언어} 소통
- {선호 톤}
- {권한 모델 — 일일 승인 vs 자율}

## 채널 정보
- X: @{handle}
- 컨셉: {1줄}

## 자동화 stack
~/your-x/grow/auto/ + ~/your-x/grow/house/workers/

## 글로벌 작업 규칙
### 하지 말 것
- {거부 항목 list}

### 항상 할 것
- {필수 항목 list}
- 작업 디렉토리: ~/your-x/

## 다음 세션 시작 시 필독
1. ~/your-x/grow/house/constitution.md
2. ~/your-x/ONBOARDING.md (이 파일)
3. ~/your-x/grow/house/voice/banned.md
4. ~/your-x/grow/house/voice/signatures.md
5. https://x.com/{handle} 최근 발행물 — 본인 voice 듣기
```

---

*{USER} @YOUR_HANDLE — Day 9 evening, 2026-05-07. House가 자라는 과정. 100만 가는 길 보고 있는 사람한테.*
