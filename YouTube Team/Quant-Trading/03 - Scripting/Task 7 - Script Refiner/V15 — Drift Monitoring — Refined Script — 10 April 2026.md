# V15 — Drift Monitoring — Refined Script

**Title:** 7 Drift Tests for Strategy Decay: When to Pause and Retrain
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

[INFORMATION GAIN] A strategy can go from 75% directional accuracy to 49% without any code change. Same model, same features, same execution engine, suddenly weaker outcomes. That is drift. If you do not monitor it, your strategy becomes a zombie: still trading, still consuming risk, but no longer producing edge.

This video is the drift-monitoring layer I built: seven tests, one decision framework, and automatic actions when enough alarms fire.

---

## SECTION 2 — WHAT DRIFT ACTUALLY IS (2:00–8:00)

Drift is not one thing. There are at least three failure types:

1. **Data drift**: input feature distribution changes from training period.
2. **Concept drift**: relationship between features and target changes.
3. **Execution drift**: same predictions but worse fills, higher costs, or regime mismatch.

[INFORMATION GAIN] Most people only monitor rolling Sharpe and call it drift detection. That misses early warnings. Sharpe is a lagging indicator. By the time rolling Sharpe collapses, real capital damage has already happened. You need distribution-level and structure-level tests to detect decay earlier.

---

## SECTION 3 — TESTS 1 AND 2: DISTRIBUTION SHIFT (8:00–14:00)

### Test 1: Kolmogorov-Smirnov (KS)

```python
from scipy.stats import ks_2samp

def ks_drift_test(train_returns, live_returns, alpha=0.01):
    stat, pval = ks_2samp(train_returns, live_returns)
    return {
        'test': 'KS',
        'stat': float(stat),
        'pval': float(pval),
        'drift': bool(pval < alpha)
    }
```

This compares training-period return distribution to current live-window distribution.

### Test 2: Population Stability Index (PSI)

```python
def population_stability_index(expected, actual, bins=10):
    exp_hist, bin_edges = np.histogram(expected, bins=bins)
    act_hist, _ = np.histogram(actual, bins=bin_edges)

    exp_pct = np.clip(exp_hist / exp_hist.sum(), 1e-6, None)
    act_pct = np.clip(act_hist / act_hist.sum(), 1e-6, None)

    psi = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return psi
```

PSI thresholds:
- < 0.10: stable
- 0.10-0.25: moderate drift
- > 0.25: significant drift

[INFORMATION GAIN] PSI is more operationally useful than KS in production because it gives severity bands, not just reject/not-reject. KS is statistically clean, PSI is operationally interpretable.

---

## SECTION 4 — TESTS 3 AND 4: CUMULATIVE CHANGE + MEMORY (14:00–20:00)

### Test 3: CUSUM change detection

```python
def cusum_test(series, threshold=0.02, drift=0.0):
    pos, neg = 0.0, 0.0
    alarms = []
    for i, x in enumerate(series):
        pos = max(0, pos + x - drift)
        neg = min(0, neg + x + drift)
        if pos > threshold or neg < -threshold:
            alarms.append(i)
            pos, neg = 0.0, 0.0
    return alarms
```

### Test 4: Hurst exponent drift

```python
def hurst_exponent(ts):
    lags = range(2, 20)
    tau = [np.std(np.subtract(ts[lag:], ts[:-lag])) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    return poly[0] * 2.0
```

Interpretation:
- $H < 0.5$: mean-reverting
- $H \approx 0.5$: random walk
- $H > 0.5$: persistent trending

[INFORMATION GAIN] If your strategy is trend-following and Hurst moves from ~0.58 to ~0.48 in the live window, your edge is likely degrading even before PnL fully reflects it.

---

## SECTION 5 — TESTS 5, 6, 7: PERFORMANCE DECAY (20:00–28:00)

### Test 5: Rolling accuracy deterioration

```python
def rolling_accuracy(y_true, y_pred, window=60):
    correct = (np.sign(y_true) == np.sign(y_pred)).astype(int)
    return pd.Series(correct).rolling(window).mean()
```

### Test 6: Rolling Sharpe trend

```python
def rolling_sharpe(returns, window=63):
    mu = pd.Series(returns).rolling(window).mean()
    sig = pd.Series(returns).rolling(window).std()
    return (mu / sig) * np.sqrt(252)
```

### Test 7: Drawdown extension test

```python
def drawdown_extension(equity_curve, expected_max_dd=-0.20):
    running_max = np.maximum.accumulate(equity_curve)
    dd = equity_curve / running_max - 1
    live_max_dd = dd.min()
    return {'live_max_dd': float(live_max_dd),
            'drift': bool(live_max_dd < expected_max_dd)}
```

[INFORMATION GAIN] Drawdown extension catches structural fragility missed by mean metrics. You can have acceptable average return but with much deeper left-tail outcomes than in training. That is drift in risk profile.

---

## SECTION 6 — DECISION ENGINE (28:00–35:00)

```python
def drift_decision_engine(test_results):
    flags = sum(int(r['drift']) for r in test_results)

    if flags >= 5:
        return 'HALT_AND_RETRAIN'
    if flags >= 3:
        return 'REDUCE_RISK_AND_MONITOR'
    return 'CONTINUE'
```

Operational policy:
- **5+ alarms**: halt new trades, retain only risk-reduction exits, retrain.
- **3-4 alarms**: reduce gross exposure by 50%, tighter risk limits.
- **0-2 alarms**: continue.

[INFORMATION GAIN] Binary stop/go policies are brittle. Tiered response works better: first reduce risk, then halt only when multiple independent tests align.

---

## SECTION 7 — RETRAIN WORKFLOW (35:00–38:00)

When halt triggers:
1. Freeze trading entries.
2. Snapshot live model + config + feature pipeline version.
3. Retrain on most recent validated window.
4. Re-run walk-forward + cost-aware backtest.
5. Only redeploy if post-retrain metrics pass thresholds.

Threshold example:
- Sharpe > 0.7
- Max DD > -22%
- Fold Sharpe std < 0.2

---

## SECTION 8 — CLOSE (38:00–40:00)

Drift monitoring keeps you from confusing historical edge with current edge. It is not a nice-to-have dashboard. It is production survival.

Next video: transaction costs and market impact. Because even a non-drifting strategy can die from friction if you overtrade.

---

## Information Gain Score

**Score: 8/10**

This script gives a practical multi-test architecture, explicit thresholds, and action mapping beyond generic "watch your Sharpe" advice.

**Before filming, add:**
1. A real incident where 5+ alarms triggered
2. Your exact per-test thresholds from your logs
3. A timeline chart showing alarms leading PnL deterioration
