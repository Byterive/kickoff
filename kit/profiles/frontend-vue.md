---
title: Frontend Vue profile
summary: Vue additions to the frontend profile: vue_version frontmatter, reactivity pitfalls, Vue VS Code extension.
keywords: [vue, frontend, components, reactivity]
status: confirmed
updated: 2026-11-11
extends: frontend
---

# Profile: frontend-vue

Extends `frontend`. Everything not listed here comes from `frontend`.

## Extra frontmatter
screen, component, framework, vue_version, browser_min, a11y (checked/unchecked)

## Known pitfalls
- Destructuring a reactive object or a prop loses reactivity; use `toRefs` or access through the object.
- Mutating a prop directly is wrong; emit an event or use a local copy.
- `v-for` needs a stable `key`.

## VS Code
### Extensions
- Vue.volar: Vue language support (unverified id)

## Wrap-up additions
Record Vue and Node versions, new dependencies, screens touched, and the real output of test, lint and type-check.
