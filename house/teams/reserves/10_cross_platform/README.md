# Cross-Platform Team — RESERVE (activate Day 30+)

## Activation triggers

- Day 30+ stable cadence on X (proven we can ship consistently)
- Library shows 5+ posts/week we'd want on multiple platforms
- {USER} wants Threads / LinkedIn / Bluesky surface

## When activated

1. Enable Typefully API multi-platform fields (already supported in `publish_typefully.py` — flip `platforms=["x", "threads"]`)
2. Translate / adapt voice per platform:
   - X: current voice (English bio, mixed posts)
   - Threads: similar to X but slightly softer (Threads audience reads slower)
   - LinkedIn: more concrete receipts, less poetry
   - Bluesky: indie tech reader; same voice as X works
3. Set platform-specific posting cadence (X may stay daily; Threads 3x/week)
4. Track per-platform metrics in audit_log
5. Update Strategy Team weekly retro to include platform comparison

## Why wait until Day 30+

Voice still settling on X. Adding platforms now = scattered identity. Better to nail one place first.

## Currently using

- Typefully API v2 (X-only currently; multi-platform infra ready)
- Day 7 noted: "Threads in Korean creator economy big — Typefully풀리면 X 발행마다 Threads에도 자동 복사"
