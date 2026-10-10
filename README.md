# Akshar

**A learning platform for Nepal — built by Team Nepluro.**

Akshar helps Nepali students understand concepts, practise exam-style questions, and prepare with confidence for NEB Grade 11–12 and CEE/IOE entrance examinations. It pairs clear Nepali/English explanations with inspectable material and uses Gemma 4 as a genuine part of the learning experience.

`NEB` · `CEE` · `IOE` · `Gemma 4` · `Python` · `Streamlit`

## Status

Active hackathon development. The learn → understand → practise flow runs end-to-end with Gemma 4; all 21 lessons (12 English, 9 Nepali) are validated and loaded. 138 unit tests pass without calling the live model.

## The learning loop

Akshar is built around one trustworthy loop: **learn → understand → practise**.

1. **Choose a track and topic** — NEB Grade 11/12, CEE, or IOE.
2. **Read the lesson** — original team-authored study notes, clearly labelled as not official NEB/IOE/CEE material.
3. **Understand** — get an AI-generated summary, ask a question, or review flashcards; Gemma 4 answers using only the selected lesson and says so plainly when the lesson does not cover the question.
4. **Practise** — generate multiple-choice questions, choose answers, check answers, and review missed questions with explanations. Progress is tracked per session.

## Live demo

- **Study app (Vercel):** <https://akshar-nepluro.vercel.app/> — the HTML/CSS/JS app in
  [`landing/`](landing), served as static files plus one serverless Gemma 4 function.
  It picks up changes on the next Vercel deploy from `main`.
- **Streamlit app:** <https://akshar-nx6cm83qzbxznw8e6d7wpm.streamlit.app/> — the same
  learn → understand → practise loop implemented in Streamlit.

Both front ends share one lesson file, one set of prompts, and one set of validators; the
test suite fails if they drift apart.

## The problem

Nepali learners preparing for NEB Grade 11–12 and entrance exams (CEE/IOE) often have to rely on generic answers or English-only resources that do not match their curriculum or language. Access to trustworthy, level-appropriate support is uneven, especially on modest devices and connections.

Akshar is being built to close that gap.

## Built on Gemma 4

The AI layer lives in [`ai_service.py`](ai_service.py) and calls Google's hosted Gemma 4 model through the official [`google-genai`](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api) SDK.

- **Model:** `gemma-4-26b-a4b-it`
- **Capabilities exposed to the app:**

  | Function | Returns |
  |----------|---------|
  | `generate_summary(lesson_text, api_key)` | A concise, faithful summary of a lesson |
  | `ask_question(lesson_text, question, api_key, history=…)` | A grounded answer to a student's question, optionally forced to English or Nepali |
  | `generate_mcqs(lesson_text, api_key, count=5)` | Validated multiple-choice questions |
  | `generate_flashcards(lesson_text, api_key, count=5)` | Validated `question` / `answer` flashcards |

- **Answers stay grounded.** The tutor answers using only the current lesson, keeps a short conversation history for context, and is instructed to say so plainly when the lesson does not cover a question instead of inventing facts. Learners can choose the reply language (match the lesson, English, or Nepali).

- **Model output is never trusted blindly.** Responses are parsed defensively (plain JSON, fenced blocks, or JSON in prose), and every MCQ — options A–D, a single valid answer, a non-empty explanation — and flashcard is validated before the app uses it.

- **Failures are explicit.** `InvalidInputError`, `AIGenerationError`, and `AIResponseError` let the UI show honest loading/error/retry states instead of presenting a broken result as success.

- **Secrets stay secret.** The API key is never logged and is redacted from error messages.

## Repository structure

| Path | Purpose |
|------|---------|
| `app.py` | Streamlit app — the learn → understand → practise interface |
| `ui.py` | Design system: tokens, injected stylesheet, shared UI blocks |
| `ai_service.py` | Gemma 4 integration — summaries, grounded Q&A, MCQs, and flashcards |
| `content.py` | Lesson loading and validation |
| `progress.py` | Session-scoped learner progress tracking |
| `data/lessons.json` | Sample curriculum lessons (team-authored study notes) |
| `tests/` | Unit tests for the AI service, content, progress, design tokens, and the web app — including cross-language prompt/validator parity (no live API calls) |
| `requirements.txt` | Runtime dependencies |
| `requirements-dev.txt` | Development and testing dependencies |
| `landing/` | **Web app deployed to Vercel** — `index.html`, `app.js`, `styles.css`, `data/lessons.json`, `api/gemma.mjs` (the only place the API key is used; prompts and validation in `lib/ai.mjs`), and `scripts/dev.mjs` (local server, optional mock upstream) |
| `docs/DESIGN.md` | Design system: colour, layout, type, components, accessibility |
| `docs/DEPLOYMENT.md` | Step-by-step deployment guide |
| `AGENTS.md` | Canonical, tool-agnostic instructions for AI coding agents |
| `GEMINI.md` | Gemini CLI entry point that imports `AGENTS.md` |
| `FIRST_PROMT.md` | Read-only repository audit prompt |
| `TEAM_PLAYBOOK.md` | Team work split, MVP scope, and demo plan |
| `LICENSE` | MIT License |

## Getting started

### The web app (no build step)

```bash
node landing/scripts/dev.mjs              # http://127.0.0.1:3000
node landing/scripts/dev.mjs --mock=ok    # run the AI flows without an API key
```

### The Streamlit app

Requires **Python 3.10+**.

```bash
pip install -r requirements-dev.txt
```

### Configure your API key

Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey), then copy the example secrets file and fill it in:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Or set an environment variable:

```bash
export GOOGLE_API_KEY=your-key-here
```

`secrets.toml` is gitignored — never commit real keys.

### Run the app

```bash
streamlit run app.py
```

Choose a track and topic, read the lesson, then use the **Explain**, **Ask**, **Practise**, and **Flashcards** tabs. AI output is clearly labelled and every question is validated before it is shown. In **Ask**, type a question and choose whether Gemma 4 replies in English or Nepali.

### Run the tests

```bash
python -m pytest tests/ -q
```

The tests use mocks and never call the live model.

### Quick script check

```python
from ai_service import generate_summary

print(generate_summary("Newton's second law: F = m a.", api_key="YOUR_KEY"))
```

## Deployment

| Part | Where | Why |
|------|-------|-----|
| `landing/` (the study app) | [Vercel](https://vercel.com) | Static HTML/CSS/JS plus one serverless function — no build step, no npm dependencies |
| `app.py` (Streamlit) | App runners such as [Streamlit Community Cloud](https://share.streamlit.io) | Its alternative UI needs a long-running Python server with WebSockets |

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the full walkthrough, including how to store the API key safely in Streamlit secrets.

## Design principles

- **Grounded, honest answers.** Curriculum answers cite the material actually shown, and AI-generated explanations and practice questions are clearly labelled.
- **Nepali-first accessibility.** Native Nepali/English support, correct Devanagari and mathematical notation, and readable text on small screens.
- **Low-bandwidth by design.** Built for modest devices and connections.
- **A real AI path.** Gemma 4 performs meaningful work in the learner flow — not a label attached to a canned answer.
- **One design system.** `ui.py`, `.streamlit/config.toml`, and `landing/styles.css` share the same tokens, checked by `tests/test_design_tokens.py` (see [`docs/DESIGN.md`](docs/DESIGN.md)).

## Team — Nepluro

| Member | Focus |
|--------|-------|
| Sagar Katwal | Learner experience / frontend |
| Dipson Basnet | Lesson content & validation |
| Dhiraj Shrestha | Gemma 4 / AI pipeline |

## Roadmap

- [x] Gemma 4 AI service (summaries, grounded Q&A, MCQs, flashcards) with validation and tests
- [x] Streamlit learning app with Explain / Ask / Practise / Flashcards flow
- [x] Grounded bilingual Q&A tutor (English / Nepali replies)
- [x] Bilingual lesson content (English + Nepali across every track)
- [x] Session-scoped learner progress tracking
- [ ] Broader, source-attributed curriculum content

## License

Released under the MIT License. See [`LICENSE`](LICENSE) for details.

## Lesson Content Contribution

Six original English-language lessons were contributed for NEB Grade 11 and Grade 12:

- Grade 11 Physics — Motion in a Straight Line
- Grade 11 Chemistry — Atomic Structure
- Grade 12 Biology — Cell Division
- Grade 12 Mathematics — Derivatives
- Grade 11 Chemistry — Chemical Bonding
- Grade 12 Biology — Basic Principles of Genetics

The lessons are stored in `data/lessons.json` using the application's 7-field lesson schema (`id`, `track`, `subject`, `topic`, `title`, `language`, `content`) and are loaded by `content.py`.

### Authoring checklist

When adding a new lesson, use the following checklist to ensure consistency and quality:

- **Clear explanation:** The core concept is explained in accessible language, assuming the target grade level. Avoid dense paragraphs; use short sections with descriptive headings.
- **Correct examples:** Every formula, equation, or worked example is mathematically/scientifically correct. Units are consistent and SI‑compliant where applicable. Symbols and notation match the conventions used in Nepalese NEB/CEE/IOE curriculum.
- **Consistent terminology:** Technical terms (e.g., "momentum", "atomic number", "derivative", "continuity") are used uniformly. On first mention, retain the English term in parentheses if it helps learners recognise textbook terminology.
- **Appropriate difficulty:** Content stays at an introductory‑to‑intermediate level for the stated grade. Do not introduce advanced topics that go beyond the intended scope unless explicitly called out as enrichment.
- **Short self‑check:** Where useful, include a brief exercise (1‑2 questions) with answers. This reinforces learning and gives readers a way to verify understanding.

### Multilingual content (Nepali / English)

When contributing a Nepali-language version of a lesson:

- **Preserve meaning, not wording:** Translate naturally; do not translate word‑for‑word. The Nepali version should convey the same concepts, examples, and conclusions as the English source.
- **Keep equations and units in English:** Mathematical notation, scientific symbols, unit abbreviations (e.g., `m/s²`, `amu), and standard formula symbols remain in English so they render correctly and match curriculum references.
- **Introduce technical terms in Nepali with English parenthesises:** On first mention, write the Nepali term followed by the English term in parentheses (e.g., "नेट बल (net force)"). This helps learners connect the two languages while reading textbook‑style content.
- **Do not change the JSON schema:** The 7-field structure (`id`, `track`, `subject`, `topic`, `title`, `language`, `content`) is unchanged for multilingual lessons. Only the `language` field and the `content` text differ.
- **Name the ID by replacing the language suffix:** If the English lesson ID ends in `-en`, the Nepali version should end in `-ne` (e.g., `phy-newton-2-en` → `phy-newton-2‑ne`). This convention applies to lesson pairs that have both English and Nepali versions. The base portion of the ID (everything before the language suffix) stays the same, which keeps the pair linked and prevents duplicate IDs. Existing lessons without a Nepali version (such as `grade11-physics-motion` and `grade12-mathematics-derivatives`) omit the language suffix entirely. For future lesson pairs, use a matching `-en`/`-ne` suffix pattern to keep IDs consistent and searchable.
- **Validate the same way:** Run `python validate_lessons.py` and `python -m pytest tests/test_validate_lessons.py tests/test_content.py -q` to confirm the new lesson passes all checks.

### Validating lesson data

Run the standalone validator (no dependencies beyond Python 3):

```bash
python validate_lessons.py
```

Run the lesson-related tests:

```bash
python -m pytest tests/test_validate_lessons.py tests/test_content.py -q
```

The validator checks JSON syntax, root structure, required fields, unique IDs, non-empty strings, and valid language codes (`en`, `ne`). All tests use temporary files and never modify the real `data/lessons.json`.

## Lesson pairs in detail

| English lesson ID | Nepali lesson ID | Track | Subject | Topic |
|---|---|---|---|---|
| `phy-newton-2-en` | `phy-newton-2-ne` | NEB Grade 11 | Physics | Newton's Laws of Motion |
| `bio-photosynthesis-en` | `bio-photosynthesis-ne` | NEB Grade 12 | Biology | Photosynthesis |
| `chem-acids-bases-en` | `chem-acids-bases-ne` | NEB Grade 11 | Chemistry | Acids, Bases and Salts |
| `cee-kinematics-en` | `cee-kinematics-ne` | CEE | Physics | Kinematics |
| `ioe-quadratics-en` | `ioe-quadratics-ne` | IOE | Mathematics | Algebra |
| `grade11-physics-motion` | (Nepali not yet) | NEB Grade 11 | Physics | Motion in a Straight Line |
| `grade11-chemistry-atomic-structure` | `grade11-chemistry-atomic-structure-ne` | NEB Grade 11 | Chemistry | Atomic Structure |
| `grade12-biology-cell-division` | `grade12-biology-cell-division-ne` | NEB Grade 12 | Biology | Cell Division |
| `grade12-mathematics-derivatives` | (Nepali not yet) | NEB Grade 12 | Mathematics | Derivatives |
| `grade12-mathematics-limits-continuity` | (Nepali not yet) | NEB Grade 12 | Mathematics | Limits and Continuity |
| `grade11-chemistry-chemical-bonding` | (Nepali not yet) | NEB Grade 11 | Chemistry | Chemical Bonding |

**21 lessons total: 12 English + 9 Nepali across 5 complete English–Nepali pairs.**