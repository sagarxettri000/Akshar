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


def _matches_filter(lesson: dict, filter_key: str, filter_value: str) -> bool:
    """Check if a lesson matches a single key/value filter.

    Handles case-insensitive matching and whitespace normalization so that
    UI filter choices compose correctly regardless of subtle formatting
    differences in the lesson data.
    """
    lesson_value = lesson.get(filter_key, "").strip().lower()
    return lesson_value == filter_value.strip().lower()


def filter_lessons(
    lessons: Iterable[dict],
    track: str | None = None,
    subject: str | None = None,
    topic: str | None = None,
    language: str | None = None,
) -> list[dict]:
    """Return lessons matching the given (optional) filters.

    Supported filters (all optional):
    - ``track``   : exam track (e.g. "NEB Grade 11", "CEE", "IOE")
    - ``subject`` : subject name (e.g. "Physics", "Chemistry", "Biology", "Mathematics")
    - ``topic``   : lesson topic (e.g. "Kinematics", "Photosynthesis")
    - ``language``: language code ("en" or "ne")

    All filters compose together — only lessons matching every supplied
    filter are returned.  Matching is case- and whitespace-tolerant.
    """
    result = list(lessons)
    if track is not None:
        result = [lesson for lesson in result if _matches_filter(lesson, "track", track)]
    if subject is not None:
        result = [lesson for lesson in result if _matches_filter(lesson, "subject", subject)]
    if topic is not None:
        result = [lesson for lesson in result if _matches_filter(lesson, "topic", topic)]
    if language is not None:
        result = [lesson for lesson in result if _matches_filter(lesson, "language", language)]
    return result


def _normalize_text(text: str) -> str:
    """Normalize text for case- and whitespace-tolerant comparison.

    - Strips leading/trailing whitespace.
    - Folds to lowercase.
    - Collapses internal runs of whitespace to a single space.
    This lets a user type "photosynthesis" and match "Photosynthesis" or
    "  photosynthesis  " without needing exact string matches.
    """
    import re
    return re.sub(r"\\s+", " ", text.strip().lower())


def search_lessons(
    lessons: Iterable[dict],
    query: str,
    fields: tuple[str, ...] = ("title", "topic", "content"),
) -> list[dict]:
    """Return lessons whose specified fields match *query*.

    The query is matched against each lesson's values in ``fields`` using
    normalized (case-insensitive, whitespace-collapsed) text comparison,
    so ``search_lessons(lessons, "photosynthesis")`` will match a lesson
    with topic ``"Photosynthesis"`` or content containing the word.

    Parameters
    - ``lessons``: iterable of lesson dicts (validated lesson records).
    - ``query``: search string typed by the user.
    - ``fields``: which lesson fields to search.  Defaults to ``("title",
      "topic", "content") `` — the most discoverable fields.

    Returns lessons that match *any* of the specified fields.  If *query* is
    empty or whitespace-only, an empty list is returned (callers should show
    a helpful message).
    """
    q = _normalize_text(query)
    if not q:
        return []

    matched: list[dict] = []
    seen: set[str] = set()
    for lesson in lessons:
        for field in fields:
            value = lesson.get(field, "")
            if not isinstance(value, str):
                continue
            if q in _normalize_text(value):
                if lesson["id"] not in seen:
                    seen.add(lesson["id"])
                    matched.append(lesson)
                break
    return matched


def lesson_label(language: str) -> str:
    """Return a human-readable label for a language code."""
    return LANGUAGE_LABELS.get(language, language)


def resolve_study_path(
    lessons: Iterable[dict],
    track: str | None = None,
    subject: str | None = None,
    topic: str | None = None,
    language: str | None = None,
) -> dict:
    """Coerce a cascading track/subject/topic/language choice into a real lesson.

    Each level falls back to the first value available under its chosen parent.
    Without this, changing a parent selection can leave a child pointing at a
    value that no longer exists — which previously produced an empty lesson list
    and crashed the app with ``StopIteration``.

    Returns ``{"track", "subject", "topic", "language", "variants", "lesson"}``.
    ``lesson`` is ``None`` only when ``lessons`` is empty.
    """
    lessons = list(lessons)
    if not lessons:
        return {
            "track": None,
            "subject": None,
            "topic": None,
            "language": None,
            "variants": [],
            "lesson": None,
        }

    def pick(options: list[str], value: str | None) -> str:
        return value if value in options else options[0]

    chosen_track = pick(unique_values(lessons, "track"), track)
    chosen_subject = pick(
        unique_values(filter_lessons(lessons, track=chosen_track), "subject"), subject
    )
    chosen_topic = pick(
        unique_values(
            filter_lessons(lessons, track=chosen_track, subject=chosen_subject), "topic"
        ),
        topic,
    )
    variants = filter_lessons(
        lessons, track=chosen_track, subject=chosen_subject, topic=chosen_topic
    )
    chosen_language = pick(unique_values(variants, "language"), language)
    lesson = next(
        (item for item in variants if item["language"] == chosen_language), variants[0]
    )
    return {
        "track": chosen_track,
        "subject": chosen_subject,
        "topic": chosen_topic,
        "language": chosen_language,
        "variants": variants,
        "lesson": lesson,
    }
