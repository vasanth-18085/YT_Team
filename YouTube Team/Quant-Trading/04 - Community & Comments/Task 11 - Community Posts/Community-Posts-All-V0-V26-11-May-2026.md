# MLQuant — Community Posts
## Season 1: Pre-Launch + All 27 Videos

**Created:** 2026-05-11
**Replaces:** Community Posts — 10 April 2026.md (old Quant_System content)
**Platform:** YouTube Community Tab
**Tone:** Honest, curious, self-aware. Not hype. Not guru. "I'm figuring this out too."

---

## Pre-Launch Posts (Nov–Dec 2026)

### Pre-Launch Post 1 — Channel Announcement
*Publish: Week of V0 recording, before launch*

> Starting something I've been thinking about for a while.
>
> I'm an ML/AI engineer and I've been self-studying quant finance for the past few months. The plan: build 7 real quant ML projects from scratch, document the whole thing, put it all on YouTube for free.
>
> Not a guru channel. Not a course in disguise. Just me building real systems and showing what actually happens — including the parts that don't work.
>
> Channel drops next month. If you're an ML/SWE person curious about quant finance, this might be for you.
>
> What do you want to see first?
> 🅐 How I get NSE stock data for free
> 🅑 Why most backtests are secretly wrong
> 🅒 How hedge funds actually pick stocks (it's not charts)

---

### Pre-Launch Post 2 — The Plan
*Publish: 1 week before V0 drop*

> Here's the full plan for Season 1.
>
> 7 projects. 27 videos. All free.
>
> P1 — Market Data & Risk Engine (the data foundation)
> P2 — Event-Driven Backtesting (the testing framework)
> P3 — Factor Alpha Engine (how hedge funds rank stocks)
> P4 — Volatility & Options Lab (GARCH, Black-Scholes, IV surface)
> P5 — ML Alpha Research Lab (LightGBM on NIFTY 200)
> P6 — Portfolio Optimizer (Markowitz, HRP, Black-Litterman)
> P7 — Multi-Strategy Arena (everything combined)
>
> Season 2: The Quant Agent. But that's 2+ years away.
>
> First video drops this week. Drop a 🔥 if you're in.

---

## Video Community Posts

### V0 — Series Trailer
*Post same day as publish*

> The trailer is live.
>
> 3-year plan. 7 projects. 26 episodes. Here's why I'm doing this publicly instead of just studying quietly.
>
> Link in the description. Drop a comment if you're on a similar path — software engineer, ML person, or just someone who found quant finance and doesn't know where to start.

---

### V1 — NSE Data Pipeline

> P1 is here.
>
> Before any model, any backtest, any alpha signal — there's data. And most "quant trading" tutorials skip this completely.
>
> This video: how to get NSE stock data for free, handle corporate actions correctly, and build the foundation every quant system needs.
>
> The code is on GitHub (link in description). Let me know what I missed.

---

### V2 — Risk Metrics

> Second video of P1.
>
> Quick question: what's the difference between VaR and CVaR? If you can't answer that in under 30 seconds, this video is for you.
>
> Sharpe. Sortino. Max Drawdown. VaR. CVaR. All implemented from scratch in Python — no QuantStats, no pyfolio.
>
> Because if you don't know what's inside the function, you don't really know the risk.

---

### V3 — Risk Dashboard

> P1 Part 3.
>
> Code that outputs numbers is fine. A dashboard you can actually look at is better.
>
> This one builds the monitoring system: rolling Sharpe, drawdown charts, benchmark vs portfolio. The kind of thing a PM would look at every morning.
>
> P1 complete demo drops next. All the pieces running together for the first time.

---

### V4 — P1 Complete Demo

> P1 is done.
>
> Market data pipeline, corporate action adjustments, SQLite storage, risk metrics, rolling analytics, benchmark comparison — all built from scratch, all running together.
>
> The demo is in the video. Bloomberg charges ₹24,000/year for this. Mine cost ₹0.
>
> P2 is next: the backtesting engine. This is where I get to show you exactly how backtests lie.

---

### V5 — Why Backtests Lie

> This is probably the most important video in Season 1.
>
> I broke my own backtest on purpose. Five different ways. Lookahead bias, survivorship bias, transaction cost blindness, overfitting, selection bias.
>
> Every "amazing" backtest I've ever seen on YouTube fails at least one of these tests.
>
> The good news: once you know what to look for, they're not hard to catch. Video is live.

---

### V6 — Backtesting Engine

> P2 Part 2.
>
> No Backtrader. No Zipline. Built from scratch.
>
> DataHandler → Strategy → Portfolio → ExecutionHandler. Four components, one event loop. The architecture that makes lookahead bias impossible by design.
>
> This one's longer than usual because I wanted to actually show the architecture decisions, not just the final code. The GitHub link is in the description.

---

### V7 — Walk-Forward Validation

> P2 is complete.
>
> I put walk-forward validation on the backtesting engine. Expanding window, rolling window, backtest integrity report.
>
> The honest result: my momentum strategy looked incredible in-sample. Walk-forward cut the Sharpe in half.
>
> That's a good result actually. Better to find out here than with real money.
>
> P3 is next: how hedge funds actually pick stocks.

---

### V8 — How Hedge Funds Pick Stocks

> Most people think hedge funds use complex technical analysis or secret indicators.
>
> They don't.
>
> They use factors. Mathematical scores that rank stocks based on momentum, value, quality, and volatility characteristics. Fama and French got a Nobel Prize for proving these work.
>
> This video: the theory. Next video: I build it for NIFTY 200.

---

### V9 — Building Factor Signals

> P3 Part 2.
>
> Built 4 factor signals this week:
> — Momentum (12M-1M return)
> — Value (Earnings/Price)
> — Quality (ROE composite)
> — Low-Vol (trailing standard deviation)
>
> Cross-sectional z-score normalized, monthly rebalanced. 200 stocks. Code on GitHub.
>
> Next: does this actually work? IC, quintile spreads, and the full evaluation.

---

### V10 — Factor Evaluation

> P3 is done.
>
> The evaluation is in. IC for the momentum factor: 0.06 over 10 years. For reference, anything above 0.05 is considered a real signal in industry.
>
> Quintile spreads are monotonic. Factor decay is significant after 2 months.
>
> Honest verdict: the factors work on NIFTY 200. They're not as clean as US data. That's expected and actually more interesting.
>
> P4 next: volatility and options.

---

### V11 — GARCH

> P4 starts with volatility.
>
> Markets aren't uniformly volatile. Calm periods are followed by storms, storms return to calm. GARCH models this directly — today's volatility predicts tomorrow's.
>
> Implemented GARCH(1,1) from scratch this week. 30-day forecasts, compared to realized vol. The model actually captures the COVID spike shape.
>
> Black-Scholes is next. Building the options pricer from the formula up.

---

### V12 — Black-Scholes

> Had to implement Black-Scholes from scratch. No scipy.stats.norm. No QuantLib.
>
> Just the formula, the derivation, and all 5 Greeks implemented analytically.
>
> There's a moment when put-call parity holds to 6 decimal places in your own code and you realize the math is actually right. That's a good moment.
>
> IV surface is next — where it gets more interesting.

---

### V13 — IV Surface

> P4 Part 3.
>
> NSE options chain data → implied vol for each strike/expiry combination → 3D surface.
>
> The vol smile is real. OTM puts are systematically more expensive than Black-Scholes predicts. The market knows something Black-Scholes doesn't (fat tails).
>
> Last video of P4 drops next: is there a systematic edge in selling options when IV > realized vol?

---

### V14 — Vol Risk Premium

> P4 is complete.
>
> The data says: on NSE, implied vol has been systematically higher than realized vol about 68% of the time over the last 5 years.
>
> That sounds like an edge. It might be. It comes with risks (tail events can wipe you if you're naked short). This video shows the data, the backtest, and the honest caveats.
>
> P5 is next: the ML alpha research lab. LightGBM on 200 stocks.

---

### V15 — Feature Engineering

> P5 starts.
>
> Built 50+ features this week: momentum at multiple lookbacks, volume ratios, volatility of volatility, fundamental ratios from screener.in, microstructure proxies.
>
> Roughly 30% of them survive the IC test.
>
> What kills most features: they only work in one regime. Bull market features die in bear markets. The ones that survive are more boring than you'd expect.
>
> Next: why standard cross-validation will destroy your model.

---

### V16 — Purged CV

> This video might save you from a costly mistake.
>
> Standard k-fold cross-validation lets your model see the future during training. In finance, that's catastrophic. Your validation score is a lie.
>
> Purged k-fold adds an embargo period. It's a few extra lines of code. It completely changes your results.
>
> If you're doing any kind of ML on time series data, watch this one.

---

### V17 — LightGBM Results

> LightGBM on NIFTY 200. 5 years of data. 50+ features. Purged CV.
>
> Honest results:
> IC: 0.072 (good — above industry threshold of 0.05)
> Top quintile beats bottom quintile: yes, monotonically
> Out-of-sample: holds, but noisier than in-sample
>
> SHAP shows momentum features dominate. The model is mostly a fancy momentum signal. That's actually useful information.
>
> Full code on GitHub.

---

### V18 — Alpha Evaluation

> P5 Part 4.
>
> Quick check: are you evaluating your stock model with accuracy or R²?
>
> If yes — stop. Those metrics don't tell you if you'll make money.
>
> IC does. Quintile spreads do. Factor neutralization does.
>
> This video: the full quant evaluation stack for ML alpha signals. How to know if your signal is real before you bet on it.

---

### V19 — Overfitting Audit

> P5 is complete.
>
> Ran the overfitting audit on my LightGBM model:
> — Permutation test: shuffled labels, retrained. IC dropped to near zero. ✓ (signal is real, not accidental)
> — Stability: top features consistent across time periods. ✓
> — Deflated Sharpe: passes. ✓
>
> The model is real. Or at least, as real as you can prove before trading it.
>
> P6 is next: portfolio construction. The other half of the problem.

---

### V20 — Markowitz Fails

> Harry Markowitz won the Nobel Prize in Economics in 1990.
>
> His mean-variance optimization is theoretically elegant and practically unusable.
>
> Reason: tiny changes in expected returns cause huge swings in portfolio weights. The optimizer is error-maximizing, not error-minimizing.
>
> This video shows the math of why, and tests it on real NSE data. The results are exactly as ugly as you'd expect.

---

### V21 — HRP + BL + Risk Parity

> P6 Part 2.
>
> Three methods that actually work:
>
> — Risk Parity: equal risk contribution from each asset
> — Black-Litterman: combine market equilibrium with your factor views
> — Hierarchical Risk Parity (De Prado): cluster-based allocation, no matrix inversion
>
> All three implemented from scratch. Code on GitHub.
>
> Head-to-head comparison is next. Who wins on real NSE data?

---

### V22 — 4 Methods Head-to-Head

> P6 is done.
>
> 4 portfolio methods, 10 years of NSE data, walk-forward testing with real constraints.
>
> Results (Sharpe, out-of-sample):
> — Equal Weight: 0.61
> — Markowitz: 0.47 (yes, worse)
> — Risk Parity: 0.68
> — HRP: 0.72
> — Black-Litterman: 0.65
>
> HRP wins. Equal weight beats Markowitz. The Nobel Prize method finished last.
>
> P7 is the capstone. Everything comes together here.

---

### V23 — Strategy Ensemble

> P7 starts.
>
> This is where everything from P1–P6 gets combined into one system.
>
> Factor signals, ML alpha, vol signals, portfolio construction, risk monitoring — all feeding into a single decision framework.
>
> The hard part isn't the individual pieces. It's making them talk to each other consistently.
>
> This video: the architecture. Next: how the system handles different market regimes.

---

### V24 — Regime Detection

> P7 Part 2.
>
> The same strategy shouldn't behave the same way in a bull market and a crash. Most systems ignore this.
>
> Added Hidden Markov Model regime detection. Three states: trending bull, ranging, high-vol/bear.
>
> In high-vol regime: reduce position sizing, widen stops, increase cash allocation.
> In trending bull: let the momentum factors run.
>
> The system now knows when to be aggressive and when not to be.

---

### V25 — System Live

> It's live.
>
> Not live trading. Paper trading. But the dashboard is running, the system is making decisions every day on NSE data, and everything is logged.
>
> 2 years of study and building leading to this moment. It's not perfect. It's real.
>
> The video is a full demo walkthrough. Season finale is next.

---

### V26 — Season 1 Finale

> Season 1 is complete.
>
> 27 videos. 7 projects. 2 years.
>
> What I learned that no textbook tells you:
> — Data is 80% of the work
> — Backtests are optimistic by design
> — IC of 0.07 is genuinely good
> — Markowitz really does underperform equal weight
> — The system works, but it's not magic
>
> Season 2 will be the Quant Agent. 10-layer autonomous system. That's a different kind of project.
>
> For now: thank you for watching. Drop a comment on what helped most.

---

## Engagement Post Templates (Between Videos)

### Study Check-In (monthly)
> Month [X] update.
>
> Currently studying: [CPF module / MScFE course]
> DSA problems this month: [X]
> Project status: [which P is in progress]
>
> Hardest concept this month: [honest answer]
>
> Where are you in your quant learning path right now?

### Question Post (every 2–3 videos)
> Quick question for the channel:
>
> When you're learning a new quant concept, do you:
> 🅐 Study the theory first, then implement
> 🅑 Start coding immediately, figure it out as you go
> 🅒 Read one reference, then implement + debug your way to understanding
>
> Asking because I keep flip-flopping between B and C and I'm not sure which is actually faster.

### Honest Failure Post (when relevant)
> Tried to implement [X] this week.
>
> It didn't work the way I expected. Here's what actually happened: [brief honest description]
>
> I fixed it by [solution], but it took [time] longer than it should have.
>
> This is the part nobody puts in their tutorials. Sharing it anyway.
