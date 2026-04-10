# V23 — Cross-Sectional Alpha — Final Script

**Title:** From Time-Series Prediction to Cross-Sectional Ranking
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — HOOK (0:00–2:00)

Time-series question: "Will AAPL go up tomorrow?"
Cross-sectional question: "Will AAPL outperform other stocks?"

[INFORMATION GAIN] Cross-sectional ranking is often more stable than absolute return prediction because dispersion is easier to forecast than market direction.

---


[CTA 1]
By the way, if you want the full MLQuant build resources in one place, I put together a free starter pack with the repo map, workflow checklist, and implementation notes. It is built for this exact stage of the journey. Grab it here: [INSERT PRIMARY LINK]

## SECTION 2 — CORE SHIFT IN PROBLEM FORMULATION (2:00–9:00)

Time-series model output:
- signed return forecast per stock

Cross-sectional pipeline:
1. score all stocks on same date
2. rank scores
3. long top quantile, short bottom quantile
4. hold fixed horizon (e.g., 5 days)

This naturally reduces market beta and focuses on relative edge.

---

## SECTION 3 — RANKING ENGINE (9:00–18:00)

```python
def rank_signals(score_df, date_col='date', ticker_col='ticker', score_col='score'):
    out = score_df.copy()
    out['rank'] = out.groupby(date_col)[score_col].rank(ascending=False, method='first')
    out['pct_rank'] = out.groupby(date_col)[score_col].rank(pct=True, ascending=False)
    return out
```

Portfolio construction:

```python
def long_short_baskets(ranked_df, top_q=0.1, bot_q=0.1):
    long_df = ranked_df[ranked_df['pct_rank'] <= top_q]
    short_df = ranked_df[ranked_df['pct_rank'] >= 1-bot_q]
    return long_df, short_df
```

[INFORMATION GAIN] Ranking transforms scale-sensitive prediction errors into order-sensitive decisions. Even if predicted returns are miscalibrated in magnitude, ordering can remain useful.

---

## SECTION 4 — HOLDING HORIZON & REBALANCING (18:00–26:00)

Test horizons: 1, 3, 5, 10 days.

Trade-off:
- shorter hold -> fresher signal, higher turnover
- longer hold -> lower turnover, possible decay

```python
def rebalance_dates(index, step=5):
    return index[::step]
```

[INFORMATION GAIN] In many equity universes, 5-day holds capture most ranking signal while cutting turnover sharply versus daily rebalance.

---

## SECTION 5 — EVALUATION METRICS FOR CROSS-SECTIONAL SYSTEMS (26:00–33:00)

1. long-short spread return
2. hit rate of top decile vs bottom decile
3. Information Coefficient (IC)
4. rank IC stability

```python
def daily_ic(pred_scores, realized_returns):
    return pred_scores.corr(realized_returns, method='spearman')
```

Monitor:
- mean IC
- IC std
- IC hit rate (% days IC > 0)

---

## SECTION 6 — RISK CONTROLS (33:00–37:00)

1. sector neutrality constraints
2. beta neutrality at portfolio level
3. liquidity constraints
4. max weight per name

```python
def cap_weights(w, cap=0.03):
    w = w.clip(upper=cap)
    return w / w.sum()
```

[INFORMATION GAIN] Without neutrality constraints, cross-sectional portfolios can quietly become sector bets.

---


[CTA 2]
Quick reminder before we continue, if this is helping you, the free MLQuant starter pack is in the description and it goes deeper than what we can fit in one video. Link: [INSERT PRIMARY LINK]

## SECTION 7 — CLOSE (37:00–40:00)

Cross-sectional alpha reframes prediction into ranking, often improving robustness and cost efficiency.

Next video: live backtester and paper-trading bridge to production.

---

## Information Gain Score

**Score: 8/10**

Strong on practical ranking conversion, horizon trade-off framing, and IC-based monitoring.

**Before filming, add:**
1. Your decile spread chart
2. IC time series and hit rate
3. Turnover comparison by rebalance horizon
