# Akshar — Hackathon Demo Script

**Total time:** ~5 minutes  
**Speakers:** Sagar Katwal, Dipson Basnet, Dhiraj Shrestha

---

## Speaker 1: Dipson Basnet (Problem & Educational Impact) — ~1.5 min

### [0:00 – 0:30] The Problem

> "Hi, I'm Dipson. Let me start with the problem we're solving.
>
> Students across Nepal preparing for NEB board exams, CEE, and IOE entrance tests face a common challenge: access to affordable, personalised tutoring is limited. Many existing resources are either expensive, not aligned with the Nepali curriculum, or don't adapt to individual student needs.
>
> We wanted to build something free, accessible, and tailored to the Nepali education system — a study assistant that actually understands what students here are learning."

### [0:30 – 1:00] Our Solution

> "That's why we built **Akshar** — an AI-powered learning platform for Nepal.
>
> Akshar combines a curated set of original, syllabus-aligned lessons with Google's Gemma language model. Students can browse lessons by grade, subject, and exam type, and ask questions to get instant explanations.
>
> We've included sample lessons for Grade 11 Physics, Grade 11 Chemistry, Grade 12 Biology, and Grade 12 Mathematics — all tagged with relevant exams like NEB, CEE, and IOE."

### [1:00 – 1:30] Educational Impact

> "The goal is simple: give every student with an internet connection access to a free, on-demand study assistant. Whether you're in Kathmandu or a rural village, Akshar can help explain concepts, clarify doubts, and support exam preparation — all through a simple web interface that works on any device."

---

## Speaker 2: Sagar Katwal (Technical Approach & AI Implementation) — ~1.5 min

### [1:30 – 2:00] Technical Overview

> "Thanks, Dipson. I'm Sagar, and I'll walk you through the technical side.
>
> Akshar is built with **Python** and **Streamlit** — a lightweight web framework that lets us build interactive apps quickly. The frontend is entirely Streamlit, so it's responsive and works on both desktop and mobile browsers.
>
> For data, we use a simple **JSON file** to store our lesson content. Each lesson includes the grade, subject, chapter, exam tags, and the full lesson text. This makes it easy to add new lessons without changing any code."

### [2:00 – 2:30] AI Implementation

> "The AI layer uses **Google's Gemma** model through the Gemini API. We built a service module — `ai_service.py` — that handles all communication with the API. When a student asks a question, the app sends the question along with relevant lesson context to Gemma, which then generates a clear, contextual response.
>
> The API key is configured securely via an environment variable or Streamlit secrets — it's never hardcoded in the source.
>
> The architecture is intentionally simple: Streamlit frontend → Python backend → Gemma API. This keeps the project easy to understand, maintain, and extend."

### [2:30 – 3:00] Why Gemma

> "We chose Gemma because it's a capable language model from Google that's accessible via a straightforward API. It handles educational content well — explaining concepts, working through problems, and adapting to different subjects. For a hackathon prototype, it gave us a good balance of quality, speed, and ease of integration."

---

## Speaker 3: Dhiraj Shrestha (Live Demo) — ~1.5 min

### [3:00 – 3:30] Demo Setup

> "Hi everyone, I'm Dhiraj. Let me show you how Akshar works.
>
> I've already set up the environment and started the app locally. You can see the main interface here — it's clean and straightforward."

**Demo steps:**

1. **Show the lesson browser** — "On the left, students can filter by grade, subject, and exam tag. Let me select Grade 11 Physics."
2. **Open a lesson** — "Here's our Motion in a Straight Line lesson. It covers key definitions, formulas, and explanations — all original content written for the Nepali curriculum."
3. **Show the AI chat** — "Now, let's say a student doesn't understand a concept. They can type a question right here."

### [3:30 – 4:00] Live AI Interaction

> "Let me ask: *'What is the difference between speed and velocity?'*
>
> Watch how Gemma responds with a clear, contextual explanation — pulling from the lesson content we provided. The student gets an instant, understandable answer without needing to search through a textbook."

**Demo steps:**

4. **Ask a question** in the chat interface and show the AI response.
5. **Show another subject** — "Let me switch to Grade 12 Mathematics and ask about derivatives. The AI adapts to whatever lesson is loaded."

### [4:00 – 4:30] Deployment & Accessibility

> "Deploying Akshar is straightforward. We push the code to GitHub, connect the repository to Streamlit Community Cloud, add the API key in the secrets section, and click deploy. Within minutes, the app is live and accessible to anyone with a link — no installation required on the student's end."

---

## All Speakers: Limitations & Conclusion — ~30 sec

### [4:30 – 5:00] Limitations

> "As a hackathon prototype, Akshar has some limitations:
>
> - We currently have **4 sample lessons** — this is not the full NEB, CEE, or IOE syllabus.
> - AI responses, while helpful, should be verified against official textbooks.
> - The app requires an internet connection and a Gemini API key.
> - We don't yet have user accounts or progress tracking."

### Conclusion

> "Our vision is to expand Akshar into a comprehensive learning platform for Nepali students — covering the full syllabus, adding more subjects, and making quality education accessible to everyone.
>
> Thank you! We're happy to take any questions."

---

## Quick Reference

| Time | Speaker | Topic |
|---|---|---|
| 0:00 – 1:30 | Dipson | Problem, solution, educational impact |
| 1:30 – 3:00 | Sagar | Technical architecture, AI implementation |
| 3:00 – 4:30 | Dhiraj | Live demo and deployment |
| 4:30 – 5:00 | All | Limitations and conclusion |
