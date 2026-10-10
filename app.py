"""Akshar — a Streamlit learning app powered by Gemma 4.

Flow: choose a track and topic -> read the study notes -> have Gemma 4 explain
them or answer questions about them -> practise and review.

Layering: presentation lives in :mod:`ui` (design tokens and shared blocks),
lesson data and selection logic live in :mod:`content`, session progress lives in
:mod:`progress`, and every model call goes through :mod:`ai_service`. Nothing
here talks to the model directly.
"""

from __future__ import annotations

import os

import streamlit as st

import ai_service
import progress
import ui
from ai_service import AIServiceError
from content import (
    ContentError,
    filter_lessons,
    lesson_label,
    lessons_signature,
    load_lessons,
    resolve_study_path,
    unique_values,
)

MCQ_COUNT = 3
FLASHCARD_COUNT = 4

ASK_LANGUAGE_OPTIONS = {
    "Auto (match the lesson)": None,
    "English": "en",
    "नेपाली (Nepali)": "ne",
}

SUGGESTED_QUESTIONS = (
    "Explain the main idea in simpler words.",
    "Work through one example step by step.",
    "What should I remember for the exam?",
)

SOURCE_NOTE = (
    "Team-authored study notes, written for the Akshar demo. Not official NEB, "
    "CEE, or IOE material, and no replacement for your textbook."
)
SUMMARY_NOTE = (
    "Written by Gemma 4 from the notes above, using only that text. It can be "
    "wrong — check it against the notes or your textbook."
)
PRACTICE_NOTE = (
    "Gemma 4 writes these from the notes above, so they are not official exam "
    "questions and the facts still need your judgement. Each set is checked for "
    "structure — four options, one marked answer, an explanation."
)
FLASHCARD_NOTE = (
    "Written by Gemma 4 from the notes above. A prompt for self-testing, not a "
    "summary you should memorise unchecked."
)
ASK_LEAD = (
    "Gemma 4 answers from the notes above only. When the notes do not cover "
    "something, it says so instead of inventing an answer."
)


# ---------------------------------------------------------------------------
# Data, configuration, and session state
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def get_lessons(signature: str) -> list[dict]:
    """Load lessons, re-reading them whenever ``signature`` changes.

    ``signature`` combines the lesson file path with its modification time, so
    editing ``data/lessons.json`` invalidates the cache without a restart.
    """
    return load_lessons()


def get_api_key() -> str | None:
    """Return the Gemma 4 API key from Streamlit secrets or the environment."""
    try:
        key = st.secrets["GOOGLE_API_KEY"]
        if key:
            return str(key)
    except Exception:
        # No secrets file configured, or the key is absent.
        pass
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")


def get_progress() -> dict:
    """Return this session's progress state, creating it on first use."""
    if "progress" not in st.session_state:
        st.session_state["progress"] = progress.new_state()
    return st.session_state["progress"]


def bump(key: str) -> int:
    """Return the current value of a counter and increment it.

    Counters are folded into widget keys so that regenerating a set of questions
    or clearing a question box produces fresh widgets with clean state.
    """
    value = int(st.session_state.get(key, 0))
    st.session_state[key] = value + 1
    return value


# ---------------------------------------------------------------------------
# Chrome: masthead, study path, lesson
# ---------------------------------------------------------------------------


def render_ai_status(api_key: str | None) -> None:
    """Explain a missing key before the learner meets a disabled button.

    Nothing is shown when Gemma 4 is available: the sidebar already reports the
    connection, and a second confirmation box would only add noise.
    """
    if not api_key:
        ui.note(
            "warning",
            "AI features are off",
            "No Gemma 4 API key found. Reading the study notes still works. To "
            "enable explanations and practice, add GOOGLE_API_KEY to "
            ".streamlit/secrets.toml or your environment, then reload the page.",
        )


def render_study_path(lessons: list[dict]) -> dict:
    """Render the cascading track pickers and return the reconciled selection."""
    ui.section_title("Choose what to study", level=2)
    track_col, subject_col, topic_col, language_col = st.columns([1, 0.95, 1.4, 1])

    with track_col:
        track = st.selectbox("Track", unique_values(lessons, "track"), key="path-track")

    subjects = unique_values(filter_lessons(lessons, track=track), "subject")
    with subject_col:
        subject = st.selectbox("Subject", subjects, key="path-subject")

    topics = unique_values(
        filter_lessons(lessons, track=track, subject=subject), "topic"
    )
    with topic_col:
        topic = st.selectbox("Topic", topics, key="path-topic")

    variants = filter_lessons(lessons, track=track, subject=subject, topic=topic)
    languages = unique_values(variants, "language")
    with language_col:
        language = st.selectbox(
            "Language",
            languages,
            format_func=lesson_label,
            key="path-language",
        )

    # Widgets can hand back a value that no longer exists under a new parent
    # (for example a topic from the previous track), so reconcile the path.
    return resolve_study_path(lessons, track, subject, topic, language)


def render_lesson(lesson: dict) -> None:
    """Breadcrumb, title, and the notes themselves with their provenance."""
    ui.lesson_header(
        [lesson["track"], lesson["subject"], lesson["topic"]],
        lesson["title"],
        [(lesson_label(lesson["language"]), False), ("Study notes", True)],
    )

    with st.expander("Study notes — the source for everything below", expanded=True):
        ui.prose(lesson["content"])
        ui.source_disclosure(SOURCE_NOTE, label=f"Source · {lesson_label(lesson['language'])}")


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------


def render_explain_tab(lesson: dict, api_key: str | None) -> None:
    """A grounded summary of the lesson, clearly marked as model output."""
    ui.section_title("Explain this lesson")
    st.markdown(
        "A short, faithful summary of the notes, in the same language as the "
        "lesson. Useful before you start practising."
    )

    state_key = f"summary::{lesson['id']}"
    summary = st.session_state.get(state_key)

    if st.button(
        "Summarise the lesson",
        key=f"gen-summary::{lesson['id']}",
        type="primary",
        disabled=not api_key,
        help=None if api_key else "Add a Gemma 4 API key to run this.",
    ):
        with st.spinner("Gemma 4 is reading the lesson…"):
            try:
                st.session_state[state_key] = ai_service.generate_summary(
                    lesson["content"], api_key
                )
                st.rerun()
            except AIServiceError as exc:
                ui.note("danger", "Could not write a summary", f"{exc}")

    if not summary:
        ui.empty_state(
            "Nothing generated yet",
            "Select “Summarise the lesson” and Gemma 4 will condense the notes "
            "above into a few short paragraphs.",
        )
        return

    ui.turn("assistant", summary, 0)
    ui.ai_disclosure(SUMMARY_NOTE, label="AI-generated summary")
    if st.button("Start over", key=f"regen-summary::{lesson['id']}"):
        st.session_state.pop(state_key, None)
        st.rerun()


def _ask(lesson: dict, question: str, language: str | None, api_key: str) -> None:
    """Ask Gemma 4 one question, recording the turn or a recoverable error."""
    history: list[dict] = st.session_state.setdefault(f"ask::{lesson['id']}", [])
    error_key = f"ask-error::{lesson['id']}"

    history.append({"role": "user", "content": question})
    with st.spinner("Gemma 4 is reading the notes and answering…"):
        try:
            answer = ai_service.ask_question(
                lesson["content"],
                question,
                api_key,
                history=history[:-1],
                language=language,
            )
            history.append({"role": "assistant", "content": answer})
            st.session_state.pop(error_key, None)
        except AIServiceError as exc:
            # The learner's question stays on screen; the failure is recoverable.
            st.session_state[error_key] = {"question": question, "message": str(exc)}
    st.rerun()


def render_ask_tab(lesson: dict, api_key: str | None) -> None:
    """The grounded tutor: question in, sourced answer out, errors recoverable."""
    ui.section_title("Ask about this lesson")
    st.markdown(ASK_LEAD)

    history: list[dict] = st.session_state.setdefault(f"ask::{lesson['id']}", [])
    error_key = f"ask-error::{lesson['id']}"
    nonce = int(st.session_state.get(f"ask-nonce::{lesson['id']}", 0))

    language_col, _ = st.columns([1, 1])
    with language_col:
        language_label = st.selectbox(
            "Answer language",
            list(ASK_LANGUAGE_OPTIONS),
            key=f"ask-lang::{lesson['id']}",
            help="Choose the language Gemma 4 should reply in.",
        )
    language = ASK_LANGUAGE_OPTIONS[language_label]

    if not history:
        ui.empty_state(
            "No questions yet",
            "Ask about anything in the notes above — a definition, a step in a "
            "worked example, or what is worth memorising.",
        )
        ui.section_title("Questions to start with")
        for index, suggestion in enumerate(SUGGESTED_QUESTIONS):
            if st.button(
                suggestion,
                key=f"ask-suggest::{lesson['id']}::{index}",
                disabled=not api_key,
                help=None if api_key else "Add a Gemma 4 API key to ask a question.",
            ):
                _ask(lesson, suggestion, language, api_key)

    for index, message in enumerate(history):
        ui.turn(message["role"], message["content"], index)

    if history:
        ui.ai_disclosure(
            "Answers are generated by Gemma 4 from the notes above and can be "
            "wrong. The notes are the source; this is a study aid.",
            label="AI-generated answers",
        )

    pending = st.session_state.get(error_key)
    if pending:
        ui.note("danger", "Could not answer", pending["message"])
        if st.button(
            "Try that question again",
            key=f"ask-retry::{lesson['id']}",
            disabled=not api_key,
        ):
            failed = st.session_state[error_key].get("question")
            # Drop the unanswered turn so the retry does not duplicate it.
            if history and history[-1]["role"] == "user":
                history.pop()
            st.session_state.pop(error_key, None)
            _ask(lesson, failed, language, api_key)

    with st.form(key=f"ask-form::{lesson['id']}::{nonce}"):
        question = st.text_input(
            "Your question",
            placeholder="e.g. Why is acceleration inversely proportional to mass?",
            key=f"ask-input::{lesson['id']}::{nonce}",
        )
        submitted = st.form_submit_button(
            "Ask Gemma 4",
            type="primary",
            disabled=not api_key,
            help=None if api_key else "Add a Gemma 4 API key to ask a question.",
        )

    if submitted:
        if not question.strip():
            ui.note("warning", "Nothing to ask", "Type a question first.")
        else:
            # A new nonce gives the next run a fresh, empty question box.
            bump(f"ask-nonce::{lesson['id']}")
            _ask(lesson, question.strip(), language, api_key)

    if history:
        ui.ai_disclosure(
            "Answers are generated by Gemma 4 from the notes above and can be "
            "wrong. The notes are the source; this is a study aid.",
            label="AI-generated answers",
        )
        if st.button("Clear this conversation", key=f"clear-chat::{lesson['id']}"):
            st.session_state[f"ask::{lesson['id']}"] = []
            st.session_state.pop(error_key, None)
            st.rerun()


def render_practice_tab(lesson: dict, api_key: str | None) -> None:
    """Generated multiple-choice practice with graded, persistent feedback."""
    ui.section_title("Practise this lesson")
    ui.ai_disclosure(PRACTICE_NOTE, label="AI-generated practice")

    lesson_id = lesson["id"]
    questions_key = f"mcqs::{lesson_id}"
    nonce_key = f"mcq-nonce::{lesson_id}"
    questions = st.session_state.get(questions_key)
    nonce = int(st.session_state.get(nonce_key, 0))
    graded_key = f"mcq-graded::{lesson_id}::{nonce}"
    graded = st.session_state.get(graded_key)

    if not questions:
        ui.empty_state(
            "No questions yet",
            f"Akshar will write {MCQ_COUNT} multiple-choice questions from the "
            "notes above, then mark them and explain each answer.",
        )
        if st.button(
            "Write practice questions",
            key=f"gen-mcq::{lesson_id}",
            type="primary",
            disabled=not api_key,
            help=None if api_key else "Add a Gemma 4 API key to write questions.",
        ):
            with st.spinner("Gemma 4 is writing questions…"):
                try:
                    st.session_state[questions_key] = ai_service.generate_mcqs(
                        lesson["content"], api_key, count=MCQ_COUNT
                    )
                    st.session_state[nonce_key] = nonce + 1
                    st.rerun()
                except AIServiceError as exc:
                    ui.note("danger", "Could not write questions", f"{exc}")
        return

    if graded:
        ui.score_summary(graded["score"], graded["total"], graded["best"])
        for index, question in enumerate(questions, start=1):
            chosen = graded["answers"].get(index)
            letter = question["answer"]
            ui.result_row(
                index,
                chosen == letter,
                question["question"],
                f"{chosen}. {question['options'][chosen]}" if chosen else None,
                f"{letter}. {question['options'][letter]}",
                question["explanation"],
            )
        action_left, action_right = st.columns(2)
        with action_left:
            if st.button("Try these again", key=f"retry-mcq::{lesson_id}::{nonce}"):
                st.session_state.pop(graded_key, None)
                st.rerun()
        with action_right:
            if st.button(
                "Write new questions",
                key=f"new-mcq::{lesson_id}",
                type="primary",
                disabled=not api_key,
            ):
                st.session_state.pop(questions_key, None)
                st.session_state.pop(graded_key, None)
                st.session_state[nonce_key] = nonce + 1
                st.rerun()
        return

    with st.form(key=f"mcq-form::{lesson_id}::{nonce}"):
        for index, question in enumerate(questions, start=1):
            ui.question(index, question["question"])
            st.radio(
                question["question"],
                options=("A", "B", "C", "D"),
                index=None,
                format_func=lambda letter, q=question: f"{letter}. {q['options'][letter]}",
                key=f"mcq-ans::{lesson_id}::{nonce}::{index}",
                label_visibility="collapsed",
            )
        submitted = st.form_submit_button("Check my answers", type="primary")

    if submitted:
        answers = {
            index: st.session_state[f"mcq-ans::{lesson_id}::{nonce}::{index}"]
            for index in range(1, len(questions) + 1)
        }
        score = sum(
            1
            for index, question in enumerate(questions, start=1)
            if answers.get(index) == question["answer"]
        )
        state = get_progress()
        progress.record_attempt(state, lesson_id, score, len(questions))
        best = progress.get_lesson_progress(state, lesson_id) or {}
        st.session_state[graded_key] = {
            "score": score,
            "total": len(questions),
            "answers": answers,
            "best": (
                f"Session best for this lesson: {best.get('best_score', score)} / "
                f"{best.get('best_total', len(questions))}"
            ),
        }
        st.rerun()


def render_flashcards_tab(lesson: dict, api_key: str | None) -> None:
    """Generated flashcards for self-testing."""
    ui.section_title("Review with flashcards")
    ui.ai_disclosure(FLASHCARD_NOTE, label="AI-generated flashcards")

    lesson_id = lesson["id"]
    state_key = f"cards::{lesson_id}"
    cards = st.session_state.get(state_key)

    if not cards:
        ui.empty_state(
            "No flashcards yet",
            f"Akshar will write {FLASHCARD_COUNT} prompt-and-answer cards from the "
            "notes above. Open a card to check yourself.",
        )
        if st.button(
            "Write flashcards",
            key=f"gen-fc::{lesson_id}",
            type="primary",
            disabled=not api_key,
            help=None if api_key else "Add a Gemma 4 API key to write flashcards.",
        ):
            with st.spinner("Gemma 4 is writing flashcards…"):
                try:
                    st.session_state[state_key] = ai_service.generate_flashcards(
                        lesson["content"], api_key, count=FLASHCARD_COUNT
                    )
                    st.rerun()
                except AIServiceError as exc:
                    ui.note("danger", "Could not write flashcards", f"{exc}")
        return

    for index, card in enumerate(cards, start=1):
        with st.expander(f"Card {index} · {card['question']}"):
            st.markdown(card["answer"])

    if st.button("Start over", key=f"reset-fc::{lesson_id}"):
        st.session_state.pop(state_key, None)
        st.rerun()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def render_sidebar(lessons: list[dict], api_key: str | None) -> None:
    """Gemma 4 status and this session's real progress."""
    titles = {lesson["id"]: lesson["title"] for lesson in lessons}
    with st.sidebar:
        ui.sidebar_brand()

        ui.section_title("Gemma 4", level=2)
        if api_key:
            st.caption("Connected — an API key is configured for this session.")
        else:
            st.caption("No API key — reading works, AI features are off.")
        st.caption(f"Model · {ai_service.MODEL_ID}")

        st.divider()
        ui.section_title("Your progress", level=2)
        st.caption("This browser session only — reloading the page clears it.")

        state = get_progress()
        summary = progress.summarize(state)
        if not state:
            ui.empty_state(
                "No attempts yet",
                "Check a practice set and your best score will appear here.",
            )
        else:
            ui.stats(
                [
                    ("Lessons practised", str(summary["lessons_practised"])),
                    ("Attempts", str(summary["total_attempts"])),
                    ("Average best", f"{summary['average_best_percent']}%"),
                ]
            )
            ui.stats_list(
                [
                    (
                        titles.get(lesson_id, lesson_id),
                        f"{entry['best_score']} / {entry['best_total']}",
                    )
                    for lesson_id, entry in state.items()
                    if entry["best_total"]
                ]
            )

        if st.button("Reset session progress"):
            st.session_state["progress"] = progress.new_state()
            st.rerun()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    st.set_page_config(
        page_title="Akshar — Learning Platform for Nepal",
        page_icon=":material/school:",
        layout="wide",
    )
    ui.install()

    try:
        lessons = get_lessons(lessons_signature())
    except ContentError as exc:
        ui.note("danger", "Could not load lesson content", str(exc))
        st.stop()

    api_key = get_api_key()
    render_sidebar(lessons, api_key)

    ui.masthead()
    selection = render_study_path(lessons)
    lesson = selection["lesson"]

    if lesson is None:
        ui.empty_state(
            "No lessons available",
            "The lesson file loaded but contains no usable lessons.",
        )
        st.stop()

    render_lesson(lesson)
    render_ai_status(api_key)

    tab_explain, tab_ask, tab_practice, tab_flashcards = st.tabs(
        ["Explain", "Ask Gemma 4", "Practise", "Flashcards"]
    )
    with tab_explain:
        render_explain_tab(lesson, api_key)
    with tab_ask:
        render_ask_tab(lesson, api_key)
    with tab_practice:
        render_practice_tab(lesson, api_key)
    with tab_flashcards:
        render_flashcards_tab(lesson, api_key)

    st.divider()
    st.caption(
        f"Akshar · Team Nepluro · MIT License · Model {ai_service.MODEL_ID} · "
        "Lesson content: team-authored study notes, not official NEB/CEE/IOE material."
    )


if __name__ == "__main__":
    main()
