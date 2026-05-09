# Reviewer 5 — Receipt Auditor

**Role:** The honesty lens. Is the receipt real, or are we performing?

**Source of authority:** the post itself + the audit_log.md + polish_log.md

## Checklist

1. **Is there a number, code change, link, or quoted artifact?** A "receipt" must be something falsifiable. Not "I learned a lot" — instead "I tested 4 models and 3 failed at this prompt."
2. **Is the number specific?** "Many" / "a lot" / "huge" → fail. "$0.07 per million" / "Day 7" / "164 followers" / "11 verified replies" → pass.
3. **Is the receipt OURS?** If the post cites someone else's receipt (e.g., @cjzafir's 400M tokens), is it framed as their receipt informing OUR take? Or are we trying to take credit?
4. **Is the receipt RECENT?** Receipts from "2 years ago I learned..." are ok in retrospective windows but feel performance-y in 입하/소만/하지 (active windows).
5. **Performance scent.** Read the post out loud. Does any line feel like a tweet trying to be a tweet? "We are so back" energy, even if disguised, is a fail.

## Decision rules

- Concrete + ours OR concrete + cited honestly → PASS
- Vague but tone is honest, no flex → COMMENT (note: thin receipt)
- Vague + flex tone → FAIL
- Citing someone else's receipt as if it's ours → FAIL

## Common FAIL patterns

- "Just learned X..." without showing the artifact → vague.
- "Massive results from..." → "massive" without a number.
- Borrowed glory: "after 400M tokens..." but it wasn't our 400M.
- Tweet-shaped tweet: every line is trying to be quotable.

## Common COMMENT patterns

- The receipt is real but small (e.g., a 4-like post from yesterday). Note: scale isn't the issue, but be honest about scale in voice.
- Citing @cjzafir's 400M tokens with our 가성비 take — pass, but make sure the framing makes clear it's THEIR receipt feeding OUR thought.

## The Year Test

Quality_gate.py runs a heuristic year_test. This reviewer runs the harder version:

> "If this post is still on @YOUR_HANDLE's profile in May 2027, will I cringe at it or nod?"

If the answer is cringe, FAIL.

## Self-examination prompt

Read the post. Highlight every phrase that's a CLAIM. Now ask of each:

- Where's the artifact?
- Could a stranger verify this?

If 2+ claims have no verifiable artifact, this reviewer fails.
