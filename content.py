"""Lesson content loading and validation for Akshar.

Kept free of Streamlit imports so it can be unit tested and reused by the UI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

DEFAULT_LESSONS_PATH = Path(__file__).resolve().parent / "data" / "lessons.json"

REQUIRED_FIELDS = ("id", "track", "subject", "topic", "title", "language", "content")

LANGUAGE_LABELS = {"en": "English", "ne": "नेपाली (Nepali)"}


class ContentError(Exception):
    """Raised when lesson content is missing or malformed."""


def validate_lesson(item: Any) -> dict:
    """Validate a single lesson record and return a normalized copy."""
    if not isinstance(item, dict):
        raise ContentError("Each lesson must be a JSON object.")

    lesson: dict[str, str] = {}
    for field in REQUIRED_FIELDS:
        value = item.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ContentError(f"Lesson is missing a non-empty '{field}'.")
        lesson[field] = value.strip()
    return lesson


def load_lessons(path: str | Path = DEFAULT_LESSONS_PATH) -> list[dict]:
    """Load and validate lessons from ``path``."""
    path = Path(path)
    if not path.exists():
        raise ContentError(f"Lesson file not found: {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContentError(f"Lesson file is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("lessons"), list):
        raise ContentError("Lesson file must be an object with a 'lessons' list.")

    lessons = [validate_lesson(item) for item in raw["lessons"]]
    if not lessons:
        raise ContentError("Lesson file contains no lessons.")
    return lessons


def lessons_signature(path: str | Path = DEFAULT_LESSONS_PATH) -> str:
    """Return a cache-busting signature for the lesson file.

    Combines the file path with its modification time so that any cached
    lesson data is invalidated whenever the content on disk changes, even
    when the app process itself is not restarted.
    """
    target = Path(path)
    try:
        mtime = target.stat().st_mtime_ns
    except OSError:
        mtime = 0
    return f"{target}:{mtime}"


def unique_values(lessons: Iterable[dict], field: str) -> list[str]:
    """Return the distinct values of ``field`` in first-seen order."""
    seen: list[str] = []
    for lesson in lessons:
        value = lesson[field]
        if value not in seen:
            seen.append(value)
    return seen


def filter_lessons(
    lessons: Iterable[dict],
    track: str | None = None,
    subject: str | None = None,
    topic: str | None = None,
) -> list[dict]:
    """Return lessons matching the given (optional) filters."""
    result = list(lessons)
    if track is not None:
        result = [lesson for lesson in result if lesson["track"] == track]
    if subject is not None:
        result = [lesson for lesson in result if lesson["subject"] == subject]
    if topic is not None:
        result = [lesson for lesson in result if lesson["topic"] == topic]
    return result


def lesson_label(language: str) -> str:
    """Return a human-readable label for a language code."""
    return LANGUAGE_LABELS.get(language, language)
