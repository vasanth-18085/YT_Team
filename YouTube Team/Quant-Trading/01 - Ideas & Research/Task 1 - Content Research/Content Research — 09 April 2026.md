# Content Research — MLQuant
## Task 1 — 09 April 2026

> **Channel:** MLQuant
> **Series Title:** ML Trading Systems from Scratch
> **Total Videos:** 26 (1 trailer + 25 main)
> **Avg Length:** ~30 min per video
> **Total Course Time:** ~12.5 hours
> **Status:** APPROVED
> **Source Repo:** /Users/vasanth-18085/Projects/Quant_System (44 ML models, 10 phases, 58 Python files, 10 notebooks)

---

## Market Research Summary

### Proven Demand (view counts from comparable videos)
| Topic | Views | Channel |
|-------|-------|---------|
| "Algorithmic Trading with ML" (3hr course) | 1.4M | freeCodeCamp |
| "Build a Python Trading Bot" | 71.8K | Ryan O'Connell |
| "22-Hour Algo Trading Free Course" | 58.2K | Kuldeep Singh |
| "ML Trading Indicator" (classifier) | 48.2K | CodeTrading |
| "Build a Trading Bot" (OANDA API) | 50.6K | Trading Steady |

### Competitive Gap (topics with near-zero YouTube coverage)
| Topic | Current Coverage | Opportunity |
|-------|-----------------|-------------|
| Triple-barrier labeling (López de Prado) | Almost zero | HUGE |
| Walk-forward validation with purge + embargo | Near zero | HUGE |
| LoRA fine-tuning FinBERT for trading sentiment | Zero | HIGH |
| End-to-end ML trading system (10 phases) | Zero at this scale | MASSIVE |
| GARCH + ML hybrid volatility | Near zero | HIGH |
| Black-Litterman with ML views | Near zero | HIGH |
| Almgren-Chriss market impact modeling | Near zero | HIGH |
| Meta-labeling (9 classifiers) | Near zero | HIGH |

### CPM Estimate
- Indian viewers: $1-5 CPM
- US/UK/EU viewers: $15-30 CPM
- Blended estimate (English, global ML/QF niche): $5-12 CPM
- Finance/tech is one of the highest CPM niches on YouTube

### Competitor Landscape (25 channels mapped)
- **Part Time Larry** — Python algo, practical, no ML depth
- **Algovibes** — myth-busting backtests, Python, no end-to-end systems
- **Coding Jesus** — live coding, broad coverage, not ML+QF focused
- **Sentdex** — approachable ML, not QF-focused
- **QuantPy** — theoretical (options, market making), not hands-on
- **The Python Quants** — academic heavy, derivatives focused
- **Kuldeep Singh Rathore** — traditional algo, not ML-research focused
- **Nobody combines ML + QF at the depth of your system**

---

## Video Length Strategy

**30 minutes per video.** Rationale:
- Mid-roll ads at 8+ min → 30 min = 3-4 ad slots per video
- freeCodeCamp proved long-form finance/coding works (1.4M views on 3hr)
- Individual searchable videos > one monolith (more total views)
- 30 min × 25 = 12.5 hour free course (the forever USP)
- Each video stands alone AND works as a binge-able series

---

## Release Strategy

| Phase | Videos | Cadence |
|-------|--------|---------|
| Pre-launch | Trailer (Video 0) | Post alone, build anticipation 3-5 days |
| Launch week | Videos 1-2 | Back-to-back, 2-3 days apart |
| Weeks 2-3 | Videos 3-4 | Completes the hook (Act 1) |
| Ongoing | Videos 5-25 | 1-2 per week depending on schedule |
| Full series | ~3-4 months from launch | 12.5hr free course complete |

---

## FULL VIDEO PLAN (26 Videos)

---

### VIDEO 0 — SERIES TRAILER (2-3 min)

**Title:** "I'm Releasing a Free 12-Hour Course on ML Trading Systems — Here's What's Inside"

**Content:**
- Quick montage: code running, backtest equity curves, architecture diagrams, model comparisons
- Key line: "44 ML models, 10 phases, from raw data to production deployment. All free. All code on GitHub."
- Show the series roadmap visually
- CTA: Subscribe + turn on notifications

**Purpose:** Build anticipation. Post 3-5 days before Video 1.

**Repo source:** Highlights from all notebooks, `GUIDE.md` architecture diagrams

---

### ACT 1: THE HOOK (Videos 1-4) — Wide Audience Pull

---

### VIDEO 1 — "I Built a Complete ML Trading System — Full Architecture Reveal"

**Content:**
- Walk through all 10 phases of Quant_System at high level
- Show the end result first: equity curves, model comparison tables, Sharpe ratios
- Architecture overview: data → features → forecasting → signals → sentiment → fusion → risk → strategy → backtest → production
- Don't teach implementation yet — reveal what exists. "I built this, and over the next 24 videos I'll show you exactly how."
- Show code structure briefly (58 files, 10 notebooks)
- End with GitHub link: "All of this code is free."

**Hook angle:** "This is what a real ML trading system looks like — not a Jupyter notebook, not LSTM stock prediction."

**Repo source:**
- `GUIDE.md` (full architecture overview)
- `src/orchestrator.py` (pipeline flow)
- All 10 `notebooks/` (quick walkthrough)
- Results from `results/ablation/` and `results/backtest/`

**Search terms:** ML trading system, algorithmic trading python, quant trading system architecture

---

### VIDEO 2 — "Why 90% of ML Backtests Are Lies (and How to Fix Yours)"

**Content:**
- The problem: most backtests have lookahead bias → inflated returns → false confidence
- Show a standard backtest (looks great) vs walk-forward with purge+embargo (realistic results)
- Explain: what is walk-forward validation, why purge, why embargo
- Live code walkthrough of `purged_cv.py`
- Show ablation framework: how to systematically compare model performance
- "If you've ever backtested an ML model on stock data and got amazing results — you probably cheated without knowing it."

**Hook angle:** Contrarian myth-buster. Every ML trader has been burned by this.

**Repo source:**
- `src/m7_validation/purged_cv.py`
- `src/ablation.py`
- `notebooks/07_production_hardening.ipynb`

**Search terms:** backtesting python, walk forward validation, lookahead bias trading, why backtests fail

---

### VIDEO 3 — "Triple-Barrier Labeling — The Signal Method Quant Funds Actually Use"

**Content:**
- The problem with standard labels: "stock went up" / "stock went down" is useless for trading
- What triple-barrier labeling is (López de Prado's method): profit target, stop loss, time horizon
- Why it produces BETTER trading signals than simple direction labels
- Full implementation walkthrough with your code
- How triple-barrier feeds into meta-labeling (teaser for Video 10)
- Show real labeled data, distribution of signals

**Hook angle:** Industry-standard technique that's referenced everywhere (quant Twitter, AFML book) but NOBODY has a good YouTube explainer with working code.

**Repo source:**
- `src/m2_signals/triple_barrier.py`
- `src/m2_signals/meta_label.py` (preview)
- `notebooks/02_triple_barrier_signals.ipynb`

**Search terms:** triple barrier labeling, trading signals python, López de Prado, meta labeling

---

### VIDEO 4 — "I Fine-Tuned FinBERT with LoRA for Stock Sentiment — Here's What Happened"

**Content:**
- The premise: can fine-tuning a financial language model improve trading signals?
- Brief intro to FinBERT (pre-trained financial NLP) and LoRA (parameter-efficient fine-tuning)
- Fine-tune FinBERT with LoRA on financial news data (show the process)
- Evaluate: sentiment accuracy comparison across all 5 fine-tuned models
- The honest answer: did it actually help trading signals? Show real impact metrics.
- "Here's what worked, here's what didn't, and here's why."

**Hook angle:** Hottest AI topic (LoRA/LLMs) applied to finance. "Did it actually work?" framing = honest + compelling.

**Repo source:**
- `src/m3_sentiment/models.py`
- `src/m3_sentiment/fine_tune.py`
- `src/m3_sentiment/impact.py`
- `notebooks/03_sentiment_analysis.ipynb`

**Search terms:** FinBERT, LoRA fine-tuning, NLP for trading, sentiment analysis stocks, LLM finance

---

### ACT 2: THE FOUNDATION (Videos 5-9) — Building From Scratch

---

### VIDEO 5 — "Building the Data Pipeline — Yahoo Finance to Feature-Ready DataFrames"

**Content:**
- Data ingestion: Yahoo Finance API for OHLCV data
- Multi-ticker handling: S&P 100 (101 tickers) + Nifty 50 (50 tickers)
- Parquet caching for speed (why not CSV)
- Data quality: handling missing values, splits, dividends
- Configuration management with YAML
- "This is the boring-but-essential foundation. Every model we build depends on this."

**Repo source:**
- `src/data_pipeline.py`
- `config.yaml`
- `config/universes/sp100.csv`, `config/universes/nifty50.csv`
- `notebooks/00_data_pipeline.ipynb`

**Search terms:** python trading data pipeline, yahoo finance python, stock data parquet

---

### VIDEO 6 — "45 Trading Features in Python — The Feature Engineering Bible"

**Content:**
- Complete feature engineering walkthrough: 45+ features across 4 groups
- Group 1: Technical indicators (RSI, MACD, Bollinger, ATR, ADX, CCI, Stochastic, OBV, Ichimoku)
- Group 2: Rolling statistics (lagged returns, rolling volatility, rolling momentum)
- Group 3: Calendar features (day of week, month, quarter, month start/end)
- Group 4: Price structure (intraday range, candle body, shadows)
- For each: WHY it matters for ML (not just what it calculates)

**Repo source:**
- `src/features.py`
- `notebooks/00_data_pipeline.ipynb`

**Search terms:** feature engineering trading, technical indicators python, RSI MACD python, trading features ML

---

### VIDEO 7 — "14 Time-Series Models Compared — Which One Actually Predicts Stock Prices?"

**Content:**
- The big question: which forecasting model actually works for stocks?
- 14 models in 4 tiers: Statistical (ARIMA, Prophet), RNN (LSTM, GRU, TCN), MLP (DLinear, N-BEATS, N-HiTS, TiDE), Transformer (PatchTST, TFT, iTransformer, Chronos)
- Ablation study with walk-forward validation (not fake backtests)
- Real results table: MAE, RMSE, IC, Sharpe for each model
- Honest verdict: which ones are good, which ones suck, and why
- "Spoiler: the simplest models might surprise you."

**Repo source:**
- `src/m1_forecasting/models.py`
- `src/m1_forecasting/sequence.py`
- `notebooks/01_time_series_forecasting.ipynb`

**Search terms:** stock prediction ML, time series forecasting python, LSTM vs transformer stocks, best model stock prediction

---

### VIDEO 8 — "LSTM vs Transformer vs Foundation Model — The Forecasting Deep Dive"

**Content:**
- Deep dive into the neural architectures (Tier B + D from Video 7)
- LSTM & GRU: gates, memory cells, sequence handling, training tricks
- PatchTST, TFT, iTransformer: attention mechanisms, variable selection, how they differ
- Chronos: what a pre-trained foundation model brings to financial time series
- Architecture diagrams for each
- Head-to-head: training time, performance, stability
- When to use which (and when NOT to)

**Repo source:**
- `src/m1_forecasting/models.py` (Tier B + D classes)
- `src/m1_forecasting/sequence.py`
- `notebooks/01_time_series_forecasting.ipynb`

**Search terms:** LSTM stock prediction, transformer time series, TFT model, PatchTST, Chronos model

---

### VIDEO 9 — "DLinear, N-BEATS, N-HiTS, TiDE — Modern MLPs That Beat Transformers"

**Content:**
- The "sleeper" models: modern MLP architectures that often outperform transformers
- DLinear: trend + seasonality decomposition with linear layers
- N-BEATS: neural basis expansion analysis (interpretable!)
- N-HiTS: hierarchical interpolation variant
- TiDE: time series dense encoder
- Why simpler might be better for financial data
- Show ablation results: these models vs transformers head-to-head

**Repo source:**
- `src/m1_forecasting/models.py` (Tier C classes)
- `notebooks/01_time_series_forecasting.ipynb`

**Search terms:** N-BEATS, DLinear, time series MLP, NHiTS, TiDE model

---

### ACT 3: SIGNALS & INTELLIGENCE (Videos 10-14) — The Secret Sauce

---

### VIDEO 10 — "Meta-Labeling — Filtering Bad Trades with ML on Top of ML"

**Content:**
- Concept: your base model generates signals, meta-labeling decides which to KEEP
- 9 classifiers: LightGBM, XGBoost, CatBoost, RF, LSTM, CNN, TabNet, FT-Transformer, Stacking
- Why meta-labeling works: precision over recall, confidence gating
- Full implementation walkthrough
- Before/after: trading results with and without meta-label filter
- "This single technique can cut your losing trades in half."

**Repo source:**
- `src/m2_signals/meta_label.py`
- `notebooks/02_triple_barrier_signals.ipynb`

**Search terms:** meta labeling trading, filter bad trades ML, LightGBM trading, XGBoost trading signals

---

### VIDEO 11 — "VADER vs FinBERT vs RoBERTa vs DeBERTa — Sentiment Model Showdown"

**Content:**
- Head-to-head comparison: 6 sentiment models on financial news
- VADER (rule-based baseline) vs 5 fine-tuned transformers
- Evaluation: accuracy, precision, recall on financial sentiment
- Daily sentiment aggregation: how to turn per-article scores into daily trading features
- Which model best predicts next-day returns?
- Real impact on trading signals

**Repo source:**
- `src/m3_sentiment/models.py`
- `src/m3_sentiment/aggregator.py`
- `notebooks/03_sentiment_analysis.ipynb`

**Search terms:** sentiment analysis stocks, FinBERT vs VADER, NLP trading python, stock sentiment model

---

### VIDEO 12 — "How to Fine-Tune ANY Transformer for Finance with LoRA (Step by Step)"

**Content:**
- Generic LoRA fine-tuning recipe for financial NLP
- Step by step: model selection → LoRA config → data prep → training → evaluation
- Works on ANY HuggingFace model, not just FinBERT
- Low-GPU requirements (runs on free Colab)
- FNSPID financial sentiment labeling explained
- Production-ready: how to deploy a fine-tuned model

**Repo source:**
- `src/m3_sentiment/fine_tune.py`
- `src/m3_sentiment/fnspid_labeler.py`
- `notebooks/03_sentiment_analysis.ipynb`

**Search terms:** LoRA fine-tuning tutorial, fine-tune transformer finance, HuggingFace LoRA, FinBERT fine-tune

---

### VIDEO 13 — "Multi-Input Fusion — Combining Forecasts, Signals, and Sentiment into One Model"

**Content:**
- The problem: you have forecasts, signals, AND sentiment — how to combine them?
- 4 feature groups: (A) technical, (B) forecast outputs, (C) signal features, (D) sentiment
- 7 fusion architectures explained:
  - Tree-based: LightGBM Fusion, CatBoost Fusion, Stacking Fusion
  - Neural: MultiHeadMLP, MultiInputTCN, Gated Multimodal, CrossAttention
- Head-to-head results: which fusion method works best?
- Custom dataset builder for 4-group features

**Repo source:**
- `src/m4_returns/fusion.py`
- `src/m4_returns/dataset.py`
- `notebooks/04_returns_fusion.ipynb`

**Search terms:** multi-input ML, fusion model trading, ensemble trading strategies, multimodal ML finance

---

### VIDEO 14 — "Gated Multimodal Fusion vs Cross-Attention — Advanced Neural Trading Architectures"

**Content:**
- Deep dive into the two most interesting fusion architectures
- Gated Multimodal Unit (GMU): how per-modality gates work, when to use
- Cross-Attention Fusion: attention over feature-group embeddings, architecture details
- Code walkthrough: PyTorch implementation line by line
- When simple (LightGBM fusion) beats complex (CrossAttention), and why
- "Architecture innovation for trading — but does complexity help?"

**Repo source:**
- `src/m4_returns/fusion.py` (GMU + CrossAttention classes)
- `notebooks/04_returns_fusion.ipynb`

**Search terms:** attention mechanism trading, gated multimodal unit, cross-attention fusion, PyTorch trading model

---

### ACT 4: RISK & PORTFOLIO (Videos 15-18) — Where Theory Meets Money

---

### VIDEO 15 — "GARCH + ML — Predicting Volatility with Classical Finance Meets Machine Learning"

**Content:**
- Why volatility matters: position sizing, risk management, option pricing
- GARCH(p,q): the classical approach. Auto-select p,q by AIC.
- The hybrid: GARCH residuals + technical features → LightGBM
- LSTM volatility: sequence-to-volatility neural approach
- Compare all 3: which predicts realized volatility best?
- VaR and CVaR from GARCH predictions

**Repo source:**
- `src/m5_risk/volatility.py`
- `notebooks/05_risk_portfolio.ipynb`

**Search terms:** GARCH python, volatility prediction ML, GARCH vs LSTM, risk management trading python

---

### VIDEO 16 — "Markowitz, HRP, Black-Litterman, Risk Parity — ML-Powered Portfolio Optimization"

**Content:**
- 4 portfolio construction methods, each explained from scratch
- Markowitz: max-Sharpe via PyPortfolioOpt. Why it's fragile.
- HRP: clustering-based, no covariance inversion needed. More stable.
- Black-Litterman: uses YOUR ML predictions as Bayesian prior. The most advanced.
- Risk Parity: equal risk contribution. The default for many funds.
- Real allocations + Sharpe comparisons across all 4

**Repo source:**
- `src/m5_risk/portfolio.py`
- `notebooks/05_risk_portfolio.ipynb`

**Search terms:** portfolio optimization python, Markowitz python, Black-Litterman ML, HRP portfolio, risk parity

---

### VIDEO 17 — "From Predictions to Actual Trades — Signal Gating + Position Sizing"

**Content:**
- The bridge: how forecasts become real trading positions
- Signal gating: confidence thresholds, meta-label filtering
- Position sizing: volatility targeting, Kelly criterion framework
- The SignalCombiner class: how all components connect
- "Your model says BUY — but how much? And should you even trust it?"

**Repo source:**
- `src/m6_strategy/combiner.py`
- `notebooks/06_integrated_strategy.ipynb`

**Search terms:** position sizing python, Kelly criterion trading, signal gating ML, trading strategy python

---

### VIDEO 18 — "Backtesting with VectorBT — Running the Full ML Strategy End-to-End"

**Content:**
- First real "did this system make money?" video
- VectorBT integration: signals → portfolio → equity curve
- Add transaction costs, slippage
- Analyze tearsheets: Sharpe, max drawdown, win rate, profit factor
- Compare: ML system vs buy-and-hold SPY
- Honest results — show the warts

**Repo source:**
- `src/m6_strategy/backtest.py`
- `src/m8_backtest/engine.py`
- `notebooks/06_integrated_strategy.ipynb`

**Search terms:** vectorbt tutorial, backtesting python, ML trading backtest, algorithmic trading results

---

### ACT 5: PRODUCTION & REALITY (Videos 19-23) — What Nobody Shows

---

### VIDEO 19 — "Hidden Markov Models for Market Regime Detection — Bull, Bear, or Sideways?"

**Content:**
- Why regimes matter: your model trained in a bull market → fails in a crash
- HMM basics: hidden states, emission probabilities, Baum-Welch
- Implementation: detect bull/bear/sideways regimes automatically
- Show real regime switches on historical data (2015-2025)
- How the system adapts strategy to current regime

**Repo source:**
- `src/m7_risk/regime.py`
- `notebooks/07_production_hardening.ipynb`

**Search terms:** HMM finance, regime detection trading, Hidden Markov Model stocks, market regime python

---

### VIDEO 20 — "Why Your ML Model Silently Fails — Drift Detection & Monitoring"

**Content:**
- The silent killer: your model works great... until it doesn't
- Covariate drift: when feature distributions shift
- CUSUM filter: detecting structural changes in time series
- Statistical tests for detecting drift
- How to build a monitoring system that alerts you before it's too late
- "Most ML traders don't know their model stopped working 3 months ago."

**Repo source:**
- `src/m7_validation/drift_monitor.py`
- `src/m7_validation/statistical_tests.py`
- `notebooks/07_production_hardening.ipynb`

**Search terms:** ML model drift, CUSUM filter, model monitoring trading, concept drift finance

---

### VIDEO 21 — "Almgren-Chriss Market Impact — Why Your Backtest Profits Disappear in Real Trading"

**Content:**
- The gap between backtest and reality: transaction costs eat your alpha
- Almgren-Chriss model: permanent vs temporary market impact
- Slippage modeling: what actually happens when you execute
- Show: a strategy that looks profitable → add realistic costs → watch profits shrink
- "This is why most retail algo traders lose money despite 'profitable' backtests."

**Repo source:**
- `src/m7_execution/costs.py`
- `notebooks/07_production_hardening.ipynb`

**Search terms:** market impact model, transaction costs trading, Almgren-Chriss, slippage trading python

---

### VIDEO 22 — "Fantasy Backtest vs Reality — Running ML Trading with Real-World Costs"

**Content:**
- LiveBacktester: the realistic version
- Side-by-side: standard backtest vs backtest with costs, slippage, leverage constraints
- Show the gap in Sharpe, drawdown, returns
- The psychology: how to set realistic expectations
- Tearsheet analysis: what to actually look at

**Repo source:**
- `src/m8_backtest/engine.py`
- `src/m8_backtest/tearsheet.py`
- `notebooks/08_real_backtest_paper_trade.ipynb`

**Search terms:** realistic backtesting, backtest with slippage, trading costs python, algo trading reality

---

### VIDEO 23 — "Cross-Sectional Alpha — Building a Long-Short Factor Strategy with ML"

**Content:**
- Factor investing: a different approach (cross-sectional, not time-series)
- 5-factor model implementation
- Quintile backtests: long top quintile, short bottom quintile
- Portfolio construction for long-short
- How ML predictions become alpha factors
- Results: does the ML alpha factor add value over traditional factors?

**Repo source:**
- `src/m8_alpha/` (cross-sectional alpha module)
- `notebooks/08_real_backtest_paper_trade.ipynb`

**Search terms:** factor investing python, long-short strategy, cross-sectional alpha ML, quant factor model

---

### ACT 6: PUTTING IT ALL TOGETHER (Videos 24-25) — Grand Finale

---

### VIDEO 24 — "Experiment Tracking & Reproducible Quant Research — MLOps for Trading"

**Content:**
- Why reproducibility matters in quant: P-hacking, overfitting, selection bias
- JSONL experiment logging: track every run, every parameter, every result
- Journal export: how to build a research journal from experiments
- Comparing runs: how to know if a new model actually improved things
- "The discipline that separates hobbyists from real quant researchers."

**Repo source:**
- `src/m9_experiment/tracker.py`
- `notebooks/09_universe_experiments.ipynb`

**Search terms:** MLOps trading, experiment tracking python, reproducible ML, quant research workflow

---

### VIDEO 25 — "The Full System — S&P 100 + Nifty 50, 44 Models, Final Results"

**Content:**
- The grand finale: run EVERYTHING end-to-end
- Multi-universe: US (S&P 100) + India (Nifty 50) — international markets
- Final equity curves, Sharpe ratios, max drawdowns
- Which models contributed most? Which phases mattered?
- Honest verdict: what worked, what didn't, what would I do differently
- "Here's the full 12.5-hour journey in one final video. All code is on GitHub."
- Tease: what's next for MLQuant

**Repo source:**
- Full system run across all modules
- `notebooks/09_universe_experiments.ipynb`
- All results from `results/`

**Search terms:** ML trading system results, algorithmic trading full system, quant trading python complete, S&P 100 ML

---

## Video-to-Repo File Mapping (Quick Reference)

| Video | Key Repo Files |
|-------|---------------|
| 0 (Trailer) | Highlights from all notebooks |
| 1 (Architecture) | `GUIDE.md`, `orchestrator.py`, all `notebooks/` |
| 2 (Backtests) | `purged_cv.py`, `ablation.py`, `notebooks/07` |
| 3 (Triple Barrier) | `triple_barrier.py`, `meta_label.py`, `notebooks/02` |
| 4 (FinBERT LoRA) | `m3_sentiment/models.py`, `fine_tune.py`, `notebooks/03` |
| 5 (Data Pipeline) | `data_pipeline.py`, `config.yaml`, `notebooks/00` |
| 6 (Features) | `features.py`, `notebooks/00` |
| 7 (14 Models) | `m1_forecasting/models.py`, `sequence.py`, `notebooks/01` |
| 8 (LSTM vs Transformer) | `m1_forecasting/models.py` (Tier B+D), `notebooks/01` |
| 9 (Modern MLPs) | `m1_forecasting/models.py` (Tier C), `notebooks/01` |
| 10 (Meta-Labeling) | `meta_label.py`, `notebooks/02` |
| 11 (Sentiment Showdown) | `m3_sentiment/models.py`, `aggregator.py`, `notebooks/03` |
| 12 (LoRA Tutorial) | `fine_tune.py`, `fnspid_labeler.py`, `notebooks/03` |
| 13 (Fusion) | `m4_returns/fusion.py`, `dataset.py`, `notebooks/04` |
| 14 (GMU vs CrossAttn) | `m4_returns/fusion.py` (neural), `notebooks/04` |
| 15 (GARCH + ML) | `m5_risk/volatility.py`, `notebooks/05` |
| 16 (Portfolio) | `m5_risk/portfolio.py`, `notebooks/05` |
| 17 (Signal Gating) | `m6_strategy/combiner.py`, `notebooks/06` |
| 18 (VectorBT) | `m6_strategy/backtest.py`, `m8_backtest/engine.py`, `notebooks/06` |
| 19 (HMM Regimes) | `m7_risk/regime.py`, `notebooks/07` |
| 20 (Drift) | `drift_monitor.py`, `statistical_tests.py`, `notebooks/07` |
| 21 (Market Impact) | `m7_execution/costs.py`, `notebooks/07` |
| 22 (Realistic Backtest) | `m8_backtest/engine.py`, `tearsheet.py`, `notebooks/08` |
| 23 (Alpha) | `m8_alpha/`, `notebooks/08` |
| 24 (MLOps) | `m9_experiment/tracker.py`, `notebooks/09` |
| 25 (Final Results) | Full system, `notebooks/09`, `results/` |
