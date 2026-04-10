# V19 — Deflated Sharpe & PBO — Clean Script

**Title:** Is Your Backtest Real or Luck? Deflated Sharpe and PBO
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — HOOK (0:00–2:00)

Your backtest Sharpe is 2.0. Live Sharpe becomes 0.5. What happened?

[INFORMATION GAIN] Selection bias and overfitting inflated your in-sample score. Deflated Sharpe and PBO quantify how much of that score is likely luck.

---

## SECTION 2 — WHY RAW SHARPE MISLEADS (2:00–10:00)

Raw Sharpe ignores:
- number of models/hyperparameters tried
- non-normal return distribution
- serial correlation
- selection process bias

If you try many variants and report the best Sharpe, expected max Sharpe from luck grows with search breadth.

Approximate expected maximum Sharpe from noise among $N$ trials:

$$E[\max(SR)] \approx \sqrt{2\log N} - \frac{\gamma}{2\sqrt{2\log N}}$$

where $\gamma$ is Euler-Mascheroni constant.

---

## SECTION 3 — DEFLATED SHARPE RATIO (10:00–20:00)

Conceptually:

$$DSR = SR_{observed} - SR_{luck\ baseline}$$

In practice, DSR implementations include skew/kurtosis and finite-sample effects.

```python
def deflated_sharpe(observed_sr, n_trials, luck_baseline):
    return observed_sr - luck_baseline

# Example
observed = 1.20
luck = 0.60
dsr = deflated_sharpe(observed, 14, luck)  # 0.60
```

[INFORMATION GAIN] A Sharpe of 1.2 sounds excellent. A deflated Sharpe of 0.6 is still decent, but much less magical. DSR gives a reality-adjusted lens.

---

## SECTION 4 — PROBABILITY OF BACKTEST OVERFITTING (PBO) (20:00–30:00)

PBO asks: how often does the model that looks best in-sample rank poorly out-of-sample?

Framework:
1. Split history into many train/test partitions.
2. For each split, rank models in-sample.
3. Observe out-of-sample rank of in-sample winner.
4. PBO = fraction where winner lands in poor OOS quantiles.

```python
def pbo_score(is_ranks, oos_ranks, threshold_quantile=0.5):
    # is_ranks/oos_ranks: lower rank = better
    bad = 0
    total = len(is_ranks)
    for is_best, oos_rank in zip(is_ranks, oos_ranks):
        if is_best == 1 and oos_rank > threshold_quantile:
            bad += 1
    return bad / max(total, 1)
```

Example:
- PBO = 0.35 means in 35% of splits, in-sample winner does poorly out-of-sample.

[INFORMATION GAIN] PBO is intuitive for decision-making. Teams understand "35% chance the selected model is overfit" faster than they understand asymptotic p-value arguments.

---

## SECTION 5 — MINIMUM BACKTEST LENGTH (MinBTL) (30:00–34:00)

MinBTL estimates how much history is needed for statistically reliable inference given turnover, Sharpe, and noise level.

Rule-of-thumb interpretation:
- If MinBTL is 8 years and you have 5 years, confidence is weak.
- If you have 10+ years, confidence improves materially.

```python
def min_backtest_length(required_years, available_years):
    return {
        'required': required_years,
        'available': available_years,
        'sufficient': available_years >= required_years
    }
```

---

## SECTION 6 — APPLIED TO THIS PIPELINE (34:00–38:00)

Illustrative outputs:
- Observed Sharpe: 1.20
- Deflated Sharpe: 0.60
- PBO: 0.35
- MinBTL: 8 years
- Available data: 10 years

Interpretation:
- edge exists, but less than headline Sharpe implies
- overfitting risk is non-trivial
- sample length is adequate but not huge margin

[INFORMATION GAIN] This is the point: DSR/PBO do not "kill" your strategy. They calibrate your confidence so you size risk appropriately.

---

## SECTION 7 — CLOSE (38:00–40:00)

Deflated Sharpe and PBO force honesty. They turn "this looks great" into "how much of this is probably real?"

Next video: professional tearsheets and reporting so decisions are made on complete risk-return context, not one metric.

---

## Information Gain Score

**Score: 8/10**

Strong because it operationalizes selection-bias adjustment and gives actionable interpretation rules.

**Before filming, add:**
1. Your exact DSR and PBO outputs from current model set
2. A chart comparing raw vs deflated Sharpe across models
3. MinBTL assumptions used in your calculation
