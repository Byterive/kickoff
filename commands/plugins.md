---
description: "Turn plugins and skills on/off for this project: list | on | off | find | preset | choose | undo"
argument-hint: "list | on <names> | off <names> | find <term> | preset <profile> [--tier minimal|recommended|full] | choose | undo"
allowed-tools: Bash(python:*)
---

Script: `python "${CLAUDE_PLUGIN_ROOT}/kit/tools/proj_toggle.py"` (call it T).
- `list`, `on`, `off`, `find`, `preset`, `undo`: run `T $ARGUMENTS` and show the output. For on/off/preset run once with `--dry-run` first, show it, then run for real unless I said not to.
- `choose` (or empty): run `T list`, ask me with AskUserQuestion (multiSelect, split across questions of max 4): "Keep all" / "Select", then which plugins to turn OFF and any skills; build ONE command `cd "<project dir>" && python "<T path>" off <names>` in its own bash block for me to run, and offer to open a terminal tab. Do not run it unless I say so.
- Always end: start a new session to apply (terminal: /reload-plugins). A turned-off skill is blocked from running but may still be listed; plugins are fully removed.
