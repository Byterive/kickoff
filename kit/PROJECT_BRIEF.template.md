---
title: Project brief template
summary: Fill-in-the-blanks brief that gives Claude the maximum project detail once, before setup.
keywords: [brief, template, requirements]
status: draft
updated: 2026-10-25
---

# PROJECT_BRIEF (copy to project root, fill in, delete the hints)

## 1. Goal
What are you building or finding out? What does "done" look like? (hint: measurable)

## 2. Profile
unity | backend | backend-go | backend-python | backend-rust | backend-node | frontend | frontend-react | frontend-vue | data-research | utility | netsuite | mobile-app | personal-utilities | trading-research | desktop-app | claude-plugin | custom

## 3. Background and sources
Docs, links, courses, repos, tickets, existing notes (give paths). What each one is for.

## 4. Environment and tools
OS, language/runtime versions, engines, SDKs, hardware, accounts/environments (names only, never passwords).

## 5. Rules and constraints
Budget, deadlines, platforms, compliance, performance targets, style guides.

## 6. Definition of status words
How a thing becomes DONE / PASSED / FAILED / DOUBTFUL (be exact, with numbers if possible).

## 7. Already done / known problems
What exists, what works, what is broken, quirks you already know.

## 8. Next steps wanted
Top 3 to 5 things, in order.

## 9. Never do
Actions Claude must not take (e.g. touch production, delete data, trade live, commit secrets).

## 10. Plugins and skills for this project
`minimal`, `recommended` (profile preset), `keep-all`, or a list of plugins to turn OFF (this project only). Leave blank and kickoff asks you to pick. Names as shown by `python tools/proj_toggle.py list`; skills as `name` or `plugin:*`.

## 11. Guide (optional)
`none` (default) or `local`: a plain-language HTML guide built by the guidebook plugin. List the versions wanted (layman, client, teammate, maintainer, quick-start, or your own) or leave blank to let guidebook propose them. The hub folder comes from `~/.claude/kickoff/config.json`.

## 12. Tracking fields and plan (optional)
`none` (default), `fields` (frontmatter keys only), `plan` (keys plus phases, dates and priority in `.kickoff/plan.json`). Contract: `kit/FIELDS_CONTRACT.md`, schema: `kit/PLAN_SCHEMA.md`.
Dates, if known (leave blank otherwise, never guess):
- target date (soft, YYYY-MM-DD):
- hard deadline (YYYY-MM-DD):
- what "completed" means and who confirms it (with the plan tier the actual end date lives in `plan.json`; otherwise record it in the body):
Plan (only for tier `plan`; blank = not set):
- phases, one per line (the profile's "Default phases" are offered if blank):
- rough start and end per phase (YYYY-MM-DD):
- priority 1..999, lower is more urgent, e.g. 10, 20, 30:

## 13. How to run, setup, data, troubleshooting (optional, default on)
Anything you already know goes here; blanks are asked in the interview.
- command that runs the project, from which folder, and what you should see:
- setup: what must be installed or configured first (names only, never secrets):
- data: each source, its current path, how to obtain it; the downloader if the project has one (how to run it, parameters, settings):
- known problems and what fixes them:
