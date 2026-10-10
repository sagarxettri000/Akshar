"""
validate_lessons.py — Beginner-friendly validator for Akshar lesson data.

Checks data/lessons.json for:
  - Valid JSON syntax
  - Root element is a list
  - Every lesson has exactly: id, grade, subject, chapter, exam_tags, content
  - Unique, non-empty IDs
  - Non-empty strings for grade, subject, chapter, content
  - exam_tags is a non-empty list of non-empty strings

Usage:
    python validate_lessons.py

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
"""

import json
import os
import sys

LESSON_FILE = os.path.join("data", "lessons.json")
REQUIRED_FIELDS = {"id", "grade", "subject", "chapter", "exam_tags", "content"}
STRING_FIELDS = ["grade", "subject", "chapter", "content"]


def main():
    errors = []

    # --- Check 1: File exists ---
    if not os.path.isfile(LESSON_FILE):
        print(f"FAIL: File not found: {LESSON_FILE}")
        sys.exit(1)
    print(f"PASS: File found: {LESSON_FILE}")

    # --- Check 2: Valid JSON ---
    try:
        with open(LESSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("PASS: JSON parsed successfully")
    except json.JSONDecodeError as e:
        print(f"FAIL: Invalid JSON — {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: Could not read file — {e}")
        sys.exit(1)

    # --- Check 3: Root is a list ---
    if not isinstance(data, list):
        print(f"FAIL: Root element is {type(data).__name__}, expected list")
        sys.exit(1)
    print(f"PASS: Root is a list with {len(data)} lesson(s)")

    # --- Check 4: Every lesson has exactly the required fields ---
    for i, lesson in enumerate(data):
        if not isinstance(lesson, dict):
            errors.append(f"Lesson {i}: not a dictionary (got {type(lesson).__name__})")
            continue

        keys = set(lesson.keys())
        missing = REQUIRED_FIELDS - keys
        extra = keys - REQUIRED_FIELDS

        if missing:
            errors.append(f"Lesson {i}: missing field(s) {sorted(missing)}")
        if extra:
            errors.append(f"Lesson {i}: unexpected field(s) {sorted(extra)}")

    if any("missing field" in e or "unexpected field" in e for e in errors):
        for e in errors:
            if "missing field" in e or "unexpected field" in e:
                print(f"FAIL: {e}")
        sys.exit(1)
    print(f"PASS: All {len(data)} lesson(s) have exactly the 6 required fields")

    # --- Check 5: IDs are unique and non-empty ---
    seen_ids = set()
    for lesson in data:
        lid = lesson.get("id", "")
        if not isinstance(lid, str) or not lid.strip():
            errors.append(f"Lesson has empty or non-string 'id': {repr(lid)}")
        elif lid in seen_ids:
            errors.append(f"Duplicate id: '{lid}'")
        else:
            seen_ids.add(lid)

    if any("id" in e.lower() for e in errors):
        for e in errors:
            if "id" in e.lower():
                print(f"FAIL: {e}")
        sys.exit(1)
    print(f"PASS: All {len(seen_ids)} ID(s) unique and non-empty")

    # --- Check 6: grade, subject, chapter, content are non-empty strings ---
    for lesson in data:
        lid = lesson.get("id", f"lesson {data.index(lesson)}")
        for field in STRING_FIELDS:
            val = lesson.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"Lesson '{lid}': '{field}' is empty or not a string (got {type(val).__name__})")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: grade, subject, chapter, content are all non-empty strings")

    # --- Check 7: exam_tags is a non-empty list of non-empty strings ---
    for lesson in data:
        lid = lesson.get("id", f"lesson {data.index(lesson)}")
        tags = lesson.get("exam_tags")
        if not isinstance(tags, list):
            errors.append(f"Lesson '{lid}': exam_tags is {type(tags).__name__}, expected list")
        elif len(tags) == 0:
            errors.append(f"Lesson '{lid}': exam_tags is empty")
        else:
            for j, tag in enumerate(tags):
                if not isinstance(tag, str) or not tag.strip():
                    errors.append(f"Lesson '{lid}': exam_tags[{j}] is empty or not a string")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: exam_tags are non-empty lists of non-empty strings")

    # --- All passed ---
    print()
    print(f"SUCCESS: All checks passed. {len(data)} lesson(s) validated.")
    print()
    for lesson in data:
        print(f"  - {lesson['id']} (Grade {lesson['grade']} {lesson['subject']})")
    sys.exit(0)


if __name__ == "__main__":
    main()
