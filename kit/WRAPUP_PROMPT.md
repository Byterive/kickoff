---
title: Wrap-up prompt
summary: Closing message to send at the end of every thread so knowledge, status and indexes are saved before the thread is closed.
keywords: [wrap-up, handover, close thread, update docs]
status: confirmed
updated: 2026-10-25
---

# Wrap-up prompt

````text
Wrap up this thread:
1. Update all knowledge, findings, results, data-source and script docs for what we did
   (frontmatter complete, summaries specific, `updated:` dates refreshed).
2. Update PROJECT_STATUS.md: statuses, tables, gaps. Never leave a status implicit
   (use the profile's status words; UNKNOWN if there is no evidence).
3. Mark anything contradicted by new evidence as `superseded` and link the new file.
4. Add a "Next steps" section to PROJECT_STATUS.md for the next thread, including
   anything half-done and exactly where it stopped.
5. Plan (only when .kickoff/fields.json has tier "plan"; otherwise skip this step):
   for each step finished this thread, and only with evidence you can name, run
   `python tools/plan.py set-status <step-id> DONE --evidence "<file, commit or command output>"`
   (add `--actual-end <date>` if it ended on another day); set the step starting next to IN_PROGRESS the same way; set a phase
   DONE when all its steps are DONE. If a step ended after its planned end, say "slipped N days" in PROJECT_STATUS.md.
   Never edit start, end or priority, and never add, remove or rename phases or steps: write any change you think the plan
   needs under "Plan changes proposed" in NEXT.md for me to decide. Then run
   `python tools/plan.py render-status --write PROJECT_STATUS.md` to refresh the "Where we are" block.
6. Status sections (only when .kickoff/options.json has "sections": true; otherwise skip): in PROJECT_STATUS.md, for "How to run" and
   "Setup" re-run the commands this thread touched or that are marked GUESSED and quote the real output; replace GUESSED with the confirmed
   text, or write UNKNOWN plus the question that would settle it. "Data": check every listed path still exists, note what changed, and,
   if the project has a downloader, its command, parameters and settings. "Troubleshooting": add the problems met this thread (what you saw,
   why, what fixed it). Never leave a section empty and never invent a command.
7. Requirements (only when REQUIREMENTS.md exists; otherwise skip): add every requirement I agreed this thread in my words, set each
   status with the evidence (file or command output), keep the questions I have not answered as OPEN, and trace every requirement to
   evidence. If a decision, phase, step or requirement changed this thread without my explicit answer, list it as a numbered question with
   your recommendation; do not record it as decided. Report partial and missing items in the summary yourself.
8. From the project root run the project's own tools: python tools/build_index.py  then  python tools/check_budgets.py
   (never the kit copy, never from another folder).
   Fix every failure by condensing or splitting. Ask me before raising a budget.
9. If I corrected you this thread, add one line per correction to "Mistakes Claude made
   before" in CLAUDE.md (what went wrong + the rule that prevents it). Keep CLAUDE.md under 200 lines.
10. Verify before claiming done: run the commands in CLAUDE.md "How to verify" and quote their
   real output. If a command is UNKNOWN or failed, say so; never write "should work".
11. List every file you created or changed. Do not commit unless I ask; if I do, do not
   add Claude as co-author.
12. Append this thread's decisions (what was chosen and why) to DECISIONS.md, newest first, one line each.
    Write NEXT.md (template: kit/templates/NEXT.template.md): where we stopped, next 3 steps, half-done
    work, traps found. Overwrite it; /resume reads it first. Set `saved: wrapup` in its front matter (a checkpoint sets `saved: checkpoint`). Recompute "Half-done / uncommitted" from `git status --short` (list the files, or
    write "nothing uncommitted" when it is clean) and put the latest commit (`git log -1 --format='%h %cs'`) in "Stopped at"; never copy the old text. With the plan tier, list the next steps by step id from
    `python tools/plan.py next --count 3` (ids, not copied dates: /resume reads the live plan) plus anything I said.
13. If .kickoff/guide.json exists with "enabled": true and the `guidebook` command is available, run `guidebook update` and
    report what changed. If it fails or is missing, say so and carry on; never fail the wrap-up because of it.
14. If .kickoff/fields.json exists with tier "fields" or "plan", refresh the tracking
    fields (kit/FIELDS_CONTRACT.md): `project_status`, `blocked_by`, `updated` in PROJECT_STATUS.md and `next` + `updated` in
    NEXT.md (with the plan tier, `project_status` mirrors the current phase and `next` the first item of `plan.py next`).
    Change `target_date` / `deadline` only if I said so; leave a key blank rather than guess. Skip this step when the tier is
    "none" or the file is missing.
15. Finish with one summary: files created/changed, rules added, what you tested, what still needs
    my input, and the 3 things I should try first next time.
````
