"""Unit tests for the Nepluro content validator."""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from validate_content import (
    _normalize_text,
    _is_devanagari,
    validate_lesson_file,
    REQUIRED_FIELDS,
    VALID_LANGS,
)


def test_normalize_text_basic():
    """Whitespace is collapsed and text is lowered."""
    assert _normalize_text("  Photosynthesis  ") == "photosynthesis"
    assert _normalize_text("MULTIPLE   SPACES") == "multiple spaces"
    assert _normalize_text("\tTabs\tand\nnewlines\t") == "tabs and newlines"


def test_normalize_text_empty():
    """Empty/whitespace-only returns empty string."""
    assert _normalize_text("") == ""
    assert _normalize_text("   ") == ""


def test_is_devanagari_basic():
    """Devanagari detection works."""
    assert _is_devanagari("नमस्ते") is True
    assert _is_devanagari("Namaste") is False
    assert _is_devanagari("") is False
    assert _is_devanagari("Hello नेमलो") is True


def test_validate_schema_all_fields():
    """A lesson with all required fields passes schema check."""
    import json
    from pathlib import Path
    lessons_path = Path(__file__).parent / "data" / "lessons.json"
    ok, messages = validate_lesson_file(str(lessons_path))
    assert ok is True, f"Expected valid, got: {messages}"


def test_validate_duplicate_ids():
    """Duplicate IDs are detected."""
    import json
    from pathlib import Path

    # Create a temp file with duplicate IDs
    data = {
        "lessons": [
            {"id": "dup-1", "track": "T", "subject": "S", "topic": "Top", "title": "T", "language": "en", "content": "C"},
            {"id": "dup-1", "track": "T", "subject": "S", "topic": "Top", "title": "T", "language": "en", "content": "C"},
        ]
    }
    tmp_path = Path(__file__).parent / "test_dup_lessons.json"
    tmp_path.write_text(json.dumps(data), encoding="utf-8")

    ok, messages = validate_lesson_file(str(tmp_path))
    assert ok is False, "Should detect duplicate IDs"
    assert any("duplicate id" in m for m in messages), f"Expected duplicate ID message, got: {messages}"

    # Clean up
    tmp_path.unlink()


def test_validate_invalid_language():
    """Invalid language codes are rejected."""
    import json
    from pathlib import Path

    data = {
        "lessons": [
            {"id": "bad-lang", "track": "T", "subject": "S", "topic": "Top", "title": "T", "language": "fr", "content": "C"},
        ]
    }
    tmp_path = Path(__file__).parent / "test_bad_lang.json"
    tmp_path.write_text(json.dumps(data), encoding="utf-8")

    ok, messages = validate_lesson_file(str(tmp_path))
    assert ok is False, "Should reject invalid language code"
    assert any("invalid language code" in m for m in messages), f"Expected invalid language message, got: {messages}"

    tmp_path.unlink()


def test_validate_ne_without_devanagari():
    """Nepali lessons without Devanagari are flagged."""
    import json
    from pathlib import Path

    data = {
        "lessons": [
            {
                "id": "no-nepali",
                "track": "T",
                "subject": "S",
                "topic": "Top",
                "title": "Title",
                "language": "ne",
                "content": "This is English content, not Nepali.",
            }
        ]
    }
    tmp_path = Path(__file__).parent / "test_no_ne.json"
    tmp_path.write_text(json.dumps(data), encoding="utf-8")

    ok, messages = validate_lesson_file(str(tmp_path))
    assert ok is False, "Should flag ne-lesson without Devanagari"
    assert any("no Devanagari" in m for m in messages), f"Expected Devanagari message, got: {messages}"

    tmp_path.unlink()


def test_validate_en_with_devanagari():
    """English lessons with Devanagari are flagged."""
    import json
    from pathlib import Path

    data = {
        "lessons": [
            {
                "id": "en-has-nepali",
                "track": "T",
                "subject": "S",
                "topic": "Top",
                "title": "Title",
                "language": "en",
                "content": "नमस्ते world",
            }
        ]
    }
    tmp_path = Path(__file__).parent / "test_en_ne.json"
    tmp_path.write_text(json.dumps(data), encoding="utf-8")

    ok, messages = validate_lesson_file(str(tmp_path))
    assert ok is False, "Should flag en-lesson with Devanagari"
    assert any("Devanagari" in m for m in messages), f"Expected Devanagari message, got: {messages}"

    tmp_path.unlink()


def test_validate_missing_field():
    """Missing required fields are detected."""
    import json
    from pathlib import Path

    data = {
        "lessons": [
            {
                "id": "missing-field",
                "track": "T",
                # missing subject, topic, title, language, content
                "subject": "S",
            }
        ]
    }
    tmp_path = Path(__file__).parent / "test_missing_field.json"
    tmp_path.write_text(json.dumps(data), encoding="utf-8")

    ok, messages = validate_lesson_file(str(tmp_path))
    assert ok is False, "Should detect missing fields"
    # Should mention the missing field
    missing_mentions = [m for m in messages if "missing non-empty" in m]
    assert len(missing_mentions) > 0, f"Expected missing field messages, got: {messages}"

    tmp_path.unlink()


def test_validate_empty_content():
    """Empty content strings are rejected."""
    import json
    from pathlib import Path

    data = {
        "lessons": [
            {
                "id": "empty-content",
                "track": "T",
                "subject": "S",
                "topic": "Top",
                "title": "T",
                "language": "en",
                "content": "",
            }
        ]
    }
    tmp_path = Path(__file__).parent / "test_empty_content.json"
    tmp_path.write_text(json.dumps(data), encoding="utf-8")

    ok, messages = validate_lesson_file(str(tmp_path))
    assert ok is False, "Should reject empty content"
    assert any("missing non-empty 'content'" in m for m in messages), f"Expected empty content message, got: {messages}"

    tmp_path.unlink()


def test_validator_with_real_data():
    """Validator passes on the actual lessons.json file."""
    lessons_path = Path(__file__).parent / "data" / "lessons.json"
    ok, messages = validate_lesson_file(str(lessons_path))
    assert ok is True, f"Expected real lessons to pass, errors: {messages}"
    assert len(messages) == 0, f"Expected no messages, got: {messages}"


if __name__ == "__main__":
    # Run all tests
    failures = 0
    tests = [
        test_normalize_text_basic,
        test_normalize_text_empty,
        test_is_devanagari_basic,
        test_validate_schema_all_fields,
        test_validate_duplicate_ids,
        test_validate_invalid_language,
        test_validate_ne_without_devanagari,
        test_validate_en_with_devanagari,
        test_validate_missing_field,
        test_validate_empty_content,
        test_validator_with_real_data,
    ]

    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
        except AssertionError as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"  ERROR: {test.__name__}: {e}")
            failures += 1

    print(f"\n{len(tests) - failures}/{len(tests)} tests passed")
    sys.exit(1 if failures else 0)