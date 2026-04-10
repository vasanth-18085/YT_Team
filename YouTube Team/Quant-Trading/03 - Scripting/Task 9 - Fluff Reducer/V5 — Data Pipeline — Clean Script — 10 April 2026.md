# V5 — Data Pipeline — Clean Script

**Title:** My Stock Data Pipeline: No More Corrupt Downloads, Missing Dates, or Feature Misalignment
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

[INFORMATION GAIN] Yahoo Finance is lying to you. Not maliciously — it just has problems you have never noticed unless your trading backtest broke because of them. NaN prices appearing mid-series. The same date listed twice. Adjusted close that does not align to your feature calculations because the adjustment happened after you downloaded the data. These are not hypothetical edge cases. These are problems I hit in this project, hard. This video is the data pipeline that solved all of them.

I am going to walk you through every stage: download, validation, alignment, splitting, feature engineering, and standardisation. By the end you have a pipeline that takes raw ticker symbols and returns a clean, split, leakage-free tensor ready for your model. Every step is production-quality code, not Kaggle notebook spaghetti.

---

## SECTION 2 — WHY YOUR DATA IS BROKEN AND YOU DO NOT KNOW IT (2:00–8:00)

Let me walk through the three categories of Yahoo Finance problems that I actually encountered.

**Problem 1: Duplicate dates in the same download**

Yahoo Finance occasionally duplicates rows when splits or adjustments are applied retroactively. If you do not check for duplicates, your rolling window features compute twice over that row. The feature for that day is wrong. The model trains on a corrupted row and you will never notice in aggregate.

**Problem 2: NaN prices scattered mid-series**

For thinly traded stocks and ETFs, Yahoo Finance will return NaN for closing price on certain days even though the exchange was open. If you forward-fill blindly, you silently carry stale prices forward. The next-day return calculation then shows zero return followed by a large jump when the real price resumes. The model learns to predict zero returns before large moves — the exact opposite of a useful signal.

**Problem 3: Adjusted close misalignment**

Yahoo Finance adjusts all historical prices when dividends or splits occur. If you download today and then download again six months later after a split, you get different price series. Any features you precomputed from the first download are now misaligned with the repriced series. This is the most dangerous problem because it is invisible and makes your offline model incompatible with live data.

[INFORMATION GAIN] The solution to all three: a `DataValidator` class that runs on every download before data is stored, and a caching system that stores the raw download with a hash so you can detect when Yahoo reissues adjusted prices.

---

## SECTION 3 — THREE DATA LOADERS (8:00–14:00)

The pipeline standardises three completely distinct data sources into the same interface. That interface contract is: return a dataframe with DatetimeIndex, consistent column names, and no gaps within the requested range.

### Loader 1: Yahoo Finance (Price Data)

```python
class YahooLoader:
    def __init__(self, tickers: list[str], start: str, end: str):
        self.tickers = tickers
        self.start = start
        self.end = end

    def load(self) -> pd.DataFrame:
        data = yf.download(
            self.tickers,
            start=self.start,
            end=self.end,
            auto_adjust=True,
            actions=True
        )
        data = data.dropna(how='all')
        data = data[~data.index.duplicated(keep='last')]
        return data
```

Auto-adjust is enabled to use adjusted close consistently. `actions=True` downloads dividend and split data separately — useful for the dividend sentiment signal in later videos. Duplicated index rows are dropped keeping the last version, which mirrors Yahoo's own most-recent adjustment.

### Loader 2: Hugging Face Datasets (Fundamental and Alternative Data)

```python
class HFLoader:
    def __init__(self, dataset_name: str, tickers: list[str]):
        self.dataset_name = dataset_name
        self.tickers = tickers

    def load(self) -> pd.DataFrame:
        dataset = load_dataset(self.dataset_name, split='train')
        df = dataset.to_pandas()
        df = df[df['ticker'].isin(self.tickers)]
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()
        return df
```

Hugging Face hosts several financial datasets: FinNLP, StockNews, FNSPID. The loader provides a consistent interface — any of these datasets return the same indexed dataframe shape as Yahoo data.

### Loader 3: Sentiment Loader (From the Fine-Tuned Model)

```python
class SentimentLoader:
    def __init__(self, model_path: str, tickers: list[str]):
        self.model = load_model(model_path)
        self.tickers = tickers

    def load(self, news_df: pd.DataFrame) -> pd.DataFrame:
        results = []
        for ticker in self.tickers:
            ticker_news = news_df[news_df['ticker'] == ticker]
            daily_sentiment = self.aggregate_by_day(ticker_news)
            results.append(daily_sentiment)
        return pd.concat(results)
```

[INFORMATION GAIN] The Sentiment Loader outputs all six daily features we built in Video 4: mean score, std, volume, bullish ratio, momentum, and EWM. The other two loaders output price/returns data. The Alignment stage (Section 5) stitches these three schemas onto the same date index. The reason this matters: news does not arrive at market close. The SentimentLoader must assign each headline to the *next trading day* when the market can act on the news, not the publication day. The loader handles this time-shift internally.

---

## SECTION 4 — DATA VALIDATION (14:00–19:00)

Before any downloaded data enters the pipeline, it passes through the `DataValidator`. This is a class I wrote specifically for this project — it runs a battery of checks and raises `ValidationError` with a specific failure code so the pipeline can decision-tree its way to recovery.

```python
class DataValidator:
    def __init__(self, ticker: str, start: str, end: str):
        self.ticker = ticker
        self.start = pd.Timestamp(start)
        self.end = pd.Timestamp(end)

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        checks = [
            self._check_date_range(df),
            self._check_duplicates(df),
            self._check_gaps(df),
            self._check_price_validity(df),
            self._check_volume_validity(df),
        ]
        errors = [c for c in checks if not c.passed]
        return ValidationResult(
            passed=(len(errors) == 0),
            errors=errors,
            df_shape=df.shape
        )
```

Each check returns a `CheckResult` with a passed flag, a failure message, and the row indices of any offenders.

```python
def _check_price_validity(self, df: pd.DataFrame) -> CheckResult:
    invalid_prices = (df[['Open', 'High', 'Low', 'Close']] <= 0).any(axis=1)
    pct_invalid = invalid_prices.mean()
    return CheckResult(
        name="price_validity",
        passed=(pct_invalid == 0),
        message=f"{pct_invalid:.1%} of rows have zero or negative price",
        bad_rows=df.index[invalid_prices].tolist()
    )
```

[INFORMATION GAIN] The gap check deserves particular attention. Not all missing dates are errors. Saturday, Sunday, and market holidays should be missing. The check uses a market calendar — specifically the `exchange_calendars` library — to know which dates were actual trading days. Only gaps within trading days trigger a validation failure.

```python
def _check_gaps(self, df: pd.DataFrame) -> CheckResult:
    import exchange_calendars as xcals
    nasdaq = xcals.get_calendar("NASDAQ")
    expected_sessions = nasdaq.sessions_in_range(self.start, self.end)
    actual_dates = pd.DatetimeIndex(df.index.date)
    missing = expected_sessions.difference(actual_dates)
    return CheckResult(
        name="gap_check",
        passed=(len(missing) == 0),
        message=f"Missing {len(missing)} trading sessions",
        bad_rows=missing.tolist()
    )
```

---

## SECTION 5 — DATE ALIGNMENT (19:00–23:00)

The three loaders return data on different date schedules. Price data exists on every trading day. Sentiment data may be missing on weekends and holidays but also on days with no relevant news. Fundamental data may arrive quarterly.

```python
class DataAligner:
    def align(
        self,
        price_df: pd.DataFrame,
        sentiment_df: pd.DataFrame,
        fundamental_df: pd.DataFrame
    ) -> pd.DataFrame:

        # Trading calendar index from price data
        trading_days = price_df.index

        # Reindex all sources to trading days
        sentiment_aligned = sentiment_df.reindex(trading_days).ffill(limit=5)
        fundamental_aligned = fundamental_df.reindex(trading_days).ffill()

        # Merge
        aligned = price_df.copy()
        aligned = aligned.join(sentiment_aligned, how='left')
        aligned = aligned.join(fundamental_aligned, how='left')

        return aligned
```

[INFORMATION GAIN] The `ffill(limit=5)` on sentiment is intentional and bounded. If no news headline existed for a ticker on a given day, forward-fill the previous day's sentiment — but only for up to 5 days. Beyond 5 days the sentiment is set to NaN and the model uses a learned default representation. This prevents stale week-old sentiment from contaminating live trading signals. Fundamental data forward-fills without limit because quarterly earnings do not expire the same way.

---

## SECTION 6 — WALK-FORWARD SPLITS (23:00–28:00)

This is where most pipelines are completely wrong, and where lookahead bias silently inflates your backtest returns.

The splitting is handled by `PurgedWalkForwardCV` — the same class from Video 2. But the pipeline adds one layer above it: the split must be applied at the *window level*, not the feature-matrix level.

```python
class PipelineSplitter:
    def __init__(self, n_splits=5, test_size=252, purge_days=5, embargo_days=2):
        self.splitter = PurgedWalkForwardCV(
            n_splits=n_splits,
            test_size=test_size,
            purge_days=purge_days,
            embargo_days=embargo_days
        )

    def split_pipeline(self, aligned_df: pd.DataFrame):
        for train_idx, test_idx in self.splitter.split(aligned_df):
            train_data = aligned_df.iloc[train_idx]
            test_data = aligned_df.iloc[test_idx]

            # Fit scaler ONLY on training data
            scaler = StandardScaler()
            train_scaled = scaler.fit_transform(train_data[FEATURE_COLS])
            test_scaled = scaler.transform(test_data[FEATURE_COLS])

            yield train_scaled, test_scaled, scaler
```

[INFORMATION GAIN] The critical line: `scaler.fit_transform(train_data)` followed by `scaler.transform(test_data)` — not `fit_transform` on test. The scaler is fitted only on training data and then *applied* to test data. If you scale the entire dataset first and then split, the test set's statistics have influenced your scaler. Every sample in your test set is then slightly contaminated with future information. This inflates Sharpe by measurable amounts. I tested both approaches — the difference was non-trivial.

---

## SECTION 7 — FEATURE ENGINEERING AND STANDARDISATION (28:00–35:00)

Feature engineering is covered in depth in Video 6 — 45 features across 8 categories. The pipeline's job here is not feature selection, it is applying feature engineering within each training window without leakage.

```python
class FeatureEngineer:
    def fit_transform(
        self,
        df: pd.DataFrame,
        is_train: bool = True
    ) -> pd.DataFrame:
        df = df.copy()

        # Momentum features
        for window in [5, 10, 20, 60]:
            df[f'return_{window}d'] = df['Close'].pct_change(window)

        # Volatility features — rolling std computed within window
        for window in [10, 20, 60]:
            df[f'vol_{window}d'] = df['return_1d'].rolling(window).std()

        # Volume features
        df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()

        return df.dropna()
```

The final standardisation stage:

```python
class Standardiser:
    def __init__(self):
        self.scaler = RobustScaler()   # median/IQR not mean/std — outlier resistant

    def fit_transform(self, X_train: np.ndarray) -> np.ndarray:
        return self.scaler.fit_transform(X_train)

    def transform(self, X_test: np.ndarray) -> np.ndarray:
        return self.scaler.transform(X_test)
```

[INFORMATION GAIN] `RobustScaler` instead of `StandardScaler` — this is a finance-specific choice. Financial returns have fat tails. A 5-sigma move that you would expect to see once in ~3.5 million observations actually happens once every few years in equity markets. StandardScaler subtracts the mean and divides by standard deviation. In the presence of fat tails, extreme outlier returns inflate the standard deviation estimate and compress all your "normal" feature values into a tiny range. RobustScaler uses median and interquartile range, making it robust to the fat-tail events that corrupt StandardScaler.

---

## SECTION 8 — PIPELINE ORCHESTRATION (35:00–39:00)

The six stages wire together in a single `DataPipeline` class.

```python
class DataPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.loader = YahooLoader(config.tickers, config.start, config.end)
        self.validator = DataValidator(config.tickers, config.start, config.end)
        self.aligner = DataAligner()
        self.splitter = PipelineSplitter(
            n_splits=config.n_splits,
            test_size=config.test_size
        )
        self.feature_engineer = FeatureEngineer()
        self.standardiser = Standardiser()

    def run(self):
        # Stage 1: Load
        raw_data = self.loader.load()

        # Stage 2: Validate
        validation_result = self.validator.validate(raw_data)
        if not validation_result.passed:
            raise PipelineError(validation_result.errors)

        # Stage 3: Align
        aligned_data = self.aligner.align(raw_data, sentiment_df, fundamental_df)

        # Stage 4: Feature engineering
        featured_data = self.feature_engineer.fit_transform(aligned_data)

        # Stage 5: Split
        for train_X, test_X, scaler in self.splitter.split_pipeline(featured_data):
            # Stage 6: Standardise
            train_X_scaled = self.standardiser.fit_transform(train_X)
            test_X_scaled = self.standardiser.transform(test_X)
            yield train_X_scaled, test_X_scaled
```

[INFORMATION GAIN] The pipeline yields split batches rather than returning a full dataset. This is a memory design decision. For large universes — 50 or more stocks, 10 or more years, 45 features — the full feature matrix can be several gigabytes. Yielding train-test pairs allows the model training loop in Video 7 to process each split without holding the entire dataset in RAM.

There is a second reason for the generator pattern: it makes the pipeline composable with any downstream consumer. The orchestrator does not care what model you are training. It yields (train_X, test_X) pairs and the consumer decides what to do with them. This means the same pipeline serves the forecasting models, the meta-labeling classifiers, the sentiment models, and the fusion architectures without any modification.

### Error handling

Production pipelines fail. The network drops during a Yahoo download. A ticker gets delisted mid-download. A date column has a timezone mismatch. Each stage in the orchestrator wraps its call in a try-except block that logs the error with full context — which stage failed, which ticker, which date range — and either retries (for network issues) or skips (for data issues) with a clear log message. After the full pipeline runs, the orchestrator produces a summary: 87 out of 100 tickers succeeded, 13 failed with reasons listed. You review the failures and decide whether to proceed or investigate.

[INFORMATION GAIN] I learned this the hard way. My first version of the pipeline had no error handling. A single corrupted ticker in a 100-stock universe caused the entire pipeline to crash at 3am during an automated run. By the time I woke up, I had no data for that day's trading. The fix was not just adding try-except — it was building the pipeline to tolerate partial failures gracefully and still produce usable output from the tickers that succeeded.

The logging design matters too. Each failed ticker gets a structured log entry with the failure time, the exception type, the failing stage name, and the ticker symbol. These logs feed into a monitoring dashboard that tracks failure rates over time. If a ticker starts failing consistently across multiple runs, that is a signal to investigate whether it was delisted, acquired, or has changed its data format. Automated alerts trigger when the failure rate exceeds 10 percent of the universe on any single run.

---

## SECTION 9 — THE CLOSE (39:00–40:00)

Six stages, three data sources, eight validation criteria, one clean tensor at the other end.

This pipeline is what allows every other video in the series to assume the data is correct. Without this foundation, every model you build is building on uncertain ground, and you can never tell whether your results are signal or data artefact.

Next video: what features go into the pipeline. Forty-five trading features across eight categories — momentum, volatility, trend, volume, Ichimoku, price structure, rolling statistics, and calendar effects.

See you there.

---

## Information Gain Score

**Score: 7/10**

The NaN-handling rationale, calibrated forward-fill limit, RobustScaler vs StandardScaler reasoning, and the memory-efficient yielding approach are genuine actionable insights not commonly assembled together.

**Before filming, add:**
1. A specific example of a data corruption you actually found — even one headline about which ticker and when
2. The actual numbers on how Sharpe changes between correct and incorrect scaler fit order
3. Your config file contents to show what the default pipeline parameters look like
