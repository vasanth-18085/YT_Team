# V13 — VectorBT Backtesting — Refined Script

**Title:** VectorBT: Testing 100 Stocks, 6 Folds, 50 Features in 2 Minutes
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

[INFORMATION GAIN] Traditional loop-based backtesting on 100 stocks across 6 walk-forward folds takes 10 to 20 minutes per run. That sounds acceptable until you realise that a proper hyperparameter search means running hundreds of variations. At 15 minutes each, you can maybe do 5 experiments per day. VectorBT does the same backtest in under 2 minutes because it never loops over individual trades. I will walk you through the exact setup I use, how to add realistic transaction costs, and which metrics actually matter for evaluating strategy quality.

---

## SECTION 2 — WHY VECTORISATION CHANGES EVERYTHING (2:00–8:00)

The standard backtesting approach: loop over each day, check your signals, simulate a trade, update portfolio state, advance to the next day. For 100 stocks over 10 years that is 2,500 dates per stock, 250,000 iterations total, with position tracking logic inside each iteration. Even fast Python code takes seconds per run.

VectorBT's approach: represent the entire price series and signal series as NumPy arrays. Apply operations across the entire array simultaneously using vectorised NumPy and Numba-compiled operations.

The technical difference: instead of `for day in trading_days: execute_trade(day)` you write `portfolio = vbt.Portfolio.from_signals(close, signals)` and the entire portfolio simulation happens in one GPU-friendly matrix operation.

[INFORMATION GAIN] The 50x speed improvement is not just about convenience — it changes what is computationally feasible to research. At 15 minutes per backtest, you can test maybe 20 hyperparameter combinations in a day. At 2 minutes, you can test 150. That is the difference between an afternoon's research and a week's research, run in one session. For a system with as many moving parts as this one — 14 forecasting models, 7 fusion architectures, 4 portfolio methods — the ability to sweep parameter spaces quickly is essential. VectorBT is what makes that affordable.

---

## SECTION 3 — BASIC VECTORBT SETUP (8:00–18:00)

```python
import vectorbt as vbt
import numpy as np
import pandas as pd

# Step 1: Load price data
close = vbt.YFData.download(
    ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
    start='2015-01-01',
    end='2024-12-31'
).get('Close')
# close shape: (2,500 trading days, 4 stocks)

# Step 2: Your fusion model generates signals
# True = long signal, False = flat or exit
entry_signals = (fusion_predictions > 0)   # Boolean array, same shape as close
exit_signals  = (fusion_predictions <= 0)  # Exit when signal reverses

# Step 3: Create Portfolio object
pf = vbt.Portfolio.from_signals(
    close,
    entries=entry_signals,
    exits=exit_signals,
    init_cash=100_000,
    fees=0.001,         # 10 bps commission per trade
    slippage=0.0005,    # 5 bps slippage per trade
    freq='1D'           # Daily frequency
)
```

[INFORMATION GAIN] `vbt.Portfolio.from_signals` is the core API. The `entries` and `exits` are boolean arrays with the same shape as `close`. Every True in `entries` triggers a buy; every True in `exits` triggers a sell. The portfolio handles position tracking, cash management, and all cost accounting internally. You do not write any of that logic yourself.

### Getting results

```python
# All metrics in one call
stats = pf.stats()
print(stats)

# Output keys include:
# Total Return, Annual Return, Annual Volatility
# Sharpe Ratio, Sortino Ratio, Calmar Ratio
# Max Drawdown, Max Drawdown Duration
# Win Rate, Best Trade, Worst Trade
# Num Trades, Avg Trade Return
# Total Commission Paid, Total Slippage Paid
```

The `pf.stats()` call is vectorised across all stocks simultaneously. You get one stats object per stock, or you can aggregate across the universe with `pf.stats(group_by=True)`.

---

## SECTION 4 — WALK-FORWARD BACKTESTING LOOP (18:00–28:00)

VectorBT handles execution but does not build the walk-forward CV structure automatically. That wrapper comes from the `PurgedWalkForwardCV` from Video 2.

```python
all_fold_results = []

for fold_idx in range(6):
    # Get train/test split dates from purged walk-forward CV
    train_dates, test_dates = walk_forward_cv.get_fold(fold_idx)

    # Train pipeline on training window
    pipeline.fit(aligned_data.loc[train_dates])

    # Generate signals on test window
    test_signals = pipeline.predict(aligned_data.loc[test_dates])
    test_close   = close.loc[test_dates]

    # Run VectorBT on this fold
    pf_fold = vbt.Portfolio.from_signals(
        test_close,
        entries=(test_signals > 0),
        exits=(test_signals <= 0),
        init_cash=100_000,
        fees=0.001,
        slippage=0.0005,
        freq='1D'
    )

    fold_stats = pf_fold.stats(group_by=True)   # Aggregate across stocks
    all_fold_results.append({
        'fold': fold_idx,
        'train_start': str(train_dates[0].date()),
        'test_start':  str(test_dates[0].date()),
        'test_end':    str(test_dates[-1].date()),
        'sharpe':      fold_stats['Sharpe Ratio'],
        'max_dd':      fold_stats['Max Drawdown'],
        'ann_return':  fold_stats['Annual Return'],
        'n_trades':    fold_stats['Total Trades'],
    })

results_df = pd.DataFrame(all_fold_results)
print(f"Mean Sharpe: {results_df['sharpe'].mean():.2f}")
print(f"Sharpe std:  {results_df['sharpe'].std():.2f}")
print(f"Min Sharpe:  {results_df['sharpe'].min():.2f}")
```

[INFORMATION GAIN] The standard deviation of Sharpe across folds is as important as the mean. A system with mean Sharpe 1.2 and std 0.9 has some excellent folds and some terrible ones — its performance is unstable and likely overfitted to the specific market regimes that happened to be in the good folds. A system with mean Sharpe 0.85 and std 0.15 is consistent across different market environments, which means its signal is genuine. Consistency is what predicts live performance. Variance in fold Sharpe predicts live disappointment.

---

## SECTION 5 — TRANSACTION COSTS IN DETAIL (28:00–33:00)

```python
# Three cost parameters
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    fees=0.001,       # 10 bps commission — Interactive Brokers standard for US equities
    slippage=0.0005,  # 5 bps slippage — typical for mid-cap liquid names
    freq='1D'
)
```

The performance impact on this system:

```
Without transaction costs: Sharpe 0.85
With fees + slippage:       Sharpe 0.72  (-15%)
Number of trades per year:  400 (after meta-labeling filter)
```

[INFORMATION GAIN] The math behind the 15% Sharpe reduction: with 400 trades per year on a $100,000 portfolio, an average position size of $1,000, and a round-trip cost of 15 bps (10 bps commission + 5 bps slippage), total annual cost is approximately 400 × $1,000 × 0.0015 = $600. On a $100,000 portfolio that is 0.6% of capital per year. If your gross returns are 8%, your net after costs is 7.4% — the Sharpe impact depends on how that 0.6% maps to the volatility-normalised metric.

The meta-labeling filter in Video 8 reducing trades from 1,000 to 400 per year cuts transaction costs by 60% in addition to improving win rate. This is the second reason meta-labeling improves net performance beyond its direct accuracy benefit.

---

## SECTION 6 — RISK METRICS THAT MATTER (33:00–38:00)

```python
stats = pf.stats(group_by=True)

# The five you actually care about:
sharpe     = stats['Sharpe Ratio']        # Return / Vol — quality of risk-adjusted return
sortino    = stats['Sortino Ratio']       # Return / Downside-Vol — penalises only bad vol
calmar     = stats['Calmar Ratio']        # Annual Return / Max Drawdown
max_dd     = stats['Max Drawdown']        # Single worst peak-to-trough loss
win_rate   = stats['Win Rate']            # Fraction of trades that were profitable

# Additional diagnostic
total_trades       = stats['Total Trades']
avg_trade_return   = stats['Avg Trade Return']
max_dd_duration    = stats['Max Drawdown Duration']
total_commissions  = stats['Total Commission']
```

[INFORMATION GAIN] Calmar ratio is the most practical metric for real-money trading. It directly answers: "How much drawdown do I need to endure per unit of annual return?" A Calmar of 0.5 means a 20% annual return comes with a 40% historical max drawdown. That is a very different psychological and operational challenge than a 10% return with a 5% max drawdown (Calmar 2.0). Sharpe tells you about daily-level noise. Calmar tells you whether you can stomach the ride.

Max drawdown duration is often overlooked but matters as much as drawdown magnitude. A -15% drawdown that recovers in 2 weeks is operationally very different from a -15% drawdown that lasts 18 months. Long drawdown durations destroy investor patience and force strategy abandonment at exactly the wrong time.

---

## SECTION 7 — THE CLOSE (38:00–40:00)

VectorBT removes the computation bottleneck from your research cycle. Six walk-forward folds across 100 stocks in 2 minutes means you can iterate on model parameters, signal thresholds, and portfolio rules at a pace that was previously impossible with loop-based tools.

The key discipline: report fold-level consistency, not just mean Sharpe. Mean Sharpe is what optimistic presenters show; Sharpe standard deviation is what honest researchers show.

Next video: the trading system works on average, but markets are not average. Regime detection — automatically identifying bull, bear, and crash environments in real time and adapting position sizing accordingly.

---

## Information Gain Score

**Score: 6/10**

The fold-consistency argument over mean Sharpe, the Calmar-as-primary-metric reasoning, the meta-labeling transaction cost connection, and the specific vectorisation speed numbers are practical additions.

**Before filming, add:**
1. Your actual fold-by-fold Sharpe table from your runs with the series of videos
2. The before/after costs numbers from your specific universe
3. A screen recording of VectorBT portfolio.stats() output — it is visually compact and impressive
