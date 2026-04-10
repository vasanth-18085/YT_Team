# V20 — Performance Tearsheet — Logical Flow — 09 April 2026

**Title:** How to Present Strategy Results Like a Quant Team
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** A pretty equity curve is not a performance report. Professional quant teams do not look at a single chart and decide to deploy capital. They want a tearsheet: return metrics, risk metrics, stability analysis, drawdown structure, turnover analysis, and cost attribution — all on one page. I built a Tearsheet class that generates a publication-quality 6-panel report automatically from any backtest result. This video shows you what each panel means, why it matters, and how to read a tearsheet like a portfolio manager.

## 2. WHY TEARSHEETS EXIST (2:00–8:00)

The equity curve is the most misleading chart in quant finance. A smooth upward line hides: how volatile the ride was, how deep the drawdowns were, whether the Sharpe was consistent or concentrated in one lucky period, how much turnover generated costs, and whether the returns look like a normal distribution or have fat tails.

Professional quant funds use tearsheets because capital allocation decisions require a multi-dimensional view of risk and return. A portfolio manager allocates capital across 20+ strategies. They need to compare: which strategy has the best risk-adjusted return (Sharpe), the worst drawdown experience (max DD and duration), the most stable edge (rolling Sharpe), and the most realistic cost profile (turnover × fees).

**[INFORMATION GAIN]** At quant fund interviews, you will be asked to present a tearsheet, not an equity curve. If you show only a chart going up and to the right, the interviewer assumes you are hiding something. The tearsheet is the standardized language of quant performance — learning to read and produce one is a genuine career skill.

## 3. THE TEARSHEET CLASS ARCHITECTURE (8:00–14:00)

The implementation in `src/m8_backtest/tearsheet.py` takes a BacktestResult object and produces a 6-panel matplotlib figure.

Constructor: Tearsheet(result, title). The result object contains: equity series, daily returns series, positions series, turnover series, costs series, stats dictionary, trades DataFrame, and optional benchmark equity.

Main method: `full_report(figsize=(18, 24))` returns a matplotlib Figure with 6 subplots arranged in a 3x2 grid. Each panel serves a specific diagnostic purpose.

The design philosophy: one page, no scrolling, no click-through. Everything a decision-maker needs is visible simultaneously. The panels are ordered from most important (equity curve, drawdown) to most detailed (monthly heatmap, return distribution).

## 4. PANEL 1: EQUITY CURVE + BENCHMARK (14:00–18:00)

The top-left panel shows the cumulative equity curve of your strategy overlaid with the benchmark (typically S&P 500 buy-and-hold). Both start at $100,000 for easy comparison.

Key visual signals: Does the strategy line stay above the benchmark? Is the gap widening over time (compounding alpha) or narrowing (decaying alpha)? Are there periods where the strategy underperforms the market?

The panel also annotates the total return and CAGR in the legend. My pipeline: strategy total return 68%, CAGR 12.4%, benchmark total return 55%, CAGR 9.8%. The strategy outperforms by 2.6% annualized — meaningful but not spectacular after costs.

**[INFORMATION GAIN]** The equity curve comparison is where you immediately see whether your strategy has genuine excess return (alpha) or is just levered market exposure (beta). If your equity curve moves in lockstep with the benchmark but higher, you are mostly capturing beta with moderate alpha. If it moves independently, you have genuine alpha. The correlation between strategy and benchmark returns is a quick quantitative check.

## 5. PANEL 2: UNDERWATER DRAWDOWN CHART (18:00–24:00)

The top-right panel shows the drawdown percentage over time — how far below the previous peak the equity sits at each point. This is the most important risk panel.

Visually it looks like an inverted bar chart hanging below zero. Deep troughs are severe drawdowns. Wide troughs are long drawdowns. The ideal pattern is shallow and brief troughs — you recover quickly from losses.

Key metrics from this panel: Max drawdown (deepest trough — mine is -8.7%). Max underwater duration (longest time below previous peak — mine is 47 days). Average drawdown depth. These numbers matter because drawdown determines: (1) whether you psychologically survive to see the recovery, (2) whether your risk limits trigger forced liquidation, (3) how long your capital is trapped not compounding.

**[INFORMATION GAIN]** Drawdown duration is often a better predictor of strategy abandonment than drawdown depth. Professional teams can tolerate a sharp -15% drawdown that recovers in 2 weeks. They CANNOT tolerate a -5% drawdown that persists for 6 months, because it suggests the edge has structurally broken. Duration signals regime change; depth may be normal volatility.

The top-3 drawdown events are automatically annotated with dates and recovery times. This lets you correlate drawdowns with known market events (COVID crash, rate hikes, etc.) and understand whether the strategy fails systematically in certain conditions.

## 6. PANEL 3: ROLLING SHARPE (24:00–28:00)

The middle-left panel shows the 126-day (6-month) rolling Sharpe ratio over time. This is the stability diagnostic.

A stable strategy shows a rolling Sharpe that fluctuates around a consistent positive level. An unstable strategy shows a rolling Sharpe that crosses zero frequently, has long negative stretches, or shows a downward trend.

My interpretation guide: Rolling Sharpe consistently > 0.5 = robust edge. Rolling Sharpe oscillating between -0.5 and 1.5 = edge exists but inconsistent, likely regime-dependent. Rolling Sharpe trending downward = alpha decay, need to investigate drift. Rolling Sharpe negative for 3+ months = strategy may be broken.

**[INFORMATION GAIN]** I compare 3-month and 12-month rolling Sharpe windows. If the 3-month Sharpe is negative but the 12-month is positive, the strategy is in a temporary drawdown within a longer positive trend — probably fine. If both are negative, the edge may have disappeared. This dual-window approach prevents overreacting to short-term noise while catching genuine deterioration.

## 7. PANEL 4: MONTHLY RETURNS HEATMAP (28:00–32:00)

The middle-right panel shows a heatmap with months as columns (Jan-Dec) and years as rows. Each cell is colored by monthly return: green for positive, red for negative, intensity proportional to magnitude.

This panel reveals: seasonal patterns (does the strategy underperform in September?), clustering of losses (are bad months adjacent, suggesting regime-driven failure?), consistency (are the greens evenly spread or concentrated in a few months?).

My pipeline: the heatmap shows no strong seasonal pattern, which is good. Losses are scattered rather than clustered. The worst month was -6.2% (March 2020, COVID crash). The best month was +8.3%. Most months are within -2% to +3%.

**[INFORMATION GAIN]** Heatmaps reveal risk concentration in time better than any summary statistic. A strategy that returns 12% annually might have earned all of it in January-March and been flat for 9 months. That is effectively a seasonal bet, not a year-round alpha. The heatmap makes this immediately obvious while averages hide it.

## 8. PANEL 5: DAILY RETURN DISTRIBUTION (32:00–36:00)

The bottom-left panel shows a histogram of daily returns overlaid with a fitted normal distribution curve. This reveals the tail behavior of your strategy.

Key questions: are returns approximately normal (the bell curve fits) or do they have fat tails (more extreme events than normal predicts)? Is there negative skew (more large losses than large gains)? What is the kurtosis (how peaked and heavy-tailed)?

My pipeline: returns show mild negative skew (-0.3) and excess kurtosis (4.2 vs normal's 3.0). The excess kurtosis means extreme days occur more often than a normal distribution predicts. This matters for risk management: VaR estimates based on normality underestimate tail risk.

## 9. PANEL 6: KEY METRICS TABLE (36:00–38:00)

The bottom-right panel is a clean table with all computed statistics: total return, CAGR, annualized volatility, Sharpe, Sortino, Calmar, max drawdown, underwater days, win rate, profit factor, daily turnover, total cost drag, skewness, kurtosis, alpha versus benchmark, information ratio.

Each metric answers a specific question. Sharpe: return per unit of total risk. Sortino: return per unit of downside risk (more relevant for asymmetric returns). Calmar: return per unit of maximum drawdown (how much pain per unit of gain). Information ratio: alpha per unit of tracking error (outperformance consistency versus benchmark).

**[INFORMATION GAIN]** The single most underrated metric on the tearsheet is cost drag — the annualized reduction in return from transaction costs. If your CAGR is 12% gross and 10% net, the cost drag is 2%. If turnover increases by 50%, cost drag increases proportionally. This is the metric that connects the backtesting world to the real execution world.

## 10. THE CLOSE (38:00–40:00)

A professional tearsheet transforms your backtest from an optimistic equity curve into an honest, multi-dimensional risk assessment. The 6 panels together tell the full story: how the strategy performed, how risky the ride was, whether the edge is stable or decaying, and whether costs are manageable.

Next video: experiment tracking. After 200+ model runs, you need a system to log every configuration, every result, and every insight — so you can reproduce any experiment and build on your best ideas systematically.

[NEEDS MORE] Your actual tearsheet screenshot. Three annotated drawdown events with explanations. Gross vs net return attribution from your live pipeline.
