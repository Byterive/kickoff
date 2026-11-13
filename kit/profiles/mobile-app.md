---
title: Mobile app profile
summary: Folder skeleton, status tables, budgets and never-do rules for Android and iOS app projects.
keywords: [android, ios, mobile, app store, play store, release]
status: confirmed
updated: 2026-10-17
---

# Profile: mobile-app

## Folder skeleton
docs/product (requirements, user flows) | docs/screens (one note per screen) | docs/architecture | docs/api
| docs/store (listing text, screenshots list, privacy/compliance) | docs/release (signing, checklist, versions) | docs/decisions | tools/

## Extra frontmatter
platform (android/ios/both), screen, min_os, app_version, build_number

## PROJECT_STATUS.md tables
- Features/screens: name | platform | status (IDEA/WIP/DONE) | tests | doc link
- Device matrix: device/OS version | build | result | issues
- Releases: version | build | platform | store status (draft/review/live) | date
- Store compliance checklist: item | status
- Gaps and next steps

## Budgets
Code: max 400 lines per file (Kotlin/Swift/Java). Docs default.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Design
- Build
- Beta
- Store release
- Post-launch

## Never do
Commit keystores, provisioning profiles, certificates or API keys (document location only); change bundle/package id
or signing config; submit to a store; bump version numbers without approval.

## DONE means
Works on minimum and latest supported OS on real device or emulator, documented, no new crashes.

## Wrap-up additions
Record OS/devices tested, SDK/dependency versions changed, permissions added (and why).

## VS Code
### Extensions
- editorconfig.editorconfig: shared formatting rules
- eamodio.gitlens: history and blame
### Settings
- `"files.insertFinalNewline": true`
### Notes
Add the platform extension (Kotlin, Swift or Flutter) once the stack is chosen.

