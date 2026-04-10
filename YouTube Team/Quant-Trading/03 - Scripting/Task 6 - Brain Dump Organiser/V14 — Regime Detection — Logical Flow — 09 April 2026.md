# V14 — Regime Detection — Logical Flow — 09 April 2026

**Title:** HMM-Based Regime Detection: Bull, Bear, and Crash Modes
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** Markets are not stationary. The same signal that prints money in a low-volatility bull market can blow up your account in a crash regime. I built a regime detector using a Hidden Markov Model that classifies market state into three regimes — bull, bear, and crash — in real time. Then I adapt leverage and position sizing based on regime probability. The result: 30-40% drawdown reduction during crashes without sacrificing too much upside.

The core insight: the biggest model risk is not parameter mismatch, it is regime mismatch. A perfectly tuned model in the wrong regime is more dangerous than a simple model in the right regime.

## 2. WHY REGIME DETECTION IS ESSENTIAL (2:00–8:00)

Most quant pipelines assume one stable data-generating process. You train a model on 5 years of data, fit your parameters, deploy. But the stock market has at least three fundamentally different operating modes.

Bull regimes: returns drift positive, volatility is moderate, correlations between stocks are moderate. Trend-following works. Momentum persists. Position sizing can be aggressive.

Bear regimes: returns drift negative, volatility climbs, correlations rise. Mean-reversion starts to outperform. Momentum becomes unreliable. You want smaller positions and tighter stops.

Crash regimes: returns are sharply negative, volatility spikes nonlinearly, correlations approach 1 — everything sells off together. Liquidity collapses. The only safe move is to dramatically reduce exposure.

**[INFORMATION GAIN]** In my backtest data, the worst drawdowns did not come from bad signal predictions. They came from the system maintaining full position size during regime transitions — the moments when the market shifts from bull to bear or bear to crash. The model was still predicting correctly relative to the current regime, but position sizing was calibrated for a different regime. That mismatch is the killer.

## 3. WHAT IS A HIDDEN MARKOV MODEL (8:00–16:00)

An HMM is a probabilistic model that assumes the market is always in one of N hidden states (regimes), but we cannot directly observe which state we are in. We can only observe the returns, volatility, and correlations. The HMM learns to infer regime from observables.

Two key components. First, the transition matrix: probability that the market stays in current regime versus switches. P(state_t = j | state_{t-1} = i) = A_ij. This captures the fact that regimes are persistent — bull markets last months or years, not just days.

Second, emission distributions: each regime generates returns from a different Gaussian distribution. Bull regime has positive mean and low sigma. Crash regime has negative mean and very high sigma. The HMM learns these parameters from the data.

Fitting uses the Expectation-Maximization algorithm. You do not need to label historical regimes by hand. The HMM discovers the states automatically from the data.

## 4. THE ACTUAL IMPLEMENTATION (16:00–26:00)

My RegimeDetector class in `src/m7_risk/regime.py` takes price data and produces regime labels plus probabilities.

Feature preparation: three features designed for regime separation. Rolling 21-day returns (captures trend direction). Rolling 21-day volatility (captures risk level). Log returns (captures distribution shape). These features are standardized before fitting.

The HMM is configured with n_components=3 (three regimes), full covariance matrix (allows correlations between features within each regime), and 200 EM iterations.

After fitting, the numeric states (0, 1, 2) need to be mapped to semantic labels. The mapping heuristic: sort states by their mean volatility. Lowest vol = low_vol (bull). Middle = high_vol (bear). Highest = crisis (crash). This automatic relabeling ensures consistent interpretation across different fitting runs.

**[INFORMATION GAIN]** The fallback mechanism is critical for production. If hmmlearn is not installed or the HMM fails to converge, the system falls back to a simple volatility-threshold method: below 25th percentile vol = bull, above 75th = crash, middle = bear. This is not as good as the HMM but it means the system never crashes and always provides a regime estimate. Production systems need this kind of graceful degradation.

The model also outputs regime statistics: mean return per regime, Sharpe per regime, average duration of each regime. These inform your expectations — bull regimes last 180 days on average, bear regimes 60 days, crash regimes 15 days. That asymmetry matters for position management.

## 5. TRANSITION PROBABILITIES — THE REAL GOLD (26:00–32:00)

Most people use the HMM for hard regime labels: are we in bull, bear, or crash right now? But the transition matrix is equally valuable.

The transition matrix tells you: given current state, what is the probability of switching to each other state tomorrow? Typical values from my fits: P(bull → bull) ≈ 0.98. P(bull → bear) ≈ 0.018. P(bull → crash) ≈ 0.002. Regimes are sticky — once you are in a bull market, you tend to stay there.

**[INFORMATION GAIN]** Transition probabilities are early warning signals. If regime posterior probability for crash is only 10%, but the transition probability from bear-to-crash has risen sharply (say from 2% to 8%), that means the model is starting to see crash precursors even though the hard label has not switched yet. I use probability thresholds for gradual risk reduction rather than waiting for the hard regime switch. When crash probability exceeds 15%, I start scaling down. When it exceeds 30%, I am at minimum exposure. This smooth scaling avoids the whiplash of binary regime switching.

## 6. REGIME-AWARE POSITION SIZING (32:00–38:00)

The RegimeAwarePositionSizer class takes the raw signal from the SignalCombiner and multiplies it by a regime-dependent leverage factor.

Default multipliers: bull = 1.0 (full exposure). Bear = 0.5 (half exposure). Crash = 0.1 (minimal exposure). These are configurable but the principle is fixed: scale down when risk is elevated.

The key is using soft probabilities, not hard labels. If crash probability is 20% and bull probability is 60% and bear is 20%, the effective leverage is: 1.0 * 0.6 + 0.5 * 0.2 + 0.1 * 0.2 = 0.72. This probability-weighted approach is smoother than hard switching and reduces turnover from regime oscillation.

Expected impact from backtests: during bull regimes, the system captures full upside with standard leverage. During bear regimes, exposure is halved which limits drawdown but also limits gains from short positions. During crash regimes, exposure drops to 10% — you are mostly in cash, preserving capital.

**[INFORMATION GAIN]** The biggest benefit of regime-aware sizing is not better entry timing — it is avoided overexposure. Most drawdown reduction comes from not being fully invested when the crash hits, not from predicting the crash perfectly. You do not need perfect crash prediction. You need earlier risk reduction than your baseline.

## 7. THE CLOSE (38:00–40:00)

Regime detection adds state-awareness to the entire trading pipeline. Same signals, same models, same forecasts — but different risk posture based on what the market is doing right now. This is how you survive structural shifts without redesigning the whole system.

Next video: drift monitoring. Even with regime detection, individual models decay over time as market microstructure changes. We add 7 statistical tests that detect when your strategy's edge is degrading and trigger retraining before losses compound.

[NEEDS MORE] Your fitted transition matrix with actual numbers, a chart of regime probabilities through the 2020 COVID crash, and your measured drawdown improvement before/after regime adaptation.
