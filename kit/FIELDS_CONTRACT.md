---
title: Tracking fields contract
summary: Optional frontmatter fields and .kickoff files that make a project's status, next step, dates, blockers and plan machine-readable, for any tool, with tiers, keys and who may write each field.
keywords: [fields, frontmatter, status, deadline, blocked_by, plan, contract, ownership]
status: confirmed
updated: 2026-11-02
---

# Tracking fields contract

Entirely optional. Kickoff never adds these unless the user picks a tier; `none` is the default. They are plain files, so any tool or script can read them.

## Tiers (stored in `.kickoff/fields.json`)
| tier | adds |
|---|---|
| `none` | nothing (default; the choice is remembered so upgrade does not re-ask) |
| `fields` | the frontmatter keys below, nothing else |
| `plan` | `fields` plus the shared plan file `.kickoff/plan.json` (phases, steps, planned and actual dates, priority; see `PLAN_SCHEMA.md`) |

`.kickoff/fields.json`: `{ "contract": 1, "tier": "none|fields|plan" }`. A tier name from an older kit is read as `fields` (or `plan` when the file has `"plan": true`). Contract stays 1: new keys are optional and readers ignore keys they do not know.

## Keys
`PROJECT_STATUS.md` frontmatter:
| key | meaning |
|---|---|
| `project_status` | project state in the profile's status words, or `UNKNOWN` (not `status`: that key already means doc state: draft/confirmed) |
| `target_date` | soft target, `YYYY-MM-DD` |
| `deadline` | hard deadline, `YYYY-MM-DD` |
| `blocked_by` | one line, empty when not blocked |
| `updated` | last refresh, `YYYY-MM-DD` (already required) |

`NEXT.md` frontmatter: `next` = the single next action, one line.

Rules: blank means "not set", never guess (write `UNKNOWN` only in a document body, never in a date key). Dates are ISO only; if the source wording is ambiguous, keep it in the body and leave the key blank. A completion date is not a front matter key: with tier `plan` it lives as `actual_end` in `plan.json`; otherwise record it in the body.

## Who writes what (one writer per field, everyone reads everything)
| field | writer |
|---|---|
| `project_status`, `blocked_by`, `next`, `updated` | `/kickoff:wrapup` (mirrors the plan when tier `plan`) |
| `deadline`, `target_date` | you |
| `plan.json` structure (phases, steps, ids, names) | you, by hand or in a tool of your own; bootstrap writes the first version from your interview; wrap-up only proposes changes in `NEXT.md` |
| `plan.json` planned `start`, `end`, `priority` | you, by hand or in a tool of your own, on explicit action |
| `plan.json` `status`, `actual_start`, `actual_end`, `evidence` | `/kickoff:wrapup` through `tools/plan.py` only |
| `PROJECT_STATUS.md`, `NEXT.md` bodies | `/kickoff:wrapup` |

The write exception: another tool may change only planned dates, priority and (on your action) structure in `plan.json`, as an atomic replace after checking the file has not changed since it was read. Wrap-up never changes planned dates or priority. All other readers stay read-only.

## `.kickoff/plan.json` (tier `plan`)
See `PLAN_SCHEMA.md`. Test files for implementers: `kit/tests/plan/`, `kit/examples/plan.example.json`.
