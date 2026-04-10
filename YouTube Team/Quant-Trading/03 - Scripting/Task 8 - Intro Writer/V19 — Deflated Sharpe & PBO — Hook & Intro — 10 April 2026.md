# V19 — Deflated Sharpe & PBO — Hook & Intro

**Video Title:** Is Your Sharpe Real? Deflated Sharpe Ratio & Probability of Backtest Overfitting
**Date:** 10 April 2026

---

## Hook Question

Your strategy has a Sharpe ratio of 1.3. Impressive — until I tell you that after adjusting for the number of configurations you tried, the probability that Sharpe is real drops to 40 percent. Would you still trade it?

## Credibility

I computed the Deflated Sharpe Ratio and the Probability of Backtest Overfitting for every strategy variant in my pipeline. Strategies that looked like solid 1.0+ Sharpe performers deflated to 0.4 once you accounted for the search process that found them. Only the handful with deflated Sharpe above 0.7 made it into the production pipeline.

## Video Structure

In this video I cover two frameworks — the Deflated Sharpe Ratio from Bailey and López de Prado which adjusts your Sharpe for how many strategies you tried, and Probability of Backtest Overfitting which tells you the odds that your best in-sample strategy underperforms out of sample. You will see the exact formulas, the code, and the real numbers from my pipeline. By the end you will never trust a raw Sharpe ratio again.

## Open Loop

But first I want to show you a result that genuinely unsettled me — because the strategy I was most confident about had the highest probability of overfitting. Let me show you why.
