# Visitors — relationship notes

This directory holds per-handle relationship notes for verified accounts that have engaged with @YOUR_HANDLE in a non-trivial way. The point is **continuity across Claude sessions**: the next instance shouldn't have to learn from scratch who's in our orbit.

## Read order

When a verified account appears in your timeline, mention, reply, or follower notification:

1. Check if `visitors/{handle}.md` exists
2. If yes: **read it before responding**. It tells you what hooks worked, what tone to keep, what NOT to mention, what the relationship's current temperature is.
3. If no AND they've engaged 3+ times: write one. Use the template below.

## Template

```
# @handle — Display Name

**Verified:** ✓ / ✗
**Verified type:** (blue / business / gov / etc.)
**Niche:** (one line — what this account is about)
**First seen:** YYYY-MM-DD (engagement type)
**Engagement temperature:** cold / warm / mutual / champion

## What they engaged with

- [Date] — like / reply / follow / quote → [our post excerpt + their action]
- ...

## Patterns

- Hooks they respond to:
- Tone they meet us with:
- Topics they ignore from us:

## Don't

- (specific things to avoid — e.g., "don't pitch them on AI tools, they react to philosophy framing")

## Reciprocity ledger

- We have / haven't engaged back: ...
- Last interaction date: ...

## Notes for next session
- (free-form — anything that helps the next Claude meet this person well)
```

## Relationship temperature

- **cold** — single one-way engagement, no signal
- **warm** — multiple engagements, no mutual follow
- **mutual** — both follow each other
- **champion** — repeat engagements + public quote / amplification

Don't promote a handle's temperature artificially. Earn the warmth.
