# V7 — Testing 14 Forecasting Models — Hook & Intro

**Video Title:** ARIMA vs LSTM vs Transformers: I Tested Them All (Spoilers: Not What You Think)
**Date:** 10 April 2026

---

## Hook Question

If someone told you that a simple linear model beats a transformer at predicting stock returns — would you believe them?

## Credibility

I trained and validated 14 forecasting models on the same dataset with the same walk-forward protocol — from ARIMA and Ridge regression to LSTMs, Temporal Fusion Transformers, and gradient-boosted trees. The results completely broke my assumptions about which model families work best for financial time series.

## Why Now (R.A.I.N.Y — N)

New model architectures are being published monthly — foundation models, time-series transformers, Mamba, you name it. But nobody is benchmarking them head-to-head on real financial data with proper walk-forward validation. This video fills that gap with results you cannot find anywhere else right now.

## Video Structure

In this video you are going to see every model, every hyperparameter configuration, and every performance metric side by side. I will show you the actual accuracy tables, the training times, and the stability across folds. By the end you will know which models are worth your time for stock return prediction and which ones are overrated hype.

## Open Loop

But first there is a result that genuinely shocked me when I saw it — a model I almost did not bother testing came out on top in four out of six folds. Let me show you why.
