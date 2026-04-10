# V6 — 45 Trading Features: The Technical Analysis Bible — Logical Flow

**Title:** "45 Indicators in Python: Every Feature You Need for Stock Prediction"
**Length:** ~40 min
**Date:** 09 April 2026

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** "Feature engineering is 80% of ML. You can have a perfect model, but if you feed it garbage features, it outputs garbage. I engineered 45 trading features from scratch — RSI, MACD, Bollinger Bands, ATR, Ichimoku, rolling correlations, calendar effects, everything. Today you're getting the complete compendium."

---

## 2. WHY FEATURES MATTER MORE THAN MODELS (2:00–6:00)

"A mediocre random forest with great features beats a great transformer with mediocre features. Every time."

**Example:** "I tested two scenarios:
- Scenario A: 500 mediocre features + linear regression → Sharpe 0.7
- Scenario B: 10-20 engineered features + LSTM → Sharpe 1.1

The LSTM was 10x more complex. But the 10 feature-engineered inputs were so informative, even a simple model crushed it."

**Why?** ML models are pattern matchers. If the input data has no pattern, no model finds one.

---

## 3. THE 45 FEATURES: ORGANIZED BY CATEGORY (6:00–35:00)

### Category 1: Momentum (7 features)

```python
class MomentumFeatures:
    def rsi(self, close, period=7):
        """Relative Strength Index — overbought/oversold"""
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))  # Returns 0–100, 70+ = overbought, 30- = oversold
    
    # Also: RSI_14, RSI_21 (different periods are different features)
    # Also: MACD(12,26,9), Stochastic(14), CCI(20), ROC(12)
```

**Why they matter:** RSI tells you if a stock is exhausted (oversold = potential reversal). MACD shows momentum shifts.

**[INFORMATION GAIN]** "These 7 features capture: mean reversion patterns, momentum, overbought/oversold signals. They're uncorrelated with price level — great for ML."

### Category 2: Volatility (8 features)

```python
def atr(high, low, close, period=14):
    """Average True Range — volatility measure"""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def bollinger_bands(close, period=20, num_std=2):
    """Bollinger Bands — dynamic support/resistance"""
    ma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = ma + (std * num_std)
    lower = ma - (std * num_std)
    # Return: band_width, band_height, position_in_bands
    return upper - lower, upper - lower, (close - lower) / (upper - lower)

def adx(high, low, close, period=14):
    """Average Directional Index — trend strength (0-100)"""
    # Complex calculation, but core idea: strong trends → high ADX. Sideways → low ADX.
    # ADX > 25 = strong trend, < 20 = no trend
```

**Why they matter:** Volatility is non-stationary. Bollinger Bands adapt to market regime. ATR normalizes stop-losses.

**[INFORMATION GAIN]** "8 features capturing: daily volatility, regime-adaptive bands, trend strength. Models use these to scale position size."

### Category 3: Trend (7 features)

```python
def ema(close, span):
    """Exponential Moving Average — fast trend follower"""
    return close.ewm(span=span, adjust=False).mean()

def macd(close, fast=12, slow=26, signal=9):
    """MACD — trend + momentum"""
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def adx_trend(high, low, close):
    """ADX trend direction: +DI vs -DI"""
    # Return: +DM_ratio, -DM_ratio (tells you if trend is up or down)
```

**Why they matter:** Trends are real in markets (medium term). EMA helps models ride trends. MACD histogram predicts momentum shifts.

### Category 4: Volume (6 features)

```python
def obv(close, volume):
    """On-Balance Volume — accumulation/distribution"""
    obv_values = []
    obv = 0
    for i in range(len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv += volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv -= volume.iloc[i]
        obv_values.append(obv)
    return pd.Series(obv_values)

def ad_line(high, low, close, volume):
    """Accumulation/Distribution Line"""
    clv = ((close - low) - (high - close)) / (high - low)  # Close Location Value
    return (clv * volume).rolling(21).mean()

def volume_rate_change(volume, period=21):
    """Volume increasing or decreasing?"""
    return volume.pct_change(period)
```

**Why they matter:** Volume confirms trends. Rising price + rising volume = real move. Rising price + falling volume = suspicious.

### Category 5: Ichimoku Cloud (5 features)

```python
def ichimoku(high, low, close):
    """Japanese technical analysis — multi-component"""
    # Tenkan (conversion): (9-period high + 9-period low) / 2
    tenkan = ((high.rolling(9).max() + low.rolling(9).min()) / 2)
    
    # Kijun (base): (26-period high + 26-period low) / 2
    kijun = ((high.rolling(26).max() + low.rolling(26).min()) / 2)
    
    # Senkou spans (leading spans) — future cloud
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
    
    # Chikou (lagging span)
    chikou = close.shift(-26)
    
    return tenkan, kijun, senkou_a, senkou_b, chikou
```

**[INFORMATION GAIN]** "Ichimoku is holistic. It's not just one line — it's a complete support/resistance cloud. Price above cloud = bullish structure. Below = bearish."

### Category 6: Price Structure (5 features)

```python
def returns(close, period=1):
    """Simple returns — the target we're predicting!"""
    return close.pct_change(period)

def log_returns(close, period=1):
    """Log returns — more stationary, better for models"""
    return np.log(close / close.shift(period))

def high_low_ratio(high, low):
    """Intraday range as % of close — volatility proxy"""
    return (high - low) / close

def gap(open, close):
    """Overnight gap as % ofclosing price"""
    return (open - close.shift(1)) / close.shift(1)

def realized_volatility(returns, period=21):
    """Realized volatility over 21 days"""
    return returns.rolling(period).std()
```

### Category 7: Rolling Statistics (5 features)

```python
def rolling_correlation(x, y, period=21):
    """How correlated is price with another series (e.g., VIX)?"""
    return x.rolling(period).corr(y)

def rolling_skewness(returns, period=21):
    """Are returns asymmetric? (left-tailed = crashes likely)"""
    return returns.rolling(period).skew()

def rolling_kurtosis(returns, period=21):
    """Do tails have fat tails? (high = extreme moves likely)"""
    return returns.rolling(period).kurtosis()

def rolling_autocorrelation(returns, period=21, lag=1):
    """Is return on day T correlated with day T-lag?"""
    return returns.rolling(period).apply(lambda x: x.autocorr(lag))

def drawdown(cumulative_return):
    """How far down from peak? (risk metric)"""
    running_max = cumulative_return.expanding().max()
    return (cumulative_return - running_max) / running_max
```

**[INFORMATION GAIN]** "Rolling statistics capture regime. High rolling skew = crash risk. High rolling correlation with VIX = market stress."

### Category 8: Calendar Features (2 features)

```python
def day_of_week(dates):
    """Monday=0, ..., Friday=4 — day-of-week seasonality?"""
    return dates.dayofweek

def day_of_month(dates):
    """Is there a month-end effect? Quarter-ends?"""
    return dates.day
```

**Why they matter (controversial):** Some evidence for day-of-week effects (Monday blues, Friday rallies). Very small but consistent.

---

## 4. FEATURE ENGINEERING ANTIPATTERNS (35:00–37:30)

### Don't do this:

1. **Data leakage:** Using future information in features.
   - WRONG: `feature = log(price_tomorrow / price_today)` — you're using tomorrow's data!
   - RIGHT: `feature = log(price_today / price_yesterday)` — only past data

2. **Look-ahead bias:** Computing features on full dataset, then splitting.
   - WRONG: `df['feature'] = engineer_feature(df)` then split train/val
   - RIGHT: Compute features inside train/val loops separately

3. **Non-stationary features** (huge mistake):
   - WRONG: Raw price level (changes over time, breaks models)
   - RIGHT: Percentage change, log returns, or normalize

4. **Too many features**: 500 features on 2500 samples = overfitting guaranteed.
   - RIGHT: 45-50 carefully selected features.

---

## 5. FEATURE DEBUGGING (37:30–39:30)

**When features go wrong:**

```python
def debug_features(df):
    # Check 1: Any NaN?
    print(df.isnull().sum())
    
    # Check 2: Correlation with target (are features useful?)
    corr_with_target = df.corr()['next_return'].dropna()
    print("Top 10 correlated features:")
    print(corr_with_target.abs().nlargest(10))
    
    # Check 3: Feature scaling (should be similar magnitudes)
    print(df.describe())  # std should be ~ 1 after scaling
    
    # Check 4: Feature stability (does correlation degrade over time?)
    for year in range(2015, 2024):
        year_data = df[df.index.year == year]
        print(f"{year}: RSI avg = {year_data['rsi_7'].mean():.1f}")
```

---

## 6. THE PAYOFF (39:30–40:00)

"45 features. Each selected for a reason. Momentum, volatility, trend, volume, structure, statistics, calendar. Together, they tell your model: what's the market saying?"

"Next video: I throw these 45 features at 14 different ML models. Which one wins? The answer will surprise you."

**CTA:**
1. "Subscribe for feature engineering deep dives"
2. "Comment: What's your favorite indicator? What's a feature you wish existed?"
3. GitHub link (feature_engineer.py, all 45 functions)
4. "See you in the next one"

---

## [NEEDS MORE]

- **Your correlation analysis:** "When I computed correlation between each feature and next-day return, here are the top 10:"
- **Feature stability test:** "How does RSI_7 average change year by year? Is it stable?"
- **Your feature list:** The actual names + descriptions
- **Computation time:** "Computing all 45 features for 100 stocks takes X minutes"
- **Feature interactions:** "Some features are multicollinear (e.g., RSI + Stochastic). I removed one."
