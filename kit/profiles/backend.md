---
title: Backend profile
summary: Shared folder skeleton, status tables, budgets, never-do rules and VS Code setup for backend services; language secondaries (backend-go, backend-python) extend it.
keywords: [backend, api, service, migrations, deploy, family]
status: confirmed
updated: 2026-11-11
---

# Profile: backend

Main profile of the backend family. Secondaries (`backend-go`, `backend-python`) say `extends: backend` and add only what differs. Old name `go-backend` is an alias of `backend-go`.

## Folder skeleton
docs/architecture | docs/api (endpoint notes + OpenAPI link) | docs/data (schemas, migrations log)
| docs/runbooks (deploy, rollback, incidents) | docs/config (env vars: names/purpose only) | docs/decisions | tools/

## Extra frontmatter
package, endpoint, service, env (local/staging/prod), language, runtime_version

## PROJECT_STATUS.md tables
- Endpoints: method+path | handler | auth | tests | status (PLANNED/WIP/DONE) | doc link
- Migrations: id | purpose | applied in (local/staging/prod) | reversible?
- Services/deploys: service | env | version | date | health
- Tests: package | coverage % | last run | failures
- Gaps and next steps

## Budgets
Code: max 400 lines per source file. Docs: default budgets.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Design
- Build
- Staging
- Production

## Never do
- Commit secrets or .env files (document names only).
- Run destructive migrations or touch prod without explicit approval.
- Change public API contracts silently (log in docs/decisions).
- Disable tests to pass CI.

## DONE means
Handler implemented, tests pass, documented, migration reversible or noted.

## Wrap-up additions
Record the runtime version, new dependencies, env vars added, and the real output of the test and lint commands.

## VS Code
### Extensions
- editorconfig.editorconfig: shared formatting rules
- eamodio.gitlens: history and blame
- redhat.vscode-yaml: CI, compose and OpenAPI files
- ms-azuretools.vscode-docker: Dockerfile and compose support
- usernamehw.errorlens: shows errors inline
### Settings
- `"files.insertFinalNewline": true`
- `"editor.formatOnSave": true`

