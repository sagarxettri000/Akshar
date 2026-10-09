# Akshar

**A learning platform for Nepal — built by Team Nepluro.**

Akshar helps Nepali students understand concepts, practise exam-style questions, and prepare with confidence for **NEB Grade 11–12** and **CEE / IOE** entrance examinations. It pairs clear Nepali/English explanations with material students can inspect, and uses **Gemma 4** as a genuine part of the learning experience.

`NEB` · `CEE` · `IOE` · `Gemma 4` · `Python`

> **Status:** Active hackathon development. The learn → understand → practise flow runs end-to-end with Gemma 4; lesson content is being expanded.

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
| Dipson Basnet | Gemma 4 / AI pipeline |
| Dhiraj Shrestha | Learning content, practice & validation |

## Roadmap

- [x] Gemma 4 AI service (summaries, MCQs, flashcards) with validation and tests
- [x] Streamlit learning app with an Explain / Practise / Flashcards flow
- [x] Sample bilingual lesson content
- [x] Session-scoped learner progress tracking
- [ ] Broader, source-attributed curriculum content

## License

Released under the MIT License. See [`LICENSE`](LICENSE) for details.
