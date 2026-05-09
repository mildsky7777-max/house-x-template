"""
Typefully integration — schedule posts via Typefully Public API v2.

v2 API key facts (verified 2026-05-05 Day 7 16:00 KST after Discord support response):
  - Base: https://api.typefully.com   (NOT /v1 — that's deprecated)
  - Auth: Authorization: Bearer YOUR_API_KEY
  - Endpoint pattern: /v2/social-sets/{social_set_id}/drafts
  - Multi-platform native: each platform under `platforms.{x|threads|linkedin|...}`

Setup (one-time, manual):
  1. Sign up + Pro: https://typefully.com
  2. Connect X (and optionally Threads, LinkedIn) inside Typefully UI
  3. Generate API key: typefully.com/settings/integrations
  4. Save API key to ~/x/grow/house/.typefully_key (one line, no quotes)
  5. (auto) On first run, this module fetches social_set_id and caches to .typefully_set_id

Usage:
    python publish_typefully.py status               # health check + list drafts
    python publish_typefully.py post --text "..."    # immediate draft
    python publish_typefully.py post --text "..." --schedule 2026-05-06T00:00:00+00:00
    python publish_typefully.py post --text "..." --threadify
    python publish_typefully.py thread --text "tweet1\\n---\\ntweet2"
    python publish_typefully.py from-draft --id ID   # publish a drafts.json entry
"""
import argparse
import json
import os
import ssl
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]              # ~/x/grow/house
KEY_FILE = ROOT / ".typefully_key"
SET_ID_FILE = ROOT / ".typefully_set_id"
LOG_FILE = ROOT / "typefully_log.json"
DRAFTS_FILE = ROOT.parent / "auto" / "drafts.json"

API_BASE = "https://api.typefully.com"

_SSL_CTX = ssl.create_default_context()
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE


def get_api_key() -> str:
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip()
    env = os.environ.get("TYPEFULLY_API_KEY")
    if env:
        return env
    raise RuntimeError(f"No API key. Save to {KEY_FILE} or set TYPEFULLY_API_KEY.")


def _request(method: str, path: str, body: dict | None = None) -> dict | None:
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30, context=_SSL_CTX) as resp:
            if resp.status == 204:
                return None  # No content (e.g., DELETE success)
            return json.load(resp)
    except HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        return {"error": str(e), "status": e.code, "body": body_text}


def list_social_sets() -> dict:
    return _request("GET", "/v2/social-sets") or {}


def get_social_set_id() -> int:
    """Return cached social_set_id, fetching once on first call."""
    if SET_ID_FILE.exists():
        try:
            return int(SET_ID_FILE.read_text().strip())
        except ValueError:
            pass
    sets = list_social_sets()
    if "error" in sets:
        raise RuntimeError(f"Could not list social sets: {sets}")
    results = sets.get("results", [])
    if not results:
        raise RuntimeError("No social sets found. Connect X in Typefully UI.")
    set_id = results[0]["id"]
    SET_ID_FILE.write_text(str(set_id))
    print(f"  (cached social_set_id={set_id} → {SET_ID_FILE})")
    return set_id


def create_draft(text: str, schedule_iso: str | None = None,
                 threadify: bool = False, posts: list[str] | None = None,
                 platforms: list[str] | None = None) -> dict:
    """
    Create a draft on Typefully.

    text       — single post text (used if `posts` not provided)
    posts      — list of post texts for a thread (overrides text)
    schedule_iso — ISO datetime with timezone, e.g. 2026-05-06T00:00:00+00:00
    threadify  — single text auto-split by Typefully (separator: 4 newlines)
    platforms  — list of platform keys, default ["x"]. Available: x, threads, linkedin, mastodon, bluesky.
    """
    set_id = get_social_set_id()
    plats = platforms or ["x"]

    if posts is None:
        posts = [text]

    platform_block = {}
    for p in ["x", "threads", "linkedin", "mastodon", "bluesky"]:
        if p in plats:
            platform_block[p] = {
                "enabled": True,
                "posts": [{"text": t} for t in posts],
            }
        else:
            platform_block[p] = {"enabled": False}

    body: dict = {"platforms": platform_block}
    if schedule_iso:
        body["scheduled_date"] = schedule_iso
    # NOTE: threadify behavior in v2 is implicit — multi-element posts array IS the thread.
    # threadify (auto-split by Typefully) is not exposed in the v2 schema we've seen;
    # split client-side for now.

    return _request("POST", f"/v2/social-sets/{set_id}/drafts", body) or {}


def list_drafts(status: str | None = None) -> dict:
    """List drafts. status: 'draft' | 'scheduled' | 'published' | None (all)."""
    set_id = get_social_set_id()
    path = f"/v2/social-sets/{set_id}/drafts"
    if status:
        path += f"?status={status}"
    return _request("GET", path) or {}


def delete_draft(draft_id: int) -> bool:
    set_id = get_social_set_id()
    r = _request("DELETE", f"/v2/social-sets/{set_id}/drafts/{draft_id}")
    return r is None  # 204 No Content = success


def _log(entry: dict):
    log = {"entries": []}
    if LOG_FILE.exists():
        try:
            log = json.load(LOG_FILE.open())
        except Exception:
            pass
    log["entries"].append({**entry, "at": datetime.now(timezone.utc).isoformat()})
    log["entries"] = log["entries"][-200:]
    LOG_FILE.open("w").write(json.dumps(log, indent=2, ensure_ascii=False))


def cmd_status():
    print("=== Health ===")
    sets = list_social_sets()
    if "error" in sets:
        print(f"✗ {sets}")
        sys.exit(1)
    for s in sets.get("results", []):
        print(f"  ✓ social_set_id={s['id']} username=@{s['username']} ({s['name']})")

    print("\n=== Recent scheduled drafts ===")
    sched = list_drafts(status="scheduled")
    for d in sched.get("results", [])[:10]:
        print(f"  {d['id']}  @ {d.get('scheduled_date','-')}  preview={d.get('preview','')[:60]}")

    print("\n=== Recent published ===")
    pub = list_drafts(status="published")
    for d in pub.get("results", [])[:5]:
        print(f"  {d['id']}  @ {d.get('published_at','-')}  preview={d.get('preview','')[:60]}")


def cmd_post(args):
    posts = None
    text = args.text
    if args.thread_separator and "---" in text:
        # Split thread
        posts = [p.strip() for p in text.split("\n---\n") if p.strip()]
        text = posts[0]
    r = create_draft(text, schedule_iso=args.schedule,
                     threadify=args.threadify, posts=posts,
                     platforms=(args.platforms.split(",") if args.platforms else None))
    print(json.dumps(r, indent=2, ensure_ascii=False))
    _log({
        "action": "create_draft",
        "text_preview": text[:80],
        "schedule_iso": args.schedule,
        "result_id": r.get("id"),
        "status": r.get("status") or r.get("error"),
    })


def cmd_thread(args):
    parts = [p.strip() for p in args.text.split("\n---\n") if p.strip()]
    r = create_draft(parts[0], schedule_iso=args.schedule, posts=parts,
                     platforms=(args.platforms.split(",") if args.platforms else None))
    print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_from_draft(args):
    """Pull a draft from drafts.json by id and push to Typefully."""
    data = json.load(DRAFTS_FILE.open())
    target = next((d for d in data["drafts"] if d["id"] == args.id), None)
    if not target:
        print(f"draft {args.id} not in drafts.json")
        sys.exit(1)
    text = target["text"]
    schedule = target.get("scheduled_at") or args.schedule
    posts = None
    if target.get("type") == "thread" or "---" in text and "\n---\n" in text:
        posts = [p.strip() for p in text.split("\n---\n") if p.strip()]
        if len(posts) <= 1:
            posts = None
    r = create_draft(text, schedule_iso=schedule, posts=posts,
                     platforms=(args.platforms.split(",") if args.platforms else None))
    print(json.dumps(r, indent=2, ensure_ascii=False))
    if "id" in r:
        # Update local draft with typefully id for tracking
        for d in data["drafts"]:
            if d["id"] == args.id:
                d["typefully_id"] = r["id"]
                d["typefully_pushed_at"] = datetime.now(timezone.utc).isoformat()
        DRAFTS_FILE.open("w").write(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"  ✓ recorded typefully_id={r['id']} on local draft {args.id}")
    _log({
        "action": "from_draft",
        "local_id": args.id,
        "typefully_id": r.get("id"),
        "status": r.get("status") or r.get("error"),
    })


def cmd_delete(args):
    ok = delete_draft(int(args.id))
    print("✓ deleted" if ok else "✗ failed")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("status")

    pp = sub.add_parser("post")
    pp.add_argument("--text", required=True)
    pp.add_argument("--schedule", help="ISO datetime with TZ")
    pp.add_argument("--threadify", action="store_true", help="(no-op in v2; client splits)")
    pp.add_argument("--thread-separator", action="store_true",
                    help="treat \\n---\\n as thread separator")
    pp.add_argument("--platforms", help="comma list, default 'x'. e.g. 'x,threads'")

    pt = sub.add_parser("thread")
    pt.add_argument("--text", required=True, help="separator: \\n---\\n")
    pt.add_argument("--schedule")
    pt.add_argument("--platforms")

    pf = sub.add_parser("from-draft", help="push a drafts.json entry to Typefully")
    pf.add_argument("--id", required=True)
    pf.add_argument("--schedule", help="override scheduled_at")
    pf.add_argument("--platforms")

    pd = sub.add_parser("delete")
    pd.add_argument("--id", required=True)

    args = p.parse_args()
    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "post":
        cmd_post(args)
    elif args.cmd == "thread":
        cmd_thread(args)
    elif args.cmd == "from-draft":
        cmd_from_draft(args)
    elif args.cmd == "delete":
        cmd_delete(args)
    else:
        p.print_help()
