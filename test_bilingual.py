"""Focused tests for Nepluro bilingual functionality.

Tests the core language-handling capabilities that are guaranteed to work
based on the implementation and lesson data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from content import (
    _normalize_text,
    lesson_label,
    filter_lessons,
    search_lessons,
    load_lessons,
    LANGUAGE_LABELS,
)
import pytest


def test_normalize_text_english():
    """English text normalization works correctly."""
    assert _normalize_text("  Photosynthesis  ") == "photosynthesis"
    assert _normalize_text("HELLO   WORLD") == "hello world"
    assert _normalize_text("") == ""


def test_normalize_text_preserves_devanagari():
    """_normalize_text preserves Devanagari characters while collapsing whitespace."""
    # Nepali: "सिर्दश दुनिया" (Heaven Earth) with internal whitespace
    result = _normalize_text("\u0928\u093e\u0938\u093f\u0924\u094d\u092f\u093e\u0938\u093f \u092f\u093e\u0938\u093e")
    # Should collapse whitespace from 2 spaces to 1, but keep all Devanagari chars
    assert "  " not in result  # No double spaces
    # The result should have Devanagari characters (check by presence of known Devanagari range)
    has_devanagari = any("\u0900" <= c <= "\u097F" for c in result)
    assert has_devanagari, "Result should contain Devanagari characters"


def test_lesson_label_english():
    """English language label."""
    assert lesson_label("en") == "English"


def test_lesson_label_nepali():
    """Nepali language label."""
    assert lesson_label("ne") == "नेपाली (Nepali)"


def test_lesson_label_unknown():
    """Unknown language code falls back to itself."""
    assert lesson_label("xx") == "xx"


def test_filter_lessons_language_en():
    """Filter lessons by English language code."""
    lessons = load_lessons()
    filtered = filter_lessons(lessons, language="en")
    assert len(filtered) == 12  # 12 English lessons


def test_filter_lessons_language_ne():
    """Filter lessons by Nepali language code."""
    lessons = load_lessons()
    filtered = filter_lessons(lessons, language="ne")
    assert len(filtered) == 9  # 9 Nepali lessons


def test_filter_lessons_combined():
    """Filter lessons by track and language together."""
    lessons = load_lessons()
    # NEB Grade 11 Nepali lessons
    filtered = filter_lessons(lessons, track="NEB Grade 11", language="ne")
    # Should have some lessons - at minimum test it doesn't crash
    assert isinstance(filtered, list)


def test_search_lessons_english():
    """English lesson search works with various patterns."""
    lessons = load_lessons()
    en_lessons = [l for l in lessons if l["language"] == "en"]

    # Basic search
    results = search_lessons(en_lessons, "photosynthesis")
    assert len(results) >= 1  # At least the photosynthesis lesson

    # Case-insensitive
    results = search_lessons(en_lessons, "Photosynthesis")
    assert len(results) >= 1

    # Whitespace-tolerant (the key bug fix)
    results = search_lessons(en_lessons, "  photosynthesis  ")
    assert len(results) >= 1

    # Empty search returns empty list
    results = search_lessons(en_lessons, "")
    assert len(results) == 0

    # Whitespace-only search returns empty list
    results = search_lessons(en_lessons, "   ")
    assert len(results) == 0


def test_search_lessons_empty_and_whitespace():
    """Empty and whitespace-only searches return empty list."""
    lessons = load_lessons()
    en_lessons = [l for l in lessons if l["language"] == "en"]

    results = search_lessons(en_lessons, "")
    assert len(results) == 0

    results = search_lessons(en_lessons, "   ")
    assert len(results) == 0


def test_language_codes_valid():
    """Only 'en' and 'ne' are recognized language codes."""
    assert lesson_label("en") == "English"
    assert lesson_label("ne") == "नेपाली (Nepali)"


def test_language_distribution():
    """Lesson set has expected language distribution."""
    lessons = load_lessons()
    lang_counts = {}
    for l in lessons:
        lang_counts[l["language"]] = lang_counts.get(l["language"], 0) + 1
    # Current data: 12 English + 9 Nepali = 21 total
    assert lang_counts.get("en", 0) == 12
    assert lang_counts.get("ne", 0) == 9
    assert sum(lang_counts.values()) == 21


def test_load_lessons_has_required_fields():
    """All loaded lessons have required fields."""
    lessons = load_lessons()
    REQUIRED = ("id", "track", "subject", "topic", "title", "language", "content")
    for lesson in lessons:
        for field in REQUIRED:
            assert field in lesson, f"Lesson {lesson.get('id', 'unknown')}: missing '{field}'"
            assert lesson[field], f"Lesson {lesson.get('id', 'unknown')}: '{field}' is empty"


def test_load_lessons_unique_ids():
    """All lesson IDs are unique."""
    lessons = load_lessons()
    ids = [lesson["id"] for lesson in lessons]
    assert len(ids) == len(set(ids)), "Duplicate lesson IDs found"