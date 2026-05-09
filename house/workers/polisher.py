"""
Polisher worker — Claude API turns scaffolds into draft candidates.

Reads `drafts.json` for `status="scaffold"` entries. For each one:

  1. Builds a tight prompt anchored in:
     - constitution.md voice rules + banned phrases (truncated)
     - almanac/CURRENT.md (this 절기, this room)
     - rooms/{room}.md canonical receipt (the keystone)
     - the scaffold's source (article link, almanac context, etc.)
  2. Calls Claude (Sonnet) for ONE draft candidate
  3. Runs quality_gate.py on the result
  4. If passed → store as `ai_polished_text` and flip status to `ai-polished`
     (NOT `pending` — human eye still required before publish)
  5. If failed → leave scaffold alone, log the gate failures

Runs daily at 12:00 KST via cron, after article_curator (11:00) and almanac (06:00).
Never auto-publishes. Quality gate + human review before pending.

Design rules:
- Cost cap: max 5 polishes per run (≈ $0.10/day Sonnet)
- One model call per scaffold (no chain-of-thought, no retries on quality fails)
- Original scaffold text preserved in `original_scaffold_text` field

Usage:
    python polisher.py            # polish up to 5 scaffolds
    python polisher.py --max 1    # polish 1 (testing)
    python polisher.py --id ID    # polish a specific scaffold
    python polisher.py --dry-run  # show what would be polished, no API calls
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import ssl
from urllib.request import Request, urlopen
from urllib.error import HTTPError

_SSL_CTX = ssl.create_default_context()
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE

# Project paths
HOUSE = Path(__file__).resolve().parents[1]            # ~/x/grow/house
ROOT = HOUSE.parent                                     # ~/x/grow
DRAFTS_FILE = ROOT / "auto" / "drafts.json"
CONSTITUTION = HOUSE / "constitution.md"
BANNED = HOUSE / "voice" / "banned.md"
SIGNATURES = HOUSE / "voice" / "signatures.md"
CURRENT_ALMANAC = HOUSE / "almanac" / "CURRENT.md"
ROOMS_DIR = HOUSE / "rooms"
LOG_FILE = HOUSE / "polisher_log.json"

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-5"  # adjust if needed
MAX_TOKENS = 1200
DEFAULT_MAX_PER_RUN = 5

# Add quality_gate sibling dir to path for import
sys.path.insert(0, str(HOUSE / "workers"))
from quality_gate import check_draft  # noqa: E402


def get_api_key() -> str:
    # Priority: env var, then ~/x/grow/.anthropic_key, then ~/.anthropic_key
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    for p in (ROOT / ".anthropic_key", Path.home() / ".anthropic_key"):
        if p.exists():
            return p.read_text().strip()
    raise RuntimeError(
        "ANTHROPIC_API_KEY not found. Set env var OR save to ~/x/grow/.anthropic_key (one line, no quotes)."
    )


def read_text_safely(p: Path, max_chars: int = 8000) -> str:
    if not p.exists():
        return ""
    s = p.read_text()
    if len(s) > max_chars:
        s = s[:max_chars] + f"\n\n[...truncated, full file at {p.name}]"
    return s


def build_system_prompt(room_name: str | None) -> str:
    """The system prompt is the house — voice, banned phrases, current 절기, and (if present) the room's canonical receipt."""
    parts = []

    parts.append("# You are drafting one X post for @YOUR_HANDLE ({USER})\n")
    parts.append("Korean AI builder posting from YOUR_LOCATION Island. Faceless. Solo. The X account is the front yard of three YouTube channels (Vanished Mysteries, Heartfelt Stories, AI Weekly Briefing).\n")

    parts.append("\n## House voice rules (excerpt from constitution.md)\n")
    constitution = read_text_safely(CONSTITUTION, 6000)
    parts.append(constitution)

    parts.append("\n## Banned phrases (verbatim — never use)\n")
    parts.append(read_text_safely(BANNED, 3000))

    parts.append("\n## Today's 절기 (almanac/CURRENT.md)\n")
    parts.append(read_text_safely(CURRENT_ALMANAC, 1500))

    if room_name:
        room_file = ROOMS_DIR / f"{room_name}.md"
        if room_file.exists():
            parts.append(f"\n## The room of this post — {room_name}\n")
            parts.append("Use this room's voice. Study its CANONICAL RECEIPT — your draft should resemble that shape.\n\n")
            parts.append(read_text_safely(room_file, 2500))

    parts.append("\n## Output rules\n")
    parts.append(
        "- Output ONE post draft. No preamble, no commentary, no triple backticks.\n"
        "- 500-1500 chars. Visual rhythm: short lines, empty lines between, ⸻ as separator.\n"
        "- Korean concept used naturally, not as lecture.\n"
        "- End with a stamp like 'Korean builder, Day X.' or 'Day X from YOUR_LOCATION.' or 'Korean builder, Day X. Inside <절기>.'\n"
        "- One concept room MAX (sister rooms allowed in tension, never three).\n"
        "- No emojis at line starts. No 'Hot take:'. No AI tells (delve, tapestry, 'it's not just X — it's Y').\n"
        "- If the input is an article scaffold: keep the article URL on its own line near the end.\n"
        "- The receipt must be specific: a number, a code change, a small ship, a reader interaction.\n"
    )
    return "".join(parts)


def build_user_prompt(draft: dict) -> str:
    """The user prompt is the scaffold itself + any context fields."""
    lines = []
    if draft.get("almanac_jeolgi"):
        lines.append(f"Today's 절기: {draft['almanac_jeolgi']}")
    if draft.get("almanac_room"):
        lines.append(f"Room: {draft['almanac_room']}")
    if draft.get("almanac_audit_day"):
        lines.append(f"Audit Day: {draft['almanac_audit_day']} / 30")
    if draft.get("source_title"):
        lines.append(f"Source article title: {draft['source_title']}")
    if draft.get("source_link"):
        lines.append(f"Source article URL: {draft['source_link']}")
    lines.append("")
    lines.append("Scaffold (this is the placeholder you're replacing — KEEP its frame, REPLACE the bracketed placeholders with real specifics):")
    lines.append("")
    lines.append(draft.get("text", ""))
    lines.append("")
    lines.append("Write the polished post now. ONE post. No commentary. Output starts directly with the post text.")
    return "\n".join(lines)


def call_claude(system_prompt: str, user_prompt: str) -> str:
    body = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    key = get_api_key()
    headers = {
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    # OAuth tokens (sk-ant-oat...) use Authorization: Bearer
    # API keys (sk-ant-api...) use x-api-key
    if key.startswith("sk-ant-oat"):
        headers["authorization"] = f"Bearer {key}"
        headers["anthropic-beta"] = "oauth-2025-04-20"
    else:
        headers["x-api-key"] = key
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    url = f"{base}/v1/messages"
    req = Request(url, data=json.dumps(body).encode(),
                  headers=headers, method="POST")
    try:
        with urlopen(req, timeout=120, context=_SSL_CTX) as r:
            payload = json.load(r)
    except HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Claude API HTTP {e.code}: {body_text}")
    # Extract text from content blocks
    content = payload.get("content", [])
    if not content:
        raise RuntimeError(f"Empty content in API response: {payload}")
    text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
    return "\n".join(text_parts).strip()


def polish_draft(draft: dict, dry_run: bool = False) -> dict:
    """Return a polish-result dict: {polished_text, gate_result, error}."""
    system_prompt = build_system_prompt(draft.get("almanac_room"))
    user_prompt = build_user_prompt(draft)

    if dry_run:
        return {"dry_run": True, "system_prompt_chars": len(system_prompt),
                "user_prompt_chars": len(user_prompt)}

    try:
        polished = call_claude(system_prompt, user_prompt)
    except Exception as e:
        return {"error": str(e)}

    # Strip code fences if Claude added them despite instruction
    if polished.startswith("```"):
        polished = polished.strip("`").strip()
        if polished.startswith("\n"):
            polished = polished[1:]

    gate = check_draft({"text": polished})
    return {"polished_text": polished, "gate": gate}


def load_drafts() -> dict:
    return json.load(DRAFTS_FILE.open())


def save_drafts(data: dict):
    DRAFTS_FILE.open("w").write(
        json.dumps(data, indent=2, ensure_ascii=False))


def select_scaffolds(data: dict, max_age_hours: int | None,
                     specific_id: str | None, max_n: int) -> list[dict]:
    out = []
    now = datetime.now(timezone.utc)
    for d in data["drafts"]:
        if d.get("status") != "scaffold":
            continue
        if specific_id and d.get("id") != specific_id:
            continue
        if max_age_hours is not None:
            try:
                created = datetime.fromisoformat(d["created_at"])
                if (now - created) < timedelta(hours=max_age_hours):
                    continue
            except Exception:
                pass
        out.append(d)
        if len(out) >= max_n:
            break
    return out


def log_run(entries: list[dict]):
    log = {"runs": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    })
    log["runs"] = log["runs"][-50:]
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=DEFAULT_MAX_PER_RUN)
    p.add_argument("--id", help="polish a specific scaffold draft by id")
    p.add_argument("--min-age-hours", type=int, default=None,
                   help="only polish scaffolds older than N hours (default: any age)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    data = load_drafts()
    scaffolds = select_scaffolds(data, args.min_age_hours, args.id, args.max)
    if not scaffolds:
        print("No scaffolds match criteria.")
        return

    print(f"Polishing {len(scaffolds)} scaffold(s):")
    log_entries = []

    for s in scaffolds:
        print(f"\n  → {s['id']}  (room={s.get('almanac_room','-')}, age={s.get('created_at')})")
        result = polish_draft(s, dry_run=args.dry_run)

        if args.dry_run:
            print(f"    dry-run: system_prompt {result['system_prompt_chars']} chars,"
                  f" user_prompt {result['user_prompt_chars']} chars")
            log_entries.append({"id": s["id"], "dry_run": True})
            continue

        if "error" in result:
            print(f"    ✗ ERROR: {result['error']}")
            log_entries.append({"id": s["id"], "error": result["error"]})
            continue

        gate = result["gate"]
        passed = gate["passed"]
        print(f"    polished ({len(result['polished_text'])} chars) — gate {'PASS' if passed else 'FAIL: ' + ','.join(gate['fails'])}")

        # Update draft in-place
        for i, d in enumerate(data["drafts"]):
            if d["id"] == s["id"]:
                d["original_scaffold_text"] = d["text"]
                d["text"] = result["polished_text"]
                d["ai_polished_at"] = datetime.now(timezone.utc).isoformat()
                d["ai_polished_gate"] = gate
                if passed:
                    d["status"] = "ai-polished"
                # If fails gate, status stays "scaffold" but we still record the attempt
                d["last_polish_attempt"] = result["polished_text"]
                data["drafts"][i] = d
                break

        log_entries.append({
            "id": s["id"],
            "gate_passed": passed,
            "gate_fails": gate["fails"],
            "polished_chars": len(result["polished_text"]),
        })

    if not args.dry_run:
        save_drafts(data)
        log_run(log_entries)
        print("\n  ✓ drafts.json updated, log written")


if __name__ == "__main__":
    main()
