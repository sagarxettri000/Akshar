# Akshar design system

The whole design system lives in one file: [`landing/styles.css`](../landing/styles.css).
Its `:root` block holds the tokens, and everything below it is the component layer. There is
no second theme file and no build step — the earlier Python/Streamlit front end, and with it
the second set of theme tokens, was removed, so there is nothing left to keep in step.

To change a colour, a radius, or a spacing step: edit the token in `:root` and use it
everywhere else. Never hard-code a hex value or a magic margin in a component rule.

## Colour

Warm neutral surfaces, dark text, one accent (deep teal). Colour only ever communicates
hierarchy, state, or action — never decoration.

| Token | Value | Use |
|-------|-------|-----|
| `--akx-ink` | `#14201d` | Headings and body text |
| `--akx-ink-muted` | `#4c5a56` | Supporting text, metadata |
| `--akx-ink-subtle` | `#66736e` | Breadcrumbs, uppercase labels |
| `--akx-surface` | `#ffffff` | Page and card surfaces |
| `--akx-surface-sunken` | `#f7f6f3` | Notes panel, empty states, source blocks |
| `--akx-border` | `#e4e2dc` | Hairline separators |
| `--akx-border-strong` | `#cfccc4` | Emphasised outlines |
| `--akx-brand` | `#0f6e5a` | Primary actions, links, focus rings, AI accent |
| `--akx-brand-strong` | `#0b5646` | Hover/active, link text on a light tint |
| `--akx-brand-soft` | `#e9f2ef` | Source/provenance tint |
| `--akx-success` / `--akx-warning` / `--akx-danger` (+ `-soft`) | `#1a6b3c` / `#8a5300` / `#a32a1f` | Feedback states only |

Every foreground/background pair the interface uses meets WCAG AA; an axe-core run over the
app at 375, 390, 768, 1280, and 1440 px reports no violations. Status is never conveyed by
colour alone: every verdict also carries a word (`Correct`, `Not quite`) or an icon.

## Layout

| Token | Value | Use |
|-------|-------|-----|
| `--akx-content-max` | `1120px` | The centred app shell |
| `--akx-prose-max` | `68ch` | Reading surfaces: lesson notes, AI answers, explanations |
| `--akx-gutter` | `clamp(1.5rem, 4vw, 3.5rem)` | Page gutters (24 px → 56 px across viewports) |
| `--akx-section-y` | `clamp(2.5rem, 6vw, 4.5rem)` | Vertical rhythm between sections |
| `--akx-space-1` … `--akx-space-8` | `0.25rem` … `4rem` | A 4/8 spacing rhythm; no arbitrary margins |

Content is never edge-to-edge: paragraphs stop at the reading measure, and the shell keeps a
sane maximum width instead of stretching across a wide monitor.

## Radius, type

- `--akx-radius-sm` 4px (chips, small markers), `--akx-radius-md` 8px (buttons, notes,
  cards), `--akx-radius-lg` 12px, `--akx-radius-pill` reserved for compact labels whose
  behaviour calls for it. Not every element is a pill.
- Type scale: `--akx-text-micro` 0.75rem (uppercase labels), `--akx-text-meta` 0.875rem
  (metadata, helper text), `--akx-text-body` 1rem (body text on desktop), `--akx-text-lead`
  1.125rem (section leads). Lesson titles are 1.75rem, 1.4rem on phones.
- Font stack: `system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans Devanagari",
  "Nirmala UI", Arial, sans-serif` — no webfont download. `Noto Sans Devanagari` keeps
  Nepali text rendering with the reader's own glyphs on modest devices and slow connections.

## Components

| Class | Purpose |
|-------|---------|
| `.skip-link` | First focus stop; jumps to the study area |
| `.masthead`, `.brand` | Product identity and the Gemma 4 status chip |
| `.filters`, `.field` | The cascading goal → grade → subject → chapter → language controls |
| `.path`, `.path__sep` | The curriculum breadcrumb (separators are real text, not CSS decoration) |
| `.lesson__title`, `.prose`, `.chips` | Lesson header and reading column |
| `.note`, `.note--source`, `.note--warning`, `.note--danger`, `.disclosure` | Provenance, warnings, and errors; the source panel is labelled `SOURCE`, AI output is labelled as AI-generated |
| `.tabs`, `.panel` | The four study panels (Explain / Ask / Practise / Flashcards), one clear primary action each |
| `.quiz`, `.question`, `.option`, `.option--correct`, `.option--wrong`, `.review`, `.score` | Practice set, marking, review, and score |
| `.cards`, `.card` | Flashcards |
| `.state`, `.empty` | Loading, error, and empty states, with the next useful action named |
| `.progress`, `.stat` | Real browser-local numbers: lessons opened, attempts, best score |
| `.button`, `.button--primary` | Controls: one primary action per panel |

Provenance is structural, not decorative: lesson text sits in a bordered source panel; AI
output carries an AI label inside the result; practice questions are marked as generated
rather than official exam questions.

## Accessibility rules

- A skip link, semantic landmarks, and exactly one `h1`; heading levels never skip.
- Every focus stop draws a visible ring (`outline: 2px solid var(--akx-brand)`), including
  custom controls.
- Interactive targets are at least 44 × 44 px, which matters on the phones most students use.
- The study panels are ARIA tabs: `role="tab"`/`role="tabpanel"`, `aria-selected`, and
  arrow-key navigation with roving `tabindex`.
- Asynchronous results and validation messages use `role="status"`, and a failed AI call is
  reported as a failure — never rendered as an answer.
- Labels wrap instead of truncating; Devanagari and mathematical notation wrap or scroll
  rather than breaking the layout.
- `prefers-reduced-motion: reduce` turns off transitions and smooth scrolling.
