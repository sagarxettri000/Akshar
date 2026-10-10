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


# ---------------------------------------------------------------------------
# Grounded Q&A tutor
# ---------------------------------------------------------------------------


def test_ask_question_rejects_empty_lesson():
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.ask_question("   ", "why?", "key")


def test_ask_question_rejects_empty_question():
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.ask_question("lesson", "   ", "key")


def test_ask_question_rejects_missing_api_key():
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.ask_question("lesson", "why?", "")


def test_ask_question_rejects_oversized_question():
    too_long = "x" * (ai_service.MAX_QUESTION_LENGTH + 1)
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.ask_question("lesson", too_long, "key")


def test_ask_question_rejects_unsupported_language():
    with pytest.raises(ai_service.InvalidInputError):
        ai_service.ask_question("lesson", "why?", "key", language="fr")


def test_ask_question_returns_trimmed_answer(monkeypatch):
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate("  Because F = m a.  "))
    assert ai_service.ask_question("lesson", "why?", "secret") == "Because F = m a."


def test_ask_question_rejects_empty_model_output(monkeypatch):
    monkeypatch.setattr(ai_service, "_generate_text", _fake_generate("   "))
    with pytest.raises(ai_service.AIGenerationError):
        ai_service.ask_question("lesson", "why?", "secret")


def test_clean_history_drops_malformed_entries():
    history = [
        {"role": "user", "content": "hi"},
        {"role": "system", "content": "ignored"},
        {"content": "missing role"},
        "not a dict",
        {"role": "assistant", "content": "   "},
    ]
    assert ai_service._clean_history(history) == [{"role": "user", "content": "hi"}]


def test_clean_history_caps_length():
    many = [{"role": "user", "content": str(i)} for i in range(20)]
    assert len(ai_service._clean_history(many)) == ai_service.MAX_HISTORY_MESSAGES


def test_ask_prompt_is_grounded_and_sets_language():
    prompt = ai_service._build_ask_prompt("LESSON BODY", "Why?", [], "ne")
    assert "ONLY the lesson below" in prompt
    assert "Nepali" in prompt
    assert "LESSON BODY" in prompt
    assert "Why?" in prompt
    assert ai_service.GROUNDED_DIRECTIVE in prompt


def test_forced_answer_language_replaces_the_match_the_lesson_rule():
    """A forced language must be stated as a rule, not silently ignored."""
    forced = ai_service._build_ask_prompt("LESSON BODY", "Why?", [], "ne")
    assert "- Write the answer in Nepali (Devanagari script)." in forced
    assert ai_service.MATCH_RESPONSE_LANGUAGE not in forced

    matched = ai_service._build_ask_prompt("LESSON BODY", "Why?", [], None)
    assert ai_service.MATCH_RESPONSE_LANGUAGE in matched
    assert "Write the answer in Nepali" not in matched


def test_ask_prompt_includes_prior_conversation():
    history = [{"role": "user", "content": "first"}, {"role": "assistant", "content": "reply"}]
    prompt = ai_service._build_ask_prompt("lesson", "second", history, None)
    assert "CONVERSATION SO FAR" in prompt
    assert "Student: first" in prompt
    assert "Tutor: reply" in prompt


# ---------------------------------------------------------------------------
# Secret handling and model-call errors
# ---------------------------------------------------------------------------


def test_redact_secret_masks_key():
    assert (
        ai_service._redact_secret("bad key secret123 rejected", "secret123")
        == "bad key *** rejected"
    )


def test_generate_text_redacts_api_key_in_errors(monkeypatch):
    class _Boom(Exception):
        pass

    class _Models:
        @staticmethod
        def generate_content(**kwargs):
            raise _Boom("request rejected for key secret-key-123")

    class _Client:
        models = _Models()

    monkeypatch.setattr(ai_service, "_build_client", lambda api_key: _Client())

    with pytest.raises(ai_service.AIGenerationError) as excinfo:
        ai_service._generate_text("prompt", "secret-key-123")

    assert "secret-key-123" not in str(excinfo.value)
    assert "***" in str(excinfo.value)
