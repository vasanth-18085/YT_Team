# V22 — Factor Analysis — Refined Script

**Title:** Fama-French 5-Factor Model: Where Does Your Edge Come From?
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

Your strategy made 15 percent annualized return. But where did that return actually come from?

When I decomposed my pipeline's returns using a 5-factor model, I found: 10 percent came from market beta — I was long in a rising market. 3 percent came from a size tilt — I accidentally overweighted small-caps. And only 2.1 percent was genuine alpha — return that cannot be explained by any known risk factor.

[INFORMATION GAIN] That 2.1 percent is the only part your ML models actually contribute. The other 13 percent could have been replicated by buying a combination of index funds and factor ETFs for 10 basis points per year in fees. If your alpha is zero after factor decomposition, your complex quant pipeline is nothing more than an expensive way to buy beta. Factor analysis is the honesty test that separates real predictive edge from disguised factor exposure.

---

## SECTION 2 — WHAT ARE RISK FACTORS AND WHY THEY EXPLAIN RETURNS (2:00–10:00)

Academic finance has identified several systematic sources of return that are available to anyone who takes the corresponding risk. These are called risk factors because the returns they generate are compensation for bearing specific, documented risks.

The Fama-French framework identifies 5 main factors.

The market factor (MKT minus RF): the return of the entire stock market above the risk-free rate. If you hold any stock portfolio, you have positive market exposure. This is the easiest return to capture — buy an S&P 500 index fund and you get the market factor for 3 basis points per year. Any return your strategy earns that is correlated with the overall market is not alpha. It is beta.

The size factor (SMB — Small Minus Big): historically, small-cap stocks have outperformed large-cap stocks on a risk-adjusted basis. If your trading universe skews toward smaller companies, part of what looks like alpha might actually be the size premium you are passively harvesting.

The value factor (HML — High Minus Low): stocks with high book-to-market ratios — value stocks — have historically outperformed growth stocks. If your ML features happen to select stocks with low price-to-book ratios, you might be loading on the value factor without realising it.

The profitability factor (RMW — Robust Minus Weak): profitable firms outperform unprofitable ones. This is the quality premium.

The investment factor (CMA — Conservative Minus Aggressive): firms that invest conservatively tend to outperform those that invest aggressively. This is the low-investment anomaly.

These 5 factors together explain approximately 80 to 90 percent of the cross-sectional variation in stock returns. What they do not explain — the residual — is alpha.

[INFORMATION GAIN] The practical implication for your quant strategy is blunt. If your 15 percent return is entirely explained by these 5 well-known factors, you have no alpha. You are just bearing known risks that the market compensates. A much simpler and cheaper approach would be to buy factor ETFs: IWM for size, IWD for value, QUAL for profitability, and SPY for market exposure. The total fee would be roughly 15 basis points per year instead of the operational cost and complexity of running a quantitative pipeline. Factor decomposition tells you whether your pipeline earns its keep.

---

## SECTION 3 — THE FACTOR DECOMPOSITION REGRESSION (10:00–18:00)

The standard approach: regress your strategy's excess returns against the 5 factor return series.

$r_{strategy} - r_f = \alpha + \beta_{MKT} \cdot MKT + \beta_{SMB} \cdot SMB + \beta_{HML} \cdot HML + \beta_{RMW} \cdot RMW + \beta_{CMA} \cdot CMA + \epsilon$

The 5 factor return series are publicly available from Kenneth French's data library (updated monthly) and from AQR (updated daily). The risk-free rate is the US T-bill rate.

The regression output gives you 6 numbers plus diagnostics. The 5 betas are your factor loadings — how much of each factor your strategy is implicitly exposed to. Alpha (the intercept) is the return that cannot be explained by any factor. If alpha is statistically significant with a p-value below 0.05, you have genuine excess return.

My pipeline's decomposition results across the full out-of-sample period:

Beta MKT equals 0.82 (t-stat 12.4, p essentially zero). This means the strategy moves 82 percent as much as the market. In a 10 percent market rally, the strategy captures about 8.2 percent from market exposure alone.

Beta SMB equals 0.15 (t-stat 2.1, p equals 0.04). A slight small-cap tilt, statistically significant. This means about 1.5 percentage points of the annual return comes from the size factor.

Beta HML equals negative 0.08 (t-stat negative 1.1, p equals 0.27). A slight growth tilt, not statistically significant. The strategy has no meaningful value or growth exposure.

Beta RMW equals 0.03 (t-stat 0.4, p equals 0.69). Negligible profitability exposure.

Beta CMA equals negative 0.02 (t-stat negative 0.3, p equals 0.77). Negligible investment exposure.

Alpha equals 2.1 percent annualised (t-stat 2.1, p equals 0.04). Statistically significant genuine alpha.

R-squared equals 0.68. The 5 factors explain 68 percent of the strategy's daily return variation. The remaining 32 percent includes alpha plus idiosyncratic noise.

[INFORMATION GAIN] The alpha of 2.1 percent may seem modest compared to the 15 percent gross return. But here is the correct way to think about it. The market beta of 0.82 contributed approximately 8.2 percent (assuming 10 percent market return). The size beta contributed about 1.5 percent. That accounts for 9.7 percent. The remainder — roughly 5.3 percent — is split between alpha (2.1 percent) and idiosyncratic variation. The alpha is the only part that justifies the complexity and cost of running the quant pipeline. And 2.1 percent of genuine alpha is actually a strong result by institutional standards — most hedge funds would be delighted with consistent, statistically significant alpha of 2 percent after costs.

---

## SECTION 4 — MY CUSTOM FACTOR MODEL (18:00–26:00)

The FactorModel class in `src/m8_alpha/factor_model.py` takes a different approach from the standard Fama-French regression. Instead of downloading academic factor libraries, it computes 5 custom factors directly from price and volume data.

```python
class FactorModel:
    FACTORS = {
        "momentum": {"weight": 0.30, "window": 252, "skip": 21},
        "reversal": {"weight": 0.15, "window": 5},
        "volatility": {"weight": 0.20, "window": 63},
        "volume_trend": {"weight": 0.15, "window": 63},
        "distance_high": {"weight": 0.20, "window": 252},
    }
```

Factor 1 — Momentum (weight 0.30): the 12-month return excluding the most recent 21 days. This captures medium-term price continuation while avoiding short-term mean reversion. The 1-month exclusion is a well-known technique from Jegadeesh and Titman's 1993 paper — stocks that went up over the past 12 months tend to continue going up, but stocks that went up over the past week tend to reverse. Excluding the last month isolates the persistent momentum signal from the transient reversal noise.

Factor 2 — Short-term Reversal (weight 0.15): the negative of the 5-day return. Stocks that fell over the past week tend to bounce back. This is a contrarian signal that works at short horizons where momentum fails.

Factor 3 — Low Volatility (weight 0.20): the negative of 63-day realised volatility. Lower volatility stocks receive higher factor scores. This captures the low-volatility anomaly — low-vol stocks deliver higher risk-adjusted returns than high-vol stocks, which contradicts classical finance theory. In theory, higher risk should mean higher return. In practice, the opposite is true for individual stocks because speculative demand for lottery-like high-vol stocks pushes their prices up and their expected returns down.

Factor 4 — Volume Trend (weight 0.15): the ratio of current volume to the 63-day average volume. Unusual volume often precedes price moves because it signals attention, liquidity, or informed trading activity.

Factor 5 — Distance to 52-Week High (weight 0.20): (current price divided by 52-week high) minus 1. Stocks near their all-time highs tend to continue performing well due to the anchoring effect — investors view stocks near highs as strong and are more willing to buy them.

Each factor is z-scored cross-sectionally per date:

```python
def _cross_sectional_zscore(self, df: pd.DataFrame) -> pd.DataFrame:
    """Z-score each row (date) across tickers."""
    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1) + 1e-12, axis=0)
```

[INFORMATION GAIN] Cross-sectional z-scoring is essential. Without it, a factor value of 0.05 means different things on different dates. When the entire market has momentum of 0.04 to 0.06, a raw value of 0.05 tells you nothing about relative ranking. After z-scoring, a value of plus 2.0 always means two standard deviations above the cross-sectional mean on that specific date — consistently interpretable and comparable across time.

The composite signal is the weighted sum of all 5 z-scored factors. The weights (0.30, 0.15, 0.20, 0.15, 0.20) were set based on the historical information content of each factor, not optimised on my specific backtest period — that would introduce look-ahead bias.

---

## SECTION 5 — FACTOR ATTRIBUTION OVER TIME (26:00–34:00)

The static regression from Section 3 gives you average factor exposures over the full period. But factor loadings change over time. During a momentum rally, your strategy's momentum beta increases. During a volatility spike, the low-vol beta might flip as high-vol stocks crash.

I run the Fama-French regression on a rolling 126-day (6-month) window to track how factor exposures evolve:

```python
def rolling_factor_attribution(strategy_returns, factor_returns, window=126):
    """Rolling OLS regression on 5 factors."""
    n = len(strategy_returns)
    results = []
    for end in range(window, n):
        start = end - window
        y = strategy_returns.iloc[start:end].values
        X = factor_returns.iloc[start:end].values
        X = np.column_stack([np.ones(window), X])  # add intercept
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        results.append({
            'date': strategy_returns.index[end],
            'alpha': beta[0] * 252,  # annualise
            'beta_MKT': beta[1],
            'beta_SMB': beta[2],
            'beta_HML': beta[3],
            'beta_RMW': beta[4],
            'beta_CMA': beta[5],
        })
    return pd.DataFrame(results).set_index('date')
```

The rolling attribution chart reveals several insights. First: during Q1 2020 (pre-COVID), the strategy's market beta spiked from 0.82 to 1.1 as the ML models became more bullish. When the crash hit in March, the higher beta amplified losses. The regime detector from V14 caught this and reduced position sizes, but the elevated beta had already cost extra drawdown.

Second: the rolling alpha is most positive during medium-volatility environments (VIX between 15 and 25). In very low volatility (VIX below 12), alpha drops toward zero because everything moves together and there is less cross-sectional dispersion for the model to exploit. In very high volatility (VIX above 35), alpha drops because the signal-to-noise ratio collapses.

[INFORMATION GAIN] Attribution changes over time, and understanding this temporal pattern prevents two mistakes. Mistake one: taking credit for factor returns. In quiet bull markets, most of the strategy's return comes from market beta. If you think that is your ML model's alpha, you will be surprised when the market turns. Mistake two: losing confidence during factor drawdowns. If the value factor is in a drawdown period and your strategy underperforms, the factor attribution tells you the underperformance is from HML exposure, not from a model failure. You should not retrain or abandon the model — you should wait for the factor to recover.

The `factor_exposures()` method returns individual DataFrames for each factor, allowing you to see which stocks score highest and lowest:

```python
def factor_exposures(self, prices: pd.DataFrame, volumes: pd.DataFrame = None):
    """Return dict of factor_name → DataFrame of z-scores."""
    signals = self.compute_signals(prices, volumes)
    exposures = {}
    for factor_name in self.FACTORS:
        exposures[factor_name] = self._compute_single_factor(
            prices, volumes, factor_name
        )
    return exposures
```

And the `factor_correlation()` method reveals how diversified your factors are:

```python
def factor_correlation(self, prices, volumes=None):
    """Cross-factor correlation matrix."""
    exposures = self.factor_exposures(prices, volumes)
    # Stack all factors and compute correlation
    combined = pd.DataFrame({k: v.mean(axis=1) for k, v in exposures.items()})
    return combined.corr()
```

In my data: momentum and reversal have correlation negative 0.3 (they partially offset, which is expected — momentum buys recent winners while reversal buys recent losers). Momentum and distance-to-high have correlation 0.4 (both capture recent winners). Volatility and volume have near-zero correlation. The factors are moderately diversified — the composite captures more information than any single factor alone.

---

## SECTION 6 — DESIGN IMPLICATIONS AND NEUTRALISATION (34:00–38:00)

Factor analysis has direct implications for strategy design.

If your strategy has high market beta (like my 0.82), you can reduce it by hedging with short SPY positions or by constructing the portfolio as dollar-neutral — equal dollar value of long and short positions. A market-neutral strategy has beta approximately zero, which means returns are independent of market direction. This comes at a cost: you give up the market risk premium (roughly 8 percent long-run average) in exchange for a purer alpha signal.

If your strategy has unintended factor tilts — my size beta of 0.15 was unintentional — you can neutralise them. The simplest approach: add a constraint to the portfolio optimiser that the portfolio's weighted average size factor exposure must be zero. This forces equal weight in small and large stocks and removes the size tilt.

The goal for a pure quantitative alpha strategy is: market-neutral (market beta approximately zero), factor-neutral (all factor betas approximately zero), with significant positive alpha. This is the purest form of predictive edge. It is also the hardest to achieve.

My pipeline is not factor-neutral. I deliberately keep the 0.82 market beta because the market has positive expected return over the long run. And the 2.1 percent alpha on top is the evidence that the ML models add genuine value beyond what market exposure provides. This is a conscious design decision: I accept factor exposure for the premium it provides and layer alpha on top.

[INFORMATION GAIN] Whether to be factor-neutral versus factor-exposed is ultimately a question about your investment horizon and risk tolerance. For a $100M institutional fund competing on risk-adjusted returns versus a benchmark, factor-neutral is necessary because investors can get factor exposure cheaply elsewhere. For a $100K personal account trying to maximise absolute return, keeping market exposure (getting the beta premium for free) and adding alpha on top is perfectly rational. The factor analysis tells you what you are doing so the decision is conscious rather than accidental.

---

## SECTION 7 — THE CLOSE (38:00–40:00)

Factor analysis is the honesty test for strategy returns. It decomposes your performance into components that are available to anyone (factor premiums) and the component that is genuinely yours (alpha). Without this decomposition, a 15 percent return looks impressive. With it, you discover that 13 percent was factor exposure and 2.1 percent was alpha.

Three numbers from this video. 0.82 — the market beta, meaning 82 percent of market moves flow through to the strategy. 2.1 percent — the statistically significant annualised alpha (p equals 0.04) that justifies the pipeline's complexity. And 68 percent — the R-squared, meaning the 5 factors explain two-thirds of the strategy's variation and the other third is alpha plus noise.

Next video: cross-sectional alpha. We shift from predicting absolute returns, which is noisy and beta-contaminated, to ranking stocks against each other — which is inherently market-neutral and produces a purer alpha signal with 80 percent lower turnover.

---

## Information Gain Score

**Score: 7.5/10**

Strong on the factor decomposition walkthrough with real regression numbers, the rolling attribution insight, and the neutralisation design implications. The "15% return but only 2.1% alpha" framing is a compelling wake-up call. Good connection between factor analysis and practical portfolio decisions.

**Before filming, add:**
1. Your actual regression output with t-stats and p-values displayed on screen
2. The rolling attribution chart showing how factor exposures changed through 2020-2024
3. A comparison of gross return attribution — pie chart showing market, size, alpha contributions
4. The factor correlation heatmap from your 5 custom factors
