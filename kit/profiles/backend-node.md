---
title: Backend Node profile
summary: Node.js and TypeScript additions to the backend profile: node_version frontmatter, 400-line .ts budget, npm test, tsc and eslint checks, ESLint and Prettier VS Code extensions.
keywords: [node, nodejs, typescript, express, fastify, backend, api]
status: confirmed
updated: 2026-11-12
extends: backend
---

# Profile: backend-node

Extends `backend`. Everything not listed here comes from `backend`.

## Extra frontmatter
package, endpoint, service, env (local/staging/prod), node_version, framework (express/fastify/nest/other), language (ts/js)

## Budgets
Code: max 400 lines per .ts or .js file. Docs: default budgets.

## Never do
- Install packages globally or edit lockfiles by hand; use the project's package manager and commit its lockfile.
- Commit node_modules, dist or .env files.
- Add a dependency without noting why in the README or package notes.

## DONE means
Handler implemented, `npm test` passes, `npx tsc --noEmit` (TypeScript) and `npx eslint .` are clean, documented, migration reversible or noted.

## Wrap-up additions
Record node version, new dependencies (package.json), env vars added, and the real output of `npm test`, `tsc` and `eslint`.

## VS Code
### Extensions
- dbaeumer.vscode-eslint: lint in the editor
- esbenp.prettier-vscode: formatting
### Settings
- `"editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" }`
- `"[typescript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" }`
