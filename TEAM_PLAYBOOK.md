# Nepluro / Akshar — Hackathon Execution Playbook

## Project

**Akshar — Learning Platform for Nepal** · **Team:** Nepluro · **Members:** Sagar Katwal · Dipson Basnet · Dhiraj Shrestha

**Problem:** Nepali learners need accessible, understandable, trustworthy support for NEB Grade 11–12 learning and CEE/IOE entrance preparation.

**Product promise:** Help a learner go from *stuck on a question* to *understanding the concept and successfully practising it*—with Nepali/English explanations and sources they can inspect.

## The strongest demo target: the Akshar Learning Loop

Build and polish one complete flow before broadening the feature set:

1. Select a learning track and topic.
2. Ask a question or open a reviewed practice question.
3. Receive a useful explanation powered by the actual configured Gemma 4 model.
4. Show source references when the answer uses curriculum content; clearly label generated explanations and generated questions.
5. Offer one follow-up question that tests understanding, then show helpful feedback.
6. Where persistence exists, record the attempt and show a simple learning-progress signal.

The exact first slice must be chosen after inspecting the repository. Do not build all six steps as fake placeholders. A smaller working loop is stronger than six broken ones.

## Suggested work split (adjust after repository audit)

These are starting ownership areas, not rigid job titles. Agree on shared contracts before coding and rotate review/demo responsibilities so everyone contributes to the final quality.

### Sagar Katwal — learner experience / frontend

Own one cohesive path through the app: navigation, learning-track/topic selection, readable lesson/tutor screens, responsive states, and clear next actions. Coordinate the expected API/data shape with the AI and content owners before wiring screens.

### Dipson Basnet — Gemma 4 / AI pipeline

Own the real model integration, prompt/version management, model configuration, response validation, error handling, and evaluation cases. Make the Gemma 4 path easy for a judge to trace in the code and demonstrate live. Coordinate with content on how retrieved sources reach the model and how citations return to the UI.

### Dhiraj Shrestha — learning content / practice / validation

Own the initial, legally usable and documented content set, metadata and attribution, topic/question structures, follow-up practice and answer validation. Coordinate a stable contract with frontend and AI so source references and question provenance are preserved end to end.

### Shared responsibilities

All three review each other's contracts, test the integrated flow, help remove blockers, and prepare the pitch/demo. If the actual repository suggests different ownership, divide by existing modules and change these assignments together.

## Fair commits without vanity commits

A fair contribution history means three people make meaningful, attributable contributions—not necessarily exactly the same number of commits.

- Each member configures their own real Git name/email and authors their own work.
- Split work into reviewable vertical milestones, each of which can be demonstrated or tested.
- Commit every completed logical milestone after checking its diff and relevant tests. Do not wait until the last hour to dump everything into one commit.
- Use short-lived branches if supported, e.g. `feat/learner-flow-sagar`, `feat/gemma-pipeline-dipson`, `feat/practice-content-dhiraj`.
- Agree on shared types/API/data contracts before implementation. One owner should not overwrite another's files without coordination.
- Do not fabricate authorship, game contribution graphs, or make trivial commits to hit a quota.
- Integrate to the main branch early enough to fix conflicts and run the full demo from a clean checkout.

## What makes this more than a generic chatbot?

The product should demonstrate education-specific engineering rather than merely sending a prompt to a model:

- Curriculum/topic-aware retrieval from a small but trustworthy, openly usable source set.
- Clear source attribution, including a graceful answer when the sources do not support a claim.
- Explanations adapted for Nepali students, with Nepali/English selection and correct handling of Devanagari and maths.
- A follow-up practice question and validated feedback that closes the learning loop.
- A small repeatable evaluation set: known-answer STEM questions, bilingual prompts, an ambiguous question, and a no-evidence case.
- A real, visible, testable Gemma 4 inference path. Be honest about model size, runtime, hosted/local behavior, latency, and fallbacks.

Do not try to win by claiming features you cannot show. Do not call content official unless its origin is verified. Use only sources the team has permission to use and document their provenance.

## Demo/story structure

Build the video/live demo around a learner, not a list of features:

1. **Problem (10–15 seconds):** A student gets stuck on a NEB/CEE/IOE concept and a generic answer or English-only resource is not enough.
2. **Akshar in action:** Select a topic, ask a realistic question, show a useful bilingual explanation with evidence/source references.
3. **Proof of learning:** Answer a follow-up question and show clear feedback or progress.
4. **Technical proof:** Briefly show where Gemma 4 is invoked, where the curriculum material is retrieved, and how the app handles unsupported claims or model failure.
5. **Impact and next step:** Explain who benefits, how the source set can grow responsibly, and how the design can fit different devices/connectivity levels—only claim what the prototype supports.

Rehearse from a fresh session and a clean start. Keep a backup recording, but never present a prerecorded or mocked response as a live inference result. Label any offline/demo fallback honestly.

## Suggested team checkpoints

- **Checkpoint A — audit:** Map the existing repository and current working state before feature work.
- **Checkpoint B — shared contract:** Agree on topic/content schema, tutor request/response shape, error format, and citation shape.
- **Checkpoint C — vertical slices:** Each owner completes a small end-to-end piece; commit and integrate early.
- **Checkpoint D — integration:** Run the full flow in the actual target environment; fix the most visible reliability issues.
- **Checkpoint E — judging evidence:** Add setup instructions, architecture/model notes, source attribution, evaluation examples, and demo script.
- **Checkpoint F — final rehearsal:** Fresh clone or clean checkout, follow README exactly, verify credentials/config, exercise the happy path and one failure path, then record the demo.

Before submission, check the exact hackathon's current official rules and judging rubric. Different Gemma 4 events may use different criteria or submission requirements.
