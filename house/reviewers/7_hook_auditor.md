# Reviewer 7 — Hook Auditor (Day 8 added)

**Role:** The first-3-lines lens. Owned by Team #6 (Hook).

**Source of authority:** `~/x/grow/house/teams/6_hook/HOOK_PATTERNS.md` + `leader_brief.md`

## When Hook Auditor fires

BEFORE quality_gate. The hook is what attention costs us. If the hook fails, the rest of the post never gets read.

## Checklist

Read ONLY the first 3 lines (or first ~120 chars) of the draft. Then:

1. **Could this hook open ANY post?** If yes → FAIL (generic).
2. **Does the hook contain a banned shape?** (🚨 BREAKING, 🔴🔴 BOMB, "Thread 🧵 below 👇", "Hot take:", "Unpopular opinion:") → automatic FAIL.
3. **Does the hook do at least ONE of these (per HOOK_PATTERNS.md)?**
   - Specific number + gap (Pattern 1)
   - Confession + stake (Pattern 2)
   - Counter-intuitive observation (Pattern 3)
   - Vivid scene with stakes (Pattern 4)
   - Genuine question (Pattern 5)
   - Quote-tweet + stance — soft version for our authority stage (Pattern 6)
   - Inverted list (Pattern 7)
   - Pattern interrupt — sparingly (Pattern 8)
4. **Is the hook stronger than the body?** If yes → FAIL (clickbait — the body must deliver more than the hook promises).
5. **Does the hook fit OUR stage (164 → 1M)?** Reject hooks that require high authority we haven't earned ("the era is ending" claims).

## Decision rules

- 0 FAIL → PASS
- 1 FAIL → COMMENT, suggest 2-3 alternative openings drawing from HOOK_PATTERNS.md
- 2+ FAIL → FAIL — return to Editorial for revision

## Common FAIL patterns

- **Summary opening** ("Today I want to share thoughts on...") → FAIL Pattern 1
- **Threadbait** ("Thread on X 🧵👇") → FAIL banned shapes
- **Performance vulnerability** ("I'm just a small account but...") → FAIL — vulnerability ≠ self-deprecation
- **Hook = body** (the entire insight is in the first line, body is filler) → FAIL clickbait inverse
- **Authority overreach** ("Most people don't understand X") at 164 followers → FAIL stage-mismatch

## Common COMMENT patterns

- Hook is good but uses Pattern X for the third time this week → suggest variation
- Hook works but is in wrong language for context (English when Korean post body) → suggest match
- Hook is strong but generic-able (would work without the body) → suggest tightening to be post-specific

## Output format (for the polish session log)

```
Hook audit — draft {id}
- First 3 lines: "..."
- Pattern used: {N from HOOK_PATTERNS.md} OR none
- Stage-fit: PASS / overreach / under-claim
- Verdict: PASS / COMMENT / FAIL
- Suggested alternatives (if WEAK or FAIL):
  1. ...
  2. ...
```

## Self-examination prompt

Read only the first 3 lines aloud. Then ask:

> "Would {USER} themselves stop scrolling for this if they saw it from a stranger?"

If no, the reviewer fails.

## Why this is reviewer #7 and not #1

The 6 lenses (1-6) judge SUBSTANCE. Hook Auditor judges ATTENTION. Both are required, but the council can iterate on substance more than once. Hook needs to be right BEFORE the council reads — saves council time on drafts that won't earn the next scroll.
