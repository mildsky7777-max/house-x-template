# News Radar — News Desk Team #13

> Current breaking + analysis queue. Updated when news signals are surfaced.

**Last updated:** 2026-05-07 11:38 KST (Day 9 — house-daily-polish autonomous run)

---

## Active queue (waiting to be addressed)

(empty — Day 8 setup)

## Recently shipped (last 7 days)

(none yet — News Desk just activated Day 8 evening)

## Watching (not yet actionable)

| Source | Topic | Why we're watching | Decision time |
|---|---|---|---|
| WebMCP (Chrome) | Will X / Twitter adopt? | Tech Adoption priority | Quarterly check |
| Anthropic | Sonnet 4.6 / Opus 5 release | Bridge format opportunity | Monitor changelog |
| Naver / Kakao Brain | Q2 2026 announcements | Korean→English bridge | Watch official blogs |

## Format rotation tracker

To avoid monoculture:

| Format | Used (last 4 weeks) | Next priority |
|---|---|---|
| 1: Korean → English | 3 (a4fd1bce Day 8 21:00; 760e565b Day 9 18:43; a05e198c Day 10 06:14 nabeno_kitchen YT/TikTok) | medium |
| 2: Global → Korean angle | 4 (Day 8 21:53 Iran/chip; Day 9 ASML; Day 9 DeepSeek; Day 9 Voicebox; Day 9 Claude/Blender) | **HARD COOLDOWN until Day 11** |
| 3: Both → synthesis | 2 (Day 9 14:44 @1osabori Japan→Korea; Day 10 09:42 0edff330 Match Group US/KR-indie) | medium |
| 4: World commentary (Korean lens) | 3 (Day 9 16:43 Iran armistice; Day 10 07:08 AI doctor; Day 10 13:27 bfe6c199 NPR Chinese AI labor) | rotate Day 11 |

## Source diversity tracker

| Source | Last cited | Rotation status |
|---|---|---|
| Daring Fireball | Day 9 (3 times in 3 days) | **HARD COOLDOWN** until at least Day 11 |
| TechCrunch | Day 10 09:42 (Match Group) — 3rd citation in 24h | **soft cooldown** Day 11+ |
| The Verge | not yet cited in posts | available |
| MIT Tech Review | not yet cited | available |
| Hacker News (story) | not directly cited | available |
| NPR | Day 10 13:27 (1st news-desk citation, Chinese AI labor) | available |
| Aljazeera | Day 9 16:43 (Iran armistice) | available |
| Wired | not yet cited | available |
| Engadget | not yet cited | available |
| BBC News | not yet cited | available |
| Korean sources | Day 9 18:43 (@haaaaanna__) | available (rotate among Korean sources) |
| Japanese visitor likes | Day 10 06:14 (@nabeno_kitchen YT/TikTok); Day 9 14:44 (@1osabori) | available — third use possible |

## Korean source onboarding (Day 9+ task for Tech Adoption + Library)

Add to knowledge_warden.py FEEDS list:
- 디지털타임스 RSS
- ZDnet Korea RSS  
- Bloter RSS
- AI타임스 RSS

Verify each feed is:
1. Valid RSS / Atom
2. English-readable (or translatable)
3. Not paywalled

## Verification log (when news posts ship)

For each News Desk post, log here:
```
- Date | Tier | Topic | Source 1 | Source 2 | Verdict
```

- 2026-05-07 (Day 10 06:14 fire) | Tier 2 | a05e198c YT vs TikTok revenue | @nabeno_kitchen post (Japanese ✓) | TechCrunch / industry-known revenue ratio (TikTok creator fund < YouTube AdSense per-view, then split shifts on different volume models — Japanese receipt aligns with industry pattern) | PASS
- 2026-05-07 (Day 10 09:42 fire) | Tier 2 | 0edff330 Match Group AI hiring | TechCrunch (digest 2026-05-07T08) | Match Group official statement quoted in TC article | PASS
- 2026-05-07 (Day 10 13:27 fire) | Tier 2 | bfe6c199 NPR Chinese AI labor | NPR article (digest 2026-05-07T08, 危機 section) | Korean labor history 1997 IMF / 2008 — historical fact verifiable from public record | PASS

## Drift log (verification failures)

If a post claims something that turns out wrong:
```
- Date | Post id | Claim | Reality | Correction issued (yes/no/where) | Lesson
```

(empty — protect this list at all costs)

---

## ⚠️ The hard rule — opinion required

Every News Desk post must contain {USER}'s stance line, not just translation/observation.

**Self-check before scheduling**:
- "What's the stance line in this post?"
- If you can't point to a single sentence that states {USER}'s opinion → REJECT or rewrite

This is a HARD failure mode for News Desk. Without opinion = RSS aggregator = no reader value.

## Update protocol

News Desk team session:
1. Read latest digest + likes for news signals
2. Classify any new news into queue (Tier 1/2/3) or skip
3. **For each candidate, draft the stance line FIRST** — if the stance is weak, the whole post is weak
4. Update format rotation tracker after each ship
5. Update source diversity tracker after each citation
6. Watch source cooldowns (Daring Fireball locked until Day 11)
7. Log to `teams/13_news/log.md`
