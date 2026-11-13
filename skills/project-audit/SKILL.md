---
name: project-audit
description: Read-only inventory of an existing project into _audit/ (components, status, data sources, scripts, results, findings, gaps). Use before bootstrapping a project that already has files, or when asked to audit or inventory a project.
---

# project-audit

Input: PROFILE (ask if missing). Follow `<skill base dir>/../../kit/AUDIT_PROMPT.md` and `<skill base dir>/../../kit/profiles/<PROFILE>.md`.

Strictly read-only except for the new `_audit/` folder: no moving, renaming, deleting or tool installs. Cite source paths for every claim, write UNKNOWN instead of guessing, flag CONFLICT. Work one top-level folder at a time and log progress in `_audit/PROGRESS.md`. Every _audit .md has frontmatter. Write every path relative to the project root (`src/app.py`), never absolute (no drive letters, no user folders), so the audit is safe to commit. End with `_audit/SUMMARY.md` and `_audit/PROJECT_STATUS.draft.md`, then STOP and show the summary.
