# V24 — Live Backtester — Logical Flow — 09 April 2026

**Title:** Testing Your Strategy Live (Without Real Money)
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** Historical backtesting has a fatal limitation: it runs on perfect data with instant execution. In real markets, orders partially fill, slippage depends on volume, and your system must handle disconnections and data gaps gracefully. I built two tools to bridge this gap: a LiveBacktester that runs historical backtests with realistic execution models, and a PaperTrader that simulates actual live trading with orders, fills, commissions, and portfolio tracking. These are the final validation step before deploying real capital.

## 2. WHY HISTORICAL BACKTESTING IS NOT ENOUGH (2:00–8:00)

The VectorBT backtester from V13 is excellent for rapid research iteration. But it makes simplifying assumptions: orders fill instantly at the close price, there is no notion of order types (market vs limit vs stop), there is no partial fill modeling, and the cost model is a flat percentage.

In real trading: orders fill at the best available price at the time of execution, which may differ from the close price by tens of basis points depending on your order timing. Large orders may only partially fill if the order book is thin. Limit orders may not fill at all if the price moves away. And your system must mechanically generate orders, submit them, handle rejections, and track positions — there is a whole operational layer that backtesting skips.

**[INFORMATION GAIN]** The gap between backtested and live performance has a name: implementation shortfall. Studies show that the average implementation shortfall for systematic strategies is 200-400 basis points annually. If your backtested return is 12%, your live return is likely 8-10% after implementation costs. The LiveBacktester and PaperTrader aim to close this gap by simulating realistic execution before going live.

## 3. THE LIVEBACKTESTER ENGINE (8:00–18:00)

The LiveBacktester in `src/m8_backtest/engine.py` is a pure numpy/pandas backtester that does not require VectorBT as a dependency.

Constructor parameters: initial_capital (default $100,000), cost_bps (proportional cost, default 5 bps), fixed_cost (per-trade fixed cost, default $0), slippage_bps (slippage model, default 2 bps), max_position (maximum position weight, default 1.0).

The `run()` method takes price data and signal data and executes the backtest. The cost model is more detailed than VectorBT's flat fee:

cost_rate = (cost_bps + slippage_bps) * 1e-4. For each day: turnover = absolute value of change in signal. costs = turnover * cost_rate. If any trades occurred that day, add the fixed cost divided by capital.

The strategy return per day: strat_ret = signal_yesterday * daily_return_today - costs_today. Note the one-day lag: you trade on yesterday's signal because in live trading you see the signal after market close and execute the next day's open. This avoids look-ahead bias.

The output is a BacktestResult namedtuple with: equity series, daily returns, daily positions, daily turnover, daily costs, statistics dictionary, trades DataFrame (every trade with date, direction, size, price), and optional benchmark equity for comparison.

**[INFORMATION GAIN]** The BacktestResult includes a full trade log — every position change with its date, direction, size, and price. This trades DataFrame is essential for debugging: if the backtest underperforms, you can inspect individual trades to find where slippage or timing cost you. In my experience, 80% of backtest-to-live gaps come from 20% of trades — usually the largest orders in the least liquid stocks.

## 4. WALK-FORWARD BACKTESTING (18:00–24:00)

The `walk_forward()` method implements out-of-sample backtesting with periodic retraining. Parameters: signal_fn (a function that takes training data and returns signals), train_window (default 504 days = 2 years), test_window (default 63 days = 3 months), step (default 63 days).

The process: for each step, train the model on the most recent train_window days, generate signals for the next test_window days, and record the out-of-sample results. Then slide forward by step days and repeat.

The key guarantee: the model never sees test data during training. This is the most important property for trustworthy backtesting. Many researchers accidentally leak information by: computing features that look forward, normalizing data using the full period (including future), or tuning hyperparameters on the test window.

The walk-forward result stitches all out-of-sample periods together into a single continuous equity curve. This curve has ONE look at every data point — the same as live trading would.

## 5. THE PAPER TRADING ENGINE (24:00–34:00)

The PaperTrader in `src/m8_trading/paper_trader.py` simulates actual live trading with explicit order handling.

The order model: orders are created as Order objects with ticker, side (buy/sell), order_type (market, limit, stop), quantity, and optional limit_price/stop_price. This mirrors the interface of real broker APIs.

The execution model: when `submit_order()` receives an order and a market price, it applies slippage to compute the fill price. For buy orders: fill_price = market_price + slippage. For sell orders: fill_price = market_price - slippage. Where slippage = market_price * slippage_bps * 1e-4. Commission is calculated per-share with a minimum floor: commission = max(quantity * commission_per_share, commission_min). Default: $0.005 per share with $1.00 minimum.

Position limits: before executing, the PaperTrader checks that the resulting position does not exceed max_position_pct (default 20%) of total portfolio equity. If it would, the order is partially filled up to the limit.

**[INFORMATION GAIN]** The commission model seems trivial but it reveals a counterintuitive edge: per-share commissions create a hidden bias against low-priced stocks. At $0.005 per share, trading 500 shares of a $200 stock costs $2.50 on a $100,000 notional — 0.25 bps. Trading 5000 shares of a $20 stock costs $25 on the same $100,000 notional — 2.5 bps. That is a 10x cost difference for the same dollar amount. This means your effective cost model varies by price level, and low-priced stocks are structurally more expensive to trade.

The `run_simulation()` method automates the trading loop for single-asset paper trading: iterate over dates, convert signal to target position in shares, compute the trade needed to reach target, submit orders, process fills, mark portfolio to market, record everything.

The `run_multi_asset()` method extends this to multiple assets simultaneously. It takes a DataFrame of target weights (rows = dates, columns = tickers) and executes rebalancing across all assets each period.

## 6. PORTFOLIO TRACKING AND REPORTING (34:00–38:00)

The Portfolio class in `src/m8_trading/portfolio.py` tracks cash, positions, and equity through time.

Each position tracks: ticker, quantity (positive for long, negative for short), average cost (volume-weighted entry price), realized PnL (from closed trades), and unrealized PnL (mark-to-market on open positions).

The `equity()` method computes total portfolio value: cash + sum of (quantity * current price) for all open positions. The `mark_to_market()` method updates unrealized PnL daily and records the equity snapshot.

The trade log records every fill with: timestamp, ticker, side, quantity, fill price, commission, slippage, and pre-trade and post-trade portfolio equity. This is the complete audit trail.

The `plot_equity()` method generates a 2-panel chart: equity curve and drawdown, optionally overlaid with a benchmark. This visual check bridges the gap between the backtester (which uses aggregate statistics) and the paper trader (which shows the actual simulated trading experience).

**[INFORMATION GAIN]** Comparing the LiveBacktester result to the PaperTrader result on the same data is a validation test. If the LiveBacktester shows 12% return and the PaperTrader shows 10.5%, the 1.5% gap is your implementation shortfall estimate. If the gap exceeds 3%, there is likely a bug in order execution, timing, or cost modeling that needs investigation before going live.

## 7. THE CLOSE (38:00–40:00)

The LiveBacktester and PaperTrader close the gap between idealized backtesting and real-world execution. The LiveBacktester adds realistic costs and walk-forward discipline. The PaperTrader adds explicit order handling, position tracking, and the operational mechanics of live trading. Together, they give you confidence that the equity curve in your tearsheet will translate to a real P&L statement.

Next and final video: the deployment checklist. 30 points across code quality, model validation, risk controls, operations, compliance, and capital ramp — everything between paper trading and live capital deployment.

[NEEDS MORE] Your actual paper trading results compared to the backtest. Screenshots of the trade log. A specific case where paper trading revealed a bug before live deployment.
