---
title: Trading research profile
summary: Folder skeleton, setup/test status tables, PASSED/FAILED/DOUBTFUL definitions and never-do rules for trading course and strategy research.
keywords: [trading, backtest, setups, courses, ict, ml, research]
status: confirmed
updated: 2026-10-17
extends: data-research
---

# Profile: trading-research

## Folder skeleton
knowledge/ (course notes) | data/ (source docs, download scripts, not raw data) | scripts/ | results/ (one report per test)
| findings/ (confirmed conclusions) | ml/ (features, labels, split, leakage risks, OOS results) | tools/

## Extra frontmatter
setup, assets, timeframe, direction (long/short/both), market (spot/futures), leverage, fees_included, data_source, date_range

## PROJECT_STATUS.md tables
- Setups: name | source lesson | status PASSED/FAILED/DOUBTFUL/UNTESTED | evidence link
- Tests: setup | direction | assets | timeframe | date range | spot/futures | leverage | fees+slippage | script | result | trades, win%, PF, return, max DD
- Assets x setups coverage matrix
- Data sources: provider | assets | timeframe | range | quirks (e.g. bid/ask swaps, DST)
- Gaps: untested setup x direction x asset x spot/futures x leverage, ranked

## Status definitions (set exact numbers in PROJECT_BRIEF.md)
Default: PASSED = positive expectancy after fees, enough trades, holds out-of-sample. FAILED = clearly negative.
DOUBTFUL = small sample, no OOS, no fees, or suspected look-ahead. UNTESTED = not run.

## Default phases
Used by `plan.py init` and the bootstrap interview when the tracking tier is `plan` (kit/PLAN_SCHEMA.md). One phase per line; add steps after a colon, separated by semicolons. Edit freely; ids are generated.
- Research
- Backtest
- Paper
- Live

## Never do
Live trading or orders; report results without fees/slippage stated; mix in-sample and out-of-sample silently; delete result files.

## Wrap-up additions
List every test run this thread with all table fields; flag look-ahead/leakage risks.

## VS Code
### Extensions
- ms-python.python: Python language support
- ms-toolsai.jupyter: notebooks for research
- charliermarsh.ruff: lint and format
### Settings
- `"jupyter.askForKernelRestart": false`
