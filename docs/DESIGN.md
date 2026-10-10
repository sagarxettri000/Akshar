# Akshar design system

One design system, three places it is expressed:

| Surface | Where it lives |
|---------|----------------|
| Streamlit app components and injected CSS | [`ui.py`](../ui.py) (`TOKENS`, `stylesheet()`) |
| Streamlit's native theme (colours, radii, type) | [`.streamlit/config.toml`](../.streamlit/config.toml) |
| Web app (Vercel) | [`landing/styles.css`](../landing/styles.css) (`:root`) |

`tests/test_design_tokens.py` compares the three and fails if they drift. To
change a colour or a radius: edit `ui.TOKENS`, mirror the value in
`config.toml` and `landing/styles.css`, then run the test suite.

## Colour

Warm neutral surfaces, dark text, one accent (deep teal). Colour only ever
communicates hierarchy, state, or action — never decoration.

| Token | Value | Use |
|-------|-------|-----|
| `ink` | `#14201d` | Headings and body text |
| `ink-muted` | `#4c5a56` | Supporting text, metadata |
| `ink-subtle` | `#66736e` | Breadcrumbs, uppercase labels |
| `surface` | `#ffffff` | Page and card surfaces |
| `surface-sunken` | `#f7f6f3` | Sidebar, notes, empty states |
| `border` | `#e4e2dc` | Hairline separators |
| `border-strong` | `#cfccc4` | Dashed empty-state outlines |
| `brand` | `#0f6e5a` | Primary actions, links, focus rings, AI accent |
| `brand-strong` | `#0b5646` | Hover/active, link text on light tint |
| `brand-soft` | `#e9f2ef` | Source/provenance tint |
| `success` / `warning` / `danger` (+ `-soft`) | `#1a6b3c` / `#8a5300` / `#a32a1f` | Feedback states only |

Every foreground/background pair used by the UI meets WCAG AA (≥ 4.5:1); the
lowest ratio in use is 4.95:1 (`ink-subtle` on `surface`). Status is never
conveyed by colour alone: every verdict also carries a word (`Correct`,
`Not quite`) or an icon.

## Layout

* App shell: centred container, `--akx-content-max` = 1120px, gutters
  `clamp(1rem, 3vw, 2.5rem)` (24px → 40px across viewports), 4rem top clearance
  under Streamlit's fixed header.
* Reading surfaces (lesson notes, AI answers, explanations) stop at
  `--akx-prose-max` = 68ch, so paragraphs never run the width of the shell.
* Spacing follows a 4/8 rhythm: `space-1` 4px … `space-8` 64px.
* Radius scale: `radius-sm` 4px (chips, step numbers), `radius-md` 8px
  (buttons, notes, cards), `radius-lg` 12px, `radius-pill` reserved for compact
  labels whose behaviour calls for it.

## Type

System sans stack only — no webfont download:

```
system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans Devanagari",
"Nirmala UI", Arial, sans-serif
```

`Noto Sans Devanagari` is in the stack for both surfaces so Nepali text renders
with the reader's own glyphs on any device, and Latin and Devanagari stay in the
same type system. Body text is 16px with 1.6–1.7 line height; metadata 14px;
labels 12px uppercase; lesson titles 1.75rem (1.4rem on phones); the masthead
1.5rem.

## Components (`ui.py`)

| Helper | Purpose |
|--------|---------|
| `masthead()` / `sidebar_brand()` | Product identity; `h1` on the main column |
| `lesson_header()` | Curriculum breadcrumb, `h2` title, status chips |
| `prose()` | Lesson text in the reading measure |
| `note(kind, label, body)` | Provenance, warnings, errors (`source`, `ai`, `warning`, `danger`, `success`) |
| `ai_disclosure()` / `source_disclosure()` | The two provenance notes, always adjacent to what they describe |
| `section_title(text, level)` | `h2` for page sections, `h3` inside tabs |
| `empty_state()` | Names the next useful action before anything is generated |
| `turn()` | One question/answer pair with an explicit speaker label |
| `question()` / `score_summary()` / `result_row()` | Practice set, grade, and review |
| `stats()` / `stats_list()` | Real session numbers, right-aligned so labels can wrap |

Dynamic values always pass through `esc()`; model output is rendered as Markdown
with HTML escaping left on.

## Accessibility rules

* Exactly one `h1`, no descending level skips (enforced by
  `tests/test_app.py::test_heading_outline_has_no_skips`). Streamlit renders the
  sidebar before the main column, so the two sidebar `h2`s precede the `h1`.
* Every focus stop draws a visible ring: `2px solid brand`. Streamlit's inputs
  only shift a 1px border colour, so `ui.py` adds an explicit outline for
  selectboxes, text areas, and `[tabindex="0"]` containers.
* Answer groups carry the full question text as their accessible name; graded
  rows repeat the question they mark.
* Controls are ≥ 44px tall (`min-height` on buttons). Streamlit's own ⋮ main-menu
  button stays 28px — it is platform chrome, not app UI.
* `prefers-reduced-motion` disables transitions and smooth scrolling.
