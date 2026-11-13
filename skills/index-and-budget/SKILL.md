---
name: index-and-budget
description: Regenerate INDEX.md files and enforce documentation/code budgets in a kickoff project. Use before committing, before ending a session, or when asked to reindex or check budgets.
---

# index-and-budget

1. Find the project root (folder containing PROJECT_STATUS.md). Use `./tools/` if it exists there; otherwise copy `<skill base dir>/../../kit/tools/` to `./tools/` first.
2. Run the project's own `python tools/build_index.py` (never the kit copy from another folder) then `python tools/check_budgets.py --profile <PROFILE>` (profile is named in CLAUDE.md; omit the flag if unknown).
3. For every violation: missing frontmatter or empty summary -> write a specific one-sentence summary; file too long -> split into focused files with their own frontmatter, or condense; too many files in a folder -> create subfolders. Re-run both tools until clean.
4. Never raise a budget in `tools/budgets.json` without asking the user first.
5. Report which files you changed and the final tool output.
