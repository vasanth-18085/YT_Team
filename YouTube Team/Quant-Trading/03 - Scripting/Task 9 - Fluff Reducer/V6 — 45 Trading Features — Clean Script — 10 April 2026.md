# V6 — 45 Trading Features — Clean Script

**Title:** 45 Trading Features Explained: Every Signal In My Quant System
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

[INFORMATION GAIN] The most common mistake in financial ML is feature selection. People copy the first twenty indicators they find on Investopedia and feed them into a model. Then they wonder why their backtest looks good and live trading loses money. The features were noise from the start — you just overfit to them.

This video is every feature in my system with the rationale for why it is there. Not just the code. The rationale — what price phenomenon the feature is supposed to capture, how it can fail, and when I would remove it.

Forty-five features across eight categories. Let me walk you through all of them.

---

## SECTION 2 — CATEGORY 1: MOMENTUM FEATURES (2:00–7:00)

The core idea: prices that have risen over the past N days tend to continue rising in the short term. This is the most replicated finding in empirical asset pricing literature. It also completely stops working in crash regimes. Both things are true.

**[DIAGRAM SUGGESTION]** Eight-segment timeline showing a 60-day rolling window with arrows at 5, 10, 20, and 60 days back. Label each arrow with its return calculation.

```python
def add_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Returns at multiple horizons
    for window in [5, 10, 20, 60]:
        df[f'return_{window}d'] = df['Close'].pct_change(window)

    # 2. Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi_14'] = 100 - 100 / (1 + gain / loss)

    return df
```

You have seven momentum features: returns at 5, 10, 20, 60 days (four features) plus RSI-14 (one feature). The remaining two are momentum z-scores — the raw return divided by the rolling standard deviation. This normalises momentum for volatility regime.

```python
    # 6. Momentum z-score (volatility-normalised momentum)
    df['mom_z_20'] = df['return_20d'] / df['return_1d'].rolling(20).std()
    df['mom_z_60'] = df['return_60d'] / df['return_1d'].rolling(60).std()
```

[INFORMATION GAIN] Why z-score momentum instead of raw return? A 5% return in a stock with daily volatility of 0.5% is qualitatively different from a 5% return in a stock with daily volatility of 3%. The first is 10 standard deviations of movement in 20 days — extraordinary. The second is less than 2 standard deviations — ordinary. The z-score creates comparable units across different volatility regimes, which matters when training on multiple tickers simultaneously.

---

## SECTION 3 — CATEGORY 2: VOLATILITY FEATURES (7:00–12:00)

Volatility predicts volatility — this is the GARCH effect. High volatility periods cluster. If you bought shares yesterday, today's opening volatility tells you something about how much uncertainty surrounds your position.

```python
def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    # Rolling realised volatility
    df['vol_10d']  = df['return_1d'].rolling(10).std()
    df['vol_20d']  = df['return_1d'].rolling(20).std()
    df['vol_60d']  = df['return_1d'].rolling(60).std()

    # Parkinson volatility (uses high-low range)
    log_hl = np.log(df['High'] / df['Low'])
    df['vol_parkinson'] = (log_hl**2 / (4 * np.log(2))).rolling(20).mean()**0.5

    # Garman-Klass volatility
    log_hl = np.log(df['High'] / df['Low'])
    log_co = np.log(df['Close'] / df['Open'])
    df['vol_gk'] = (0.5 * log_hl**2 - (2*np.log(2)-1) * log_co**2).rolling(20).mean()**0.5

    # ATR - Average True Range
    tr = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - df['Close'].shift()).abs(),
        (df['Low'] - df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(14).mean()

    # Vol ratio: short-term vs long-term
    df['vol_regime'] = df['vol_10d'] / df['vol_60d']

    return df
```

[INFORMATION GAIN] Parkinson and Garman-Klass volatility estimators use intraday high-low data rather than just closing prices. Rolling close-to-close volatility ignores everything that happens during the trading day. A stock that opens at 100, spikes to 115 during the day, and closes at 101 has low close-to-close volatility but enormous intraday volatility. For options and position sizing, the intraday path matters. Parkinson is approximately 20% more efficient than close-to-close for estimating true volatility.

`vol_regime` — the ratio of 10-day to 60-day volatility — is a regime detector embedded in the feature set. A ratio above 1 means short-term volatility is elevated relative to the long-term baseline. The models can use this to adjust their confidence even without explicit regime labeling from Video 14.

---

## SECTION 4 — CATEGORY 3: TREND FEATURES (12:00–16:00)

Trend features encode the direction of the broader price move. Momentum features look at returns over a fixed window. Trend features look at the structure of moving averages — whether the price is above or below various smoothing levels and whether those smoothing levels are aligned.

```python
def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    # Moving averages
    df['ma_20']  = df['Close'].rolling(20).mean()
    df['ma_50']  = df['Close'].rolling(50).mean()
    df['ma_200'] = df['Close'].rolling(200).mean()

    # Price relative to MAs
    df['price_to_ma20']  = df['Close'] / df['ma_20'] - 1
    df['price_to_ma50']  = df['Close'] / df['ma_50'] - 1
    df['price_to_ma200'] = df['Close'] / df['ma_200'] - 1

    # MA alignment: golden cross / death cross region
    df['ma_trend'] = (df['ma_20'] > df['ma_50']).astype(int) * 2 - 1  # +1 or -1
    df['ma_spread'] = (df['ma_20'] - df['ma_50']) / df['ma_50']

    return df
```

Seven trend features. The three price-to-MA features capture distance from each anchor. `ma_trend` is a binary signal: is the 20-day average above or below the 50-day? `ma_spread` is its quantified magnitude.

[INFORMATION GAIN] Price-to-MA features are mean-reverting. When a stock is 15% above its 200-day MA, mean reversion theory predicts a pull-back. When it is 15% below, value theory predicts a recovery. What makes this interesting for ML is that in trending regimes, both overextension signals can *predict continuation* rather than reversal — the market can stay irrational longer than intuition expects. The model learns which regime it is in from the volatility features and the regime detection in Video 14.

---

## SECTION 5 — CATEGORY 4: VOLUME FEATURES (16:00–20:00)

Volume confirms price action. A rising stock on falling volume is a weaker signal than a rising stock on rising volume. Volume features encode this confirmation dimension.

```python
def add_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    # Volume ratio: today vs recent average
    df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()

    # OBV: On-Balance Volume
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['obv'] = np.array(obv)
    df['obv_signal'] = df['obv'].ewm(span=9).mean()

    # Volume price trend
    df['price_volume'] = df['return_1d'] * df['Volume']
    df['pv_trend'] = df['price_volume'].rolling(10).sum()

    return df
```

[INFORMATION GAIN] OBV is one of the oldest technical indicators — Gerald Appel introduced it in 1963. It has survived because it captures something real: cumulative buying pressure. When price rises on heavy volume, that volume gets added to OBV. When price falls on light volume, less gets subtracted. A stock where OBV is rising while price is flat is accumulating smartly — institutions are building a position without moving the price. That divergence is a genuine signal that older technical analysis identified before ML existed.

`pv_trend` is a 10-day signed volume flow. The sum of (daily return × daily volume) over 10 days gives the net dollar flow direction over the window. Positive means money flowed in on net; negative means it flowed out.

---

## SECTION 6 — CATEGORY 5: ICHIMOKU FEATURES (20:00–24:00)

Ichimoku Kinkō Hyō is a Japanese charting system from the 1930s. It is the one indicator outsiders find visually intimidating and insiders find genuinely useful. The English translation is "one glance equilibrium chart."

```python
def add_ichimoku_features(df: pd.DataFrame) -> pd.DataFrame:
    # Tenkan-sen (Conversion Line): 9-period midpoint
    high_9  = df['High'].rolling(9).max()
    low_9   = df['Low'].rolling(9).min()
    df['tenkan'] = (high_9 + low_9) / 2

    # Kijun-sen (Base Line): 26-period midpoint
    high_26 = df['High'].rolling(26).max()
    low_26  = df['Low'].rolling(26).min()
    df['kijun'] = (high_26 + low_26) / 2

    # Senkou Span A (leading A): avg of tenkan and kijun, shifted 26 periods forward
    df['senkou_a'] = ((df['tenkan'] + df['kijun']) / 2).shift(26)

    # Senkou Span B (leading B): 52-period midpoint, shifted 26 periods forward
    high_52 = df['High'].rolling(52).max()
    low_52  = df['Low'].rolling(52).min()
    df['senkou_b'] = ((high_52 + low_52) / 2).shift(26)

    # Cloud position: +1 if price above cloud, -1 if below
    cloud_top = df[['senkou_a', 'senkou_b']].max(axis=1)
    cloud_bot = df[['senkou_a', 'senkou_b']].min(axis=1)
    df['kumo_position'] = np.where(df['Close'] > cloud_top, 1,
                          np.where(df['Close'] < cloud_bot, -1, 0))

    return df
```

[INFORMATION GAIN] Five Ichimoku features: tenkan, kijun, senkou_a, senkou_b, and kumo_position. The tenkan-kijun cross is similar to the golden cross but on shorter time horizons. Kumo position is the most predictively useful feature — it encodes whether the price is above the cloud (bullish territory), below it (bearish), or inside it (conflict zone).

The Japanese practitioners who use Ichimoku on equity markets have empirically found that the cloud provides dynamic support and resistance — price tends to stall at cloud boundaries and accelerate when it clears them. This has an ML-amenable representation as the `kumo_position` feature, which turns that continuous cloud relationship into a discrete categorical signal.

---

## SECTION 7 — CATEGORY 6: PRICE STRUCTURE (24:00–27:00)

Price structure features capture candlestick shapes and the relationship between open, high, low, and close within individual sessions.

```python
def add_price_structure_features(df: pd.DataFrame) -> pd.DataFrame:
    # Candle body size
    df['body_size'] = (df['Close'] - df['Open']).abs() / df['Open']

    # Upper shadow
    df['upper_shadow'] = (df['High'] - df[['Open','Close']].max(axis=1)) / df['Open']

    # Lower shadow
    df['lower_shadow'] = (df[['Open','Close']].min(axis=1) - df['Low']) / df['Open']

    # Gap
    df['gap'] = (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)

    # Price position in daily range
    df['price_position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'])

    return df
```

[INFORMATION GAIN] `price_position` is the Williams %R concept normalised to a 0-1 range. A close at 0 means the stock closed at its daily low. A close at 1 means it closed at its daily high. Stocks that consistently close near their high are showing internal buying strength. Stocks that gap up but sell all day and close near the low are showing distribution — sellers are using each rally to exit. The model can learn these patterns without being explicitly told about candlestick theory.

---

## SECTION 8 — CATEGORY 7: ROLLING STATISTICS (27:00–31:00)

Rolling statistics capture the distributional shape of returns — not just their direction and magnitude but their stability.

```python
def add_rolling_stats_features(df: pd.DataFrame) -> pd.DataFrame:
    returns = df['return_1d']

    # Skewness: direction of tail
    df['skew_20d'] = returns.rolling(20).skew()

    # Kurtosis: fat-tail indicator
    df['kurt_20d'] = returns.rolling(20).kurt()

    # Autocorrelation at lag 1
    df['autocorr_1d'] = returns.rolling(20).apply(
        lambda x: x.autocorr(1), raw=False
    )

    # Drawdown from 60-day high
    rolling_max = df['Close'].rolling(60).max()
    df['drawdown_60d'] = (df['Close'] - rolling_max) / rolling_max

    # Consecutive up/down days
    up_streak = (returns > 0).astype(int)
    df['streak'] = up_streak.groupby(
        (up_streak != up_streak.shift()).cumsum()
    ).cumcount() + 1

    return df
```

[INFORMATION GAIN] Skewness and kurtosis of the rolling return distribution — this is unusual to include as features and most textbook systems omit them. The reason they matter: a stock with negative skew returns has more very bad days than very good ones. Negative skew combined with fat kurtosis (heavy tails) is the statistical profile of a stock that has risk of blowup. The model can use these features to reduce position size or skew predictions toward caution for such stocks, even without explicit risk management rules.

`autocorr_1d` is particularly interesting. Positive autocorrelation at lag 1 means: if yesterday was a positive return day, today probably is too. That is the momentum signal in its most direct form. Negative autocorrelation is mean reversion signal. The market switches between these regimes and the rolling 20-day autocorrelation captures which regime you are currently in.

---

## SECTION 9 — CATEGORY 8: CALENDAR FEATURES (31:00–33:00)

Two lightweight calendar features that capture seasonal and weekly patterns.

```python
def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df['day_of_week'] = df.index.dayofweek   # 0=Mon, 4=Fri
    df['month']       = df.index.month       # 1-12

    return df
```

[INFORMATION GAIN] Two features, no apologies. Calendar effects are real — Monday has historically had different return profiles than Friday, and January has the January effect. But these are weak signals and the model will learn to mostly ignore them. They are included to give the model the option of using seasonality if it genuinely improves prediction. The model will weight them appropriately via tree-based or attention-based feature importance. Including two integer features is negligible computational cost.

---

## SECTION 10 — ANTIPATTERNS AND DEBUGGING (33:00–38:00)

I want to walk through three mistakes I made and would have made if I did not catch them during validation.

**Antipattern 1: Using the next day's price in feature calculation**

```python
# WRONG — this leaks future information
df['tomorrow_return'] = df['Close'].shift(-1) / df['Close'] - 1  # shift(-1) looks ahead

# RIGHT — today's feature uses only past data
df['yesterday_return'] = df['Close'].shift(1) / df['Close'] - 1  # shift(+1) looks backward
```

[INFORMATION GAIN] `shift(-1)` is the most common source of data leakage in financial ML. It calculates a feature using tomorrow's price today. Your model then effectively can see the future, and your backtest will have a near-perfect Sharpe ratio. When you go live, it will lose money immediately. The fix: always use `shift(+1)` for features and `shift(-1)` only for the *target label* — which you want to be tomorrow's return.

**Antipattern 2: Normalising across the full dataset before splitting**

Already covered in Video 5, but worth repeating here in the features context. If you compute rolling standardisation using the mean and std of the full dataset, you contaminate training features with test-period information.

**Antipattern 3: Correlated feature clusters**

```python
# These four features are effectively the same thing:
df['return_1d']     # raw
df['return_1d_sq']  # squared
df['return_1d_abs'] # absolute
df['return_1d_log'] # log

# One is enough in most cases
```

[INFORMATION GAIN] Highly correlated features do not add information — they add noise and slow down training. Before fitting any model, I run a correlation matrix on the feature set and drop any features with Pearson correlation above 0.95 with another feature. The feature that stays is the one with higher predictive power, measured by information coefficient against the label.

### Feature debugging utility

When a model is underperforming, the first thing to check is feature quality, not model architecture. Use this:

```python
def debug_feature_quality(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    results = []
    for col in df.select_dtypes(include='number').columns:
        if col == target_col:
            continue
        ic = df[[col, target_col]].corr().iloc[0, 1]
        nan_pct = df[col].isna().mean()
        results.append({'feature': col, 'IC': ic, 'nan_pct': nan_pct})
    return pd.DataFrame(results).sort_values('IC', ascending=False)
```

Information Coefficient (IC) is the Pearson correlation between the feature and the next-period return label. An IC of 0.05 is considered meaningful in quantitative finance. An IC below 0.01 means the feature is essentially uncorrelated with future returns — it is noise. This does not mean remove it immediately; it means investigate why and cross-check on subperiods.

---

## SECTION 11 — THE CLOSE (38:00–40:00)

Forty-five features across eight categories. Every one of them exists for a reason.

What makes this feature set different from a random collection of indicators: it covers independent dimensions of the price process — momentum, risk, trend, volume, structure, seasonality. These dimensions are partially independent, and the ML models can combine them more effectively than any rules-based system.

The next video: these features go into fourteen forecasting models. Every model evaluated side by side, on the same data, with the same cross-validation protocol. No cherry-picking, no survivorship bias.

See you there.

---

## Information Gain Score

**Score: 7/10**

The momentum z-score reasoning, Parkinson vs close-to-close volatility explanation, OBV history, Ichimoku kumo encoding, skewness/kurtosis inclusion rationale, and the shift(-1) antipattern explanation all provide material that goes beyond surface-level indicator description.

**Before filming, add:**
1. Your actual IC values for the top and bottom 5 features — this is the one number that proves the feature selection was principled
2. Which features you removed after seeing IC values
3. One specific moment where an antipattern bit you — a real example makes this section land
