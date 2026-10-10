"""Tests for the Vercel web app in ``landing/``.

The web app is a second front end over the same content and the same Gemma 4
prompts as the Streamlit app. These tests keep the two honest:

* the lesson data served to the browser matches the Streamlit copy;
* the prompts sent to Gemma 4 are byte-identical across both front ends;
* the response validators agree on a shared corpus of model outputs;
* no secret value is committed anywhere under ``landing/``.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import ai_service

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "landing"
AI_MJS = LANDING / "api" / "ai.mjs"
NODE = shutil.which("node")

SECRET_PATTERNS = (
    re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"sk-[0-9A-Za-z]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def _run_node(script: str) -> object:
    """Run an ES module snippet that imports ``landing/api/ai.mjs``."""
    if not NODE:
        pytest.skip("node is not installed")
    completed = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout.strip().splitlines()[-1])


# --------------------------------------------------------------------------- #
# Content parity
# --------------------------------------------------------------------------- #


def test_browser_lesson_copy_matches_the_streamlit_copy():
    """The web app must serve exactly the lessons the Streamlit app uses."""
    shared = json.loads((ROOT / "data" / "lessons.json").read_text(encoding="utf-8"))
    served = json.loads((LANDING / "data" / "lessons.json").read_text(encoding="utf-8"))
    assert served == shared, "landing/data/lessons.json has drifted from data/lessons.json"


def test_served_lessons_cover_every_track_and_language():
    served = json.loads((LANDING / "data" / "lessons.json").read_text(encoding="utf-8"))
    lessons = served["lessons"]
    assert {"NEB Grade 11", "NEB Grade 12", "CEE", "IOE"} <= {l["track"] for l in lessons}
    assert {"en", "ne"} <= {l["language"] for l in lessons}


# --------------------------------------------------------------------------- #
# Prompt parity with ai_service.py
# --------------------------------------------------------------------------- #

LESSON = "Newton's second law: F = m a. Acceleration is proportional to net force."


def test_summary_mcq_and_flashcard_prompts_match_the_python_service():
    results = _run_node(
        f"""
        import {{ buildSummaryPrompt, buildMcqPrompt, buildFlashcardPrompt }} from 'file://{AI_MJS}';
        const lesson = {json.dumps(LESSON)};
        console.log(JSON.stringify({{
          summary: buildSummaryPrompt(lesson),
          mcq: buildMcqPrompt(lesson, 4),
          flashcards: buildFlashcardPrompt(lesson, 6),
        }}));
        """
    )
    assert results["summary"] == ai_service._build_summary_prompt(LESSON)
    assert results["mcq"] == ai_service._build_mcq_prompt(LESSON, 4)
    assert results["flashcards"] == ai_service._build_flashcard_prompt(LESSON, 6)


def test_ask_prompt_matches_the_python_service_including_history_and_language():
    history = [
        {"role": "user", "content": "What is force?"},
        {"role": "assistant", "content": "Force is mass times acceleration."},
    ]
    results = _run_node(
        f"""
        import {{ buildAskPrompt }} from 'file://{AI_MJS}';
        const lesson = {json.dumps(LESSON)};
        const history = {json.dumps(history)};
        console.log(JSON.stringify({{
          match: buildAskPrompt(lesson, 'Why?', [], null),
          nepali: buildAskPrompt(lesson, 'Why?', history, 'ne'),
        }}));
        """
    )
    assert results["match"] == ai_service._build_ask_prompt(LESSON, "Why?", [], None)
    assert results["nepali"] == ai_service._build_ask_prompt(LESSON, "Why?", history, "ne")


# --------------------------------------------------------------------------- #
# Validator parity
# --------------------------------------------------------------------------- #

MCQ_CASES = [
    {
        "question": "Q?",
        "options": {"a": " one ", "B": "two", "c": "three", "d": "four"},
        "answer": "a",
        "explanation": " because ",
    },
    {"question": "Q?", "options": {"A": "1", "B": "2", "C": "3"}, "answer": "A", "explanation": "x"},
    {"question": "Q?", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "answer": "E", "explanation": "x"},
    {"question": "Q?", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "answer": "A", "explanation": "  "},
    {"question": "", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "answer": "A", "explanation": "x"},
    "not-an-object",
]

FLASHCARD_CASES = [
    {"question": " Q ", "answer": " A "},
    {"question": "Q"},
    {"answer": "A"},
    {"question": "  ", "answer": "A"},
    7,
]

PARSING_CASES = [
    '[{"a": 1}]',
    '```json\n[{"a": 1}]\n```',
    'Here you go:\n[{"a": 1}]\nHope that helps.',
    '{"a": 1}',
    "   ",
    "no json at all",
]


def _python_mcq_result(case):
    try:
        return ai_service.validate_mcq(case)
    except ai_service.AIResponseError:
        return "rejected"


def _python_flashcard_result(case):
    try:
        return ai_service.validate_flashcard(case)
    except ai_service.AIResponseError:
        return "rejected"


def _python_parse_result(text):
    try:
        return ai_service.parse_json_response(text)
    except ai_service.AIResponseError:
        return "rejected"


def test_mcq_validation_agrees_between_python_and_javascript():
    results = _run_node(
        f"""
        import {{ validateMcq }} from 'file://{AI_MJS}';
        const cases = {json.dumps(MCQ_CASES)};
        const out = cases.map((item) => {{
          try {{ return validateMcq(item); }} catch (error) {{ return 'rejected'; }}
        }});
        console.log(JSON.stringify(out));
        """
    )
    assert results == [_python_mcq_result(case) for case in MCQ_CASES]


def test_flashcard_validation_agrees_between_python_and_javascript():
    results = _run_node(
        f"""
        import {{ validateFlashcard }} from 'file://{AI_MJS}';
        const cases = {json.dumps(FLASHCARD_CASES)};
        const out = cases.map((item) => {{
          try {{ return validateFlashcard(item); }} catch (error) {{ return 'rejected'; }}
        }});
        console.log(JSON.stringify(out));
        """
    )
    assert results == [_python_flashcard_result(case) for case in FLASHCARD_CASES]


def test_json_parsing_agrees_between_python_and_javascript():
    results = _run_node(
        f"""
        import {{ parseJsonResponse }} from 'file://{AI_MJS}';
        const cases = {json.dumps(PARSING_CASES)};
        const out = cases.map((text) => {{
          try {{ return parseJsonResponse(text); }} catch (error) {{ return 'rejected'; }}
        }});
        console.log(JSON.stringify(out));
        """
    )
    assert results == [_python_parse_result(text) for text in PARSING_CASES]


# --------------------------------------------------------------------------- #
# Deployment wiring and secrets
# --------------------------------------------------------------------------- #


def test_vercel_config_exposes_the_function_and_security_headers():
    config = json.loads((LANDING / "vercel.json").read_text(encoding="utf-8"))
    assert "api/gemma.mjs" in config["functions"]
    assert config["functions"]["api/gemma.mjs"]["maxDuration"] >= 30
    header_keys = {
        header["key"] for entry in config["headers"] for header in entry["headers"]
    }
    assert {"X-Content-Type-Options", "Referrer-Policy", "X-Frame-Options"} <= header_keys


def test_the_api_reads_the_key_from_the_server_environment_only():
    source = (LANDING / "api" / "gemma.mjs").read_text(encoding="utf-8")
    assert "process.env.GOOGLE_API_KEY" in source
    # The handler must never hand the key back to the browser.
    assert "apiKey," not in source.replace("const base = { apiKey };", "")


def test_no_secret_values_are_committed_under_landing():
    offenders = []
    for path in LANDING.rglob("*"):
        if not path.is_file() or path.suffix in {".png", ".jpg", ".woff", ".woff2"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"possible secrets committed: {offenders}"


def test_the_browser_bundle_never_contains_a_key_value():
    """app.js may name the variable, but must not carry a credential."""
    source = (LANDING / "app.js").read_text(encoding="utf-8")
    assert "x-goog-api-key" not in source
    assert "generativelanguage.googleapis.com" not in source
