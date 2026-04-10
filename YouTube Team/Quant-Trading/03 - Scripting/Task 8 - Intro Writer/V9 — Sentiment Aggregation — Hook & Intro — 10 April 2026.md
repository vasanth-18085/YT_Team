# V9 — Sentiment Aggregation — Hook & Intro

**Video Title:** How to Turn 10,000 Headlines into Trading Features (The Right Way)
**Date:** 10 April 2026

---

## Hook Question

You have a fine-tuned sentiment model that can score individual headlines. But how do you actually turn thousands of noisy headline scores into a single clean trading signal for each stock on each day?

## Credibility

I process over 10,000 financial headlines per week through my pipeline. The raw sentiment scores are incredibly noisy — contradictory headlines for the same stock on the same day are normal. It took three iterations of the aggregation logic before the sentiment features actually improved the downstream models instead of making them worse.

## Video Structure

In this video I show you the full aggregation pipeline — from raw per-headline scores through time-decay weighting, source reliability ranking, and daily aggregation into a single sentiment feature per stock. You will see the exact code, the specific decay parameters I chose and why, and the before-and-after impact on model accuracy. By the end you will know how to turn messy text data into clean quantitative features.

## Open Loop

But first there is a counterintuitive finding I need to share — because the naive approach to sentiment aggregation that everyone tries first actually makes your models worse, not better. Let me show you the data.
