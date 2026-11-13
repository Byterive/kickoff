---
title: Frontend React profile
summary: React additions to the frontend profile: react_version frontmatter, hooks and key pitfalls, React test and lint checks.
keywords: [react, frontend, hooks, components]
status: confirmed
updated: 2026-11-11
extends: frontend
---

# Profile: frontend-react

Extends `frontend`. Everything not listed here comes from `frontend`.

## Extra frontmatter
screen, component, framework, react_version, browser_min, a11y (checked/unchecked)

## Known pitfalls
- A `key` must be stable and unique among siblings; an array index as key breaks state when the list reorders.
- Hooks run in the same order on every render: no hooks inside conditions or loops.
- An effect that sets state it depends on can loop; list every dependency.
- Do not mutate state or props; copy first.

## DONE means
Screen works at the target breakpoints with empty, loading and error states, component tests pass, `tsc` and lint are clean, keyboard use and labels checked, documented.

## Wrap-up additions
Record React and Node versions, new dependencies, screens touched, and the real output of test, lint and type-check.
