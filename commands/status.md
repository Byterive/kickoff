---
description: "Summarize PROJECT_STATUS.md (what is done, in progress, blocked, next), using the plan when there is one"
allowed-tools: Bash(python:*)
---

Read PROJECT_STATUS.md and root INDEX.md only. If `.kickoff/fields.json` has tier `plan` and `.kickoff/plan.json` exists, run `python tools/plan.py show` first (or `python "${CLAUDE_PLUGIN_ROOT}/kit/tools/plan.py" show`) and report phases, steps done, late or slipped items from it; with tier `fields`, use the front matter keys first. Give me a short summary: counts by status, what is in progress, blockers or gaps, and the next steps. Do not open other files unless I ask.
