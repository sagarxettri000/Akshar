"""Lightweight, session-scoped learner progress tracking for Akshar.

Progress is stored as a plain dictionary so it can live in Streamlit's session
state and be unit tested without a Streamlit runtime. As little data as possible
is kept: only lesson ids, attempt scores, and timestamps — no personal details.
"""

from __future__ import annotations

from datetime import datetime, timezone

__all__ = [
    "new_state",
    "record_attempt",
    "get_lesson_progress",
    "summarize",
]


def new_state() -> dict:
    """Return an empty progress state."""
    return {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _percent(score: int, total: int) -> float:
    return (score / total * 100.0) if total else 0.0


def record_attempt(
    state: dict,
    lesson_id: str,
    score: int,
    total: int,
    timestamp: str | None = None,
) -> dict:
    """Record one practice attempt for ``lesson_id`` and return ``state``.

    Raises ``ValueError`` for invalid input so callers cannot store bad data.
    """
    if not isinstance(lesson_id, str) or not lesson_id.strip():
        raise ValueError("lesson_id must be a non-empty string.")
    if not isinstance(score, int) or isinstance(score, bool):
        raise ValueError("score must be an integer.")
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise ValueError("total must be a positive integer.")
    if not 0 <= score <= total:
        raise ValueError("score must be between 0 and total.")

    moment = timestamp or _now()
    entry = state.setdefault(
        lesson_id.strip(),
        {
            "attempts": [],
            "best_score": 0,
            "best_total": 0,
            "best_percent": 0.0,
            "last_at": moment,
        },
    )

    entry["attempts"].append({"score": score, "total": total, "at": moment})

    percent = _percent(score, total)
    if percent >= entry["best_percent"]:
        entry["best_score"] = score
        entry["best_total"] = total
        entry["best_percent"] = percent
    entry["last_at"] = moment
    return state


def get_lesson_progress(state: dict, lesson_id: str) -> dict | None:
    """Return the stored progress entry for ``lesson_id``, or ``None``."""
    return state.get(lesson_id)


def summarize(state: dict) -> dict:
    """Return an aggregate summary across all practised lessons."""
    lessons_practised = len(state)
    total_attempts = sum(len(entry["attempts"]) for entry in state.values())
    percents = [
        entry["best_percent"] for entry in state.values() if entry["best_total"]
    ]
    average_best = round(sum(percents) / len(percents), 1) if percents else 0.0
    return {
        "lessons_practised": lessons_practised,
        "total_attempts": total_attempts,
        "average_best_percent": average_best,
    }
