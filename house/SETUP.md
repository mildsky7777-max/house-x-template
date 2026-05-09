# Setup — Typefully integration (one-time, ~10 minutes)

## Why Typefully

`@09pauai`'s recipe (4.17M impressions on a single post, 90 days $700+) uses Typefully as the orchestration layer:

```
Claude Code → drafts → Typefully (API) → X + Threads (scheduled, multi-account)
```

We add it to our existing Playwright stack as a hybrid:
- **Typefully** = scheduled long-forms, threads, X+Threads simultaneous publish
- **Playwright** = real-time replies, likes, follows, engagement (existing)

## Steps

### 1. Sign up at Typefully

Visit https://typefully.com.

Free plan = 4 drafts max (enough to test). Paid = $14/mo for unlimited.

Affiliate options:
- ばうう (the user we learned from): `typefully.com/?via=pauu`
- Or sign up directly without referral

### 2. Connect X account

Settings → Connected accounts → X → Authorize.

### 3. (Optional) Connect Threads account

Settings → Connected accounts → Threads → Authorize.

This doubles audience for the same post. We don't have a Threads account yet — create one first at threads.net.

### 4. Generate API key

Settings → Integrations → API → Generate.

Copy the key. It looks like `tfly_...`.

### 5. Save the key locally

```bash
echo "YOUR_KEY_HERE" > ~/x/grow/house/.typefully_key
chmod 600 ~/x/grow/house/.typefully_key
```

### 6. Test

```bash
cd ~/x/grow/house/workers
python publish_typefully.py post --text "Korean builder, Day 7. Testing Typefully integration." --schedule "2026-05-06T09:00:00+09:00"
```

If you get a JSON response with an `id` field, you're connected.

### 7. (Eventually) Add to Flask queue

When ready, integrate `publish_typefully` into `~/x/grow/auto/server.py` so the queue UI can pick between Playwright and Typefully per draft.

## What changes once connected

- Long-form drafts that we used to fight ProseMirror for can be scheduled cleanly via Typefully
- Multi-paragraph + threads = native (no workarounds)
- Threads + X simultaneous = audience x2
- Analytics in Typefully UI for what worked

## What stays the same

- Replies, likes, follows, real-time → Playwright (Typefully doesn't do these well)
- The constitution, voice, signature moves
- Quality gate before any publish
