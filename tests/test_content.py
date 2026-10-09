"""Tests for lesson content loading and validation."""

import json
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


def test_repo_lessons_file_is_valid():
    lessons = content.load_lessons()
    assert len(lessons) >= 3
    assert all(lesson["language"] in content.LANGUAGE_LABELS for lesson in lessons)
    ids = [lesson["id"] for lesson in lessons]
    assert len(ids) == len(set(ids)), "lesson ids must be unique"
    assert all(len(lesson["content"]) > 40 for lesson in lessons)
