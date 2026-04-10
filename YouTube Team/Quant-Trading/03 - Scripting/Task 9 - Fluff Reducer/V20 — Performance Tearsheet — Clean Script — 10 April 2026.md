# V20 — Performance Tearsheet — Clean Script

**Title:** How to Present Strategy Results Like a Quant Team
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — HOOK (0:00–2:00)

A pretty equity curve is not a performance report.

[INFORMATION GAIN] Professional decisions require a tearsheet: return, risk, stability, drawdown structure, turnover, and cost drag in one coherent view.

---

## SECTION 2 — TEARSHEET BLUEPRINT (2:00–10:00)

Core sections:
1. Summary metrics panel
2. Equity and drawdown curves
3. Rolling metrics (Sharpe/vol/beta)
4. Monthly heatmap
5. Trade and turnover diagnostics
6. Cost attribution panel

Why this structure:
- summary for quick triage
- curves for temporal behavior
- rolling stats for stability
- diagnostics for implementation quality

---

## SECTION 3 — SUMMARY METRICS THAT MATTER (10:00–18:00)

Essential metrics:
- CAGR
- Annualized Vol
- Sharpe
- Sortino
- Calmar
- Max Drawdown
- Win Rate
- Avg Win / Avg Loss

```python
def summary_metrics(returns):
    ann_ret = (1 + returns).prod() ** (252 / len(returns)) - 1
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
    return {
        'cagr': float(ann_ret),
        'ann_vol': float(ann_vol),
        'sharpe': float(sharpe)
    }
```

[INFORMATION GAIN] A high Sharpe with severe max drawdown duration can still be unacceptable operationally. Duration matters alongside depth.

---

## SECTION 4 — EQUITY + DRAWDOWN PANELS (18:00–24:00)

```python
def drawdown_series(equity):
    peak = equity.cummax()
    dd = equity / peak - 1
    return dd
```

Plot requirements:
- equity with regime markers
- drawdown depth and duration bands
- annotate top-3 drawdown events

[INFORMATION GAIN] Drawdown duration often predicts strategy abandonment risk better than drawdown depth. Teams can tolerate sharp recoverable drops more than long stagnation.

---

## SECTION 5 — ROLLING STABILITY (24:00–30:00)

Rolling windows:
- 3-month Sharpe
- 1-year Sharpe
- rolling volatility

```python
def rolling_sharpe(returns, window=252):
    mu = returns.rolling(window).mean()
    sig = returns.rolling(window).std()
    return (mu / sig) * np.sqrt(252)
```

Interpretation:
- stable positive rolling Sharpe -> robust
- sign-flipping rolling Sharpe -> fragile

---

## SECTION 6 — MONTHLY HEATMAP + SEASONALITY (30:00–34:00)

Monthly returns matrix reveals:
- consistency
- clustered bad periods
- quarter effects

[INFORMATION GAIN] Heatmaps reveal risk concentration in time better than averages. A strategy that looks fine annually may hide repeated Q3 stress.

---

## SECTION 7 — TURNOVER AND COST ATTRIBUTION (34:00–38:00)

Track:
- gross vs net return
- annual turnover
- cost drag decomposition

```python
def cost_drag(gross, net):
    return float((gross - net).sum())
```

Report panel example:
- Gross CAGR: 12.5%
- Net CAGR: 10.9%
- Annual cost drag: 1.6%
- Turnover: 7.8x/year

---

## SECTION 8 — CLOSE (38:00–40:00)

A strong tearsheet prevents bad deployment decisions. It turns performance into an auditable risk-return story.

Next video: experiment tracking and research journals, so every result in the tearsheet is reproducible.

---

## Information Gain Score

**Score: 8/10**

High value from decision-oriented panel design and stability-first interpretation.

**Before filming, add:**
1. Your actual tearsheet screenshot
2. Three annotated drawdown events
3. Gross vs net attribution from your live pipeline
