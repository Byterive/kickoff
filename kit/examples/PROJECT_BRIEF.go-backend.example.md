---
title: Go backend brief example
summary: Filled example PROJECT_BRIEF for a small Go REST API with Postgres.
keywords: [example, go, backend, brief]
status: draft
updated: 2026-10-17
---

# PROJECT_BRIEF: "Inventory API" (example)

## 1. Goal
REST API for stock tracking used by a web admin. Done = 12 endpoints, 80% test coverage, deployed to staging.

## 2. Profile
go-backend

## 3. Background and sources
Existing spec: docs/api/openapi.yaml. Legacy schema dump in _inbox/legacy.sql.

## 4. Environment and tools
Go 1.23, Postgres 16, Docker, chi router, golang-migrate. Env names only: DATABASE_URL, JWT_SECRET (values in password manager).

## 5. Rules and constraints
p95 latency under 150 ms. JWT auth on all but /health. No breaking API changes after staging.

## 6. Definition of status words
DONE = handler + tests pass (`go test ./...`) + documented + migration reversible.

## 7. Already done / known problems
Auth and /items done. /orders half-built. Migration 0004 not reversible.

## 8. Next steps wanted
1) Finish /orders 2) Fix migration 0004 3) Add rate limiting 4) Staging deploy runbook.

## 9. Never do
Touch prod, run destructive migrations unasked, commit .env, disable tests.
