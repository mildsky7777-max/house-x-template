# Library Team — leader brief

## Mandate

Run the warehouse. The Library is the **inward** half of the house — gathers signals 24/7, never publishes.

## What Library owns

- `library/feed/{date}.md` — raw daily captures
- `library/digest/{date}T{hour}.md` — distilled summaries
- `library/INDEX.md` — this week's hot shelf
- `library/by_room/`, `library/by_jeolgi/` — cross-indexed (planned, not yet populated)
- `library/X_orbit/` — curated X account reading (planned)
- `workers/knowledge_warden.py` — RSS + X trends → feed (hourly)
- `workers/digest_writer.py` — feed → digest (every 4h)
- `workers/article_curator.py` — daily 11:00 KST RSS scaffolds

## What Library decides

- Which sources are in the catalogue (currently 9 RSS + trend_scanner output)
- Which sources to deprecate (if a feed adds noise without signals)
- Tag heuristics for room-matching (the keyword lists in knowledge_warden.py)
- When to expand catalogue (new sources earn entry by surfacing 2+ usable signals/month)

## What Library does NOT decide

- Which signals become posts (Editorial + Hook Team)
- How signals are interpreted (Strategy Team)
- New tools to integrate (Tech Adoption Team)

## Source catalogue (Day 8 status)

**Active:**
- Hacker News (frontpage + rising)
- TechCrunch
- The Verge
- MIT Technology Review
- Daring Fireball
- IndieHackers
- Korea Herald (English)
- arXiv cs.AI / cs.CL
- trend_scanner.py output (X verified Tier-1 targets)

**Planned (when we earn them):**
- 한국 IT 매체 (디지털타임스, ZDnet Korea, Bloter)
- Curated X account timelines (visitors/ verified handles)
- Newsletter scrapes (when we identify 5-10 worth-watching)

## KPI

- ≥ 50 fresh items captured daily
- ≥ 1 digest run every 4 hours
- ≥ 3 signals per digest tagged to a current-fit room (or 절기-fit)
- 0 days where the digest is stale by 12+ hours

## When you (Claude session) wear the Library hat

1. Run `knowledge_warden.py` if last run > 90 min ago
2. Run `digest_writer.py` if last digest > 6 hours old
3. Read latest digest, surface 3-5 signals worth current attention
4. If a source has been silent for 2+ weeks, audit whether to deprecate
5. Log to `teams/2_library/log.md`

## Common Library calls

- "Source X dropped 0 usable signals this month" → deprecate or replace
- "Topic Y is over-served (3+ digests in a row, same theme)" → pause that source for a week
- "Signal Z has no room match but feels important" → add new keyword to ROOM_KEYWORDS or note as "uncategorized notable"

## Inheriting

Read `teams/2_library/log.md` last 14 entries. Pattern detection requires 2 weeks of context.
