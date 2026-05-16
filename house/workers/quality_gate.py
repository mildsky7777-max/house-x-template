"""
Quality gate — checks every draft against the constitution before publishing.

Three failures = block. Two failures = warn. Zero failures = pass.

Checks:
  1. Banned phrases (voice/banned.md)
  2. Visual rhythm (no >3 line paragraphs without break)
  3. Stamp presence (each post needs a Korean-builder stamp at end OR a strong final line)
  4. Korean concept usage — illuminates, not decorates
  5. AI-tell phrasing
  6. The Year Test — would I be proud of this in a year?
     (heuristic: does the post have a real receipt OR a real concept?)
"""
import json
import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]  # ~/x/grow/house
BANNED_FILE = ROOT / "voice" / "banned.md"


class CheckResult(NamedTuple):
    name: str
    passed: bool
    note: str


def load_banned_phrases() -> list[str]:
    """Extract bullet-point phrases from voice/banned.md."""
    if not BANNED_FILE.exists():
        return []
    phrases = []
    for line in BANNED_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("- "):
            phrase = line[2:].strip()
            # strip surrounding quotes
            phrase = phrase.strip('"').strip("'")
            if phrase and len(phrase) > 2:
                phrases.append(phrase.lower())
    return phrases


# Stamps that close a post in our voice
STAMP_PATTERNS = [
    r"korean builder,?\s+(day\s*\d+|in public|taking notes)",
    r"day\s*\d+\s*from\s*jeju",
    r"day\s*\d+/\d+\b",
    r"korean\s+builder\s*\.",
]

# AI-tell phrasing — the X viral list (Day 9 evening {USER} surfacing)
AI_TELLS = [
    # verbs
    "delve into",
    "delve",
    "navigate the complexities",
    "harness the power",
    "harness",
    "unlock the power",
    "unlock the potential",
    "embark on a journey",
    "embark on",
    "let's dive in",
    "dive deep",
    "let's explore",
    # nouns / metaphors
    "tapestry",
    "rich tapestry",
    "in the realm of",
    "in the world of",
    "evolving landscape",
    "paradigm shift",
    "a testament to",
    "a wealth of",
    "plethora of",
    "myriad of",
    # sentence shapes
    "it's not just",
    "it's not about",
    "whether you're",
    "in today's fast-paced",
    "at the end of the day",
    "here's the thing",
    "the truth is",
    "buckle up",
    "spoiler:",
    "plot twist:",
    # connectors at sentence start
    "crucially,",
    "importantly,",
    "notably,",
    "ultimately,",
    "moreover,",
    "furthermore,",
    "in essence,",
    # adjectives
    "robust",
    "seamless",
    "cutting-edge",
    "transformative",
    "groundbreaking",
    # bro / hype
    "game changer",
    "10x",
    "insanely",
    "game over",
    "this will change everything",
    "mind = blown",
]

# Korean concepts we know
KNOWN_CONCEPTS = [
    "위기", "危機", "wi-gi",
    "가성비", "ga-seong-bi", "gaseongbi",
    "한솥밥", "han-sot-bap", "hansotbap",
    "깐깐함", "kkang-kkang", "kkangkkang",
    "빨리빨리", "ppalli ppalli", "ppalli-ppalli",
    "의리", "uy-ri", "uyri",
    "복기", "bok-gi", "bokgi",
    "눈치", "nun-chi", "nunchi",
    "정성", "jeong-seong",
    "시작이 반이다",
    "한솥밥",
]


def check_banned(text: str, banned: list[str]) -> CheckResult:
    lower = text.lower()
    hits = [p for p in banned if p in lower]
    if hits:
        return CheckResult("banned_phrases", False, f"hits: {hits[:3]}")
    return CheckResult("banned_phrases", True, "")


def check_ai_tells(text: str) -> CheckResult:
    lower = text.lower()
    hits = [t for t in AI_TELLS if t in lower]
    if hits:
        return CheckResult("ai_tells", False, f"hits: {hits[:3]}")
    return CheckResult("ai_tells", True, "")


# Korean 번역체 patterns (Day 9 evening study)
KOREAN_TRANSLATIONESE = [
    "에 의해",
    "을 가지고 있",
    "를 가지고 있",
    "에 대하여",
    "로 인해",
    "에 위치한",
    "이 존재한",
    "가 존재한",
    "에도 불구하고",
]

# Brand-banned consonant reactions (Day 9 evening {USER} critique)
KOREAN_BANNED_REACTIONS = ["ㅋㅋ", "ㅎㅎ", "ㄷㄷ", "ㅠㅠ", "ㅜㅜ", "ㅗㅗ"]


def check_korean_translationese(text: str) -> CheckResult:
    """Catch 영한 직역체 patterns in Korean posts."""
    # only check if text has Korean
    if not re.search(r"[가-힣]", text):
        return CheckResult("translationese", True, "no korean")
    hits = [p for p in KOREAN_TRANSLATIONESE if p in text]

    # Catch: same English word repeated with Korean 조사 (calque pattern)
    # e.g. "fire가 fire를", "signal이 signal을"
    calque_pattern = re.findall(
        r"\b([a-z]{3,})\s*[가이은는을를]\s+\1\b", text.lower()
    )
    if calque_pattern:
        hits.append(f"calque-doubling:{calque_pattern[0]}")

    # Catch: English metaphor noun + Korean verb suffix
    # (technical terms like reply/like/cron OK; metaphor nouns NO)
    metaphor_words = ["fire", "cheap", "surf", "signal", "polling", "stitch",
                      "bridge", "harbor", "anchor", "leverage"]
    for w in metaphor_words:
        # match like "fire가 fire를 부르" or "polling만 보고"
        if re.search(rf"\b{w}\s*[을를이가은는만도에]", text.lower()):
            hits.append(f"english-metaphor:{w}")
            break

    # Brand-level ban on consonant reactions
    for r in KOREAN_BANNED_REACTIONS:
        if r in text:
            hits.append(f"banned-reaction:{r}")
            break

    if hits:
        return CheckResult("translationese", False, f"hits: {hits[:3]}")
    return CheckResult("translationese", True, "")


def check_publish_safety(text: str) -> CheckResult:
    """
    Catch the patterns that broke Day 7 13:00 fire (a3afd92a).
    X compose dialog disables Post button when:
      - Excessive total lines (>30) trip multi-line ProseMirror state
      - Numbered lists (1. 2. 3.) at line starts may auto-format
      - Emoji at line start in many lines (✅✅✅) sometimes trips state
    Heuristic: any one of these is a warning; combination is a fail.
    """
    lines = text.split("\n")
    n = len(lines)
    flags = []
    if n > 30:
        flags.append(f"{n} lines (>30 risks compose timeout)")
    numbered = sum(1 for ln in lines if re.match(r"^\s*\d+\.\s", ln))
    if numbered >= 3:
        flags.append(f"{numbered} numbered list items")
    emoji_starts = sum(1 for ln in lines if re.match(r"^\s*[✅✓✗❌🚀🚨⚡📌🔥💡]", ln))
    if emoji_starts >= 4:
        flags.append(f"{emoji_starts} emoji-prefix lines")
    line_start_emoji = re.search(r"^[🚀🚨⚡🔥]", text)
    if line_start_emoji:
        flags.append("emoji prefix on first line (constitution forbids)")
    # Angle brackets — X compose disables Post button when interpreting as markdown
    # (Day 9 evening a596720f fire failure)
    if re.search(r"\s[<>]\s|^[<>]|[<>]\s", text):
        flags.append("angle bracket (< or >) — X compose may disable Post button")

    if not flags:
        return CheckResult("publish_safety", True, "")
    if len(flags) >= 2:
        return CheckResult("publish_safety", False, "; ".join(flags))
    return CheckResult("publish_safety", True, f"warning: {flags[0]}")


def check_visual_rhythm(text: str) -> CheckResult:
    """No paragraph >3 lines without a break."""
    lines = text.split("\n")
    in_block = 0
    max_block = 0
    for line in lines:
        if line.strip() == "":
            in_block = 0
        elif line.strip() == "⸻":
            in_block = 0
        else:
            in_block += 1
            max_block = max(max_block, in_block)
    if max_block > 4:
        return CheckResult("visual_rhythm", False,
                           f"{max_block} lines without break (max 4)")
    return CheckResult("visual_rhythm", True, "")


def check_stamp(text: str) -> CheckResult:
    """Stamp at end OR a strong final line.
    v2 (Day 7 evening reset): stamps are OPTIONAL. v1's mandatory 'Korean builder, Day X.'
    was retired. A post can stand without a stamp; a strong closing line is enough.
    This check now passes by default; it only fails if the post explicitly tries
    to USE a v1 stamp incorrectly (left here for forward compatibility)."""
    return CheckResult("stamp", True, "v2: stamps optional")
    # --- v1 logic preserved below for reference ---
    lower = text.lower()
    last_block = text.strip().split("\n")[-3:]
    last_text = " ".join(last_block).lower()
    if any(re.search(p, last_text) for p in STAMP_PATTERNS):
        return CheckResult("stamp", True, "")
    # Allow no stamp if the post is short (<3 lines) or is a reply (often shorter)
    if len(text.split("\n")) < 3:
        return CheckResult("stamp", True, "short post — stamp optional")
    return CheckResult("stamp", False, "no stamp at end (consider adding 'Korean builder, Day X.')")


def check_korean_concept_usage(text: str) -> CheckResult:
    """If a Korean concept appears, it should be USED in a sentence, not just defined."""
    found_concepts = [c for c in KNOWN_CONCEPTS if c in text.lower()]
    if not found_concepts:
        return CheckResult("concept_usage", True, "no concept (OK)")

    # Check: does the concept appear in only one place AND with parenthetical romanization?
    # That's a sign of forced lecture mode.
    pattern_lecture = r"\([a-z\-]+\)\s*(—|-)\s*[a-z]"  # "(romanization) — meaning"
    has_lecture = bool(re.search(pattern_lecture, text.lower()))
    has_multiple_uses = sum(text.lower().count(c) for c in found_concepts) >= 2

    # Also check: more than 2 distinct concepts in one post = stacking (banned)
    distinct = set()
    for c in found_concepts:
        # group canonical: 가성비 + ga-seong-bi count as one
        if "가성비" in c or "ga-seong-bi" in c or "gaseongbi" in c:
            distinct.add("가성비")
        elif "위기" in c or "危機" in c or "wi-gi" in c:
            distinct.add("危機")
        elif "한솥밥" in c or "han-sot" in c:
            distinct.add("한솥밥")
        elif "깐깐" in c:
            distinct.add("깐깐함")
        elif "빨리" in c or "ppalli" in c:
            distinct.add("빨리빨리")
        elif "의리" in c or "uy-ri" in c:
            distinct.add("의리")
        elif "복기" in c or "bok-gi" in c:
            distinct.add("복기")
        elif "눈치" in c or "nun-chi" in c:
            distinct.add("눈치")
        elif "정성" in c or "jeong-seong" in c:
            distinct.add("정성")
        elif "시작이" in c:
            distinct.add("시작이 반이다")
        else:
            distinct.add(c)

    if len(distinct) > 2:
        return CheckResult("concept_usage", False,
                           f"stacking {len(distinct)} concepts: {distinct}")

    return CheckResult("concept_usage", True, f"used: {distinct}")


def check_year_test(text: str) -> CheckResult:
    """Heuristic: does this have a real receipt OR a real insight, not just a take?
    Day 9 update: handles Korean text (no \b boundary on digits)."""
    lower = text.lower()
    # English regex (word boundary)
    has_specific_en = bool(re.search(
        r"\b(day\s*\d+|\d{2,}|\d+[kmKMxX]|\$\d|\d+%|\d+/\d+)\b", text
    ))
    # Korean / unicode-friendly: any 2+ digit sequence works (handles 30초, 2024년, 1만)
    has_specific_ko = bool(re.search(r"\d{2,}", text)) or bool(re.search(r"\d+[만천억]", text))
    has_specific = has_specific_en or has_specific_ko

    has_personal_action_en = any(p in lower for p in [
        "i shipped", "i'm running", "i tested", "i built", "i'm on day",
        "i tried", "i found", "i learned", "i pick", "saving this", "i'm watching",
        "i've been", "i noticed", "i'm reading", "i'm seeing"
    ])
    has_personal_action_ko = any(p in text for p in [
        "내가", "나는", "저는", "내일", "오늘", "어제",
        "발견", "배웠", "깨달", "확인", "사용", "운영", "보고 있",
        "쓰고 있", "만들었", "테스트", "느꼈", "생각함"
    ])
    has_personal_action = has_personal_action_en or has_personal_action_ko

    has_quote = '"' in text or '"' in text or "'" in text
    if has_specific or has_personal_action:
        return CheckResult("year_test", True, "")
    if len(text) < 200 and has_quote:
        return CheckResult("year_test", True, "short reply — quote alone is OK")
    return CheckResult("year_test", False,
                       "no concrete receipt or first-person action — feels generic")


def check_draft(draft: dict) -> dict:
    """Return {passed, fails, warnings, results[]} for a draft dict."""
    text = draft.get("text", "")
    banned = load_banned_phrases()

    checks = [
        check_banned(text, banned),
        check_ai_tells(text),
        check_korean_translationese(text),
        check_visual_rhythm(text),
        check_publish_safety(text),
        check_stamp(text),
        check_korean_concept_usage(text),
        check_year_test(text),
    ]

    fails = [c for c in checks if not c.passed]
    return {
        "passed": len(fails) == 0,
        "fails": [c.name for c in fails],
        "warnings": [],
        "details": [{"name": c.name, "passed": c.passed, "note": c.note} for c in checks],
    }


# CLI
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Check arbitrary text")
    parser.add_argument("--draft-id", help="Check a draft by ID from drafts.json")
    parser.add_argument("--all-pending", action="store_true",
                        help="Check all pending drafts")
    args = parser.parse_args()

    drafts_file = Path.home() / "x" / "grow" / "auto" / "drafts.json"

    if args.text:
        result = check_draft({"text": args.text})
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.draft_id:
        with drafts_file.open() as f:
            data = json.load(f)
        for d in data["drafts"]:
            if d["id"] == args.draft_id:
                result = check_draft(d)
                print(f"=== {args.draft_id} ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                break
        else:
            print(f"Draft {args.draft_id} not found.")
            sys.exit(1)
    elif args.all_pending:
        with drafts_file.open() as f:
            data = json.load(f)
        for d in data["drafts"]:
            if d["status"] != "pending":
                continue
            result = check_draft(d)
            symbol = "✓" if result["passed"] else "✗"
            fails = ",".join(result["fails"]) if result["fails"] else "ok"
            print(f"  {symbol} {d['id']:10s} ({d['type']:5s}) {fails}")
    else:
        parser.print_help()
