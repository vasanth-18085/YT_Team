# V21 — Experiment Tracking — Hook & Intro

**Video Title:** Systematic Experimentation: How to Track 1000 Backtests
**Date:** 10 April 2026

---

## Hook Question

You have run 200 backtest configurations. Can you tell me right now which hyperparameters produced the best risk-adjusted return — and whether that result was statistically significant?

## Credibility

I could not answer that question for way too long. I was tracking experiments in spreadsheets and Jupyter notebook filenames. When I built a proper experiment tracker that logs every run with full metadata, I found three configurations I had tested months ago that I had completely forgotten about — and one of them was the best performer in the entire pipeline.

## Why Now (R.A.I.N.Y — N)

MLflow and Weights & Biases dominate ML experiment tracking. But neither handles the specific needs of trading backtests — fold-level metrics, statistical corrections, regime-tagged results. If you are running backtests without a proper tracker right now, you are losing experiments to disorganisation.

## Video Structure

In this video I show you the ExperimentTracker class I built — how it logs every backtest run with parameters, metrics, timestamps, and fold-level results. You will see how to query across experiments, rank by any metric, and generate comparison reports. By the end you will have a system that turns hundreds of scattered backtests into an organised searchable database.

## Open Loop

But first let me show you the specific experiment naming and tagging system I use — because without it, even a good tracker becomes a graveyard of unlabelled results you will never look at again.
