# Akshar

Akshar is a Vercel-hosted learning platform for Nepali students preparing for NEB, CEE, and IOE examinations. It combines study notes, bilingual content, and AI-assisted support in a focused learning flow.

## Overview

Akshar helps students:

- study structured lessons in English and Nepali
- continue from a dashboard-based learning path
- ask grounded questions about the current lesson
- generate short practice questions and flashcards
- review progress without relying on a separate backend app

The app is intentionally simple: one front end in `landing/`, one Vercel serverless function, and one deployment target.

## Project structure

- `landing/index.html` — app shell
- `landing/app.js` — study flow, lesson rendering, quiz logic, and dashboard behavior
- `landing/styles.css` — styles and layout
- `landing/lib/ai.mjs` — AI prompt and validation logic
- `landing/api/gemma.mjs` — server-side function that reads the key and calls Gemini
- `landing/data/lessons.json` — lesson content used by the app
- `landing/tests/` — Node-based validation suite
- `docs/` — deployment and design notes
- `AGENTS.md` — repository operating rules for AI agents

## Learning flow

1. Open the dashboard and choose a track, subject, and lesson.
2. Read the lesson content in English or Nepali.
3. Use grounded AI support to explain a concept or answer a question.
4. Practice with generated questions or flashcards.
5. Review progress and continue to the next chapter.

## AI behavior

Gemma 4 is used as a real part of the learning experience, but the model call stays server-side. The browser never sends the API key and never calls Google directly.

Supported actions:

- summary
- ask
- mcqs
- flashcards

Responses are validated before they are shown to the learner, and missing or malformed outputs are rejected instead of being presented as content.

## Local development

From the repository root:

```bash
node landing/scripts/dev.mjs
```

For mock mode:

```bash
node landing/scripts/dev.mjs --mock=ok
node landing/scripts/dev.mjs --mock=fail
node landing/scripts/dev.mjs --mock=empty
```

For real model calls, set the environment variable before running the app:

```bash
GOOGLE_API_KEY="your-key" node landing/scripts/dev.mjs
```

## Testing

Run the project test suite with:

```bash
node --test landing/tests/*.mjs
```

This project validates the lesson data, study-path logic, reading progress, quiz behavior, and deployment rules without depending on a live model call.

## Deployment

Akshar is deployed on Vercel only.

- Root directory: `landing`
- Framework preset: `Other`
- Build command: none
- Runtime: static files + one serverless function
- Required environment variable: `GOOGLE_API_KEY`

The deployment should not use a second host or any Streamlit setup.

## Documentation

- `AGENTS.md` — repository instructions and deployment rules
- `docs/DEPLOYMENT.md` — deployment and environment setup
- `docs/DESIGN.md` — design and product guidance

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Team

- Sagar Katwal
- Dipson Basnet
- Dhiraj Shrestha

## Notes

This repo is intentionally kept focused on one product path: a clear study experience for Nepali learners, using AI where it adds value and keeping the architecture simple and transparent.
