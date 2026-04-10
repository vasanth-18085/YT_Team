# V12 — Portfolio Construction — Hook & Intro

**Video Title:** How to Allocate Capital Across Positions: Mean-Variance vs HRP vs Black-Litterman
**Date:** 10 April 2026

---

## Hook Question

You have 25 stocks your model says to buy. How do you decide whether to put 1 percent in each or 10 percent in the top five?

## Credibility

I implemented four portfolio construction methods — Mean-Variance, Hierarchical Risk Parity, Black-Litterman, and Risk Parity — and ran all four through 6 walk-forward folds on the same signal set. The difference in max drawdown between the best and worst allocator was 14 percentage points. Same signals, same stocks, dramatically different risk outcomes.

## Video Structure

In this video I walk through each method — the math, the code, and the real backtest results. You will see why Mean-Variance is unstable, how HRP fixes it using hierarchical clustering, what Black-Litterman adds with ML-generated views, and when simple Risk Parity beats them all. By the end you will know which allocator fits your risk tolerance.

## Open Loop

But first I need to show you what happens when you use Mean-Variance with estimated returns — because the portfolio it builds is so extreme it looks like a bug, and understanding why teaches you everything about why smart allocation matters.
