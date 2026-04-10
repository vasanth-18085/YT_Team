# V22 — Factor Analysis — Refined Script

**Title:** Fama-French 5-Factor: Where Does Your Edge Actually Come From?
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — HOOK (0:00–2:00)

Your strategy returned 15% annualized. Sounds great.

[INFORMATION GAIN] If 14% of that can be explained by market, size, and value exposures, your true alpha is tiny. Factor analysis tells you what you are actually betting on.

---

## SECTION 2 — WHY FACTOR DECOMPOSITION MATTERS (2:00–8:00)

Without factor decomposition:
- you may mistake beta for alpha
- risk regimes can surprise you
- diversification assumptions are wrong

With decomposition:
- you know exposure sources
- you can hedge specific factors
- you can claim alpha credibly

---

## SECTION 3 — 5-FACTOR MODEL SETUP (8:00–16:00)

Fama-French 5-factor equation:

$$R_t - R_{f,t} = \alpha + \beta_M MKT_t + \beta_S SMB_t + \beta_H HML_t + \beta_R RMW_t + \beta_C CMA_t + \epsilon_t$$

Factors:
- MKT-RF: market
- SMB: size
- HML: value
- RMW: profitability
- CMA: investment

```python
import statsmodels.api as sm

def ff5_regression(strategy_excess, ff_factors_df):
    X = ff_factors_df[['MKT_RF','SMB','HML','RMW','CMA']]
    X = sm.add_constant(X)
    y = strategy_excess
    model = sm.OLS(y, X).fit()
    return model
```

---

## SECTION 4 — INTERPRETING OUTPUT (16:00–24:00)

Key outputs:
- alpha (intercept)
- factor betas
- t-stats / p-values
- $R^2$

Interpretation example:
- $\beta_M = 0.9$ -> strong market dependence
- $\beta_S = 0.3$ -> small-cap tilt
- alpha statistically insignificant -> weak idiosyncratic edge

[INFORMATION GAIN] A high $R^2$ with low alpha is not failure; it means your strategy is mostly factor expression. Decide if that matches your objective.

---

## SECTION 5 — ROLLING FACTOR EXPOSURES (24:00–31:00)

Static betas hide temporal instability.

```python
def rolling_ff5(strategy_excess, ff_df, window=252):
    rows = []
    for i in range(window, len(strategy_excess)):
        y = strategy_excess.iloc[i-window:i]
        X = sm.add_constant(ff_df[['MKT_RF','SMB','HML','RMW','CMA']].iloc[i-window:i])
        res = sm.OLS(y, X).fit()
        rows.append(res.params)
    return pd.DataFrame(rows, index=strategy_excess.index[window:])
```

[INFORMATION GAIN] Many ML strategies show regime-dependent beta drift. A strategy that appears market-neutral in aggregate may become market-long in crises.

---

## SECTION 6 — FROM DIAGNOSIS TO ACTION (31:00–36:00)

If alpha too small:
1. tighten model selection criteria
2. add orthogonal features
3. remove redundant factor-loading signals

If beta too high:
1. hedge with index futures/ETFs
2. introduce beta-neutral position constraints

If factor drift unstable:
1. use rolling exposure controls
2. reduce leverage in unstable windows

---

## SECTION 7 — CLOSE (36:00–40:00)

Factor analysis gives strategic honesty. It tells you whether you built alpha or repackaged common risk premia.

Next video: cross-sectional alpha, where we shift from absolute prediction to relative ranking.

---

## Information Gain Score

**Score: 8/10**

Strong due to concrete regression pipeline, rolling beta logic, and deployment decisions from decomposition.

**Before filming, add:**
1. Your actual FF5 regression table
2. Rolling beta chart for crisis periods
3. Alpha significance result with confidence interval
