---
description: "Bring an existing project up to the current kit: lists what is missing, adds it after approval, never overwrites"
argument-hint: "[--guide local] [--fields none|fields|plan] [--sections yes|no] [--clarity yes|no] [--profile NAME] [--refresh-tools]"
allowed-tools: Bash(python:*)
---

Run `python "${CLAUDE_PLUGIN_ROOT}/kit/tools/upgrade.py" $ARGUMENTS` (dry run, no --apply). Show the TODO lines. Ask the guide question only if the output says "no guide set up": "Add a plain-language guide? No / Local", and add `--guide local` when I say Local. If it says "guide already present", do not ask. If the output says "fields not chosen", ask once: "Tracking fields? Skip (default) / Fields only / Plan (fields + phases, dates, priority in .kickoff/plan.json)". Recommend Plan for projects with dated phases, Fields only for other active projects, Skip for dormant or archived ones; re-run (dry run) with `--fields none|fields|plan`. Then ask whether to apply; on yes run again with `--apply`, then run `/kickoff:doctor`. Never overwrite existing files.

Also ask once, if the output says "status sections not chosen": "Add the status sections How to run, Setup, Data and Troubleshooting to PROJECT_STATUS.md (pre-filled from the repo, marked GUESSED)? Yes (recommended) / No"; re-run the dry run with `--sections yes|no`. The clarity rule (a marked block in CLAUDE.md plus REQUIREMENTS.md) is added by default; `--clarity no` opts out. Present anything you need from me as a numbered brief with your recommendation and the question for each number.

If the output says "tool copy(ies) in tools/ differ", offer once: "Refresh the project tool copies (old copies are saved to .kickoff/backup/<date>/; budgets.json is never touched)? Yes / No"; on yes re-run with `--refresh-tools` (dry run), show it, then apply after I say yes.
