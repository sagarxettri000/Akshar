"""Gemma 4 AI service for Akshar.

This module is the single integration point between the Akshar app and Google's
hosted Gemma 4 model. The rest of the app imports three functions:

    generate_summary(lesson_text, api_key) -> str
    generate_mcqs(lesson_text, api_key, count=5) -> list[dict]
    generate_flashcards(lesson_text, api_key, count=5) -> list[dict[str, str]]

Model output is treated as untrusted: JSON is parsed defensively and every
question/flashcard is validated before it is returned. The module never logs or
returns the API key.

Model: ``gemma-4-26b-a4b-it`` via the official ``google-genai`` SDK.
Docs: https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api
"""

from __future__ import annotations

import json
import logging
from typing import Any

__all__ = [
    "AIServiceError",
    "InvalidInputError",
    "AIGenerationError",
    "AIResponseError",
    "MODEL_ID",
    "DEFAULT_MCQ_COUNT",
    "DEFAULT_FLASHCARD_COUNT",
    "generate_summary",
    "generate_mcqs",
    "generate_flashcards",
    "parse_json_response",
    "validate_mcq",
    "validate_mcqs",
    "validate_flashcard",
    "validate_flashcards",
]

logger = logging.getLogger(__name__)

# Official Gemma 4 model ID, verified against the Google AI docs.
MODEL_ID = "gemma-4-26b-a4b-it"
DEFAULT_MCQ_COUNT = 5
DEFAULT_FLASHCARD_COUNT = 5
OPTION_KEYS = ("A", "B", "C", "D")


class AIServiceError(Exception):
    """Base class for every error raised by this module."""


class InvalidInputError(AIServiceError):
    """The caller supplied invalid input (for example an empty lesson)."""


class AIGenerationError(AIServiceError):
    """The model call failed or returned nothing usable."""


class AIResponseError(AIServiceError):
    """The model response could not be parsed or failed validation."""


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------


def _clean_lesson_text(lesson_text: str) -> str:
    """Return validated, trimmed lesson text or raise ``InvalidInputError``."""
    if not isinstance(lesson_text, str) or not lesson_text.strip():
        raise InvalidInputError("lesson_text must be a non-empty string.")
    return lesson_text.strip()


def _clean_api_key(api_key: str) -> str:
    """Return a validated API key or raise ``InvalidInputError``.

    The key is never logged or included in an error message.
    """
    if not isinstance(api_key, str) or not api_key.strip():
        raise InvalidInputError("api_key must be a non-empty string.")
    return api_key.strip()


def _clean_count(count: int) -> int:
    """Return a validated item count or raise ``InvalidInputError``."""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise InvalidInputError("count must be a positive integer.")
    return count


def _redact_secret(message: str, secret: str) -> str:
    """Return ``message`` with any occurrence of ``secret`` masked."""
    if secret and secret in message:
        return message.replace(secret, "***")
    return message


# ---------------------------------------------------------------------------
# Response parsing and validation
# ---------------------------------------------------------------------------


def _strip_code_fences(text: str) -> str:
    """Remove a wrapping Markdown code fence (triple backticks) if present."""
    cleaned = text.strip()
    if not cleaned.startswith("```"):
        return cleaned

    lines = cleaned.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _extract_json_snippet(text: str) -> str | None:
    """Return the first bracketed JSON block found in ``text``, if any."""
    for open_char, close_char in (("[", "]"), ("{", "}")):
        start = text.find(open_char)
        end = text.rfind(close_char)
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
    return None


def parse_json_response(text: str) -> Any:
    """Parse a model response that should contain JSON.

    Handles a bare JSON value, a fenced code block, or JSON wrapped in a little
    prose. Raises ``AIResponseError`` when no valid JSON can be found.
    """
    if not isinstance(text, str) or not text.strip():
        raise AIResponseError("The model returned an empty response.")

    cleaned = _strip_code_fences(text)
    for candidate in (cleaned, _extract_json_snippet(cleaned)):
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise AIResponseError("The model response was not valid JSON.")


def validate_mcq(item: Any) -> dict:
    """Validate one multiple-choice question and return a normalized copy."""
    if not isinstance(item, dict):
        raise AIResponseError("Each MCQ must be a JSON object.")

    question = item.get("question")
    if not isinstance(question, str) or not question.strip():
        raise AIResponseError("MCQ is missing a non-empty 'question'.")

    raw_options = item.get("options")
    if not isinstance(raw_options, dict):
        raise AIResponseError("MCQ 'options' must be an object with keys A, B, C, D.")

    found: dict[str, str] = {}
    for raw_key, raw_value in raw_options.items():
        key = str(raw_key).strip().upper()
        if isinstance(raw_value, str) and raw_value.strip():
            found[key] = raw_value.strip()

    missing = [key for key in OPTION_KEYS if key not in found]
    if missing:
        raise AIResponseError(
            "MCQ options are incomplete; missing: " + ", ".join(missing) + "."
        )

    answer = item.get("answer")
    if not isinstance(answer, str) or answer.strip().upper() not in OPTION_KEYS:
        raise AIResponseError("MCQ 'answer' must be one of A, B, C, D.")

    explanation = item.get("explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        raise AIResponseError("MCQ is missing a non-empty 'explanation'.")

    return {
        "question": question.strip(),
        "options": {key: found[key] for key in OPTION_KEYS},
        "answer": answer.strip().upper(),
        "explanation": explanation.strip(),
    }


def validate_mcqs(items: Any) -> list[dict]:
    """Validate a list of MCQs, skipping malformed entries.

    Raises ``AIResponseError`` if the value is not a list or if no valid
    question remains. Skipped entries are logged without their raw content.
    """
    if not isinstance(items, list):
        raise AIResponseError("The model did not return a JSON list of questions.")

    valid: list[dict] = []
    for index, item in enumerate(items):
        try:
            valid.append(validate_mcq(item))
        except AIResponseError as exc:
            logger.warning("Skipping malformed MCQ at index %s: %s", index, exc)

    if not valid:
        raise AIResponseError("The model returned no valid multiple-choice questions.")
    return valid


def validate_flashcard(item: Any) -> dict[str, str]:
    """Validate one flashcard and return a normalized copy."""
    if not isinstance(item, dict):
        raise AIResponseError("Each flashcard must be a JSON object.")

    question = item.get("question")
    answer = item.get("answer")
    if not isinstance(question, str) or not question.strip():
        raise AIResponseError("Flashcard is missing a non-empty 'question'.")
    if not isinstance(answer, str) or not answer.strip():
        raise AIResponseError("Flashcard is missing a non-empty 'answer'.")

    return {"question": question.strip(), "answer": answer.strip()}


def validate_flashcards(items: Any) -> list[dict[str, str]]:
    """Validate a list of flashcards, skipping malformed entries."""
    if not isinstance(items, list):
        raise AIResponseError("The model did not return a JSON list of flashcards.")

    valid: list[dict[str, str]] = []
    for index, item in enumerate(items):
        try:
            valid.append(validate_flashcard(item))
        except AIResponseError as exc:
            logger.warning("Skipping malformed flashcard at index %s: %s", index, exc)

    if not valid:
        raise AIResponseError("The model returned no valid flashcards.")
    return valid


# ---------------------------------------------------------------------------
# Model access
# ---------------------------------------------------------------------------


def _build_client(api_key: str):
    """Create a Google GenAI client, importing the SDK lazily.

    The import is deferred so the validation and parsing helpers can be tested
    without the optional ``google-genai`` dependency installed.
    """
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise AIGenerationError(
            "The 'google-genai' package is required. Install it with: "
            "pip install google-genai"
        ) from exc
    return genai.Client(api_key=api_key)


def _extract_response_text(response: Any) -> str:
    """Pull text out of a GenAI response without assuming a single shape."""
    try:
        text = response.text
    except Exception:
        text = None
    if isinstance(text, str) and text.strip():
        return text.strip()

    for candidate in getattr(response, "candidates", None) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", None) or []:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str) and part_text.strip():
                return part_text.strip()
    return ""


def _generate_text(prompt: str, api_key: str) -> str:
    """Send one prompt to Gemma 4 and return its text response."""
    try:
        client = _build_client(api_key)
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    except AIServiceError:
        raise
    except Exception as exc:
        # Never include the API key in the raised message.
        raise AIGenerationError(
            "The Gemma 4 request failed: " + _redact_secret(str(exc), api_key)
        ) from exc

    text = _extract_response_text(response)
    if not text:
        raise AIGenerationError("The model returned an empty response.")
    return text


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


def _build_summary_prompt(lesson_text: str) -> str:
    return (
        "You are a careful tutor for Nepali students in Grade 11 and 12.\n"
        "Summarize the lesson below.\n"
        "Rules:\n"
        "- Use only the lesson provided. Do not add outside facts.\n"
        "- Keep important definitions, formulas, and key concepts.\n"
        "- Use short paragraphs or bullet points with clear language.\n"
        "- Write in the same language as the lesson (Nepali, English, or a mix).\n"
        "Return plain text only, with no preamble.\n\n"
        f"LESSON:\n{lesson_text}"
    )


def _build_mcq_prompt(lesson_text: str, count: int) -> str:
    return (
        "You are an exam-question writer for Nepali students in Grade 11 and 12.\n"
        f"Create exactly {count} multiple-choice questions based only on the lesson.\n"
        "Return ONLY a JSON array. Each element must be a JSON object with these keys:\n"
        '  "question": string,\n'
        '  "options": an object with string keys "A", "B", "C", "D" and string values,\n'
        '  "answer": one of "A", "B", "C", "D" (the single correct option),\n'
        '  "explanation": string explaining why the answer is correct.\n'
        "Rules:\n"
        "- Base every question strictly on the lesson. Do not invent facts.\n"
        "- Give exactly four options per question and only one correct answer.\n"
        "- Write in the same language as the lesson (Nepali, English, or a mix).\n"
        "- Return JSON only: no Markdown fences, comments, or extra text.\n\n"
        f"LESSON:\n{lesson_text}"
    )


def _build_flashcard_prompt(lesson_text: str, count: int) -> str:
    return (
        "You are a study-aid writer for Nepali students in Grade 11 and 12.\n"
        f"Create exactly {count} flashcards based only on the lesson.\n"
        "Return ONLY a JSON array. Each element must be a JSON object with these keys:\n"
        '  "question": string,\n'
        '  "answer": string.\n'
        "Rules:\n"
        "- Base every flashcard strictly on the lesson. Do not invent facts.\n"
        "- Keep each answer short and accurate.\n"
        "- Write in the same language as the lesson (Nepali, English, or a mix).\n"
        "- Return JSON only: no Markdown fences, comments, or extra text.\n\n"
        f"LESSON:\n{lesson_text}"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_summary(lesson_text: str, api_key: str) -> str:
    """Return a concise, faithful summary of ``lesson_text``.

    Raises ``InvalidInputError`` for bad input, ``AIGenerationError`` if the
    model call fails, and ``AIServiceError`` subclasses for unexpected issues.
    """
    lesson = _clean_lesson_text(lesson_text)
    key = _clean_api_key(api_key)

    summary = _generate_text(_build_summary_prompt(lesson), key).strip()
    if not summary:
        raise AIGenerationError("The model returned an empty summary.")
    return summary


def generate_mcqs(
    lesson_text: str, api_key: str, count: int = DEFAULT_MCQ_COUNT
) -> list[dict]:
    """Return validated multiple-choice questions based on ``lesson_text``."""
    lesson = _clean_lesson_text(lesson_text)
    key = _clean_api_key(api_key)
    count = _clean_count(count)

    raw = _generate_text(_build_mcq_prompt(lesson, count), key)
    questions = validate_mcqs(parse_json_response(raw))
    return questions[:count]


def generate_flashcards(
    lesson_text: str, api_key: str, count: int = DEFAULT_FLASHCARD_COUNT
) -> list[dict[str, str]]:
    """Return validated ``{question, answer}`` flashcards based on the lesson."""
    lesson = _clean_lesson_text(lesson_text)
    key = _clean_api_key(api_key)
    count = _clean_count(count)

    raw = _generate_text(_build_flashcard_prompt(lesson, count), key)
    cards = validate_flashcards(parse_json_response(raw))
    return cards[:count]
