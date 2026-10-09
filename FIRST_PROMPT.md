# Akshar — First Repository Audit Prompt

Use this prompt to start a new contributor or AI coding-agent session from a clear, read-only understanding of the repository. The canonical guidance lives in `AGENTS.md`; this prompt is tool-agnostic.

---

Read `AGENTS.md` and follow it. Akshar is a learning platform for Nepali students covering NEB Grade 11–12 and CEE/IOE entrance preparation, with real Gemma 4 integration as a core requirement.

**For this first task, perform a read-only repository audit. Do not edit, create, delete, install, stage, commit, push, or deploy anything.**

Inspect the repository structure, instructions, README/docs, Git status and recent history, manifests and scripts, app entry points and main user flows, API/data layer, current model integration, content/source pipeline, tests/CI, design system, and deployment configuration. Inspect pre-existing staged and unstaged changes without altering them. Do not traverse vendor/dependency/build/cache directories or print secrets.

Return a concise, evidence-based report with these headings:

1. **Repository map** — stack, entry points, key folders/files, run/test/build commands.
2. **What works today** — implemented user flows and the actual evidence in code.
3. **AI truth check** — whether Gemma 4 is genuinely connected, where inference happens, which model/runtime is configured, and what is mock, fallback, or unimplemented. Never infer that it works just because a dependency or label exists.
4. **Learning content and grounding** — current NEB/CEE/IOE content, source provenance and licensing, retrieval, citations, and gaps.
5. **Git and worktree state** — existing changes, branch and history, and any commit-safety concerns; do not alter them.
6. **Delivery and judging risks** — the three most serious risks to impact, technical depth, functionality, demo clarity, or required submissions. Verify the specific event's current rubric if the event is identifiable; otherwise flag it as unknown.
7. **Recommended MVP** — the smallest end-to-end learner journey that can be demonstrated honestly, with acceptance checks.
8. **Work split** — meaningful, balanced workstreams for Sagar Katwal, Dipson Basnet, and Dhiraj Shrestha; list ownership and the shared interfaces to agree on first. Avoid overlapping file ownership where possible.
9. **Next task** — the single highest-leverage next task and its exact verification commands.

Separate facts found in the repository from assumptions and recommendations. If a path or tool is unavailable, say so. Do not make changes until an implementation task is provided.
