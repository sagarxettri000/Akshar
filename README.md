# Akshar

**A learning platform for Nepal — built by Team Nepluro.**

Akshar helps Nepali students understand concepts, practise exam-style questions, and prepare with confidence for **NEB Grade 11–12** and **CEE / IOE** entrance examinations. It pairs clear Nepali/English explanations with material students can inspect, and uses **Gemma 4** as a genuine part of the learning experience.

`NEB` · `CEE` · `IOE` · `Gemma 4` · `Python`

> **Status:** Active hackathon development. The learn → understand → practise flow runs end-to-end with Gemma 4; lesson content is being expanded.

## Live demo

- **App (Streamlit Community Cloud):** <https://akshar-nx6cm83qzbxznw8e6d7wpm.streamlit.app/>
- **Landing page (Vercel):** <https://akshar-nepluro.vercel.app/>

## The problem

Nepali learners preparing for NEB Grade 11–12 and entrance exams (CEE / IOE) often have to rely on generic answers or English-only resources that do not match their curriculum or language. Access to trustworthy, level-appropriate support is uneven, especially on modest devices and connections.

Akshar is being built to close that gap.

## The learning loop

Akshar is built around one trustworthy loop: **learn → understand → practise**.

1. Choose a track and topic — NEB Grade 11/12, CEE, or IOE.
2. Ask a question or open a reviewed practice question.
3. Get a clear, appropriately leveled explanation in Nepali or English, with source references when curriculum material is used.
4. Try a related question or a short knowledge check.
5. Receive encouraging, specific feedback and, where supported, track progress.

## Built on Gemma 4

The AI layer lives in [`ai_service.py`](ai_service.py) and calls Google's hosted Gemma 4 model through the official [`google-genai`](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api) SDK.

- **Model:** `gemma-4-26b-a4b-it`
- **Capabilities exposed to the app:**

  | Function | Returns |
  |----------|---------|
  | `generate_summary(lesson_text, api_key)` | A concise, faithful summary of a lesson |
  | `generate_mcqs(lesson_text, api_key, count=5)` | Validated multiple-choice questions |
  | `generate_flashcards(lesson_text, api_key, count=5)` | Validated `question` / `answer` flashcards |

- **Model output is never trusted blindly.** Responses are parsed defensively (plain JSON, fenced blocks, or JSON in prose), and every MCQ — options `A`–`D`, a single valid `answer`, a non-empty explanation — and flashcard is validated before the app uses it.
- **Failures are explicit.** `InvalidInputError`, `AIGenerationError`, and `AIResponseError` let the UI show honest loading/error/retry states instead of presenting a broken result as success.
- **Secrets stay secret.** The API key is never logged and is redacted from error messages.

## Repository structure

| Path | Purpose |
|------|---------|
| `app.py` | Streamlit app — the learn → understand → practise interface |
| `ai_service.py` | Gemma 4 integration — summaries, MCQs, and flashcards |
| `content.py` | Lesson loading and validation |
| `progress.py` | Session-scoped learner progress tracking |
| `data/lessons.json` | Sample curriculum lessons (team-authored study notes) |
| `tests/` | Unit tests for the AI service and content (no live API calls) |
| `requirements.txt` | Runtime dependencies |
| `requirements-dev.txt` | Development and testing dependencies |
| `landing/` | Static landing page deployed to Vercel |
| `docs/DEPLOYMENT.md` | Step-by-step deployment guide |
| `AGENTS.md` | Canonical, tool-agnostic instructions for AI coding agents |
| `GEMINI.md` | Gemini CLI entry point that imports `AGENTS.md` |
| `FIRST_PROMPT.md` | Read-only repository audit prompt |
| `TEAM_PLAYBOOK.md` | Team work split, MVP scope, and demo plan |
| `LICENSE` | MIT License |

## Getting started

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

Choose a track and topic, read the lesson, then use the **Explain**, **Practise**, and **Flashcards** tabs. AI output is clearly labelled and every question is validated before it is shown.

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
| `app.py` | [Streamlit Community Cloud](https://share.streamlit.io) | Streamlit needs a long-running Python server with WebSockets — Vercel cannot run it |
| `landing/` | [Vercel](https://vercel.com) | A static landing page, which Vercel is built for |

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the full walkthrough, including how to store the API key safely in Streamlit secrets.

## Design principles

- **Grounded, honest answers.** Curriculum answers cite the material actually shown, and AI-generated explanations and practice questions are clearly labelled.
- **Nepali-first accessibility.** Native Nepali/English support, correct Devanagari and mathematical notation, and readable text on small screens.
- **Low-bandwidth by design.** Built for modest devices and connections.
- **A real AI path.** Gemma 4 performs meaningful work in the learner flow — not a label attached to a canned answer.

## Team — Nepluro

| Member | Focus |
|--------|-------|
| Sagar Katwal | Learner experience / frontend |
| Dipson Basnet | Lesson content & validation |
| Dhiraj Shrestha | Gemma 4 / AI pipeline |

## Roadmap

- [x] Gemma 4 AI service (summaries, MCQs, flashcards) with validation and tests
- [x] Streamlit learning app with an Explain / Practise / Flashcards flow
- [x] Sample bilingual lesson content
- [x] Session-scoped learner progress tracking
- [ ] Broader, source-attributed curriculum content

## License

Released under the MIT License. See [`LICENSE`](LICENSE) for details.

## Lesson Content Contribution

Four original English-language lessons were contributed for NEB Grade 11 and Grade 12:

- Grade 11 Physics — Motion in a Straight Line
- Grade 11 Chemistry — Atomic Structure
- Grade 12 Biology — Cell Division
- Grade 12 Mathematics — Derivatives

The lessons are stored in `data/lessons.json` using the application's 7-field lesson schema
(`id`, `track`, `subject`, `topic`, `title`, `language`, `content`) and are loaded by `content.py`.

### Authoring Checklist

When adding a new lesson, use the following checklist to ensure consistency and quality:

- **Clear explanation:** The core concept is explained in accessible language, assuming the target grade level. Avoid dense paragraphs; use short sections with descriptive headings.
- **Correct examples:** Every formula, equation, or worked example is mathematically/scientifically correct. Units are consistent and SI‑compliant where applicable. Symbols and notation match the conventions used in Nepalese NEB/CEE/IOE curriculum.
- **Consistent terminology:** Technical terms (e.g., "momentum", "atomic number", "derivative", "continuity") are used uniformly. On first mention, retain the English term in parentheses if it helps learners recognise textbook terminology.
- **Appropriate difficulty:** Content stays at an introductory‑to‑intermediate level for the stated grade. Do not introduce advanced topics that go beyond the intended scope unless explicitly called out as enrichment.
- **Short self‑check:** Where useful, include a brief exercise (1‑2 questions) with answers. This reinforces learning and gives readers a way to verify understanding.

### Multilingual content (Nepali / English)

When contributing a Nepali‑language version of a lesson:

- **Preserve meaning, not wording:** Translate naturally; do not translate word‑for‑word. The Nepali version should convey the same concepts, examples, and conclusions as the English source.
- **Keep equations and units in English:** Mathematical notation, scientific symbols, unit abbreviations (e.g., `m/s²`, `amu), and standard formula symbols remain in English so they render correctly and match curriculum references.
- **Introduce technical terms in Nepali with English parenthesises:** On first mention, write the Nepali term followed by the English term in parentheses (e.g., "नेट बल (net force)"). This helps learners connect the two languages while reading textbook‑style content.
- **Do not change the JSON schema:** The 7‑field structure (`id`, `track`, `subject`, `topic`, `title`, `language`, `content`) is unchanged for multilingual lessons. Only the `language` field and the `content` text differ.
- **Name the ID by replacing the language suffix:** If the English lesson ID ends in `‑en`, the Nepali version should end in `‑ne` (e.g., `phy-newton-2-en` → `phy-newton-2‑ne`). This convention applies to lesson pairs that have both English and Nepali versions. The base portion of the ID (everything before the language suffix) stays the same, which keeps the pair linked and prevents duplicate IDs. Existing lessons without a Nepali version (such as `grade11-physics-motion` and `grade12-mathematics-derivatives`) omit the language suffix entirely. For future lesson pairs, use a matching `-en`/`-ne` suffix pattern to keep IDs consistent and searchable.
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
