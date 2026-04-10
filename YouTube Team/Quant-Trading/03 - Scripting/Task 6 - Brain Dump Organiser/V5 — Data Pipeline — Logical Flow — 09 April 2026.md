# V5 — Building the Data Pipeline: From Yahoo Finance to Trading-Ready DataFrames — Logical Flow

**Title:** "Data Pipeline 101: Yahoo Finance → Features → ML Ready"
**Length:** ~40 min
**Date:** 09 April 2026

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** "You have a brilliant ML model idea. But if your data pipeline is broken, your model is trained on garbage. I spent 8 months building a data pipeline that handles 100+ stocks, 10+ years, 50+ edge cases — missing data, splits, dividends, delisting, corporate actions. Today I'm showing you exactly how to build one that won't fail at 3 AM."

---

## 2. THE PROBLEM: RAW DATA IS A NIGHTMARE (2:00–6:00)

### Why Yahoo Finance alone isn't enough

**[INFORMATION GAIN]** "Yahoo Finance data is free and easy, but it has problems:"

1. **Survivorship bias:** Delisted stocks disappear. You can't download historical Nokia — it crashed and delisted. So your backtest only sees winners.
2. **Corporate actions:** A 2:1 stock split on January 15 means prices before that date need adjustment. Most people forget.
3. **Missing data:** Market holidays, data glitches, API downtime. What do you do on Feb 15 when Yahoo didn't report?
4. **Different indicators need different timeframes:** Volatility needs daily data. Sentiment needs minutes. You can't train a model if data columns don't align.
5. **Speed:** Real-time trading needs ultra-fast reads. Querying Yahoo every second = too slow.

### The solution: A robust pipeline

"Cache locally, validate everything, handle edge cases, resample intelligently, align all signals. That's what a production pipeline does."

---

## 3. THE DATA SOURCES (6:00–12:00)

### Three loaders in the system

```python
class YahooLoader:
    def load(self, tickers, start_date, end_date):
        # Downloads OHLCV from Yahoo Finance API
        # Caches as Parquet locally
        # Returns: pd.DataFrame with columns [Open, High, Low, Close, Volume]

class HFLoader:  # High-frequency (minute-bar)
    def load(self, ticker, date):
        # Loads minute-level OHLCV
        # Used for intraday sentiment correlation
        
class SentimentLoader:
    def load(self, tickers, start_date, end_date):
        # Loads pre-scored headlines (from FinBERT pipeline)
        # Returns: DataFrame with [timestamp, sentiment_score, source]
```

**[DIAGRAM SUGGESTION]** Show 3 data sources merging into one:
- Top left: Yahoo Finance (daily bars)
- Top middle: Minute data (intraday)
- Top right: Sentiment API (headlines)
- Bottom: Merged aligned dataset
- Label: "Multi-source alignment = the hard part"

### Why three sources?

1. **Daily OHLCV** — model input, backtesting
2. **Minute bars** — intraday sentiment correlation (for Features video)
3. **Sentiment** — already fine-tuned and scored

"If you're starting out, use Yahoo daily + calculate sentiment yourself. This architecture is modular — swap out sources later."

---

## 4. THE DATA PIPELINE STAGES (12:00–28:00)

### Stage 1: Download & Caching

```python
def download_and_cache(ticker, start_date, end_date):
    cache_path = f"./data/cache/{ticker}.parquet"
    
    if cache_path exists and is_recent:
        return pd.read_parquet(cache_path)
    
    # Not cached, fetch from Yahoo
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Save for next time
    data.to_parquet(cache_path)
    return data
```

**[INFORMATION GAIN]** "Caching is essential. Yahoo throttles requests. If you're training models that crash halfway and retry, you'll get rate-limited. Always cache."

### Stage 2: Validation & Cleaning

**Check 1: Missing data (NaN checks)**

```python
def check_missing(df):
    missing = df.isnull().sum()
    if missing.any():
        print(f"Missing values:\n{missing}")
        # Options:
        # - Drop rows (lose data)
        # - Forward fill (yesterday's close = today's open? risky)
        # - Interpolation (safer for small gaps)
        df = df.fillna(method='ffill').fillna(method='bfill')
    return df
```

**Strategy:** Forward-fill for market holidays (expected missing). Drop if > 5 consecutive NaNs (data corruption).

**Check 2: Price jumps (outliers)**

```python
def detect_splits_and_miracles(df):
    returns = df['Close'].pct_change()
    
    # Identify impossible jumps (e.g., -50% overnight without news)
    suspicious = returns[returns.abs() > 0.20]  # 20% overnight jump
    
    for date, ret in suspicious.items():
        # Could be: stock split, reverse split, data error, or real crash
        # Check if volume spiked (split indicator)
        if df.loc[date, 'Volume'] > avg_volume * 3:
            print(f"Suspected split on {date}: {ret*100:.1f}%")
        else:
            print(f"Real crash on {date}: {ret*100:.1f}%")
```

**[INFORMATION GAIN]** "Handling this wrong = your whole backtest is wrong. If Tesla splits 3:1 on August 25, 2022, all pre-split prices need to be divided by 3. Most free data already adjusts for this, but double-check."

### Stage 3: Feature Alignment

"Now all your data sources (daily, minute, sentiment) need aligned indices."

```python
def align_data(daily_df, minute_df, sentiment_df):
    # Resample minute to daily OHLC
    minute_daily = minute_df.resample('D').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    
    # Match sentiment to date (sentiment timestamps are dates)
    sentiment_daily = sentiment_df.set_index('date')
    
    # Align all three on daily index
    aligned = daily_df.join(minute_daily, rsuffix='_minute') \
                      .join(sentiment_daily)
    
    # Drop rows where any core signal is NaN
    aligned = aligned.dropna(subset=['Close', 'sentiment_mean', 'volatility'])
    
    return aligned
```

**[DIAGRAM SUGGESTION]** Show 3 tables with different row counts:
- Left: Daily data (2500 trading days)
- Middle: Minute data (resampled, 2500 days)
- Right: Sentiment data (2000 days, missing some older dates)
- Bottom: Aligned result (1800 rows after dropping NaN)
- Label: "Alignment = losing data when sources don't overlap"

### Stage 4: Walk-Forward Splits

"For backtesting, you need train/val/test splits that respect time order and don't look forward."

```python
def create_walk_forward_splits(df, initial_train=504, val_size=126, step=63):
    """
    Expanding walk-forward splits.
    504 trading days ≈ 2 years training
    126 trading days ≈ 6 months validation
    step = 63 ≈ 3 months (quarterly retraining)
    """
    splits = []
    dates = df.index
    
    for n_splits in range(6):
        train_start = 0
        train_end = initial_train + (n_splits * step)
        val_start = train_end + 5  # purge window
        val_end = val_start + val_size
        
        if val_end > len(dates):
            break
        
        train_data = df.iloc[train_start:train_end]
        val_data = df.iloc[val_start:val_end]
        
        splits.append({
            'train': train_data,
            'val': val_data,
            'fold': n_splits
        })
    
    return splits
```

**[INFORMATION GAIN]** "This is the same walk-forward CV from Video 2. But here it's applied to the data pipeline. You prepare 6 separate (train, val) pairs once, then use them consistently across all model training."

### Stage 5: Feature Engineering

"Raw OHLCV isn't enough. You need 50+ features. (That's Video 6 — I'll show feature building in depth there.)"

For now: think of it as transformation:
```
Input: [Open, High, Low, Close, Volume, sentiment_mean, sentiment_std, ...]
Output: [RSI_7, RSI_14, MACD, Bollinger, ATR, ADX, Stochastic, OBV,
          Ichimoku, rolling_vol, rolling_skew, rolling_correlation, 
          calendar_features, sentiment_aggregates, ...]
          
Shape: (2500 dates, 50+ features) — ready for ML
```

### Stage 6: Standardization & Scaling

"ML models prefer features scaled to mean=0, std=1."

```python
def scale_train_val(train, val):
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    scaler.fit(train)  # Learn mean/std from TRAINING only
    
    train_scaled = scaler.transform(train)   # Apply to train
    val_scaled = scaler.transform(val)       # Apply to val using SAME scaler
    
    return train_scaled, val_scaled, scaler
```

**[INFORMATION GAIN]** "Critical: fit the scaler on TRAINING ONLY. If you fit on train+val combined, you leak val information into training. Huge mistake that many people make."

---

## 5. ERROR HANDLING & TESTING (28:00–34:00)

### The DataValidator class

```python
class DataValidator:
    def validate(self, df):
        errors = []
        warnings = []
        
        # Check 1: No NaN
        if df.isnull().any().any():
            errors.append(f"NaN found in {df.isnull().sum().sum()} cells")
        
        # Check 2: Realistic prices (shouldn't be negative)
        if (df[['Open', 'High', 'Low', 'Close']] < 0).any().any():
            errors.append("Negative prices detected")
        
        # Check 3: OHLC order (High >= Open, Close, Low)
        if not (df['High'] >= df[['Open', 'Low', 'Close']].max(axis=1)).all():
            errors.append("High < Low or High < Open/Close")
        
        # Check 4: Volume is non-negative
        if (df['Volume'] < 0).any():
            errors.append("Negative volume")
        
        # Check 5: Date continuity (no gaps except weekends)
        date_diffs = df.index.to_series().diff().dt.days
        if (date_diffs > 3).any():  # More than 3 days = gap
            warnings.append(f"Data gap detected: {date_diffs.max()} days")
        
        if errors:
            raise ValueError(f"Data validation failed:\n{errors}")
        if warnings:
            print(f"Warnings: {warnings}")
        
        return True
```

**[DIAGRAM SUGGESTION]** Show a checklist:
```
✅ No NaN values
✅ All prices > 0
✅ OHLC order correct
✅ Volume non-negative
✅ No multi-day gaps
✅ Return distribution sane
✅ Correlation matrix reasonable
```

### Unit tests for the pipeline

```python
def test_pipeline():
    # Test 1: Can load data
    data = load_data("AAPL", "2023-01-01", "2023-12-31")
    assert len(data) > 200
    
    # Test 2: Features are generated
    features = engineer_features(data)
    assert features.shape[1] > 40
    assert not features.isnull().any().any()
    
    # Test 3: Walk-forward splits don't leak
    splits = create_walk_forward_splits(data)
    for split in splits:
        assert split['val'].index[0] > split['train'].index[-1]
    
    # Test 4: Scaling is sane
    train_scaled, val_scaled, scaler = scale_train_val(features[:1000], features[1000:])
    assert train_scaled.mean() < 0.01  # Should be ~ 0
    assert abs(train_scaled.std() - 1.0) < 0.01  # Should be ~ 1
    
    print("All tests passed!")
```

**[INFORMATION GAIN]** "I run these tests every time I rebuild the pipeline. One tiny bug in data loading breaks everything downstream. Automation catches it."

---

## 6. THE FULL PIPELINE IN PRODUCTION (34:00–38:00)

### End-to-end flow

```python
class DataPipeline:
    def __init__(self, config):
        self.config = config
        self.loader = YahooLoader()
        self.validator = DataValidator()
        self.engineer = FeatureEngineer()
    
    def run(self, tickers, start_date, end_date):
        # Stage 1: Load
        data = {}
        for ticker in tickers:
            data[ticker] = self.loader.load(ticker, start_date, end_date)
        
        # Stage 2: Validate
        for ticker, df in data.items():
            self.validator.validate(df)
        
        # Stage 3: Align (merge all tickers)
        aligned = self.align_dataframes(data)
        
        # Stage 4: Split
        splits = self.create_walk_forward_splits(aligned)
        
        # Stage 5: Engineer features
        processed_splits = []
        for split in splits:
            train_features = self.engineer.transform(split['train'])
            val_features = self.engineer.transform(split['val'])
            processed_splits.append({'train': train_features, 'val': val_features})
        
        # Stage 6: Scale
        final_splits = []
        for split in processed_splits:
            train_scaled, val_scaled, scaler = scale_train_val(
                split['train'], split['val']
            )
            final_splits.append({
                'train': train_scaled,
                'val': val_scaled,
                'scaler': scaler
            })
        
        return final_splits
```

**Run time:** ~5 minutes for 100 stocks, 10 years, 50 features.

---

## 7. WHY THIS MATTERS (38:00–40:00)

"A sloppy data pipeline causes 80% of bugs in production trading systems. Off-by-one errors in data alignment, scaling leakage, missing corporate action adjustments — these turn winning strategies into losing ones."

"This pipeline is defensive. It catches issues early, validates at every stage, and forces you to think about train/val splits carefully."

**Bridge:** "Next video: the 50+ features this pipeline generates. Why each one matters, how to debug them, and which ones actually predict returns."

**CTA:**
1. "Subscribe for production-grade ML trading code"
2. "Comment: what data source do you use? Yahoo? Alpaca? IB?"
3. GitHub link (pipeline.py, datavalidator.py, tests)
4. "See you in the next one"

---

## [NEEDS MORE]

- **Your real timing:** How long does loading 100 stocks take? Cache hit time vs cold start?
- **Edge cases you hit:** "I spent a week debugging [specific issue]. Here's what went wrong..."
- **Cost analysis:** "Yahoo Finance free tier can handle X requests. Beyond that, I used [paid source]."
- **Failure story:** "One time I forgot to validate a dataset and trained for 12 hours on corrupted data before realizing."
- **Caching size:** "My Parquet cache is X GB for 100 stocks, 10 years. RAM needed: Y GB."
