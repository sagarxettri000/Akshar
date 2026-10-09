"""Tests for validate_lessons.py — the standalone lesson-file validator.

All tests use temporary files (pytest's tmp_path fixture). The real
data/lessons.json is never read or modified.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import validate_lessons  # noqa: E402


# ── Helpers ──────────────────────────────────────────────────────────────────

def _valid_lesson(lesson_id="test-1", **overrides):
    """Return a valid lesson dict, with optional field overrides."""
    lesson = {
        "id": lesson_id,
        "track": "NEB Grade 11",
        "subject": "Physics",
        "topic": "Kinematics",
        "title": "Speed and Velocity",
        "language": "en",
        "content": "Speed is the rate of change of distance.",
    }
    lesson.update(overrides)
    return lesson


def _write_json(path, data):
    """Write data as JSON to path. Returns the path."""
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def _valid_file(tmp_path, lessons=None):
    """Create a valid lessons.json in tmp_path. Returns the path."""
    if lessons is None:
        lessons = [_valid_lesson("lesson-a"), _valid_lesson("lesson-b")]
    return _write_json(tmp_path / "lessons.json", {"version": 1, "lessons": lessons})


# ── Valid data ────────────────────────────────────────────────────────────────

class TestValidData:
    def test_valid_file_passes(self, tmp_path):
        path = _valid_file(tmp_path)
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is True
        assert any("SUCCESS" in m for m in messages)

    def test_single_lesson_passes(self, tmp_path):
        path = _valid_file(tmp_path, lessons=[_valid_lesson("only-one")])
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is True

    def test_nepali_language_passes(self, tmp_path):
        path = _valid_file(tmp_path, lessons=[_valid_lesson("nepali-1", language="ne")])
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is True

    def test_extra_top_level_keys_ok(self, tmp_path):
        """Extra top-level keys like 'note' should not cause failure."""
        data = {"version": 1, "note": "test", "lessons": [_valid_lesson("x")]}
        path = _write_json(tmp_path / "lessons.json", data)
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is True

    def test_whitespace_only_id_fails(self, tmp_path):
        path = _valid_file(tmp_path, lessons=[_valid_lesson("  ")])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("empty or non-string 'id'" in m for m in messages)


# ── Malformed JSON ──────────────────────────────────────────────────────────

class TestMalformedJson:
    def test_invalid_json_syntax(self, tmp_path):
        path = tmp_path / "lessons.json"
        path.write_text("{not valid json", encoding="utf-8")
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("Invalid JSON" in m for m in messages)

    def test_empty_file(self, tmp_path):
        path = tmp_path / "lessons.json"
        path.write_text("", encoding="utf-8")
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("Invalid JSON" in m for m in messages)

    def test_file_not_found(self, tmp_path):
        missing = str(tmp_path / "does-not-exist.json")
        ok, messages = validate_lessons.validate_lesson_file(missing)
        assert ok is False
        assert any("File not found" in m for m in messages)


# ── Root structure ───────────────────────────────────────────────────────────

class TestRootStructure:
    def test_root_is_list_not_object(self, tmp_path):
        """A bare JSON array at root should fail (app expects an object)."""
        path = _write_json(tmp_path / "lessons.json", [_valid_lesson("x")])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("expected object" in m for m in messages)

    def test_missing_lessons_key(self, tmp_path):
        path = _write_json(tmp_path / "lessons.json", {"version": 1})
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("missing 'lessons' key" in m for m in messages)

    def test_lessons_is_not_a_list(self, tmp_path):
        path = _write_json(tmp_path / "lessons.json", {"lessons": "not a list"})
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("expected list" in m for m in messages)

    def test_empty_lessons_list(self, tmp_path):
        path = _write_json(tmp_path / "lessons.json", {"lessons": []})
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        # Empty list passes structural checks but yields 0 lessons
        assert ok is True
        assert any("0 lesson(s)" in m for m in messages)


# ── Missing required fields ─────────────────────────────────────────────────

class TestMissingFields:
    @pytest.mark.parametrize("field", ["id", "track", "subject", "topic", "title", "language", "content"])
    def test_each_required_field(self, tmp_path, field):
        lesson = _valid_lesson("x")
        del lesson[field]
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any(f"missing field(s)" in m and field in m for m in messages)

    def test_multiple_missing_fields(self, tmp_path):
        lesson = _valid_lesson("x")
        del lesson["track"]
        del lesson["content"]
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("track" in m and "content" in m for m in messages)

    def test_extra_unexpected_field(self, tmp_path):
        lesson = _valid_lesson("x", extra_field="should not be here")
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("unexpected field(s)" in m for m in messages)


# ── Empty strings ──────────────────────────────────────────────────────────

class TestEmptyStrings:
    @pytest.mark.parametrize("field", ["id", "track", "subject", "topic", "title", "language", "content"])
    def test_each_field_empty(self, tmp_path, field):
        lesson = _valid_lesson("x", **{field: ""})
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False

    def test_whitespace_only_string_fails(self, tmp_path):
        lesson = _valid_lesson("x", content="   ")
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is False


# ── Incorrect field types ──────────────────────────────────────────────────

class TestIncorrectTypes:
    def test_grade_is_integer_not_string(self, tmp_path):
        """track must be a string; integer should fail."""
        lesson = _valid_lesson("x", track=11)
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is False

    def test_language_is_integer(self, tmp_path):
        lesson = _valid_lesson("x", language=1)
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is False

    def test_content_is_null(self, tmp_path):
        lesson = _valid_lesson("x", content=None)
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is False

    def test_lesson_is_not_dict(self, tmp_path):
        """A lesson entry that is a plain string should fail."""
        path = _valid_file(tmp_path, lessons=["not a dict"])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("not a dictionary" in m for m in messages)


# ── Duplicate IDs ────────────────────────────────────────────────────────────

class TestDuplicateIds:
    def test_two_lessons_same_id(self, tmp_path):
        path = _valid_file(tmp_path, lessons=[_valid_lesson("dup"), _valid_lesson("dup")])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("Duplicate id" in m for m in messages)

    def test_three_lessons_one_duplicate(self, tmp_path):
        lessons = [_valid_lesson("a"), _valid_lesson("b"), _valid_lesson("a")]
        path = _valid_file(tmp_path, lessons=lessons)
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is False

    def test_all_unique_ids_pass(self, tmp_path):
        lessons = [_valid_lesson("a"), _valid_lesson("b"), _valid_lesson("c")]
        path = _valid_file(tmp_path, lessons=lessons)
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is True


# ── Invalid language values ─────────────────────────────────────────────────

class TestInvalidLanguage:
    def test_unknown_language_code(self, tmp_path):
        lesson = _valid_lesson("x", language="fr")
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, messages = validate_lessons.validate_lesson_file(str(path))
        assert ok is False
        assert any("language" in m and "fr" in m for m in messages)

    def test_empty_language_fails(self, tmp_path):
        lesson = _valid_lesson("x", language="")
        path = _valid_file(tmp_path, lessons=[lesson])
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is False

    def test_both_valid_languages_pass(self, tmp_path):
        lessons = [_valid_lesson("en-1", language="en"), _valid_lesson("ne-1", language="ne")]
        path = _valid_file(tmp_path, lessons=lessons)
        ok, _ = validate_lessons.validate_lesson_file(str(path))
        assert ok is True


# ── Real data file (read-only) ──────────────────────────────────────────────

class TestRealDataFile:
    """Validate the actual data/lessons.json without modifying it."""

    def test_real_file_passes(self):
        repo_root = Path(__file__).resolve().parents[1]
        real_path = repo_root / "data" / "lessons.json"
        ok, messages = validate_lessons.validate_lesson_file(str(real_path))
        assert ok is True, "\n".join(messages)
