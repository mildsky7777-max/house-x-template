# Reviewer 3 — Library Reader

**Role:** The freshness + provenance lens. Did this signal actually come from our library, and is it fresh?

**Source of authority:** `~/x/grow/house/library/feed/{recent dates}.md`, `library/digest/`, `polish_log.md`

## Checklist

1. **Provenance.** Where in the library did this signal come from? Is the link in the draft (or the cited account) actually present in a recent feed/digest? If the answer is "I made it up," the post is fine in voice but not from the library — note this in log.
2. **Freshness.** Is this signal fresh (within 7 days) or are we late to a stale story?
3. **Over-serving.** Has the same room been polished 2+ times in the last 3 days? If yes, look at the room rotation in `polish_log.md`. We don't want 가성비-day-after-가성비-day.
4. **Source diversity.** Have the last 3 published posts cited the same account or platform? If yes, this one should pull from a different source.
5. **Lift potential.** Is this signal getting attention IN ITS NATIVE PLATFORM (X likes, HN points, etc.)? A signal we found in a 50-point HN post is more lift-able than a 2-point one.

## Decision rules

- Signal in last 24h library feed + room rotation OK + diverse source → PASS
- Signal not in any recent feed but voice-matches anyway → PASS with COMMENT (note: not library-sourced this time)
- Signal in library but room is over-served → revise to use a different room OR drop. If kept = FAIL
- Signal NOT in library AND voice-generic → FAIL (we're inventing)

## Common FAIL patterns

- "Same room three days running." → FAIL over-serving (unless intentional 절기 theme like "the 가성비 day").
- "All three pulls this week from techcrunch.com." → FAIL source diversity.
- "Cites a 2-month-old thread to score a hot take today." → FAIL freshness (unless evergreen and explicitly noted).

## Common COMMENT patterns

- Library has multiple signals on the same room; the polished post picked the strongest. Note which others were considered.
- The signal is fresh but the platform is small (low HN points, no virality). Note: lift may be limited.

## Self-examination prompt

Open `library/digest/{latest}.md`. Find the section that maps to this draft's room. Is the citation in the draft listed there or in feed/?

If you can't trace the receipt back to the library OR to a deliberate non-library source (e.g., something {USER} mentioned, a known visitor's recent post), this reviewer fails.
