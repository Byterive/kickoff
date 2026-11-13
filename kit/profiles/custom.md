---
title: Custom profile
summary: How /kickoff builds a project-specific profile (skeleton, status tables, definitions, never-do, plugin preset) from a short interview.
keywords: [custom, profile, interview, preset]
status: confirmed
updated: 2026-10-22
---

# Profile: custom

Used when no built-in profile fits. Kickoff interviews the user (max 6 questions) and writes:
- `.kickoff/profile.md`: same sections as the built-in profiles (Folder skeleton, Extra frontmatter, PROJECT_STATUS.md tables, Status definitions, Never do, Wrap-up additions).
- `.kickoff/presets/custom.json`: `{ "keep": ["plugin-name", ...] }`, plugins this project needs (kickoff is always kept).

Questions: what is the project; folders it needs; what counts as done/passed/failed; what Claude must never do; which plugins it needs; save as a reusable profile name?
If the user gives a name, also save both files to `~/.claude/kickoff/profiles/<name>/` (profile.md, preset.json) so any project can pick it later.
Profile lookup order: project `.kickoff/` -> `~/.claude/kickoff/profiles/<name>/` -> this folder.

## Default phases
Asked in the interview (when the tracking tier is `plan`): the phases this project goes through, as one line each. Written to `.kickoff/profile.md` under this heading so `plan.py init --profile custom` can use them.
