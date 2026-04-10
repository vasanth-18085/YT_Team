# V25 — Deployment Checklist — Logical Flow — 09 April 2026

**Title:** Going Live: 30-Point Checklist Before Risking Real Capital
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** You have backtested. You have paper traded. The Sharpe looks good. Now what? One missed checklist item equals a blown account. I have a 30-point deployment checklist organized into 6 blocks — code quality, model validation, risk controls, execution operations, compliance, and capital ramp. Every professional quant fund runs through something similar before committing capital. A rigorous go-live checklist is not bureaucracy — it is a risk firewall.

## 2. WHY CHECKLISTS EXIST IN HIGH-STAKES ENVIRONMENTS (2:00–6:00)

Atul Gawande's The Checklist Manifesto documents how checklists reduce fatal errors in surgery and aviation. The principle applies directly to algorithmic trading where a single oversight can lose real money in minutes.

The deployment failure modes I have seen in the quant community: deploying with stale model weights (the model had not retrained in 3 months and was predicting on a different market regime). Deploying without a kill switch (the strategy entered a feedback loop and kept buying as losses mounted). Deploying with production data that had different scaling than training data (features were z-scored differently, producing garbage signals). Each of these was preventable with a checklist.

**[INFORMATION GAIN]** Most live blowups in smaller quant setups are operational, not model-driven. The model is usually fine — it is the surrounding infrastructure (data feeds, execution, monitoring) that fails. A checklist ensures the boring but critical infrastructure gets the same attention as the exciting ML model.

## 3. BLOCK 1: CODE AND REPRODUCIBILITY (6:00–12:00)

Item 1: All unit and integration tests pass. Run the full test suite (`make test` or `pytest`) and confirm everything is green. Do not deploy with known test failures, even if you think they are unrelated.

Item 2: No hard-coded paths or secrets. Every path comes from config.yaml. API keys come from environment variables, never from code files. If someone clones your repo, it should work with their own paths and keys.

Item 3: Structured logging for every order and decision. Every signal generated, every order submitted, every fill received, and every error encountered must be logged with timestamps, tickers, prices, and quantities. Without this, debugging a live issue is impossible.

Item 4: Git commit hash stored per run. Every prediction batch saves the git hash so you know exactly which code version produced it. The ExperimentTracker from V21 does this automatically.

Item 5: Config versioned and hashed. The config.yaml used for deployment is saved alongside the model weights. A hash of the config is stored so you can detect if someone modified it after deployment.

**[INFORMATION GAIN]** Item 3 (structured logging) is the most commonly skipped and the most painful when missed. I log to both a local file and a remote service. Format: JSON lines with fields: timestamp, event_type, ticker, signal, order_type, quantity, price, fill_price, slippage, commission, portfolio_equity. This log is the forensic record — when something goes wrong (and it will), this is how you reconstruct what happened.

## 4. BLOCK 2: MODEL VALIDATION (12:00–18:00)

Item 6: Untouched out-of-sample holdout. There must be a data period that the model has NEVER seen during training, hyperparameter tuning, or feature selection. This is the final reality check. If performance drops materially on this holdout, the model is overfit.

Item 7: Walk-forward stability. The walk-forward Sharpe should be consistent across folds. If fold 2 has Sharpe 1.5 and fold 5 has Sharpe 0.1, the model is not stable — it works in some regimes and fails in others.

Item 8: Robustness to parameter perturbation. Perturb each hyperparameter by ±10% and re-run. If the Sharpe ratio drops more than 20%, the model is fragile — it is relying on a knife-edge configuration that is unlikely to persist live.

Item 9: Stress window performance. Test explicitly on 2008 (financial crisis), 2020 (COVID crash), and 2022 (rate hike regime). If the model survives these with acceptable drawdowns, it has passed a minimum durability test.

Item 10: Corrected significance from V18-V19. Deflated Sharpe Ratio is positive. PBO is below 0.50. BH-FDR correction confirms at least one model variant is statistically significant.

**[INFORMATION GAIN]** Item 8 (parameter perturbation) catches a subtle failure mode: strategies that are optimized to a very specific parameter set that happened to work on this particular dataset but would fail with slightly different parameters. This is a form of overfitting that walk-forward validation alone does not catch because all folds use the same hyperparameters.

## 5. BLOCK 3: RISK CONTROLS (18:00–24:00)

Item 11: Maximum position cap. No single stock exceeds max_weight (default 25%) of portfolio. Enforced in code, not just policy.

Item 12: Leverage cap. Total exposure (sum of absolute position values / equity) does not exceed the configured leverage limit. Default: 1.0 (no leverage).

Item 13: Daily loss stop. If the portfolio drops more than 2% in a single day, all trading halts automatically. No new positions opened. Existing positions held (not liquidated in panic).

Item 14: Correlation spike de-risking. If the average pairwise correlation among portfolio stocks exceeds a threshold (default 0.7), reduce all positions by 50%. High correlation means diversification has collapsed and a correlated selloff is likely.

Item 15: Volatility spike de-risking. If VIX exceeds 50 (or realized vol spikes above 2x the historical average), reduce all positions by 50%.

Item 16: Kill-switch tested. The emergency shutdown mechanism works: one command or button halts all trading, closes all positions, moves to cash. Test this before deployment, not during a crisis.

The kill-switch implementation: `risk_kill_switch(daily_pnl, vix, max_loss=-0.02)` returns True if daily PnL exceeds the max loss threshold OR if VIX exceeds 50. When True, the system transitions to a fully flat cash position.

**[INFORMATION GAIN]** The most important risk control is Item 16 (kill-switch tested). Every other control is automated and works within parameters. But there will be situations that fall outside all parameters — a flash crash, a market-wide halt, a broker API failure. The kill switch is the manual override. Test it the same way pilots test emergency procedures: simulate the failure, trigger the switch, confirm the system goes flat.

## 6. BLOCK 4: EXECUTION AND OPERATIONS (24:00–28:00)

Item 17: Broker API failover tested. If the primary broker API connection drops, does the system have a fallback? At minimum, it should detect the disconnection, pause trading, and alert the operator. Ideally, it connects to a secondary endpoint.

Item 18: Data feed redundancy. At least 2 data sources for price data. If yfinance fails, fall back to Alpha Vantage or a paid API. The system should detect stale data (no new prices for 30+ minutes during market hours) and alert.

Item 19: Clock synchronization. The system's clock must be synchronized with exchange time. A 5-second clock drift can cause orders to be submitted at the wrong time relative to market events.

Item 20: Order retry policy. If an order submission fails (network error, broker rejection), the system should retry with exponential backoff (wait 1s, then 2s, then 4s). After 3 failures, escalate to operator.

Item 21: Partial fill handling. If a market order for 500 shares only fills 300, what happens to the remaining 200? The system must track the open order, decide whether to resubmit, and reconcile the portfolio state.

Item 22: Latency benchmarks logged. Measure and record: time from signal generation to order submission, time from order submission to fill, total decision-to-execution latency. If latency exceeds historical benchmarks by 2x, investigate.

Item 23: Monitoring dashboard is live. A real-time dashboard showing: current positions, daily P&L, rolling Sharpe, drift monitor alerts, and order activity. If the dashboard is not running, do not trade.

## 7. BLOCK 5: COMPLIANCE AND ACCOUNTING (28:00–32:00)

Item 24: Regional legal checks done. Algorithmic trading regulations vary by country. In the US, pattern day trader rules require $25K minimum for frequent trading. In the EU, MiFID II has specific requirements for automated trading.

Item 25: Broker account permissions verified. The account is approved for the trading activity you intend (margin trading, short selling, options if applicable). Do not assume — verify explicitly with the broker.

Item 26: Tax lot and PnL logging configured. Every trade must be logged for tax reporting. For US taxes: track short-term vs long-term gains, wash sale rules, and cost basis method (FIFO, LIFO, specific identification).

Item 27: Audit trail retention policy. Define how long you keep trade logs — typically at least 7 years for tax purposes. Store securely with backups.

## 8. BLOCK 6: CAPITAL RAMP PLAN (32:00–38:00)

Item 28: Start with a small capital slice. Deploy with 1-5% of your intended final capital. This limits downside while testing the live system. If the strategy works with $5K, you lose at most $5K while validating. If it works, scale up.

Item 29: Objective scale-up criteria. Define in advance: under what conditions do you add more capital? My criteria: minimum 1 month live, live Sharpe > 1.0, max drawdown < -5%, all drift monitors green. These must be met simultaneously — no cherry-picking.

The code: `scale_decision(sharpe, max_dd, months_live)` returns "SCALE_UP" if Sharpe > 1.0 AND max_dd > -0.05 AND months_live >= 1. Otherwise "HOLD_SIZE". This makes scaling a rule-based decision, not an emotional one.

Item 30: Reserve cash buffer. Never deploy more than 80% of your capital into the strategy. Keep 20% as a reserve for: margin calls, unexpected tax liabilities, or opportunistic rebalancing during market dislocations.

**[INFORMATION GAIN]** Emotional scaling after short good streaks is one of the most common failure modes for retail quant traders. You start with $5K, make $500 in the first week (10% return — clearly unsustainable), get excited, and dump $50K in. Then the mean reversion hits and you lose $5K in a week from a larger base. Rule-based scaling prevents this. The minimum 1-month observation period ensures you have enough data to distinguish skill from luck.

## 9. FIRST-WEEK LIVE MONITORING (38:00–39:00)

Daily checklist for the first week of live trading: compare expected vs realized P&L (should be within ±20% of backtest expectations). Verify all orders executed and logged correctly. Inspect any anomalies manually. Keep the manual override active — you should be able to go flat in under 60 seconds. Review the drift monitor dashboard every morning before market open.

## 10. THE CLOSE (39:00–40:00)

This checklist converts a trading strategy from a research idea into a controllable business process. Deployment is not the end of research — it is the start of disciplined operations. Every item on this list exists because someone, somewhere, learned it the hard way.

This is the final video in the series. We have gone from raw data to features, from 14 forecasting models to sentiment analysis, from fusion signals to regime detection, from statistical validation to live deployment. The entire pipeline is open source, every component explained, every design decision documented.

[NEEDS MORE] Your exact numeric thresholds for scale-up. Your first-week monitoring dashboard screenshot. An incident-response runbook snippet for the most common failure scenarios.
