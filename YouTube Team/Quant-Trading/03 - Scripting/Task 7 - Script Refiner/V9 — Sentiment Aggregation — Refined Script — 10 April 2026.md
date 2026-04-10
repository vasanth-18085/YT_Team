# V9 — Sentiment Aggregation — Refined Script

**Title:** How to Turn 10,000 Headlines into Trading Features (The Right Way)
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

[INFORMATION GAIN] You fine-tuned FinBERT in Video 4 to score individual headlines. Now what? You have 10,000 scored headlines across 100 stocks spread over years of data. How do you aggregate them into something a trading model can actually use? A naive average completely misses the structure. Recency matters — today's news outweighs last week's. Volume matters — one headline is not the same as twenty. Agreement matters — ten headlines pointing the same direction is different from ten pointing in opposite directions.

I built a system that turns raw sentiment scores into seven daily aggregated features, then validated them with actual event studies to confirm the signal is real and not just noise. This video walks through all of it: the aggregation code, the event study framework, and the results.

---

## SECTION 2 — THE RAW PROBLEM (2:00–6:00)

After running FinBERT inference on a news dataset you end up with a table that looks roughly like this:

```
date        ticker  headline                                     score
2024-01-15  AAPL    Apple beats Q4 earnings expectations       +0.82
2024-01-15  AAPL    Analysts raise AAPL price target           +0.67
2024-01-15  AAPL    Supply chain disruption hits margins       -0.44
2024-01-15  MSFT    Microsoft cloud growth accelerates         +0.71
2024-01-15  MSFT    Antitrust probe expands to new markets     -0.55
...
```

The problem is that models do not consume individual rows. They need one feature vector per stock per day. If AAPL has 5 headlines today and MSFT has 8, you need to reduce both to the same fixed-dimension feature vector before combining them with price and volatility signals.

The naive approach — simple mean — loses most of the information. Three positive headlines and one very negative one average out to mildly positive. But that one very negative headline might be about an accounting scandal. The mean cannot distinguish "mild net positive" from "three positives partially offset by a bombshell negative."

---

## SECTION 3 — THE SEVEN DAILY AGGREGATES (6:00–22:00)

The aggregation produces seven features per stock per day.

```python
class SentimentAggregator:
    def daily_aggregation(
        self, headlines_df: pd.DataFrame, ticker: str, date: str
    ) -> dict:
        day_headlines = headlines_df[
            (headlines_df['ticker'] == ticker) &
            (headlines_df['date'] == date)
        ]
        scores = day_headlines['sentiment_score'].values

        if len(scores) == 0:
            return self._zero_features()

        return {
            'sentiment_mean':     np.mean(scores),
            'sentiment_std':      np.std(scores) if len(scores) > 1 else 0,
            'sentiment_volume':   len(scores),
            'bullish_ratio':      float(np.mean(scores > 0)),
            'sentiment_rw':       self.recency_weighted(scores),
            'sentiment_ew':       self.exponential_weighted(scores),
            'sentiment_momentum': self.compute_momentum(ticker, date),
        }
```

Let me walk through each feature individually, because the reasoning matters.

### Feature 1: sentiment_mean
The average score across all headlines for that stock that day. Has the limitation I described but is the baseline signal.

### Feature 2: sentiment_std
The standard deviation of scores. High standard deviation means conflicting sentiment — some headlines very positive, some very negative. Low standard deviation means consensus. [INFORMATION GAIN] Conflict itself is a signal. When analyst coverage disagrees strongly about a stock, that disagreement reflects genuine uncertainty about future direction. High-std days tend to precede higher-than-average volatility. The model can use sentiment_std as a volatility regime feature, independent of the direction.

### Feature 3: sentiment_volume
How many headlines existed for this stock today. Volume spikes in news coverage — typically precede price moves, whether up or down. A stock that goes from 1 headline per day to 15 headlines on the same day has had something happen. That jump is itself a feature.

### Feature 4: bullish_ratio
The fraction of headlines with positive scores. This captures distribution shape independently of magnitude. A stock with three +0.1 headlines has the same mean as a stock with one +0.9 headline and two -0.4 headlines — but very different bullish_ratios (1.0 vs 0.33).

### Feature 5: sentiment_rw (recency-weighted)

```python
def recency_weighted(self, scores: np.ndarray) -> float:
    if len(scores) == 0:
        return 0.0
    # Earlier headlines get weight 0.5, later ones get weight 1.5
    weights = np.linspace(0.5, 1.5, len(scores))
    return float(np.average(scores, weights=weights))
```

[INFORMATION GAIN] Headlines are ordered by publication time within a day. The first headline at 7am carries less weight than the last one at 5pm, because the market has had more time to react to the morning news. The market-close-weighted version of daily sentiment is a better predictor of next-day opening returns than the equal-weighted version.

### Feature 6: sentiment_ew (exponential-weighted)

```python
def exponential_weighted(self, scores: np.ndarray, span: int = 5) -> float:
    if len(scores) == 0:
        return 0.0
    return float(pd.Series(scores).ewm(span=span).mean().iloc[-1])
```

EWM across headlines within the day gives the most recent sentiment maximum weight while still incorporating earlier context.

### Feature 7: sentiment_momentum

```python
def compute_momentum(self, ticker: str, date: str) -> float:
    today_mean = self.cache.get_mean(ticker, date)
    yesterday_mean = self.cache.get_mean(ticker, self._prev_trading_day(date))
    if yesterday_mean is None:
        return 0.0
    return today_mean - yesterday_mean
```

[INFORMATION GAIN] Sentiment momentum — the change in mean sentiment from yesterday to today — is arguably more predictive than raw sentiment level. A stock with sentiment that jumped from -0.3 to +0.4 overnight carries a stronger signal than a stock that has been stable at +0.5 for a week. The market prices gradual sentiment into prices gradually. Sudden shifts in sentiment represent new information that has not yet been fully incorporated.

### The resulting daily feature table

```
Date        Ticker  mean   std   vol  bull%   rw     ew    mom
2024-01-15  AAPL    0.35  0.25   5   0.60   0.38  0.36  +0.12
2024-01-15  MSFT    0.18  0.30   8   0.50   0.20  0.19  -0.05
2024-01-15  GOOGL   0.42  0.20   3   0.70   0.45  0.43  +0.08
```

---

## SECTION 4 — VALIDATION: EVENT STUDY FRAMEWORK (22:00–32:00)

Generating seven features is only half the work. The other half is proving those features actually predict price movements. The validation tool is the event study, which has been used in academic finance since the 1960s.

```python
class PriceImpactAnalyzer:
    def event_study(
        self,
        headlines_df: pd.DataFrame,
        prices_df: pd.DataFrame,
        event_pre: int = 2,
        event_post: int = 5
    ) -> dict:
        """
        For each news event:
        - Measure baseline return in event_pre days before
        - Measure abnormal return in event_post days after
        - Bucket events by FinBERT sentiment score
        """
        results_by_bucket = {
            'VeryNeg': [], 'Neg': [], 'Neutral': [], 'Pos': [], 'VeryPos': []
        }

        for _, row in headlines_df.iterrows():
            ticker = row['ticker']
            event_date = row['date']
            sentiment = row['FinBERT_score']

            # Baseline: average return in the 2 days before the event
            pre_dates = self._trading_days_before(event_date, event_pre)
            pre_returns = prices_df.loc[
                (prices_df['ticker'] == ticker) &
                (prices_df['date'].isin(pre_dates)), 'return'
            ].values
            baseline = np.mean(pre_returns) if len(pre_returns) > 0 else 0

            # Post-event: average return in 5 days after the event
            post_dates = self._trading_days_after(event_date, event_post)
            post_returns = prices_df.loc[
                (prices_df['ticker'] == ticker) &
                (prices_df['date'].isin(post_dates)), 'return'
            ].values

            if len(post_returns) == 0:
                continue

            # Abnormal return = post-event return - baseline
            abnormal = np.mean(post_returns) - baseline

            bucket = self._sentiment_to_bucket(sentiment)
            results_by_bucket[bucket].append(abnormal)

        return {
            bucket: np.mean(returns)
            for bucket, returns in results_by_bucket.items()
            if len(returns) > 0
        }

    def _sentiment_to_bucket(self, score: float) -> str:
        if score < -0.6: return 'VeryNeg'
        if score < -0.2: return 'Neg'
        if score < 0.2:  return 'Neutral'
        if score < 0.6:  return 'Pos'
        return 'VeryPos'
```

### The result

```
AAPL Event Study — 2015 to 2024 (n=4,280 headlines):

Sentiment Bucket    Avg Post-Event Abnormal Return
VeryNegative        -0.42%
Negative            -0.15%
Neutral             -0.02%
Positive            +0.18%
VeryPositive        +0.55%

Regression: 0.72% per 1.0 unit sentiment increase
p-value: < 0.001
```

[INFORMATION GAIN] The gradient is consistent and statistically significant. More positive FinBERT sentiment reliably precedes better-than-baseline returns over the subsequent 5 trading days. Not enormous — a 0.97% spread between VeryNeg and VeryPos is modest. But it is consistent, it survives standard robustness checks, and in a system that trades every day across 100 stocks, a 0.72% per unit relationship is a genuine edge.

**[DIAGRAM SUGGESTION]** Bar chart with five bars (VeryNeg through VeryPos), Y-axis showing avg abnormal return percentage. Clear staircase pattern going from -0.42% to +0.55%. Title: "FinBERT Sentiment vs Post-Event Returns (AAPL 2015-2024)"

---

## SECTION 5 — ROBUSTNESS CHECKS (32:00–36:00)

Three checks I ran to confirm the event study results are not statistical artefacts.

**Check 1: Market-adjusted returns.** Remove broad market returns from each observation. If the S&P rose 1% on that day, subtract that from the post-event return before bucketing. This isolates stock-specific responses to the news from market-wide moves. The gradient persisted with market adjustment — the sentiment signal is capturing stock-specific information, not just overall market direction.

**Check 2: Volume-stratified analysis.** Run the event study separately for high-volume and low-volume days. A hypothesis: sentiment on high-volume days has more market impact than on low-volume days. The result: correct. The VeryPositive bucket had a 0.38% abnormal return on low-volume days and a 0.71% abnormal return on high-volume days. This confirms that volume and sentiment interact — which is why both are in the daily feature set.

**Check 3: Horizon sensitivity.** Ran the event study for post-event windows of 1, 2, 5, 10, and 20 days. The clearest gradient appears at 5 days. At 1 day, the signal is noisier — some news is too immediate for the full 5-day window. At 20 days, the signal attenuates — sentiment from three weeks ago has been absorbed into price. The 5-day horizon for post-event measurement aligns with the 20-day prediction horizon used in the forecasting models.

---

## SECTION 6 — CROSS-STOCK AND MARKET-LEVEL AGGREGATION (36:00–39:00)

The seven daily features at the ticker level flow into the fusion layer in Video 10. But there are two additional aggregations that add useful context.

### Sector-level sentiment

```python
def sector_sentiment(
    self, date: str, sector: str, universe: list[str]
) -> float:
    sector_stocks = [t for t in universe if self.sector_map[t] == sector]
    daily_scores = [
        self.get_daily_feature(t, date, 'sentiment_mean')
        for t in sector_stocks
    ]
    return np.nanmean(daily_scores)
```

[INFORMATION GAIN] When 80% of tech stocks show negative sentiment on the same day, that is sector-wide risk aversion — not stock-specific news. Stock-specific models that ignore sector collective sentiment will misread these moments as idiosyncratic single-stock signals and mis-size positions. The sector sentiment feature lets the fusion layer adjust for whether bad news about a specific stock is swimming against a positive sector tide or aligned with a sectorwide down-draft.

### Market-level sentiment index

```python
market_sentiment = all_stocks_df.groupby('date')['sentiment_mean'].mean()
```

A single daily number: average sentiment across all stocks in the universe. This serves as a market mood indicator — are analysts broadly positive or negative today? It becomes one of the fusion features in Video 10 alongside VIX and price-based regime indicators.

---

## SECTION 7 — THE CLOSE (39:00–40:00)

Sentiment alone does not trade. As a standalone signal, its predictive power is modest. But as one component in a multi-signal system, it reduces drawdowns and improves the Calmar ratio by incorporating a dimension of market information that price-only models completely miss: how the institutional analyst community is currently feeling about the stock.

Next video: the Fusion Layer. We have four signal types — forecasting model output, technical indicators, sentiment aggregates, and volatility estimates. Video 10 shows how to combine all four into a single ensemble prediction using seven different architectures, and which one wins.

What news sources do you currently track for your system? Comment below — I read every one.

---

## Information Gain Score

**Score: 7/10**

The sentiment_std rationale, recency-weighting reasoning, sentiment momentum as a distinctly different signal from level, event study horizon sensitivity analysis, and volume-stratified results are all genuine additions over standard sentiment-to-features tutorials.

**Before filming, add:**
1. Your actual cross-stock event study numbers beyond AAPL — MSFT, GOOGL results to show the signal generalises
2. The specific day where a high-sentiment-std reading preceded a large volatility move — one example makes this concrete
3. Whether sector sentiment or market sentiment actually ended up in the final feature set after ablation
