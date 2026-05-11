# Contributing

> Korean indie automation stack. Battle-tested daily. Open to forks + PRs.

## Quick start for contributors

1. Fork on GitHub
2. Clone your fork locally
3. Replace placeholders: `YOUR_HANDLE`, `YOUR_LOCATION`, `{USER}` with yours
4. Test the Quickstart in `README.md` end-to-end
5. Run the full daily cycle on your account for at least 7 days

If you build something useful on top:
- File an Issue with the pattern + result
- Open a PR with the improvement
- Or just fork it and run it — that's also fine

## What we want

- New voice modes (reference accounts in different niches)
- Better quality_gate patterns (regex for AI-tells in other languages)
- Additional scanner workers (Threads, Bluesky, Mastodon)
- AutoResearch loop improvements (better hypothesis tracking)
- Bug fixes from real daily use

## What we don't want

- Engagement bot mechanics (no auto-like spam, no follow-back farms)
- "Make Claude post AI thoughts" — this is AI-as-gate, not AI-as-generation
- Generic LinkedIn-style thread machines
- Removed safety rails (quality_gate is the brand defense)

## Daily use feedback

If you run it for 7+ days, share what you noticed:
- Which capture sources gave you best material
- Which voice mode hit hardest in your niche
- Which mandate fired most often in your case

Issues + replies welcome.

## Code style

- Python: keep workers single-file when possible
- No dependencies beyond playwright + flask
- Cron entries documented in worker docstring header
- All logs JSON for easy parsing

## License

MIT. Your fork is yours. Replace what you need.
