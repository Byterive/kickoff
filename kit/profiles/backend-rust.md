---
title: Backend Rust profile
summary: Rust additions to the backend profile: rust_version frontmatter, 400-line .rs budget, cargo test, clippy and fmt checks, rust-analyzer VS Code extension.
keywords: [rust, cargo, backend, api, migrations]
status: confirmed
updated: 2026-11-12
extends: backend
---

# Profile: backend-rust

Extends `backend`. Everything not listed here comes from `backend`.

## Extra frontmatter
crate, endpoint, service, env (local/staging/prod), rust_version, framework (axum/actix/rocket/other)

## Budgets
Code: max 400 lines per .rs file. Docs: default budgets.

## Never do
- Ignore `cargo clippy` warnings or silence them with `#[allow]` without a written reason.
- Commit /target or credentials.
- Add `unsafe` without a comment saying why it is sound.

## DONE means
Handler implemented, `cargo test` passes, `cargo clippy -- -D warnings` and `cargo fmt --check` are clean, documented, migration reversible or noted.

## Wrap-up additions
Record rust version, new crates (Cargo.toml), env vars added, and the real output of `cargo test` and `cargo clippy`.

## VS Code
### Extensions
- rust-lang.rust-analyzer: official Rust language support
### Settings
- `"rust-analyzer.check.command": "clippy"`
- `"[rust]": { "editor.formatOnSave": true }`
