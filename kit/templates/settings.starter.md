---
title: Starter permissions explained
summary: One-line reason for each deny rule in settings.starter.json so you can drop any rule you do not want.
keywords: [permissions, settings, deny, secrets, env]
status: confirmed
updated: 2026-10-22
---

# settings.starter.json: what each rule does

Merged into the project's `.claude/settings.json` by bootstrap (existing rules are kept). No allow-list is
added, because safe everyday commands differ per repo; add those yourself once you see which prompts repeat.

| Rule | Why |
|---|---|
| `Read(./.env)`, `Read(./.env.*)` | Stops Claude reading local environment files that hold keys and passwords |
| `Read(./**/.env)`, `Read(./**/.env.*)` | Same, for env files in subfolders (monorepos, services) |
| `Read(./secrets/**)`, `Read(./**/secrets/**)` | Blocks any folder named secrets |
| `Read(./**/*.pem)`, `Read(./**/*.key)` | Blocks private keys and certificates |

To drop a rule, delete its line from `.claude/settings.json`. Deny rules cover Claude's Read tool; they are a
guard, not a vault, so still keep secrets out of git and out of the repo where you can.
