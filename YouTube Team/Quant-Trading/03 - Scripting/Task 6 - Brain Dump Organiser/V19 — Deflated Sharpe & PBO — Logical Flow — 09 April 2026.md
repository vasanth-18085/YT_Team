# V19 — Deflated Sharpe & PBO — Logical Flow — 09 April 2026

**Title:** Is Your Backtest Real or Luck? The Deflated Sharpe Test
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** Your backtest shows a Sharpe ratio of 1.5. Looks great. But you tested 14 different model configurations before finding this one. The Deflated Sharpe Ratio adjusts your observed Sharpe for the number of trials you ran, the skewness of your returns, and the kurtosis. After deflation, your Sharpe drops to 0.7 — still positive, but much less impressive. Then I run the Probability of Backtest Overfitting (PBO) test, which tells me there is a 35% chance that the strategy I chose as best in-sample is actually worst out-of-sample. These two tests are the last line of defense against self-delusion in quantitative research.

## 2. WHY SHARPE RATIOS LIE (2:00–10:00)

The Sharpe ratio is the most commonly cited performance metric in quant finance. But it has a fundamental flaw: it does not account for how many strategies you tried before reporting it.

Here is the problem. If you test N random strategies on the same data, the expected maximum Sharpe ratio among them grows as approximately sqrt(2 * log(N)). For N=14 models, E[max(SR)] ≈ 0.6. For N=100 models, E[max(SR)] ≈ 1.0. For N=1000, E[max(SR)] ≈ 1.2. This means that even if EVERY model is random noise with zero true edge, you will observe Sharpe ratios of 1.0+ just by picking the best of 100 random trials.

This is the selection bias problem. When you report "my strategy has Sharpe 1.5," you are reporting the maximum of N trials. Unless you account for N, the Sharpe is inflated by luck.

**[INFORMATION GAIN]** The standard Sharpe ratio formula assumes you tested exactly one strategy. If you tested one, the sampling distribution is straightforward and a Sharpe of 1.0 is genuinely impressive. But most quant researchers test dozens of combinations — different models, features, lookback windows, thresholds. Each variation is a separate trial. The corrected Sharpe must reflect all of them, not just the winner.

## 3. THE DEFLATED SHARPE RATIO (10:00–22:00)

The Deflated Sharpe Ratio (DSR) from Bailey and de Prado (2014) formalizes this correction.

Step 1: Compute the observed Sharpe ratio (SR_observed) from your final strategy's out-of-sample returns.

Step 2: Compute the expected maximum Sharpe ratio under the null hypothesis that all N strategies have zero true edge. This depends on N (number of trials), T (number of observations), skewness and kurtosis of returns.

Formula for variance of SR: Var(SR) = (1 - skew * SR + ((kurt - 1) / 4) * SR^2) / T. This accounts for the fact that non-normal returns (high kurtosis, negative skewness) make Sharpe estimation noisier.

Formula for expected max SR: E[max(SR)] ≈ sqrt(Var(SR)) * (sqrt(2 * log(N)) - (log(pi) + log(log(N))) / (2 * sqrt(2 * log(N)))). This is a result from extreme value theory.

Step 3: Deflated SR = SR_observed - E[max(SR)]. If Deflated SR > 0, the strategy has genuine edge beyond what luck alone would produce. If Deflated SR ≤ 0, the strategy's performance is explainable by selection bias.

The implementation in `src/m7_validation/statistical_tests.py` as class DeflatedSharpe. The `test()` method takes returns, n_trials, and optional skewness/kurtosis. It returns a DeflatedResult namedtuple with observed_SR, deflated_SR, expected_max_SR, p_value, is_significant (p < 0.05).

**[INFORMATION GAIN]** In my pipeline, observed SR across 6 walk-forward folds averages 0.85. N_trials = 14 (models tested). Expected max SR ≈ 0.6. Deflated SR = 0.85 - 0.6 = 0.25. The p-value for this is 0.08 — NOT significant at the 5% level. This means that even though the observed Sharpe looks decent, I cannot confidently reject the hypothesis that it arose from testing 14 models and picking the best one. I need more data or fewer trials to achieve significance.

The practical implication: if I had tested only 3 models (fewer trials), the same observed SR = 0.85 would have a deflated SR of 0.45 with p = 0.02 — significant. Fewer trials means less selection bias, which means your observed results are more trustworthy.

## 4. PROBABILITY OF BACKTEST OVERFITTING (PBO) (22:00–32:00)

PBO goes deeper than DSR. Instead of adjusting the Sharpe ratio, it asks: what is the probability that the strategy you selected as best in-sample actually underperforms out-of-sample?

The method is Combinatorial Symmetric Cross-Validation (CSCV) from Bailey, Borwein, de Prado, and Zhu (2017). Here is how it works:

Step 1: Split your data into S partitions (I use S=16, must be even).

Step 2: For each combination of S/2 partitions as in-sample and S/2 as out-of-sample (there are C(S, S/2) combinations), determine which strategy performed best in-sample and check how it ranked out-of-sample.

Step 3: PBO = fraction of combinations where the in-sample best is below median out-of-sample. If PBO = 0.5, the in-sample selection is no better than random — complete overfitting. If PBO = 0, every time the best in-sample strategy was also best out-of-sample — no overfitting at all.

Implementation: the BacktestOverfitDetector class with n_partitions=16. It takes a matrix of strategy returns (rows = time periods, columns = strategy variants). It outputs PBO percentage, the distribution of relative in-sample-to-out-of-sample ranks, and visualization.

**[INFORMATION GAIN]** My pipeline's PBO test result: PBO = 0.35. This means 35% of the time, the strategy selected as best in-sample would rank below median out-of-sample. This is not catastrophic (PBO < 0.50 means more good than bad), but it is a warning that there is meaningful overfitting. The implication: I should not blindly trust that the best in-sample model (TiDE in my case) is truly the best. I should consider ensemble methods or model averaging rather than winner-take-all selection.

## 5. MINIMUM BACKTEST LENGTH (MinBTL) (32:00–36:00)

MinBTL answers the question: how much historical data do I need for my backtest to be statistically relevant?

Formula: MinBTL = (N * (e^(z^2/2) - 1)) / (annualized_SR^2). Where N is the number of strategies tested, z is the standard normal quantile for desired significance (z = 1.96 for 95%), and annualized_SR is the target Sharpe ratio.

For N=14 strategies and target SR=0.85: MinBTL ≈ 8.3 years of daily data. I have 5 years of data. This means my backtest length is marginally insufficient — the result is suggestive but not conclusive.

**[INFORMATION GAIN]** MinBTL reveals a painful truth: most individual backtests are too short to be conclusive. The solution is not always to get more data (markets change, and 20-year-old data may not be relevant). Instead, the approach is to: (1) reduce N by being more disciplined about what you test, (2) use ensemble methods to leverage multiple signals rather than selecting one winner, (3) supplement with out-of-distribution stress testing (test on markets you did not train on — e.g., Japanese equities if you trained on US).

## 6. PUTTING IT ALL TOGETHER (36:00–38:00)

The complete statistical validation workflow runs in sequence: First, multiple testing correction (V18) to filter which models have genuine significance. Second, deflated Sharpe to check whether the surviving models' Sharpe ratios are evidence of real edge or selection bias. Third, PBO to test whether the best in-sample model is truly better out-of-sample. Fourth, MinBTL to verify you have enough data for conclusions.

My pipeline: after BH-FDR correction, 2 models survive. After DSR adjustment, the p-value is 0.08 — borderline. PBO is 0.35 — some overfitting. MinBTL suggests I need 8 years, I have 5.

The honest conclusion: there is signal here, but it is not as strong as the raw numbers suggest. This is exactly the kind of honest assessment that separates real quant research from backtest fantasy.

## 7. THE CLOSE (38:00–40:00)

Deflated Sharpe and PBO are the honesty tests. They force you to confront how much of your backtest performance is real edge versus selection luck. Using them does not make your results look as impressive, but it makes them trustworthy — and in live trading, trustworthy matters infinitely more than impressive.

Next video: the performance tearsheet. How to present your strategy results the way professional quant teams do — one page, every metric that matters, visually clear.

[NEEDS MORE] Your actual DSR computation with real numbers. The PBO distribution histogram. A story about a strategy that looked great until PBO killed it.
