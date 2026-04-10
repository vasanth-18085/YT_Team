# V2 — Why 90% of ML Backtests Are Lies — Logical Flow

**Title:** "The Backtesting Lie No One Talks About"
**Length:** ~40 min
**Date:** 09 April 2026

---

## 1. THE HOOK (0:00–1:30)

**[INFORMATION GAIN]** "If you've ever backtested an ML model on stock data and got amazing results — you probably cheated without knowing it. I know because I did it too. I built 14 forecasting models, got one with a backtest Sharpe of [tease number], and felt like a genius. Then I tested it properly. Here's what actually happened."

The bait: show a "fake" backtest first — beautiful equity curve, high Sharpe, looks incredible.

"This is a lie. And I'm going to show you exactly why."

---

## 2. THE THREE LIES OF BACKTESTING (1:30–8:30)

### Lie #1: Standard k-fold on time series

**[INFORMATION GAIN]** "Most ML tutorials use `train_test_split(shuffle=True)`. On time series, this is a guaranteed way to cheat. If your test set contains January 2023 and your training set contains December 2022 AND February 2023, you're literally seeing the future."

**[DIAGRAM SUGGESTION]** Draw a horizontal timeline showing:
- Row 1 (correct time-series split): Green "Train" block → Blue "Test" block → Red "Future" block
- Row 2 (shuffled split with data leakage): Green "Train" with red dots mixed in (showing February 2023 data mixed into training), Blue "Test" in middle, showing the model trained on FUTURE data

Label: "Shuffled split = model sees tomorrow's prices while 'training'"

Even sklearn's `TimeSeriesSplit` isn't enough for financial data because of...

### Lie #2: Label overlap (no purge)

**[INFORMATION GAIN]** "In our system, triple-barrier labels have a max holding period of 10 days. That means the label for day T depends on prices from day T through day T+10. If your training set ends at day T and your test set starts at day T+1, the training set used information about the test period through the label. This is label leakage, and standard time-series splits don't handle it."

**Example walkthrough:** "Say I'm running a model on Apple stock. I take a position on Day 100. The triple-barrier label depends on what happens Days 100–110. If I'm 'testing' on Day 101–105, and my 'training' goes up to Day 100, the training set KNOWS the price outcome from Days 101–105 through the Day 100 label. The test set is supposed to be unseen. It's not."

The fix: **purging** — remove the last `purge_window` (default: 5) training samples before each test fold.

Code from `purged_cv.py`:
```python
# Purge: remove last `purge_window` samples from training
train_end = max(train_start, test_start - self.purge_window)
```

**[DIAGRAM SUGGESTION]** Show Day-by-day label generation:
- Day 100: Label depends on prices Day 100–110
- Day 101: Label depends on prices Day 101–111
- Row diagram: Training [Days 1–95], Gap [Days 96–100 purged], Testing [Days 101–110]
- Label: "Purge removes the boundary where future info leaks backward"

### Lie #3: Autocorrelation leakage (no embargo)

**[INFORMATION GAIN]** "Even after purging, financial returns are autocorrelated. If you train on data right up to the purge boundary, your model memorizes patterns that persist into the test set. Embargo adds an additional gap AFTER the purge."

**Deep intuition:** "Financial returns aren't random. If returns are positive on Day 100, they're slightly more likely to be positive on Day 101. Your model can pick this up during training. But this autocorrelation pattern ALSO exists in your test set. So the model trained on the pattern from Days 1–100 can exploit the same pattern in Days 101–110. That's not a real trading signal — that's just momentum inertia, and it's ALWAYS there."

Config from `config.yaml`:
```yaml
walk_forward:
  embargo: 5     # samples removed at end of training
  purge: 5       # samples purged around val boundary
```

**[DIAGRAM SUGGESTION]** Three-panel comparison:
- Panel 1: "No Purge, No Embargo" — Returns line chart, red shaded region showing correlation bleeding from train into test
- Panel 2: "Purge Only" — Gap shown, but slight correlation still seeps through
- Panel 3: "Purge + Embargo" — Two gaps shown, autocorrelation fully suppressed
- Label: "Embargo = buffer zone for autocorrelation decay"

---

## 3. EMBARGO DEEP DIVE: Why You Can't Just Purge (8:30–11:30)

### The Autocorrelation Problem in Markets

**[INFORMATION GAIN]** "In many domains, you can get away with just purging. But financial returns have a special property: they're correlated with their own past. Not strongly, but enough to matter."

Show a correlation decay chart:
```
Autocorrelation of daily S&P 500 returns:
Lag 1:  0.08  (slight positive correlation)
Lag 2:  0.03
Lag 3:  0.01
Lag 5:  0.00
```

"A lag-1 correlation of 0.08 sounds tiny. But if your model is trained on Days 1–100 and tested on Days 101–110, the model can exploit this lag-1 pattern. It sees: 'When Day 100 goes up, Day 101 tends to go up.' That's ALWAYS true in your test set too. So the model wins, not because it found real alpha, but because it learned a market microstructure pattern that repeats."

### Embargo Window Logic

**[INFORMATION GAIN]** "The embargo window is a buffer zone. After you stop training, you skip a few days before you start testing. This allows market autocorrelation to decay naturally."

The question: **how long is 'a few days'?**
- Default config: `embargo_pct=0.01` (1% of test set size)
- If test set is 126 days, embargo ~= 1.26 days → rounds to 5 days
- Why 1%? Empirically, most autocorrelation in stock returns decays within 1% of your test window

**Advanced note (for curious viewers):** "If you're trading high-frequency or certain derivative products, you might need embargo_pct=0.05 (5%). If you're trading daily, 1% is typically enough."

Code from `PurgedWalkForwardCV`:
```python
embargo_samples = max(1, int(self.embargo_pct * (test_end - test_start)))
test_start = test_start + embargo_samples  # Skip first N days of test set
```

**[DIAGRAM SUGGESTION]** Timeline showing:
- Day 1–100: Training data
- Day 101–105: Embargo buffer (skipped — neither train nor test)
- Day 106–130: Test set (model evaluates here)
- Label: "Return autocorrelation decays in the embargo zone → test set is truly independent"

### Expanding vs Sliding Windows

"There's a choice: do you grow your training window (expanding) or slide it (fixed size)?"

- **Expanding (default):** Day 1–100 test, then Day 1–163 test, then Day 1–226 test. Training window grows. Pros: more data for later folds. Cons: distribution shift (early market conditions different from recent).
- **Sliding (alternative):** Day 1–100 test, then Day 64–163 test, then Day 127–226 test. Training window stays 504 days, slides forward. Pros: stable distribution. Cons: less data for early folds.

Config:
```yaml
expanding: True  # Set to False for sliding window
```

"In this system, we use expanding because we want the model to learn from the full history. But try both and see which gives more honest results on YOUR data."

---

## 4. THE FIX: PURGED WALK-FORWARD CV (11:30–21:30)

### What is walk-forward validation?

**[INFORMATION GAIN]** "Instead of one train/test split, you simulate what a real trader would do: train on available data, predict forward, then advance the window and repeat."

**Real trader analogy:** "A prop trader in 2020 didn't have access to 2023 data. They trained on 2018–2020, made predictions for 2021, then retrained on 2018–2021, predicted 2022, then retrained on 2018–2022, predicted 2023. Walk-forward CV mimics this: you move through time, always predicting into unseen future, never looking forward."

Walk-forward config (from `config.yaml`):
- initial_train_days: 504 (~2 years)
- val_days: 126 (~6 months)
- step_days: 63 (~3 months — retrain every quarter)
- n_splits: 6
- expanding window (training grows each fold)

**[DIAGRAM SUGGESTION]** 6-row timeline chart:
- Row 1 (Fold 0): Green [504d Train] → Red [126d Test]
- Row 2 (Fold 1): Green [567d Train] → Red [126d Test]
- Row 3 (Fold 2): Green [630d Train] → Red [126d Test]
- ... (Rows 3-6)
- Each row shifted by 63 days (step_days)
- Label: "Walk-forward = expanding training window, fixed test windows, advancing in time"

### The `PurgedWalkForwardCV` class

Full code walkthrough:

```python
class PurgedWalkForwardCV:
    def __init__(self, n_splits=5, purge_window=5, embargo_pct=0.01,
                 expanding=True, min_train_size=100):
```

Each parameter is a boundary condition:
- `purge_window=5` — removes 5 training samples before each test fold boundary (prevents label leakage from test into training)
- `embargo_pct=0.01` — removes 1% of test set size as additional buffer (lets autocorrelation decay)
- `expanding=True` — training window grows (alternative: sliding window)
- `min_train_size=100` — skips folds where training set is too small (needs minimum data to fit model)

**Deep reason for each:**
- **Purge:** Triple-barrier labels depend on future prices. A label generated on Day 100 reflects prices through Day 110. If you remove Days 96–100 from training, the training set no longer "knows" what happened in Days 101–110.
- **Embargo:** Even without label leakage, price momentum and autocorrelation let your model cheat. Embargo is a gap for these effects to dissipate.
- **Expanding:** More training data = more stable estimates. Sliding window is more conservative but doesn't leverage full history.
- **min_train_size:** If training set becomes too small, estimates become unreliable. Skip that fold rather than trust bad results.

**[INFORMATION GAIN]** The `CVFold` dataclass tracks exactly what happened at each fold:
```python
@dataclass
class CVFold:
    fold_id: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    n_train: int
    n_test: int
    n_purged: int = 0
    n_embargoed: int = 0
```

And `.summary()` gives you a clean table showing every fold's ranges and how many samples were purged/embargoed. This is the transparency. **[DIAGRAM SUGGESTION]** Show a CSV-like table:
```
| Fold | Train Start | Train End | Test Start | Test End | n_Train | n_Test | n_Purged | n_Embargoed |
|------|-------------|-----------|------------|----------|---------|--------|----------|-------------|
|  0   |     0       |    500    |    506     |    632   |  500    |  126   |    5     |      1      |
|  1   |     0       |    563    |    569     |    695   |  563    |  126   |    5     |      1      |
| ...  |    ...      |    ...    |    ...     |   ...    |   ...   |  ...   |   ...    |    ...      |
```

Label: "Fold summary table: confirms all boundary conditions were applied"

### The `AblationRunner` — systematic comparison

Show how `AblationRunner` wraps `PurgedWalkForwardCV`:
- Plugs in ANY list of `ModelWrapper` models
- Runs walk-forward CV across all folds for each model
- Computes metrics per fold, averages across folds
- Returns a tidy comparison DataFrame

```python
runner = AblationRunner(config, task="regression")
report = runner.run(models=[ARIMA(), LSTM(), PatchTST(), ...], X=features, y=targets)
# report is a DataFrame:
# | Model      | Mean_Sharpe | Std_Sharpe | Min_Sharpe | Max_Sharpe | Avg_Return | Avg_Drawdown | ... |
# | ARIMA      |     0.45    |    0.12    |    0.25    |    0.68    |    0.023   |     0.32     | ... |
# | LSTM       |     0.52    |    0.18    |    0.15    |    0.89    |    0.031   |     0.40     | ... |
# | PatchTST   |     0.61    |    0.14    |    0.38    |    0.93    |    0.042   |     0.28     | ... |
```

**[INFORMATION GAIN]** "Every single model comparison in this series uses this framework. No cherry-picking. No lucky splits. Walk-forward with purge and embargo, every single time."

---

## 5. THE STATISTICAL RIGOR LAYER (21:30–29:30)

### Why good CV isn't enough

"Even with proper walk-forward CV, you can STILL fool yourself. If you test 14 models and pick the best one, you're running 14 statistical tests. The more tests you run, the higher the chance of a false positive."

### Multiple Testing Correction

**[INFORMATION GAIN]** `MultipleTestingCorrector` — 4 correction methods:
- Bonferroni (most conservative)
- Holm (step-down Bonferroni)
- Benjamini-Hochberg FDR (default — controls false discovery rate)
- Benjamini-Yekutieli

```python
corrector = MultipleTestingCorrector(alpha=0.05, method="fdr_bh")
result = corrector.correct(p_values)
# result.summary → table of original p, corrected p, significant?
```

"I test 14 forecasting models. Without correction, 1-2 might look significant by chance. With BH-FDR correction at α=0.05, only the genuinely predictive ones survive."

### Deflated Sharpe Ratio (Bailey & de Prado, 2014)

**[INFORMATION GAIN]** "The deflated Sharpe ratio answers: given that I tried N strategies, what is the probability that the BEST Sharpe is a false positive?"

It adjusts for:
- Number of trials (more trials = more luck)
- Skewness of returns (asymmetric distributions inflate Sharpe)
- Excess kurtosis (fat tails inflate Sharpe)

Uses the expected maximum Sharpe under the null (Euler-Mascheroni correction):
```python
E[max(SR)] ≈ √(2·log(N)) - (log(π) + γ) / (2·√(2·log(N)))
```

### Probability of Backtest Overfitting (PBO)

**[INFORMATION GAIN]** `BacktestOverfitDetector` — two tests:
1. **PBO** — what fraction of train/test partition pairs show the "best" in-sample strategy performing WORST out-of-sample?
2. **MinBTL (Minimum Backtest Length)** — how many years of data do you need for this Sharpe to be significant?

"If PBO > 0.5, your best strategy is probably just luck. If MinBTL > your data length, you don't have enough history to trust the result."

### Why good CV isn't enough

"Even with proper walk-forward CV, you can STILL fool yourself. If you test 14 models and pick the best one, you're running 14 statistical tests. The more tests you run, the higher the chance of a false positive."

**Fun fact (optional tangent):** "There's a famous study: if you flip a coin 20 times for 100 different coins, at least one will show 'heads' 15+ times by pure luck. Same thing in backtesting. Test 14 models = 14 coin flips per fold = some will just look good."

### Multiple Testing Correction

**[INFORMATION GAIN]** `MultipleTestingCorrector` — 4 correction methods:
- **Bonferroni** (most conservative): p_corrected = p * N. If you test 14 models, multiply each p-value by 14. Safe, but rejects too many real signals.
- **Holm** (step-down Bonferroni): Adaptive version of Bonferroni. Less strict than pure Bonferroni.
- **Benjamini-Hochberg FDR (default)** — controls false discovery rate: "On average, how many of the 'significant' results are actually false?" If you reject 10 tests, maybe 0.5 are false positives (FDR=0.05). Much less strict than Bonferroni—useful when you have many tests but can tolerate some false positives.
- **Benjamini-Yekutieli**: FDR under general dependence (complex, rarely needed).

```python
corrector = MultipleTestingCorrector(alpha=0.05, method="fdr_bh")
result = corrector.correct(p_values)
# result.summary → table of original p, corrected p, significant?
```

**[DIAGRAM SUGGESTION]** Show 2 columns:
- Column 1: "Without Correction" — all 14 models, 3 highlighted as "significant" (but some are luck)
- Column 2: "With BH-FDR Correction" — same 14 models, only 1 highlighted as "significant" (the others were luck)
- Label: "Correction filters out the 'lucky winners'"

"I test 14 forecasting models. Without correction, 1-2 might look significant by chance. With BH-FDR correction at α=0.05, only the genuinely predictive ones survive."

### Deflated Sharpe Ratio (Bailey & de Prado, 2014)

**[INFORMATION GAIN]** "The deflated Sharpe ratio answers: given that I tried N strategies, what is the probability that the BEST Sharpe is a false positive?"

**Intuition:** "Imagine I run 100 random trading strategies. No skill, pure noise. The best one MUST have some positive Sharpe just by luck. The deflated Sharpe estimates: what is that expected lucky Sharpe? Then it subtracts that from your observed Sharpe to get the 'real' Sharpe accounting for luck."

It adjusts for:
- **Number of trials** (more trials = higher expected lucky Sharpe)
- **Skewness of returns** (if your returns are negatively skewed—more small gains, occasional crashes—the Sharpe ratio overstates true performance)
- **Excess kurtosis** (fat tails = extreme events more likely = Sharpe overstates stability)

The math uses the expected maximum Sharpe under the null (Euler-Mascheroni correction):
```python
E[max(SR)] ≈ √(2·log(N)) - (log(π) + γ) / (2·√(2·log(N)))
# N = number of trials
# γ (gamma) = Euler-Mascheroni constant ≈ 0.5772
# π = 3.14159...
# This gives: expected Sharpe if you tested N random strategies
```

**Example walkthrough:**
- You test 14 forecasting models
- The best one has Sharpe = 1.2
- With 14 trials, the expected lucky Sharpe = 0.6
- Deflated Sharpe = 1.2 - 0.6 = 0.6 (your "real" Sharpe after debiasing)

**[DIAGRAM SUGGESTION]** Show 2 Sharpe ratio distributions (side by side):
- Left: "Observed Sharpe (seems impressive, 1.2)"
- Right: "Deflated Sharpe (99% confidence, 0.6)"
- Arrow pointing down: "Adjustment for: N trials, skewness, kurtosis"
- Label: "Deflating removes luck bias"

### Probability of Backtest Overfitting (PBO)

**[INFORMATION GAIN]** `BacktestOverfitDetector` — two tests:

**Test 1: PBO (Probability of Backtest Overfitting)**

"Take your best in-sample strategy and your best out-of-sample strategy. Are they the same? Or did the best performer in-sample become the worst out-of-sample?"

Formally: "For all 6 walk-forward folds, what fraction of the time does the in-sample winner become the out-of-sample loser?"

Example:
- Fold 0: Model A is best in-sample, Model B is best out-of-sample → count = 1
- Fold 1: Model A is best in-sample, Model A is best out-of-sample → count = 0
- ... (continue for all 6 folds)
- PBO = (count of mismatches) / (total folds) = 2/6 = 0.33

**Threshold:** "If PBO > 0.5, your best strategy is probably just luck. If PBO < 0.2, your best strategy generalizes well."

**Test 2: MinBTL (Minimum Backtest Length)**

"How many years of data do you need for this Sharpe to be significant?"

Example:
- Your best model has Sharpe = 0.8
- You have 3 years of data
- MinBTL = 5 years
- Conclusion: You need 5 years to trust this Sharpe. You only have 3. HIGH RISK.

Formal: Solving for T (years) such that:
```
Deflated_Sharpe(N=1, T) = 0  # You'd need this many years
```

**[DIAGRAM SUGGESTION]** Show a "Traffic Light" display:
- Green: PBO < 0.2, MinBTL < your_data_length → CONFIDENT
- Yellow: PBO 0.2–0.5, MinBTL ~ your_data_length → CAUTIOUS
- Red: PBO > 0.5, MinBTL > your_data_length → AVOID

Label: "Backtest overfitting detector = healthy skepticism engine"

---

## 6. WHY THIS MATTERS: The Practical Impact (29:30–32:30)

### The Graveyard of Failed Quant Funds

**Honest takeaway:** "A lot of quant funds fail. Not because the traders are stupid, but because they didn't use this framework. They backtested on shuffled data, didn't purge labels, didn't test for overfitting, and took a strategy live that was 80% luck."

**[INFORMATION GAIN]** "This framework isn't just academic. Renaissance Technologies (the most successful quant fund ever) got rich by being paranoid about backtest bias. They:
1. Purged walk-forward CV (similar to what we do)
2. Out-of-sample testing on data they hadn't touched
3. Out-of-market validation (tested in parallel universes of similar stocks)
4. Tested edge cases: what if your signal reverses? What if volatility spikes?

The difference between their framework and YouTube tutorials: they assume they're wrong until proven otherwise."

### Why You Should Care

"If you're:
- **A quant researcher:** You're bleeding alpha to false positives. Use this framework to find the 1-2 real signals instead of 14 false ones.
- **A trader:** Every 'edge' you see online that doesn't mention purged CV is probably worthless. Use this framework to filter ideas.
- **Learning ML:** This is how ML is supposed to work when the stakes are real (money, not Kaggle leaderboards). Generalization is everything."

**[DIAGRAM SUGGESTION]** Comparison table:
```
| Framework         | Purge | Embargo | Multiple Test Correction | Deflated Sharpe | PBO |
|-------------------|-------|---------|--------------------------|-----------------|-----|
| YouTube tutorials | ✗     | ✗       | ✗                        | ✗               | ✗   |
| Serious quants    | ✓     | ✓       | ✓                        | ✓               | ✓   |
| This system       | ✓     | ✓       | ✓                        | ✓               | ✓   |
```

Label: "You can spot the difference in 30 seconds"

---

## 7. LIVE DEMO: FAKE vs REAL (32:30–37:30)

Show side-by-side:

1. **Fake backtest:** Standard train/test split, no purge, no embargo, pick the best model
   - Beautiful equity curve, high Sharpe, looks like free money

2. **Real backtest:** Purged walk-forward CV, BH-FDR correction, deflated Sharpe
   - Honest results: lower Sharpe, some models fail, but the ones that survive are REAL

**[INFORMATION GAIN]** "The Sharpe dropped from [fake number] to [real number]. That gap is the lie. Every impressive backtest you see online that doesn't mention purged CV, embargoed folds, or p-value correction is probably in that gap."

---

## 8. THE PAYOFF (37:30–40:00)

"Now you know how to test properly. You know the three lies, purging, embargo, multiple testing correction, and how to detect overfitting. Most backtests are wrong. Yours won't be."

**Bridge to next video:** "In the next video, I'll show you the labeling method that quant funds use instead of 'stock went up / stock went down' — triple-barrier labeling. This is where the magic starts: good labels = good models."

**CTA Sequence:**
1. "Subscribe if you want to build systems that actually work"
2. "Comment: what's YOUR worst backtesting mistake? Or drop a 📊 if you've already been burned by a fake edge"
3. GitHub link, Jupyter notebook walkthrough link
4. "See you in the next one"

---

## [NEEDS MORE]

- **Your specific numbers:** The fake Sharpe vs real Sharpe for at least one model. This is the money shot of the video.
- **A personal story:** "When I first ran this system without purging, I thought I had found alpha. Then I added purge+embargo and the Sharpe dropped from X to Y. That moment when you realize your model isn't actually good..."
- **Visual of the gap:** Can you generate a comparison chart showing the same strategy with/without purge+embargo? Even a simple matplotlib plot.
- **Mention of competitors:** "Go look at any ML trading tutorial on YouTube. How many of them mention purged CV? Embargo? Deflated Sharpe? Exactly."
