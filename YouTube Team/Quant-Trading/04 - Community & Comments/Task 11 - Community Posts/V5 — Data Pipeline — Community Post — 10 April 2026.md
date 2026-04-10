# V5 — Data Pipeline — Community Post

**Date:** 10 April 2026

Yahoo Finance is lying to you.

Duplicate dates. NaN prices mid series. Adjusted close that changes retroactively after splits.

Most people never notice until their backtest breaks in ways they cannot explain. I hit all three problems building this system.

The fix: a DataValidator class that runs on every download before data touches your pipeline. Plus a caching system that detects when Yahoo reissues adjusted prices.

New video covers the full pipeline: download, validation, alignment, splitting, standardisation 👉 [INSERT PRIMARY LINK]
