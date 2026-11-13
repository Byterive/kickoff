---
description: "Health check: status freshness, CLAUDE.md size, budgets, plugin set, stale plugin installs, risky permissions"
argument-hint: "[--repair] [--dry-run]"
allowed-tools: Bash(python:*)
---

Run `python tools/doctor.py $ARGUMENTS` in the project (if tools/doctor.py is missing use `python "${CLAUDE_PLUGIN_ROOT}/kit/tools/doctor.py" $ARGUMENTS`). Show the OK, WARN, FAIL and INFO lines, then list at most 3 fixes in priority order. Run with --repair only if I passed it.
