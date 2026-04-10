# V25 — Deployment Checklist — Final Script

**Title:** Going Live: 30-Point Checklist Before Risking Real Capital
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — HOOK (0:00–2:00)

One missed control can erase years of work.

[INFORMATION GAIN] A rigorous go-live checklist is not bureaucracy. It is a risk firewall across code, model validity, execution, and capital protection.

---


[CTA 1]
By the way, if you want the full MLQuant build resources in one place, I put together a free starter pack with the repo map, workflow checklist, and implementation notes. It is built for this exact stage of the journey. Grab it here: [INSERT PRIMARY LINK]

## SECTION 2 — CHECKLIST BLOCK 1: CODE & REPRODUCIBILITY (2:00–8:00)

1. Unit/integration tests passing
2. No hard-coded paths/secrets
3. Structured logging for every order/decision
4. Git commit hash stored per run
5. Config versioned and hashed

```python
def preflight_code_checks(test_ok, config_hash, commit_hash):
    return all([test_ok, bool(config_hash), bool(commit_hash)])
```

---

## SECTION 3 — BLOCK 2: MODEL VALIDATION (8:00–14:00)

6. untouched out-of-sample holdout
7. walk-forward stability
8. robustness to parameter perturbation
9. stress windows (2008/2020/2022)
10. corrected significance (BH-FDR / DSR / PBO)

[INFORMATION GAIN] "Best fold" performance is not deployment evidence. Stability across folds and stress periods is.

---

## SECTION 4 — BLOCK 3: RISK CONTROLS (14:00–20:00)

11. max position cap
12. leverage cap
13. daily loss stop
14. correlation spike de-risking
15. volatility spike de-risking
16. kill-switch tested

```python
def risk_kill_switch(daily_pnl, vix, max_loss=-0.02):
    return (daily_pnl <= max_loss) or (vix > 50)
```

---

## SECTION 5 — BLOCK 4: EXECUTION & OPERATIONS (20:00–27:00)

17. broker API failover tested
18. data feed redundancy
19. clock synchronization verified
20. order retry policy
21. partial-fill handling
22. latency benchmarks logged
23. monitoring dashboard live

[INFORMATION GAIN] Most live blowups in smaller quant setups are operational, not model-driven.

---

## SECTION 6 — BLOCK 5: COMPLIANCE & ACCOUNTING (27:00–32:00)

24. regional legal checks done
25. broker/account permissions verified
26. tax lot and PnL logging configured
27. audit trail retention policy

---

## SECTION 7 — BLOCK 6: CAPITAL RAMP PLAN (32:00–36:00)

28. start with small capital slice (e.g., 1-5%)
29. objective scale criteria (Sharpe/DD/stability)
30. reserve cash buffer

```python
def scale_decision(sharpe, max_dd, months_live):
    if months_live >= 1 and sharpe > 1.0 and max_dd > -0.05:
        return 'SCALE_UP'
    return 'HOLD_SIZE'
```

[INFORMATION GAIN] Scaling must be rule-based. Emotional scaling after short good streaks is a common failure.

---

## SECTION 8 — FIRST-WEEK LIVE MONITORING (36:00–38:00)

Daily checklist:
- compare expected vs realized behavior
- verify all executions and logs
- inspect anomalies manually
- keep manual override active

---


[CTA 2]
Quick reminder before we continue, if this is helping you, the free MLQuant starter pack is in the description and it goes deeper than what we can fit in one video. Link: [INSERT PRIMARY LINK]

## SECTION 9 — CLOSE (38:00–40:00)

Deployment is not the end of research. It is the start of disciplined operations.

This checklist converts a strategy into a controllable business process.

---

## Information Gain Score

**Score: 8.5/10**

High practical value from operationally complete readiness framework and scale governance.

**Before filming, add:**
1. Your exact numeric thresholds for scale-up
2. First-week dashboard screenshot
3. Incident-response runbook snippet
