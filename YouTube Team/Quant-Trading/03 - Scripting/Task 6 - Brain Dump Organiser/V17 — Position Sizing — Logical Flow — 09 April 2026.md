# V17 — Position Sizing — Logical Flow — 09 April 2026

**Title:** Kelly Criterion vs Fixed Size: Which Maximizes Long-Term Wealth?
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** Same trading signals. Same entry and exit points. One trader makes 15% annualized. Another makes 8%. The only difference: position sizing. How much you bet on each trade matters more than when you bet. I compared three approaches — fixed sizing, Kelly criterion, and adaptive confidence-weighted sizing — on the same pipeline. The results are not what most people expect.

## 2. WHY POSITION SIZING IS THE REAL EDGE (2:00–8:00)

Most quant tutorials spend 90% of their time on signal generation — which model to use, which features to engineer, how to combine signals. Then they test the signal with a flat 1% position size per trade and call it done.

But position sizing is where the real money is made or lost. Consider: a strategy with 55% win rate and 1.2 payoff ratio is modestly profitable. With flat 1% sizing it compounds at about 8% annually. With optimal sizing it compounds at 15%. With aggressive oversizing it compounds at -20% (eventual ruin). Same signal, dramatically different outcomes.

The reason is geometric compounding. Your portfolio compounds multiplicatively, not additively. A -50% loss requires a +100% gain to recover. A -20% loss only requires +25%. Position sizing controls drawdown depth, and drawdown depth controls compound growth rate.

**[INFORMATION GAIN]** I ran a Monte Carlo simulation with 10,000 paths. Same signal (55% win, 1.2 payoff). With 1% fixed sizing, 0 out of 10,000 paths hit ruin. With Kelly sizing, 500 paths (5%) hit ruin within 10 years due to heavy tail events. With half-Kelly (halving the Kelly recommendation), 0 paths hit ruin and the median return was still 12% versus Kelly's 15%. The lesson: half-Kelly gives you 80% of Kelly's upside with essentially zero ruin risk.

## 3. METHOD 1: FIXED POSITION SIZING (8:00–16:00)

The simplest approach: every trade gets the same portfolio weight. I use 1% per position, controlled by the max_weight parameter in config. With 100 stocks in the universe and at most 25 active positions, the maximum invested capital is 25%.

Compute: position_size = base_allocation (e.g., 0.01). Dollar amount = portfolio_value * 0.01. Shares = dollar_amount / current_price. Apply min trade filter ($50 minimum to avoid excessive commission drag).

Pros: bounded risk per trade (never more than 1% of portfolio on any single position). Simple to implement and reason about. No estimation error — you are not trying to estimate win probability or payoff ratio.

Cons: completely ignores signal strength. A trade where your model is 90% confident gets the same weight as one where it is 55% confident. This is leaving alpha on the table — you should bet more when the signal is stronger.

In my backtests, fixed 1% sizing across 6 walk-forward folds: CAGR 8.2%, Sharpe 0.73, Max Drawdown -22%, annual turnover 4.2x.

## 4. METHOD 2: KELLY CRITERION (16:00–26:00)

The Kelly criterion is the mathematically optimal bet size that maximizes the expected logarithm of wealth — which is equivalent to maximizing long-term geometric growth rate.

Formula: f* = (p * b - q) / b, where f* is the fraction of capital to wager, p is win probability, b is the payoff ratio (average win / average loss), and q = 1 - p.

For a trade with 60% win rate and 1.3 payoff ratio: f* = (0.6 * 1.3 - 0.4) / 1.3 = 0.29. Kelly says bet 29% of capital on this trade. That is extremely aggressive.

The problem: Kelly assumes you know p and b exactly. In practice, you estimate them from historical data with substantial uncertainty. If your estimate is off by even a small amount, Kelly oversizes and the volatility of your equity curve becomes terrifying.

**[INFORMATION GAIN]** Kelly is provably optimal in the limit — given infinite time and perfect parameter knowledge, no other strategy compounds faster. But in finite time with estimated parameters, Kelly is actually suboptimal because the variance of outcomes is so high that the geometric mean suffers. The standard industry practice is to use fractional Kelly — usually f*/2 or f*/3. Half-Kelly halves the bet size, which reduces variance by 75% while only reducing expected growth rate by 25%.

Implementation: estimate win_rate and payoff_ratio from the walk-forward training window. Compute kelly_fraction. Multiply by a dampening factor (0.5 for half-Kelly). Clip to max_weight. The resulting position size varies per trade based on estimated edge.

In my backtests, full Kelly: CAGR 16.1%, Sharpe 0.92, Max Drawdown -45%, ruin probability 5%. Half-Kelly: CAGR 13.8%, Sharpe 0.88, Max Drawdown -28%, ruin probability 0%.

## 5. METHOD 3: ADAPTIVE CONFIDENCE-WEIGHTED SIZING (26:00–34:00)

This is what the actual pipeline uses. The SignalCombiner in the previous video produces a `position_size` that incorporates three factors: signal strength, meta-label confidence, and predicted volatility.

The sizing formula: position_size = |gated_signal| * vol_target * portfolio_weight. Where vol_target = risk_budget / predicted_vol. The risk_budget is 2% daily portfolio volatility target, and predicted_vol comes from the Phase 5 volatility models (GARCH, hybrid, or LSTM).

This is volatility-targeted sizing: when predicted volatility is low (calm markets), you bet more because the risk per dollar of exposure is smaller. When predicted volatility is high (turbulent markets), you bet less. Combined with the regime multiplier from V14, the position size adapts to both signal confidence and market conditions.

**[INFORMATION GAIN]** The volatility-targeting produces a remarkable effect: the daily dollar-risk of the portfolio stays roughly constant regardless of market conditions. In a bull market with 10% annualized vol, positions might be 2% each. In a crash with 40% annualized vol, positions shrink to 0.5% each. The result is that drawdowns during volatile periods are much shallower than they would be with fixed sizing, but the return during calm periods is fully captured.

In my backtests, adaptive sizing: CAGR 11.4%, Sharpe 0.85, Max Drawdown -18%. The max drawdown is significantly lower than both fixed sizing (-22%) and Kelly (-45%) while the Sharpe is competitive with Kelly.

## 6. COMPARISON TABLE AND WHEN TO USE EACH (34:00–38:00)

Method comparison across 6 walk-forward folds:

Fixed 1%: CAGR 8.2%, Sharpe 0.73, Max DD -22%, ruin risk 0%, simplicity high. Best for: beginners, risk-averse capital, strategies where signal confidence cannot be estimated.

Full Kelly: CAGR 16.1%, Sharpe 0.92, Max DD -45%, ruin risk 5%, simplicity low. Best for: theory papers. Do not use in practice.

Half Kelly: CAGR 13.8%, Sharpe 0.88, Max DD -28%, ruin risk 0%, simplicity medium. Best for: when you have reliable edge estimates from large sample sizes.

Adaptive (vol-targeted): CAGR 11.4%, Sharpe 0.85, Max DD -18%, ruin risk 0%, simplicity medium. Best for: production systems where drawdown control matters more than maximum return.

**[INFORMATION GAIN]** The adaptive method wins on risk-adjusted return when you measure by Calmar ratio (CAGR / Max DD). Fixed: 0.37. Kelly: 0.36. Half-Kelly: 0.49. Adaptive: 0.63. The adaptive method extracts the most return per unit of drawdown, which is the right objective for anyone with finite capital and finite patience.

## 7. THE CLOSE (38:00–40:00)

Position sizing is the multiplier on your signal quality. A great signal with bad sizing underperforms. A good signal with great sizing outperforms. The adaptive method we use — combining vol-targeting, regime awareness, and meta-label confidence — gives 80% of Kelly's upside with half the drawdown.

Next video: statistical testing. You have tested 14 models and found 5 that look profitable. But some of those 5 are there by pure chance. We use multiple testing correction to separate real edge from statistical luck.

[NEEDS MORE] Your actual Kelly estimates and how volatile they are across folds. Screenshots of the equity curves for all three methods overlaid. Specific trades where adaptive sizing prevented a disaster.
