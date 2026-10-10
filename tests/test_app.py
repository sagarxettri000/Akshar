"""End-to-end UI tests for the Streamlit app.

Gemma 4 is replaced by a deterministic fake, so these tests drive the real
widget states — first run, generated content, graded feedback, recoverable
errors, and cascading study-path changes — without any live model call.
"""

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ai_service  # noqa: E402

APP = str(Path(__file__).resolve().parents[1] / "app.py")

FAKE_SUMMARY = "A short summary of the lesson."
FAKE_CARDS = [
    {"question": f"Card question {index}?", "answer": f"Card answer {index}."}
    for index in range(1, 5)
]
FAKE_MCQS = [
    {
        "question": f"Question {letter}?",
        "options": {"A": "alpha", "B": "beta", "C": "gamma", "D": "delta"},
        "answer": "B",
        "explanation": f"Because beta is right for question {letter}.",
    }
    for letter in ("One", "Two", "Three")
]


def start(monkeypatch, api_key="test-key"):
    """Run the app once, with or without a (fake) API key configured."""
    if api_key is None:
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    else:
        monkeypatch.setenv("GOOGLE_API_KEY", api_key)
    at = AppTest.from_file(APP, default_timeout=90)
    at.run()
    return at


def failures(at):
    return [getattr(item, "value", str(item)) for item in at.exception]


def markdown_html(at):
    """Every rendered HTML/markdown block except the injected stylesheet."""
    return "\n".join(
        block.value for block in at.markdown if "<style>" not in block.value
    )


# ---------------------------------------------------------------------------
# First run
# ---------------------------------------------------------------------------


def test_first_run_renders_the_study_journey_without_an_api_key(monkeypatch):
    at = start(monkeypatch, api_key=None)
    assert not failures(at)

    assert [box.label for box in at.selectbox[:4]] == [
        "Track",
        "Subject",
        "Topic",
        "Language",
    ]
    assert [tab.label for tab in at.tabs] == ["Explain", "Ask Gemma 4", "Practise", "Flashcards"]

    page = markdown_html(at)
    assert "akx-masthead" in page, "product masthead is missing"
    assert "akx-path" in page, "curriculum breadcrumb is missing"
    # Lesson titles are escaped before they reach raw HTML.
    assert "Newton&#x27;s Second Law" in page or "Newton's Second Law" in page
    assert "ai_disclosure" not in page and "akx-note--ai" in page, "AI output is not labelled"
    assert "No Gemma 4 API key found" in page, "missing-key state is not explained"

    # Every model-backed action is disabled rather than failing after a click.
    model_buttons = [
        button
        for button in at.button
        if button.label
        in {
            "Summarise the lesson",
            "Ask Gemma 4",
            "Write practice questions",
            "Write flashcards",
        }
    ]
    assert model_buttons, "expected model-backed actions on the page"
    assert all(button.disabled for button in model_buttons)


def test_heading_outline_has_no_skips(monkeypatch):
    """One h1, starting there, and no level jumps (h1 -> h3 etc.)."""
    import re

    at = start(monkeypatch)
    levels = [int(level) for level in re.findall(r"<h([1-6])\b", markdown_html(at))]
    assert levels.count(1) == 1, f"expected exactly one h1, got {levels}"
    assert levels[0] == 1, f"the first heading must be the h1, got {levels}"
    for previous, current in zip(levels, levels[1:]):
        assert current <= previous + 1, f"heading levels jump: {previous} -> {current} in {levels}"


def test_switching_track_refreshes_the_whole_path(monkeypatch):
    """Regression: changing a parent selection used to leave the app empty.

    Streamlit hands back the *stale* raw value for a child selectbox when the
    options change, which previously produced an empty lesson list and a
    StopIteration crash. content.resolve_study_path owns the fallback, so the
    app must always show a real lesson.
    """
    at = start(monkeypatch)
    at.selectbox(key="path-track").set_value("IOE").run()
    assert not failures(at)
    page = markdown_html(at)
    assert "Quadratic Equations" in page
    assert at.selectbox(key="path-subject").value == "Mathematics"

    # Move to a track whose subject/topic/language names are all different.
    at.selectbox(key="path-track").set_value("CEE").run()
    assert not failures(at)
    page = markdown_html(at)
    assert "Equations of Motion" in page
    assert at.selectbox(key="path-topic").value == "Kinematics"
    assert at.selectbox(key="path-language").value == "en"


def test_explain_tab_shows_the_summary_it_just_generated(monkeypatch):
    monkeypatch.setattr(ai_service, "generate_summary", lambda *a, **k: FAKE_SUMMARY)
    at = start(monkeypatch)
    at.button(key="gen-summary::phy-newton-2-en").click().run()

    assert not failures(at)
    page = markdown_html(at)
    assert FAKE_SUMMARY in page
    assert "akx-note--ai" in page, "the summary must be labelled as AI-generated"
    assert "Akshar · Gemma 4" in page


def test_flashcard_tab_shows_cards_immediately_after_generating(monkeypatch):
    monkeypatch.setattr(ai_service, "generate_flashcards", lambda *a, **k: list(FAKE_CARDS))
    at = start(monkeypatch)
    at.button(key="gen-fc::phy-newton-2-en").click().run()

    assert not failures(at)
    assert [expander.label for expander in at.expander][1:] == [
        f"Card {index} · Card question {index}?" for index in range(1, 5)
    ]
    assert "No flashcards yet" not in markdown_html(at)


# ---------------------------------------------------------------------------
# Practice: generate -> answer -> grade -> record
# ---------------------------------------------------------------------------


def test_practice_flow_generates_grades_and_records_progress(monkeypatch):
    monkeypatch.setattr(ai_service, "generate_mcqs", lambda *a, **k: list(FAKE_MCQS))
    at = start(monkeypatch)

    at.button(key="gen-mcq::phy-newton-2-en").click().run()
    assert not failures(at)
    assert len(at.radio) == 3, "expected one answer group per generated question"
    assert "Check my answers" in [button.label for button in at.button]

    # Radios live inside a form: set the choices and submit in one pass.
    # AppTest takes the *formatted* option label, which is what the browser sends.
    at.radio(key="mcq-ans::phy-newton-2-en::1::1").set_value("B. beta")
    at.radio(key="mcq-ans::phy-newton-2-en::1::2").set_value("B. beta")
    at.radio(key="mcq-ans::phy-newton-2-en::1::3").set_value("A. alpha")
    next(button for button in at.button if button.label == "Check my answers").click().run()
    assert not failures(at)

    page = markdown_html(at)
    assert "akx-score" in page and "2 / 3" in page, "score summary is missing"
    assert page.count("akx-result") >= 3, "expected one graded row per question"
    assert "Correct" in page and "Not quite" in page
    assert "Because beta is right" in page, "explanations are missing"
    # The answer form is hidden once graded, so each row must repeat its question.
    assert "Question One?" in page and "Question Three?" in page

    recorded = at.session_state["progress"]["phy-newton-2-en"]
    assert recorded["best_score"] == 2 and recorded["best_total"] == 3
    assert len(recorded["attempts"]) == 1

    # Graded feedback survives the next rerun instead of vanishing.
    at.run()
    assert "2 / 3" in markdown_html(at)
    assert "Session best for this lesson: 2 / 3" in markdown_html(at)


def test_practice_grading_uses_the_answer_key(monkeypatch):
    """A wrong selection must not be scored as correct."""
    monkeypatch.setattr(ai_service, "generate_mcqs", lambda *a, **k: list(FAKE_MCQS))
    at = start(monkeypatch)
    at.button(key="gen-mcq::phy-newton-2-en").click().run()
    at.radio(key="mcq-ans::phy-newton-2-en::1::1").set_value("D. delta")
    next(button for button in at.button if button.label == "Check my answers").click().run()
    assert not failures(at)
    page = markdown_html(at)
    assert "0 / 3" in page
    assert "The correct answer is B. beta." in page


def test_practice_generation_failure_is_reported_honestly(monkeypatch):
    def boom(*args, **kwargs):
        raise ai_service.AIGenerationError("The Gemma 4 request failed.")

    monkeypatch.setattr(ai_service, "generate_mcqs", boom)
    at = start(monkeypatch)
    at.button(key="gen-mcq::phy-newton-2-en").click().run()

    assert not failures(at)
    page = markdown_html(at)
    assert "Could not write questions" in page
    assert "akx-note--danger" in page
    assert "akx-score" not in page, "a failed call must not render fake results"


# ---------------------------------------------------------------------------
# Ask: grounded answer and a recoverable error
# ---------------------------------------------------------------------------


def test_ask_shows_answer_with_ai_provenance(monkeypatch):
    monkeypatch.setattr(
        ai_service,
        "ask_question",
        lambda lesson, question, key, history=None, language=None: "Acceleration is "
        "inversely proportional to mass.",
    )
    at = start(monkeypatch)
    at.button(key="ask-suggest::phy-newton-2-en::0").click().run()

    assert not failures(at)
    page = markdown_html(at)
    assert "Your question" in page and "Akshar · Gemma 4" in page
    assert "inversely proportional to mass" in page
    assert "AI-generated answers" in page


def test_ask_failure_is_recoverable(monkeypatch):
    def boom(*args, **kwargs):
        raise ai_service.AIGenerationError("The Gemma 4 request failed: timeout.")

    monkeypatch.setattr(ai_service, "ask_question", boom)
    at = start(monkeypatch)
    at.button(key="ask-suggest::phy-newton-2-en::0").click().run()

    assert not failures(at)
    page = markdown_html(at)
    assert "Could not answer" in page and "timeout" in page
    assert "Try that question again" in [button.label for button in at.button]
