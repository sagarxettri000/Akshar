# Akshar — Agent Pack for Nepluro

These files are the canonical agent instructions for the Akshar learning platform, deployed at the repository root to guide coding agents on the Nepluro project.

## Files

- `AGENTS.md` — canonical, project-wide instruction source for AI coding agents. Covers mission, repository audit discipline, Gemma 4 integration, educational accuracy, testing, and Git workflow.
- `GEMINI.md` — Gemini CLI entry point that imports the canonical rules from `AGENTS.md`.
- `FIRST_PROMPT.md` — copy/paste prompt for a read-only repository audit before implementation begins.
- `TEAM_PLAYBOOK.md` — suggested three-person work split, focused learning-loop MVP, fair commit practices, and demo story for the Nepluro team.

## Recommended order

1. Copy these files into the repository root.
2. Start a fresh coding-agent session so it loads the instruction file(s).
3. Paste `FIRST_PROMPT.md` and get a read-only audit. Review the audit as a team.
4. Send a precise implementation task. Have the AI complete one vertical slice, verify it, inspect the diff, and commit it locally.
5. Repeat, integrating teammates' work early. Each person must use their own Git identity for their commits.

`AGENTS.md` is the canonical source of truth. The `GEMINI.md` import is for Gemini CLI; other tools may have their own context-file conventions. Ensure the coding tool actually loads its instruction file. These files guide an agent but cannot guarantee that every model/tool will obey them.

This pack is tailored for the Akshar project — a learning platform for Nepali students studying NEB Grade 11–12 and preparing for CEE/IOE entrance exams. No application source code was inspected during preparation.