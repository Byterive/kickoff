---
title: Unity brief example
summary: Filled example PROJECT_BRIEF for a small 2D Unity mobile game.
keywords: [example, unity, brief]
status: draft
updated: 2026-10-17
---

# PROJECT_BRIEF: "Tiny Farm" (example)

## 1. Goal
Ship a 2D idle-farming game to Android. Done = playable 20-minute loop, 60 fps on a mid-range phone, on Play Store internal track.

## 2. Profile
unity

## 3. Background and sources
Design doc: docs/design/pitch.md (to be written). Art pack in Assets/ThirdParty/FarmPack (licensed, do not edit).

## 4. Environment and tools
Windows 11, Unity 6 LTS (URP 2D), Android target API 34, Git. Test device: Pixel 6.

## 5. Rules and constraints
Max APK 100 MB. No ads in v1. C# files under 400 lines.

## 6. Definition of status words
DONE = works in an Android build on Pixel 6, playtested for 10 minutes, documented in docs/systems.

## 7. Already done / known problems
Prototype: planting and harvesting work in editor. Save system missing. Touch input lags on device.

## 8. Next steps wanted
1) Save/load 2) Touch input fix 3) Shop UI 4) First Android build.

## 9. Never do
Edit .meta/scene YAML by hand, delete assets, upgrade Unity or packages, commit Library/.
