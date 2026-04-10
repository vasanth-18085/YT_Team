# V11 — Volatility Estimation: 3 Models from GARCH to LSTM — Logical Flow

**Title:** "Predicting Volatility: Why GARCH Fails (And What Works Better)"
**Length:** ~40 min
**Date:** 09 April 2026

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** "Volatility forecasts drive position sizing. Underestimate vol = blown account. Overestimate = missed profits. I tested 3 approaches: GARCH (the 30-year-old standard), GARCHModel hybrid, and LSTM-Vol. Spoiler: the 30-year-old model still works best most of the time, but there are specific periods where it fails catastrophically."

---

## 2. WHY VOLATILITY MATTERS (2:00–6:00)

- Position sizing: higher vol → smaller positions
- Stop-loss placement: higher vol → wider stops
- Risk budgeting: vol is the denominator

---

## 3. VOLATILITY MODEL 1: GARCH (6:00–14:00)

"Generalized Autoregressive Conditional Heteroskedasticity. 1986 Nobel Prize. Still used."

```python
from arch import arch_model

class GARCHVolatility:
    def fit(self, returns):
        # GARCH(1,1): most common
        model = arch_model(returns, vol='Garch', p=1, q=1)
        result = model.fit(disp='off')
        return result
    
    def forecast_vol(self, horizon=10):
        # Forecast volatility 10 days ahead
        return result.forecast(horizon=horizon)
```

**Math:**
```
σ_t^2 = ω + α·ε_{t-1}^2 + β·σ_{t-1}^2
```
- ω: long-run variance
- α: weight on recent shocks
- β: weight on recent vol (momentum)

**[INFORMATION GAIN]** "GARCH assumes vol reverts to a constant mean. During normal times: accurate. During crises (2008, COVID): fails – vol doesn't revert, it explodes."

### GARCH strengths & weaknesses

**Strengths:**
- Fast (fits in seconds)
- Interpretable (α + β tells you vol memory length)
- Proven (30+ years)
- Hyperparameter-free (auto ARMA model selection)

**Weaknesses:**
- Assumes normal distribution (stock returns have fat tails)
- Vol doesn't revert (fails in crashes)
- Can't use external features (only returns)

---

## 4. VOLATILITY MODEL 2: GARCH + LightGBM Hybrid (14:00–22:00)

"GARCH gives baseline vol. Machine learning improves it with market regime features."

```python
class HybridGARCHLGB:
    def __init__(self):
        self.garch_model = arch_model(returns, vol='Garch', p=1, q=1)
        self.lgb_model = LGBMRegressor()
    
    def fit(self, returns, regime_features=None):
        # Step 1: Get GARCH predictions
        garch_result = self.garch_model.fit(disp='off')
        garch_variance = garch_result.conditional_volatility
        
        # Step 2: LightGBM learns residuals
        # garch_variance over/under estimates actual vol?
        actual_vol = returns.rolling(21).std()
        residuals = actual_vol - garch_variance
        
        # regex features: regime indicators, market-wide metrics, etc.
        self.lgb_model.fit(regime_features, residuals)
    
    def forecast_vol(self, horizon, regime_features_future):
        garch_vol = self.garch_model.get_forecast().variance
        lgb_adjustment = self.lgb_model.predict(regime_features_future)
        hybrid_vol = garch_vol + lgb_adjustment
        return np.sqrt(hybrid_vol)
```

**Regime features (external data):**
```python
regime_features = {
    'vix': vix_index,  # Market fear gauge
    'trend': market_trend,  # Bull or bear?
    'liquidity': bid_ask_spread,  # Liquidity stress?
    'correlation': stock_to_market_correlation,  # Systemic risk?
}
```

**Results:**
- GARCH alone: MAE = 0.25% (volatility estimate error)
- GARCH + LGB: MAE = 0.18% (28% improvement)
- Improvement during crises: 40-50% better

---

## 5. VOLATILITY MODEL 3: LSTM-Vol (22:00–30:00)

"LSTM sees 60 days of returns, predicts next day's volatility."

```python
class LSTMVolatility:
    def __init__(self, hidden_size=32):
        self.model = nn.Sequential(
            nn.LSTM(input_size=1, hidden_size=hidden_size, num_layers=1, batch_first=True),
            nn.Dense(hidden_size, 1),  # Output: 1 volatility
            nn.Softplus()  # Ensure output > 0
        )
    
    def fit(self, returns_windows, vol_targets):
        # returns_windows: (n_samples, 60, 1) — 60-day rolling windows
        # vol_targets: (n_samples,) — realized vol for next day
        optimizer = Adam(lr=0.001)
        loss_fn = nn.MSELoss()
        
        for epoch in range(50):
            pred = self.model(returns_windows)
            loss = loss_fn(pred, vol_targets)
            loss.backward()
            optimizer.step()
    
    def forecast_vol(self, recent_returns):
        # recent_returns: (60,) — last 60 days
        with torch.no_grad():
            pred = self.model(recent_returns.unsqueeze(0))
        return pred.item()
```

### LSTM advantages

- Can incorporate lagged market data (VIX, bond yields)
- Learns regime switches automatically
- During volatile periods, upweights recent shocks

### Trade-offs

- Slow to train (hours on GPU)
- Needs more data (2500+ samples)
- Prone to overfitting

---

## 6. COMPARISON: When Each Model Wins (30:00–35:00)

```
| Period       | Market Condition | Best Model   | Sharpe Boost |
|--------------|-----------------|--------------|--------------|
| 2015-2018    | Normal           | GARCH        | Baseline     |
| 2018 Q4      | Correction       | Hybrid       | +15%         |
| 2020 Mar     | COVID crash      | LSTM         | +25%         |
| 2021-2023    | Normalized       | GARCH        | Baseline     |
```

"GARCH for baseline. Hybrid during market stress. LSTMfor crisis prediction."

---

## 7. ENSEMBLE VOL FORECAST (35:00–38:00)

In production, use all three:

```python
vol_ensemble = (0.5 * garch_vol + 0.3 * hybrid_vol + 0.2 * lstm_vol)
```

Rebalance weights based on recent accuracy (last 60 days, which model was closest?)

---

## 8. THE PAYOFF (38:00–40:00)

"Volatility forecasting isn't about perfect accuracy. It's about regime-awareness. Good vol estimates reduce position sizing bloat and drowdowns."

"Next: Portfolio construction. We have volatility estimates. Now strategically allocate capital."

**CTA:**
1. "Subscribe"
2. "Comment: do you forecast vol? Which method?"
3. GitHub (garch_vol.py, hybrid_vol.py, lstm_vol.py)

---

## [NEEDS MORE]

- Your vol forecast acuracy vs realized vol
- Specific periods showing GARCH failure + hybrid recovery
- GPU time for LSTM training
