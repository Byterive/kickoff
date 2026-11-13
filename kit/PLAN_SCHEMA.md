---
title: Plan file schema
summary: "The shared plan file .kickoff/plan.json (schema 1): phases and steps with planned and actual dates, status words, priority, who may write which field, and the rules plan.py enforces."
keywords: [plan, schema, phases, steps, priority, timeline, plan.json]
status: confirmed
updated: 2026-11-02
---

# Plan file schema (`.kickoff/plan.json`, schema 1)

Used when the tracking tier is `plan` (see `FIELDS_CONTRACT.md`). Plain JSON, UTF-8, 2-space
indent, trailing newline. Read with any tool; change status and actual dates only through `tools/plan.py`.
Conformance files that every reader and writer (kickoff and any other tool) must handle: `kit/tests/plan/` (see `expected.json`) and
`kit/examples/plan.example.json`.

## Shape
```json
{ "schema": 1, "priority": 20,
  "phases": [
    { "id": "p1", "name": "Design", "start": "2026-11-01", "end": "2026-11-14", "status": "DONE",
      "actual_start": "2026-11-01", "actual_end": "2026-11-16",
      "steps": [
        { "id": "p1-s1", "name": "Write the brief", "start": "2026-11-01", "end": "2026-11-05", "status": "DONE",
          "actual_start": "2026-11-01", "actual_end": "2026-11-04", "evidence": "PROJECT_BRIEF.md" } ] } ] }
```

## Fields
| field | where | meaning |
|---|---|---|
| `schema` | top | integer, 1 |
| `priority` | top | integer 1..999 or empty. Lower is more urgent. Use sparse ranks (10, 20, 30) so one drag changes one file. Ties between projects: priority, then project name |
| `phases` | top | ordered list; order is the plan order |
| `id` | phase, step | unique in the file, stable, letters digits `. _ -`. Never reused or renamed; `NEXT.md` refers to steps by id |
| `name` | phase, step | non-empty text |
| `start`, `end` | phase, step | planned dates `YYYY-MM-DD` or empty. `end` is not before `start`; a step lies inside its phase when both are set |
| `status` | phase, step | `PLANNED`, `IN_PROGRESS`, `DONE`, `BLOCKED`, `CUT`; missing means `PLANNED` |
| `actual_start`, `actual_end` | phase, step | what really happened, `YYYY-MM-DD` or empty; `actual_end` is not before `actual_start` |
| `evidence` | phase, step | optional text: the file, commit or command output that shows a step is DONE |
| `steps` | phase | optional ordered list of steps |
| `meta` | top | optional; `plan.py` sets `updated_by` and `updated_at` on every write; another tool may set its own |

Rules: empty means not set, never guess. Unknown keys are preserved by every writer. The current phase and step are derived (the
first phase and step not `DONE` or `CUT`) and never stored. Slips are derived from planned and actual dates and never stored.

## Status words in a profile's own language
`plan.py set-status` accepts these on input and stores the canonical word.
| canonical | also accepted |
|---|---|
| `DONE` | PASSED, COMPLETE, COMPLETED, FINISHED |
| `IN_PROGRESS` | WIP, ACTIVE, STARTED, INPROGRESS, "in progress" |
| `PLANNED` | TODO, PENDING, UNTESTED |
| `BLOCKED` | HOLD, ON_HOLD, STUCK |
| `CUT` | DROPPED, CANCELLED, CANCELED, WONTFIX |
`PROJECT_STATUS.md` keeps the profile's own words (PASSED, DOUBTFUL ...) for its tables. The plan uses the five words above; `project_status` in the front
matter mirrors the profile word for the current state.

## Who writes what (one writer per field, everyone reads everything)
| field | writer |
|---|---|
| structure: add, remove, rename or reorder phases and steps (ids, names) | you, by hand or in a tool of your own. Bootstrap writes the first version from your interview. `/kickoff:wrapup` never changes structure; it lists proposed changes in `NEXT.md` |
| planned `start`, `end`, `priority` | you, by hand or in a tool of your own, on explicit action |
| `status`, `actual_start`, `actual_end`, `evidence` | `/kickoff:wrapup`, only through `plan.py` |
| `PROJECT_STATUS.md`, `NEXT.md` | `/kickoff:wrapup` |
| `deadline`, `target_date` (front matter) | you |

Another tool may change only planned dates and priority (and structure on your action), as an atomic replace after checking that the file has not changed since it was read. Work that was not planned: wrap-up reports it in `NEXT.md`; you decide whether to add a step.

## plan.py behaviour
`validate`, `show`, `next`, `set-status`, `render-status`, `init` (see its header). It never changes start, end, priority, ids, names or unknown keys. A write is atomic. If the file changed between read and write, plan.py re-reads and applies only its own change again, so both edits survive. Exit codes: 0 ok, 1 error or refused, 2 invalid file.
