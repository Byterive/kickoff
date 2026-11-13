# CLAUDE.md (copy to project root as CLAUDE.md; keep under 200 lines)

Profile: <PROFILE>
Start every session by reading `INDEX.md` and `PROJECT_STATUS.md`. Open deeper files only by
following indexes/frontmatter. Project overview for humans: README.md (read only if needed).

Rules (full text: .kickoff/kit/CLAUDE_INSTRUCTIONS.md; profile rules: the kickoff plugin kit's profiles/<PROFILE>.md or this project's .kickoff/profile.md):
- After each meaningful step update the matching docs and PROJECT_STATUS.md; refresh `updated:`.
- Unknown -> write UNKNOWN; never invent. Never overwrite findings silently (mark `superseded`).
- Before ending: `python tools/build_index.py` then `python tools/check_budgets.py`; fix failures.
- Ask before moving/deleting files or raising budgets. Never commit secrets. Never read .env or secrets files.
- Git: never add `Co-Authored-By: Claude` or any Claude attribution to commits or PRs.
- Closing a thread: follow .kickoff/kit/WRAPUP_PROMPT.md.
- Plan file: do not edit planned dates or priority in .kickoff/plan.json unless I ask. Status and actual dates change only through tools/plan.py (done by /kickoff:wrapup).

## How to verify (definition of done)
Work is done only when these pass and you report the command run and its real output.
Never say "should work". For UI work, look at a screenshot you actually took.
Fill from the repo only (FOUND = cite file; otherwise UNKNOWN):
- Build: UNKNOWN
- Test: UNKNOWN
- Lint/format: UNKNOWN

## Never do in this repo
(From the user's answer to "What should Claude never do in this repo?")
- UNKNOWN

## Mistakes Claude made before
(One line each: what went wrong, the rule that prevents it. Add one whenever you are corrected.)
- none yet

## For the human
`/clear` between unrelated tasks. `/compact` when one task runs long. Esc Esc when we take a wrong
turn (rewinds file edits; shell-command changes need git).
