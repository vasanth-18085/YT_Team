# V18 — Multiple Testing Correction — Hook & Intro

**Video Title:** p-value Hacking: How to Avoid Fooling Yourself
**Date:** 10 April 2026

---

## Hook Question

You tested 50 model configurations and found 5 that are profitable. Congratulations — statistically, at least 2 of those are pure luck. Do you know which ones?

## Credibility

I ran 50 strategy variations through my walk-forward pipeline. Before multiple testing correction, 12 looked statistically significant. After applying Bonferroni, Holm-Bonferroni, and Benjamini-Hochberg corrections, only 4 survived. The other 8 were noise that I would have confidently traded with real money if I had not applied these corrections.

## Why Now (R.A.I.N.Y — N)

With ChatGPT and Copilot generating strategy code faster, people are testing more configurations than ever before. The multiple testing problem has never been more relevant. If you can spin up 50 strategy variants in an afternoon, you need this correction or you will trade noise with confidence.

## Video Structure

In this video I explain the multiple comparisons problem, walk through three correction methods with actual code, and show you exactly how many of my strategies survived the filter. You will see the p-value distributions, the correction thresholds, and the specific configurations that passed versus failed. By the end you will have a statistical hygiene system that prevents you from trading noise.

## Open Loop

But first let me show you how easy it is to accidentally p-value hack yourself — even if you think you are being careful — because the mechanism is more subtle than most people realise.
