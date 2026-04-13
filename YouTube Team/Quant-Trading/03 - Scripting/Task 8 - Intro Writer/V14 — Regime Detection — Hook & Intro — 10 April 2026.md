# V14 — Regime Detection — Hook & Intro

**Video Title:** HMM-Based Regime Detection: Bull, Bear, and Crash Modes
**Date:** 10 April 2026

---

## Hook Question

Your model was printing money last month. This month it is haemorrhaging. What changed? Not the model. Not the features. The market regime shifted and nobody told your pipeline.

## Credibility

I built a Hidden Markov Model that classifies market state into bull, bear, and crash in real time — then adapts leverage and position sizing based on regime probability. In my backtests this single addition reduced max drawdown by 30 to 40 percent during crisis periods without sacrificing much upside in bull markets.

## Why Now (R.A.I.N.Y — N)

Market regimes are shifting faster than ever. The transition from zero-rate to high-rate caught most systematic strategies off guard. If your system traded through 2022-2023 without knowing the regime changed, it likely bled edge for months. This is the component that prevents that.

## Video Structure

In this video I walk through the complete regime detection system — the HMM architecture, the feature preparation, the transition probability matrix, and how soft probability-weighted sizing outperforms hard binary switching. You will see the actual code from my pipeline and real numbers from the walk-forward backtest. By the end you will have a meta-layer that tells every other component in your system how aggressively to trust its own signals.

## Open Loop

But first I need to show you what the transition matrix reveals about crash dynamics — because there is a number in that matrix that completely changed how I think about risk management.
