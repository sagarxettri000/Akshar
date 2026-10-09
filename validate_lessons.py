"""
validate_lessons.py - Beginner-friendly validator for Akshar lesson data.

Checks data/lessons.json against the schema expected by content.py:
  - Valid JSON syntax
  - Root is an object with a 'lessons' list
  - Every lesson has exactly: id, track, subject, topic, title, language, content
  - Unique, non-empty IDs
  - Non-empty strings for all required fields
  - language is one of the codes defined in content.LANGUAGE_LABELS

Usage:
    python validate_lessons.py [path]

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
"""

import json
import os
import sys

DEFAULT_LESSON_FILE = os.path.join("data", "lessons.json")
REQUIRED_FIELDS = {"id", "track", "subject", "topic", "title", "language", "content"}
VALID_LANGUAGES = {"en", "ne"}


def validate_lesson_file(path):
    """Validate a lesson file at the given path.

    Returns (ok, messages) where ok is True if all checks passed,
    and messages is a list of human-readable strings.
    Does not call sys.exit() so it can be imported and tested safely.
    """
    messages = []

    # --- Check 1: File exists ---
    if not os.path.isfile(path):
        messages.append(f"FAIL: File not found: {path}")
        return False, messages
    messages.append(f"PASS: File found: {path}")

    # --- Check 2: Valid JSON ---
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        messages.append("PASS: JSON parsed successfully")
    except json.JSONDecodeError as e:
        messages.append(f"FAIL: Invalid JSON - {e}")
        return False, messages
    except Exception as e:
        messages.append(f"FAIL: Could not read file - {e}")
        return False, messages

    # --- Check 3: Root is an object with a 'lessons' list ---
    if not isinstance(data, dict):
        messages.append(f"FAIL: Root element is {type(data).__name__}, expected object (dict)")
        return False, messages
    if "lessons" not in data:
        messages.append("FAIL: Root object missing 'lessons' key")
        return False, messages
    if not isinstance(data["lessons"], list):
        messages.append(f"FAIL: 'lessons' is {type(data['lessons']).__name__}, expected list")
        return False, messages
    lessons = data["lessons"]
    messages.append(f"PASS: Root is an object with a 'lessons' list ({len(lessons)} lesson(s))")

    # --- Check 4: Every lesson has exactly the required fields ---
    errors = []
    for i, lesson in enumerate(lessons):
        if not isinstance(lesson, dict):
            errors.append(f"Lesson {i}: not a dictionary (got {type(lesson).__name__})")
            continue

        keys = set(lesson.keys())
        missing = REQUIRED_FIELDS - keys
        extra = keys - REQUIRED_FIELDS

        if missing:
            errors.append(f"Lesson {i} ({lesson.get('id', '?')}): missing field(s) {sorted(missing)}")
        if extra:
            errors.append(f"Lesson {i} ({lesson.get('id', '?')}): unexpected field(s) {sorted(extra)}")

    if errors:
        for e in errors:
            messages.append(f"FAIL: {e}")
        return False, messages
    messages.append(f"PASS: All {len(lessons)} lesson(s) have exactly the 7 required fields")

    # --- Check 5: IDs are unique and non-empty ---
    seen_ids = set()
    for lesson in lessons:
        lid = lesson.get("id", "")
        if not isinstance(lid, str) or not lid.strip():
            messages.append(f"FAIL: Lesson has empty or non-string 'id': {repr(lid)}")
            return False, messages
        if lid in seen_ids:
            messages.append(f"FAIL: Duplicate id: '{lid}'")
            return False, messages
        seen_ids.add(lid)
    messages.append(f"PASS: All {len(seen_ids)} ID(s) unique and non-empty")

    # --- Check 6: All required fields are non-empty strings ---
    errors = []
    for lesson in lessons:
        lid = lesson.get("id", "?")
        for field in REQUIRED_FIELDS:
            val = lesson.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"Lesson '{lid}': '{field}' is empty or not a string")
    if errors:
        for e in errors:
            messages.append(f"FAIL: {e}")
        return False, messages
    messages.append("PASS: All required fields are non-empty strings")

    # --- Check 7: Language values are valid ---
    errors = []
    for lesson in lessons:
        lid = lesson.get("id", "?")
        lang = lesson.get("language", "")
        if lang not in VALID_LANGUAGES:
            errors.append(f"Lesson '{lid}': language '{lang}' not in {sorted(VALID_LANGUAGES)}")
    if errors:
        for e in errors:
            messages.append(f"FAIL: {e}")
        return False, messages
    messages.append("PASS: All language values are valid (en, ne)")

    # --- All passed ---
    messages.append("")
    messages.append(f"SUCCESS: All checks passed. {len(lessons)} lesson(s) validated.")
    return True, messages


def main():
    """CLI entry point. Accepts an optional file path argument."""
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LESSON_FILE
    ok, messages = validate_lesson_file(path)
    for msg in messages:
        print(msg)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
