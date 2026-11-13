---
title: Claude plugin profile
summary: Folder skeleton, status tables, how to verify, never-do rules, known pitfalls and UI rules for building a Claude Code plugin or mod in TypeScript.
keywords: [claude-plugin, mod, typescript, hooks, ui, profile]
status: confirmed
updated: 2026-11-11
---

# Profile: claude-plugin

Use for: building Claude Code plugins/mods in TypeScript (hooks modules, a band above the prompt, panes, slash commands).

## Defaults for the /kickoff questions
Plugin set: minimal; keep any plugin this project replaces until the new one passes. Guide: none. Tracking tier: Plan, with phases and no dates. Registration: private (withheld) first; public only on the owner's go.

## Folder skeleton
.claude-plugin/plugin.json | hooks/hooks.json | hooks/*.tsx | types/index.d.ts | docs/ | design/ (UI specs, screenshots) | tests/ | tools/
Root files: DECISIONS.md, REQUIREMENTS.md, PROJECT_STATUS.md, NEXT.md, INDEX.md, CLAUDE.md. No tsconfig in the repo (the types path depends on the version). Empty folders are created only when needed.

## Extra frontmatter
phase, surface (terminal, desktop, vscode, all), source (observed, configured, inferred, unknown)

## PROJECT_STATUS.md tables
- Phases: phase | goal | status (PLANNED/IN_PROGRESS/DONE) | exit evidence
- Surfaces: surface | minimum version | what draws | status (PASSED/DOUBTFUL/FAILED/UNKNOWN)
- Features: feature | phase | data source | status
- Risks: risk | impact | mitigation
- Unresolved decisions: id | question | recommendation
- Gaps and next steps

## Budgets
Code: max 400 lines per file. Docs: kit defaults.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Capability and data contract: register privately; read the plugin types; list what each surface supports
- Core feature
- Surface checks: terminal, Desktop, VS Code
- Polish and release

## How to verify (definition of done for CLAUDE.md)
- Test: `claude plugin test .` from the repo root
- Validate: `claude plugin validate .` from the repo root (an ICON_MISSING warning is OK)
- Type-check: `tsc -p <tsconfig outside the repo>` that includes the plugin-authoring skill's claude-code.d.ts, types/index.d.ts and hooks/*.ts(x); jsx `react`, jsxFactory `h`
- Build and lint: NOT FOUND unless the project adds them
- UI work: a real screenshot on each surface used (terminal, Desktop, VS Code)

## Never do
- Send network requests, start processes or call models from the base plugin
- Store or show prompt text, tool results or secrets; read .env files
- Run /compact or /clear, change settings or send prompts for the user
- Show an inferred figure as certain: label every figure observed, configured, inferred or unknown
- Name withheld plugins in public text; push to the production repo from dev
- Copy upstream code without its licence notice
- Add Claude co-author lines or any Claude attribution

## Known pitfalls (seed the CLAUDE.md "Mistakes" list)
- `$.clock.every` returns a Timer ({ cancel }), not a function.
- The function-hook `session.start` has only cwd, surface and isInteractive, and fires once per plugin load, never on /clear.
- `ui.find` matches `text`, not `label`; make a negative test fail once first.
- Every atom must be declared in the file that reads it, so shared atom files fail to load.
- Every state key must be declared in types/index.d.ts.
- Surfaces refuse fractional percentage widths; use whole %.
- A `key` inside a mapped list is not kept as a prop, so tests must match on text.
- Pane placement (dock or inline) is chosen by the host and is read-only.
- VS Code reports fewer columns than it draws; set width cut-offs from measured values.
- The terminal has no Svg; give it a text fallback.

## UI rules
- Band: two rows at most, never wrapping (flexWrap nowrap; the bar shrinks first, then the text truncates).
- Bars are made of filled Boxes, not block characters (no seams in HTML).
- Short labels at narrow widths; `wrap="truncate-end"`.
- Check the previous plugin's UI before designing.

## Process
- Clarify before building: a numbered brief with options, a recommendation and a question for each item; wait for an answer to each number.
- Record answers in DECISIONS.md and REQUIREMENTS.md before building.
- Write the test first and see it fail.
- Commit after each plan step; never add Claude attribution.
- Run build_index and check_budgets before ending.

## DONE means
Works on each surface used at its minimum version, `claude plugin test .` has 0 failures, a screenshot is taken on each surface, every figure is labelled.

## Wrap-up additions
Record the Claude Code version tested, surfaces checked, the real output of `claude plugin test .`, and any undocumented field relied on.

## VS Code
### Extensions
- anthropic.claude-code: Claude Code in VS Code
- dbaeumer.vscode-eslint: lint the hooks modules
- esbenp.prettier-vscode: format TypeScript and JSON
### Settings
- `"typescript.tsdk"`: point at the TypeScript used for the type-check (no tsconfig lives in the repo)
