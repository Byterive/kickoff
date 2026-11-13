---
title: Unity game profile
summary: Folder skeleton, status tables, budgets and never-do rules for Unity game projects.
keywords: [unity, game, c#, scenes, prefabs, builds]
status: confirmed
updated: 2026-10-17
---

# Profile: unity

## Folder skeleton (docs live beside, not inside, Assets/)
docs/design (pitch, mechanics) | docs/systems (one note per gameplay system) | docs/scenes-prefabs (what each does)
| docs/playtests | docs/builds (per platform) | docs/decisions | tools/ | Assets/ (engine-managed, unchanged)

## Extra frontmatter
system, scene, platform (pc/android/ios/webgl), unity_version, depends_on

## PROJECT_STATUS.md tables
- Features: feature | system | status (IDEA/WIP/DONE/CUT) | owner | evidence/link
- Bugs: id | symptom | repro | severity | status
- Builds: platform | version | date | result | known issues
- Playtests: date | build | tester | findings link
- Gaps and next steps

## Budgets / exclusions
skip: Library, Temp, Logs, obj, Packages, UserSettings, Assets/ThirdParty. Never index .meta, .unity, .prefab, binaries.
Code: max 400 lines per C# file (split MonoBehaviours into components).

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Prototype
- Vertical slice
- Alpha
- Beta
- Release

## Never do
Edit .meta/.unity/.prefab YAML by hand without asking; delete or rename assets (breaks GUID refs);
commit Library/ or keystores; upgrade the Unity version or packages without asking.

## DONE means
Feature works in a build on the target platform, playtested, documented in docs/systems.

## Wrap-up additions
Record Unity version, packages added, scenes touched, and the platform tested.

## VS Code
### Extensions
- ms-dotnettools.csdevkit: C# language support (unverified id)
- visualstudiotoolsforunity.vstuc: Unity debugging and integration (unverified id)
### Settings
- `"files.exclude"`: hide Library, Temp and Logs

## Companion plugins
- unity-game-kit: Unity setup, Android build, checks, art pipeline | when: new or existing Unity game | command: `/game-setup`, then `/game-doctor`
- unity: Unity's official skills | when: Unity coding help | command: skills load by topic

Loop guard: `/game-setup` calls `/kickoff:bootstrap` with profile unity and bootstrap may offer `/game-setup`; whichever runs first runs once, and the other is skipped when PROJECT_STATUS.md or gamekit.json already exists.
