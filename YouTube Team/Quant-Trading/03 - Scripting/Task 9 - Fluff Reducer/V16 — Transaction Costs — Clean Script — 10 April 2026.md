# V16 — Transaction Costs — Clean Script

**Title:** 10 bps Matters: How Commissions + Slippage Kill Backtests
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

[INFORMATION GAIN] On paper: Sharpe 1.2. After realistic costs: Sharpe 0.6. Half your edge gone. The model did not get worse. Your assumptions got honest.

This video shows exactly how to model transaction costs, how turnover converts into annual drag, and what operational changes preserve edge.

---

## SECTION 2 — THE THREE COSTS (2:00–10:00)

1. **Commissions**: explicit broker fee.
2. **Spread/slippage**: implicit cost from execution price vs mid.
3. **Market impact**: your own order moving price.

Retail/medium-size quant systems mostly pay commissions + spread/slippage. Impact is smaller but not zero.

[INFORMATION GAIN] Spread cost is paid twice per round trip: once at entry, once at exit. Many backtests model it once and understate friction by almost 50%.

---

## SECTION 3 — COST FORMULAS (10:00–18:00)

Per-trade cost model:

$$\text{Cost}_{trade} = c_{comm} + c_{slip} + c_{spread}$$

Annual drag approximation:

$$\text{Annual Drag} \approx \text{Turnover} \times \text{Cost per Turnover Unit}$$

Python utility:

```python
def annual_cost_drag(turnover_per_year, cost_bps_per_side=10):
    # bps round-trip: two sides
    round_trip_bps = 2 * cost_bps_per_side
    return turnover_per_year * round_trip_bps / 10000.0

# Example: turnover=10x/year, 10 bps/side
# drag = 10 * 20 / 10000 = 0.02 = 2% annually
```

[INFORMATION GAIN] A 2% annual drag can cut Sharpe dramatically if gross alpha is only 4-6% annualised. Costs scale with activity, not with model quality.

---

## SECTION 4 — COST-AWARE BACKTEST IMPLEMENTATION (18:00–25:00)

```python
pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entries,
    exits=exits,
    fees=0.001,       # 10 bps
    slippage=0.0005,  # 5 bps
    init_cash=100_000
)

gross = pf.returns().add(pf.fees().abs(), fill_value=0)
net = pf.returns()
```

Comparison template:

```python
def compare_cost_scenarios(close, entries, exits):
    scenarios = {
        'no_costs': {'fees': 0.0, 'slippage': 0.0},
        'realistic': {'fees': 0.001, 'slippage': 0.0005},
        'stress': {'fees': 0.0015, 'slippage': 0.0010}
    }
    out = {}
    for name, cfg in scenarios.items():
        pf = vbt.Portfolio.from_signals(close, entries, exits, **cfg)
        s = pf.stats()
        out[name] = {
            'sharpe': float(s['Sharpe Ratio']),
            'cagr': float(s['CAGR [%]'])
        }
    return out
```

---

## SECTION 5 — TURNOVER AS THE MAIN LEVER (25:00–32:00)

Turnover estimate:

```python
def annual_turnover(weights):
    # weights: DataFrame indexed by date
    daily_rebal = weights.diff().abs().sum(axis=1).fillna(0)
    return daily_rebal.mean() * 252
```

If turnover is too high, even good signals lose net value.

[INFORMATION GAIN] Most edge-preserving cost reduction comes from reducing unnecessary rebalancing, not from broker fee negotiation. Dropping from daily to twice-weekly rebalance can reduce turnover by 30-50% while preserving most directional edge.

---

## SECTION 6 — REDUCTION STRATEGIES (32:00–37:00)

1. **Rebalance less frequently**: daily -> weekly where signal half-life allows.
2. **No-trade bands**: do not trade unless signal change exceeds threshold.
3. **Batch orders**: one execution window/day.
4. **Liquidity filters**: avoid thin names with large spreads.
5. **Limit-order logic for non-urgent trades**.

No-trade band example:

```python
def rebalance_with_band(target_w, current_w, band=0.002):
    delta = target_w - current_w
    trade = np.where(np.abs(delta) > band, delta, 0.0)
    return trade
```

---

## SECTION 7 — CLOSE (37:00–40:00)

Transaction costs are not noise. They are a deterministic tax on activity. If your design ignores them, your backtest is fiction.

Next video: position sizing and risk management. Because even cost-aware strategies still fail without sizing discipline.

---

## Information Gain Score

**Score: 8/10**

This script ties costs to turnover math, gives implementation patterns, and shows where practical cost reduction actually comes from.

**Before filming, add:**
1. Your gross vs net Sharpe table from live backtests
2. Turnover before/after no-trade band
3. One liquidity-stress day example
