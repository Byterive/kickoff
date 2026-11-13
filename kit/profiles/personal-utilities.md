---
title: Personal utilities profile
summary: Lightweight skeleton, status table and relaxed budgets for productivity tools and personal helper scripts.
keywords: [scripts, utilities, productivity, automation, personal]
status: confirmed
updated: 2026-10-17
extends: utility
---

# Profile: personal-utilities

## Folder skeleton
One folder per tool: tools-name/ with README.md (purpose, usage, inputs, outputs), the script, and optional notes.
Top level: docs/decisions (optional) | shared/ (common helpers) | PROJECT_STATUS.md

## Extra frontmatter
language, runs_on (windows/mac/linux), entrypoint, schedule (manual/daily/etc.), last_run

## PROJECT_STATUS.md tables
- Tools: name | what it does | works on | last run | status (WORKS/BROKEN/IDEA) | known issues
- Ideas backlog
- Next steps

## Budgets (relaxed)
Docs 400 lines, 25 md per folder, code 600 lines (see budgets.json profile_overrides).
Use `--profile personal-utilities` with check_budgets.py.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Idea
- Build
- Daily use
- Polish

## Never do
Hard-code passwords/tokens (use env vars or a config file kept out of git); delete user files without a dry-run
mode first; add dependencies without noting them in the tool's README.

## DONE means
Runs from a clean shell with documented usage, has a dry-run/safe mode if it changes files.

## Wrap-up additions
Record usage example that was actually run and its output.

## VS Code
### Extensions
- editorconfig.editorconfig: shared formatting rules
- eamodio.gitlens: history and blame
### Settings
- `"files.insertFinalNewline": true`
