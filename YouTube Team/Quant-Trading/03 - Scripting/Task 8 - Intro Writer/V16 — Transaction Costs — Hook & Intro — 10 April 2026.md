# V16 — Transaction Costs — Hook & Intro

**Video Title:** 10 bps Matters: How Commissions + Slippage Kill Backtests
**Date:** 10 April 2026

---

## Hook Question

Your backtest says Sharpe of 1.2. You add realistic transaction costs. Now it is 0.6. Where did half your edge go?

## Credibility

I built three cost models — commission, slippage, and market impact — and ran a sensitivity sweep from 1 to 20 basis points. The break-even point for my strategy was 35 bps. Above that, the strategy loses money. That single number determines whether this pipeline is a real business or an academic exercise.

## Why Now (R.A.I.N.Y — N)

Zero-commission brokers created the illusion that trading is free. But hidden costs — payment for order flow, spread widening, market impact — are higher than ever for retail traders. If you think your trades are free, this video will show you exactly how much you are actually paying.

## Video Structure

In this video I break down all three cost layers — the explicit commission, the hidden slippage from the square-root volume law, and the permanent market impact from the Almgren-Chriss model. You will see the exact code, worked examples comparing Apple versus small-cap slippage, and the full cost sensitivity sweep output. By the end you will know precisely where your strategy's cost ceiling is.

## Open Loop

But first let me show you a calculation that should scare you — because it reveals exactly how much money daily rebalancing costs even with a supposedly zero-commission broker.
