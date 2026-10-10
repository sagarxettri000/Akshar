# Akshar — Hackathon Demo Script

**Product link (Vercel):** <https://akshar-nepluro.vercel.app/> — the Vercel project serves
`landing/`: one static page plus one serverless function.
**Run it locally:** `node landing/scripts/dev.mjs` (add `--mock=ok` to exercise the AI flows
without a key; say so out loud if you demo with the mock).
**Total time:** ~5 minutes
**Speakers:** Sagar Katwal, Dipson Basnet, Dhiraj Shrestha

> **Platform and deployment rules:** everything here runs on **Vercel** — one front end, one
> project. **Streamlit is not used**, and nothing is deployed, redeployed, or republished for
> a demo. There is exactly one published deployment, the Vercel project above. See
> [`AGENTS.md` §10](AGENTS.md).

---

## Speaker 1: Dipson Basnet (Problem & Educational Impact) — ~1.5 min

### [0:00 – 0:30] The Problem

> "Hi, I'm Dipson. Let me start with the problem we're solving.
>
> Students across Nepal preparing for NEB board exams, CEE, and IOE entrance tests often can't access affordable, personalised tutoring. Existing resources are expensive, not aligned to the Nepali curriculum, or only in English. We wanted to build something free, accessible, and genuinely useful for students here."

### [0:30 – 1:00] Our Solution

> "That's why we built **Akshar** — an AI-powered learning platform for Nepal.
>
> Akshar pairs short, original, syllabus-aligned lessons with Google's **Gemma 4** model. A student picks an exam goal — NEB, CEE, or IOE — then a grade, a subject and a chapter, reads the lesson, and gets an explanation, answers to their own questions, practice questions, or flashcards in English or Nepali."

### [1:00 – 1:30] Educational Impact

> "The goal is simple: give every student with an internet connection a free, on-demand study assistant. Whether you're in Kathmandu or a rural village, Akshar helps explain concepts, check understanding, and prepare for exams — through a simple web app that works on any device, including the phone in your pocket."

---

## Speaker 2: Sagar Katwal (Technical Approach & AI Implementation) — ~1.5 min

### [1:30 – 2:00] Technical Overview

> "Thanks, Dipson. I'm Sagar, and I'll cover the technical side.
>
> Akshar is one web page. There is no framework, no build step, and no runtime dependency to install: `landing/` holds the page, the script, the stylesheet, the lesson data, and **one serverless function**. Vercel serves the files and runs that function, so the whole product is small, fast, and cheap to host — which matters for students on modest connections.
>
> Lesson content lives in a single JSON file — each lesson has an id, track, subject, topic, title, language, and body — so we can add lessons without touching code. The test suite validates every lesson record and checks that all tracks and both languages are covered."

### [2:00 – 2:30] AI Implementation

> "The Gemma 4 pipeline is `landing/lib/ai.mjs`: it builds the prompts, parses the response, and validates it. The browser never talks to Google — it sends an action and a lesson id to `landing/api/gemma.mjs`, our only serverless function, which holds the API key and calls `gemma-4-26b-a4b-it` through the Gemini API. The key never reaches the browser, is never logged, and is redacted from errors.
>
> Critically, we never trust the model blindly. Every response is parsed defensively — plain JSON, fenced blocks, or JSON inside a sentence — and a question needs four options A–D, exactly one marked answer, and a non-empty explanation before it is shown. Malformed items are dropped, and a failed call is shown as an error, never as an answer."

### [2:30 – 3:00] Why Gemma 4

> "We chose Gemma 4 because it's a capable, open model from Google with a straightforward API, and it handles educational content well across subjects. It gave us the best balance of quality, speed, and ease of integration.
>
> The architecture stays deliberately simple: one page → one function → one pipeline → Gemma 4."

---

## Speaker 3: Dhiraj Shrestha (Live Demo) — ~1.5 min

### [3:00 – 3:30] Demo Setup

> "Hi everyone, I'm Dhiraj. Let me show how Akshar works. This is the deployed app — one Vercel project, no other host involved, and nothing is deployed or redeployed while we talk."

**Demo steps:**

1. **The dashboard** — This is what a student sees first. **Continue learning** is empty on a fresh browser and says so honestly: no invented streaks or completion, just a starting chapter. **Learning pathways** shows NEB, CEE, and IOE with their real chapter, subject, and language counts, and **Practise next** recommends from real attempts.
2. **Open a pathway** — NEB takes us into **Study**. Set the exam goal to **NEB**, keep the grade, then pick Physics and Newton's Laws of Motion. Switch the **Language** to Nepali to show bilingual support; the breadcrumb under the filters tracks every choice.
3. **Read the lesson** — Our own study notes, in the **SOURCE** panel, labelled as not official NEB material, with a reading-progress bar, a text-size control, a bookmark, and previous/next chapter navigation.
4. **Explain tab** — Click **Explain this lesson** and Gemma 4 writes an explanation grounded in that lesson, labelled as AI-generated so nobody mistakes it for an official source.
5. **Ask tab** — Better still, the student asks their own question. The assistant suggests a few from the chapter on screen, Gemma 4 answers using only this lesson, tells them when the lesson doesn't cover something instead of inventing facts, and can reply in **Nepali** if they set the answer language.

### [3:30 – 4:00] Practice & Progress

> "Learning needs practice, so they open the **Practise** tab and choose a mode. In **practice** mode every answer is marked straight away with the reason; in **exam** mode nothing is revealed until they mark the whole set, and if a question is still blank the app asks before it submits. The progress bar counts the questions they have answered.
>
> The result leads with the score, then the correct / incorrect / unanswered split, their accuracy, what to revise, and a review of every question against the notes — with new questions, a retry, or a way back to the dashboard. The panel reminds them these questions are generated, not official exam questions.
>
> Back on the **dashboard**, **Continue learning** now names the chapter they just studied, and **Your progress** shows chapters opened, practice attempts, and their best score — all stored in the browser, so we collect no personal data and need no accounts."

### [4:00 – 4:30] Flashcards & Deployment

**Demo steps:**

6. **Flashcards tab** — The **Flashcards** tab turns the lesson into quick revision cards with **Build flashcards**.
7. **Deployment** — One Vercel project serves `landing/` and runs the one function; it redeploys automatically when a change is merged into `main`. Our CI is the Node test suite — the AI pipeline, the dashboard and study-path logic, reading progress, quiz scoring, the lesson data, and the deployment guards. Nothing is deployed or redeployed for this demo.

---

## All Speakers: Limitations & Conclusion — ~30 sec

### [4:30 – 5:00] Limitations

> "As a hackathon prototype, Akshar has some limitations:
>
> - We have **21 sample lessons** across NEB 11/12, CEE, and IOE — not the full syllabus; five topics exist in both English and Nepali.
> - Our notes are original text written for this build: not official curriculum material, and source-attributed content is the next thing we are building.
> - AI output, while grounded in the lesson shown, should be verified against official textbooks.
> - The app needs an internet connection and a configured Gemma 4 API key; without the key it says so plainly and serves the notes only.
> - Progress is stored in the browser only; there are no user accounts yet."

### Conclusion

> "Our vision is to grow Akshar into a full learning platform for Nepali students — the complete syllabus, more subjects, saved progress, and quality education accessible to everyone.
>
> Thank you! We're happy to take any questions."

---

## Quick Reference

| Time | Speaker | Topic |
|---|---|---|
| 0:00 – 1:30 | Dipson | Problem, solution, educational impact |
| 1:30 – 3:00 | Sagar | Technical architecture, Gemma 4 |
| 3:00 – 4:30 | Dhiraj | Live demo and deployment |
| 4:30 – 5:00 | All | Limitations and conclusion |
