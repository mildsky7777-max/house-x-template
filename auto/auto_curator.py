"""
Auto curator — find popular posts in our niche, generate quote-tweet drafts
with our take + Korean cultural angle, queue as pending.

Pipeline:
  1. Run trend_scanner (or read existing targets.json)
  2. For each high-quality target, detect topic keywords
  3. Match Korean concept (가성비, 빨리빨리, 의리, 깐깐함, 복기, 한솥밥...)
  4. Generate quote text from template
  5. Queue as type="quote" with target_url
  6. User reviews + approves in queue UI

Output: drafts go into queue with status=pending. Manual approval required.
(Quote tweets reach a separate audience than replies, lower spam risk.)

Usage:
    python auto_curator.py            # one-shot: read targets.json, queue 3-5
    python auto_curator.py --scan     # also re-run trend_scanner first
    python auto_curator.py --max 5
"""
import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
TARGETS_FILE = ROOT / "targets.json"
CURATED_LOG = ROOT / "curated.json"
BASE_URL = "http://localhost:5050"


# Keyword → (concept name, template fragment)
# Order matters — first match wins.
CONCEPTS = [
    {
        "name": "가성비",
        "keywords": ["price", "cost", "cheap", "tokens", "$", "subscription", "rate limit", "deepseek"],
        "lead": "가성비 (price-to-performance) is the lens we use for everything in Korea.",
    },
    {
        "name": "빨리빨리",
        "keywords": ["fast", "speed", "ship", "race", "shipped", "rapid", "velocity", "next thing"],
        "lead": "빨리빨리 (fast fast) — the Korean cadence meets the AI ship cycle.",
    },
    {
        "name": "한솥밥",
        "keywords": ["memory", "context", "remember", "session", "persistent", "long-running", "team", "cofounder"],
        "lead": "한솥밥 (rice from one pot) — relationships that survive the long sessions.",
    },
    {
        "name": "깐깐함",
        "keywords": ["review", "quality", "meticulous", "careful", "rigor", "audit", "spec", "standards"],
        "lead": "깐깐함 (meticulous to the point of friction) is the Korean bar.",
    },
    {
        "name": "복기",
        "keywords": ["mistake", "failure", "retro", "post-mortem", "debug", "what went wrong", "wrong move"],
        "lead": "복기 (Go-style replay): not 'why did it fail' — 'when did I stop being right'.",
    },
    {
        "name": "의리",
        "keywords": ["loyalty", "stay", "switch", "tool of the week", "stack", "muscle memory"],
        "lead": "의리 (loyalty) — staying long enough to learn the deep moves.",
    },
    {
        "name": "눈치",
        "keywords": ["read the room", "context", "understand", "intent", "infer"],
        "lead": "눈치 (the skill of reading what's in the room before anyone speaks).",
    },
    {
        "name": "default",
        "keywords": [],
        "lead": None,
    },
]


def match_concept(text: str) -> dict:
    lower = text.lower()
    for c in CONCEPTS:
        if not c["keywords"]:
            continue
        if any(kw in lower for kw in c["keywords"]):
            return c
    return CONCEPTS[-1]  # default


def build_quote_text(target: dict, day_num: int = 7) -> tuple[str, str]:
    """Returns (text, concept_name)."""
    concept = match_concept(target.get("text", ""))
    handle = target["handle"]
    if concept["name"] == "default":
        # No clear concept — generic builder framing
        text = (
            f"Korean builder reading this from YOUR_LOCATION.\n\n"
            f"[INSERT YOUR TAKE — what does this mean for builders?]\n\n"
            f"Korean builder, Day {day_num}."
        )
    else:
        text = (
            f"Korean builder reading this from YOUR_LOCATION.\n\n"
            f"{concept['lead']}\n\n"
            f"[INSERT YOUR TAKE — connect {concept['name']} to the original tweet]\n\n"
            f"Korean builder, Day {day_num}."
        )
    return text, concept["name"]


def queue_draft(payload: dict) -> dict:
    body = json.dumps(payload).encode()
    req = Request(f"{BASE_URL}/api/draft", data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=10) as r:
        return json.load(r)


def load_curated_log() -> dict:
    if not CURATED_LOG.exists():
        return {"drafted_urls": []}
    with CURATED_LOG.open() as f:
        return json.load(f)


def save_curated_log(d: dict):
    with CURATED_LOG.open("w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def curate(max_n: int = 5):
    if not TARGETS_FILE.exists():
        print("No targets.json. Run: python trend_scanner.py")
        return
    with TARGETS_FILE.open() as f:
        tj = json.load(f)
    targets = tj.get("targets", [])
    if not targets:
        print("targets.json has no candidates.")
        return

    log = load_curated_log()
    already = set(log["drafted_urls"])
    queued = 0
    for t in targets:
        if queued >= max_n:
            break
        url = t.get("tweet_url")
        if not url or url in already:
            continue
        if not t.get("verified"):
            continue
        # Score >= 0.5 only
        if t.get("score", 0) < 0.5:
            continue

        text, concept = build_quote_text(t)
        payload = {
            "type": "quote",
            "target_url": url,
            "text": text,
            "tags": ["quote-curated", "auto-curator", concept],
            "notes": (
                f"Auto-curated. Original by @{t['handle']} ({t['views']:,}v / {t['replies']}r). "
                f"Topic: '{t['text'][:120]}'. Concept: {concept}. "
                f"REPLACE [INSERT YOUR TAKE] before approving."
            ),
        }
        try:
            r = queue_draft(payload)
            print(f"  [{queued+1}] queued ({concept:8s}) @{t['handle']} → {r['draft']['id']}")
            log["drafted_urls"].append(url)
            queued += 1
        except Exception as e:
            print(f"  ! failed @{t['handle']}: {e}")

    save_curated_log(log)
    print(f"\n  ✓ Queued {queued} curated quote drafts (status=pending, awaiting your insight + approval).")
    print(f"  Open http://localhost:5050 to review.")


async def run_scan():
    """Re-run trend_scanner before curating."""
    from trend_scanner import scan
    await scan(verbose=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true", help="Re-run trend_scanner first")
    parser.add_argument("--max", type=int, default=5)
    args = parser.parse_args()

    if args.scan:
        asyncio.run(run_scan())
    curate(max_n=args.max)
