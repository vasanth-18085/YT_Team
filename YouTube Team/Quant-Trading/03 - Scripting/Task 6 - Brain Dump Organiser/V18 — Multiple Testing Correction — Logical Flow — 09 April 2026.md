# V18 — Multiple Testing Correction — Logical Flow — 09 April 2026

**Title:** p-value Hacking: How to Avoid Fooling Yourself
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** You tested 14 forecasting models. One of them had p < 0.05. You declare victory. But here is the uncomfortable math: if you test 14 random models on random data, 0.7 of them (14 * 0.05) are expected to pass p < 0.05 by pure chance. That is not an edge — that is a lucky coin flip. I implemented three correction methods (Bonferroni, Holm, Benjamini-Hochberg FDR) in the statistical testing module, and after correction, only 2 of my 5 apparently significant models survived. The other 3 were statistical flukes.

## 2. THE MULTIPLE TESTING PROBLEM EXPLAINED (2:00–10:00)

The multiple testing problem is one of the most important and most ignored concepts in quantitative finance. Every time you run a backtest and check if the result is significant, you are performing a statistical test. Run one test and the chance of a false positive is 5% (at alpha = 0.05). Run 20 tests and the chance that at least one false positive appears is 1 - (1 - 0.05)^20 = 64%. Run 100 tests and it is 99.4% — you are virtually guaranteed to find something significant even in random data.

This is not an abstract concern. In practice, quant researchers test dozens or hundreds of model configurations. Different architectures (ARIMA, LSTM, transformer, etc.), different hyperparameters, different feature sets, different training windows. Every combination is an implicit hypothesis test. The total number of tests is not 14 (the number of final models) — it is the total number of configurations you tried before selecting those 14. If you tried 200 combinations, the correction should account for 200, not 14.

**[INFORMATION GAIN]** This is why many published backtesting results fail in live trading. The researcher tried 50 strategies, published the 2 that worked, and the reader assumes those 2 were the only ones tested. This is called p-value hacking or data snooping. The honest way to report: we tried N strategies, M appeared significant, and after correction K remain significant. Most honest quant researchers find K is much smaller than M.

## 3. CORRECTION METHOD 1: BONFERRONI (10:00–16:00)

The simplest and most conservative correction. Divide the significance threshold by the number of tests: alpha_corrected = alpha / N_tests. If alpha = 0.05 and you ran 14 tests, the new threshold is 0.05 / 14 = 0.0036. Now a p-value of 0.01 is not significant anymore — you need p < 0.0036.

The implementation in `src/m7_validation/statistical_tests.py` via the MultipleTestingCorrector class: corrected_pvalues = min(1, original_p * n_tests). The rejected mask is corrected_p < alpha.

Pros: mathematically rigorous. Controls the family-wise error rate (FWER) — the probability of even one false positive. Extremely conservative.

Cons: very low power. With 14 tests, only strategies with p < 0.004 survive. This means you will also reject many real effects alongside the false ones. In practice, Bonferroni is too strict for exploratory research.

When to use Bonferroni: when a false positive is catastrophic. If you are deploying capital based on the result and one false positive could cost you $100K+, Bonferroni is appropriate because the cost of a miss is low compared to the cost of a false positive.

## 4. CORRECTION METHOD 2: HOLM STEP-DOWN (16:00–22:00)

Holm is a less conservative version of Bonferroni that controls the same FWER but has higher power (rejects more true effects).

The procedure: sort all p-values from smallest to largest. For the smallest p-value, compare against alpha / N. If significant, move to the next: compare against alpha / (N-1). Continue until the first non-rejection, then stop. Everything after that is non-significant.

Example with 14 models: sorted p-values are 0.001, 0.008, 0.012, 0.035, 0.047, 0.089, ... . Compare 0.001 vs 0.05/14=0.004: significant. Compare 0.008 vs 0.05/13=0.0038: NOT significant. Stop. Only the first model survives. Holm rejected one less than Bonferroni would have (in this case both reject the same number, but in general Holm rejects more because the thresholds increase at each step).

**[INFORMATION GAIN]** Holm is uniformly more powerful than Bonferroni — it will always find at least as many significant results, usually more. There is no reason to use Bonferroni when Holm exists, unless you need the absolute simplest calculation for manual checking.

## 5. CORRECTION METHOD 3: BENJAMINI-HOCHBERG FDR (22:00–30:00)

This is the recommended default for quant research. Instead of controlling the probability of any false positive (FWER), FDR controls the expected proportion of false positives among all rejected hypotheses. If your FDR threshold is 5%, you accept that 5% of your declared significant results might be false — but you will find many more true results than FWER methods.

Procedure: sort p-values from smallest to largest. For each rank k, compare p_k against (k/N) * alpha. Find the largest k where this holds. All hypotheses up to and including k are rejected.

Example with 14 models at alpha = 0.05: p-value 0.001 vs (1/14)*0.05=0.0036 → significant. p-value 0.008 vs (2/14)*0.05=0.0071 → NOT significant. p-value 0.012 vs (3/14)*0.05=0.0107 → NOT significant.

Wait — we need to scan from the bottom. Largest k where p_k <= (k/14)*0.05. Check p_5=0.047 vs (5/14)*0.05=0.018 → no. Check p_3=0.012 vs (3/14)*0.05=0.0107 → no. Check p_2=0.008 vs (2/14)*0.05=0.0071 → no. Check p_1=0.001 vs (1/14)*0.05=0.0036 → YES. Largest k=1, so only 1 model is significant.

**[INFORMATION GAIN]** In practice with real trading data (not this toy example), BH-FDR typically rejects 2-3x more hypotheses than Bonferroni or Holm. This matters because rejecting too many real strategies is almost as costly as accepting false ones — you are leaving alpha on the table. For most quant research where you are exploring many models, FDR is the right trade-off: accept a small proportion of false discoveries to gain substantially more true discoveries.

## 6. APPLYING TO THE FULL PIPELINE (30:00–36:00)

In my 14-model forecasting comparison from V7, the raw p-values from walk-forward backtests were: ARIMA 0.23, Prophet 0.45, LSTM 0.003, GRU 0.008, TCN 0.012, N-BEATS 0.035, N-HiTS 0.047, TiDE 0.001, DLinear 0.089, PatchTST 0.067, iTransformer 0.045, Chronos 0.078, XGBoost 0.015, LightGBM 0.009.

Uncorrected significant at p < 0.05: 8 models (LSTM, GRU, TCN, N-BEATS, N-HiTS, TiDE, XGBoost, LightGBM).

After BH-FDR correction: 2 models survive (TiDE and LSTM). The other 6 were close enough to significance that they appeared real but were likely inflated by multiple testing.

After Bonferroni correction: 1 model survives (TiDE at 0.001).

**[INFORMATION GAIN]** This result matches intuition from V7: TiDE and LSTM were the consistently best performers across all walk-forward folds. The other models that appeared significant on raw p-values were only significant in 2-3 of 6 folds — their aggregate p-value was inflated by a few good folds, not consistent outperformance. Multiple testing correction strips away the lucky folds and reveals only the models with genuine edge.

## 7. PRACTICAL GUIDELINES AND THE CLOSE (36:00–40:00)

Rules I follow: always report the total number of tests, not just the finalists. Use BH-FDR as the default method. Use Bonferroni only when the cost of a false positive is extreme (e.g., deploying $1M on a strategy). Keep a research journal that logs every model tested, including the failures — this is the honest denominator.

The mindset shift: significance is not a property of a strategy. It is a property of a strategy in the context of all other strategies tested. The same backtest can be significant if it was the only one you ran, and insignificant if it was one of 200. Multiple testing correction makes this explicit.

Next video: deflated Sharpe ratio and probability of backtest overfitting. We go beyond p-value correction to test whether the entire backtest framework is trustworthy.

[NEEDS MORE] Your actual 14-model p-values from real data. The spreadsheet showing correction calculations. A moment where you thought something was significant and correction saved you.
