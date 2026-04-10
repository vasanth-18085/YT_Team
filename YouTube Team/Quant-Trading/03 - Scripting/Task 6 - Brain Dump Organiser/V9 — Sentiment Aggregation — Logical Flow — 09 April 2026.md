# V9 — Sentiment Aggregation & Price Impact: Extracting Edge from Financial News — Logical Flow

**Title:** "How to Turn 10,000 Headlines into Trading Features (The Right Way)"
**Length:** ~40 min
**Date:** 09 April 2026

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** "You fine-tuned FinBERT to score sentiment. Now what? You have 10,000 headlines across 100 stocks. How do you aggregate them meaningfully? I built a system that turns raw sentiment scores into 7 daily aggregates, then validated that they actually predict price moves using event studies."

---

## 2. THE RAW PROBLEM: 10,000 HEADLINES → 100 STOCKS → 1 DAILY NUMBER? (2:00–6:00)

Not all headlines matter equally. Some are noise.

"Strategy: weight headlines by recency, exclusivity, and agreement strength."

---

## 3. THE AGGREGATION PIPELINE (6:00–22:00)

### Step 1: Single Headline Scoring

From V4, FinBERT outputs: score ∈ [-1, +1]

### Step 2: Intra-Day Aggregation

```python
class SentimentAggregator:
    def daily_aggregation(self, headlines_df, ticker, date):
        # Filter to ticker + date
        day_headlines = headlines_df[(headlines_df['ticker'] == ticker) & 
                                     (headlines_df['date'] == date)]
        scores = day_headlines['sentiment_score'].values  # Array of scores from FinBERT
        
        # 7 aggregated features
        agg = {
            'sentiment_mean': np.mean(scores),                    # Average score
            'sentiment_std': np.std(scores) if len(scores) > 1 else 0,  # Disagreement
            'sentiment_volume': len(scores),                       # # headlines
            'bullish_ratio': np.mean(scores > 0),                 # % positive
            'sentiment_rw': self.recency_weighted(scores),        # Recent news weighted higher
            'sentiment_ew': self.exponential_weighted(scores),    # EW moving average
            'sentiment_momentum': self.compute_momentum(ticker, date)  # Change from yestday
        }
        return agg
    
    def recency_weighted(self, scores):
        """Later headlines weighted more"""
        if len(scores) == 0:
            return 0
        weights = np.linspace(0.5, 1.5, len(scores))  # 0.5 for first, 1.5 for last
        return np.average(scores, weights=weights)
    
    def exponential_weighted(self, scores):
        """Exponential decay: recent news dominates"""
        if len(scores) == 0:
            return 0
        span = 5  # EWA span
        return pd.Series(scores).ewm(span=span).mean().iloc[-1]
    
    def compute_momentum(self, ticker, date):
        """Sentiment change vs yesterday"""
        today_mean = self.get_agg_sentiment(ticker, date)['sentiment_mean']
        yesterday_mean = self.get_agg_sentiment(ticker, date - timedelta(days=1))['sentiment_mean']
        return today_mean - yesterday_mean
```

### Step 3: Daily Feature Matrix

```
Date        Ticker  sent_mean  sent_std  sent_vol  bullish_%  sent_rw  sent_ew  sent_mom
2024-01-15  AAPL    0.35       0.25     5         0.6        0.38    0.36    +0.12
2024-01-15  MSFT    0.18       0.30     8         0.5        0.20    0.19    -0.05
2024-01-15  GOOGL   0.42       0.20     3         0.7        0.45    0.43    +0.08
...
```

**[INFORMATION GAIN]** "7 features per day per stock. sent_std tells you if headlines agree (low = consensus) or disagree (high = controversy). bullish_ratio captures distribution shape."

---

## 4. VALIDATION: DOES SENTIMENT PREDICT PRICE? (22:00–32:00)

### Event Study Framework

"For every headline on date D, measure: what was the post-announcement return?"

```python
class PriceImpactAnalyzer:
    def event_study(self, headlines_df, prices_df, event_pre=2, event_post=5):
        """
        Measure abnormal return around news events.
        event_pre: days before (get baseline)
        event_post: days after (measure impact)
        """
        results_by_bucket = {bucket: [] for bucket in ['VeryNeg', 'Neg', 'Neutral', 'Pos', 'VeryPos']}
        
        for idx, row in headlines_df.iterrows():
            ticker = row['ticker']
            event_date = row['date']
            sentiment = row['FinBERT_score']
            
            # Get returns pre-event (establish baseline)
            pre_dates = pd.date_range(event_date - timedelta(days=event_pre), event_date)
            pre_returns = prices_df.loc[(prices_df['ticker'] == ticker) & 
                                       (prices_df['date'].isin(pre_dates)), 'return'].values
            baseline = np.mean(pre_returns)
            
            # Get returns post-event
            post_dates = pd.date_range(event_date, event_date + timedelta(days=event_post))
            post_returns = prices_df.loc[(prices_df['ticker'] == ticker) & 
                                        (prices_df['date'].isin(post_dates)), 'return'].values
            abnormal = np.mean(post_returns) - baseline
            
            # Bucket by sentiment strength
            sentiment_bucket = self.sentiment_to_bucket(sentiment)
            results_by_bucket[sentiment_bucket].append(abnormal)
        
        # Average effect per bucket
        impact = {bucket: np.mean(returns) for bucket, returns in results_by_bucket.items()}
        return impact
    
    def sentiment_to_bucket(self, score):
        if score < -0.6: return 'VeryNeg'
        if score < -0.2: return 'Neg'
        if score < 0.2: return 'Neutral'
        if score < 0.6: return 'Pos'
        return 'VeryPos'
```

### Example results

```
AAPL Headlines Event Study (2015-2024):
VeryNegative:  -0.42% average post-announce return
Negative:      -0.15%
Neutral:       -0.02%
Positive:      +0.18%
VeryPositive:  +0.55%

Correlation: statistically significant (p < 0.001)
Linear fit: +0.72% per 1.0 sentiment score change
```

**[INFORMATION GAIN]** "Clear gradient. More positive sentiment → higher post-event return. The relationship is REAL."

### Robustness checks

1. **Market-adjusted returns:** Remove broad market moves, isolate stock-specific effect
2. **Control for volume:** High volume + negative sentiment might have different impact than low volume + same sentiment
3. **Intra-day look:** Do sentiment effects show up in minutes/hours or just days?

---

## 5. CROSS-STOCK AGGREGATION (32:00–36:00)

### Sector-level sentiment

"If 80% of tech stocks are negative on the same day, that's sector-wide risk."

```python
sector_sentiment = {}
for sector in ['Tech', 'Finance', 'Healthcare', ...]:
    stocks_in_sector = get_stocks_by_sector(sector)
    daily_scores = [get_daily_sentiment(stock, date) for stock in stocks_in_sector]
    sector_sentiment[sector] = np.mean(daily_scores)
```

### Market-level sentiment

"Average across all stocks → market-wide sentiment index."

```python
market_sentiment = df.groupby('date')['sentiment_mean'].mean()
```

---

## 6. INTEGRATION WITH OTHER SIGNALS (36:00–39:00)

Sentiment feeds into the fusion layer (V10):

```python
fusion_features = {
    'forecast': TiDE_prediction(X),
    'technical': [RSI, MACD, Bollinger, ...],
    'sentiment': sentiment_daily_agg,
    'meta_label_prob': meta_label_confidence,
    'volatility': realized_vol,
}
```

---

## 7. THE PAYOFF (39:00–40:00)

"Sentiment alone doesn't trade. But as one signal in a multi-signal system, it reduces drawdowns and improves cal mar by accounting for behavioral dynamics."

"Next: The Fusion Layer — combining 4 signal types (forecast, technical, sentiment, volatility) into one ensemble prediction."

**CTA:**
1. "Subscribe"
2. "Comment: what news sources do you track?"
3. GitHub (sentiment_aggregator.py, event_study.py)

---

## [NEEDS MORE]

- Your event study results
- Sector sentiment impact
- Daily sentiment heatmap
