---
title: Utility profile
summary: Shared lightweight skeleton, status table, never-do rules and VS Code setup for scripts, small tools and command-line utilities; personal-utilities extends it.
keywords: [utility, scripts, cli, tools, automation, family]
status: confirmed
updated: 2026-11-11
---

# Profile: utility

Main profile of the utility family. `personal-utilities` extends it.

## Folder skeleton
One folder per tool with a README (purpose, usage, inputs, outputs) and the script | shared/ | docs/decisions (optional) | tools/

## Extra frontmatter
language, entrypoint, runs_on, last_run

## PROJECT_STATUS.md tables
- Tools: name | what it does | works on | last run | status (WORKS/BROKEN/IDEA) | known issues
- Next steps

## Budgets
Docs: default budgets. Code: max 400 lines per file.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Idea
- Build
- Daily use
- Polish

## Never do
- Hard-code passwords or tokens; use environment variables or a config file kept out of git.
- Delete or overwrite user files without a dry-run mode.
- Add a dependency without noting it in the tool's README.

## DONE means
Runs from a clean shell with documented usage and has a dry-run mode if it changes files.

## Wrap-up additions
Record a usage example that was actually run and its output.

## VS Code
### Extensions
- editorconfig.editorconfig: shared formatting rules
- eamodio.gitlens: history and blame
### Settings
- `"files.insertFinalNewline": true`
