# Akshar

**A learning platform for Nepal — built by Team Nepluro.**

Akshar helps Nepali students understand concepts, practise exam-style questions, and prepare with confidence for NEB Grade 11–12 and CEE/IOE entrance examinations. It pairs clear Nepali/English explanations with inspectable material and uses Gemma 4 as a genuine part of the learning experience.

`NEB` · `CEE` · `IOE` · `Gemma 4` · one static page + one serverless function · no build step

## Status

Active hackathon development. The learn → understand → practise flow runs end-to-end with Gemma 4; all 21 lessons (12 English, 9 Nepali) are served from a single lesson file, and 65 Node tests pass without calling the live model.

## Live link

- **Study app (Vercel):** <https://akshar-nepluro.vercel.app/> — the product link. The Vercel
  project serves [`landing/`](landing): a static page plus one serverless function. It
  follows `main`, so a change reaches students after it is merged there and deployed.

There is exactly **one published deployment**. Deploying, republishing, switching hosts, or
adding another project needs an explicit request from a human — [`AGENTS.md` §10](AGENTS.md)
is binding.

## The learning loop

Akshar is built around one trustworthy loop: **learn → understand → practise**.

1. **Choose where you are** — an exam goal (NEB, CEE, or IOE), a grade where the track has one, then a subject, a chapter, and the study language (English or Nepali).
2. **Read the lesson** — original team-authored study notes, clearly labelled as not official NEB/IOE/CEE material.
3. **Understand** — an AI-generated explanation, a question you ask yourself, or flashcards; Gemma 4 answers using only the selected lesson and says so plainly when the lesson does not cover the question.
4. **Practise** — generated multiple-choice questions with per-question marking, a score, and an explanation for every answer. Generated questions are labelled as not official exam questions.
5. **Track progress** — lessons opened, practice attempts, and best score, kept in the browser's own storage.

## The problem

Nepali learners preparing for NEB Grade 11–12 and entrance exams (CEE/IOE) often have to rely on generic answers or English-only resources that do not match their curriculum or language. Access to trustworthy, level-appropriate support is uneven, especially on modest devices and connections.

Akshar is being built to close that gap.

## Built on Gemma 4

The model call lives in [`landing/lib/ai.mjs`](landing/lib/ai.mjs) and is reached only through [`landing/api/gemma.mjs`](landing/api/gemma.mjs), the one serverless function. The browser sends an action and a lesson id — never a prompt and never a key.

- **Model:** `gemma-4-26b-a4b-it` over the Gemini API (`generateContent`), key in the `x-goog-api-key` header.
- **Capabilities exposed to the app:**

  | Action | Returns |
  |--------|---------|
  | `summary` | A concise, faithful summary of the selected lesson |
  | `ask` | A grounded answer to a student's question, optionally forced to English or Nepali |
  | `mcqs` | Validated multiple-choice questions |
  | `flashcards` | Validated `question` / `answer` flashcards |

- **Answers stay grounded.** The tutor answers using only the current lesson and is instructed to say so plainly when the lesson does not cover a question instead of inventing facts.
- **Model output is never trusted blindly.** Responses are parsed defensively (plain JSON, fenced blocks, or JSON inside prose), and every MCQ — options A–D, a single valid answer, a non-empty explanation — and flashcard is validated before the app uses it. Malformed items are dropped rather than shown.
- **Failures are explicit.** Timeouts, quota/auth errors, and upstream failures produce honest messages, and a failure is never rendered as an answer.
- **Secrets stay secret.** The key is read from the server environment only, is never returned to the browser, is never logged, and is redacted from error messages.

## Repository structure

| Path | Purpose |
|------|---------|
| `landing/index.html` | The app shell |
| `landing/app.js` | Study state, study-path selection, grading, progress, and the four AI flows |
| `landing/styles.css` | The whole design system and component layer |
| `landing/lib/ai.mjs` | Prompts, defensive parsing, validation, and transport — the one Gemma 4 pipeline |
| `landing/api/gemma.mjs` | The one serverless function; the only place the API key is read |
| `landing/data/lessons.json` | The lesson file the app serves (21 lessons, English + Nepali) |
| `landing/scripts/dev.mjs` | Local dev server with an optional mock Gemma upstream; no dependencies |
| `landing/tests/` | Node tests: AI pipeline, study selection, lesson data, deployment guards |
| `docs/DEPLOYMENT.md` | Running and deployment guide |
| `docs/DESIGN.md` | Design system reference |
| `AGENTS.md` | Canonical, tool-agnostic instructions for AI coding agents |
| `GEMINI.md` | Gemini CLI entry point that imports `AGENTS.md` |
| `FIRST_PROMPT.md` | Read-only repository audit prompt |
| `TEAM_PLAYBOOK.md` | Team work split, scope, and demo plan |
| `LICENSE` | MIT License |

## Getting started

There is nothing to install: the app has no runtime dependencies, no build step, and no package manifest.

```bash
node landing/scripts/dev.mjs                 # http://127.0.0.1:3000 — reading works, AI needs a key
node landing/scripts/dev.mjs --mock=ok       # same, plus a fake Gemma upstream — no key needed
node landing/scripts/dev.mjs --mock=fail     # exercise the error state
node landing/scripts/dev.mjs --mock=empty    # exercise the "nothing usable came back" state
node landing/scripts/dev.mjs --host=0.0.0.0 --port 3000   # bind all interfaces (containers, previews)

GOOGLE_API_KEY="your-key" node landing/scripts/dev.mjs    # real Gemma 4 calls
```

With `--mock`, the real handler, the real prompts, and the real validators run against a stand-in upstream — the honest way to work on the interface without a key or without spending quota. `--mock` is a development tool: it is never part of a deployment.

### Run the tests

```bash
node --test landing/tests/*.mjs
```

The tests never call the live model.

## Deployment

One Vercel project (Root Directory `landing`, framework preset **Other**, no build command) serves `landing/` as static files plus `landing/api/gemma.mjs`. The only environment variable is `GOOGLE_API_KEY`, set in the host's environment variables — never in the repository, a file, chat, or a log.

[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) has the walkthrough; [`AGENTS.md` §10](AGENTS.md) has the binding rules (one published deployment, never deploy without being asked, never add a second host).

## Design principles

- **Grounded, honest answers.** Curriculum answers cite the material actually shown, and AI-generated explanations and practice questions are clearly labelled.
- **Nepali-first accessibility.** Native Nepali/English support, correct Devanagari and mathematical notation, and readable text on small screens.
- **Low-bandwidth by design.** No build step, no webfont download, and no dependency the browser has to fetch beyond the app's own files.
- **A real AI path.** Gemma 4 performs meaningful work in the learner flow — not a label attached to a canned answer.
- **One source of truth per concern.** Lesson data, prompts and validation, study-path logic, and styles each live in exactly one file, checked by the test suite (see [`docs/DESIGN.md`](docs/DESIGN.md)).

## Team — Nepluro

| Member | Focus |
|--------|-------|
| Sagar Katwal | Learner experience / frontend |
| Dipson Basnet | Lesson content & validation |
| Dhiraj Shrestha | Gemma 4 / AI pipeline |

## Roadmap

- [x] Gemma 4 AI pipeline (summary, grounded Q&A, MCQs, flashcards) with validation and tests
- [x] Web app with Explain / Ask / Practise / Flashcards flow, served from `landing/`
- [x] Grounded bilingual Q&A tutor (English / Nepali replies)
- [x] Bilingual lesson content (English + Nepali across every track)
- [x] Browser-local learner progress
- [x] One front end and one deployment: the earlier Python/Streamlit app was retired
- [ ] Broader, source-attributed curriculum content

## License

Released under the MIT License. See [`LICENSE`](LICENSE) for details.

## Lesson content contribution

Six original English-language lessons were contributed for NEB Grade 11 and Grade 12:

- Grade 11 Physics — Motion in a Straight Line
- Grade 11 Chemistry — Atomic Structure
- Grade 12 Biology — Cell Division
- Grade 12 Mathematics — Derivatives
- Grade 11 Chemistry — Chemical Bonding
- Grade 12 Biology — Basic Principles of Genetics

All lessons are stored in `landing/data/lessons.json` using the app's 7-field schema (`id`, `track`, `subject`, `topic`, `title`, `language`, `content`). That one file is what the browser and the serverless function both read — there is no second copy to keep in step.

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
- **Keep equations and units in English:** Mathematical notation, scientific symbols, unit abbreviations (e.g., `m/s²`, `amu`), and standard formula symbols remain in English so they render correctly and match curriculum references.
- **Introduce technical terms in Nepali with English parentheses:** On first mention, write the Nepali term followed by the English term in parentheses (e.g., "नेट बल (net force)"). This helps learners connect the two languages while reading textbook‑style content.
- **Do not change the JSON schema:** The 7-field structure (`id`, `track`, `subject`, `topic`, `title`, `language`, `content`) is unchanged for multilingual lessons. Only the `language` field and the `content` text differ.
- **Name the ID by replacing the language suffix:** If the English lesson ID ends in `-en`, the Nepali version should end in `-ne` (e.g., `phy-newton-2-en` → `phy-newton-2-ne`). This convention applies to lesson pairs that have both English and Nepali versions. The base portion of the ID (everything before the language suffix) stays the same, which keeps the pair linked and prevents duplicate IDs. Existing lessons without a Nepali version (such as `grade11-physics-motion` and `grade12-mathematics-derivatives`) omit the language suffix entirely. For future lesson pairs, use a matching `-en`/`-ne` suffix pattern to keep IDs consistent and searchable.
- **Validate the same way:** run `node --test landing/tests/lessons.test.mjs` and confirm the new lesson passes every check.

### Validating lesson data

```bash
node --test landing/tests/lessons.test.mjs
```

The checks cover JSON structure, the required fields, unique and non-empty ids, non-empty strings, valid language codes (`en`, `ne`), and that every track and both languages are still covered.

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
