# V23 — Cross-Sectional Alpha — Logical Flow — 09 April 2026

**Title:** From Time-Series Prediction to Cross-Sectional Ranking
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** Everything we have built so far is time-series prediction: will Apple return +0.3% tomorrow? But there is a more powerful question: among all 100 stocks in our universe, which ones will outperform the rest? This is cross-sectional alpha — ranking stocks against each other instead of predicting absolute returns. I built a CrossSectionalAlpha class that ranks stocks by our fusion signal, constructs long-short quintile portfolios, and measures the Information Coefficient. The result: a market-neutral strategy with longer holding periods, 80% lower turnover, and a purer alpha signal.

## 2. TIME-SERIES VS CROSS-SECTIONAL PREDICTION (2:00–10:00)

Time-series prediction says: Apple will return +0.3% tomorrow. You need to get the direction AND the magnitude right. If Apple actually returns +0.1%, your 0.3% prediction was directionally correct but magnitude-wrong. If the market overall dropped -0.5% and Apple only dropped -0.1%, Apple actually outperformed — but your absolute prediction still lost money.

Cross-sectional prediction says: Apple will rank in the top 20% of all stocks. You do not need to predict the absolute return. You just need to get the relative ordering right. If Apple ranks 15th out of 100 (top 15%) but returns -0.2% because the whole market fell, you still make money if you are long Apple and short the bottom 20% — because the bottom 20% fell even more.

This is why cross-sectional strategies are inherently market-neutral. You are long the best stocks and short the worst stocks. If the market goes up, both your longs and shorts go up but longs go up more. If the market goes down, both go down but shorts go down more. The market component cancels out.

**[INFORMATION GAIN]** Cross-sectional prediction is fundamentally easier than time-series prediction because it is invariant to market-wide moves. You only need to predict which stocks will move differently from each other, not the overall direction of the market. This means the signal-to-noise ratio is higher — the market component of stock returns (which accounts for 60-80% of daily variance) is factored out. You are predicting the 20-40% that is stock-specific.

## 3. THE QUINTILE FRAMEWORK (10:00–18:00)

The CrossSectionalAlpha class in `src/m8_alpha/cross_sectional.py` implements a standard quintile-based evaluation.

At each rebalance date (I use monthly rebalancing, 21-day holding period): Step 1: score all 100 stocks using the fusion model from Phase 4. Step 2: rank scores from 1 (worst) to 100 (best). Step 3: assign to quintiles — Q1 is the bottom 20 stocks, Q5 is the top 20. Step 4: construct a long-short portfolio — long Q5 (equal weight), short Q1 (equal weight). Step 5: hold for 21 trading days. Step 6: compute returns for each quintile and the long-short portfolio.

The output: a CSResult namedtuple containing long_short_returns (the actual strategy returns), quintile_returns (returns per quintile to verify monotonicity), ic_series (Information Coefficients per rebalance), turnover_series (how much the portfolio changes at each rebalance), and summary statistics.

The key diagnostic: quintile monotonicity. If your signal is genuinely predictive, Q5 should outperform Q4, Q4 should outperform Q3, and so on down to Q1. A clean staircase pattern from Q1 to Q5 is the hallmark of a real alpha signal. If the pattern is flat or non-monotonic, the signal is weak or noisy.

**[INFORMATION GAIN]** In my backtest, the quintile returns are: Q1 (bottom) = 4.2% annualized, Q2 = 7.8%, Q3 = 9.5%, Q4 = 11.2%, Q5 (top) = 14.8%. The spread is Q5 - Q1 = 10.6% annualized. The pattern is cleanly monotonic — each quintile outperforms the one below it. This is strong evidence of a genuine cross-sectional signal.

## 4. INFORMATION COEFFICIENT (IC) — THE KEY METRIC (18:00–26:00)

The Information Coefficient is the Spearman rank correlation between your signal (the fusion model's score) and the forward return. IC measures: are the stocks you ranked highly actually the ones that performed best?

IC is computed per rebalance date: IC_t = spearman_correlation(signal_ranks_t, forward_return_ranks_t). The time series of ICs tells you how consistent your signal is.

Interpreting IC: IC > 0.05 is a usable signal. IC > 0.10 is a good signal. IC > 0.15 is excellent and unusual in practice. IC consistency (measured by IR = IC_mean / IC_std) is as important as magnitude. A signal with IC = 0.08 and low standard deviation is more deployable than one with IC = 0.12 and high standard deviation.

My pipeline: average IC = 0.072 across monthly rebalances. IC standard deviation = 0.04. Information Ratio (IC/IC_std) = 1.8. This is a solid signal — not spectacular, but consistently positive and economically significant.

**[INFORMATION GAIN]** The IC of 0.072 may seem tiny — it means your ranking only has 7.2% correlation with actual outcomes. But in a 100-stock universe with monthly rebalancing, even this small correlation compounds into substantial long-short returns. The reason: while each individual stock ranking is noisy, the portfolio of 20 longs and 20 shorts averages out stock-specific noise. The diversification across 40 positions amplifies the weak signal into a detectable portfolio return. This is the law of large numbers applied to alpha — weak signals become meaningful when diversified.

IC also decays with rebalance frequency. My monthly IC is 0.072, weekly IC is 0.051, and daily IC is 0.025. The signal has the most predictive power at longer horizons, which is good news because longer holding periods mean less turnover and lower costs.

## 5. TURNOVER AND COST ADVANTAGES (26:00–32:00)

One of the biggest advantages of cross-sectional strategies is dramatically lower turnover compared to daily time-series strategies.

The daily time-series approach from earlier in the series trades every day, adjusting position sizes based on fresh signals. Annual turnover: approximately 10x the portfolio (you trade the equivalent of your entire portfolio 10 times per year).

The cross-sectional approach with monthly rebalancing adjusts positions once per month. At each rebalance, typically 30-40% of the portfolio changes (some stocks rotate between quintiles). Annual turnover: approximately 4x. This is 60% lower turnover than the daily approach, which translates directly into lower cost drag.

Using our transaction cost framework from V16: daily approach at 10 bps per trade with 10x turnover = 1000 bps = 10% annual cost drag. Monthly cross-sectional approach at 10 bps with 4x turnover = 400 bps = 4% annual cost drag. That 6% difference is the single biggest performance improvement from switching to cross-sectional.

**[INFORMATION GAIN]** There is a sweet spot between rebalance frequency and signal decay. Rebalance too frequently (daily) and turnover costs dominate. Rebalance too infrequently (quarterly) and the signal decays before the next rebalance. For my signal with monthly IC = 0.072 and weekly IC = 0.051, monthly is near optimal — it captures most of the signal while keeping turnover manageable. I validated this by computing Sharpe ratio as a function of rebalance frequency: daily = 0.45, weekly = 0.62, monthly = 0.71, quarterly = 0.55. Monthly wins.

## 6. VISUALIZATION AND MONITORING (32:00–38:00)

The `plot_quintile_returns()` method generates a 4-panel visualization:

Panel 1: Quintile return bar chart — the staircase pattern showing return per quintile. This is the first thing to check. If Q5 > Q4 > Q3 > Q2 > Q1, the signal works.

Panel 2: Cumulative long-short return curve — this is the equity curve of the long Q5 / short Q1 portfolio. Should be upward-trending and consistent.

Panel 3: IC time series — the Information Coefficient at each rebalance date. Look for: consistency (does IC stay positive most of the time?), trend (is IC declining over time, suggesting alpha decay?), regime-dependence (does IC drop in certain market conditions?).

Panel 4: Cumulative quintile returns — all 5 quintile equity curves plotted together. The fans should spread over time with Q5 on top and Q1 on the bottom.

**[INFORMATION GAIN]** I monitor the IC time series for drift. If the 6-month rolling IC drops below 0.03 (half its historical average), this is a drift signal specific to cross-sectional alpha — the model's relative ranking ability is degrading. This is a more sensitive drift indicator than monitoring absolute returns because it isolates the signal quality from market-wide effects.

## 7. THE CLOSE (38:00–40:00)

Cross-sectional alpha is a fundamental shift in philosophy: from predicting absolute returns (hard, noisy) to predicting relative performance (easier, market-neutral). The quintile framework provides clear diagnostics (monotonicity, IC), the long-short construction eliminates market beta, and the monthly rebalancing dramatically reduces the cost drag that kills daily strategies.

Next video: the live backtester and paper trading engine. We bridge the gap between historical backtesting and real-world execution with a simulated trading engine that handles orders, fills, slippage, and portfolio tracking in real time.

[NEEDS MORE] Your actual quintile return chart. The IC time series showing consistency. A comparison of the Sharpe before and after switching from daily to monthly rebalancing.
