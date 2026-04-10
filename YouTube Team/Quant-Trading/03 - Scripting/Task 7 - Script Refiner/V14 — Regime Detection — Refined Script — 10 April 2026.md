# V14 — Regime Detection — Refined Script

**Title:** HMM-Based Regime Detection: Bull, Bear, and Crash Modes
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

[INFORMATION GAIN] Markets are not stationary. The same signal that works in a low-volatility bull market can fail instantly in a crash regime. I built a regime detector using a Hidden Markov Model that classifies market state into three regimes: Bull, Bear, and Crash. Then I adapt leverage and position sizing based on regime probability. The result is lower drawdowns without sacrificing too much upside.

---

## SECTION 2 — WHY REGIME DETECTION IS ESSENTIAL (2:00–6:00)

Most quant pipelines assume one stable data-generating process. That assumption is wrong for markets.

In bull regimes:
- Trend-following works
- Momentum persists
- Correlations are moderate

In bear regimes:
- Mean reversion often outperforms
- Negative drift dominates
- Correlations rise

In crash regimes:
- Correlations approach 1
- Volatility spikes nonlinearly
- Liquidity collapses

[INFORMATION GAIN] The biggest model risk is regime mismatch, not parameter mismatch. A well-tuned model in the wrong regime is worse than a simple model in the right regime. Regime detection is a meta-layer that chooses how aggressively to trust the base signal.

---

## SECTION 3 — HMM ARCHITECTURE (6:00–20:00)

```python
import numpy as np
from hmmlearn.hmm import GaussianHMM

# Features designed for regime separation
# 1) rolling return, 2) rolling volatility, 3) rolling market correlation
features = np.column_stack([
    returns.rolling(20).mean().fillna(0),
    returns.rolling(20).std().fillna(0),
    stock_to_index_corr.rolling(20).mean().fillna(0)
])

model = GaussianHMM(
    n_components=3,
    covariance_type='full',
    n_iter=1000,
    random_state=42
)
model.fit(features)

regimes = model.predict(features)           # Hard labels: 0,1,2
regime_probs = model.predict_proba(features) # Soft probabilities per regime
```

Why HMM:
- Hidden state model: regime is latent, not directly observed
- Transition matrix: estimates how likely the market is to remain in current regime vs switch
- Probabilistic outputs: you get confidence in each regime, not just hard classification

[INFORMATION GAIN] Transition probabilities are as valuable as regime labels. If crash-regime probability is only 15% but the transition probability from bear to crash has risen sharply, this is an early warning signal before the hard crash label is assigned. I use probability thresholds for gradual risk reduction rather than waiting for hard regime switches.

---

## SECTION 4 — INTERPRETING THE THREE REGIMES (20:00–28:00)

After fitting, map numeric states to semantic regimes by their feature means:

```python
def map_states_to_regimes(model, features):
    state_means = []
    for state in range(model.n_components):
        mask = (model.predict(features) == state)
        mean_ret = features[mask, 0].mean()
        mean_vol = features[mask, 1].mean()
        mean_corr = features[mask, 2].mean()
        state_means.append((state, mean_ret, mean_vol, mean_corr))

    # Heuristic mapping
    # Bull: highest return, moderate vol
    # Crash: lowest return, highest vol/corr
    # Bear: remaining state
    return state_means
```

Typical mapping from my runs:
- **Bull:** positive mean return, moderate vol, moderate correlation
- **Bear:** negative mean return, moderate-high vol
- **Crash:** strongly negative return, highest vol, highest correlation

[INFORMATION GAIN] Crash regimes are rare, which creates class imbalance in hidden-state estimation. If your training period has too few crash examples, HMM may merge bear and crash into one state. The fix is longer training windows and feature scaling that amplifies high-vol/high-correlation joint events.

---

## SECTION 5 — ADAPTIVE POSITION SIZING (28:00–36:00)

```python
def adaptive_position_size(signal_strength, confidence, regime_probs):
    # Base risk budget per position
    base = 0.01

    p_bull = regime_probs[0]
    p_bear = regime_probs[1]
    p_crash = regime_probs[2]

    # Smooth leverage multiplier from probabilities
    leverage = 1.5 * p_bull + 0.7 * p_bear + 0.2 * p_crash

    size = base * signal_strength * confidence * leverage
    return max(0.0, min(size, 0.03))  # clamp to 3% max per position
```

This is probability-weighted sizing, not hard-switch sizing. If crash probability rises from 5% to 30%, position sizes already shrink even before full crash classification.

Expected impact:
- Bull regimes: capture upside with moderate leverage
- Bear regimes: reduce risk and rely on higher-confidence signals only
- Crash regimes: preserve capital, minimal risk exposure

[INFORMATION GAIN] Drawdown reduction from regime-aware sizing often comes more from avoided overexposure than from better entry timing. You do not need perfect crash prediction. You need earlier risk reduction than your non-regime baseline.

---

## SECTION 6 — THE CLOSE (36:00–40:00)

Regime detection adds state-awareness to the whole system. Same signals, same models, but different risk posture based on current market mode. This is how you survive structural shifts.

Next video: drift monitoring. Even with regime detection, models decay. We add seven statistical tests to detect when the strategy's edge is degrading and trigger retraining before losses compound.

---

## Information Gain Score

**Score: 7/10**

The transition-probability use, crash-state class imbalance caution, and probability-weighted leverage logic provide strong practical value.

**Before filming, add:**
1. Your fitted transition matrix and how often regime switches occur
2. A chart of regime probabilities through 2020 crash period
3. Your measured drawdown improvement with regime adaptation
