---
name: trading-test-logger
description: Record a finished backtest or strategy test with all required fields and update PROJECT_STATUS.md (trading-research profile). Use right after any test run completes.
---

# trading-test-logger

1. Gather every field; if any is not in the files or output, write UNKNOWN: setup, direction (long/short/both), assets, timeframe, date range, spot or futures, leverage, fees and slippage included?, data source, script used, trades, win rate, profit factor, return, max drawdown, in-sample vs out-of-sample.
2. Write `results/<setup>-<assets>-<date>.md` with frontmatter (title, summary, keywords, status, updated, plus setup, assets, direction, market, leverage, fees_included, data_source, date_range) and the fields above.
3. Update PROJECT_STATUS.md: add the row to Tests, update the setup's status (PASSED/FAILED/DOUBTFUL/UNTESTED) per the brief's definitions, update the coverage matrix and Gaps.
4. Flag look-ahead, leakage, tiny samples or missing fees as DOUBTFUL reasons.
5. Run the `index-and-budget` skill.
