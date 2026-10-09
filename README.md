# Akshar

**A learning platform for Nepal — built by Team Nepluro.**

Akshar helps Nepali students understand concepts, practise exam-style questions, and prepare with confidence for NEB Grade 11–12 and CEE/IOE entrance examinations. It pairs clear Nepali/English explanations with material students can inspect, and uses **Gemma 4** as a genuine part of the learning experience.

> **Status:** Active hackathon development. This repository currently holds the project documentation and AI-agent guidelines; application code is being added incrementally.

## The problem

Nepali learners preparing for NEB Grade 11–12 and entrance exams (CEE/IOE) often have to rely on generic answers or English-only resources that do not match their curriculum or language. Access to trustworthy, level-appropriate support is uneven, especially on modest devices and connections.

Akshar is being built to close that gap.

## What makes Akshar different

Akshar is built around one trustworthy loop: **learn → understand → practise**.

1. Choose a track and topic — NEB Grade 11/12, CEE, or IOE.
2. Ask a question or open a reviewed practice question.
3. Get a clear, appropriately leveled explanation in Nepali or English, with source references when curriculum material is used.
4. Try a related question or a short knowledge check.
5. Receive encouraging, specific feedback and, where supported, track progress.

Design principles:

- **Grounded, honest answers.** Curriculum answers cite the material actually shown, and clearly label AI-generated explanations and practice questions.
- **Nepali-first accessibility.** Native Nepali/English support, correct Devanagari and mathematical notation, and readable text on small screens.
- **Low-bandwidth by design.** Built for modest devices and connections.
- **A real AI path.** Gemma 4 performs meaningful work in the learner flow — not a label attached to a canned answer.

## Team — Nepluro

| Member | Focus |
|--------|-------|
| Sagar Katwal | Learner experience / frontend |
| Dipson Basnet | Gemma 4 / AI pipeline |
| Dhiraj Shrestha | Learning content, practice & validation |

## Repository contents

| File | Purpose |
|------|---------|
| `AGENTS.md` | Canonical project instructions for AI coding agents |
| `GEMINI.md` | Gemini CLI entry point that imports `AGENTS.md` |
| `FIRST_PROMPT.md` | Read-only repository audit prompt |
| `TEAM_PLAYBOOK.md` | Team work split, MVP scope, and demo plan |
| `LICENSE` | MIT License |

## License

Released under the MIT License. See [`LICENSE`](LICENSE) for details.
