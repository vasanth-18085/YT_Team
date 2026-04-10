# V11 — Volatility Estimation — Hook & Intro

**Video Title:** Predicting Volatility: Why GARCH Fails (And What Works Better)
**Date:** 10 April 2026

---

## Hook Question

What if the most widely taught volatility model in quantitative finance — the one in every textbook and every course — consistently underestimates tail risk in real markets?

## Credibility

I compared GARCH, EGARCH, a hybrid ensemble, and an LSTM volatility model on 20 years of daily data across 100 stocks. GARCH underpredicted realised volatility during every major crisis in the sample. The hybrid model I built — which blends GARCH's structure with ML flexibility — cut volatility forecast error by 23 percent.

## Video Structure

In this video I show you why GARCH fails when you need it most, how EGARCH partially fixes the problem, and how the hybrid and LSTM approaches handle the cases GARCH cannot. You will see the actual error metrics, the calibration plots, and the impact on downstream position sizing. By the end you will have a volatility model that does not lie to you when markets get rough.

## Open Loop

But first let me show you a specific week where GARCH predicted 12 percent annualised volatility and realised volatility was 45 percent — because understanding why this happens is the key to building something better.
