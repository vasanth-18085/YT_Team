# V2 — Backtesting Lies — Community Post

**Date:** 10 April 2026

Your backtest is lying to you.

Not maybe. Almost certainly.

I built 14 forecasting models. Got a Sharpe of 1.14 on test data. Felt brilliant. Then I tested properly with purged walk forward validation. The real number was 0.72.

Three specific types of leakage were inflating my results. Shuffled splits. Label overlap from triple barrier horizons. Autocorrelation at fold boundaries.

Standard sklearn time series splits do not catch any of these.

New video breaks down all three lies and shows the exact fix 👉 [INSERT PRIMARY LINK]
