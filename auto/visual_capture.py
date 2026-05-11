"""
Visual capture worker — Day 12 (이지 mandate "그럼 해").

Daily 06:50 KST: capture visuals for the day's posts to draw on.
Output: library/visuals/{date}/ — PNG files ready for media_path attach in drafts.json.

Captures rotated daily:
- cron log tail (terminal screenshot via headless Chromium rendering text)
- drafts.json beautified preview
- heartbeat status snapshot
- experiment_log latest entries
- one fresh evolution capture page

Polish task references this dir → picks 1-3 visuals → assigns to draft.media_path.

Cron: 50 6 * * *
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
HOUSE = ROOT.parent / "house"
VISUALS_DIR = HOUSE / "library" / "visuals"
KST = timezone(timedelta(hours=9))


def render_text_html(title: str, content: str, fg="#e6edf3", bg="#0d1117", accent="#2ea043") -> str:
    """Build a terminal-styled HTML page for screenshot."""
    safe = (
        content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>
  body {{ margin:0; padding:40px; background:{bg}; color:{fg};
         font: 14px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; }}
  .header {{ color:{accent}; margin-bottom:16px; font-size:18px; }}
  pre {{ white-space:pre-wrap; margin:0; }}
  .footer {{ margin-top:24px; color:#7d8590; font-size:11px; }}
</style></head>
<body>
  <div class='header'>● {title}</div>
  <pre>{safe}</pre>
  <div class='footer'>house stack · @YOUR_HANDLE</div>
</body></html>"""


async def capture_text_image(page, html: str, out_path: Path, w=1080, h=1080):
    await page.set_viewport_size({"width": w, "height": h})
    await page.set_content(html, wait_until="domcontentloaded")
    await page.wait_for_timeout(300)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(out_path), full_page=True)


def read_tail(path: Path, max_lines: int = 18) -> str:
    if not path.exists():
        return f"(empty: {path.name})"
    try:
        text = path.read_text()
        lines = [l for l in text.split("\n") if l.strip()]
        return "\n".join(lines[-max_lines:])
    except Exception as e:
        return f"(read error: {e})"


def heartbeat_snapshot() -> str:
    f = HOUSE / "heartbeat.json"
    if not f.exists():
        return "(no heartbeat.json)"
    try:
        d = json.load(f.open())
    except Exception as e:
        return f"(parse error: {e})"
    out = [f"checked: {d.get('checked_at','?')[:19]}"]
    for s in d.get("scanners", []):
        flag = "✓" if s["ok"] else "✗"
        out.append(f"  {flag} {s['name']:25s} age={s.get('age_hours','-')}h")
    mc = d.get("mandate_compliance", {})
    out.append(f"  ✓ mandate_compliance     {mc.get('pass_rate','-')} ({mc.get('passed','-')}/{mc.get('checked','-')})")
    return "\n".join(out)


def drafts_summary() -> str:
    f = ROOT / "drafts.json"
    if not f.exists():
        return "(no drafts.json)"
    try:
        d = json.load(f.open())
    except Exception as e:
        return f"(parse error: {e})"
    drafts = d.get("drafts", [])
    pending = [p for p in drafts if p.get("status") == "pending"]
    pub = [p for p in drafts if p.get("status") == "published"]
    today = datetime.now(KST).strftime("%Y-%m-%d")
    pub_today = [p for p in pub if (p.get("published_at") or "").startswith(today.replace("-","-")) or (p.get("published_at") or "").startswith(today)]
    out = [
        f"drafts: {len(drafts)} total",
        f"  pending  : {len(pending)}",
        f"  published: {len(pub)}",
        f"  today    : {len(pub_today)}",
        "",
        "next 3 pending:",
    ]
    pending_sorted = sorted(pending, key=lambda x: x.get("scheduled_at",""))[:3]
    for p in pending_sorted:
        out.append(f"  • {p['id']} {p.get('scheduled_at','-')[:16]} -- {p.get('text','')[:60]}")
    return "\n".join(out)


def experiment_top_3() -> str:
    f = HOUSE / "experiment_log.md"
    if not f.exists():
        return "(no experiment_log.md yet)"
    text = f.read_text()
    # Extract entries with score, sort top 3
    import re
    entries = re.findall(r"## ([a-f0-9]+) .+?score\*\*: (\d+\.?\d*)", text, re.DOTALL)
    if not entries:
        return text[:1500]
    entries.sort(key=lambda e: -float(e[1]))
    out = ["top 3 by engagement score:\n"]
    for eid, score in entries[:5]:
        out.append(f"  • {eid}  score={score}")
    return "\n".join(out)


async def main():
    today = datetime.now(KST).strftime("%Y-%m-%d")
    out_dir = VISUALS_DIR / today
    out_dir.mkdir(parents=True, exist_ok=True)

    captures = [
        ("heartbeat.png", "heartbeat", heartbeat_snapshot()),
        ("drafts.png", "drafts.json (today)", drafts_summary()),
        ("experiment_top.png", "experiment_log top scores", experiment_top_3()),
        ("evolution_tail.png", "evolution capture (latest)",
            read_tail(HOUSE / "library" / "evolution" / f"{today}.md", 16)),
        ("for_you_tail.png", "for_you capture (latest)",
            read_tail(HOUSE / "library" / "for_you" / f"{today}.md", 16)),
    ]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        for fname, title, content in captures:
            html = render_text_html(title, content)
            try:
                await capture_text_image(page, html, out_dir / fname)
                print(f"  ✓ {fname}")
            except Exception as e:
                print(f"  ! {fname}: {e}")
        await ctx.close()
        await browser.close()
    print(f"  → {out_dir}")


if __name__ == "__main__":
    asyncio.run(main())
