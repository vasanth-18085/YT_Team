# V20 — Performance Tearsheet — Clean Script

**Title:** The 6-Panel Strategy Report That Replaces Your Equity Curve
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

Most people evaluate a trading strategy by looking at an equity curve. A line going up and to the right. If it looks good, they deploy. This is like evaluating a car by only looking at the top speed and ignoring the brakes, fuel efficiency, handling, and crash test rating.

A professional tearsheet is a single-page diagnostic with 6 panels that tell you everything you need to know about a strategy: how it performed, how risky the ride was, whether the edge is stable or decaying, how the returns distribute across time, what the tail risk looks like, and whether the costs are sustainable.

[INFORMATION GAIN] I built a Tearsheet class that takes a return series and automatically generates all 6 panels with 13 computed statistics. The output is a publication-quality figure that I use for every walk-forward fold and every model comparison. The tearsheet has caught problems that the headline Sharpe completely hid — specifically a model with Sharpe 0.85 that had negative skew of minus 1.4, meaning it was collecting small daily gains and occasionally taking massive losses. The Sharpe looked great because the average return was positive. But the tail risk was unacceptable. Without the return distribution panel, I would have deployed it.

---

## SECTION 2 — WHY EQUITY CURVES LIE (2:00–8:00)

An equity curve is a cumulative sum of returns. It shows you one number per day — the total value. That is the least informative way to display performance data.

Here is what an equity curve hides. First: it hides drawdown severity. An equity curve that goes from 100K to 150K in 2 years looks great. But if it went 100K to 80K to 60K to 150K, you experienced a 40 percent drawdown that lasted 8 months. Most humans would have stopped trading during that drawdown. The equity curve does not show the pain.

Second: it hides return distribution. The curve might be driven by 5 lucky trades that each returned 10 percent while the other 245 trading days were flat or slightly negative. The strategy is really a lottery ticket, not a consistent edge. The curve hides this because cumulative returns smooth over the daily reality.

Third: it hides regime dependence. The equity curve went up during 2020 to 2021 (the everything rally) and was flat during 2022 (the rate hike correction). Is the strategy good or was it just long in a bull market? The curve does not decompose the return into regime-specific periods.

Fourth: it hides cost sustainability. The gross equity curve might show 15 percent annual return. But if cost drag is 6 percent, the net return is 9 percent. And if turnover increases (because you are scaling or changing the rebalance frequency), cost drag can rise to 10 percent, making the net return 5 percent — barely worth the operational risk.

The tearsheet addresses all four blind spots across its 6 panels.

---

## SECTION 3 — THE TEARSHEET CLASS AND PANEL 1: EQUITY CURVE (8:00–14:00)

The Tearsheet class in `src/m8_backtest/tearsheet.py`:

```python
class Tearsheet:
    def __init__(
        self,
        returns: pd.Series,
        benchmark: pd.Series | None = None,
        title: str = "Strategy Tearsheet",
        risk_free: float = 0.0,
    ):
        self.returns = returns
        self.benchmark = benchmark
        self.title = title
        self.risk_free = risk_free
        self._stats: dict | None = None
```

It takes your strategy's daily return series and an optional benchmark return series. The `full_report()` method generates a 3-by-2 grid of matplotlib subplots — the 6 panels — sized at 18 by 24 inches and saved at 150 DPI for publication quality.

Panel 1 is the equity curve — but done properly. It plots the cumulative return of the strategy as a solid line and the benchmark as a dashed line on the same axes. Both start at 1.0 (or 100 percent) so you can visually compare growth rates.

```python
def _plot_equity(self, ax):
    equity = (1 + self.returns).cumprod()
    ax.plot(equity.index, equity.values, label="Strategy", linewidth=1.5)
    if self.benchmark is not None:
        bench_eq = (1 + self.benchmark).cumprod()
        ax.plot(bench_eq.index, bench_eq.values,
                label="Benchmark", linewidth=1.0, linestyle="--", alpha=0.7)
    ax.set_title("Cumulative Returns")
    ax.legend()
    ax.grid(True, alpha=0.3)
```

The benchmark comparison is critical. An equity curve that goes up 50 percent over 3 years looks good in isolation. But if the S&P 500 went up 60 percent in the same period, you underperformed a free index fund. Always plot against a benchmark.

[INFORMATION GAIN] I use SPY as the benchmark for my pipeline. The strategy's cumulative return over 5 years was 42 percent versus SPY's 65 percent. On raw cumulative return, the strategy underperformed the benchmark. But the strategy had a max drawdown of negative 18 percent versus SPY's negative 34 percent (March 2020). The strategy preserved capital during the crash and compounded more efficiently despite lower gross return. This is why you need the full tearsheet — cumulative return alone says SPY won, but risk-adjusted return says the strategy won.

---

## SECTION 4 — PANEL 2: DRAWDOWN CHART (14:00–20:00)

The drawdown panel shows the underwater curve — how far below the previous equity high you are at each point in time.

```python
def _plot_drawdown(self, ax):
    equity = (1 + self.returns).cumprod()
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    ax.fill_between(drawdown.index, drawdown.values, 0,
                    color="red", alpha=0.3)
    ax.plot(drawdown.index, drawdown.values, color="red",
            linewidth=0.8)
    ax.set_title("Drawdown")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.3)
```

The drawdown chart answers three questions that the equity curve cannot.

First: how deep are the worst drops? The maximum drawdown is the deepest red on the chart. For my pipeline, negative 18 percent. This is the worst-case pain you would have experienced as an investor in this strategy.

Second: how long do drawdowns last? This is the width of the red regions. Recovery time matters more than depth for many investors. A sharp negative 15 percent that recovers in 2 weeks is psychologically easier than a shallow negative 5 percent that persists for 6 months. The 6-month drawdown suggests the edge has structurally broken.

Third: how frequent are drawdowns? If the chart shows continuous red with brief green breaks, the strategy is volatile and psychologically demanding. If it shows long green stretches interrupted by brief red events, the strategy is stable with occasional pullbacks.

[INFORMATION GAIN] Drawdown duration is often a better predictor of strategy abandonment than drawdown depth. Professional teams can tolerate a sharp negative 15 percent drawdown that recovers in 2 weeks because they understand volatility. They cannot tolerate a negative 5 percent drawdown that persists for 6 months because it suggests the edge has structurally broken. Duration signals regime change. Depth may be normal volatility.

The top 3 drawdown events are automatically annotated with dates and recovery times in the stats table (Panel 6). This lets you correlate drawdowns with known market events — COVID crash, rate hikes, sector rotations — and understand whether the strategy fails systematically in certain conditions.

---

## SECTION 5 — PANELS 3 AND 4: ROLLING SHARPE AND MONTHLY HEATMAP (20:00–28:00)

Panel 3 shows the 126-day (6-month) rolling Sharpe ratio over time.

```python
def _plot_rolling_sharpe(self, ax):
    rolling_ret = self.returns.rolling(126).mean()
    rolling_vol = self.returns.rolling(126).std()
    rolling_sharpe = (rolling_ret - self.risk_free / 252) / (rolling_vol + 1e-12)
    rolling_sharpe *= np.sqrt(252)
    ax.plot(rolling_sharpe.index, rolling_sharpe.values,
            linewidth=1.0, color="steelblue")
    ax.axhline(y=0, color="black", linewidth=0.5, linestyle="--")
    ax.set_title("126-Day Rolling Sharpe")
    ax.grid(True, alpha=0.3)
```

This is the stability diagnostic. A stable strategy shows a rolling Sharpe that fluctuates around a consistent positive level — maybe oscillating between 0.5 and 1.5 but always positive. An unstable strategy shows a rolling Sharpe that crosses zero frequently, has long negative stretches, or trends downward.

My interpretation guide. Rolling Sharpe consistently above 0.5: robust edge. Oscillating between negative 0.5 and 1.5: edge exists but is regime-dependent and will require patience during drawdowns. Trending downward over time: alpha decay — investigate whether drift monitoring from V15 is detecting degradation. Negative for 3 or more consecutive months: the strategy may be broken and should be halted.

[INFORMATION GAIN] I compare 3-month and 12-month rolling Sharpe windows. If the 3-month Sharpe is negative but the 12-month is positive, the strategy is in a temporary drawdown within a longer positive trend — probably fine, ride it out. If both are negative, the edge may have genuinely disappeared. This dual-window approach prevents overreacting to short-term noise while catching genuine deterioration. My DriftMonitor from V15 uses a similar principle with its 60-day rolling window versus 120-day baseline.

Panel 4 is the monthly returns heatmap — months as columns (January through December), years as rows. Each cell is coloured by monthly return: green for positive, red for negative, intensity proportional to magnitude.

```python
def _plot_monthly_heatmap(self, ax):
    monthly = self.returns.resample("M").apply(
        lambda x: (1 + x).prod() - 1
    )
    table = pd.DataFrame({
        'year': monthly.index.year,
        'month': monthly.index.month,
        'return': monthly.values
    })
    pivot = table.pivot(index='year', columns='month', values='return')
    sns.heatmap(pivot, annot=True, fmt=".1%", cmap="RdYlGn",
                center=0, ax=ax, cbar=False)
    ax.set_title("Monthly Returns")
```

The heatmap reveals three things that summary statistics hide. Seasonal patterns: does the strategy systematically underperform in September? Many momentum strategies do because of fiscal year-end rebalancing. Clustering of losses: are bad months adjacent, suggesting regime-driven failure rather than random bad luck? Consistency: are the positive months evenly spread or concentrated in a few months?

[INFORMATION GAIN] A strategy that returns 12 percent annually might have earned all of it in January through March and been flat for 9 months. That is effectively a seasonal bet, not a year-round alpha. The heatmap makes this immediately obvious while the annual return figure hides it completely. My pipeline's heatmap shows no strong seasonal pattern — losses are scattered rather than clustered. The worst month was negative 6.2 percent (March 2020). The best was positive 8.3 percent. Most months fall between negative 2 percent and positive 3 percent.

---

## SECTION 6 — PANELS 5 AND 6: DISTRIBUTION AND STATS TABLE (28:00–36:00)

Panel 5 is the daily return distribution — a histogram overlaid with a fitted normal distribution curve.

```python
def _plot_return_distribution(self, ax):
    ax.hist(self.returns.values, bins=50, density=True,
            alpha=0.6, color="steelblue", edgecolor="white")
    mu, sigma = self.returns.mean(), self.returns.std()
    x = np.linspace(self.returns.min(), self.returns.max(), 200)
    normal_pdf = stats.norm.pdf(x, mu, sigma)
    ax.plot(x, normal_pdf, 'r--', linewidth=1.5, label="Normal fit")
    ax.set_title("Daily Return Distribution")
    ax.legend()
```

The gap between the histogram and the normal curve is the tail-risk story. If the histogram has fatter left tails than the normal curve, you have more extreme losses than a Gaussian model predicts. This means VaR estimates based on normality are understating your risk.

Three key statistics from the distribution. Skewness: zero for normal. Negative means more large losses than large gains. My pipeline: negative 0.3, mildly left-skewed. This is acceptable for an equity strategy. Strategies with skewness below negative 1.0 should be treated with extreme caution regardless of their Sharpe.

Kurtosis: 3.0 for normal. Higher means fatter tails. My pipeline: 4.2, meaning excess kurtosis of 1.2. Extreme days happen more often than normal predicts. This affects position sizing — if you size based on standard deviation assuming normality, you will be over-exposed during tail events.

The Jarque-Bera test formally tests whether the returns are normally distributed. P-value less than 0.05 rejects normality. My pipeline: p-value essentially at zero. Returns are definitively non-normal. This is why the Deflated Sharpe from V19 adjusts for skewness and kurtosis.

Panel 6 is the stats table — the comprehensive numerical summary.

```python
def _plot_stats_table(self, ax):
    stats = self.summary()
    rows = [
        ["Total Return", f"{stats['total_return']:.1%}"],
        ["CAGR", f"{stats['cagr']:.1%}"],
        ["Ann. Volatility", f"{stats['annual_vol']:.1%}"],
        ["Sharpe Ratio", f"{stats['sharpe']:.2f}"],
        ["Sortino Ratio", f"{stats['sortino']:.2f}"],
        ["Calmar Ratio", f"{stats['calmar']:.2f}"],
        ["Max Drawdown", f"{stats['max_drawdown']:.1%}"],
        ["Max DD Duration", f"{stats['max_dd_days']} days"],
        ["Win Rate", f"{stats['win_rate']:.1%}"],
        ["Profit Factor", f"{stats['profit_factor']:.2f}"],
        ["Skewness", f"{stats['skewness']:.2f}"],
        ["Kurtosis", f"{stats['kurtosis']:.2f}"],
        ["Daily Turnover", f"{stats.get('daily_turnover', 0):.2%}"],
    ]
    ax.axis("off")
    table = ax.table(cellText=rows, colLabels=["Metric", "Value"],
                     loc="center", cellLoc="center")
```

Each metric answers a specific question. Sharpe: return per unit of total risk. Sortino: return per unit of downside risk — more relevant for strategies with asymmetric returns because it only penalises downward volatility. Calmar: return per unit of maximum drawdown — how much pain per unit of gain. A Calmar above 1.0 is excellent. Between 0.5 and 1.0 is good. Below 0.3 means the drawdowns are disproportionate to the returns.

Win rate: what fraction of days were profitable. Profit factor: sum of all positive returns divided by the absolute sum of all negative returns. A profit factor above 1.5 means your winners are meaningfully larger than your losers.

[INFORMATION GAIN] The single most underrated metric on the tearsheet is cost drag — the annualised reduction in return from transaction costs. If your CAGR is 12 percent gross and 10 percent net, the cost drag is 2 percent. This connects the backtesting world to the real execution world. If turnover increases by 50 percent due to scaling or parameter changes, cost drag increases proportionally and your net return drops by another 1 percent. Monitoring this number every time you modify the pipeline prevents the slow creep of costs eroding your edge.

---

## SECTION 7 — HOW TO READ THE TEARSHEET AS A WHOLE AND THE CLOSE (36:00–40:00)

Do not look at the 6 panels individually. Read them as a story.

Start with Panel 6, the stats table. Check the Sharpe, Calmar, and max drawdown. If any are below your minimum thresholds (I use Sharpe above 0.5, Calmar above 0.3, max drawdown better than negative 30 percent), do not proceed.

Next, Panel 1 and 2 — equity curve and drawdown. Does the equity curve grow consistently or was it driven by a few large moves? Are the drawdowns brief and recoverable or long and deep? Correlate the worst drawdown dates with known market events. If the strategy always fails during rate hikes, you have a structural vulnerability to monitor.

Then Panel 3 — rolling Sharpe. Is the edge stable over time or decaying? A downward trend means the strategy is losing its predictive power and may need retraining soon.

Panel 4 — monthly heatmap. Any seasonal patterns? Any clustering of losses? If all serious losses happened during two specific months, investigate whether there is a structural reason.

Finally Panel 5 — return distribution. Negative skew and high kurtosis mean the strategy has hidden tail risk that the Sharpe ratio understates. Adjust your position sizing downward if kurtosis exceeds 5.

The tearsheet is generated with `full_report()` and saved to PNG with `save()`. I generate one per walk-forward fold, one for the full out-of-sample period, and one comparing gross versus net (pre-cost versus post-cost) returns. That gives me a complete diagnostic set for any pipeline configuration.

Three numbers from this video. 6 panels covering equity, drawdown, stability, seasonality, distribution, and statistics. 13 computed metrics from Sharpe to cost drag. And 1 diagnostic that caught a model with 0.85 Sharpe but negative 1.4 skewness — a hidden tail-risk bomb.

Next video: experiment tracking. After 200 model runs, you need a system to log every configuration, every result, and every insight so you can reproduce any experiment and build on your best ideas systematically.

---

## Information Gain Score

**Score: 7/10**

Strong on the panel-by-panel explanation with code, the "equity curves lie" framing, the practical interpretation guide, and the cost drag insight. The skewness negative 1.4 case study is a compelling example of why the tearsheet matters.

**Before filming, add:**
1. Your actual tearsheet PNG from the best walk-forward fold — annotate each panel
2. The negative 1.4 skewness tearsheet side by side with the production model's tearsheet
3. Gross vs net tearsheet comparison showing cost drag impact
4. A live walkthrough of reading a tearsheet from scratch — narrate your thought process
