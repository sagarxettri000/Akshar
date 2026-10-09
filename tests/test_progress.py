"""Tests for session-scoped progress tracking."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import progress  # noqa: E402


def test_new_state_is_empty():
    assert progress.new_state() == {}


def test_record_attempt_creates_entry():
    state = progress.new_state()
    progress.record_attempt(state, "lesson-1", 2, 3)
    entry = progress.get_lesson_progress(state, "lesson-1")
    assert entry is not None
    assert len(entry["attempts"]) == 1
    assert entry["attempts"][0]["score"] == 2
    assert entry["best_score"] == 2
    assert entry["best_total"] == 3


def test_best_score_only_improves():
    state = progress.new_state()
    progress.record_attempt(state, "l", 3, 4)
    progress.record_attempt(state, "l", 1, 4)
    entry = progress.get_lesson_progress(state, "l")
    assert entry["best_score"] == 3
    assert len(entry["attempts"]) == 2


def test_better_ratio_replaces_best():
    state = progress.new_state()
    progress.record_attempt(state, "l", 3, 5)  # 60%
    progress.record_attempt(state, "l", 2, 3)  # 66.6%
    entry = progress.get_lesson_progress(state, "l")
    assert entry["best_score"] == 2
    assert entry["best_total"] == 3


def test_record_attempt_uses_supplied_timestamp():
    state = progress.new_state()
    progress.record_attempt(state, "l", 1, 1, timestamp="2026-01-01T00:00:00+00:00")
    entry = progress.get_lesson_progress(state, "l")
    assert entry["last_at"] == "2026-01-01T00:00:00+00:00"


@pytest.mark.parametrize(
    "lesson_id, score, total",
    [
        ("", 1, 1),
        ("l", 5, 3),
        ("l", -1, 3),
        ("l", 1, 0),
    ],
)
def test_record_attempt_rejects_invalid_input(lesson_id, score, total):
    with pytest.raises(ValueError):
        progress.record_attempt(progress.new_state(), lesson_id, score, total)


def test_get_lesson_progress_missing_returns_none():
    assert progress.get_lesson_progress(progress.new_state(), "nope") is None


def test_summarize_counts_and_average():
    state = progress.new_state()
    progress.record_attempt(state, "a", 3, 4)  # 75%
    progress.record_attempt(state, "a", 4, 4)  # 100% -> best
    progress.record_attempt(state, "b", 1, 2)  # 50%
    summary = progress.summarize(state)
    assert summary["lessons_practised"] == 2
    assert summary["total_attempts"] == 3
    assert summary["average_best_percent"] == 75.0


def test_summarize_empty_state():
    summary = progress.summarize(progress.new_state())
    assert summary == {
        "lessons_practised": 0,
        "total_attempts": 0,
        "average_best_percent": 0.0,
    }
