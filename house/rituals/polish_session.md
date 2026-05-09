# Polish session ritual

The bridge between **library** (수집) and **timeline** (발행).

When {USER} (or Claude-in-session) sits down, this is the ritual. The library has been gathering 24/7; this is the act of cooking from the storeroom.

## Before you write

1. **Read** `~/x/grow/house/almanac/CURRENT.md` — what 절기? what room?
2. **Read** the most recent `~/x/grow/house/library/digest/{date}T{hour}.md` — what signals?
3. **Read** `~/x/grow/house/library/INDEX.md` — what's hot this week?

Open both `library/INDEX.md` and the almanac CURRENT.md side by side. The room from CURRENT determines what you can ship in this 절기. The library has the raw material.

## The ritual (≈ 30 min, 2-3 posts polished)

### Step 1 — pick (5 min)

From the digest, pick **2-3 signals** that meet ALL of these:

- The signal's room is **NOT** in the current 절기's `forbidden_rooms` (e.g., 빨리빨리 is forbidden in 입하)
- The signal has a **specific receipt** (a number, a quote, a real artifact — not a vibe)
- You can **add** to it (Korean lens, contradiction, deeper read) — not just summarize

If a signal can only be summarized, skip it. The library is full of signals; pick the ones that you have something to say about.

### Step 2 — polish (15-20 min)

For each pick, write a draft using one of the signature shapes from `voice/signatures.md`:

- **Triplet + Pivot** (the @cnemalek 38K shape) — 3 parallel lines + Korean-lens pivot
- **Two-line punch** — statement + counter-statement
- **Quote-tweet pattern** — direct take + receipt + URL

The post structure should be:

```
[the signal in one quoted/cited line]

[your take in 2-4 lines, using the room]

⸻

[a deeper second beat — the ROOM made specific]

[optional: URL on its own line]

Korean builder, Day X. Inside <절기>.
```

### Step 3 — gate (2 min)

Run `quality_gate.py --text "$(cat /tmp/draft.txt)"` for each.

**Must pass** all checks. If `publish_safety` flags lines/emoji prefix, restructure. If `concept_usage` says "stacking 3+ concepts," cut to 1-2.

### Step 3.5 — Council of Reviewers (15 min — the deepest filter)

After quality_gate passes, run the draft through the **6 reviewers** in `~/x/grow/house/reviewers/`:

1. **Constitution Keeper** — read `1_constitution_keeper.md`, apply checklist
2. **Jeolgi Warden** — read `2_jeolgi_warden.md`, check current 절기's forbidden room
3. **Library Reader** — read `3_library_reader.md`, verify provenance + freshness + room rotation
4. **Visitor Voice** — read `4_visitor_voice.md`, run the 3-visitor test
5. **Receipt Auditor** — read `5_receipt_auditor.md`, falsifiability check
6. **Tension Holder** — read `6_tension_holder.md`, second-beat check

For each reviewer, return PASS / FAIL / COMMENT.

Apply `reviewers/ESCALATION.md` decision rules:
- 0 FAIL → schedule
- 1 FAIL → revise the relevant axis, re-run only that reviewer
- 2+ FAIL → drop or radically revise

Record EVERY reviewer's verdict in the polish_log.md entry.

### Step 4 — schedule (5 min)

Add to `drafts.json` with `status="pending"` and a `scheduled_at`. Slot guidance:

| Slot (KST) | UTC | What goes here |
|---|---|---|
| 06:00 | 21:00 prev | Day-X milestone, 절기-aware |
| 09:00 | 00:00 | Hero post — concept + receipt |
| 13:00 | 04:00 | Mid-day reply window OR library-harvest |
| 17:00 | 08:00 | US-East-morning slot (good for global reach) |
| 21:00 | 12:00 | Hero post for US-East work-day |

Distribute rooms across slots; don't let one day go monothematic unless that's the intent.

### Step 5 — log (3 min)

Append a one-line note to `~/x/grow/house/rituals/polish_log.md` (this file's sibling):

```
## YYYY-MM-DD HH:MM KST — Day X — by {Claude session ID or {USER}}

- {scheduled_for_KST} → {draft_id} — room={room} — source={library digest URL or signal}
- ...
- Notes: {anything noticed during polish}
```

This becomes the audit trail of how raw library signals turn into posts. Combined with `audit_log.md`, it proves the cadence is real.

## Cadence guidance

- **Minimum**: 1 polish session every 24-36 hours = 2-3 posts/day
- **Healthy**: 1 polish session every morning (~10 min) + 1 evening (~20 min)
- **Burst**: Day-mass polishing (5-7 posts at once) is allowed if 절기 is right (e.g., 하지 = peak velocity, ok). NOT in 입하.

In 입하 specifically: polish slowly. 2-3 posts per session is plenty. The library will keep gathering; the queue doesn't have to keep up.

## What NOT to do during polish

- Don't polish **every** signal in the digest. Most signals are not for us.
- Don't polish a signal **just because it's viral**. The constitution forbids viral chasing in 입하.
- Don't use 3+ Korean concepts in one polished post (lecture mode).
- Don't auto-summarize an article and call it polish. The Korean lens IS the work.
- Don't schedule >4 posts in one day from a single polish session — too much loud signal. Trust the cadence.

## When you're stuck

If you can't find 2 signals you have a take on:

- Read `library/INDEX.md` for room counts — maybe a different room has fresher material
- Read yesterday's `feed/{date}.md` — older signals sometimes ripen
- Read 3 recent verified-actor posts on x.com/{handle} from `visitors/`
- Skip the session. The constitution says: don't post if nothing is true.

The library will still be gathering when you come back.
