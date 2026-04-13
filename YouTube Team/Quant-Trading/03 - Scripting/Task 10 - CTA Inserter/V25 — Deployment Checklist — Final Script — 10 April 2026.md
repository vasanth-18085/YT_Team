# V25 — Deployment Checklist — Final Script

**Title:** Going Live: 30-Point Checklist Before Risking Real Capital
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

You have backtested. You have paper traded. The Sharpe ratio (your risk-adjusted return score) looks good. The tearsheet shows acceptable risk. Now what?

One missed checklist item can blow an account. A stale model weight that was not retrained. A missing kill switch that lets a feedback loop compound losses. A data feed that silently stopped updating and fed yesterday's prices into today's model.

[INFORMATION GAIN] I have a 30-point deployment checklist organised into 6 blocks: code quality, model validation, risk controls, execution operations, compliance, and capital ramp. Every professional quant fund runs through something similar before committing capital. This is not bureaucracy. This is a risk firewall. Most live blowups in smaller quant setups are not caused by bad models. The model is usually fine. It is the surrounding infrastructure — data feeds, execution mechanics, monitoring, kill switches — that fails. A checklist ensures the boring but critical infrastructure gets the same attention as the exciting ML model.

---

## SECTION 2 — BLOCK 1: CODE AND REPRODUCIBILITY (2:00–10:00)

Five items that ensure your code is production-ready.

**Item 1: All tests pass.** Run the full test suite — `pytest` with no flags, no skips, no known failures. If a test is failing and you think it is unrelated, fix it anyway. In production, unrelated failures become related at 2am when something goes wrong and you need to diagnose the actual cause versus pre-existing noise.

**Item 2: No hard-coded paths or secrets.** Every file path comes from config.yaml. Every API key comes from environment variables, never from source files. If someone clones your repository with their own directory structure and their own broker credentials, everything should work by editing config.yaml and setting environment variables. Hard-coded paths break when you deploy to a different machine. Hard-coded secrets get pushed to GitHub and compromise your accounts.

**Item 3: Structured logging for every order and decision.** Every signal generated, every order submitted, every fill received, and every error encountered must be logged with timestamps, tickers, prices, and quantities. JSON-lines format: one structured record per event. This is the forensic record. When something goes wrong at 2am — and it will — this log is how you reconstruct exactly what happened.

```python
import json, logging

logger = logging.getLogger("trading")

def log_event(event_type, **kwargs):
    record = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **kwargs
    }
    logger.info(json.dumps(record))

# Usage:
log_event("order_submitted", ticker="AAPL", side="buy",
          quantity=500, price=185.20, signal=0.72)
log_event("fill_received", ticker="AAPL", fill_price=185.25,
          slippage_bps=2.7, commission=2.50)
```

[INFORMATION GAIN] Item 3 is the most commonly skipped item on this entire checklist and the most painful when it is missing. I log to both a local file and a remote logging service. The local file is the primary record. The remote service is the backup that survives if the local machine crashes. The full schema includes: timestamp, event_type, ticker, signal, order_type, quantity, price, fill_price, slippage, commission, and current portfolio equity. This is not overkill. Every field has been needed at some point during debugging.

**Item 4: Git commit hash stored per run.** Every daily prediction batch saves the git hash of the code that produced it. The ExperimentTracker from V21 does this automatically with `git rev-parse HEAD`. This means you can always trace a prediction back to the exact code version. If the model starts behaving strangely, you can diff the current code against the last known good commit.

**Item 5: Config versioned and hashed.** The config.yaml used for deployment is saved alongside the model weights. A SHA-256 hash of the config file is stored in the run log. If someone modifies the config after deployment — changing a threshold, adjusting a risk parameter — the hash change is detectable. Unauthorised config changes are one of the most common sources of unexpected behaviour in production systems.

---


[CTA 1]
If you want the full deployment checklist as a reference you can print and check off, the free starter pack has it along with the CI/CD pipeline template and the monitoring dashboard config. In the description.

## SECTION 3 — BLOCK 2: MODEL VALIDATION (10:00–16:00)

Five items that ensure the model is trustworthy.

**Item 6: Untouched out-of-sample holdout.** There must be a data period that the model has never seen during training, hyperparameter tuning, or feature selection. Not the walk-forward test folds — those were used for model comparison and selection. A completely separate reserved holdout that you saved from the very beginning and only touch once, as the final go/no-go check.

**Item 7: Walk-forward stability.** Check the Sharpe ratio per fold across all 6 walk-forward folds. If fold 2 has Sharpe 1.5 and fold 5 has Sharpe 0.1, the model is not stable. It works in some market regimes and fails in others. A stable model should show Sharpe ratios within a reasonable band — maybe 0.4 to 1.0 across folds. Wide dispersion means the strategy is regime-dependent and you need to understand which regimes it fails in.

**Item 8: Robustness to parameter perturbation.** Perturb each key hyperparameter by plus or minus 10 percent and re-run the validation. Hidden size: 64 becomes 58 and 70. Learning rate: 0.001 becomes 0.0009 and 0.0011. If the Sharpe drops more than 20 percent from a 10 percent parameter change, the model is fragile — it relies on a knife-edge configuration that will not persist in live markets where the true distribution drifts continuously.

[INFORMATION GAIN] Item 8 catches a subtle overfitting failure mode that walk-forward validation alone does not detect. A model can pass walk-forward with flying colours but be sitting on a narrow parameter peak where slightly different parameters produce much worse results. In live trading, the effective parameters shift as the market evolves. If you are on a knife-edge, any small shift pushes you off. Robust models sit on broad plateaus where nearby parameters produce similar results.

**Item 9: Stress window performance.** Test explicitly on 2008 (financial crisis), 2020 (COVID crash), and 2022 (rate hike regime). These three periods test different failure modes: 2008 tests credit crisis and correlated selloffs, 2020 tests sudden volatility spike and recovery, 2022 tests sustained drawdown from policy change. The strategy does not need to make money during these periods. It needs to not blow up. Maximum acceptable drawdown during stress: negative 25 percent.

**Item 10: Corrected statistical significance.** The Deflated Sharpe Ratio from V19 must be positive with p-value below 0.05. The Probability of Backtest Overfitting from V19 must be below 0.50 (ideally below 0.30). The BH-FDR (Benjamini-Hochberg False Discovery Rate) correction from V18 must confirm at least one model variant is statistically significant. These three checks together ensure the results are not artifacts of multiple testing, selection bias, or data mining.

---

## SECTION 4 — BLOCK 3: RISK CONTROLS (16:00–22:00)

Six items that prevent catastrophic losses.

**Item 11: Maximum position cap enforced in code.** No single stock exceeds max_weight (default 25 percent of portfolio). This is enforced in the SignalCombiner's position sizing code (`np.clip(position_size, 0, self.max_weight * self.leverage)`) and in the PaperTrader's order submission (`max_position_pct`). Double enforcement — once at the signal level and once at the execution level — prevents position concentration even if one layer has a bug.

**Item 12: Leverage cap.** Total exposure — the sum of absolute position values divided by equity — does not exceed the configured leverage limit. Default is 1.0 (no leverage). With 25 stocks at 4 percent each, total exposure is 100 percent. If the position sizer produces weights that sum to more than 100 percent, the leverage cap scales everything down proportionally.

**Item 13: Daily loss stop.** If the portfolio drops more than 2 percent in a single day, all trading halts automatically. No new positions are opened. Existing positions are held (not panic-liquidated during a dip, which could lock in temporary losses). The halt persists until the next trading day when the system re-evaluates.

**Item 14: Correlation spike de-risking.** If the average pairwise correlation among portfolio stocks exceeds 0.7, reduce all positions by 50 percent. High correlation means diversification has collapsed — your 25 stocks are behaving as one big position. A correlated selloff in this state would produce a position-size-equivalent drawdown.

**Item 15: Volatility spike de-risking.** If VIX (the market's fear index) exceeds 50 or realised portfolio volatility spikes above 2x the rolling 60-day average, reduce all positions by 50 percent. This stacks with the regime detector from V14 — both reduce exposure during crises through independent mechanisms.

**Item 16: Kill switch tested.** The emergency shutdown works: one command halts all trading, closes all positions, moves to 100 percent cash. Test this before deployment, not during a crisis.

```python
def risk_kill_switch(daily_pnl, vix, portfolio_equity, max_loss=-0.02):
    """Emergency halt: returns True if conditions breached."""
    if daily_pnl / portfolio_equity < max_loss:
        return True
    if vix > 50:
        return True
    return False
```

[INFORMATION GAIN] The most critical item is 16 — kill switch tested. Every other control is automated and works within defined parameters. But there will be situations that fall outside all parameters. A flash crash. A market-wide trading halt. A broker API failure. The kill switch is the manual override that works when everything else breaks. Test it the same way pilots test emergency procedures: simulate the failure, trigger the switch, and confirm the system goes flat. I run this test monthly.

---


[CTA 2]
The complete deployment checklist is in the free starter pack — link in the description. Print it and check each item off.

## SECTION 5 — BLOCK 4: EXECUTION AND OPERATIONS (22:00–28:00)

Seven items covering the operational mechanics.

**Item 17: Data feed redundancy.** At least 2 data sources for price data. If yfinance fails (which happens regularly — rate limiting, API changes, missing tickers), the system falls back to an alternative source. The system must also detect stale data: if no new prices arrive for 30 minutes during market hours, alert the operator.

**Item 18: Broker API failover tested.** If the primary API connection drops, the system detects the disconnection, pauses all pending orders, and alerts the operator. Automatic reconnection with exponential backoff: wait 1 second, then 2, then 4, then 8, up to 60 seconds. After 5 minutes of continuous failure, escalate to SMS alert.

**Item 19: Clock synchronisation.** The system's clock is synced with an NTP server. A 5-second drift can cause orders to be submitted at the wrong time relative to market events. For automated systems that trade at specific times (market open, close), clock accuracy matters.

**Item 20: Order retry policy.** If an order submission fails — network error, broker rejection, insufficient buying power — the system does not silently drop the order. It retries with exponential backoff (1s, 2s, 4s). After 3 failures, it logs the error and alerts the operator rather than continuing to retry blindly.

**Item 21: Partial fill handling.** If a market order for 500 shares only fills 300, the system tracks the 200-share shortfall. It decides whether to resubmit (for time-critical signals) or absorb the shortfall (for position adjustments where the exact quantity is not critical). The portfolio state accurately reflects the partial fill.

**Item 22: Latency benchmarks logged.** Measure and record three latencies: signal generation time (from data ingestion to signal output), order submission time (from signal to broker API call), and fill latency (from API call to confirmation). If any of these exceed the historical 95th percentile by 2x, investigate.

**Item 23: Monitoring dashboard is live.** A real-time dashboard showing current positions, daily P&L, rolling Sharpe, drift monitor status, and recent order activity. The rule: if the dashboard is not running, do not trade. The dashboard is not a nice-to-have. It is a prerequisite for live operation.

---

## SECTION 6 — BLOCK 5: COMPLIANCE AND BLOCK 6: CAPITAL RAMP (28:00–38:00)

Four compliance items and three capital ramp items.

**Item 24: Regulatory requirements checked.** In the US, the pattern day trader rule requires $25,000 minimum equity for accounts that make 4 or more day trades in 5 business days. If your strategy trades daily, you must maintain this minimum. In the EU, MiFID II has specific requirements for algorithmic trading including pre-trade risk checks and reporting obligations.

**Item 25: Broker permissions verified.** The account is explicitly approved for the trading activity you intend. Margin trading, short selling, options if applicable. Do not assume — verify with the broker's compliance team. Unapproved activity can result in forced liquidation of positions without notice.

**Item 26: Tax lot and P&L logging configured.** Every trade is logged for tax reporting. For US taxes: track short-term versus long-term gains (holding period above or below 1 year), apply wash sale rules (disallow loss on a repurchase within 30 days), and select cost basis method (FIFO, LIFO, or specific identification). Automate this from day one. Reconstructing tax records from raw trade logs after a year of trading is a nightmare.

**Item 27: Audit trail retention.** Define a retention policy — typically 7 years for financial records. Store trade logs, position history, and daily portfolio snapshots in a secure, backed-up location.

Now the capital ramp — how to go from paper trading to full capital deployment without unnecessary risk.

**Item 28: Start with 1 to 5 percent of intended capital.** Deploy with a small slice: $5,000 on a $100,000 target. This limits downside while testing the live system end-to-end. You verify that data feeds work, orders execute correctly, commissions match expectations, and the daily P&L is within the expected range. If something breaks, you lose a small amount while learning, not a large amount.

**Item 29: Objective scale-up criteria.** Define in advance — before deployment — the conditions for adding more capital. My criteria: minimum 1 month of live trading, live Sharpe above 1.0, maximum drawdown better than negative 5 percent, all 7 drift monitors green. All conditions must be met simultaneously. This makes scaling a rule-based decision, not an emotional reaction to a lucky week.

```python
def scale_decision(sharpe, max_dd, months_live, drift_status):
    """Rule-based capital scaling."""
    if (sharpe > 1.0
        and max_dd > -0.05
        and months_live >= 1
        and all(s == 'green' for s in drift_status)):
        return "SCALE_UP"
    return "HOLD_SIZE"
```

[INFORMATION GAIN] Emotional scaling after short good streaks is one of the most common failure modes for retail quant traders. You start with $5K. The first week you make $500 — a 10 percent return (clearly unsustainable luck). You get excited and dump the full $100K in. Then the mean reversion hits. You lose $5K from a larger base in one bad week. The rule-based approach prevents this. The 1-month minimum ensures you have enough days (22 trading days) to distinguish skill from luck with reasonable statistical power.

**Item 30: Reserve cash buffer.** Never deploy more than 80 percent of total available capital into the strategy. Keep 20 percent in reserve for margin calls, unexpected tax liabilities, or opportunistic rebalancing during market dislocations. The reserve also serves as a psychological buffer — knowing you have cash on the side makes it easier to hold positions through drawdowns.

---

## SECTION 7 — FIRST-WEEK MONITORING AND THE CLOSE (38:00–40:00)

The first week of live trading is the highest-risk period. Daily checklist.

Compare expected versus realised P&L. The difference should be within plus or minus 20 percent of what the paper trader predicted. If it is consistently outside this range, stop and investigate.

Verify all orders executed and logged correctly. Check the fill prices against market prices at the time of execution. Confirm commissions match broker rates.

Inspect any anomalies manually. A stock that moved 10 percent on no news. An unusually large position from a signal spike. A fill price that is suspiciously far from the market price.

Keep the manual override active. You should be able to go flat — close all positions, move to 100 percent cash — in under 60 seconds. Practice this before the first live day.

Review the drift monitor dashboard every morning before market open. If any of the 7 tests from V15 are red, pause and investigate before executing today's trades.

This checklist converts a trading strategy from a research idea into a controllable business process. Deployment is not the end of research. It is the start of disciplined operations. Every item on this list exists because someone, somewhere, learned it the hard way.

This is the final video in the series. We have gone from raw data to features, from 14 forecasting models to sentiment analysis, from signal fusion to regime detection, from statistical validation to live deployment. The entire pipeline is open source, every component explained, every design decision documented.

---

## Information Gain Score

**Score: 7.5/10**

Strong on the practical operational items (structured logging, kill switch testing, capital ramp rules), the code examples for logging and kill switch, and the emotional scaling prevention framework. The 30-item structure provides clear accountability.

**Before filming, add:**
1. Your actual monitoring dashboard screenshot — annotate each panel
2. A live demo of triggering the kill switch and going flat
3. Your first-week live results versus paper trading predictions
4. The scale-up decision log showing when and why you added capital
