"""Akshar design system: tokens, injected stylesheet, and shared UI blocks.

Akshar has two surfaces — the Streamlit app (this module) and the static landing
page in ``landing/``. Both use the same ``--akx-*`` custom properties, and
``.streamlit/config.toml`` carries the same colours into Streamlit's native
theme. ``tests/test_design_tokens.py`` fails if the three drift apart, so there
is exactly one place to change a colour, radius, or reading width.

Design rules kept deliberately narrow:

* warm neutral surfaces, dark readable text, one controlled accent (deep teal);
* colour communicates state or action only — never decoration;
* a 4/8 spacing rhythm, a small radius scale, and pills only for compact labels;
* semantic HTML with escaped dynamic values; no raw model output as HTML.
"""

from __future__ import annotations

import html as _html

import streamlit as st

__all__ = [
    "TOKENS",
    "install",
    "stylesheet",
    "masthead",
    "sidebar_brand",
    "path_line",
    "lesson_header",
    "prose",
    "note",
    "ai_disclosure",
    "source_disclosure",
    "section_title",
    "empty_state",
    "turn",
    "question",
    "stats",
    "stats_list",
    "score_summary",
    "result_row",
    "esc",
]

# ---------------------------------------------------------------------------
# Tokens — the single source of truth for both surfaces.
# ---------------------------------------------------------------------------

TOKENS: dict[str, str] = {
    # Text
    "ink": "#14201d",
    "ink-muted": "#4c5a56",
    "ink-subtle": "#66736e",
    # Surfaces
    "surface": "#ffffff",
    "surface-sunken": "#f7f6f3",
    # Lines
    "border": "#e4e2dc",
    "border-strong": "#cfccc4",
    # Accent (used for actions, links, and emphasis only)
    "brand": "#0f6e5a",
    "brand-strong": "#0b5646",
    "brand-soft": "#e9f2ef",
    # State
    "success": "#1a6b3c",
    "success-soft": "#e7f3ec",
    "warning": "#8a5300",
    "warning-soft": "#fdf3e3",
    "danger": "#a32a1f",
    "danger-soft": "#fbeceb",
    # Spacing (4/8 rhythm)
    "space-1": "0.25rem",
    "space-2": "0.5rem",
    "space-3": "0.75rem",
    "space-4": "1rem",
    "space-5": "1.5rem",
    "space-6": "2rem",
    "space-7": "3rem",
    "space-8": "4rem",
    # Radius scale (pills reserved for compact labels)
    "radius-sm": "4px",
    "radius-md": "8px",
    "radius-lg": "12px",
    "radius-pill": "999px",
    # Measure
    "content-max": "1120px",
    "prose-max": "68ch",
    # Type scale
    "text-micro": "0.75rem",
    "text-meta": "0.875rem",
    "text-body": "1rem",
    "text-lead": "1.125rem",
}

# The Masthead is an editorial header, so it gets its own typographic treatment
# on both surfaces rather than Streamlit's default h1 size.
_FONT_STACK = (
    "system-ui, -apple-system, 'Segoe UI', Roboto, 'Noto Sans Devanagari', "
    "'Nirmala UI', Arial, sans-serif"
)

# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------

_ROOT_EXTRA = """
  --akx-font: __FONT__;
  --akx-shadow: 0 1px 2px rgba(20, 32, 29, 0.06);
"""

_STATIC_CSS = """
*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body,
[data-testid="stAppViewContainer"] {
  font-family: var(--akx-font);
  color: var(--akx-ink);
}

/* ---- App shell: one centred container, shared gutters ---------------- */
[data-testid="stMainBlockContainer"],
.stMainBlockContainer,
.block-container {
  max-width: var(--akx-content-max);
  margin: 0 auto;
  padding: var(--akx-space-8) clamp(1rem, 3vw, 2.5rem) 6rem;
}

[data-testid="stSidebar"] {
  border-right: 1px solid var(--akx-border);
}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding-top: var(--akx-space-5);
}

.akx-sidebar-brand {
  margin: 0 0 var(--akx-space-4);
  font-size: 1rem;
  font-weight: 700;
  color: var(--akx-ink);
}

.akx-sidebar-brand span {
  color: var(--akx-brand);
  margin-right: 0.4rem;
}

/* ---- Masthead -------------------------------------------------------- */
.akx-masthead {
  padding-bottom: var(--akx-space-5);
  border-bottom: 1px solid var(--akx-border);
  margin-bottom: var(--akx-space-5);
}

[data-testid="stMarkdownContainer"] h1.akx-masthead__title,
.akx-masthead__title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--akx-ink);
}

.akx-masthead__title span {
  color: var(--akx-brand);
  margin-right: 0.5rem;
}

.akx-masthead__tagline {
  margin: var(--akx-space-2) 0 0;
  max-width: var(--akx-prose-max);
  font-size: var(--akx-text-body);
  line-height: 1.6;
  color: var(--akx-ink-muted);
}

.akx-masthead__loop {
  margin: var(--akx-space-3) 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: var(--akx-space-2) var(--akx-space-3);
  font-size: var(--akx-text-meta);
  color: var(--akx-ink-subtle);
}

.akx-masthead__loop li::after {
  content: "\\2192";
  margin-left: var(--akx-space-3);
  color: var(--akx-border-strong);
}

.akx-masthead__loop li:last-child::after {
  content: none;
}

/* ---- Study path ------------------------------------------------------ */
.akx-path {
  margin: 0;
  font-size: var(--akx-text-meta);
  color: var(--akx-ink-subtle);
}

.akx-path__sep {
  color: var(--akx-border-strong);
  margin: 0 0.4rem;
}

[data-testid="stMarkdownContainer"] h2.akx-lesson-title,
.akx-lesson-title {
  margin: var(--akx-space-2) 0 0;
  font-size: 1.75rem;
  line-height: 1.25;
  letter-spacing: -0.015em;
  color: var(--akx-ink);
}

.akx-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--akx-space-2);
  margin: var(--akx-space-3) 0 0;
  padding: 0;
  list-style: none;
}

.akx-chip {
  border: 1px solid var(--akx-border);
  border-radius: var(--akx-radius-sm);
  background: var(--akx-surface-sunken);
  padding: 0.15rem 0.5rem;
  font-size: var(--akx-text-micro);
  color: var(--akx-ink-muted);
}

.akx-chip--source {
  border-color: transparent;
  background: var(--akx-brand-soft);
  color: var(--akx-brand-strong);
  font-weight: 600;
}

/* ---- Prose: reading surfaces stay narrower than the shell ------------- */
.st-key-akx-prose,
.st-key-akx-prose > div {
  max-width: var(--akx-prose-max);
}

.st-key-akx-prose {
  overflow-wrap: anywhere;
}

.st-key-akx-prose p,
.st-key-akx-prose li {
  font-size: var(--akx-text-body);
  line-height: 1.7;
}

.st-key-akx-prose ul,
.st-key-akx-prose ol {
  padding-left: 1.25rem;
}

.st-key-akx-prose code {
  background: var(--akx-surface-sunken);
  border-radius: var(--akx-radius-sm);
  padding: 0.1rem 0.3rem;
  font-size: 0.9em;
}

/* ---- Section titles -------------------------------------------------- */
[data-testid="stMarkdownContainer"] h2.akx-section-title,
[data-testid="stMarkdownContainer"] h3.akx-section-title,
.akx-section-title {
  margin: 0 0 var(--akx-space-2);
  font-size: 1.25rem;
  font-weight: 650;
  letter-spacing: -0.005em;
  color: var(--akx-ink);
}

/* ---- Notes / callouts ----------------------------------------------- */
.akx-note {
  border: 1px solid var(--akx-border);
  border-left: 3px solid var(--akx-border-strong);
  border-radius: 0 var(--akx-radius-md) var(--akx-radius-md) 0;
  background: var(--akx-surface-sunken);
  padding: var(--akx-space-3) var(--akx-space-4);
  margin: var(--akx-space-4) 0;
  max-width: var(--akx-prose-max);
}

.akx-note__label {
  display: block;
  margin-bottom: 0.15rem;
  font-size: var(--akx-text-micro);
  font-weight: 650;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--akx-ink-subtle);
}

.akx-note__body {
  margin: 0;
  font-size: var(--akx-text-meta);
  line-height: 1.6;
  color: var(--akx-ink-muted);
}

.akx-note--source {
  border-left-color: var(--akx-brand);
  background: var(--akx-brand-soft);
}

.akx-note--source .akx-note__label {
  color: var(--akx-brand-strong);
}

.akx-note--ai {
  border-left-color: var(--akx-ink-subtle);
}

.akx-note--warning {
  border-left-color: var(--akx-warning);
  background: var(--akx-warning-soft);
}

.akx-note--warning .akx-note__label {
  color: var(--akx-warning);
}

.akx-note--danger {
  border-left-color: var(--akx-danger);
  background: var(--akx-danger-soft);
}

.akx-note--danger .akx-note__label {
  color: var(--akx-danger);
}

.akx-note--success {
  border-left-color: var(--akx-success);
  background: var(--akx-success-soft);
}

.akx-note--success .akx-note__label {
  color: var(--akx-success);
}

/* ---- Conversation turns --------------------------------------------- */
[class*="st-key-akx-turn-"] {
  padding: var(--akx-space-3) var(--akx-space-4);
  border-radius: var(--akx-radius-md);
  margin-bottom: var(--akx-space-3);
}

[class*="st-key-akx-turn-user-"] {
  background: var(--akx-surface-sunken);
  border: 1px solid var(--akx-border);
}

[class*="st-key-akx-turn-ai-"] {
  background: var(--akx-surface);
  border: 1px solid var(--akx-border);
  border-left: 3px solid var(--akx-brand);
}

.akx-turn__label {
  margin: 0 0 0.35rem;
  font-size: var(--akx-text-micro);
  font-weight: 650;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--akx-ink-subtle);
}

[class*="st-key-akx-turn-ai-"] .akx-turn__label {
  color: var(--akx-brand-strong);
}

/* ---- Practice feedback ---------------------------------------------- */
.akx-score {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--akx-space-2) var(--akx-space-4);
  border: 1px solid var(--akx-border);
  border-radius: var(--akx-radius-md);
  background: var(--akx-surface-sunken);
  padding: var(--akx-space-3) var(--akx-space-4);
  margin: var(--akx-space-4) 0;
}

.akx-score__value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--akx-ink);
}

.akx-score__label {
  font-size: var(--akx-text-meta);
  color: var(--akx-ink-muted);
}

.akx-result {
  border: 1px solid var(--akx-border);
  border-radius: var(--akx-radius-md);
  background: var(--akx-surface);
  padding: var(--akx-space-3) var(--akx-space-4);
  margin-bottom: var(--akx-space-2);
  max-width: var(--akx-prose-max);
}

.akx-result--correct {
  border-left: 3px solid var(--akx-success);
}

.akx-result--incorrect {
  border-left: 3px solid var(--akx-danger);
}

.akx-result__head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--akx-space-2);
}

.akx-result__index {
  font-size: var(--akx-text-meta);
  font-weight: 700;
  color: var(--akx-ink);
}

.akx-result__tag {
  font-size: var(--akx-text-micro);
  font-weight: 650;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.akx-result--correct .akx-result__tag {
  color: var(--akx-success);
}

.akx-result--incorrect .akx-result__tag {
  color: var(--akx-danger);
}

.akx-result__question {
  margin: 0.35rem 0 0;
  font-size: var(--akx-text-body);
  line-height: 1.5;
  color: var(--akx-ink);
}

.akx-result__body {
  margin: 0.25rem 0 0;
  font-size: var(--akx-text-meta);
  line-height: 1.6;
  color: var(--akx-ink-muted);
}

/* ---- Empty states ---------------------------------------------------- */
.akx-empty {
  border: 1px dashed var(--akx-border-strong);
  border-radius: var(--akx-radius-md);
  background: var(--akx-surface-sunken);
  padding: var(--akx-space-4);
  margin: var(--akx-space-4) 0;
  max-width: var(--akx-prose-max);
}

.akx-empty__title {
  margin: 0;
  font-size: var(--akx-text-body);
  font-weight: 650;
  color: var(--akx-ink);
}

.akx-empty__body {
  margin: var(--akx-space-1) 0 0;
  font-size: var(--akx-text-meta);
  line-height: 1.6;
  color: var(--akx-ink-muted);
}

/* ---- Practice questions --------------------------------------------- */
.akx-question {
  margin: var(--akx-space-4) 0 var(--akx-space-2);
  max-width: var(--akx-prose-max);
  font-size: var(--akx-text-body);
  font-weight: 600;
  line-height: 1.5;
  color: var(--akx-ink);
}

.akx-question__index {
  margin-right: 0.5rem;
  color: var(--akx-brand-strong);
}

/* ---- Session stats (real values only) ------------------------------- */
.akx-stats {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: baseline;
  gap: var(--akx-space-2) var(--akx-space-3);
  margin: var(--akx-space-3) 0 0;
}

.akx-stats > div {
  display: contents;
}

.akx-stats dt {
  margin: 0;
  font-size: var(--akx-text-meta);
  color: var(--akx-ink-muted);
}

.akx-stats dd {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--akx-ink);
  white-space: nowrap;
  text-align: right;
}

.akx-stats-list {
  margin: var(--akx-space-4) 0 0;
  padding: 0;
  list-style: none;
  font-size: var(--akx-text-meta);
}

.akx-stats-list li {
  display: flex;
  justify-content: space-between;
  gap: var(--akx-space-3);
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--akx-border);
  color: var(--akx-ink-muted);
}

.akx-stats-list li:last-child {
  border-bottom: 0;
}

.akx-stats-list b {
  color: var(--akx-ink);
  font-weight: 650;
  white-space: nowrap;
}

/* ---- Controls -------------------------------------------------------- */
/* Keyboard focus has to be obvious on every control. Streamlit's own ring
   covers buttons, tabs, and the expander, but its inputs only shift a 1px
   border colour, so they get an explicit outline. */
[data-testid="stSelectbox"] :focus-within,
[data-testid="stSelectbox"] input:focus-visible,
[data-testid="stTextInput"] input:focus-visible,
[data-testid="stTextArea"] textarea:focus-visible {
  outline: 2px solid var(--akx-brand);
  outline-offset: 2px;
}

[tabindex="0"]:focus-visible {
  outline: 2px solid var(--akx-brand);
  outline-offset: -4px;
}


.stButton > button,
[data-testid^="stBaseButton"] {
  min-height: 2.75rem;
  border-radius: var(--akx-radius-md);
  font-weight: 600;
}

[data-testid="stForm"] {
  border: 1px solid var(--akx-border);
  border-radius: var(--akx-radius-md);
  background: var(--akx-surface);
  padding: var(--akx-space-4);
}

[data-testid="stTabs"] button[role="tab"] {
  font-size: 0.9375rem;
}

[data-testid="stExpander"] summary {
  font-weight: 600;
}

a,
button,
input,
textarea,
select,
summary,
[role="tab"],
[role="radio"],
[tabindex]:focus-visible {
  outline-offset: 2px;
}

a:focus-visible,
button:focus-visible,
summary:focus-visible,
[role="tab"]:focus-visible,
[data-baseweb="select"]:focus-within {
  outline: 2px solid var(--akx-brand);
}

/* ---- Responsive ------------------------------------------------------ */
@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"],
  .stMainBlockContainer,
  .block-container {
    padding: var(--akx-space-5) 1rem 4rem;
  }

  [data-testid="stMarkdownContainer"] h1.akx-masthead__title,
  .akx-masthead__title {
    font-size: 1.35rem;
  }

  [data-testid="stMarkdownContainer"] h2.akx-lesson-title,
  .akx-lesson-title {
    font-size: 1.4rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }

  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
"""


def _root_block() -> str:
    """Return the ``:root`` custom-property block generated from ``TOKENS``."""
    lines = [f"  --akx-{name}: {value};" for name, value in TOKENS.items()]
    extra = _ROOT_EXTRA.strip("\n").replace("__FONT__", _FONT_STACK)
    return ":root {\n" + "\n".join(lines) + "\n" + extra + "\n}"


def stylesheet() -> str:
    """Return the full design-system stylesheet (tokens + component rules)."""
    return _root_block() + "\n" + _STATIC_CSS


def install() -> None:
    """Inject the design system into the running Streamlit app."""
    st.markdown(f"<style>{stylesheet()}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def esc(value: object) -> str:
    """Escape a dynamic value for safe interpolation into raw HTML."""
    return _html.escape(str(value), quote=True)


def _html_block(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def masthead() -> None:
    """Product identity, purpose, and the learn/understand/practise loop."""
    _html_block(
        """
<header class="akx-masthead">
  <h1 class="akx-masthead__title"><span lang="ne">अक्षर</span> Akshar</h1>
  <p class="akx-masthead__tagline">
    Study notes, grounded explanations, and practice for NEB Grade 11&ndash;12,
    CEE, and IOE &mdash; in English or Nepali.
  </p>
  <ol class="akx-masthead__loop">
    <li>Learn</li>
    <li>Understand</li>
    <li>Practise</li>
  </ol>
</header>
"""
    )


def sidebar_brand() -> None:
    """A small wordmark for the sidebar, so the panel is not anonymous."""
    _html_block('<p class="akx-sidebar-brand"><span lang="ne">अक्षर</span> Akshar</p>')


def path_line(parts: list[str]) -> None:
    """Render where the learner is in the curriculum, as escaped plain text."""
    joined = '<span class="akx-path__sep" aria-hidden="true">/</span>'.join(
        esc(part) for part in parts
    )
    _html_block(f'<p class="akx-path">{joined}</p>')


def lesson_header(parts: list[str], title: str, chips: list[tuple[str, bool]]) -> None:
    """Breadcrumb, lesson title (h2), and compact status chips.

    ``chips`` is a list of ``(label, is_source)`` pairs; source chips use the
    accent tint so provenance reads as a property of the material.
    """
    path_line(parts)
    items = "".join(
        f'<li class="akx-chip{" akx-chip--source" if is_source else ""}">{esc(label)}</li>'
        for label, is_source in chips
    )
    _html_block(
        f'<h2 class="akx-lesson-title">{esc(title)}</h2>'
        f'<ul class="akx-chips">{items}</ul>'
    )


def prose(text: str) -> None:
    """Render lesson text in the narrower reading measure.

    ``text`` is treated as Markdown by Streamlit with HTML escaping left on, so
    lesson content can never inject markup into the page.
    """
    with st.container(key="akx-prose"):
        st.markdown(text)


def note(kind: str, label: str, body: str) -> None:
    """Render a labelled note. ``kind``: plain | source | ai | warning | danger | success."""
    modifier = "" if kind == "plain" else f" akx-note--{kind}"
    _html_block(
        f'<aside class="akx-note{modifier}" role="note">'
        f'<span class="akx-note__label">{esc(label)}</span>'
        f'<p class="akx-note__body">{esc(body)}</p>'
        "</aside>"
    )


def ai_disclosure(body: str, label: str = "AI-generated") -> None:
    """Attach the standard, unmissable AI provenance note to model output."""
    note("ai", label, body)


def source_disclosure(body: str, label: str = "Source") -> None:
    """Attach provenance to non-AI material (lesson notes, references)."""
    note("source", label, body)


def section_title(text: str, level: int = 3) -> None:
    """A quiet heading for grouping content.

    ``level`` keeps the document outline legal: top-level sections sit under the
    masthead's ``h1`` as ``h2``, and content inside a tab sits under that as ``h3``.
    """
    if level not in (2, 3):
        raise ValueError("section_title only supports h2 and h3")
    _html_block(f'<h{level} class="akx-section-title">{esc(text)}</h{level}>')


def empty_state(title: str, body: str) -> None:
    """A first-run / nothing-here block that names the next useful action."""
    _html_block(
        f'<div class="akx-empty"><p class="akx-empty__title">{esc(title)}</p>'
        f'<p class="akx-empty__body">{esc(body)}</p></div>'
    )


def turn(role: str, text: str, index: int) -> None:
    """Render one conversation turn with an explicit speaker label.

    The label matters: a learner must be able to tell Gemma 4's answer apart
    from their own question and from the lesson notes.
    """
    is_user = role == "user"
    key = f"akx-turn-{'user' if is_user else 'ai'}-{index}"
    label = "Your question" if is_user else "Akshar · Gemma 4"
    with st.container(key=key):
        _html_block(f'<p class="akx-turn__label">{esc(label)}</p>')
        st.markdown(text)


def question(index: int, text: str) -> None:
    """Render a numbered practice question above its answer options.

    Deliberately a paragraph, not a heading: the option group carries the same
    text as its accessible name, so screen-reader users hear the question with
    the choices.
    """
    _html_block(
        f'<p class="akx-question">'
        f'<span class="akx-question__index">Q{esc(index)}</span>{esc(text)}'
        "</p>"
    )


def stats(items: list[tuple[str, str]]) -> None:
    """Render a compact definition list of real, traceable numbers."""
    rows = "".join(
        f"<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>" for label, value in items
    )
    _html_block(f'<dl class="akx-stats">{rows}</dl>')


def stats_list(rows: list[tuple[str, str]]) -> None:
    """Render label/value rows (for example a lesson and its best score)."""
    items = "".join(
        f"<li><span>{esc(label)}</span><b>{esc(value)}</b></li>" for label, value in rows
    )
    _html_block(f'<ul class="akx-stats-list">{items}</ul>')


def score_summary(score: int, total: int, best: str) -> None:
    """Show this attempt's real score next to the session's real best."""
    _html_block(
        f'<div class="akx-score">'
        f'<span class="akx-score__value">{esc(score)} / {esc(total)}</span>'
        f'<span class="akx-score__label">correct on this attempt</span>'
        f'<span class="akx-score__label">{esc(best)}</span>'
        f"</div>"
    )


def result_row(
    index: int,
    correct: bool,
    question: str,
    chosen_label: str | None,
    answer_label: str,
    explanation: str,
) -> None:
    """Render one graded question: the question, the verdict, the answer, and why.

    The question is repeated here on purpose — the answer form is hidden once the
    set is marked, so a review row has to stand on its own.
    """
    modifier = "correct" if correct else "incorrect"
    tag = "Correct" if correct else "Not quite"
    detail = f"You chose {chosen_label}." if chosen_label else "You did not answer this one."
    if not correct:
        detail += f" The correct answer is {answer_label}."
    _html_block(
        f'<div class="akx-result akx-result--{modifier}">'
        f'<div class="akx-result__head">'
        f'<span class="akx-result__index">Q{esc(index)}</span>'
        f'<span class="akx-result__tag">{esc(tag)}</span>'
        f"</div>"
        f'<p class="akx-result__question">{esc(question)}</p>'
        f'<p class="akx-result__body">{esc(detail)}</p>'
        f'<p class="akx-result__body">{esc(explanation)}</p>'
        f"</div>"
    )
