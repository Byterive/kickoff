---
title: NetSuite profile
summary: Folder skeleton, status tables, budgets and never-do rules for NetSuite customization projects (SuiteScript, records, workflows).
keywords: [netsuite, suitescript, saved search, workflow, sandbox]
status: confirmed
updated: 2026-10-17
---

# Profile: netsuite

## Folder skeleton
docs/requirements | docs/scripts (one note per SuiteScript: type, trigger, records) | docs/records (custom records/fields, internal IDs)
| docs/searches (saved searches, criteria) | docs/workflows | docs/integrations | docs/deployments (env log) | docs/decisions | src/ (SuiteScripts)

## Extra frontmatter
script_id, script_type (UserEvent/Client/Suitelet/MapReduce/Scheduled/RESTlet), record_type, env (sandbox/prod), deployment_id, api_version

## PROJECT_STATUS.md tables
- Customizations: name | type | script_id/internal ID | env | status (DESIGN/DEV/SANDBOX-TESTED/PROD) | doc link
- Deployments: date | item | from env -> to env | by | rollback plan
- Test cases: scenario | env | expected | actual | pass/fail
- Open requirements and risks (governance limits, permissions)
- Gaps and next steps

## Budgets
Code: max 400 lines per script file (split into modules). Docs: default.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Discovery
- Sandbox build
- UAT
- Production release

## Never do
Touch production or deploy to it without explicit approval; commit account IDs/tokens/credentials;
change standard records/workflows without documenting; skip governance-limit checks; delete custom records or fields.

## DONE means
Tested in sandbox with logged test cases, permissions verified, deployment record and rollback written.

## Wrap-up additions
Record internal IDs created, env touched, governance/usage concerns, and what was tested.

## VS Code
### Extensions
- dbaeumer.vscode-eslint: lint SuiteScript files
- editorconfig.editorconfig: shared formatting rules
### Settings
- `"files.insertFinalNewline": true`
### Notes
Install the SuiteCloud Extension for Visual Studio Code (Oracle NetSuite) by name; its id is not verified here, so it is not in the list.

