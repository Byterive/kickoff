---
description: "Draft a reusable profile from this finished project (folders, status tables, never-do, phases); saves only after you approve"
argument-hint: "<name> [--extends <main-profile>]"
allowed-tools: Bash(python:*)
---

Run `python "${CLAUDE_PLUGIN_ROOT}/kit/tools/new_profile.py" --name <name> [--extends <main>]` from the project root (dry run, nothing is written). Show the draft. Go through every UNKNOWN as a numbered brief (options, your recommendation, the question) and wait for my answer to each number. Then show the final file and, only after my yes, re-run with `--write`. Never overwrite an existing profile. Adding it to the kit itself (kit/profiles, preset, gitignore, docs, `check_profiles.py`) is a separate step I ask for.
