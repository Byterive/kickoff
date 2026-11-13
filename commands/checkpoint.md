---
description: "Light mid-session save (seconds): NEXT.md and PROJECT_STATUS.md, so /clear then /resume is safe. The full close-out stays /kickoff:wrapup"
allowed-tools: Bash(python:*), Bash(git status:*), Bash(git log:*)
---

Checkpoint now. Fast: no reindex, no budget checks, no knowledge capture, no commits (those stay in /kickoff:wrapup). Do not invent: unknown stays UNKNOWN; never overwrite a finding silently (mark it `superseded`).

1. Always write NEXT.md (template `.kickoff/kit/templates/NEXT.template.md` or the existing file's layout): `saved: checkpoint` and `updated:` in the front matter; "Stopped at" (latest commit from `git log -1 --format='%h %cs'` plus one line on what we were doing), "Next 3 steps", "Half-done / uncommitted" (recomputed from `git status --short`, or "nothing uncommitted"), "Watch out for". Overwrite it, but keep any "Plan changes proposed" block that is still waiting for me.
2. Always refresh PROJECT_STATUS.md: `updated:`, plus phase and step status. With `.kickoff/fields.json` tier `plan`: for each step finished this session with evidence you can name, run `python tools/plan.py set-status <step-id> DONE --evidence "<evidence>"` (set the next step IN_PROGRESS the same way), then `python tools/plan.py render-status --write PROJECT_STATUS.md`, and list next steps from `python tools/plan.py next --count 3` by id. Never edit planned dates or priority; write any plan change you think is needed under "Plan changes proposed" in NEXT.md. Without a plan, edit only the status lines that this session's evidence changes.
3. Write REQUIREMENTS.md and DECISIONS.md only if something new was decided, asked or changed this session (a decision I did not answer explicitly goes in as a numbered question, not as decided). Leave them alone otherwise.
4. If `git status --short` shows uncommitted changes, warn me with the count. Never commit.

End with one line only: what you saved (NEXT.md, PROJECT_STATUS.md, and REQUIREMENTS.md / DECISIONS.md if touched, or "REQUIREMENTS.md and DECISIONS.md untouched"), the uncommitted warning if any, and "/clear then /resume is now safe".
