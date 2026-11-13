---
name: wrap-up-thread
description: "End-of-thread routine for a kickoff project: save knowledge, update PROJECT_STATUS.md, reindex, check budgets, list changed files. Use when the user says wrap up, close the thread, hand over, or save progress."
---

# wrap-up-thread

Read the project's `.kickoff/kit/WRAPUP_PROMPT.md` if it exists, otherwise `<skill base dir>/../../kit/WRAPUP_PROMPT.md` (the plugin's copy), and follow its numbered steps in order. That file is the only list of wrap-up steps: do not work from memory or from a summary of it. Steps for optional tiers (guide, tracking fields, plan) say when to skip them.
