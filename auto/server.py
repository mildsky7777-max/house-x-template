"""
Flask local app for draft queue approval.

Mobile-friendly. Open http://localhost:5050 (or LAN IP:5050) on phone.

Endpoints:
    GET  /              -> queue.html
    GET  /api/drafts    -> list pending/approved/published drafts (JSON)
    POST /api/draft     -> add new draft (called by Claude in CLI)
    POST /api/approve/<id>  -> mark approved + publish
    POST /api/reject/<id>   -> mark rejected
    POST /api/edit/<id>     -> update text/target
    POST /api/republish/<id> -> retry failed publish
"""
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import publish

ROOT = Path(__file__).parent
DRAFTS_FILE = ROOT / "drafts.json"
LOCK = threading.Lock()

app = Flask(__name__)


def _load() -> dict:
    if not DRAFTS_FILE.exists():
        return {"version": 1, "drafts": []}
    with DRAFTS_FILE.open() as f:
        return json.load(f)


def _save(data: dict):
    with DRAFTS_FILE.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find(drafts: list, draft_id: str) -> tuple[int, dict] | None:
    for i, d in enumerate(drafts):
        if d["id"] == draft_id:
            return i, d
    return None


@app.route("/")
def index():
    return render_template("queue.html")


@app.route("/api/drafts")
def list_drafts():
    data = _load()
    # Sort: pending first, then approved/published/rejected; newest first within each
    order = {"pending": 0, "approved": 1, "publishing": 2, "published": 3, "failed": 4, "rejected": 5}
    drafts = sorted(
        data["drafts"],
        key=lambda d: (order.get(d.get("status", "pending"), 99), d.get("created_at", "")),
    )
    return jsonify({"drafts": drafts})


@app.route("/api/draft", methods=["POST"])
def add_draft():
    payload = request.get_json(force=True)
    required = ["type", "text"]
    for k in required:
        if k not in payload:
            return jsonify({"error": f"missing {k}"}), 400

    if payload["type"] in ("reply", "quote") and not payload.get("target_url"):
        return jsonify({"error": "reply/quote requires target_url"}), 400

    new_draft = {
        "id": str(uuid.uuid4())[:8],
        "type": payload["type"],
        "text": payload["text"],
        "target_url": payload.get("target_url"),
        "media_path": payload.get("media_path"),
        "tags": payload.get("tags", []),
        "notes": payload.get("notes", ""),
        "status": "pending",
        "created_at": _now(),
        "published_at": None,
        "error": None,
    }

    with LOCK:
        data = _load()
        data["drafts"].append(new_draft)
        _save(data)

    return jsonify({"ok": True, "draft": new_draft})


@app.route("/api/approve/<draft_id>", methods=["POST"])
def approve(draft_id):
    with LOCK:
        data = _load()
        found = _find(data["drafts"], draft_id)
        if not found:
            return jsonify({"error": "not found"}), 404
        idx, draft = found
        draft["status"] = "publishing"
        draft["error"] = None
        _save(data)

    # Publish synchronously (Playwright blocks for ~10-15s)
    try:
        result = publish.sync_publish(draft)
    except Exception as e:
        result = {"ok": False, "url": None, "error": str(e)}

    with LOCK:
        data = _load()
        idx, draft = _find(data["drafts"], draft_id)
        if result["ok"]:
            draft["status"] = "published"
            draft["published_at"] = _now()
            draft["url"] = result.get("url")
        else:
            draft["status"] = "failed"
            draft["error"] = result.get("error")
        _save(data)

    return jsonify({"ok": result["ok"], "draft": draft, "result": result})


@app.route("/api/reject/<draft_id>", methods=["POST"])
def reject(draft_id):
    with LOCK:
        data = _load()
        found = _find(data["drafts"], draft_id)
        if not found:
            return jsonify({"error": "not found"}), 404
        _, draft = found
        draft["status"] = "rejected"
        _save(data)
    return jsonify({"ok": True, "draft": draft})


@app.route("/api/edit/<draft_id>", methods=["POST"])
def edit(draft_id):
    payload = request.get_json(force=True)
    with LOCK:
        data = _load()
        found = _find(data["drafts"], draft_id)
        if not found:
            return jsonify({"error": "not found"}), 404
        _, draft = found
        for k in ("text", "target_url", "media_path", "type", "notes"):
            if k in payload:
                draft[k] = payload[k]
        _save(data)
    return jsonify({"ok": True, "draft": draft})


@app.route("/api/republish/<draft_id>", methods=["POST"])
def republish(draft_id):
    """Retry a failed publish."""
    with LOCK:
        data = _load()
        found = _find(data["drafts"], draft_id)
        if not found:
            return jsonify({"error": "not found"}), 404
        _, draft = found
        if draft["status"] not in ("failed", "rejected"):
            return jsonify({"error": "can only republish failed/rejected"}), 400
        draft["status"] = "pending"
        _save(data)
    return jsonify({"ok": True, "draft": draft})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"\n  Draft queue running on http://localhost:{port}")
    print(f"  Mobile (LAN): http://<your-mac-ip>:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
