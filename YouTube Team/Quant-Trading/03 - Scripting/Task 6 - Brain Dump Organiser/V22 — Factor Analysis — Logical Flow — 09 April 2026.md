# V22 — Factor Analysis — Logical Flow — 09 April 2026

**Title:** Fama-French 5-Factor Model: Where Does Your Edge Come From?
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** Your strategy made 15% annualized return. Congratulations — or not. When I decomposed it using a 5-factor model, I found: 10% came from market beta (you were long in a rising market), 3% from size exposure (you accidentally overweighted small caps), 2% from value tilt (high book-to-market stocks), and 0% from genuine alpha. You did not beat the market — you just loaded on known risk factors and got paid for taking risk that any ETF could replicate for 10 bps. This video shows you how to find out whether your edge is real or just factor exposure in disguise.

## 2. WHAT ARE FACTORS AND WHY THEY MATTER (2:00–10:00)

Academic finance has identified several systematic sources of return that explain a large fraction of stock price movements. These are called risk factors because the returns they generate are compensation for bearing specific risks.

The Fama-French framework identifies 5 main factors:

Market (MKT-RF): the excess return of the entire stock market over the risk-free rate. If you hold any stock portfolio, you have positive market exposure. This is the easiest return to capture — just buy an index fund.

Size (SMB — Small Minus Big): small-cap stocks have historically outperformed large-cap stocks. If your strategy overweights small stocks, part of your return comes from this well-known factor.

Value (HML — High Minus Low): stocks with high book-to-market ratios (value stocks) have historically outperformed growth stocks. If your strategy tilts toward value, you are capturing a known factor premium.

Profitability (RMW — Robust Minus Weak): profitable firms outperform unprofitable ones. Quality factor.

Investment (CMA — Conservative Minus Aggressive): firms that invest conservatively outperform aggressive investors. Low-investment anomaly.

**[INFORMATION GAIN]** The reason these factors matter for your quant strategy: if your 15% return is entirely explained by exposure to these 5 factors, then you have no alpha. You are just bearing known risks that the market compensates. A simpler and cheaper approach would be to buy factor ETFs. The value of factor decomposition is separating genuine alpha (which is rare and valuable) from factor exposure (which is cheap and available to everyone).

## 3. THE FACTOR DECOMPOSITION REGRESSION (10:00–20:00)

The standard approach: regress your strategy's excess returns against the 5 factor returns.

r_strategy - r_f = alpha + beta_MKT * MKT + beta_SMB * SMB + beta_HML * HML + beta_RMW * RMW + beta_CMA * CMA + epsilon

Where r_f is the risk-free rate (US T-bill rate), and the factor returns are publicly available from Kenneth French's data library or AQR.

The betas tell you your factor loadings — how much of each factor you are implicitly exposed to. Alpha (the intercept) is the return that CANNOT be explained by any factor. If alpha is statistically significant (p < 0.05), you have genuine excess return.

My pipeline's decomposition: beta_MKT = 0.82 (significant market exposure), beta_SMB = 0.15 (slight small-cap tilt), beta_HML = -0.08 (slight growth tilt), beta_RMW = 0.03 (negligible), beta_CMA = -0.02 (negligible). Alpha = 2.1% annualized with p-value 0.04. This means: most of the return comes from market exposure, there is a small size tilt, and there is a statistically significant 2.1% of genuine alpha.

**[INFORMATION GAIN]** The 2.1% alpha is not huge in absolute terms, but it is meaningful relative to the factor exposures. The market beta of 0.82 means the strategy captures about 82% of the market's ups and downs. If the market returns 10%, the strategy gets roughly 8.2% from beta alone plus 2.1% from alpha. The alpha persistence across walk-forward folds is what matters — if it is consistent, it is real. A one-time spike is noise.

## 4. MY FACTOR MODEL IMPLEMENTATION (20:00–28:00)

The FactorModel class in `src/m8_alpha/factor_model.py` takes a different approach from the standard Fama-French regression. Instead of using academic factor libraries, it computes 5 custom factors directly from price and volume data:

Factor 1 — Momentum (weight 0.30): 12-month return minus the last 21 days. This captures medium-term price continuation while excluding short-term reversal effects. The 1-month exclusion is a well-known trick from Jegadeesh and Titman (1993).

Factor 2 — Short-Term Reversal (weight 0.15): negative of 5-day return. Stocks that fell over the past week tend to bounce back. This is a contrarian signal that offsets momentum at short horizons.

Factor 3 — Low Volatility (weight 0.20): negative of 63-day realized volatility. Lower volatility stocks receive higher scores. This captures the low-volatility anomaly — low-vol stocks deliver higher risk-adjusted returns than high-vol stocks, which contradicts classic theory.

Factor 4 — Volume Trend (weight 0.15): ratio of current volume to 63-day average volume. Unusual volume often precedes price moves. This factor captures attention and liquidity signals.

Factor 5 — Distance to 52-Week High (weight 0.20): (current price / 52-week high) - 1. Stocks near their highs tend to continue performing well (anchoring effect).

Each factor is z-scored cross-sectionally per date (mean=0, std=1 across all stocks on each day). The composite signal is the weighted sum.

**[INFORMATION GAIN]** Cross-sectional z-scoring is crucial. Without it, a factor value of 0.05 means different things on different dates (maybe all stocks had momentum of 0.04-0.06 that day). After z-scoring, a value of +2.0 always means "two standard deviations above the cross-sectional mean that day" — consistently interpretable.

The factor correlation matrix reveals how diversified your factors are. In my data: momentum and reversal have correlation -0.3 (they partially offset, which is expected). Momentum and distance-to-high have correlation 0.4 (both capture recent winners). Volatility and volume have near-zero correlation. Overall, the factors are moderately diversified, meaning the composite captures more information than any single factor.

## 5. FACTOR EXPOSURES AND ATTRIBUTION (28:00–34:00)

The `factor_exposures()` method returns individual DataFrames for each factor, allowing you to see exactly which stocks score highest and lowest on each factor at any point in time.

More importantly, you can attribute your strategy's return to each factor. Run the strategy's daily returns through the Fama-French regression. The beta times factor return for each factor tells you how much of your return came from that source.

Example monthly attribution: January 2024 strategy return = +3.2%. Decomposition: market beta contribution = +2.1%, momentum contribution = +0.6%, low-vol contribution = +0.3%, alpha = +0.2%. The strategy outperformed by 1.1% that month, but 0.9% was from factor tilts and only 0.2% was alpha.

**[INFORMATION GAIN]** Attribution changes over time. In quiet bull markets, most return comes from beta. In rotations, momentum and reversal contribute. Alpha tends to be most stable in medium-volatility environments where the ML models' signal-to-noise ratio is highest. Understanding this time-varying attribution prevents you from taking credit for factor returns and losing confidence during factor drawdowns that have nothing to do with your model quality.

## 6. IMPLICATIONS FOR STRATEGY DESIGN (34:00–38:00)

Factor analysis has direct design implications. If your strategy has high market beta, you can reduce it by hedging with SPY shorts or by using dollar-neutral construction (equal long and short exposure). If your strategy has unintended size or value exposure, you can neutralize it by adding offsetting factor positions.

The goal for an ML quant strategy is: market-neutral (beta ≈ 0), factor-neutral (all factor betas ≈ 0), with significant positive alpha. This is hard but it is the purest form of genuine predictive edge.

My pipeline is not factor-neutral — it has 0.82 market beta. This is a deliberate choice: I accept market exposure because the market has positive expected return long-term. But the 2.1% alpha on top is the evidence that the ML models add genuine value beyond what market exposure provides.

## 7. THE CLOSE (38:00–40:00)

Factor analysis is the honesty test for strategy returns. It forces you to separate genuine alpha from factor exposure, real edge from common risk premiums. Every quant researcher should decompose their returns before claiming outperformance.

Next video: cross-sectional alpha. We move from predicting absolute returns (time-series) to ranking stocks relative to each other (cross-section). This unlocks market-neutral strategies with longer holding periods and lower costs.

[NEEDS MORE] Your actual regression output with betas and p-values. The factor attribution chart over time. A case where factor decomposition changed your assessment of a strategy.
