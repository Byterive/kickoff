---
title: Data research profile
summary: Shared folder skeleton, status tables, never-do rules and VS Code setup for data analysis and research projects; trading-research extends it.
keywords: [data, research, analysis, notebooks, experiments, family]
status: confirmed
updated: 2026-11-11
---

# Profile: data-research

Main profile of the data-research family. `trading-research` extends it.

## Folder skeleton
data/ (source notes and download scripts, not raw data) | notebooks/ | scripts/ | results/ (one report per experiment) | findings/ (confirmed conclusions) | docs/ | tools/

## Extra frontmatter
experiment, dataset, question, method, date_range, source (observed/configured/inferred/unknown)

## PROJECT_STATUS.md tables
- Questions: question | status (OPEN/ANSWERED/DROPPED) | evidence link
- Datasets: name | provider | range | how obtained | quirks
- Experiments: id | question | method | parameters | result | sample size | confidence
- Gaps: untested question x dataset x method, ranked

## Budgets
Docs: default budgets. Code: max 400 lines per file.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Question and data contract
- Collect and clean
- Analyse
- Report

## Never do
- Commit raw data or credentials; commit scripts and reports instead.
- Mix training and held-out data silently.
- Report a result without its parameters, sample size and data source.
- Show an inferred figure as certain: label observed, configured, inferred or unknown.

## DONE means
The question is answered with the method, data, parameters and sample size stated, the result is reproducible from the scripts, and limits are written down.

## Wrap-up additions
List every experiment run this thread with parameters, sample size and result; flag leakage or small-sample risks.

## VS Code
### Extensions
- ms-python.python: Python language support
- ms-toolsai.jupyter: notebooks
- charliermarsh.ruff: lint and format
### Settings
- `"jupyter.askForKernelRestart": false`
