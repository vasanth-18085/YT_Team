# V18 — Multiple Testing Correction — Clean Script

**Title:** p-value Hacking: How to Avoid Fooling Yourself
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

You tested 14 forecasting models. Five of them have p-values below 0.05. You are excited — five profitable strategies. But here is the uncomfortable math that nobody in the YouTube quant space talks about.

If you test 14 random models on random data — completely meaningless noise — the probability that at least one passes p less than 0.05 is 1 minus 0.95 to the power of 14, which equals 51 percent. You have a coin-flip chance of finding a significant result even when there is no signal at all. And you tested 14. And you found 5. How many of those 5 are real?

[INFORMATION GAIN] I implemented three correction methods — Bonferroni, Holm step-down, and Benjamini-Hochberg FDR — in the MultipleTestingCorrector class. After applying BH-FDR correction to my 14 model results, only 2 of the 8 apparently significant models survived. TiDE and LSTM. The other 6 were statistical flukes — they appeared significant because I tested enough models that random variation was guaranteed to produce false positives. Without this correction, I would have deployed capital on 6 strategies with no real edge.

Let me show you exactly how each correction works and when to use which one.

---

## SECTION 2 — THE MULTIPLE TESTING PROBLEM (2:00–10:00)

The multiple testing problem is the single most ignored concept in quantitative finance research. Let me explain it from first principles.

When you run a statistical test at significance level alpha equals 0.05, you accept a 5 percent chance of a false positive. That means if the strategy has no real edge, there is still a 5 percent chance the backtest looks significant just from random variation. This is the definition of alpha.

Run one test. False positive probability: 5 percent. Manageable. You are wrong 1 in 20 times.

Run 20 tests. The probability that at least one false positive appears is 1 minus the probability that all 20 are true negatives: 1 minus 0.95 to the power of 20 equals 64 percent. Two-thirds of the time, at least one random strategy looks significant.

Run 100 tests. At least one false positive probability: 99.4 percent. You are virtually guaranteed to find something significant in pure noise.

This is not hypothetical. In practice, a quant researcher testing different configurations — architectures, hyperparameters, feature sets, training windows — typically evaluates hundreds of combinations. Every configuration is an implicit hypothesis test. The 14 models I compared in video 7 were the finalists. But before those 14, I tried different feature combinations, different lookback periods, different training splits. The true number of implicit tests was closer to 200.

[INFORMATION GAIN] This is why so many published backtesting results fail when deployed live. The researcher tested 50 strategies, published the 2 that worked, and the reader assumes those 2 were the only ones considered. This is called data snooping or p-value hacking. The honest report would say: we tested 50 strategies, 8 appeared significant at p less than 0.05, and after correction for all 50 tests, 2 remain significant. Most honest quant researchers find that the corrected number is much smaller than the raw count.

Here is the practical damage. You find 5 significant strategies. You allocate capital across all 5 to diversify. But 3 of them have no real edge. Those 3 are generating random returns with a slight cost drag from execution. They are diluting the performance of the 2 real strategies and adding unnecessary risk. Your portfolio Sharpe drops from 0.85 (if you only used the 2 real ones) to 0.52 (diluted by the 3 fakes). Multiple testing correction prevents this by identifying which results to trust.

---

## SECTION 3 — BONFERRONI: THE CONSERVATIVE BASELINE (10:00–16:00)

The simplest correction. Divide the significance threshold by the number of tests.

If you ran 14 tests at alpha equals 0.05, the corrected threshold is 0.05 divided by 14 equals 0.0036. A p-value of 0.03 — which looked significant before — is now insufficient. You need p less than 0.0036 to declare significance.

The MultipleTestingCorrector class in `src/m7_validation/statistical_tests.py` implements this:

```python
class MultipleTestingCorrector:
    def correct(
        self,
        p_values: np.ndarray,
        method: str = "bh",
        alpha: float = 0.05,
    ) -> Result:
        n = len(p_values)

        if method == "bonferroni":
            corrected = np.minimum(p_values * n, 1.0)
            rejected = corrected < alpha
```

The formula is clean: multiply each raw p-value by the number of tests. If the result exceeds 1.0, clip to 1.0. Then compare against the original alpha. This is mathematically equivalent to dividing alpha by n and comparing raw p-values against the lower threshold.

What Bonferroni controls is the family-wise error rate (FWER) — the probability of making even one false positive across all tests. At FWER equals 0.05, there is at most a 5 percent chance that any of your declared significant results are false.

Let me apply this to my 14 models. Corrected threshold: 0.0036. The raw p-values: TiDE 0.001, LSTM 0.003, GRU 0.008, LightGBM 0.009, TCN 0.012, XGBoost 0.015, N-BEATS 0.035, N-HiTS 0.047, iTransformer 0.045. Only TiDE at 0.001 survives Bonferroni. LSTM at 0.003 barely misses (0.003 times 14 equals 0.042 which is below 0.05 — actually it does survive). So 2 survive: TiDE and LSTM.

[INFORMATION GAIN] Bonferroni has a critical weakness: it is too conservative. It treats every test as independent, which they are not. Models that share the same features and training data are correlated — if LSTM works, GRU probably also works because they share similar architectures and learned similar patterns. Bonferroni ignores this correlation and applies the full penalty regardless. The result: it often rejects real strategies alongside the false ones. For exploratory research where you want to identify promising candidates for further testing, Bonferroni is overly strict. But for final deployment decisions where a false positive means real capital loss, the conservatism is appropriate.

---

## SECTION 4 — HOLM STEP-DOWN: MORE POWER, SAME GUARANTEE (16:00–22:00)

Holm's step-down procedure controls the same family-wise error rate as Bonferroni but finds more significant results. It is uniformly more powerful — there is no scenario where Bonferroni rejects more hypotheses than Holm.

The procedure: sort all p-values from smallest to largest. Compare the smallest p-value against alpha divided by N. If it passes, move to the next and compare against alpha divided by N minus 1. Continue until the first failure. Everything from that point onward is non-significant.

```python
if method == "holm":
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]
    corrected = np.zeros(n)
    for i, p in enumerate(sorted_p):
        corrected[sorted_idx[i]] = min(p * (n - i), 1.0)
    # Enforce monotonicity
    corrected[sorted_idx] = np.maximum.accumulate(
        corrected[sorted_idx]
    )
    rejected = corrected < alpha
```

Let me walk through my 14 models step by step.

Step 1: TiDE has p equals 0.001. Compare against 0.05 divided by 14 equals 0.0036. 0.001 is less than 0.0036. Significant. Continue.

Step 2: LSTM has p equals 0.003. Compare against 0.05 divided by 13 equals 0.0038. 0.003 is less than 0.0038. Significant. Continue.

Step 3: GRU has p equals 0.008. Compare against 0.05 divided by 12 equals 0.0042. 0.008 is greater than 0.0042. Not significant. Stop.

Result: 2 models survive (TiDE and LSTM). In this case, the same as Bonferroni. But notice the thresholds were more lenient at each step: 0.0036, 0.0038, 0.0042 instead of a flat 0.0036. With more tests and more borderline p-values, Holm typically rejects 1 to 3 more hypotheses than Bonferroni.

[INFORMATION GAIN] Here is the practical rule. There is never a reason to use Bonferroni when Holm exists. Holm controls the exact same error rate and will always find at least as many significant results. The computation is marginally more complex (sorting and stepping) but trivial to implement. If someone presents Bonferroni-corrected results, they are being unnecessarily strict and potentially missing real strategies.

---

## SECTION 5 — BENJAMINI-HOCHBERG FDR: THE RECOMMENDED DEFAULT (22:00–30:00)

BH-FDR takes a fundamentally different philosophical approach from Bonferroni and Holm. Instead of controlling the probability of any false positive (FWER), it controls the expected proportion of false positives among all rejected hypotheses.

If your FDR threshold is 5 percent, you accept that on average 5 percent of your declared significant results might be false. If you reject 10 hypotheses, you expect about 0.5 of them to be false positives. This is a much more practical guarantee for exploratory research.

The procedure: sort p-values from smallest to largest. For each rank k (starting from 1), compute the FDR threshold: k divided by N times alpha. Scan from the largest k downward. Find the largest k where p sub k is less than or equal to k over N times alpha. All hypotheses from rank 1 through k are rejected.

```python
if method == "bh":
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]
    corrected = np.zeros(n)
    for i in range(n):
        corrected[sorted_idx[i]] = sorted_p[i] * n / (i + 1)
    corrected = np.minimum(corrected, 1.0)
    # Enforce monotonicity (decreasing from the largest)
    corrected[sorted_idx[::-1]] = np.minimum.accumulate(
        corrected[sorted_idx[::-1]]
    )
    rejected = corrected < alpha
```

Let me apply this to my 14 models. I need to scan from the bottom.

Rank 8: N-HiTS p equals 0.047. FDR threshold: 8 divided by 14 times 0.05 equals 0.0286. 0.047 is greater than 0.0286. No.

Rank 7: N-BEATS p equals 0.035. FDR threshold: 7 over 14 times 0.05 equals 0.0250. 0.035 is greater. No.

Rank 6: XGBoost p equals 0.015. Threshold: 6/14 times 0.05 equals 0.0214. 0.015 is less than 0.0214. Yes. Largest k equals 6.

So all ranks 1 through 6 are significant: TiDE, LSTM, GRU, LightGBM, TCN, and XGBoost.

Wait — 6 models pass BH-FDR versus only 2 for Bonferroni and Holm? That is a dramatically different conclusion. BH-FDR says 6 of your models have a real edge. Bonferroni says only 2.

[INFORMATION GAIN] This huge difference is exactly why the choice of correction method matters so much. BH-FDR is more appropriate for research where you want to identify a broad set of candidates for further investigation — if one or two in the group are false positives, that is an acceptable cost for not missing 4 real strategies. Bonferroni is appropriate when each rejection leads directly to a capital deployment decision and you cannot afford any false positives.

My recommendation: use BH-FDR during the research phase to build your candidate set. Then use Bonferroni or Holm on the final shortlist before deploying actual capital. Two rounds of correction with different stringency at different stages.

---

## SECTION 6 — APPLYING THE CORRECTOR TO THE FULL PIPELINE (30:00–36:00)

The MultipleTestingCorrector has an `apply_to_ablation` method that integrates directly with the ablation results from the walk-forward validation:

```python
def apply_to_ablation(
    self,
    report: dict,
    method: str = "bh",
    alpha: float = 0.05,
    metric: str = "sharpe",
) -> dict:
    """Add corrected p-values and reject flags to ablation report."""
    models = list(report.keys())
    p_values = np.array([report[m].get("p_value", 1.0) for m in models])
    result = self.correct(p_values, method=method, alpha=alpha)

    for i, model in enumerate(models):
        report[model]["corrected_p"] = float(result.corrected_pvalues[i])
        report[model]["rejected"] = bool(result.rejected[i])
        report[model]["correction_method"] = method

    return report
```

This takes the ablation report dictionary — each model maps to a dictionary containing Sharpe, max drawdown, p-value, and other walk-forward metrics — and adds three new fields: corrected_p (the adjusted p-value), rejected (boolean - is this model significant after correction?), and correction_method (which method was used).

After calling this, you can filter your model list to only the rejected equals True entries. These are the models with statistically defensible performance.

Let me show how this fits into the full analysis flow. Step 1: run 14 models through 6-fold walk-forward validation. Each model gets a distribution of Sharpe ratios across folds. Step 2: for each model, compute the p-value testing whether its Sharpe is significantly different from zero. Use a one-sample t-test on the 6 fold Sharpe values. Step 3: feed all 14 p-values into the MultipleTestingCorrector. Step 4: filter to rejected equals True models only.

[INFORMATION GAIN] There is a subtlety about what counts as a test. I said the true number of tests is closer to 200 than 14 because I tried many configurations before arriving at the 14 finalists. In practice, I use N equals 14 for the formal correction because the 14 models were pre-specified before the walk-forward validation. The earlier exploratory testing was done on a separate data split. If you did your exploration on the same data that you use for final testing, then you must inflate N to include all the exploration — and your corrected thresholds will be much stricter. This is why clean data hygiene (separate exploration and validation sets) is so important. It lets you use a smaller N for correction and retain more power.

---

## SECTION 7 — PRACTICAL GUIDELINES AND THE CLOSE (36:00–40:00)

Let me give you five rules I follow for honest statistical testing.

Rule one: always report the total number of hypotheses tested. Not just the ones that worked. Not just the finalists. The full count. If you tested 47 model configurations, say 47.

Rule two: use BH-FDR as your default method. It provides a practical balance between false discovery control and power. Switch to Bonferroni only when the cost of a false positive is catastrophic — specifically when each significant result directly triggers a capital deployment decision.

Rule three: keep a research journal. Log every model tested, every configuration tried, every result — successes and failures. The ExperimentTracker from the next few videos automates this. The journal is both the honest denominator for your correction and a defense against unconscious p-value hacking.

Rule four: separate your exploration data from your validation data. Do all your experimentation (feature selection, model selection, hyperparameter tuning) on one data split. Then run the final walk-forward validation on a completely separate split. This lets you use a smaller N for the formal correction because the exploration tests were on different data.

Rule five: the mindset shift. Significance is not a property of a strategy. It is a property of a strategy in the context of all other strategies you tested. The same backtest can be significant if it was the only one you ran and insignificant if it was one of 200. Multiple testing correction makes this context explicit.

Three numbers from this video. 51 percent — the probability of finding at least one significant result in 14 random tests at the 0.05 level. 2 versus 8 — the number of models that survive correction versus the raw count. And 3x — the typical ratio of BH-FDR rejections to Bonferroni rejections in real quant research.

Next video takes this further. Correction handles the quantity of tests. But what about the quality of the backtest itself? The Deflated Sharpe Ratio asks: given how many things you tried, is this Sharpe ratio still impressive? And the Probability of Backtest Overfitting tells you whether your walk-forward framework is trustworthy at all.

---

## Information Gain Score

**Score: 7.5/10**

Strong on the mathematical framework, the step-by-step Holm/BH-FDR walkthrough, and the practical 14-model application. The contrast between 2 survivors (Bonferroni) and 6 survivors (BH-FDR) is a powerful visual. The five practical rules provide actionable guidance.

**Before filming, add:**
1. A table showing all 14 models with raw and corrected p-values side by side
2. Screen recording of running the correction code and seeing models get rejected
3. Your actual research journal showing the full count of configurations tested
4. A before/after portfolio Sharpe comparison: using all 8 raw significant models vs only the 2 corrected ones
