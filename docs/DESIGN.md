# Akshar design system

The whole design system lives in one file: [`landing/styles.css`](../landing/styles.css).
Its `:root` block holds the tokens and everything below it is the component layer. There is
no second theme file, no build step, and **no Python/Streamlit front end**: `landing/` is the
only front end this project has, so this is the only design system and there is nothing to
keep in step with a second one.

To change a colour, a radius, or a spacing step: edit the token in `:root` and use it
everywhere else. Never hard-code a hex value or a magic margin in a component rule.

## Direction

Light-first and warm: off-white paper surfaces, midnight-indigo ink for readability, deep
teal for learning actions, and saffron held back for the two moments that deserve it — the
reading-progress bar and the results score. No gradients, no floating decoration, and no
dashboard of oversized statistics; hierarchy comes from type scale, spacing, and composition.

## Colour

| Token | Value | Use |
|-------|-------|-----|
| `--akx-ink` | `#171a2b` | Headings and body text |
| `--akx-ink-muted` | `#4a5069` | Supporting text, metadata, prose in cards |
| `--akx-ink-subtle` | `#63697e` | Uppercase micro labels, hints, footer — ≥ 4.5:1 on every surface below |
| `--akx-surface` | `#ffffff` | Cards and panels |
| `--akx-surface-page` | `#fbfaf7` | The page behind the cards |
| `--akx-surface-sunken` | `#f5f3ec` | Toolbars, breadcrumbs, disabled fields |
| `--akx-border` | `#e4e1d8` | Hairline separators |
| `--akx-border-strong` | `#8f8a7c` | Form-control outlines (3:1 against the surface) |
| `--akx-brand` | `#0f6e5a` | Primary actions, links, focus rings, active nav |
| `--akx-brand-strong` | `#0b5646` | Hover and pressed states |
| `--akx-brand-soft` / `--akx-brand-line` | `#e8f2ee` / `#cfe3db` | Source/provenance tint and the selected answer |
| `--akx-accent` / `--akx-accent-strong` | `#8f5c05` / `#6f4703` | Saffron: reading progress and the results score |
| `--akx-accent-soft` / `--akx-accent-line` | `#fdf1da` / `#ecd9ae` | Revision pointer and the score panel |
| `--akx-success` / `-soft` | `#1a6b3c` / `#e7f3ec` | Correct answers, "correct" count |
| `--akx-warning` / `-soft` | `#8a5300` / `#fdf3e3` | Honest caveats (AI off, generated questions) |
| `--akx-danger` / `-soft` | `#a32a1f` / `#fbeceb` | Failures, wrong answers, "incorrect" count |

Every foreground/background pair the interface uses meets WCAG AA. An axe-core run over six
states (dashboard, lesson, quiz form, submit dialog, results, assistant) plus the sources
view at 390, 768, and 1440 px reports **no violations**. Status is never conveyed by colour
alone: each verdict also carries a word (`Correct`, `not correct`, `not answered`).

## Layout

| Token | Value | Use |
|-------|-------|-----|
| `--akx-content-max` | `1160px` | The centred app shell |
| `--akx-prose-max` | `68ch` | Reading surfaces: lesson notes, AI answers, explanations |
| `--akx-gutter` | `clamp(1rem, 4vw, 2.5rem)` | Page gutters (16 px → 40 px across viewports) |
| `--akx-section-y` | `clamp(1.75rem, 4vw, 3rem)` | Vertical rhythm between sections |
| `--akx-space-1` … `--akx-space-8` | `0.25rem` … `4rem` | A 4/8 spacing rhythm; no arbitrary margins |
| `--akx-header-h` | `3.75rem`, `7.0625rem` under 720 px | Sticky-header offset; the header wraps to two rows on narrow screens, so the token changes with it |

The dashboard is a two-column `.dash` grid with one `.card--lead` focal point (Continue
learning), collapsing to two columns under 1024 px and one under 720 px. Teaching content
never goes edge to edge: paragraphs stop at the reading measure.

## Radius, type, motion

- `--akx-radius-sm` 6px (chips, options), `--akx-radius-md` 10px (buttons, notes, tabs),
  `--akx-radius-lg` 14px (cards, panels), `--akx-radius-pill` for progress tracks and the
  status chip only.
- Depth is restrained: `--akx-shadow-sm` on buttons and inputs, `--akx-shadow-md` on hovered
  cards and the toast. Structure is drawn with borders, not shadow.
- Type: `--akx-text-micro` 0.75rem (uppercase labels), `--akx-text-meta` 0.875rem (metadata,
  helper text), `--akx-text-body` 1rem, `--akx-text-lead` 1.125rem. Page headings are
  `clamp(1.6rem, 3.4vw, 2.35rem)`; the lesson title and section titles step down from there.
- Transitions are `--akx-transition` (180 ms ease) and only ever on colour, background,
  border, and transform. `prefers-reduced-motion: reduce` disables them and smooth scrolling.

## Components

| Class | Purpose |
|-------|---------|
| `.skip-link` | First focus stop; jumps to the app instead of the nav |
| `.site-header`, `.brand`, `.site-nav`, `.status` | Identity, view navigation with `aria-current="page"`, and the Gemma 4 status chip (honest "AI off — notes only" without a key) |
| `.view--home`, `.view--study`, `.view--about` | The three mutually exclusive views; each carries the visible `h1` |
| `.hero`, `.hero__eyebrow`, `.hero__title`, `.hero__lead`, `.hero__actions`, `.hero__hint` | The compact dashboard greeting and its one primary action |
| `.dash`, `.card`, `.card--lead`, `.card__title`, `.card__meta`, `.card__body`, `.card__actions` | Dashboard surfaces; every number in them comes from saved activity or the lesson file |
| `.pathways`, `.pathway__button`, `.pathway__goal`, `.pathway__meta` | NEB / CEE / IOE entries with real chapter, subject, and language counts |
| `.bookmark-list`, `.bookmark-open` | Bookmarked chapters, openable in one click |
| `.stats`, `.stat`, `.count-chip` | Real browser-local numbers and the correct/incorrect/unanswered split |
| `.filters`, `.field`, `.count`, `.path`, `.path__sep` | The cascading goal → grade → subject → chapter → language controls; the grade step is disabled for the ungraded CEE/IOE tracks, and the breadcrumb shows the resolved path |
| `.lesson`, `.reading`, `.reading__fill`, `.lesson__head`, `.lesson-toolbar`, `.prose`, `.chips` | The reading surface: sticky reading-progress bar, chapter title and chips, text-size, bookmark, and the lesson body |
| `.lesson-nav` | Previous / next chapter in lesson-file order, keeping the reader's language |
| `.note`, `.note--source`, `.note--warning`, `.note--danger`, `.source`, `.disclosure` | Provenance and honesty: the source panel labels the notes, warnings state what is missing |
| `.tabs`, `.tab`, `.panel` | Study help: Explain / Ask / Practise / Flashcards as ARIA tabs with roving `tabindex` |
| `.assistant`, `.assistant__context`, `.assistant__label`, `.thread`, `.turn`, `.turn--assistant`, `.suggestions`, `.suggestion`, `.ask`, `.ask__row`, `.ask__language` | The assistant: lesson context, labelled AI turns, suggested questions as buttons (they fill the input, they do not send), answer language, retry, and return-to-lesson |
| `.quiz`, `.question`, `.option`, `.option--correct`, `.option--wrong`, `.option__mark`, `.feedback`, `.modes`, `.mode`, `.quiz-progress`, `.quiz-progress__fill` | The practice set: practice/exam modes, answered/unanswered states, progress counter and bar, immediate feedback in practice mode |
| `.dialog`, `.dialog__title`, `.dialog__body`, `.dialog__actions` | Confirm-before-submit for a blank answer, dismissible with Escape |
| `.result-card`, `.score`, `.score--hero`, `.result-counts`, `.result-facts`, `.result-revisit`, `.result-actions`, `.review`, `.review__item`, `.review__verdict`, `.review__yours` | The results screen: score first, then the split, accuracy, what to revise, and every question reviewed with the correct answer and why |
| `.cards`, `.card__answer` | Flashcards |
| `.state`, `.empty`, `.hint`, `.toast` | Loading, error, empty, and saved-item feedback; the toast is `role="status"` |
| `.button`, `.button--primary`, `.button--quiet`, `.button--ghost`, `.button--lg`, `.icon-button` | Controls, with hover, pressed, disabled, loading, and focus states |

Provenance is structural, not decorative: lesson text sits in a bordered source panel, AI
output carries an AI label inside the result, and practice questions are marked as generated
rather than official exam questions.

## Accessibility rules

- A skip link, semantic landmarks, and **exactly one visible `h1` per view** — the home hero,
  "Choose what to study", or "Sources and limits" while that view is on screen. Heading levels
  never skip.
- Every focus stop draws a visible ring (`outline: 2px solid var(--akx-brand)`), including
  custom controls; focused result and question panels carry a `scroll-margin-top` so the
  sticky header never covers them.
- Interactive targets are at least 44 × 44 px, which matters on the phones most students use.
- The app needs no pointer: the whole journey (goal → chapter → lesson tools → quiz →
  results → assistant) is reachable by keyboard, and view changes move focus to the app
  region without scrolling it out of view.
- Asynchronous results and validation messages use `role="status"`; a failed AI call is
  reported as a failure, never rendered as an answer.
- Labels wrap instead of truncating; Devanagari and mathematical notation wrap or scroll
  rather than breaking the layout, and the app never scrolls horizontally at 360 px.
