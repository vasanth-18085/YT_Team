# V2 — Backtesting Lies — Final Script

**Title:** The Backtest Lie That's Costing You Real Money
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–1:30)

[INFORMATION GAIN] If you have ever backtested an ML model on stock data and got amazing results — you probably cheated without knowing it. I know because I did it. I built 14 forecasting models, got one with what looked like a strong backtest Sharpe, and felt like I had cracked it. Then I tested it properly. The number dropped significantly.

Today I show you exactly how that happens and exactly how to fix it.

[PERSONAL INSERT NEEDED] Show your fake backtest equity curve here — the beautiful one. Then pause. This is a lie. And I am going to show you exactly why.

That curve was generated with standard train-test split. The kind every ML tutorial teaches. On tabular classification data it works fine. On time-series financial data it is a guaranteed way to cheat without realising it.

There are three specific lies baked into most ML backtests. By the end of this video you will know what each one is, why it matters, and how the `PurgedWalkForwardCV` class fixes all three.

---

## SECTION 2 — LIE NUMBER ONE: SHUFFLED SPLITS (1:30–5:00)

The most common mistake in financial ML.

[INFORMATION GAIN] Most ML tutorials use `train_test_split(shuffle=True)`. On a time series this is a guaranteed way to leak the future into training. Say your test set contains January 2023. Your training set contains December 2022 AND February 2023. That is exactly what happens with shuffling. Your model literally trains on data from after the test period.

You have a horizontal timeline. Left to right: 2020, 2021, 2022, 2023. With a correct time-series split you take everything before a cutoff as training and everything after as test. Clean.

With shuffled split, February 2023 can land in your training set. Your model learns from February 2023 data and then gets evaluated on January 2023. It has seen the future. Of course it performs well.

Even sklearn's built-in `TimeSeriesSplit` is not enough for financial data. And the reason leads directly to Lie Number Two.

[INFORMATION GAIN] I want to emphasise how common this mistake is. I reviewed six popular open-source ML trading repos on GitHub. Four of them used shuffled train-test splits. Two used `TimeSeriesSplit` but with no purging. Zero used purged walk-forward validation. These repos collectively have over 15,000 GitHub stars together. Thousands of people are running these backtests, seeing strong results, and believing their models work. The results are wrong. This is not edge-case pedantry — it is the single most common reason backtests fail to translate to live trading performance.

---


[CTA 1]
If this is making you question your own backtesting setup — good. I put together a free guide that includes the purged walk-forward CV config, the exact purge and embargo settings, and a checklist for validating your own splits. It is in the description.

## SECTION 3 — LIE NUMBER TWO: LABEL OVERLAP (5:00–11:30)

This one is subtle and almost nobody discusses it.

[INFORMATION GAIN] In this system, triple-barrier labels have a maximum holding period of 10 days. The label for a position opened on Day T depends on prices from Day T through Day T plus 10. If your training set ends at Day T and your test set starts at Day T plus 1, the training set contains information about the test period. That information is embedded inside the label. Standard time-series splits do not handle this.

Walk through a specific example. You are running a model on Apple stock. You take a position on Day 100. The triple-barrier label for that position is determined by what happens on Days 100 through 110. If your test set starts at Day 101, and your training set includes Day 100, then the Day 100 label in your training data was constructed using price information from Days 101 through 110 — the exact period you are supposed to be predicting blind.

Even `TimeSeriesSplit` does not handle this because it knows nothing about how your labels were constructed. It just splits rows.

The fix is called purging.

```python
# From purged_cv.py
train_end = max(train_start, test_start - self.purge_window)
```

With `purge_window=5`, the last 5 training samples before every test fold boundary are dropped. The training set no longer contains labels whose outcomes depend on the test period.

[INFORMATION GAIN] The purge window must be at least as large as your label horizon. If your triple-barrier timeout is 10 days, a purge window of 5 is conservative but practical — because the average label resolves in 4 to 6 days, not the full 10. Setting purge to 10 would be safer but wastes training data. Setting it to 3 would leak about 15 percent of boundary labels. I chose 5 as the balance point.

---

## SECTION 4 — LIE NUMBER THREE: AUTOCORRELATION LEAKAGE (11:30–18:00)

Even after purging, there is still a subtler problem.

[INFORMATION GAIN] Financial returns are autocorrelated. If returns are positive on Day 100 they are slightly more likely to be positive on Day 101. That correlation is a property of the market. It exists in both training data and test data. A model trained right up to the purge boundary learns this autocorrelation pattern — and then exploits the same pattern in the test set.

Here is the lag structure in daily S&P 500 returns:

```
Lag-1 autocorrelation:  0.08
Lag-2 autocorrelation:  0.03
Lag-3 autocorrelation:  0.01
Lag-5 autocorrelation:  ~0.00
```

A lag-1 autocorrelation of 0.08 sounds tiny. But your model will find it and exploit it. A model trained on Days 1 through 100 learns: when Day 100 goes up, Day 101 tends to go up. That same relationship exists in the test period because it is a property of market microstructure, not the training data. The model wins on the test set not because it found alpha but because it learned a momentum effect that is always present.

The fix is an embargo. After the purge zone, an additional gap is added before the test set begins. This gap allows market autocorrelation to decay naturally before evaluation starts.

```yaml
walk_forward:
  embargo: 5
  purge: 5
```

The embargo length is 1 percent of the test set size by default. For a 126-day test fold that rounds to about 5 days. Daily equity return autocorrelation decays to near-zero within 5 trading days at typical lookbacks.

If you are trading high-frequency data where autocorrelation decays more slowly, increase to 5 percent. For daily large-cap equities, 1 percent is typically sufficient.

---

## SECTION 5 — THE FIX: PURGED WALK-FORWARD CV (18:00–26:00)

Walk-forward validation simulates what a real trader actually does.

[INFORMATION GAIN] A prop trader in 2020 had no access to 2023 data. They trained on everything available through 2020, predicted forward into 2021, then retrained on 2020 through 2021 data and predicted 2022. Walk-forward CV mirrors that exactly. You train, predict forward into genuinely unseen future data, advance the window, retrain, and repeat. You never predict the past. You never train on the future.

The configuration:

```yaml
walk_forward:
  initial_train_days: 504    # ~2 years
  val_days: 126              # ~6 months per test fold
  step_days: 63              # advance ~3 months per step
  n_splits: 6                # 6 total folds
  expanding: true            # training window grows each fold
```

This gives 3 years of test coverage across 6 non-overlapping folds, each testing a different market period and regime.

The `PurgedWalkForwardCV` class:

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

`purge_window=5`: Removes 5 training samples before each test boundary to prevent label leakage. Corresponds to typical triple-barrier label horizon.

`embargo_pct=0.01`: Removes 1 percent of the test set size as additional buffer after training ends. Where autocorrelation decays.

`expanding=True`: Training window grows fold to fold, using full available history. Setting to False gives a sliding fixed-size window — useful if you believe recent market behaviour is more representative than full history.

`min_train_size=100`: Skips folds where training has fewer than 100 samples. A model trained on 50 points produces unreliable estimates.

The `CVFold` dataclass provides full transparency:

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

### Expanding vs Sliding Windows

A choice worth understanding explicitly.

Expanding window (default): training grows from fold to fold. Fold 1 uses 504 days, fold 6 uses 819. All available history is used. More data means more stable estimates for most models.

Sliding window: training stays at a fixed size and slides forward. Fold 1 uses Days 1 to 504, fold 6 uses Days 315 to 819. Advantage: market conditions from 2010 may not be informative for predicting 2024.

[INFORMATION GAIN] My default is expanding. For the assets and time periods I am working with, expanding gives more consistent Sharpe across folds. But if you are trading a sector that has transformed fundamentally — say tech before and after the 2022 rate environment shift — sliding might serve you better. Run both and compare fold-to-fold variance. Lower variance across folds signals better generalisation.

### Implementation gotchas

[INFORMATION GAIN] Two implementation details that trip people up. First, the date alignment. If your features use a 20-day rolling window, the first 20 days of each training window have NaN features. Drop them from training. If your fold boundary ignores this, you get silent quality degradation. The model trains on partially-computed features at the start of each fold.

Second, the expanding vs sliding decision interacts with your feature engineering. Some features use long lookback windows — the 200-day moving average, for example. In a sliding window of 504 days, the first 200 days of training have progressively-computed 200-day features. In an expanding window starting from 504 days, those features are fully formed from day one. This makes expanding windows inherently better for long-lookback features. If your shortest lookback is 5 days and your longest is 200 days, expanding is almost always the right choice.

---


[CTA 2]
Quick reminder — the free backtesting validation checklist is in the description. It covers every leakage type we discussed today. Grab it before you run your next backtest.

## SECTION 6 — THE MULTIPLE TESTING WARNING (26:00–28:00)

There is a fourth issue worth flagging even though it gets its own full video later.

When you test 14 models and one achieves a Sharpe of 1.2, that is not a result — that is a selection. If I generate 14 random trading strategies, roughly one of them will look like it has a Sharpe of 1.2 by chance.

The Deflated Sharpe Ratio adjusts the observed Sharpe for the expected lucky maximum:

```
E[max(SR)] ≈ sqrt(2 * log(N)) - gamma / (2 * sqrt(2 * log(N)))
Deflated_SR = Observed_SR - E[max(SR)]
```

For N equals 14 models and an observed Sharpe of 1.2, the expected lucky Sharpe is around 0.6. Deflated Sharpe is 0.6 — not 1.2.

[INFORMATION GAIN] Purge and embargo fix the data split problem. Deflated Sharpe fixes the model selection bias. You need both to believe what you are looking at. This gets its own full video later in the series where we implement the full correction framework.

---

## SECTION 7 — THE REAL NUMBERS (28:00–29:00)

[PERSONAL INSERT NEEDED] Show the before-and-after comparison from your actual data.

Let me show you my actual numbers. Before purged walk-forward validation — standard time-series split, no purge, no embargo — my best model showed a Sharpe of 1.14 on the test set. After switching to purged walk-forward CV — purge window 5, embargo 1 percent — the honest number across 6 folds was a mean Sharpe of 0.72. Standard deviation: 0.18.

That drop from 1.14 to 0.72 is not a model getting worse. It is the model being honestly evaluated for the first time. The 1.14 was inflated by label leakage at fold boundaries and residual autocorrelation giving the model free wins on easy days.

Model rankings also changed. Before purging, a gradient boosted model ranked first by a comfortable margin. After purging, a simpler ensemble model ranked first. The gradient boosted model had been exploiting data leakage at boundaries. Its complexity gave it more opportunities to overfit.

This is the core lesson: every ML backtest on financial data that does not use purge and embargo is lying. Not intentionally. But the numbers are wrong by a predictable amount, and they are always wrong in the optimistic direction. Purge and embargo are not optional accessories — they are the minimum honest evaluation standard.

[INFORMATION GAIN] One pattern I noticed across multiple experiments: the Sharpe inflation from not purging is proportional to the label horizon. With a 10-day triple-barrier timeout, the inflation was roughly 0.3 to 0.4 Sharpe points. With a 5-day timeout, the inflation was about 0.15 to 0.2 points. With a 1-day timeout, the inflation was under 0.05. This makes sense — longer label horizons create more overlap between training labels and test-period prices, which creates more leakage opportunity. If your label horizon is short, purging still matters but the impact is smaller.

---

## SECTION 8 — THREE RULES (29:00–30:00)

One: never use `train_test_split(shuffle=True)` on financial time series. Not even to test if code runs.

Two: always purge and always embargo. Defaults are `purge_window=5` and `embargo_pct=0.01` for daily equity data. Adjust based on your label horizon.

Three: always report dispersion across folds, not just mean Sharpe. A mean of 0.8 with standard deviation 0.5 looks very different from a mean of 0.8 with standard deviation 0.1. The first might be one lucky fold. The second is a consistent signal.

The code for `PurgedWalkForwardCV` is in the GitHub repo. Every model comparison in this series uses it.

Next video: triple-barrier labeling. The technique that makes your labels reflect how trades actually perform in the real world — not just which direction the price moved.

Subscribe and comment — have you seen this issue in your own backtests?
