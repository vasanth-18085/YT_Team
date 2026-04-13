# V13 — VectorBT Backtesting — Hook & Intro

**Video Title:** VectorBT: Testing 100 Stocks, 6 Folds, 50 Features in 2 Minutes
**Date:** 10 April 2026

---

## Hook Question

What if you could backtest your entire trading strategy — 100 stocks, 6 walk-forward folds, 50 features — and get full performance metrics in under 2 minutes?

## Credibility

My first backtest framework was a for-loop over dates. It took 8 hours to run a single pass. I rewrote the entire engine using VectorBT's vectorised architecture and the same backtest now runs in 110 seconds. That speed difference is not just convenience — it changes how you work because you can test ideas in real time instead of waiting overnight.

## Why Now (R.A.I.N.Y — N)

VectorBT is gaining adoption fast but its documentation does not cover walk-forward integration or proper purging. Right now most users are getting speed without correctness. This video shows you how to get both before bad habits become embedded in your workflow.

## Video Structure

In this video I show you the VectorBT engine I built — how I feed signals in, how walk-forward folds are handled, how transaction costs are integrated, and how the output metrics are computed. You will see the exact code and the performance comparison against a naive loop. By the end you will have a backtesting engine fast enough to iterate on strategies interactively.

## Open Loop

But first let me show you the one thing about VectorBT that trips everyone up on their first try — because if you get this wrong your backtest will run fast but produce completely wrong numbers.
