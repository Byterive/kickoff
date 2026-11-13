---
title: Frontend profile
summary: Shared folder skeleton, status tables, budgets, never-do rules and VS Code setup for web frontends; framework secondaries (frontend-react, frontend-vue) extend it.
keywords: [frontend, web, ui, components, accessibility, family]
status: confirmed
updated: 2026-11-11
---

# Profile: frontend

Main profile of the frontend family. Secondaries (`frontend-react`, `frontend-vue`) say `extends: frontend` and add only what differs.

## Folder skeleton
docs/product (flows, requirements) | docs/design (tokens, layouts, screenshots) | docs/components (one note per shared component)
| docs/accessibility (checks, known gaps) | docs/decisions | src/ | tests/ | tools/

## Extra frontmatter
screen, component, framework, browser_min, a11y (checked/unchecked)

## PROJECT_STATUS.md tables
- Screens: name | route | status (PLANNED/WIP/DONE) | tests | design link
- Components: name | used in | states covered (empty/loading/error) | tests
- Browser and device matrix: browser/device | build | result | issues
- Accessibility checks: item | status | note
- Gaps and next steps

## Budgets
Code: max 400 lines per source file (split large components). Docs: default budgets.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Design: tokens, layout, flows
- Build: components and screens
- Harden: accessibility, browsers, performance
- Release

## Never do
- Commit secrets or .env files; keep API keys out of client code.
- Disable lint, type-check or tests to get a build through.
- Add a dependency without noting it and its licence.
- Load third-party scripts without asking.

## DONE means
Screen works at the target breakpoints with empty, loading and error states, tests pass, type-check and lint are clean, keyboard use and labels checked, documented.

## Wrap-up additions
Record framework and Node versions, new dependencies, screens touched, and the real output of test, lint and type-check.

## VS Code
### Extensions
- dbaeumer.vscode-eslint: lint
- esbenp.prettier-vscode: format
- editorconfig.editorconfig: shared formatting rules
- ms-playwright.playwright: browser tests
### Settings
- `"editor.formatOnSave": true`
- `"editor.defaultFormatter": "esbenp.prettier-vscode"`

## Companion plugins
- frontend-design: UI design guidance | when: building screens | command: ask for a UI design review
