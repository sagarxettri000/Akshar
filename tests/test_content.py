"""Tests for lesson content loading and validation."""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import content  # noqa: E402


VALID_LESSON = {
    "id": "x",
    "track": "NEB Grade 11",
    "subject": "Physics",
    "topic": "Kinematics",
    "title": "Speed and Velocity",
    "language": "en",
    "content": "Speed is the rate of change of distance.",
}


def _write(tmp_path, data):
    path = tmp_path / "lessons.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_validate_lesson_accepts_valid():
    assert content.validate_lesson(VALID_LESSON) == VALID_LESSON


def test_validate_lesson_trims_whitespace():
    messy = dict(VALID_LESSON, title="  Speed  ")
    assert content.validate_lesson(messy)["title"] == "Speed"


def test_validate_lesson_rejects_missing_field():
    bad = dict(VALID_LESSON)
    del bad["content"]
    with pytest.raises(content.ContentError):
        content.validate_lesson(bad)


def test_validate_lesson_rejects_non_dict():
    with pytest.raises(content.ContentError):
        content.validate_lesson(["nope"])


def test_load_lessons_reads_file(tmp_path):
    path = _write(tmp_path, {"lessons": [VALID_LESSON]})
    assert content.load_lessons(path) == [VALID_LESSON]


def test_load_lessons_rejects_missing_file(tmp_path):
    with pytest.raises(content.ContentError):
        content.load_lessons(tmp_path / "missing.json")


def test_load_lessons_rejects_invalid_json(tmp_path):
    path = tmp_path / "lessons.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(content.ContentError):
        content.load_lessons(path)


def test_load_lessons_rejects_empty_list(tmp_path):
    path = _write(tmp_path, {"lessons": []})
    with pytest.raises(content.ContentError):
        content.load_lessons(path)


def test_load_lessons_rejects_wrong_shape(tmp_path):
    path = _write(tmp_path, [VALID_LESSON])
    with pytest.raises(content.ContentError):
        content.load_lessons(path)


def test_filter_and_unique_values():
    lessons = [
        VALID_LESSON,
        dict(VALID_LESSON, id="y", language="ne"),
        dict(VALID_LESSON, id="z", subject="Chemistry"),
    ]
    assert content.unique_values(lessons, "subject") == ["Physics", "Chemistry"]
    assert len(content.filter_lessons(lessons, subject="Physics")) == 2
    assert content.filter_lessons(lessons, subject="Physics", topic="None") == []


def test_lesson_label_falls_back_to_code():
    assert content.lesson_label("en") == "English"
    assert content.lesson_label("xx") == "xx"


def test_lessons_signature_is_path_bound():
    signature = content.lessons_signature()
    assert "lessons.json" in signature


def test_lessons_signature_changes_when_file_changes(tmp_path):
    path = _write(tmp_path, {"version": 1, "lessons": [VALID_LESSON]})
    first = content.lessons_signature(path)
    os.utime(path, (1, 1))
    second = content.lessons_signature(path)
    assert first != second


def test_repo_lessons_file_is_valid():
    lessons = content.load_lessons()
    assert len(lessons) >= 3
    assert all(lesson["language"] in content.LANGUAGE_LABELS for lesson in lessons)
    ids = [lesson["id"] for lesson in lessons]
    assert len(ids) == len(set(ids)), "lesson ids must be unique"
    assert all(len(lesson["content"]) > 40 for lesson in lessons)


# ---------------------------------------------------------------------------
# Study-path resolution
# ---------------------------------------------------------------------------


def test_resolve_study_path_keeps_a_valid_selection():
    lessons = content.load_lessons()
    resolved = content.resolve_study_path(
        lessons,
        track="CEE",
        subject="Physics",
        topic="Kinematics",
        language="ne",
    )
    assert resolved["lesson"]["id"] == "cee-kinematics-ne"
    assert resolved["language"] == "ne"


def test_resolve_study_path_falls_back_when_a_child_is_stale():
    """A selectbox hands back a stale value when its options change.

    The old app passed that value straight into ``next(...)`` over an empty
    lesson list and crashed with StopIteration. Each level must fall back to a
    value that exists under its parent.
    """
    lessons = content.load_lessons()
    resolved = content.resolve_study_path(
        lessons,
        track="IOE",
        subject="Mathematics",
        topic="Kinematics",
        language="xx",
    )
    assert resolved["topic"] == "Algebra"
    assert resolved["language"] == "en"
    assert resolved["lesson"]["id"] == "ioe-quadratics-en"


def test_resolve_study_path_always_matches_the_requested_track():
    lessons = content.load_lessons()
    for track in content.unique_values(lessons, "track"):
        resolved = content.resolve_study_path(
            lessons, track=track, subject="Nope", topic="Nope", language="xx"
        )
        assert resolved["lesson"] is not None
        assert resolved["lesson"]["track"] == track
        assert resolved["track"] == track


def test_resolve_study_path_handles_no_lessons():
    resolved = content.resolve_study_path([])
    assert resolved["lesson"] is None
    assert resolved["variants"] == []
