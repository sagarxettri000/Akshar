"""Unit tests for :mod:`ai_service`.

These tests never call the live Gemma 4 API. They either exercise the pure
parsing/validation helpers directly or replace ``_generate_text`` with a fake.
"""

import json
import sys
from pathlib import Path

import pytest

# Allow ``import ai_service`` when pytest is run from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ai_service  # noqa: E402


VALID_MCQ = {
    "question": "What is 2 + 2?",
    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
    "answer": "B",
    "explanation": "2 + 2 equals 4.",
}

VALID_CARD = {
    "question": "What is photosynthesis?",
    "answer": "The process plants use to make food from sunlight.",
}


def _fake_generate(text):
    """Return a ``_generate_text`` replacement that always yields ``text``."""
    return lambda prompt, api_key: text


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def test_generate_summary_rejects_empty_lesson():
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.generate_summary("   ", "key")


def test_generate_summary_rejects_missing_api_key():
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.generate_summary("some lesson", "")


def test_generate_mcqs_rejects_invalid_count():
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.generate_mcqs("lesson", "key", count=0)


def test_generate_flashcards_rejects_non_integer_count():
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.generate_flashcards("lesson", "key", count="5")


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------


def test_parse_json_response_accepts_plain_array():
    assert ai_service.parse_json_response('[{"a": 1}]') == [{"a": 1}]


def test_parse_json_response_strips_code_fence():
    text = '```json\n[{"a": 1}]\n```'
    assert ai_service.parse_json_response(text) == [{"a": 1}]


def test_parse_json_response_extracts_json_from_prose():
    text = 'Here you go:\n[{"a": 1}]\nHope that helps!'
    assert ai_service.parse_json_response(text) == [{"a": 1}]


def test_parse_json_response_rejects_empty_text():
    with pytest.raises(ai_service.AIResponseError):
        ai_service.parse_json_response("")


def test_parse_json_response_rejects_invalid_json():
    with pytest.raises(ai_service.AIResponseError):
        ai_service.parse_json_response("this is not json")


# ---------------------------------------------------------------------------
# MCQ validation
# ---------------------------------------------------------------------------


def test_validate_mcq_accepts_valid_question():
    result = ai_service.validate_mcq(VALID_MCQ)
    assert result["answer"] == "B"
    assert result["options"] == {"A": "3", "B": "4", "C": "5", "D": "6"}
    assert list(result["options"]) == ["A", "B", "C", "D"]


def test_validate_mcq_normalizes_lowercase_keys_and_answer():
    item = {
        "question": "  Question?  ",
        "options": {"a": "1", "b": "2", "c": "3", "d": "4"},
        "answer": " b ",
        "explanation": "  because  ",
    }
    result = ai_service.validate_mcq(item)
    assert result["answer"] == "B"
    assert result["options"] == {"A": "1", "B": "2", "C": "3", "D": "4"}
    assert result["question"] == "Question?"
    assert result["explanation"] == "because"


def test_validate_mcq_rejects_missing_option():
    item = dict(VALID_MCQ, options={"A": "3", "B": "4", "C": "5"})
    with pytest.raises(ai_service.AIResponseError):
        ai_service.validate_mcq(item)


def test_validate_mcq_rejects_out_of_range_answer():
    item = dict(VALID_MCQ, answer="E")
    with pytest.raises(ai_service.AIResponseError):
        ai_service.validate_mcq(item)


def test_validate_mcq_rejects_missing_explanation():
    item = dict(VALID_MCQ, explanation="  ")
    with pytest.raises(ai_service.AIResponseError):
        ai_service.validate_mcq(item)


def test_validate_mcq_rejects_non_dict():
    with pytest.raises(ai_service.AIResponseError):
        ai_service.validate_mcq("not a dict")


def test_validate_mcqs_skips_malformed_entries():
    items = [VALID_MCQ, {"question": ""}, {"answer": "Z"}]
    result = ai_service.validate_mcqs(items)
    assert len(result) == 1
    assert result[0]["answer"] == "B"


def test_validate_mcqs_rejects_non_list():
    with pytest.raises(ai_service.AIResponseError):
        ai_service.validate_mcqs({"not": "a list"})


def test_validate_mcqs_rejects_all_invalid():
    with pytest.raises(ai_service.AIResponseError):
        ai_service.validate_mcqs([{"question": ""}])


# ---------------------------------------------------------------------------
# Flashcard validation
# ---------------------------------------------------------------------------


def test_validate_flashcard_accepts_valid_card():
    assert ai_service.validate_flashcard(VALID_CARD) == VALID_CARD


def test_validate_flashcard_trims_whitespace():
    result = ai_service.validate_flashcard(
        {"question": "  q  ", "answer": "  a  "}
    )
    assert result == {"question": "q", "answer": "a"}


def test_validate_flashcard_rejects_empty_answer():
    with pytest.raises(ai_service.AIResponseError):
        ai_service.validate_flashcard({"question": "q", "answer": "   "})


def test_validate_flashcards_rejects_all_invalid():
    with pytest.raises(ai_service.AIResponseError):
        ai_service.validate_flashcards([{"question": "only question"}])


# ---------------------------------------------------------------------------
# Public functions with a faked model call
# ---------------------------------------------------------------------------


def test_generate_summary_returns_trimmed_text(monkeypatch):
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate("  A summary.  "))
    assert ai_service.generate_summary("lesson text", "secret") == "A summary."


def test_generate_summary_rejects_empty_model_output(monkeypatch):
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate("   "))
    with pytest.raises(ai_service.AIGenerationError):
        ai_service.generate_summary("lesson text", "secret")


def test_generate_mcqs_parses_and_validates(monkeypatch):
    payload = json.dumps([VALID_MCQ])
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate(payload))
    result = ai_service.generate_mcqs("lesson", "secret", count=5)
    assert len(result) == 1
    assert result[0]["answer"] == "B"


def test_generate_mcqs_trims_to_requested_count(monkeypatch):
    payload = json.dumps([VALID_MCQ, VALID_MCQ, VALID_MCQ])
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate(payload))
    result = ai_service.generate_mcqs("lesson", "secret", count=2)
    assert len(result) == 2


def test_generate_mcqs_raises_on_invalid_json(monkeypatch):
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate("not json"))
    with pytest.raises(ai_service.AIResponseError):
        ai_service.generate_mcqs("lesson", "secret")


def test_generate_flashcards_parses_fenced_json(monkeypatch):
    payload = "```json\n" + json.dumps([VALID_CARD]) + "\n```"
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate(payload))
    result = ai_service.generate_flashcards("lesson", "secret", count=3)
    assert result == [VALID_CARD]


def test_generate_flashcards_raises_when_no_valid_cards(monkeypatch):
    payload = json.dumps([{"question": "only a question"}])
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate(payload))
    with pytest.raises(ai_service.AIResponseError):
        ai_service.generate_flashcards("lesson", "secret")
