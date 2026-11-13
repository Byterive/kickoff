---
title: Master setup prompt
summary: Paste into a new Claude session to bootstrap a project with indexes, budgets, status dashboard and standing rules for a chosen PROFILE.
keywords: [setup, bootstrap, prompt, profile]
status: confirmed
updated: 2026-10-25
---

# Master setup prompt

Set `PROFILE` on the first line, then paste everything inside the block.
Profiles: `unity`, `backend`, `backend-go`, `backend-python`, `backend-rust`, `backend-node`, `frontend`, `frontend-react`, `frontend-vue`, `data-research`, `utility`, `netsuite`, `mobile-app`, `desktop-app`, `personal-utilities`, `trading-research`, `claude-plugin`, or `custom` (describe it in PROJECT_BRIEF.md).

````text
PROFILE: <profile-name>
KIT: <kit>   (the kickoff plugin's kit/ folder, ${CLAUDE_PLUGIN_ROOT}/kit)

Set up a "progressive disclosure" knowledge system for this project, then maintain it
for the whole life of the project. Do not add Claude as co-author or any Claude
attribution to commits or PRs, unless I choose "Yes" to the setup question about the Claude contribution line
(`python KIT/tools/attribution.py`; the choice is in `.kickoff/attribution.json`).

## Phase 0: read and ask
0. Undo plan: run `git status --short`. If there are uncommitted changes, ask me to commit
   (or confirm I have a backup) BEFORE anything that creates or moves files. Not a git repo:
   tell me, and ask me to back up first. Remind me once: Esc Esc rewinds your file edits,
   but files changed by shell commands need git.
1. Read PROJECT_BRIEF.md. If missing, interview me (max 5 questions: goal, profile, sources, never-do, next steps), draft it from
   KIT\PROJECT_BRIEF.template.md and show it for review. `--dry-run` anywhere: list every file and plugin change, write nothing.
2. Read KIT\CLAUDE_INSTRUCTIONS.md and the profile (lookup: .kickoff\profile.md, then ~\.claude\kickoff\profiles\<PROFILE>\profile.md,
   then KIT\profiles\<PROFILE>.md). PROFILE=custom: follow KIT\profiles\custom.md to interview me and write the profile + preset.
3. If _audit/ exists, use it to fill PROJECT_STATUS.md and plan where existing files belong.
   If the project already has files but no _audit/, tell me to run KIT\AUDIT_PROMPT.md first.
4. Plugins and skills: run `python KIT\tools\proj_toggle.py list`. If PROJECT_BRIEF.md section 10 names a choice, use it.
   Otherwise ask ONE question: Minimal (only kickoff + always-on) / Recommended (the profile preset, default) /
   Keep all / Select (multi-select of what to turn OFF). Apply with `python KIT\tools\proj_toggle.py preset <PROFILE> --tier <t>`
   or `off <names>`, preview first with `--dry-run`, and log the choice in DECISIONS.md. It only edits this project's
   .claude/settings.json (backup .bak, `undo` restores); user-level settings stay untouched. Tell me to start a new
   session afterwards (terminal: /reload-plugins).
4b. Guide: ask ONE question (skip if brief section 11 is filled): "Build a plain-language guide for this project? No / Local".
   On Local: write .kickoff/guide.json from KIT\templates\guide.json.template (contract 1; hub from ~\.claude\kickoff\config.json
   if it exists). If the `guidebook` command exists, run `guidebook init --dry-run` and show the proposed versions; otherwise say
   guidebook is not installed and that the config is ready for when it is. Contract: KIT\GUIDE_CONTRACT.md.
4c. Tracking fields (skip if brief section 12 is filled): ask ONE question: None / Fields only / Plan (kit\FIELDS_CONTRACT.md).
   Unless None, apply with `python KIT\tools\upgrade.py . --fields fields|plan --apply` after Phase 1. With Plan: interview me for
   phases (offer the profile's "Default phases"), rough dates and a priority (blank = not set); after Phase 1 run
   `python tools/plan.py init --profile <PROFILE>`, write my answers into .kickoff/plan.json (the one time you may set planned
   dates and priority, because I gave them), then `plan.py validate` and `plan.py render-status --write PROJECT_STATUS.md`.
   Schema: kit\PLAN_SCHEMA.md.
5. Ask me up to 10 questions about anything missing or contradictory. Wait for answers.

## Phase 1: one-time setup
1. Create the folder skeleton from the profile. Skip empty folders for things that do not exist yet.
2. Copy KIT\tools\ into ./tools/ (build_index.py, check_budgets.py, budgets.json, proj_toggle.py, doctor.py; plan.py and plan_lib.py when the tier is plan).
   Create DECISIONS.md, NEXT.md and REQUIREMENTS.md from KIT\templates\, .gitignore from KIT\gitignore\common.gitignore + <PROFILE>.gitignore
   and .gitattributes from KIT\templates\gitattributes (if a file exists, only append missing lines).
3. Frontmatter standard: every .md (except INDEX.md, README.md, CLAUDE.md) starts with
   title, summary (ONE specific sentence), keywords, status, updated (YYYY-MM-DD),
   plus the profile's extra fields.
4. Create PROJECT_STATUS.md using the profile's status tables.
5. Create CLAUDE.md from KIT\CLAUDE.template.md (max 200 lines) and fill in the profile name.
   Fill its "How to verify" block ONLY from commands you find in the repo (README, package.json,
   Makefile, go.mod, CI config, scripts). Report each as FOUND (with file), GUESSED, or NOT FOUND.
   Never invent a command; leave NOT FOUND items as UNKNOWN.
6. Starter permissions: show me KIT\templates\settings.starter.json and its explanations
   (KIT\templates\settings.starter.md). If .claude/settings.json exists, merge the deny rules in
   without removing anything; otherwise create it. Never read .env or secrets files, even to check them.
7. This is a git repo: install tools/pre-commit.sample as .git/hooks/pre-commit. If not a repo, say so.
8. Run `python KIT\tools\upgrade.py . --profile <PROFILE> --sections yes --clarity yes --apply` (adds .kickoff/kit/ copies of CLAUDE_INSTRUCTIONS.md and
   WRAPUP_PROMPT.md that CLAUDE.md points to, .kickoff/presets/, the tools, the clarity rule block in CLAUDE.md, REQUIREMENTS.md, and the status
   sections How to run / Setup / Data / Troubleshooting in PROJECT_STATUS.md pre-filled from the repo and marked GUESSED; never overwrites). Then show me the four
   sections as a numbered brief (for each: what was found, your recommendation, the question) and record my answer against each number. Then run: python tools/build_index.py  then  python tools/check_budgets.py --profile <PROFILE>
8b. VS Code: run `python KIT	oolsscode_ext.py . --profile <PROFILE>` (dry run), show me the recommended extensions and settings from the profile's "VS Code" section, and write `.vscode/extensions.json` with `--apply` only after I say yes. It merges, never overwrites, skips unverified ids, and never installs anything.
8c. Companion plugins: run `python KIT	ools\companions.py . --profile <PROFILE>`. For each missing one show its role and the install command and ask me; run `claude plugin install ...` only after I say yes for that plugin, then tell me to start a new session. Never install silently. Marketplace names come from ~/.claude/kickoff/config.json and stay out of project files.
9. Run `python tools/doctor.py`. Show me the root INDEX.md, PROJECT_STATUS.md and the doctor result and STOP. Do not start project work until I say go.
   Show me each file before you write it. First question to ask me: "What should Claude never do in this repo?"

## Existing files
Never move, rename or delete files without showing me the old-path -> new-path plan and getting approval.
````
