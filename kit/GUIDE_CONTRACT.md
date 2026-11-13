---
title: Guide contract (kickoff side)
summary: The small config file .kickoff/guide.json that kickoff writes and guidebook reads, with the contract version number.
keywords: [guide, guidebook, contract, hub, config]
status: confirmed
updated: 2026-10-25
---

# Guide contract (kickoff side)

Owner of the full schema: the guidebook repo (`docs/kickoff-contract.md`). Kickoff keeps only this minimal copy and the `contract` number, so old projects keep working when the schema grows.

`.kickoff/guide.json` (template: `templates/guide.json.template`):
| field | meaning |
|---|---|
| `contract` | schema version, currently 1 |
| `enabled` | false = kickoff ignores the guide |
| `brand` | name shown in the guide header |
| `versions` | guide versions to build: layman, client, teammate, maintainer, quick-start or custom names |
| `output` | folder for the built guide, relative to the project (default `docs/guide`) |
| `publish` | `local` (default) or `github-pages` (prepares a folder, never pushes) |
| `hub` | folder of the main guide; empty means none (used by the hub phases, ignored by guidebook today). Kickoff never writes your hub path into the project (it is a local path); a hub path, if you keep one, lives in `~/.claude/kickoff/config.json` key `hub` |

Kickoff only writes this file and calls `guidebook init` / `guidebook update` if the `guidebook` command exists. It never renders HTML. A failing guidebook call never fails kickoff or wrap-up.
The built guide exposes `<output>/guide.manifest.json`; the hub (guidebook mode) reads it. Kickoff's `/doctor` only checks that the file exists.
