# V18 — Multiple Testing Correction — Final Script

**Title:** p-Value Hacking in Quant: How to Avoid Fooling Yourself
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — HOOK (0:00–2:00)

[INFORMATION GAIN] You test 14 models. Five come out with p-values below 0.05. You think you found five winners. You probably did not. With multiple testing, false positives are expected. If you do not correct for this, your best model might just be the luckiest model.

This video shows the exact correction framework I use: Bonferroni, Holm, and Benjamini-Hochberg FDR, and when each is appropriate.

---


[CTA 1]
By the way, if you want the full MLQuant build resources in one place, I put together a free starter pack with the repo map, workflow checklist, and implementation notes. It is built for this exact stage of the journey. Grab it here: [INSERT PRIMARY LINK]

## SECTION 2 — WHY MULTIPLE TESTING BREAKS MODEL SELECTION (2:00–8:00)

If one test is run at $\alpha = 0.05$, false positive risk is 5%.
If $m$ independent tests are run, family-wise false positive risk is approximately:

$$1 - (1-\alpha)^m$$

For $m=14$, this is:

$$1 - 0.95^{14} \approx 0.513$$

That means a 51.3% chance that at least one "significant" result is false.

[INFORMATION GAIN] This is the hidden leak in most model-comparison workflows. People are strict about train/test separation but completely loose about statistical multiplicity.

---

## SECTION 3 — BONFERRONI: SAFE BUT HARSH (8:00–14:00)

Bonferroni correction:

$$\alpha_{adj} = \frac{\alpha}{m}$$

For $\alpha=0.05$, $m=14$:

$$\alpha_{adj} = 0.00357$$

Only p-values below 0.00357 are significant.

```python
def bonferroni(pvals, alpha=0.05):
    m = len(pvals)
    thr = alpha / m
    return [p < thr for p in pvals], thr
```

Pros:
- controls family-wise error strictly

Cons:
- high false negatives
- too conservative when models are correlated

[INFORMATION GAIN] In quant model grids, tests are rarely independent. Similar model families share errors. Bonferroni assumes independence-like behavior and can reject too aggressively.

---

## SECTION 4 — HOLM: STEP-DOWN FWER CONTROL (14:00–20:00)

Holm procedure is less conservative than Bonferroni while still controlling family-wise error.

Steps:
1. Sort p-values ascending: $p_{(1)} \le ... \le p_{(m)}$
2. Compare $p_{(i)}$ to $\alpha/(m-i+1)$
3. Stop at first failure; all remaining are non-significant

```python
def holm(pvals, alpha=0.05):
    m = len(pvals)
    order = np.argsort(pvals)
    sig = np.zeros(m, dtype=bool)
    for rank, idx in enumerate(order, start=1):
        thr = alpha / (m - rank + 1)
        if pvals[idx] <= thr:
            sig[idx] = True
        else:
            break
    return sig
```

Holm is a strong default when false positives are expensive and you still want more power than Bonferroni.

---

## SECTION 5 — BENJAMINI-HOCHBERG FDR: PRACTICAL DEFAULT (20:00–30:00)

Benjamini-Hochberg controls expected false discovery rate rather than family-wise error.

Condition:

$$p_{(i)} \le \frac{i}{m} q$$

Where $q$ is target FDR (commonly 0.05 or 0.10).

```python
def benjamini_hochberg(pvals, q=0.05):
    m = len(pvals)
    order = np.argsort(pvals)
    sorted_p = np.array(pvals)[order]

    cutoff = -1
    for i, p in enumerate(sorted_p, start=1):
        if p <= (i / m) * q:
            cutoff = i

    sig = np.zeros(m, dtype=bool)
    if cutoff > 0:
        sig[order[:cutoff]] = True
    return sig
```

[INFORMATION GAIN] For strategy research, BH-FDR is often the right tradeoff: it limits expected false discoveries while preserving enough sensitivity to keep genuinely useful models.

---

## SECTION 6 — APPLIED EXAMPLE: 14 MODEL COMPARISON (30:00–35:00)

Suppose 14 p-values from out-of-sample model-vs-benchmark tests:

```
0.001, 0.008, 0.012, 0.035, 0.047, 0.072, 0.11, 0.14, 0.21, 0.29, 0.33, 0.41, 0.55, 0.73
```

Results:
- Uncorrected (<0.05): 5 significant
- Bonferroni: 1 significant
- Holm: 2 significant
- BH-FDR: 2 significant

Interpretation: three of the original five "winners" were likely luck.

---

## SECTION 7 — INTEGRATION INTO PIPELINE (35:00–38:00)

Selection policy used in this system:
1. Run all model tests on same walk-forward folds.
2. Compute p-values on net-of-cost returns.
3. Apply BH-FDR at $q=0.05$.
4. Among surviving models, choose by stability (Sharpe std across folds).

[INFORMATION GAIN] Significance without stability is dangerous. A model can survive correction but still be operationally fragile. Statistical and operational filters must both pass.

---


[CTA 2]
Quick reminder before we continue, if this is helping you, the free MLQuant starter pack is in the description and it goes deeper than what we can fit in one video. Link: [INSERT PRIMARY LINK]

## SECTION 8 — CLOSE (38:00–40:00)

Multiple testing correction is not academic overhead. It is anti-self-deception infrastructure.

Next video: deflated Sharpe and PBO, where we adjust apparent performance for selection bias and backtest overfitting risk.

---

## Information Gain Score

**Score: 8/10**

Strong practical value from explicit correction methods, threshold math, and direct integration into model-selection policy.

**Before filming, add:**
1. Your actual 14-model p-value table
2. Side-by-side selected-model sets under each correction
3. A case where uncorrected winner failed live or on holdout
