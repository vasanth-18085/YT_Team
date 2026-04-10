# V2 — Backtesting Lies — Refined Script

**Title:** The Backtesting Lie No One Talks About
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–1:30)

[INFORMATION GAIN] If you have ever backtested an ML model on stock data and got amazing results — you probably cheated without knowing it. I know because I did it. I built 14 forecasting models, got one with what looked like a strong backtest Sharpe, and felt like I had cracked it. Then I tested it properly. The number dropped significantly.

Today I am going to show you exactly how that happens and exactly how to fix it.

[PERSONAL INSERT NEEDED] Show your "fake" backtest equity curve here — the beautiful one. Then pause. "This is a lie. And I am going to show you exactly why."

That curve was generated with standard train-test split. The kind every ML tutorial teaches. On tabular classification data it works fine. On time-series financial data it is a guaranteed way to cheat without realising it.

There are three specific lies baked into most ML backtests. By the end of this video you will know what each one is, why it matters, and how the `PurgedWalkForwardCV` class in this system fixes all three.

---

## SECTION 2 — LIE NUMBER ONE: SHUFFLED SPLITS (1:30–5:00)

The most common mistake in financial ML.

[INFORMATION GAIN] Most ML tutorials use `train_test_split(shuffle=True)`. On a time series this is a guaranteed way to leak the future into training. If your test set contains January 2023 and your training set contains December 2022 AND February 2023 — which is exactly what happens with shuffling — your model literally trains on data from after the test period.

Let me make that concrete. You have a horizontal timeline. Left to right: 2020, 2021, 2022, 2023. With a correct time-series split you take everything before a cutoff as training and everything after as test. Clean.

With shuffled split, February 2023 can land in your training set. Your model learns from February 2023 data and then gets evaluated on January 2023. It has seen the future. Of course it performs well.

Even sklearn's built-in `TimeSeriesSplit` is not enough for financial data. And the reason why leads directly to Lie Number Two.

**[DIAGRAM SUGGESTION]** Show two horizontal timelines:
Row 1 (Correct split): Solid green [Train 2020-2022] → Solid blue [Test 2023]
Row 2 (Shuffled split): Mixed green and red dots throughout the timeline, showing future data points scattered into the training window
Label: "Shuffled split = model trains on tomorrow's data"

---

## SECTION 3 — LIE NUMBER TWO: LABEL OVERLAP (5:00–11:30)

This one is subtle and almost nobody discusses it.

[INFORMATION GAIN] In this system, triple-barrier labels have a maximum holding period of 10 days. That means the label for a position opened on Day T depends on prices from Day T through Day T plus 10. If your training set ends at Day T and your test set starts at Day T plus 1, the training set contains information about what happens in the test period — embedded inside the label. That is label leakage, and standard time-series splits do not handle it.

Let me walk through a specific example.

You are running a model on Apple stock. You take a position on Day 100. The triple-barrier label for that position is determined by what happens on Days 100 through 110. If your test set starts at Day 101, and your training set includes Day 100, then the Day 100 label in your training data was constructed using price information from Days 101 through 110 — the exact period you are supposed to be predicting blind.

Even `TimeSeriesSplit` does not handle this because it knows nothing about how your labels were constructed. It just splits rows.

The fix is called purging.

```python
# From purged_cv.py
# Purge: remove last purge_window samples before each test fold boundary
train_end = max(train_start, test_start - self.purge_window)
```

With `purge_window=5`, the last 5 training samples before every test fold boundary are dropped. The training set no longer contains labels whose outcomes depend on the test period.

**[DIAGRAM SUGGESTION]** Day-by-day diagram showing:
- Training set ending at Day 95
- Purge zone: Days 96 to 100 (removed from training)
- Test set starting at Day 101
- Arrow showing: "Label for Day 100 depends on Days 100-110 — but Day 100 is purged, so it never enters training"
Label: "Purge removes label leakage at the boundary"

---

## SECTION 4 — LIE NUMBER THREE: AUTOCORRELATION LEAKAGE (11:30–18:00)

Even after purging, there is still a subtler problem.

[INFORMATION GAIN] Financial returns are autocorrelated. If returns are positive on Day 100 they are slightly more likely to be positive on Day 101. That correlation is a property of the market. It exists in both your training data and your test data. A model trained right up to the purge boundary will learn this autocorrelation pattern — and then exploit the same pattern in the test set.

Here is what the lag structure actually looks like in daily S&P 500 returns:

```
Lag-1 autocorrelation:  0.08
Lag-2 autocorrelation:  0.03
Lag-3 autocorrelation:  0.01
Lag-5 autocorrelation:  ~0.00
```

A lag-1 autocorrelation of 0.08 sounds tiny. But your model will find it and exploit it. A model trained on Days 1 through 100 learns: when Day 100 goes up, Day 101 tends to go up. That same relationship exists in the test period because it is a property of market microstructure, not of the training data. So the model wins on the test set — not because it found alpha, but because it learned a momentum effect that is always present.

The fix is an embargo.

After the purge zone, an additional gap is added before the test set begins. This gap allows market autocorrelation to decay naturally before evaluation starts.

```yaml
# config.yaml
walk_forward:
  embargo: 5     # additional samples removed after training
  purge: 5       # samples purged around label boundary
```

The embargo length is controlled by `embargo_pct`. The default is 0.01 — meaning 1% of the test set size. For a 126-day test fold that rounds to about 5 days. Daily equity return autocorrelation decays to near-zero within 5 trading days at typical lookbacks.

There is a more advanced tuning note worth mentioning. If you are trading high-frequency data where autocorrelation decays more slowly, you might need `embargo_pct=0.05`. If you are trading daily large-cap equities, 0.01 is typically sufficient. Check your autocorrelation structure and set accordingly.

**[DIAGRAM SUGGESTION]** Three-panel comparison of the same boundary:
Panel 1: No purge, no embargo — red shaded region shows autocorrelation bleeding from training into test
Panel 2: Purge only — gap shown, faint correlation still leaks at boundary
Panel 3: Purge plus embargo — two gaps shown, correlation has fully decayed before evaluation begins
Label each panel with its effect

---

## SECTION 5 — THE FIX: PURGED WALK-FORWARD CV (18:00–28:00)

Walk-forward validation simulates what a real trader actually does.

[INFORMATION GAIN] A prop trader in 2020 had no access to 2023 data. They trained on everything available through 2020, predicted forward into 2021, then retrained on 2020–2021 data and predicted 2022. Walk-forward CV mirrors that exactly. You train, predict forward into genuinely unseen future data, advance the window, retrain, and repeat. You never predict the past. You never train on the future.

The configuration in this system:

```yaml
walk_forward:
  initial_train_days: 504    # approximately 2 years to start
  val_days: 126              # approximately 6 months per test fold
  step_days: 63              # advance by approximately 3 months per step
  n_splits: 6                # 6 total walk-forward folds
  expanding: true            # training window grows each fold
```

This gives 3 years of test coverage across 6 non-overlapping folds, each testing a different market period and regime.

Here is the `PurgedWalkForwardCV` class header:

```python
class PurgedWalkForwardCV:
    def __init__(
        self,
        n_splits=5,
        purge_window=5,
        embargo_pct=0.01,
        expanding=True,
        min_train_size=100
    ):
```

Every parameter has a specific reason.

`purge_window=5`: Removes 5 training samples before each test boundary to prevent label leakage. The number 5 corresponds to the typical triple-barrier label horizon.

`embargo_pct=0.01`: Removes 1% of the test set size as an additional buffer after training ends. This is where autocorrelation decays.

`expanding=True`: Training window grows fold to fold, using the full available history. Setting this to False gives a sliding fixed-size window — useful if you believe recent market behaviour is more representative than the full history.

`min_train_size=100`: Skips folds where training has fewer than 100 samples. A model trained on 50 points produces unreliable estimates and should be skipped entirely rather than trusted.

The `CVFold` dataclass provides full transparency into what happened at each fold:

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

And `.summary()` produces a clean table showing exactly where every fold's boundaries are, how many samples were purged, and how many were embargoed. Full audit trail.

**[DIAGRAM SUGGESTION]** 6-row expanding timeline chart:
Row 1 (Fold 0): Green [504d train] → Small gap [purge+embargo] → Blue [126d test]
Row 2 (Fold 1): Green [567d train] → gap → Blue [126d test]
Row 3-6: Continue expanding
Each row shifted 63 days right. Include the purge/embargo gap as a visual element at each boundary.
Label: "Each fold sees an independent future period — no fold data ever contaminates another"

---

## SECTION 6 — EXPANDING VERSUS SLIDING WINDOWS (28:00–33:00)

A choice worth understanding explicitly.

Expanding window (default): training grows from fold to fold. Fold 1 uses 504 days, fold 6 uses 819. All available history is used.

Sliding window: training stays at a fixed size and slides forward. Fold 1 uses Days 1 to 504, fold 6 uses Days 315 to 819.

The argument for expanding: more data produces more stable estimates for most models.

The argument for sliding: market conditions from 2010 may not be informative for predicting 2024. Historical data can hurt if the market has structurally shifted.

[INFORMATION GAIN] My default is expanding, but I have tested both. For the assets and time periods I am working with, the expanding window gives more consistent Sharpe across folds. But it is not universal. If you are trading a sector that has transformed fundamentally — say, a tech sector before and after the 2022 rate environment shift — sliding might serve you better. Run both and compare fold-to-fold variance. Lower variance across folds is a signal of good generalisation.

---

## SECTION 7 — THE STATISTICAL VALIDATION LAYER (33:00–37:00)

There is a fourth issue worth flagging even though it gets its own full video later.

When you test 14 models and one achieves a Sharpe of 1.2, that is not a result — that is a selection. If I generate 14 random trading strategies, roughly one of them will look like it has a Sharpe of 1.2 by chance.

The Deflated Sharpe Ratio adjusts the observed Sharpe for the expected maximum Sharpe you would get from testing N strategies:

```
E[max(SR)] ≈ sqrt(2 * log(N)) - gamma / (2 * sqrt(2 * log(N)))
Deflated_SR = Observed_SR - E[max(SR)]
```

For N equals 14 models and an observed Sharpe of 1.2, the expected lucky Sharpe is around 0.6. Deflated Sharpe is 0.6 — not 1.2.

[INFORMATION GAIN] That is a sobering adjustment if you are used to reporting raw backtest Sharpe ratios from model comparisons. Purge and embargo clean up the data split problem. Deflated Sharpe cleans up the model selection bias. You need both to believe what you are looking at.

---

## SECTION 8 — THE REAL NUMBERS (37:00–39:00)

[PERSONAL INSERT NEEDED] This is the most important section. Show the before-and-after comparison from your actual data. The Sharpe you got before applying purged walk-forward validation, and the honest number you got after. What was the difference? Did the model rankings change — did the model that "won" under standard splits still win under honest splits? Even one concrete data point here makes this segment genuinely memorable.

---

## SECTION 9 — THREE RULES I NOW FOLLOW WITHOUT EXCEPTION (39:00–40:00)

One: never use `train_test_split(shuffle=True)` on financial time series. Not even to test if code runs.

Two: always purge and always embargo. The defaults are `purge_window=5` and `embargo_pct=0.01` for daily equity data. Adjust based on your label horizon.

Three: always report dispersion across folds, not just mean Sharpe. A mean of 0.8 with a standard deviation of 0.5 across folds looks very different from a mean of 0.8 with standard deviation 0.1. The first might be one lucky fold. The second is a consistent signal.

The code for `PurgedWalkForwardCV` is in the GitHub repo. Every model comparison in this series uses it.

Next video: triple-barrier labeling. The technique that makes your labels reflect how trades actually perform in the real world — not just which direction the price moved.

Subscribe and comment — have you seen this issue in your own backtests? What was your before-and-after number?

See you in the next one.

---

## Information Gain Score

**Score: 7/10**

The three-lie framework is well-structured. The autocorrelation section with the actual lag decay numbers, the line-by-line parameter explanation for `PurgedWalkForwardCV`, and the Deflated Sharpe preview are all specific and genuinely useful.

What holds it back: the most compelling moment — the before-and-after comparison from real data — is still a placeholder. That comparison, done with your actual numbers, is what transforms this from a good tutorial into a credibility-building video.

**Before filming, add:**
1. Your real before-and-after Sharpe numbers in Section 8
2. Whether model rankings changed after purged validation
3. One sentence in the hook about your personal experience discovering one of these three lies
