"""Comprehensive content validator for Nepluro lessons.

Validates:
- Schema compliance per lesson (required fields, types, non-empty)
- Unique lesson IDs
- Valid language codes (en, ne)
- Language-script consistency (ne lessons should have Devanagari)
- Content non-empty string check
- Duplicate ID detection across the file

No external dependencies beyond Python 3 stdlib.
"""

import json
import sys
import re
from pathlib import Path
from typing import Any, List, Set, Tuple

REQUIRED_FIELDS = ("id", "track", "subject", "topic", "title", "language", "content")
VALID_LANGS = {"en", "ne"}

# Nepali (Devanagari) Unicode range
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def _normalize_text(text: str) -> str:
    """Lowercase, strip, and collapse whitespace."""
    return re.sub(r"\s+", " ", text.strip().lower())


def validate_lesson_file(path: str) -> Tuple[bool, List[str]]:
    """Validate a lessons.json file and return (ok, messages)."""
    messages: List[str] = []
    p = Path(path)

    if not p.exists():
        messages.append(f"File not found: {path}")
        return False, messages

    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        messages.append(f"Invalid JSON: {exc}")
        return False, messages

    if not isinstance(raw, dict):
        messages.append("Root element must be a JSON object.")
        return False, messages

    if "lessons" not in raw:
        messages.append("Missing 'lessons' key.")
        return False, messages
    if not isinstance(raw["lessons"], list):
        messages.append("'lessons' must be a list.")
        return False, messages

    required_fields = REQUIRED_FIELDS
    seen_ids: Set[str] = set()

    for i, lesson in enumerate(raw["lessons"]):
        if not isinstance(lesson, dict):
            messages.append(f"Lesson {i} is not a JSON object.")
            continue

        # --- Required fields ---
        for field in required_fields:
            value = lesson.get(field)
            if not isinstance(value, str) or not value.strip():
                messages.append(f"Lesson {i}: missing non-empty '{field}'.")

        # --- Unique IDs ---
        lesson_id = lesson.get("id", "")
        if lesson_id in seen_ids:
            messages.append(f"Lesson {i}: duplicate id '{lesson_id}'.")
        else:
            seen_ids.add(lesson_id)

        # --- Valid language code ---
        lang = lesson.get("language", "")
        if lang not in VALID_LANGS:
            messages.append(f"Lesson {i}: invalid language code '{lang}' (must be 'en' or 'ne').")

        # --- Language-script consistency ---
        content = lesson.get("content")
        if isinstance(content, str):
            if lang == "ne" and not _is_devanagari(content):
                messages.append(
                    f"Lesson {i} (ne): language is 'ne' but content has no Devanagari characters."
                )
            if lang == "en" and _is_devanagari(content):
                messages.append(
                    f"Lesson {i} (en): language is 'en' but content contains Devanagari."
                )

    # --- Cross-lesson checks ---
    all_ids = [lesson.get("id", "") for lesson in raw["lessons"]]
    if len(all_ids) != len(set(all_ids)):
        messages.append("Duplicate lesson IDs found across the file.")

    if not raw["lessons"]:
        messages.append("Lesson file contains no lessons.")

    ok = len(messages) == 0
    return ok, messages


def _is_devanagari(text: str) -> bool:
    """Check if text contains Devanagari characters."""
    return bool(DEVANAGARI_RE.search(text))


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validate_content.py <path_to_lessons.json>")
        return 1

    path = Path(sys.argv[1])
    ok, messages = validate_lesson_file(str(path))

    if ok:
        raw = json.loads(path.read_text(encoding="utf-8"))
        print(f"SUCCESS: Lesson file is valid. {len(raw['lessons'])} lessons validated.")
        return 0
    else:
        print("FAILED: Lesson file has errors:")
        for m in messages:
            print(f"  - {m}")
        return 1


if __name__ == "__main__":
    sys.exit(main())