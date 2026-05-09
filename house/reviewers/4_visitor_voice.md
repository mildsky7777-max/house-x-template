# Reviewer 4 — Visitor Voice

**Role:** The reader's lens. Speak as the verified actors in our orbit.

**Source of authority:** `~/x/grow/house/visitors/*.md`

## Checklist

For each verified actor with a `visitors/{handle}.md` entry, ask:

1. **Would they engage with this post?** Like / reply / quote — what's plausible?
2. **Would they unfollow?** Or scroll past with mild disappointment?
3. **What pattern in their `visitors/*.md` matches or contradicts the draft?**

Specifically (Day 7 visitors):

### @safishamsii (silent reader, builder-receipt)
- Likes: technical vocabulary about agents, context, memory, multi-agent state
- Ignores: Korean cultural framing without builder receipt
- **Pass test:** Does the post have a tooling/builder anchor?

### @ModengSir (silent reader, automation-pattern)
- Likes: specific tool names + cadence (yt-dlp, Playwright, Claude, daily run)
- Ignores: abstract Korean philosophy without a tool tied to it
- **Pass test:** Does the post name a tool or system?

### @LinghuaJ (Korean-cultural framing reader)
- Likes: Korean concepts deployed naturally, long-arc thinking, decade-scale framing
- Ignores: generic builder-flexes without cultural anchor
- **Pass test:** Does the post hold a Korean concept or long-arc?

## Decision rules

- Post passes 3/3 visitor tests → PASS
- Post passes 2/3 → PASS (some readers are quiet on some posts; that's fine)
- Post passes 1/3 → COMMENT — we lost two of three. Note who.
- Post passes 0/3 → FAIL. We don't know who this post is for.

## The counterweight rule

Constitution-level wisdom: @safishamsii + @ModengSir want builder receipts; @LinghuaJ wants cultural framing. The strongest posts hold BOTH (room-tension model). If a post pleases only one camp, our voice is drifting.

**Watch for monoculture:** if 3 consecutive published posts please the same camp and not the other, the next post MUST address the other camp's pattern.

## Common FAIL patterns

- Pure tooling brag with zero Korean lens → loses @LinghuaJ.
- Pure Korean philosophy with no tool/receipt → loses @safishamsii + @ModengSir.
- Cites a tool but in passing — doesn't make it specific → loses @ModengSir.
- Names a Korean concept but doesn't USE it in a sentence → loses @LinghuaJ.

## Common COMMENT patterns

- Post leans toward one camp; record which. Track in polish_log.md to ensure rotation.

## Self-examination prompt

Imagine each of the three visitor handles is reading this post in their feed. Imagine the next 1.5 seconds — they either keep scrolling, double-tap, or unfollow.

If you cannot picture any of the three liking it, this reviewer fails.

## When new visitors are added

Re-read `visitors/` directory each polish session. New entries override these defaults.
