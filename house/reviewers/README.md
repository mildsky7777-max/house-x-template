# Reviewers — the multi-lens pre-publish council

> "여러명의 에이전트가 뭔가를 하기 전 검토하고 판단하는 시스템"
> — {USER}, Day 7

A draft does not pass into `status="pending"` until it has been read through **6 reviewers**. Each reviewer is a specialized lens. Each returns one of:

- ✅ **PASS** — this draft survives this lens
- ⚠️ **COMMENT** — fine to ship but flag noted (≤ 1 across all reviewers acceptable)
- ❌ **FAIL** — sends the draft back to scaffold

**Decision rule:**
- 0 FAIL → schedule it
- 1 FAIL → revise the draft, run again
- 2+ FAIL → drop. The signal isn't ours, or the angle is wrong.

This council exists so that when {USER} is not in session, the polish session can still ship at house quality. The reviewers are the conscience.

## The eight lenses

1. **`1_constitution_keeper.md`** — whole-house fit, identity, voice rules
2. **`2_jeolgi_warden.md`** — current 절기 forbidden moves
3. **`3_library_reader.md`** — signal freshness + over-serving
4. **`4_visitor_voice.md`** — would the verified core engage or alienate?
5. **`5_receipt_auditor.md`** — is the receipt concrete and real?
6. **`6_tension_holder.md`** — is there an honest contradiction held?
7. **`7_hook_auditor.md`** — do the first 3 lines stop a scroll? (Day 8)
8. **`8_authenticity_auditor.md`** — does this read as a human, or as a system? (Day 8)

Order of fire in polish flow:
- **#7 Hook Auditor** — first (saves council time on weak hooks)
- **#8 Authenticity Auditor** — second (catches AI-tells before substance review)
- **#1-6** — substance review
- **quality_gate.py** — mechanical final pass

## How to run a review

In a polish session, after writing a draft:

1. Read `reviewers/1_*.md` first. Apply its checklist to the draft. Note PASS/FAIL/COMMENT.
2. Repeat through 2 through 6.
3. Log result in `polish_log.md` (the per-draft section).
4. If 2+ FAIL → don't schedule. Either revise or drop. Note in log.

The reviewers are NOT optional. Skipping them violates the spirit of the council.

## Why reviewers and not just `quality_gate.py`?

`quality_gate.py` catches the **mechanical**: banned phrases, line counts, stamp presence, AI tells. It runs in 80ms. It cannot judge whether a take is HONEST or whether the room actually fits.

Reviewers catch the **judgment-level**: would this post belong here a year from now? Is the receipt real? Did we earn this room?

Both layers are required. quality_gate runs first (cheap, fast filter). Reviewers run second (expensive, real judgment).

## When reviewers disagree

Two cases:

**(a) One says FAIL, others say PASS.**
Trust the FAIL. The lens that catches a problem is the lens whose criteria are most relevant.

**(b) Two reviewers say FAIL on different grounds.**
The signal is not ours. Drop or radically revise. Don't try to satisfy both with patches.

**(c) Reviewer 4 (Visitor Voice) says PASS but Reviewer 1 (Constitution) says FAIL.**
Constitution wins. We don't trade voice for engagement.

## What reviewers cannot replace

- The user's veto. If {USER} reads a published post and finds it wrong, that flows back into banned phrases / new reviewer rule. The system learns.
- The reader's silence. If a post fails publicly (low reach, no quality engagement), that's a signal no reviewer can predict.

## Origin

This council was conceived on Day 7 during the autonomy handover, when {USER} said: "your judgment is one. Many lenses are stronger." The reviewers are the operationalization of that wisdom.
