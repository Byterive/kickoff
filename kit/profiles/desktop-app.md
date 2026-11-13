---
title: Desktop app profile
summary: Folder skeleton, status tables, budgets and never-do rules for local desktop apps (default stack Tauri, Rust, React/TypeScript, SQLite).
keywords: [desktop, tauri, rust, react, sqlite, windows]
status: confirmed
updated: 2026-10-31
---

# Profile: desktop-app

## Folder skeleton
docs/product (definition, non-goals, flows) | docs/architecture (modules, data model, diagrams) | docs/safety (permissions, scan and process rules)
| docs/decisions | docs/acceptance | src/ (UI) | src-tauri/ (native layer) | tools/

## Extra frontmatter
module, layer (ui/native/data), platform (windows/mac/linux), stack

## PROJECT_STATUS.md tables
- Modules: module | layer | responsibility | status (PLANNED/WIP/DONE) | doc link
- Flows: flow | screens | status | acceptance link
- Acceptance criteria: id | criterion | verified how | status (PASSED/FAILED/UNKNOWN)
- Risks: risk | impact | mitigation | owner
- Unresolved decisions: question | options | needed by
- Gaps and next steps

## Budgets
Code: max 400 lines per file (.rs, .ts, .tsx included). Skips `target/`, `node_modules/`, `src-tauri/gen/`.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Design
- Build
- Packaging
- Beta
- Release

## Never do
Write, move or delete user data as a side effect; read or scan outside folders the user selected; launch processes except through the allowlisted native commands with argument-safe invocation; run write operations on a user's Git repo; commit secrets; start building before the plan is approved.

## DONE means
Feature works in a built app, acceptance criteria verified, no write access added outside its scope, documented. Verify commands (`cargo check`, `npm run build`, `tauri build`) are only used if FOUND in the repo.

## Wrap-up additions
Record the stack versions, new native commands and permissions added, and the real output of the verify commands.

## VS Code
### Extensions
- rust-lang.rust-analyzer: Rust language support for src-tauri
- dbaeumer.vscode-eslint: lint the UI code
- esbenp.prettier-vscode: format the UI code
- tauri-apps.tauri-vscode: Tauri helpers (unverified id)
### Settings
- `"[rust]": { "editor.formatOnSave": true }`

## Companion plugins
- frontend-design: UI design guidance | when: building screens | command: ask for a UI design review
