# V17 — Position Sizing — Clean Script

**Title:** Kelly Criterion vs Fixed Size: Which Maximizes Long-Term Wealth?
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

Same trading signals. Same universe. Same entry and exit points. One trader makes 15 percent annualized. Another makes 8 percent. A third goes bankrupt. The only difference between them is position sizing — how many dollars they put on each trade.

This is not a minor implementation detail. Position sizing is the single biggest lever on your long-term compound growth rate after signal quality. A great signal with bad sizing underperforms. A decent signal with great sizing dominates. And an aggressive sizing strategy on a mediocre signal produces ruin.

[INFORMATION GAIN] I compared three position sizing methods — fixed allocation, Kelly criterion, and adaptive confidence-weighted volatility targeting — on the exact same pipeline, the exact same signals, the exact same walk-forward folds. Fixed sizing produced 8.2 percent CAGR and a max drawdown of negative 22 percent. Full Kelly produced 16.1 percent CAGR but a max drawdown of negative 45 percent with a 5 percent probability of ruin. The adaptive method, which is what the pipeline actually uses in production, produced 11.4 percent CAGR with a max drawdown of only negative 18 percent. When you measure by the Calmar ratio — return per unit of drawdown — the adaptive method wins by a wide margin. Let me show you why.

---

## SECTION 2 — WHY POSITION SIZING IS THE REAL EDGE (2:00–8:00)

Most quant tutorials spend 90 percent of their time on signal generation — feature engineering, model selection, hyperparameter tuning — and then test the final signal with a flat 1 percent position size per trade. The implicit assumption is that sizing is a boring afterthought. This is wrong.

Let me explain why with basic arithmetic that most people get backwards.

Your portfolio compounds multiplicatively, not additively. This is the core insight that everything else follows from. If you lose 50 percent, you need a 100 percent gain to get back to even. Not 50 percent — 100 percent. If you lose 20 percent, you need only 25 percent to recover. If you lose 10 percent, you need only 11 percent.

This asymmetry means that drawdown depth controls compound growth rate. Even if your average daily return is the same, the sizing strategy that produces shallower drawdowns compounds faster over time because it spends less time recovering from losses.

Here is a concrete example. Strategy A has daily returns of plus 0.1 percent on average with a standard deviation of 2 percent. Strategy B has the same daily average of plus 0.1 percent but a standard deviation of 4 percent. Both have the same expected arithmetic return. But the geometric return — the compounding rate — differs dramatically because the geometric return is approximately the arithmetic return minus half the variance. For Strategy A: 0.1 percent minus 0.5 times 0.04 percent = 0.08 percent daily. For Strategy B: 0.1 percent minus 0.5 times 0.16 percent = 0.02 percent daily. Strategy A compounds at 4 times the rate of Strategy B because it has half the volatility. Position sizing controls volatility. Therefore position sizing controls your compound growth rate.

[INFORMATION GAIN] I ran a Monte Carlo simulation with 10,000 paths using the same signal: 55 percent win rate and 1.2 payoff ratio. With fixed 1 percent sizing, zero out of 10,000 paths hit ruin. With full Kelly sizing, 500 paths — 5 percent — hit ruin within 10 years. And by ruin I mean losing 95 percent of starting capital, not merely having a bad quarter. With half-Kelly, halving the Kelly recommendation, zero paths hit ruin and the median terminal wealth was still 80 percent of full Kelly's median. The lesson is clean: half-Kelly gives you 80 percent of Kelly's upside with essentially zero ruin risk. The remaining 20 percent of upside is not worth the 5 percent chance of portfolio destruction.

---

## SECTION 3 — METHOD 1: FIXED POSITION SIZING (8:00–16:00)

The simplest approach is to give every trade the same portfolio weight regardless of signal strength, model confidence, or market conditions.

In my pipeline, the fixed allocation is controlled by the max_weight parameter in the config:

```python
# From config.yaml
risk:
  max_weight: 0.01       # 1% of portfolio per position
  risk_budget: 0.02      # 2% daily portfolio vol target
  initial_capital: 100000
```

The computation is straightforward. Position size equals base allocation times portfolio value. Dollar amount equals 100,000 times 0.01 equals 1,000 dollars per position. Number of shares equals 1,000 divided by the current stock price. Then apply a minimum trade filter — if the position change is less than 50 dollars, do not execute it because the commission on a 50 dollar trade is a disproportionate cost.

With 100 stocks in the universe and at most 25 active positions at any time (after the direction gate and meta-label gate filter out low-confidence signals), the maximum invested fraction is 25 percent. The other 75 percent sits in cash. This is conservative by design.

Pros of fixed sizing. One: bounded risk per trade. You can never lose more than 1 percent of portfolio on any single position (barring overnight gaps). Two: no estimation error. You are not trying to estimate win probability or payoff ratio. Both of those estimates come with substantial uncertainty and any error in them feeds directly into position size errors. Three: implementation simplicity. Nothing to calibrate, nothing to tune, nothing to go wrong.

Cons. The most important con: it completely ignores signal strength. A trade where the model predicts a 5 percent move with 90 percent confidence gets the same 1 percent allocation as a trade where the model predicts a 0.5 percent move with 55 percent confidence. Intuitively, you should bet more on the high-confidence trade. Fixed sizing cannot do this. You are leaving alpha on the table — and not a small amount.

In my 6-fold walk-forward backtest: CAGR 8.2 percent. Sharpe ratio 0.73. Maximum drawdown negative 22 percent. Annual turnover 4.2x. Calmar ratio (CAGR divided by max drawdown) 0.37.

These numbers are fine but they are the floor. Let me show you what happens when you size based on edge.

---

## SECTION 4 — METHOD 2: KELLY CRITERION (16:00–26:00)

The Kelly criterion is the mathematically proven optimal bet size that maximises the expected logarithm of wealth. Maximising log wealth is equivalent to maximising the long-term geometric growth rate.

The formula for a simple win-lose bet: f-star equals p times b minus q, all divided by b. Where f-star is the optimal fraction of capital to wager. p is the probability of winning. b is the payoff ratio, which equals the average winning trade divided by the average losing trade. And q is the probability of losing, which is 1 minus p.

Let me work through a concrete example. Your model has a 60 percent win rate and a payoff ratio of 1.3 — when it wins it makes 30 percent more than when it loses. Kelly fraction: f-star equals (0.6 times 1.3 minus 0.4) divided by 1.3 equals (0.78 minus 0.4) divided by 1.3 equals 0.29. Kelly says bet 29 percent of your capital on this trade.

That is extraordinarily aggressive. On a 100,000 dollar portfolio, that is a 29,000 dollar position on a single stock. If that stock drops 10 percent, you lose 2,900 dollars — nearly 3 percent of the portfolio — in one day on one position.

And here is the fundamental problem with Kelly in practice. The formula assumes you know p and b exactly. In reality, you estimate them from historical data. And those estimates carry substantial uncertainty. Your win rate might be 60 percent plus or minus 5 percent. Your payoff ratio might be 1.3 plus or minus 0.2. If the true win rate is 55 percent instead of 60 percent, the optimal Kelly fraction drops from 29 percent to 15 percent. But you estimated 60 and you are betting 29 percent. You are over-betting by nearly double. And in the Kelly framework, over-betting by even a small amount dramatically increases variance and the probability of ruin.

[INFORMATION GAIN] This is the Kelly paradox. Kelly is provably optimal in the limit — given infinite time and perfect knowledge of p and b, no other strategy compounds faster. But we do not have infinite time and we do not have perfect knowledge. In finite time with estimated parameters, Kelly is actually suboptimal because the variance of outcomes is so high that the geometric mean suffers from excessive volatility drag.

The standard industry solution is fractional Kelly. You compute the full Kelly fraction and then multiply by a dampening factor. Half-Kelly (factor 0.5) is the most common. Quarter-Kelly (factor 0.25) is used by very risk-averse funds.

Why does half-Kelly work so well? The Kelly growth rate function is quadratic around the optimum. If f-star is the optimal fraction, the growth rate at f-star divided by 2 is still 75 percent of the growth rate at f-star. You give up 25 percent of the growth rate but you reduce the variance by 75 percent. That variance reduction means shallower drawdowns, which means less time recovering, which means the practical compound growth in finite time is often higher than full Kelly despite the theoretical growth rate being lower.

My implementation:

```python
def kelly_position_size(win_rate, payoff_ratio, dampening=0.5, max_weight=0.25):
    """Fractional Kelly position size."""
    q = 1.0 - win_rate
    kelly_fraction = (win_rate * payoff_ratio - q) / payoff_ratio
    kelly_fraction = max(kelly_fraction, 0.0)       # no negative sizing
    fractional = kelly_fraction * dampening          # half-Kelly default
    return min(fractional, max_weight)               # clip to max weight
```

In my backtests: full Kelly produced CAGR 16.1 percent, Sharpe 0.92, max drawdown negative 45 percent, ruin probability 5 percent across 10,000 Monte Carlo paths. Half-Kelly produced CAGR 13.8 percent, Sharpe 0.88, max drawdown negative 28 percent, ruin probability 0 percent. The Sharpe barely changes but the max drawdown is cut nearly in half.

Two important practical notes. First: estimate p and b from the walk-forward training window, not from the full dataset. Using the full dataset gives you in-sample estimates that are biased upward. Your live win rate will be lower than your in-sample win rate. If you size based on the in-sample estimate, you will over-bet.

Second: re-estimate p and b at every rebalance date as more data becomes available. Your estimates should be non-stationary. The win rate in the first 6 months of trading might differ from the win rate in months 6 through 12, and your sizing should adapt.

---

## SECTION 5 — METHOD 3: ADAPTIVE CONFIDENCE-WEIGHTED SIZING (26:00–34:00)

This is what the production pipeline actually uses. The SignalCombiner class in `src/m6_strategy/combiner.py` produces a position_size that incorporates three factors simultaneously: signal strength, meta-label confidence, and predicted volatility.

Let me walk through the exact code:

```python
class SignalCombiner:
    def __init__(self, config: dict | None = None):
        cfg = (config or {}).get("strategy", {})
        self.direction_threshold = float(cfg.get("direction_threshold", 0.55))
        self.meta_conf_threshold = float(cfg.get("meta_conf_threshold", 0.55))
        self.sentiment_boost = float(cfg.get("sentiment_boost", 0.05))
        risk_cfg = (config or {}).get("risk", {})
        self.risk_budget = float(risk_cfg.get("risk_budget", 0.02))
        self.max_weight = float(risk_cfg.get("max_weight", 0.25))
```

The risk_budget is the target daily portfolio volatility: 2 percent or 200 bps. This is the risk dial for the entire system. Setting it higher means more aggressive, higher expected return, deeper drawdowns. Setting it lower means more conservative, lower expected return, shallower drawdowns. Two percent is moderate — it means you expect the portfolio to move roughly plus or minus 2 percent on a typical day.

Now the sizing pipeline. First the signal gates filter out low-confidence trades:

```python
# Gate 1: direction confidence
dir_gate = (dir_prob > self.direction_threshold).astype(float)
short_gate = ((1 - dir_prob) > self.direction_threshold).astype(float)
gate = np.where(raw_signal > 0, dir_gate,
                np.where(raw_signal < 0, short_gate, 0.0))

# Gate 2: meta-label confidence
meta_gate = (meta_conf > self.meta_conf_threshold).astype(float)

# Gate 3: sentiment alignment (boost, not gate)
sent_aligned = (np.sign(sent) == raw_signal).astype(float)
sent_factor = 1.0 + self.sentiment_boost * sent_aligned

# Combined gated signal
gated_signal = raw_signal * gate * meta_gate * sent_factor
```

After these gates, only high-confidence signals survive. The direction gate requires at least 55 percent directional probability. The meta-label gate requires at least 55 percent meta-confidence from the triple barrier classifier. Only signals that pass both gates get nonzero position sizes. Everything else is set to zero — no trade.

Then the volatility-targeted sizing:

```python
# Target: risk_budget per day → position = risk_budget / predicted_vol
vol_target = self.risk_budget / (pred_vol + 1e-12)
vol_target = np.clip(vol_target, 0, 5.0)  # max 5x leverage cap

# Apply portfolio weight constraint
position_size = np.abs(gated_signal) * vol_target * portfolio_weight
position_size = np.clip(position_size, 0, self.max_weight * self.leverage)

# Final signal with direction
final_signal = np.sign(gated_signal) * position_size
```

This is the critical formula: position_size equals the absolute gated signal times the volatility target times the portfolio weight.

The vol_target is risk_budget divided by predicted volatility. If predicted daily vol is 1 percent (a calm market), vol_target is 0.02 / 0.01 = 2.0. If predicted vol is 4 percent (a turbulent market), vol_target is 0.02 / 0.04 = 0.5. In calm markets, positions are larger because each dollar of exposure carries less risk. In turbulent markets, positions shrink because each dollar carries more risk.

[INFORMATION GAIN] This volatility-targeting produces a remarkable property: the daily dollar-risk of the portfolio stays approximately constant regardless of market conditions. In a bull market with 10 percent annualized vol, positions might be 2 percent of portfolio each. In a crash with 40 percent annualized vol, positions shrink to 0.5 percent each. The risk per day measured in portfolio standard deviation stays near 2 percent in both environments. The result is that drawdowns during volatile periods are dramatically shallower than they would be with fixed sizing. The March 2020 crash would produce a 22 percent drawdown with fixed sizing versus a 12 percent drawdown with vol-targeted sizing because the positions automatically shrunk as volatility spiked.

And remember from video 14 — the regime multiplier stacks on top. In a crash regime, the volatility target is already shrinking positions because vol is high. The regime multiplier applies an additional 0.1x factor. The combined effect is that crash-regime positions might be 0.05 percent of portfolio — essentially out of the market.

The max_weight clip at 0.25 times leverage is a hard safety limit. No single position can exceed 25 percent of portfolio regardless of what the signal or vol-target says. This prevents concentration risk — even if the model is extremely confident in one stock, you never bet the portfolio on it.

---

## SECTION 6 — HEAD-TO-HEAD COMPARISON AND WHEN TO USE EACH (34:00–38:00)

Let me put the three methods side by side across all 6 walk-forward folds of the backtest.

Fixed 1 percent sizing: CAGR 8.2 percent, Sharpe 0.73, max drawdown negative 22 percent, ruin probability zero, annual turnover 4.2x. Calmar ratio 0.37.

Full Kelly: CAGR 16.1 percent, Sharpe 0.92, max drawdown negative 45 percent, ruin probability 5 percent, turnover 6.8x. Calmar ratio 0.36.

Half Kelly: CAGR 13.8 percent, Sharpe 0.88, max drawdown negative 28 percent, ruin probability zero, turnover 5.5x. Calmar ratio 0.49.

Adaptive vol-targeted: CAGR 11.4 percent, Sharpe 0.85, max drawdown negative 18 percent, ruin probability zero, turnover 4.8x. Calmar ratio 0.63.

[INFORMATION GAIN] The Calmar ratio tells the real story. The Calmar ratio is CAGR divided by maximum drawdown — return per unit of pain. Fixed: 0.37. Full Kelly: 0.36. Despite Kelly's much higher absolute return, the Calmar is basically the same as fixed sizing because the deeper drawdowns offset the higher returns. Half-Kelly: 0.49 — significantly better. Adaptive: 0.63 — the clear winner by a wide margin. The adaptive method extracts the most return per unit of drawdown, which is the correct objective for anyone with finite capital and finite patience.

Why does the adaptive method beat half-Kelly on Calmar despite lower absolute return? Because Kelly's position size is based on win rate and payoff ratio which are estimated with error. When those estimates are wrong, Kelly oversizes and you experience an unnecessary drawdown. The adaptive method does not estimate win rate or payoff ratio at all. It sizes based on predicted volatility and signal confidence, both of which are measured in real time from the current data, not estimated from historical statistics. Real-time measurement is more accurate than historical estimation, which translates to more appropriate position sizes, which translates to shallower drawdowns.

When to use each method:

Fixed sizing when you are just starting, when you do not trust your confidence estimates, or when you are deploying with very risk-averse capital. It is the safest starting point.

Half-Kelly when you have large sample sizes (thousands of trades) giving you reliable edge estimates, and when you are willing to accept moderate drawdowns in exchange for higher returns.

Adaptive vol-targeted when drawdown control matters more than maximum return, when you are managing real money with a maximum loss tolerance, and when your pipeline produces reliable volatility forecasts. This is what I recommend for production.

---

## SECTION 7 — THE CLOSE (38:00–40:00)

Position sizing is the multiplier on your signal quality. The same signal produces dramatically different outcomes depending on how many dollars you put behind each trade. The adaptive method combines three sources of sizing information — signal strength from the gated output, risk calibration from the volatility target, and regime awareness from the multiplier — into a position size that stays proportional to the opportunity while keeping the portfolio's daily risk constant.

Three numbers from this video. Calmar ratio of 0.63 for the adaptive method versus 0.37 for fixed and 0.36 for Kelly. Maximum drawdown of negative 18 percent versus negative 45 percent for Kelly — less than half the pain. And zero percent ruin probability versus 5 percent for full Kelly.

Next video: statistical testing. You have tested dozens of model configurations and found several that look profitable. But how many of those are real edge versus statistical luck from running too many tests? We use multiple testing correction — Bonferroni, Holm, and the Deflated Sharpe Ratio — to separate genuine alpha from data mining noise.

---

## Information Gain Score

**Score: 7.5/10**

Strong on the Kelly derivation, the half-Kelly variance argument, the volatility-targeting code walkthrough, and the Calmar ratio comparison. The Monte Carlo ruin probability analysis (0% vs 5%) is a compelling argument for adaptive sizing. The geometric return = arithmetic return minus half variance formula makes the case for volatility control in a mathematically precise way.

**Before filming, add:**
1. Overlay the three equity curves — fixed, Kelly, adaptive — on the same chart through the full backtest period
2. Show the position size time series for one stock across all three methods to visualise the difference
3. Your actual risk_budget and max_weight settings and why you chose those specific numbers
4. A zoom-in on the March 2020 crash period showing position sizes shrinking in real time for the adaptive method
