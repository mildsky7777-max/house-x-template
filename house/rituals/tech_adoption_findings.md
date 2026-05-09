# Tech Adoption findings — surfaced for night briefing

*Overwritten each `house-tech-research` run (every 3 days, 10:08 KST). Night briefing should pull the top 3 into Daily Performance Report.*

**Last run:** 2026-05-09 10:08 KST (Day 11 morning — first proactive baseline run)
**Next run:** 2026-05-12 10:08 KST

---

## Top 3 findings for tonight's Daily Performance Report

### 1. X Grok algorithm — full weights now public; reply-to-author-reply = 75-150x like

The Jan 2026 Grok-update source code + Typefully + Sprout Social converge:
- Reply that gets author reply = **75-150x** like (highest single action)
- Quote = 25x, Retweet = 20x, Reply = 13.5x, Bookmark = 10x, Like = 1x
- **External links: 30-50% reach reduction** — News Desk drafts that lead with a link are paying a heavy tax
- Text-only posts +30% engagement vs video on X (validates our text-first posture)

**What this means for us right now**: News Desk's reply discipline (5-min window for first commenter) is mathematically our highest-leverage habit. Any quote draft that puts the link at the top is throwing away a third to half its reach. ESCALATION.md has the new drift precedent.

### 2. Anthropic Advisor Tool (BETA, May 2026) — same polish quality at lower cost

Sonnet/Haiku as executor + Opus as on-demand advisor → near-Opus intelligence at lower compute. Direct fit for our 8-reviewer council architecture.

**Test queued for Day 13**: prototype a polish run where Sonnet executes the 8-reviewer pass and Opus advisor adjudicates only the conflicts. If quality holds → 3-5x our compute budget at the same cost.

### 3. Threads Ads launched 2026 with creator revenue share + 450M MAU (April 2026, +175M YoY)

Brand adoption accelerating, lower-competition window per multiple analyst sources. We have Typefully API v2 multi-platform support already wired (X / LinkedIn / Threads / Bluesky / Mastodon).

**Recommendation moved up**: Cross-Platform Team activation candidate moves from Day 30+ → Day 14-20. Activation still requires {USER} approval per AUTONOMY.md §5 (Cross-Platform is in the "ask first" list).

---

## Lower-priority findings (full detail in `teams/5_tech_adoption/log.md`)

- **Typefully API v2 added performance-data pull (April 2026)** — could replace the Playwright scrape for night-briefing Numbers section. Test queued Day 13-15.
- **EU AI Act Article 50 effective 2026-08-02** — machine-readable AI labels mandated. Reinforces Vanished Mysteries cross-promo ban; we should re-read the full text before Aug 2.
- **X pre-share AI-content detection rolling out 2026** — platform-level (not user-declared). 90-day suspension precedent. We are AI-as-gate not generation, so safer; if we ever ship AI imagery we must self-disclose.
- **Sonnet 4.6 (1M ctx) GA at standard pricing** — no beta header needed. Sonnet 4.8 anticipated.
- **Claude Code skill marketplace (4,200+ skills)** — quarterly survey calendared.
- **`x_trends_scanner.py` likely has a selector bug** — many entries showing "·" placeholder. Production team to check.

---

## One ask of {USER} (only if RARE — per AUTONOMY.md)

None this run. All findings are inside autonomy scope. Cross-Platform activation will need approval when proposed (Day 14-20 window) but not this morning.
