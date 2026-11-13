---
title: Changes in 1.4.6, 1.4.5, 1.4.4, 1.4.3, 1.4.2, 1.4.1, 1.4.0 and 1.3.0
summary: What changed in kickoff 1.4.1 (safety fixes from the guidebook project), 1.4.0 (clarity rule, requirements ledger, status sections) and 1.3.0 (defect fixes D1 to D10 and the shared plan file), files created and changed, behaviour changes, decisions taken, and how to update the installed plugin.
keywords: [changes, release, 1.4.0, 1.3.0, clarity, requirements, plan, hooks, proj_toggle]
status: confirmed
updated: 2026-11-14
---

# kickoff 1.4.6 changes (2026-11-14)

| change | detail |
|---|---|
| README | "Try it" section, a Privacy line, images in `assets/`, a trademark line for Unity and NetSuite, and the health-check wording: the doctor prints OK, WARN, FAIL and INFO lines |
| privacy | `PRIVACY.md` added |
| doctor command | `commands/doctor.md` names the OK, WARN, FAIL and INFO lines |
| guide contract | `kit/GUIDE_CONTRACT.md` wording about the guidebook hub corrected |
| safety hook | `hooks/block_rm_rf.py` carries a comment that the hook only reads and blocks command text; no behaviour change |
| local folder | `.claude/` (per-project plugin on/off list) is git-ignored |
| test fixture | the safety test fixture uses `noreply@example.com` |
| release archive | `.gitattributes` no longer holds export-ignore lines; this repository holds release files only |

# kickoff 1.4.5 changes (2026-11-12)

| change | detail |
|---|---|
| companion list trimmed | Presets and profile companion lines no longer suggest a withdrawn plugin |
| export-ignore | `.gitattributes` keeps bootstrap files out of the release archive |
| new built-in profile `claude-plugin` | for Claude Code plugins/mods in TypeScript: `kit/profiles/claude-plugin.md`, minimal preset, gitignore |
| profile families | a secondary profile says `extends: <main>`; `kit/tools/profile_lib.py` resolves it for plan.py, proj_toggle.py, check_budgets.py, upgrade.py. Sections: a secondary replaces the main's, except Never do, Known pitfalls, VS Code and Companion plugins, which are merged. Families: `backend` (`backend-go`, `backend-python`, `backend-rust`, `backend-node`; `go-backend` stays an alias), `frontend` (`frontend-react`, `frontend-vue`), `data-research` (`trading-research` now extends it), `utility` (`personal-utilities` now extends it); existing names and content are unchanged. `.kickoff/budgets.json` and `.gitignore` keep generated INDEX.md files out of this repo |
| VS Code sections | every profile has `## VS Code` (extensions, settings); `kit/tools/vscode_ext.py` builds `.vscode/extensions.json` after approval (merge, no overwrite, skips unverified ids, never installs); `.vscode/extensions.json` is no longer git-ignored |
| companion plugins | `## Companion plugins` per profile (plugin names only); `kit/tools/companions.py` reports installed, off or missing and the install command; install runs only after the user agrees |
| new commands | `/kickoff:profiles` (families and aliases), `/kickoff:new-profile` (draft a profile from a finished project), `/kickoff:undo` (removes what bootstrap created while unchanged; uses `.kickoff/before.json` and `manifest.json`) |
| doctor | `doctor_extra.py`: profile changed since setup (stamp in `.kickoff/profile.stamp.json`), missing companion plugins, `profile_lib.py` missing from tools/ |
| tooling | `upgrade.py` split (`upgrade_lib.py`, 386 lines, was 462); `check_profiles.py` linter; `test_families.py`; GitHub Actions workflow runs the smoke test on Windows and Linux |
| `/kickoff:checkpoint` | light mid-session save (command only): always NEXT.md (`saved: checkpoint`) and PROJECT_STATUS.md, REQUIREMENTS.md and DECISIONS.md only if something new; plan.py for step status, never planned dates or priority; no reindex, budgets, knowledge capture or commits; warns about uncommitted changes; wrap-up now writes `saved: wrapup` and `/kickoff:resume` reports a checkpoint save |
| Claude contribution line option | setup step 4f asks Yes/No (default No); `kit/tools/attribution.py` writes `.kickoff/attribution.json` and the CLAUDE.md Git rule (both the Co-Authored-By trailer and the PR Generated-with line); no git hook; the plugin's co-author hook and `/kickoff:doctor` read the file, so a project that chose Yes is no longer blocked. Tests in `test_hooks.py` |
| repo | PROJECT_BRIEF.md, DECISIONS.md, REQUIREMENTS.md, PROJECT_STATUS.md, NEXT.md and `_audit/` for this repo itself |

Version bumped from 1.4.4 to 1.4.5.

# kickoff 1.4.4 changes (2026-11-10)

Cleanup before the public launch.

| change | detail |
|---|---|
| tracking tiers are `none`, `fields` and `plan` | the extra project-viewer tier and its `.kickoff/project.json` are gone; an older tier name in `fields.json` is read as `fields` (or `plan` when the file has `"plan": true`) and nothing is rewritten |
| your own always-keep plugins | `~/.claude/kickoff/always.json` (`{"keep": ["name"]}`) is added to the kit's list on your machine only; the kit's `_always.json` keeps only `kickoff`, and the trading-research preset no longer names a plugin |
| internal references removed | docs no longer point at private notes or project names |

# kickoff 1.4.3 changes (date UNKNOWN, before 2026-11-10)

Found by the guidebook session.

| issue | fix | test (`kit/tools/test_upgrade143.py`) |
|---|---|---|
| CLAUDE.md still pointed at a profile file outside the project | upgrade rewrites the profile reference: custom -> `.kickoff/profile.md` (no copy), built-in -> copied to `.kickoff/kit/profiles/<name>.md` (hash-tracked) and referenced there; DECISIONS.md note; doctor already flags any other outside path | custom, built-in, dry run, idempotence, doctor before and after |
| co-author warning gave no fix | doctor says whether kickoff is not installed (`claude plugin install kickoff@byterive-kit`) or installed but switched off here (`proj_toggle.py on kickoff`). Finding: re-adding a marketplace removes its plugin installs, so kickoff was truly not installed. `proj_toggle list` shows kickoff once installed | not installed, installed but off, enabled, list |
| tool copies in projects never refreshed | `upgrade.py --refresh-tools`: dry run first, saves old copies to `.kickoff/backup/<date>/`, never touches `budgets.json`; without the flag upgrade only reports which copies differ | report, dry run, apply, backup, budgets untouched, second run quiet |

# kickoff 1.4.2 changes (date UNKNOWN, before 2026-11-10)

Found by a security scan of a project.

| issue | fix | test (`kit/tools/test_privacy.py`) |
|---|---|---|
| hub path copied into `.kickoff/guide.json` | `upgrade.py` writes `"hub": ""`; the guide reads `~/.claude/kickoff/config.json` itself; contract, template and bootstrap skill updated | user config with a hub: not in the project file |
| `_audit/` holds absolute project paths | audit skill: every path relative to the project root | rule present; doctor flags absolute paths in `_audit/` |
| plugin choices (private marketplace names) in committed `.claude/settings.json` | `proj_toggle.py` writes `.claude/settings.local.json` (git-ignored; shared file only read); `list` and `pick` read both; new `localize` moves existing toggles and `Skill()` rules (dry run first); undo uses `settings.local.json.bak` | toggle, shared untouched, list, dry run, move, repeat, secret deny rule kept |
| nothing warned about any of it | doctor: tracked files with absolute local paths (file and lines, account-name note; generic placeholder user folders, `.guidebook/` and kickoff's own tools skipped) and a tracked `settings.json` naming plugins | path hits, placeholder, `.guidebook`, `_audit`, settings warning, gone after `localize`, clean project |

Not changed: existing projects keep what they have until you run `localize` or fix the files.

# kickoff 1.4.1 changes

Seven issues reported from the guidebook project on 2026-11-04.

| issue | fix | test (`kit/tools/test_safety.py`) |
|---|---|---|
| 1 index ignores the project's skip list | Finding: doctor already ran the project's own script; the stray files came from a run of the kit script from the wrong folder, which read the kit's `budgets.json`. `build_index.py` now reads the project's `tools/budgets.json` (else `.kickoff/budgets.json`), matches names and relative paths, never writes under skipped folders, never overwrites a non-generated file (also case-insensitively), refuses a folder with no `PROJECT_STATUS.md` and no `tools/build_index.py` (`--force` overrides), and `--verbose` lists created and changed files. Doctor prints which script ran, its skip list and what it created or changed. Wrap-up and the index skill say: the project's own tools, never the kit copy | skip_dirs and two existing `index.md` pages: no INDEX.md in skipped folders, no existing file modified, doctor output; kit copy run from another folder; refusal and `--force` |
| 2 guide question when a guide exists | upgrade detects `.guidebook/`, `docs/guide-src/` or a guidebook-built `docs/guide/` and prints "guide already present, built by guidebook"; doctor says the same | project with `.guidebook/`; project without a guide is still offered one |
| 3 CLAUDE.md points outside the project | upgrade rewrites only the `CLAUDE_INSTRUCTIONS.md` and `WRAPUP_PROMPT.md` references to `.kickoff/kit/` (visible in the dry run, one marker comment, one line in DECISIONS.md); doctor warns about other absolute paths and kit copies older than the kit | dry run, apply, idempotence, remaining path warning, old-copy warning |
| 4 stale hashes after a history rewrite | `kit/tools/fix_hashes.py`: `--make-map` pairs old and new commits (same trees and subjects), then `--map FILE [--apply]` fixes short and full hashes in NEXT.md, PROJECT_STATUS.md, DECISIONS.md, REQUIREMENTS.md and `.guidebook/state.json`; ambiguous short hashes are left alone; doctor warns about hashes git cannot find or no branch contains. Kickoff has no history-rewrite tool by design. Maps for the 7 repos rewritten on 2026-11-04 are next to the backup bundle | real filter-branch in a temp repo: map pairs, dry run, fix, doctor quiet, ambiguity |
| 5 line endings | upgrade writes each file with its own line ending, new files with the project's (from CLAUDE.md, then `.gitattributes` eol=crlf, else LF); copy hashes ignore line endings; `.gitattributes` template gains `*.json text eol=lf`; doctor recommends the lines | CRLF project, LF project, `.gitattributes`-decided project, idempotence |
| 6 stale handover | wrap-up step 12 recomputes "Half-done / uncommitted" from `git status --short` and the latest commit; doctor flags NEXT.md older than HEAD and "uncommitted" text on a clean tree | temp git repo |
| 7 co-author block | doctor reports whether it is active: kickoff enabled for the project, `KICKOFF_DISABLED_HOOKS` without `coauthor`, `commit-msg` hook noted if installed. The hook itself is covered by `test_hooks.py` | enabled, switched off, project turns kickoff off, hook blocks the trailer |

Not changed: tool copies already inside a project (`tools/*.py`) are not refreshed by upgrade; a project keeps the version it was bootstrapped with. Update the installed plugin with `/plugin marketplace update byterive-kit`.

# kickoff 1.4.0 changes

Requested by the user on 2026-11-04.

## New
| item | behaviour |
|---|---|
| Clarity rule | `kit/templates/clarity-rule.md`: a marked block appended to `CLAUDE.md` by `/kickoff:upgrade` (existing and new projects; on by default, `--clarity no` opts out). When a phase starts, a requirement is added or anything new needs a decision: ask first with a numbered brief (options, recommendation, question), wait for an explicit answer per number, record what it changes in DECISIONS.md, the plan and REQUIREMENTS.md, list anything dropped. Advisory; a blocking hook is deferred (R32). Also summarised in `CLAUDE_INSTRUCTIONS.md` |
| Requirements ledger | `REQUIREMENTS.md` per project (`kit/templates/REQUIREMENTS.template.md`); wrap-up step 7 updates it and traces requirements to evidence; doctor reports open requirements and unanswered questions |
| Status sections | `--sections yes`: How to run, Setup, Data and Troubleshooting headings in `PROJECT_STATUS.md`, pre-filled from the README, CLAUDE.md "How to verify" and the repo layout (a data folder, download/fetch scripts) and marked GUESSED; an existing heading is never changed; wrap-up step 6 confirms them (re-runs commands, checks data paths, records downloader parameters and settings); doctor reports "N of 4 confirmed" |
| Options file | `.kickoff/options.json` stores the two choices so upgrade does not ask again |
| Wrap-up | 15 steps (new steps 6 and 7) |
| Brief | section 13 for what you already know about running, setup, data and known problems |
| Tests | smoke test covers pre-fill, idempotence, opt-out, doctor counts, and two regression tests for earlier gaps: no drive paths in generated templates (D4) and a single wrap-up step list (D5) |

## Decisions taken (user answers 2026-11-04)
Status sections: on for new projects, offered by upgrade for existing ones; inside `PROJECT_STATUS.md`; pre-filled as GUESSED; Data = sources, current paths, how to obtain them, and the project's downloader with usage, parameters and settings; Setup and Troubleshooting are their own pages in the guide. Clarity rule: new and existing projects, also in the user-level `~/.claude/CLAUDE.md` (wording to be approved), per-project ledger with wrap-up and doctor checks, advisory first and a hook later.

## Not in this release
The guidebook half (pages for these sections, guidebook 0.2.0) is a prompt for its own session: `kit/docs/prompts/GUIDEBOOK_SECTIONS_PROMPT.md` in the Byterive/kit repo.

# kickoff 1.3.0 changes

## Fixed (review D1 to D10)
| id | fix |
|---|---|
| D1 | `proj_toggle.py` finds the kit by `CLAUDE_PLUGIN_ROOT`, its own `kit/`, or `.kickoff/kit_path`; a project copy also reads `.kickoff/presets/` (copied by upgrade). No silent default: it stops with a clear message. `_always.json` now keeps `kickoff` |
| D2 | `block_rm_rf.py` blocks only a deleter in command position with both recursive and force flags; text in quotes, heredocs, here-strings and commit messages passes. Shell `-c` strings, `eval`, `$( )` and `xargs`/`find -exec` still count. Unparseable input falls back to the old match |
| D3 | co-author hook registered for PowerShell too |
| D4 | no absolute or versioned plugin paths in generated files; `.kickoff/kit/` copies of `CLAUDE_INSTRUCTIONS.md` and `WRAPUP_PROMPT.md` with stored hashes; `upgrade` refreshes a copy only while unchanged |
| D5 | wrap-up skill points to `WRAPUP_PROMPT.md` (single list of 13 steps) |
| D7 | README and GUIDE profile lists include `desktop-app`; GUIDE paths and links corrected; a test keeps profiles and docs in step. README install line `Byterive/kit` is correct (the kickoff repo has no marketplace file) and was kept |
| D8 | `progressive-disclosure` removed from `_always.json` (nothing else in the kit used it) |
| D9 | `/kickoff:resume` and `/kickoff:status` read the live plan and front matter keys |
| D10 | reindex hook walks up from the current folder to the first `PROJECT_STATUS.md`, stopping at a repository top |

## New: shared plan file (tier `plan`)
Files: `kit/PLAN_SCHEMA.md`, `kit/templates/plan.template.json`, `kit/tools/plan.py` + `plan_lib.py`, `kit/examples/plan.example.json`, `kit/tests/plan/` (valid and invalid files with `expected.json`), default phases in every profile, `kit/tools/test_plan.py`, `kit/tools/test_hooks.py`.
Behaviour: wrap-up step 5 sets status, actual dates and evidence through `plan.py` and refreshes the "Where we are" block; doctor validates the plan and warns about late steps; `upgrade --fields plan` creates the file; bootstrap step 4c interviews for phases, dates and priority.
Ownership: structure and planned dates and priority are yours (you, by hand); status, actual dates and evidence are wrap-up's, through `plan.py` only. `plan.py` merges a concurrent edit instead of refusing, and never changes start, end, priority, ids, names or unknown keys.

## Decisions taken
- Structure of the plan belongs to you; wrap-up only proposes changes under "Plan changes proposed" in `NEXT.md`.
- Profile words PASSED, WIP and similar are accepted as input aliases for DONE, IN_PROGRESS (see `PLAN_SCHEMA.md`).
- `plan.py` is two files (`plan.py`, `plan_lib.py`) to stay under the 400-line code budget in projects.
- Presets and the profile file are copied into `.kickoff/` so project tools work without the plugin folder.

## Update the installed plugin
`/plugin marketplace update byterive-kit`, then `claude plugin update kickoff@byterive-kit` (or reinstall) and start a new session. Existing projects: run `/kickoff:upgrade` (dry run first) to get `.kickoff/kit/`, `.kickoff/presets/` and the newer tools; add `--fields plan` to use the plan file.
