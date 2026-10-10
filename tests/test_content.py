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


def test_filter_lessons_with_track():
    """Filter lessons by track composes correctly."""
    lessons = [
        VALID_LESSON,
        dict(VALID_LESSON, id="y", track="CEE"),
        dict(VALID_LESSON, id="z", track="IOE"),
    ]
    neb_grade11 = content.filter_lessons(lessons, track="NEB Grade 11")
    assert len(neb_grade11) == 1  # only VALID_LESSON has track "NEB Grade 11"
    assert neb_grade11[0]["id"] == "x"


def test_filter_lessons_with_subject():
    """Filter lessons by subject composes correctly."""
    lessons = [
        VALID_LESSON,
        dict(VALID_LESSON, id="y", subject="Chemistry"),
    ]
    chemistry = content.filter_lessons(lessons, subject="Chemistry")
    assert len(chemistry) == 1
    assert chemistry[0]["id"] == "y"


def test_filter_lessons_with_topic():
    """Filter lessons by topic composes correctly."""
    lessons = [
        VALID_LESSON,
        dict(VALID_LESSON, id="y", topic="Kinematics"),
        dict(VALID_LESSON, id="z", topic="Derivatives"),
    ]
    kinematics = content.filter_lessons(lessons, topic="Kinematics")
    assert len(kinematics) == 2  # both have topic Kinematics (first + the y duplicate)


def test_filter_lessons_with_language():
    """Filter lessons by language code works."""
    lessons = [
        VALID_LESSON,
        dict(VALID_LESSON, id="y", language="ne"),
    ]
    ne_lessons = content.filter_lessons(lessons, language="ne")
    assert len(ne_lessons) == 1
    assert ne_lessons[0]["id"] == "y"


def test_filter_lessons_composes():
    """Multiple filters compose together (AND logic)."""
    lessons = [
        dict(VALID_LESSON, id="a", subject="Physics", track="NEB Grade 11"),
        dict(VALID_LESSON, id="b", subject="Physics", track="CEE"),
        dict(VALID_LESSON, id="c", subject="Chemistry", track="NEB Grade 11"),
    ]
    # Physics AND NEB Grade 11 should only match lesson "a"
    result = content.filter_lessons(lessons, subject="Physics", track="NEB Grade 11")
    assert len(result) == 1
    assert result[0]["id"] == "a"


def test_filter_lessons_empty_result():
    """Filter that matches no lessons returns empty list."""
    lessons = [
        VALID_LESSON,
        dict(VALID_LESSON, id="y", subject="Chemistry"),
    ]
    result = content.filter_lessons(lessons, subject="Biology")
    assert result == []


def test_search_lessons_basic():
    """Search matches against title, topic, and content fields."""
    lessons = [
        dict(VALID_LESSON, title="Speed and Velocity", topic="Kinematics",
             content="Speed is the rate of change of distance."),
        dict(VALID_LESSON, id="y", title="Photosynthesis", topic="Photosynthesis",
             content="Photosynthesis converts light to chemical energy."),
    ]
    # Search by topic "Photosynthesis"
    results = content.search_lessons(lessons, "Photosynthesis")
    assert len(results) == 1
    assert results[0]["id"] == "y"


def test_search_lessons_case_insensitive():
    """Search is case-insensitive."""
    lessons = [
        dict(VALID_LESSON, title="Speed and Velocity", topic="Kinematics",
             content="Speed is the rate of change of distance."),
    ]
    results = content.search_lessons(lessons, "speed")
    assert len(results) == 1


def test_search_lessons_whitespace_tolerant():
    """Search ignores leading/trailing whitespace and collapses internal whitespace."""
    lessons = [
        dict(VALID_LESSON, title="Speed and Velocity", topic="Kinematics",
             content="Speed is the rate of change of distance."),
    ]
    results = content.search_lessons(lessons, "  speed  ")
    assert len(results) == 1


def test_search_lessons_empty_query():
    """Empty query returns empty list."""
    lessons = [
        VALID_LESSON,
    ]
    results = content.search_lessons(lessons, "")
    assert results == []


def test_search_lessons_whitespace_only_query():
    """Whitespace-only query returns empty list."""
    lessons = [
        VALID_LESSON,
    ]
    results = content.search_lessons(lessons, "   ")
    assert results == []


def test_search_lessons_nepali_preserved():
    """Search works with Nepali Unicode content."""
    lessons = [
        dict(
            id="ne-1",
            title="एक समान रेखामध्ये गति",
            topic="एक समान रेखामध्ये गति",
            content="एक वस्तु एकसाथ एक समान दिशामध्ये हरेक अवस्थाको साथ ठाउँबाट प्रवेश गर्दा हामी उनीको ठाउँको बदलावको बारे बोल्छौं।",
        ),
    ]
    results = content.search_lessons(lessons, "गति")
    assert len(results) == 1


def test_search_lessons_no_match():
    """Search with no matching query returns empty list."""
    lessons = [
        dict(VALID_LESSON, title="Speed and Velocity", topic="Kinematics",
             content="Speed is the rate of change of distance."),
    ]
    results = content.search_lessons(lessons, "quantum physics")
    assert results == []


def test_repo_lessons_file_is_valid():
    lessons = content.load_lessons()
    assert len(lessons) >= 3
    assert all(lesson["language"] in content.LANGUAGE_LABELS for lesson in lessons)
    ids = [lesson["id"] for lesson in lessons]
    assert len(ids) == len(set(ids)), "lesson ids must be unique"
    assert all(len(lesson["content"]) > 40 for lesson in lessons)
