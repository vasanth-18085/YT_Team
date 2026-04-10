# V16 — Transaction Costs — Logical Flow — 09 April 2026

**Title:** 10 bps Matters: How Commissions + Slippage Kill Backtests
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** On paper my strategy had a Sharpe of 1.2. After adding realistic transaction costs it dropped to 0.6. Half the edge was eaten by friction that most backtests completely ignore. Every trade has three invisible costs: commissions, slippage, and market impact. I built a full TransactionCostModel that quantifies each one, a SlippageModel based on the square-root law, and a MarketImpactModel using the Almgren-Chriss framework. Then I ran a cost sensitivity sweep to find the exact break-even point where my strategy stops being profitable.

## 2. WHY COSTS KILL MORE STRATEGIES THAN BAD SIGNALS (2:00–8:00)

Most YouTube tutorials and academic papers backtest with zero costs. They show a beautiful equity curve and declare the strategy works. Then someone tries to trade it live and the returns evaporate. This is not because the strategy was wrong — it is because the cost assumptions were wrong.

The math is brutal. If your strategy turns over the entire portfolio once per day (which is common for short-horizon momentum strategies), and each roundtrip costs 15 bps (10 bps commission + 5 bps slippage), the annual cost drag is: 15 bps * 252 trading days = 3,780 bps = 37.8% per year. If your gross return was 15%, your net return is negative. The strategy does not just underperform — it actually loses money.

**[INFORMATION GAIN]** The single most important number in a quant strategy is not the Sharpe ratio. It is the ratio of gross edge to cost drag. If your gross annualized return is 12% and your annual cost drag is 4%, your cost efficiency is 3:1 which is healthy. If the ratio drops below 2:1, you are in danger territory. Below 1:1, you are guaranteed to lose money over time.

## 3. THE THREE COST LAYERS (8:00–20:00)

### Layer 1: Commission (the visible cost)

The TransactionCostModel in `src/m7_execution/costs.py` supports three fee schedules simultaneously:

Fixed per trade: a flat dollar amount per order regardless of size. Common with full-service brokers. Rare now but still exists.

Proportional: a percentage of the trade notional (the dollar value of shares traded). Default: 5 bps (0.05%). Interactive Brokers charges 1-5 bps depending on volume. Alpaca charges 0 commission but recaptures it through wider spreads.

Per share: a fixed cost per share traded. Interactive Brokers tiered pricing charges $0.005 per share. On a $200 stock, that is 0.25 bps. On a $20 stock, that is 2.5 bps — 10x more expensive.

The formula: total_cost = fixed + proportional_bps * 1e-4 * |notional| + per_share * |n_shares|. This is clamped to a minimum cost floor (some brokers charge at least $1 per order).

### Layer 2: Slippage (the hidden cost)

Slippage is the difference between the price you see on screen and the price you actually get when the order fills. It is caused by the bid-ask spread plus the time delay between decision and execution.

My SlippageModel uses the square-root law: slippage = k * sigma * sqrt(order_size / ADV). Where k is the slippage coefficient (default 0.1), sigma is daily volatility, and ADV is average daily volume. The square root captures the empirical observation that slippage increases sub-linearly with order size — buying 100 shares barely moves the price, buying 10,000 shares pushes it up noticeably.

**[INFORMATION GAIN]** The key insight is that slippage depends on your order size relative to the market's daily volume (the participation rate). A $50,000 order in Apple (ADV of $10 billion) has essentially zero slippage. A $50,000 order in a small-cap stock with $2 million ADV has significant slippage because you are 2.5% of the daily volume. This is why universe selection matters: trading liquid large-caps has a structural cost advantage.

### Layer 3: Market Impact (the permanent cost)

Market impact is the permanent price change caused by your trade. Unlike slippage (which is temporary), market impact does not reverse. You buy shares, the price moves up permanently because the market infers from your buying that you have information.

The Almgren-Chriss MarketImpactModel decomposes impact into:

Temporary impact: gamma * sigma * (v/V)^delta. This is the immediate price displacement from your order flow. delta = 0.5 (the square-root law again). This decays after your order is filled.

Permanent impact: lambda * sigma * (v/V). This is the lasting price change. It is linear in participation rate because the informational content of your trade scales linearly with its relative size.

For a $100,000 order in a stock with $5M ADV and 2% daily volatility: participation rate = 2%. Temporary impact ≈ 0.1 * 0.02 * sqrt(0.02) = 2.8 bps. Permanent impact ≈ 0.1 * 0.02 * 0.02 = 0.4 bps. Total: 3.2 bps. Seems small, but multiply by 252 daily trades and it compounds.

## 4. FILL SIMULATION AND CAPACITY ESTIMATION (20:00–28:00)

The FillSimulator models what happens when you cannot execute your entire order at once. Real markets have finite liquidity — you cannot buy $1 million of a stock in one tick if the book only has $200,000 of offers at your price.

Parameters: max_participation = 0.10 (never execute more than 10% of ADV in a single session). If your target order is 15% of ADV, the fill simulator breaks it into two parts: 10% today, 5% tomorrow. Each partial fill incurs slippage separately.

**[INFORMATION GAIN]** Strategy capacity — the maximum capital a strategy can deploy before its own trading destroys its edge — is directly computable from the market impact model. If adding $1M of capital increases cost drag by 50 bps annually. and your gross edge is 500 bps, the strategy can handle about $10M before costs eat the edge. Most short-horizon strategies have $5-50M capacity. Long-horizon strategies can scale much further because they trade less frequently.

## 5. COST SENSITIVITY SWEEP (28:00–34:00)

The TransactionCostModel's `sweep()` method tests the strategy across a range of cost assumptions from 1 bps to 20 bps in 1 bps increments. For each cost level, it recomputes net returns, net Sharpe, and Sharpe erosion.

The output is a DataFrame showing: at 5 bps total cost, net Sharpe = 0.95. At 10 bps, net Sharpe = 0.72. At 15 bps, net Sharpe = 0.48. At 20 bps, net Sharpe = 0.24. At 35 bps, net Sharpe turns negative. This 35 bps number is the strategy's cost ceiling — above it, you lose money.

**[INFORMATION GAIN]** The cost sweep reveals that the relationship between cost and Sharpe erosion is linear for this strategy. Every additional 5 bps of cost reduces Sharpe by approximately 0.23. This linearity means you can estimate the impact of any broker's fee structure instantly. Switching from Broker A (12 bps) to Broker B (8 bps) saves exactly 4 bps in costs which translates to approximately 0.18 Sharpe improvement. This is a measurable, auditable edge.

## 6. COST REDUCTION STRATEGIES (34:00–38:00)

Strategy 1: Reduce trading frequency. Moving from daily rebalancing to weekly rebalancing cuts turnover by 80%. The Sharpe ratio drops slightly (from 0.72 to 0.65) but the cost drag drops much more.

Strategy 2: Batch orders. Instead of executing 100 individual stock orders, compute target weights and execute a single rebalance. This reduces fixed costs from 100 * $1 minimum to 1 * $1.

Strategy 3: Use limit orders instead of market orders. Market orders guarantee fill but pay the full bid-ask spread. Limit orders may not fill immediately but you can capture the spread instead of paying it. The trade-off: some signals expire before the limit order fills.

Strategy 4: Optimize position changes. Only trade when the position change exceeds a minimum threshold (I use $50 notional). This eliminates tiny position adjustments that cost more in commissions than they contribute to returns.

## 7. THE CLOSE (38:00–40:00)

Transaction costs are not an afterthought — they are a permanent drag that determines whether a profitable backtest translates to profitable live trading. The three-layer cost model (commission + slippage + market impact) gives an honest picture. The cost sensitivity sweep tells you exactly where your strategy breaks. And capacity estimation tells you how much capital it can absorb.

Next video: position sizing. We have signals, we have costs, we have regime awareness. Now we decide exactly how many dollars to put on each trade. Kelly criterion versus fixed sizing versus adaptive — which maximizes long-term wealth?

[NEEDS MORE] Your actual cost numbers from Interactive Brokers or Alpaca. A real before/after cost comparison on your live pipeline. Specific stocks where slippage was worse than expected.
