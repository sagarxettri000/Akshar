# Akshar — Hackathon Demo Script

**App:** <https://akshar-nx6cm83qzbxznw8e6d7wpm.streamlit.app/>
**Landing page:** <https://akshar-nepluro.vercel.app/>
**Total time:** ~5 minutes
**Speakers:** Sagar Katwal, Dipson Basnet, Dhiraj Shrestha

---

## Speaker 1: Dipson Basnet (Problem & Educational Impact) — ~1.5 min

### [0:00 – 0:30] The Problem

> "Hi, I'm Dipson. Let me start with the problem we're solving.
>
> Students across Nepal preparing for NEB board exams, CEE, and IOE entrance tests often can't access affordable, personalised tutoring. Existing resources are expensive, not aligned to the Nepali curriculum, or only in English. We wanted to build something free, accessible, and genuinely useful for students here."

### [0:30 – 1:00] Our Solution

> "That's why we built **Akshar** — an AI-powered learning platform for Nepal.
>
> Akshar pairs short, original, syllabus-aligned lessons with Google's **Gemma 4** model. A student picks a track — NEB Grade 11/12, CEE, or IOE — and a topic, then reads the lesson and gets an explanation, practice questions, or flashcards in English or Nepali."

### [1:00 – 1:30] Educational Impact

> "The goal is simple: give every student with an internet connection a free, on-demand study assistant. Whether you're in Kathmandu or a rural village, Akshar helps explain concepts, check understanding, and prepare for exams — through a simple web app that works on any device."

---

## Speaker 2: Sagar Katwal (Technical Approach & AI Implementation) — ~1.5 min

### [1:30 – 2:00] Technical Overview

> "Thanks, Dipson. I'm Sagar, and I'll cover the technical side.
>
> Akshar is built in **Python** with **Streamlit**, so the interface is responsive and works on desktop and mobile browsers. Lesson content lives in a single JSON file — each lesson has a track, subject, topic, title, language, and body text — so we can add lessons without changing any code."

### [2:00 – 2:30] AI Implementation

> "The AI layer is `ai_service.py`, which calls Google's hosted **Gemma 4** model (`gemma-4-26b-a4b-it`) through the official `google-genai` SDK. It exposes four functions: a grounded Q&A tutor, a summary generator, multiple-choice questions, and flashcards.
>
> Critically, we never trust the model blindly. Every response is parsed defensively and validated — options A–D, a single valid answer, a non-empty explanation — before it reaches the student. The API key comes from Streamlit secrets or an environment variable and is redacted from errors; it is never hardcoded."

### [2:30 – 3:00] Why Gemma 4

> "We chose Gemma 4 because it's a capable, open model from Google with a straightforward API, and it handles educational content well across subjects. It gave us the best balance of quality, speed, and ease of integration.
>
> The architecture stays deliberately simple: Streamlit UI → Python modules (`ai_service`, `content`, `progress`) → Gemma 4."

---

## Speaker 3: Dhiraj Shrestha (Live Demo) — ~1.5 min

### [3:00 – 3:30] Demo Setup

> "Hi everyone, I'm Dhiraj. Let me show how Akshar works. The app is already deployed on Streamlit Community Cloud, and we also have a landing page on Vercel that links to it."

**Demo steps:**

1. **Choose a lesson** — "In the sidebar I'll pick the NEB Grade 11 track, Physics, Newton's Laws of Motion. We can also switch the lesson language to Nepali."
2. **Open the lesson** — "Here's Newton's Second Law — our own study notes, and we label them clearly as not official NEB material."
3. **Explain tab** — "If a student needs a clearer explanation, they click **Generate a summary** and Gemma 4 writes one grounded in this lesson. We show an AI notice so nobody mistakes it for an official source."
4. **Ask tab** — "Better still, the student can ask their own question. Gemma 4 answers using only this lesson, tells them when the lesson doesn't cover something instead of inventing facts, and can reply in **Nepali** if they switch the answer language."

### [3:30 – 4:00] Practice & Progress

> "Learning needs practice, so they open the **Practise** tab and generate three questions. They choose answers, click **Check answers**, and get feedback for each question plus a score. The sidebar tracks lessons practised, practice attempts, and their average best score — all within the session, so we collect no personal data."

### [4:00 – 4:30] Flashcards & Deployment

**Demo steps:**

5. **Flashcards tab** — "The **Flashcards** tab turns the lesson into quick revision cards."
6. **Deployment** — "We push to GitHub. Streamlit Community Cloud runs the app and keeps the API key in secrets; Vercel hosts the landing page. Both redeploy automatically on every push."

---

## All Speakers: Limitations & Conclusion — ~30 sec

### [4:30 – 5:00] Limitations

> "As a hackathon prototype, Akshar has some limitations:
>
> - We have **14 sample lessons** across NEB 11/12, CEE, and IOE — not the full syllabus — with the core lessons available in both English and Nepali.
> - AI output, while helpful, should be verified against official textbooks.
> - The app requires an internet connection and a Gemini API key.
> - Progress tracking is per-session for now; there are no user accounts yet."

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
