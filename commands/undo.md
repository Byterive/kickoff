---
description: "Undo what /kickoff created: removes recorded files that are still unchanged; dry run first"
argument-hint: "[--apply]"
allowed-tools: Bash(python:*)
---

Run `python "${CLAUDE_PLUGIN_ROOT}/kit/tools/undo.py"` (dry run) in the project and show the list: what would be removed, what is kept because it was edited, and what existed before and was only changed (use git for those). Ask me to confirm, and only then re-run with `--apply`. If it says nothing is recorded, say that bootstrap ran without a snapshot and offer `git status` to review by hand. Never delete anything outside this list.
