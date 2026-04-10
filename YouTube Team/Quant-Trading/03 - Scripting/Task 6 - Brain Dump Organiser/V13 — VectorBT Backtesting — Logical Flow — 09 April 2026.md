# V13 — VectorBT Backtesting — Logical Flow — 09 April 2026

**Title:** VectorBT: Testing 100 Stocks, 6 Folds, 50 Features in 2 Minutes
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** Traditional backtesting is slow — simulate trade by trade, compute metrics, retry. VectorBT does it differently with vectorized operations, making it 50x faster. I backtest 100 stocks across 6 walk-forward folds in 2 minutes. That is 610+ scenarios in the time it takes to brew coffee. The whole point of Phase 6 in this system is to take every upstream signal — forecasts, meta-labels, sentiment, volatility — and test the final combined strategy against real historical data with proper costs and slippage. VectorBT is the engine that makes this iteration speed possible.

## 2. WHY MOST BACKTESTING IS BROKEN (2:00–8:00)

The typical backtesting approach is a Python for loop iterating day by day across 2500 trading days. For each day you check the signal, decide whether to enter or exit, update the portfolio, calculate PnL. That loop-based approach for 100 stocks across 6 folds is 1.5 million iterations with inner logic per iteration — takes 10+ seconds easily, often minutes.

But the deeper problem is not speed. It is that slow backtesting means fewer experiments. If each backtest takes 10 minutes you run maybe 6 per hour. If each takes 2 seconds you run 1800 per hour. The number of experiments you can run in a research session directly determines how many hypotheses you test, and that determines how quickly you find what works.

**[INFORMATION GAIN]** The research velocity problem: I found that most of my real insights came from experiment 40 or 50, not experiment 1 or 2. If your backtester is slow, you never get to experiment 40. You publish your second or third idea and call it done. Speed is not a luxury — it determines the quality of your final strategy.

VectorBT solves this with NumPy array operations. Instead of a loop over 2500 days, you perform a single matrix operation on all 2500 days simultaneously. Same mathematical result, 50x faster.

## 3. VECTORBT ARCHITECTURE AND API (8:00–18:00)

The core idea: represent everything as NumPy arrays where rows are dates and columns are stocks.

Close prices shape: (2500 dates, 100 stocks). Signals shape: (2500, 100). Portfolio weights shape: (2500, 100). One vectorized multiplication gives you daily PnL for every stock every day simultaneously.

Step 1 — Load OHLCV data. VectorBT wraps yfinance for downloading but we use our own data pipeline from Phase 0. The key is getting a clean DataFrame with DatetimeIndex rows and ticker columns.

Step 2 — Generate signals. Our SignalCombiner from the previous video produces a final_signal column per stock per day. These are position weights ranging from -0.25 to +0.25 (short to long, capped at max_weight).

Step 3 — Create the Portfolio object. VectorBT's `Portfolio.from_orders()` takes close prices and order sizes. The orders are the daily change in target shares — computed as `(|signal| * initial_capital / close)`. Transaction fees are applied per order.

Step 4 — Extract results. The portfolio object gives instant access to: daily returns, cumulative equity curve, Sharpe ratio, Sortino ratio, Calmar ratio, max drawdown, win rate, number of trades, average trade return — all computed from the vectorized arrays.

**[INFORMATION GAIN]** I use `from_orders()` instead of `from_signals()` because `from_orders()` lets me control exact share quantities and apply position sizing from the SignalCombiner. The `from_signals()` method only supports binary entry/exit signals which is too simplistic for a real system with varying position sizes.

## 4. WALK-FORWARD BACKTESTING (18:00–28:00)

Single-period backtesting is dangerous because it tests on one specific window and you do not know if the strategy works across different market regimes. Walk-forward backtesting solves this by splitting the data into multiple overlapping train/test periods.

My setup: 6 folds. Each fold has approximately 504 days of training data (2 years) and 126 days of test data (6 months). The folds march forward in time so that each test window becomes part of the next training window.

For each fold: train the full pipeline (forecasting models, meta-labeler, fusion model). Generate signals on the test window. Run VectorBT backtest on that test window. Collect Sharpe ratio, max drawdown, turnover, and cost drag per fold. The final evaluation is the average and standard deviation of Sharpe across all 6 folds. A high average with low standard deviation is what you want — it means the strategy is robust, not lucky on one window.

**[INFORMATION GAIN]** I also run a simple backtest variant called `run_simple()` that uses pure NumPy without the VectorBT dependency. The formula is: `port_ret = signal * daily_ret - turnover * cost_rate`. This is useful for quick parameter sweeps where the full VectorBT overhead is unnecessary. I use VectorBT for publication-quality results and the simple variant for rapid iteration.

## 5. ADDING TRANSACTION COSTS AND SLIPPAGE (28:00–34:00)

Costs define the barrier between a backtest fantasy and a real strategy. Three cost layers:

Commission: I use 10 bps (0.1%) per trade, which is realistic for Interactive Brokers or Alpaca on moderate volume. VectorBT applies this as the `fees` parameter.

Slippage: The difference between the price you see and the price you actually get. I use 5 bps (0.05%). For liquid S&P 100 stocks this is conservative. For small caps it would be higher.

The impact on results is sobering: before costs, the full pipeline across 6 folds gives an average Sharpe of 0.85. After costs (10 bps commission + 5 bps slippage = 15 bps per roundtrip), the average Sharpe drops to 0.72 — a 15% reduction. For a strategy that trades daily, costs compound relentlessly.

**[INFORMATION GAIN]** I built a cost sensitivity sweep that tests the strategy across 1 to 20 bps in 1 bps increments. This produces a Sharpe erosion curve — you can see exactly at what cost level your strategy becomes unprofitable. For this pipeline, the breakeven point is around 35 bps roundtrip. Above that, the edge is gone.

## 6. MODULE ABLATION — MEASURING EACH MODULE'S VALUE (34:00–38:00)

VectorBT's `module_ablation()` method runs the strategy with different module combinations to isolate each module's marginal contribution.

Variant 1: M1 only (forecast signal, no gates). Variant 2: M1 + M2 (add meta-label gate). Variant 3: M1 + M2 + M3 (add sentiment overlay). Variant 4: Full pipeline (all modules including volatility-targeted sizing).

Each variant is backtested on the same data and the marginal Sharpe improvement from each added module is reported. In my runs, the meta-label gate alone adds 0.15 to Sharpe by filtering out low-confidence trades. Sentiment overlay adds 0.03 — small but consistent. Volatility-targeted sizing adds 0.08 by reducing position size during high-vol regimes.

## 7. THE CLOSE (38:00–40:00)

VectorBT turns backtesting from a bottleneck into a research accelerator. The key numbers: 2 minutes for 610 scenarios, 15% Sharpe erosion from realistic costs, and a clear module-by-module contribution map.

Next video: regime detection. Even with a fast backtester, your strategy behaves differently in bull, bear, and crash markets. We build an HMM model that detects market state and adapts position sizing in real time.

[NEEDS MORE] Your own timing data, screenshots of actual VectorBT output, and specific parameter combinations that surprised you.
