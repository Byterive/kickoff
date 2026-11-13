---
title: Commands guide and troubleshooting
summary: Step-by-step command sequence for starting and running a project with the kickoff plugin, plus fixes for common problems.
keywords: [commands, steps, troubleshooting, unity, plugin, how to]
status: confirmed
updated: 2026-10-25
---

# Commands, step by step

Run these inside Claude, from the project root (for Unity: the folder that contains `Assets/`).
Replace `unity` with `backend`, `backend-go`, `backend-python`, `backend-rust`, `backend-node`, `frontend`, `frontend-react`, `frontend-vue`, `data-research`, `utility`, `netsuite`, `mobile-app`, `desktop-app`, `personal-utilities`, `trading-research`, `claude-plugin` or `custom`.
`<kit>` below means the kickoff plugin's `kit/` folder (`${CLAUDE_PLUGIN_ROOT}/kit`).

## Before you start (once per project)
| Step | Do | Why |
|---|---|---|
| 1 | Back up or commit the project (`git status` should be clean) | Setup may propose moving files |
| 2 | `git init` if it is not a repo | The pre-commit hook needs git |
| 3 | Copy `<kit>/PROJECT_BRIEF.template.md` to `PROJECT_BRIEF.md` and fill it in (see `<kit>/examples/`), or skip this and let `/kickoff:kickoff` interview you | Gives Claude the details once |
| 4 | Put loose notes, PDFs and links in `_inbox/` | Keeps raw material out of the index |

## Commands
| # | Command | What it does |
|---|---|---|
| 1 | `/kickoff:audit unity` | Read-only inventory of what exists. Writes only to `_audit/`. Stops at `_audit/SUMMARY.md` for your review. Run first on an existing project. |
| 2 | (you) read `_audit/SUMMARY.md` | Check statuses, gaps and risks. Fix anything wrong by telling Claude. |
| 3 | `/kickoff:kickoff unity` | Reads the brief and the audit, asks up to 10 questions, then builds folders, `tools/`, `PROJECT_STATUS.md`, `CLAUDE.md`, and the git hook. Stops for your review. |
| 4 | (you) answer questions, approve the file-move plan, say "go" | Nothing is moved until you approve. |
| 5 | work normally | Claude reads `INDEX.md` and `PROJECT_STATUS.md` first and updates docs as it goes. |
| 6 | `/kickoff:status` | Short summary of `PROJECT_STATUS.md`: counts, in-progress, gaps, next steps. Use at the start of a session. |
| 7 | `/kickoff:reindex` | Rebuilds every `INDEX.md` and checks budgets; fixes violations by splitting or condensing. |
| 7b | `/kickoff:checkpoint` | Mid-session: saves NEXT.md and PROJECT_STATUS.md in seconds (REQUIREMENTS.md and DECISIONS.md only if something new was decided). No reindex, budget check, knowledge capture or commit; it warns if changes are uncommitted. Then `/clear` and `/resume` are safe; resume tells you the last save was a checkpoint (`saved: checkpoint` in NEXT.md). |
| 8 | `/kickoff:wrapup` | End of thread: saves knowledge, updates status and next steps, reindexes, lists every changed file. Always run before closing. |

New project with no existing files: skip commands 1 and 2.

## Daily routine
Start: `/kickoff:status` -> work -> `/kickoff:wrapup`.

# Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Commands do not appear when typing `/` | Plugin not installed or session not restarted | Reopen the terminal in the project, run `/plugin`, confirm `kickoff` is installed and enabled, restart the session |
| Command says unknown / skill not found | Plugin prefix missing | Use the full name `/kickoff:wrapup`, not `/wrapup` |
| `/plugin` marketplace add fails | Wrong source or invalid JSON | Use `/plugin marketplace add Byterive/kit` (or the folder of a local clone of that repo); check its `.claude-plugin/marketplace.json` exists |
| Claude cannot find the kit or profile files | Skill path not resolved | The kit is the plugin's `kit/` folder (`${CLAUDE_PLUGIN_ROOT}/kit`). Run `/plugin`, confirm kickoff is enabled, start a new session. Outside Claude, set `CLAUDE_PLUGIN_ROOT` or put the kit path in `.kickoff/kit_path` |
| `python` not recognized | Python not on PATH | Install Python or run `py tools/build_index.py`; hooks fail silently if Python is missing |
| `check_budgets` reports missing frontmatter | A `.md` has no header | Ask Claude to add title/summary/keywords/status/updated, or add `README.md`/`CLAUDE.md` (already exempt) |
| Budget fails: file too long / too many files | Over 300 lines or 15 .md per folder | Ask Claude to split into focused files or subfolders. Do not raise the limit unless it is justified |
| INDEX.md out of date | Not regenerated | Run `/kickoff:reindex`. Never edit INDEX.md by hand |
| INDEX files appear for Unity folders you do not want | Unity or library folders included | Add folder names to `skip_dirs` in `tools/budgets.json` (e.g. `Assets/ThirdParty`) |
| Claude wants to move or rename Unity assets | Setup proposes a migration | Reject it. Moving assets without `.meta` files breaks references. Keep docs in `docs/`, leave `Assets/` as is |
| Commit blocked with "do not add Claude as co-author" | The co-author hook worked | Re-commit without the Co-Authored-By / Generated-with line |
| Pre-commit hook blocks a commit | Budget violations | Read the listed files, fix them (or run `/kickoff:reindex`), commit again |
| Hook did nothing | Folder has no `PROJECT_STATUS.md` | The auto-reindex only runs in set-up projects; run `bootstrap` first |
| Status words missing or invented | Brief lacks definitions | Fill section 6 of `PROJECT_BRIEF.md` with exact criteria, then ask Claude to re-check statuses |
| Claude forgot earlier work in a new thread | Docs were not saved | Start with `/kickoff:status`; always end threads with `/kickoff:wrapup` and check its changed-files list |
| Edited a profile but nothing changed | Plugin uses its bundled copy | Put your own profile in the project's `.kickoff/profile.md` or in `~/.claude/kickoff/profiles/<name>/`; edits inside the plugin cache are lost on update |


New in 1.4.3: `/kickoff:upgrade` keeps the profile reference inside the project (a custom profile points at `.kickoff/profile.md`; a built-in one is copied to `.kickoff/kit/profiles/<name>.md`), with a note in DECISIONS.md. New opt-in `--refresh-tools` replaces out-of-date tool copies in `tools/` after saving the old ones to `.kickoff/backup/<date>/` (never `budgets.json`). `/kickoff:doctor` now says how to fix an inactive co-author block: install the plugin, or switch it on for the project. Tests: `kit/tools/test_upgrade143.py`.

New in 1.4.2: nothing private lands in a project's repo. `guide.json` no longer stores your hub path (it stays in `~/.claude/kickoff/config.json`), the audit writes paths relative to the project, and `/kickoff:plugins` (`proj_toggle.py`) now writes your plugin and skill choices to the git-ignored `.claude/settings.local.json`; `python tools/proj_toggle.py localize` moves the choices already in the shared `settings.json`. `/kickoff:doctor` lists tracked files that contain absolute local paths (and says if one includes a user account name) and warns when a tracked `.claude/settings.json` names plugins. Tests: `kit/tools/test_privacy.py`.

New in 1.4.1: safety fixes found in the guidebook project. `tools/build_index.py` now reads the project's own skip list (`tools/budgets.json`, matching folder names and paths such as `tests/fixtures`), writes nothing under skipped folders, never overwrites a file that is not a generated INDEX.md (also when only the capitalisation differs, such as `index.md`), and refuses a folder that is not a kickoff project; `/kickoff:doctor` prints which script ran and lists the files it created or changed. `/kickoff:upgrade` no longer asks about a guide when guidebook already built one, rewrites the two absolute kit paths in `CLAUDE.md` to `.kickoff/kit/` (shown in the dry run, noted in DECISIONS.md), and writes every file with the project's own line ending. New `kit/tools/fix_hashes.py` fixes commit-hash references after a history rewrite from an old-to-new map. Doctor also warns about paths outside the project, kit copies older than the kit, hashes no branch contains, a stale NEXT.md, and whether the co-author block is active. Wrap-up recomputes the uncommitted list from `git status`. Tests: `kit/tools/test_safety.py`.

New in 1.4: a clarity rule and a requirements ledger, and four status sections. `/kickoff:upgrade` (and a new `/kickoff:kickoff`) appends one marked block to `CLAUDE.md` ("Clarify before you record or build": when a phase starts, a requirement is added or anything new needs a decision, ask first with a numbered brief, each item with options, a recommendation and the question; record what it changes in DECISIONS.md, the plan and REQUIREMENTS.md) and creates `REQUIREMENTS.md`; `--clarity no` opts out. `--sections yes` adds How to run, Setup, Data and Troubleshooting to `PROJECT_STATUS.md`, pre-filled from the README, CLAUDE.md and the repo and marked GUESSED, never touching an existing heading. Wrap-up now confirms the sections (re-runs commands, checks data paths) and updates the ledger; doctor reports the sections, open requirements and unanswered questions. Choices are stored in `.kickoff/options.json`. Wrap-up has 15 steps. An optional hook that blocks writes until you confirm is deferred. Update with `/plugin marketplace update byterive-kit`, then run `/kickoff:upgrade` in each project.

New in 1.3: fixes and the shared plan file. Fixes: the delete-blocking hook now ignores text that only mentions a delete (echo, heredocs, commit messages) and still blocks real ones; the co-author hook also covers PowerShell; `proj_toggle.py` finds its presets from a project copy (`.kickoff/presets/`, `CLAUDE_PLUGIN_ROOT`, or `.kickoff/kit_path`) and always keeps `kickoff` (plus your own list in `~/.claude/kickoff/always.json`); generated files no longer hold absolute plugin paths (`CLAUDE.md` points to `.kickoff/kit/`, copies that upgrade refreshes only while you have not edited them); wrap-up has one list of steps (`kit/WRAPUP_PROMPT.md`); the reindex hook finds the project from a subfolder; `progressive-disclosure` is no longer in the always-keep list. New: tier `plan` with `.kickoff/plan.json` (phases, steps, planned and actual dates, priority; schema in `kit/PLAN_SCHEMA.md`), `kit/tools/plan.py` (validate, show, next, set-status, render-status, init), default phases per profile, a plan step in `/kickoff:wrapup`, plan checks in `/kickoff:doctor`, and `/kickoff:resume` and `/kickoff:status` that read the live plan. Ownership: planned dates and priority belong to you (you, by hand); status and actual dates belong to wrap-up through `plan.py`. Tests: `kit/tools/smoke_test.py`, `test_hooks.py`, `test_plan.py`. Update the installed plugin with `/plugin marketplace update byterive-kit`.

New in 1.2: optional tracking fields (`project_status`, `target_date`, `deadline`, `blocked_by`, `next`) in frontmatter, with `/kickoff:upgrade --fields none|fields|plan`, wrap-up refresh, `/doctor` field checks, and the `desktop-app` profile. Also `/kickoff:kickoff <profile> --plan-only` (brief and open decisions only, builds nothing) and the opt-in `python kit/tools/export_registry.py ROOT... [--out projects.json]` (lists project candidates under folders you name; never runs automatically). All optional; works on its own. See `kit/FIELDS_CONTRACT.md`.

New in 1.1: `/kickoff:upgrade` (bring older projects up to date), optional guide setup (`.kickoff/guide.json`), `/doctor` guide checks.

New in 1.0: `/kickoff:kickoff` (replaces bootstrap), `/kickoff:resume`, `/kickoff:plugins`, `/kickoff:doctor`, custom profiles, plugin presets. The full manual is in the Byterive/kit repo (`docs/howto/01-kickoff.md`).
