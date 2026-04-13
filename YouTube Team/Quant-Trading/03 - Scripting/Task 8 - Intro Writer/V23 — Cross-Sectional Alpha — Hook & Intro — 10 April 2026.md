# V23 — Cross-Sectional Alpha — Hook & Intro

**Video Title:** From Time-Series Prediction to Cross-Sectional Ranking
**Date:** 10 April 2026

---

## Hook Question

What if predicting whether a stock goes up or down is the wrong question — and the real edge comes from predicting which stocks go up more than others?

## Credibility

I pivoted my pipeline from pure time-series prediction to cross-sectional ranking and the results changed dramatically. The time-series model predicted direction correctly 58 percent of the time but captured only part of the available alpha. The cross-sectional ranker — which builds a long-short portfolio by ranking stocks within each rebalance period — improved the information coefficient by 35 percent because it is a fundamentally easier prediction problem.

## Why Now (R.A.I.N.Y — N)

The shift from time-series to cross-sectional thinking is how hedge funds actually generate returns. This perspective is missing from virtually every retail quant education resource. If you are still trying to predict absolute returns, this reframing could save you months of dead-end research.

## Video Structure

In this video I show you the shift from time-series to cross-sectional thinking, the ranking algorithm, how the long-short portfolio is constructed, and the performance comparison against the time-series approach. You will see the CrossSectionalAlpha class code and real backtest numbers. By the end you will understand when to predict absolute returns versus relative ranks.

## Open Loop

But first let me explain why relative ranking is statistically easier than absolute prediction — because once you understand this one insight, the entire cross-sectional framework clicks into place.
