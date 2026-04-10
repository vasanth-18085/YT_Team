# V15 — Drift Monitoring — Logical Flow — 09 April 2026

**Title:** 7 Tests for Strategy Decay: When to Stop Trading and Retrain
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** Your strategy was hitting 65% directional accuracy last month. Today it is at 51% — basically a coin flip. What happened? Drift. The data distribution shifted underneath your model while you were not looking. I built a DriftMonitor class with 7 statistical tests that run continuously during live trading. When enough tests flag drift, the system automatically pauses trading and triggers retraining before losses compound.

The uncomfortable truth: every model you deploy will decay. The only question is whether you detect it before or after it costs you money.

## 2. WHAT IS DRIFT AND WHY DOES IT KILL STRATEGIES (2:00–8:00)

Concept drift means the statistical relationship between your features and your target variable changes over time. Your model was trained on a world where high RSI + positive sentiment predicted positive returns. Then the market regime shifts — maybe the Fed changes policy, maybe a sector rotation happens — and suddenly that same feature pattern predicts flat or negative returns. Your model has not changed. The world changed.

There are two types. Sudden drift: a market event (COVID crash, rate hike surprise) causes an immediate distribution shift. Your model goes from 65% accuracy to 48% overnight. Gradual drift: slow evolution of market microstructure over months. Your model goes from 65% to 62% to 58% to 53% and you do not notice until you have hemorrhaged capital.

**[INFORMATION GAIN]** Gradual drift is more dangerous than sudden drift because it is harder to detect. With a sudden event you see the equity curve plunge and react immediately. With gradual drift you keep telling yourself it is a normal variance period and stay invested through months of declining edge. The DriftMonitor catches both kinds.

## 3. THE DRIFTMONITOR CLASS (8:00–14:00)

The implementation at `src/m7_validation/drift_monitor.py` tracks a rolling metric window against a baseline established during the first N observations.

Key parameters: window=60 (rolling window for computing current metric), baseline_window=120 (initial calibration period where you establish what normal looks like), warning_pct=0.10 (trigger warning if metric drops 10% from baseline), critical_pct=0.25 (trigger critical alert if metric drops 25%).

The default metric is directional accuracy: what fraction of the time did you correctly predict the sign of the next-day return. But you can plug in any metric — Sharpe ratio, information coefficient, profit factor.

The update loop: every day, feed in the true next-day return and your yesterday's prediction. The monitor computes rolling accuracy over the last 60 observations. Once the baseline_window is filled (120 observations), it establishes the baseline accuracy. Every subsequent observation is compared against that baseline. If current metric drops below baseline * (1 - critical_pct), it fires a DriftAlert with severity critical.

## 4. THE 7 DRIFT TESTS IN DETAIL (14:00–30:00)

I run 7 complementary tests because no single test catches all drift types.

### Test 1: Directional Accuracy (the DriftMonitor default)
Rolling hit rate on return sign prediction. Baseline: 62% during training. Warning at 55.8% (10% drop). Critical at 46.5% (25% drop). This is the most intuitive test — are you predicting direction correctly?

### Test 2: Kolmogorov-Smirnov Test on Feature Distributions
Are the features your model sees today statistically different from the features it was trained on? KS test checks if two samples come from the same distribution. I run KS on each of the top 10 features monthly, comparing the last 60 days against the training period. If more than 3 features show significant drift (p < 0.05), the input distribution has shifted.

**[INFORMATION GAIN]** Feature drift often precedes performance drift by 2-4 weeks. By the time your strategy's accuracy drops, the features have been drifting for a month. Monitoring features directly gives you earlier warning than monitoring performance alone.

### Test 3: Population Stability Index (PSI)
PSI quantifies how much a feature distribution has shifted by comparing bin frequencies between the reference and current periods. PSI < 0.1 means stable. PSI 0.1-0.25 means moderate shift. PSI > 0.25 means significant drift requiring action. Unlike KS, PSI gives a magnitude of shift, not just a yes/no.

### Test 4: Rolling Sharpe Ratio
Compute 60-day rolling Sharpe. If the rolling Sharpe has been negative for 30+ consecutive days, this is a strong structural signal that the edge has evaporated. Plot the rolling Sharpe over time — a downward trend is a leading indicator of strategy decay even before the Sharpe goes negative.

### Test 5: CUSUM (Cumulative Sum Control Chart)
Industrial quality control technique applied to trading. Track the cumulative sum of deviations from expected return. When the cumulative sum exceeds a threshold, the process has shifted. CUSUM is excellent for detecting gradual drift because small daily deviations accumulate into a visible signal.

### Test 6: Correlation Decay
Measure the rolling correlation between your signal and forward returns. A strong signal has correlation 0.05-0.15 with next-day returns. If this correlation drops toward zero and stays there for 30+ days, the predictive relationship has broken.

### Test 7: Maximum Drawdown Duration
Track how long you have been in drawdown. If the current drawdown duration exceeds the maximum observed in training data by more than 50%, something structural has changed. This test catches the failure mode where accuracy is technically fine but position sizing or market conditions have changed the risk profile.

## 5. DECISION RULES AND AUTOMATED RESPONSE (30:00–36:00)

Each test runs independently and produces a severity: green (normal), yellow (warning), or red (critical).

Decision matrix: if 0-1 tests are red, continue trading with heightened monitoring. If 2-3 tests are red, reduce position sizes by 50% and alert the operator. If 4+ tests are red, halt trading entirely, liquidate positions to cash, notify operator, and queue a full retraining pipeline.

**[INFORMATION GAIN]** The hardest part is not building the tests — it is trusting them enough to actually stop trading when they fire. I have a rule: the system's pause decision is final for at least 48 hours. No manual override to resume trading within that window. This prevents the emotional bias of looking at one good day and deciding the drift was a false alarm.

The retraining pipeline after drift detection: retrain all upstream models (Phase 1-4) on a sliding window that includes the most recent data. Re-validate on a fresh holdout. Only resume trading if the re-validated Sharpe exceeds a minimum threshold (I use 0.5). If it does not pass, the strategy stays paused until the next data update.

## 6. MONITORING IN PRODUCTION (36:00–38:00)

In live trading, the DriftMonitor runs as a daily cron job. It ingests yesterday's predictions and today's realized returns. It updates the rolling metrics, checks all 7 tests, and writes results to a dashboard.

The dashboard shows: current directional accuracy vs baseline, rolling Sharpe, number of drift test alerts (green/yellow/red), current drawdown duration, and days since last retraining. A simple traffic-light system: all green means keep trading, any red means investigate.

## 7. THE CLOSE (38:00–40:00)

Drift monitoring is the immune system of your trading operation. Without it, model decay silently erodes returns until you notice the damage months later. With it, you detect shifts in days and respond before losses compound.

Next video: transaction costs. Your backtested Sharpe of 1.2 drops to 0.6 when you add realistic commissions, slippage, and market impact. We build the full cost model and find out where the breakeven point is.

[NEEDS MORE] Your actual drift detection timeline from a specific retraining event. Screenshots of the monitoring dashboard. A case where drift was detected and what you retrained.
