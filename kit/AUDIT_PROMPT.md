---
title: Audit prompt
summary: Read-only inventory prompt for an existing project; run before the master setup to capture what exists, its status, and gaps.
keywords: [audit, inventory, existing project, read-only]
status: confirmed
updated: 2026-10-17
---

# Audit prompt (existing projects only)

Set `PROFILE` first. Paste the block. The profile decides which tables (step 2) apply.

````text
PROFILE: <profile-name>
KIT: <kit>   (the kickoff plugin's kit/ folder, ${CLAUDE_PLUGIN_ROOT}/kit)

READ-ONLY inventory phase. Do NOT move, rename, delete or restructure anything, and do NOT
install tools. Write only to a new folder `_audit/`. Read KIT\profiles\<PROFILE>.md first.

## Rules
- Cite the source file path (and line/section) for every claim.
- Not stated anywhere -> write UNKNOWN. Never guess. Conflicting sources -> list both, flag CONFLICT.
- Read the real code, configs and reports; do not trust file names alone.
- Go one top-level folder at a time and append to the audit files. Record progress in
  `_audit/PROGRESS.md` so an interrupted session can resume.
- Every .md in `_audit/` starts with frontmatter: title, summary (one specific sentence),
  keywords, status: draft, updated.
- Do not add Claude as co-author or any Claude attribution anywhere.

## Produce (one file each in _audit/)
1. inventory.md   every component/feature/script/module: name | purpose | path | status | evidence
2. status tables from the profile (e.g. setups/tests for trading; features/builds for Unity; endpoints for Go)
3. data-and-sources.md   data files, links, services, environments, credentials LOCATIONS only (never values)
4. knowledge.md   notes, docs, decisions, transcripts: topic | path | one-line summary
5. scripts.md     path | purpose | inputs | outputs | runnable as-is? | used by
6. results.md     reports, test output, builds, logs: path | what produced it | takeaway
7. findings.md    conclusions with evidence + confidence (HIGH/MEDIUM/LOW); separate confirmed vs claimed
8. other.md       LIST WHAT ELSE EXISTS: configs, notebooks, logs, screenshots, TODOs, abandoned work,
                  duplicates, unlabeled files, dead links, secrets that must not be committed
9. gaps.md        untested / undocumented / missing items ranked by value
10. SUMMARY.md    counts per category, status breakdown, top 10 gaps, top risks
11. PROJECT_STATUS.draft.md   draft dashboard using the profile's tables

## Finish
STOP and show SUMMARY.md. Create no structure until I say go.
````
