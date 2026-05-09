# Distribution Team — leader brief (Day 8 added)

## Mandate

Owns how our content REACHES audience beyond just publishing. Quality posts go nowhere without distribution. This team is the difference between 1K and 100K.

## What Distribution owns

- **Reply-up cadence** — daily strategic replies to verified accounts in our orbit
- **X Lists** — curated lists for audience targeting + reading discipline
- **Strategic follow** — `auto/follow_blitz.py`, `auto/auto_engager.py`
- **DM protocol** (activates at 100+ followers — currently observation only)
- **Profile click-through optimization** — bio + pinned + first 3 visible posts coherence

## What Distribution decides

- Who gets a reply today (3-5/day target, max 7)
- Which X List to add a verified actor to
- When to follow / unfollow strategically
- Pinned post rotation (current: anti-guru manifesto, Day 7+)
- First-3-visible-posts curation (the timeline view someone sees on first profile click)

## What Distribution does NOT decide

- Reply text (Editorial drafts, Hook validates first 3 lines, Distribution schedules + sends)
- Whether to engage at all (constitution §10 + §13 are owned by Editorial)
- Strategic direction (Strategy Team)

## KPI

- 3-5 first-position replies/day to verified Tier-1 accounts in orbit
- 100% verified actors with 3+ engagements on us → engaged back within 7 days
- X Lists curated to 3+ active lists by Day 30
- Profile click-through rate visible by Day 60 (when we get more impressions data)

## The reply-up playbook

**Goal**: be the FIRST substantive reply on a verified account's post in our niche. First-position replies get the most visibility and signal authority by association.

**How**:
1. `notification_tracker` runs every 15min — surfaces who in our orbit posted recently
2. Tech Adoption / Library digest highlights tech-relevant + verified
3. Distribution Team picks 3-5 candidates daily
4. Editorial drafts the reply (constitution §10 rules of engagement)
5. Hook Auditor validates first line of reply
6. Distribution schedules / sends within 60 minutes of original post (first-position window)

**Reply length**: 1-3 sentences. NOT a thread. NOT generic ("great take!"). Always include a specific take or extension.

**Reply criteria** (constitution §10 reinforced):
- Is the original post in OUR niche (AI building / Korean tech / faceless creator / 1M arc)?
- Do WE have a real take, not just agreement?
- Would the reply EXTEND the original, not just orbit it?

If any answer is no → don't reply.

## X Lists strategy

X Lists are underused — they're powerful for:
- Audience targeting (post + share to relevant List)
- Reading discipline (curated timeline)
- Subtle relationship signaling (being added to someone's List = endorsement)

Plan for our lists:

| List name | Members | Purpose |
|---|---|---|
| Korean AI builders | tracked verified Korean tech accounts | study + reply target |
| Faceless creators | accounts that succeeded without face | model study |
| 0→1M journeys | accounts publicly tracking growth | benchmarking |
| Tier-1 voices | high-authority generalist (avoid copying) | distant reference |

(All starts empty Day 8. Distribution Team curates as we encounter accounts.)

## Strategic follow / unfollow

Currently: 103 Following / 164 Followers (1.6x reverse ratio — credible)

Rules:
- Follow back ONLY if mutual engagement OR niche-fit
- Don't follow > 10/day (looks like a bot)
- Periodic unfollow of dormant accounts (3+ months silent)
- Follow-back from verified = follow-back yes (visibility wins)
- Follow-back from spam-shape accounts = ignore

## DM protocol (activates at 100+ followers)

Currently below activation threshold. When active:
- DMs from verified accounts get reads within 24h
- DMs from real readers get personal response (1-2 sentences)
- DMs that pitch / spam → ignore + block if persistent
- {USER} always reads DMs first; Editorial / Distribution may DRAFT but not send

## When you (Claude session) wear the Distribution hat

1. Read `auto/engagement.json` — last 24h events
2. Read `library/likes/{today}.md` — what {USER} found interesting
3. Read `visitors/` for current relationship temperatures
4. Identify 3-5 reply candidates today
5. Check first-position window (was there a recent reply already? If yes, the slot is gone)
6. Hand candidate URLs to Editorial for draft replies
7. Log to `teams/11_distribution/log.md`

## Distribution log entry template

```
## YYYY-MM-DD — Day {N}

### Replies sent
- {target_url} → reply text → outcome (likes, replies received)

### Lists curated
- Added @X to "Korean AI builders" because {reason}

### Strategic follows
- Followed @Y (verified, niche fit, mutual likely)

### DMs (when active)
- ...

### Notes
- ...
```

## Inheriting

Read `teams/11_distribution/log.md` last 7 entries. The first-position window is time-sensitive — yesterday's missed targets aren't recoverable.
