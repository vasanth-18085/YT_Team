# V5 — Data Pipeline — Hook & Intro

**Video Title:** The CSV File Lie Every ML Trader Still Believes
**Date:** 10 April 2026

---

## Hook Question

Have you ever spent three days debugging a model only to discover the problem was never the model — it was the data feeding it?

## Credibility

I burned two full weeks on a feature misalignment bug that was silently leaking future data into my training set. Every backtest result I had was inflated. I had to throw away a month of work and rebuild the data pipeline from scratch with validation checks at every step. That rebuilt pipeline is what powers this entire system now.

## Why Now (R.A.I.N.Y — N)

New data sources appear weekly — alternative data, social feeds, satellite imagery. But the pipeline problem is getting harder, not simpler. More data means more chances for silent bugs to leak future information into training. If you are building any ML trading system right now, the pipeline is where it will fail first.

## Video Structure

In this video I am going to show you the complete data pipeline — from raw API downloads through cleaning, deduplication, date alignment, and feature-ready output. You will see every validation check I added after every bug I hit, including the ones that catch lookahead leaks before they contaminate your models. By the end you will have a bulletproof ingestion layer that you can trust.

## Open Loop

But first let me show you the three most common data bugs in quant pipelines — because at least one of them is probably in your code right now and you do not know it yet.
