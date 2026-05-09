# House Stack — X automation template

> Korean indie automation stack for X (Twitter). Battle-tested daily.
> Originally built by [@YOUR_HANDLE template] going for 100K+ followers from YOUR_LOCATION.
> Open-sourced as a starting point for any indie running daily content + tools.

## What this is

A complete X automation house — not just a posting bot.

- **8 reviewer council** — substance, brand, hook, risk, cadence, receipts, hook auditor, authenticity (catches AI-tells before publishing)
- **Auto-publish** with Playwright (no API tier needed, free)
- **Quality gate** that catches translation-체, AI-tells, banned phrases, parallel-symmetric "It's not X, it's Y"
- **Auto-engager** that does verified-account replies (rate-limited)
- **Evolution scanner** that captures learn-from material from your orbit hourly
- **Trend scanner** + **likes scraper** + **notification tracker**
- **Scheduled tasks** for morning/afternoon/evening polish + tech research + weekly retro

## Quickstart

```bash
git clone <this-repo> ~/your-x
cd ~/your-x
python3 -m venv auto/.venv
source auto/.venv/bin/activate
pip install playwright
playwright install chromium
```

1. Edit `house/constitution.md` — your identity, voice, rooms, north star
2. Edit `auto/CLAUDE_TEMPLATE.md` → your `CLAUDE.md` — your handle, language, refusals
3. Run `auto/login_setup.py` once to log in to X (creates `.chrome-profile/`)
4. Drop a draft into `auto/drafts.json` (see schema)
5. Run `auto/scheduler.py` — 30s polling, fires scheduled drafts via Playwright

## Read first

- `ONBOARDING.md` — full setup walkthrough (Pro plan light version included)
- `house/constitution.md` — the brand rules
- `house/MANDATES.md` — root rules every scheduled task reads first
- `house/voice/observed_patterns.md` — voice modes (viral light, reflective, etc.)
- `house/reviewers/8_authenticity_auditor.md` — the AI-tell catcher

## License

MIT. Take it, fork it, make it yours. Replace `{USER}` / `YOUR_HANDLE` / `YOUR_LOCATION` with yours.

## Built with

Python · Playwright · Cron · Claude Code

