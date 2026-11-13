---
title: Backend Go profile
summary: Go additions to the backend profile: go_version frontmatter, 400-line .go budget, go test and go vet checks, Go VS Code extension.
keywords: [go, backend, api, migrations, deploy]
status: confirmed
updated: 2026-11-11
extends: backend
---

# Profile: backend-go

Extends `backend`. Also reached by the old name `go-backend`. Everything not listed here comes from `backend`.

## Extra frontmatter
package, endpoint, service, env (local/staging/prod), go_version

## Budgets
Code: max 400 lines per .go file. Docs: default budgets.

## Never do
- Skip `go vet` or ignore its findings before calling work done.
- Vendor or commit /bin and test binaries.

## DONE means
Handler implemented, tests pass (`go test ./...`), `go vet ./...` is clean, documented, migration reversible or noted.

## Wrap-up additions
Record go version, new dependencies (go.mod), env vars added, and `go vet` / `go test` results.

## VS Code
### Extensions
- golang.go: official Go language support
### Settings
- `"go.useLanguageServer": true`
- `"[go]": { "editor.formatOnSave": true }`
