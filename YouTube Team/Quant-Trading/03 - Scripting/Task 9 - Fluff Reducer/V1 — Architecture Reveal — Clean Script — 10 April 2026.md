# V1 — Architecture Reveal — Clean Script

**Title:** I Built a 44-Model Trading System (Full Architecture)
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–1:00)

This is what a real ML trading system looks like.

Not a Jupyter notebook with an LSTM predicting prices. Not a single model backtested on two years of cherry-picked data. This is 44 machine learning models across 10 phases, chained together into a pipeline that goes from raw Yahoo Finance OHLCV data all the way to paper-traded portfolio returns.

[INFORMATION GAIN] On screen right now: the equity curve from the full system compared against SPY buy-and-hold. The ablation table where all 14 forecasting models were benchmarked head-to-head under identical conditions. And the GitHub repo — 58 Python files, 10 notebooks, fully documented and public.

Over the next 24 videos I build every single piece from scratch. Today — the full architecture so you know where we are going and why it is designed the way it is.

---

## SECTION 2 — WHY A PIPELINE, NOT A MODEL (1:00–3:00)

The most common mistake when building ML trading systems is trying to find the one model that works. There is no one model that works.

[INFORMATION GAIN] Professional quant funds do not use a single model. They use a pipeline. Data engineers clean and normalise data. Researchers build prediction models. Risk managers size positions. Execution teams minimise market impact. Monitoring teams track drift. This repo mirrors that structure in code.

The key design principle is modularity. Each phase has a well-defined interface. Each model follows the same contract. I can swap any model in or out — run an ablation study, compare 14 forecasters — without touching any other part of the system.

Here is the contract every single model in this system implements:

```python
class ModelWrapper(ABC):
    name: str = "BaseModel"

    def fit(self, X_train, y_train):
        ...

    def predict(self, X_test) -> np.ndarray:
        ...

    def get_params(self) -> dict:
        ...

    def feature_importance(self):
        ...
```

[INFORMATION GAIN] Because every model follows this exact shape, the same ablation runner can benchmark ARIMA, LightGBM, LSTM, and transformers under identical walk-forward validation rules. ARIMA and a cross-attention transformer look exactly the same to the runner. That is the point of the contract.

---

## SECTION 3 — THE 10-PHASE WALKTHROUGH (3:00–24:00)

### Phase 0 — Data Pipeline (3:00–5:00)

Source files: `src/data_pipeline.py`, `src/features.py`, `config.yaml`

The `YahooLoader` class downloads OHLCV from Yahoo Finance and caches locally as Parquet files. Parquet is three to five times smaller than CSV on disk and ten times faster to read back. When you run hundreds of experiments and reload data every run, that speed difference compounds.

The `FeatureEngineer` class transforms raw OHLCV into 45 features across four groups.

Technical indicators: RSI at periods 7, 14, and 21. MACD with 12-26-9 configuration. Bollinger Bands at 20 periods. ATR, ADX, CCI, Stochastic, Williams percent R. On-Balance Volume. Full Ichimoku cloud with all five components.

Rolling statistics: lagged returns at 1, 5, 10, and 21 days. Rolling volatility at 5, 10, 21, and 63-day lookbacks. Rolling momentum at the same intervals.

Calendar features: day of week, month, quarter, month-start and month-end flags.

Price structure: intraday range, candle body ratio, upper and lower shadow ratios.

[INFORMATION GAIN] The naming convention is `{indicator}_{params}_{timeframe}` — for example `rsi_14_1d`. Forward-compatible with multi-timeframe stacking if you decide to extend the system later. Everything is controlled by `config.yaml`. RSI periods, MACD windows, volatility lookbacks — change the config, the pipeline adapts. No hardcoded magic numbers anywhere.

### Phase 1 — Forecasting (5:00–8:00)

Source: `src/m1_forecasting/models.py`, `src/m1_forecasting/sequence.py`

14 models in 4 tiers.

Tier A — statistical: ARIMA(1,0,1) and Prophet.
Tier B — recurrent and convolutional: LSTM, GRU, TCN, TCN-LSTM hybrid.
Tier C — modern MLP: DLinear, N-BEATS, N-HiTS, TiDE.
Tier D — transformers and foundation: PatchTST, TFT, iTransformer, Chronos-Tiny.

Input shape: (n, 60, F) — 60-day lookback windows across all features. Output: (n,) — predicted 1-day forward log return.

[INFORMATION GAIN] The shared PyTorch training loop uses the last 15 percent of training data as an internal validation set for early stopping. This is separate from the outer walk-forward fold — it never touches the actual test window. Loss function is configurable: Huber by default, or MSE, quantile, or log-cosh. Learning rate scheduler is cosine with warmup. Gradient clipping and weight decay both parameterised.

The spoiler for Video 7: the simplest models in Tier C often beat the transformers in Tier D on financial data. I will show you exactly why.

### Phase 2 — Signal Generation (8:00–11:00)

Source: `src/m2_signals/triple_barrier.py`, `src/m2_signals/meta_label.py`

Triple-Barrier Labeling from Lopez de Prado's Advances in Financial Machine Learning, Chapter 3.

For each event: take-profit at plus 2 sigma, stop-loss at minus 2 sigma, vertical timeout at 10 trading days. Sigma is the EWMA daily volatility estimate with a 21-day lookback. First barrier hit determines the label: plus 1 for take-profit, minus 1 for stop-loss, 0 for timeout.

A CUSUM filter removes the non-event days — flat market days where nothing meaningful moved. You label roughly 30 to 40 percent of trading days.

[INFORMATION GAIN] Standard up or down labels treat a 0.01 percent move and a 3 percent move identically. Triple-barrier labels encode what a real trader cares about — did this trade hit the take-profit, the stop-loss, or time out? That is the question a trading system actually needs answered.

Meta-labeling sits on top. The primary forecaster gives a direction. The meta-label classifier learns whether that direction call is likely correct. 9 classifiers: LightGBM, XGBoost, CatBoost, Random Forest, LSTM-Classifier, CNN-Classifier, TabNet, FT-Transformer, and Stacking. All trained with focal loss for class imbalance, calibrated with isotonic regression. Bet size equals meta-label probability times the base position.

[INFORMATION GAIN] This is a two-model architecture: one model says which direction, the other model says how confident to be. Separating direction and confidence produces better calibrated position sizes than a single model trying to do both. The meta-label probability naturally scales your exposure — high confidence means full position, low confidence means small or no position.

### Phase 3 — Sentiment Analysis (11:00–13:30)

Source: `src/m3_sentiment/`

Six models. VADER with logistic regression as the rule-based baseline. Then five LoRA fine-tuned transformers: FinBERT, DistilBERT, FinBERT-tone, RoBERTa, and DeBERTa-v3-small.

[INFORMATION GAIN] Two-stage fine-tuning. Stage 1 is polarity pre-training on general financial sentiment. Stage 2 is FNSPID fine-tuning — financial news headlines labeled via the triple-barrier price-action outcomes from the same trading period. The model learns what financial language actually predicts, not just what sounds positive or negative. LoRA config: rank 8, alpha 16, 5 epochs, batch 16, learning rate 2e-4. Runs on free Colab — no expensive GPU required.

After scoring, the `SentimentAggregator` creates daily ticker-level features with a 3-day recency half-life. The `PriceImpactAnalyzer` runs event studies to validate: does higher sentiment in each bucket actually predict higher post-event returns? This is the credibility gate — if the sentiment signal does not pass the event study, it does not enter the pipeline.

### Phase 4 — Multi-Input Data Fusion (13:30–15:30)

Source: `src/m4_returns/fusion.py`, `src/m4_returns/dataset.py`

At this point you have four feature groups: technical indicators, forecast model outputs, meta-label signal features, and sentiment aggregates. The `FusionDataset.build()` method aligns all four into a single matrix, tracking which columns came from which source.

Seven fusion architectures benchmarked. Three tree-based: LightGBM-Fusion, CatBoost-Fusion, Stacking-Fusion. Four neural: MultiHead-MLP, MultiInput-TCN, GMU-Fusion, CrossAttention-Fusion.

[INFORMATION GAIN] The neural models respect feature group boundaries architecturally. The GMU-Fusion model uses per-modality gating — it learns how much to trust each data source dynamically. If sentiment is noisy today but technicals are strong, the gate dampens sentiment and amplifies technicals. The CrossAttention-Fusion model applies attention over group-level embeddings. These are not naive concatenation — they are architecturally aware of what each feature group represents.

### Phase 5 — Risk and Portfolio (15:30–17:30)

Source: `src/m5_risk/volatility.py`, `src/m5_risk/portfolio.py`

Three volatility models. GARCH with AIC-based automatic p and q selection — the classical approach that captures volatility clustering. GARCH-LGB combining GARCH residuals with technical features via LightGBM — a hybrid that can capture patterns GARCH misses. LSTM-Vol treating volatility as a sequence prediction problem — the deep learning approach that learns temporal patterns directly.

All three produce predicted sigma, VaR at 95 percent, and CVaR at 95 percent. These feed into position sizing: higher predicted volatility means smaller positions to keep the daily portfolio risk constant.

Four portfolio methods: Mean-Variance via PyPortfolioOpt for maximum Sharpe, HRP (Hierarchical Risk Parity) which avoids the instability of inverting covariance matrices, Black-Litterman with ML predictions as prior views for combining market equilibrium with model forecasts, and Risk Parity with equal risk contribution.

System constraints from config: max single-stock weight 25 percent, daily VaR limit 2 percent, weekly rebalancing on Fridays, 10 basis point transaction cost.

### Phase 6 — Strategy and Backtest (17:30–19:00)

Source: `src/m6_strategy/combiner.py`, `src/m6_strategy/backtest.py`

The `SignalCombiner` implements a 5-stage gating pipeline:

Stage 1: Raw directional signal — sign of the fused predicted return.
Stage 2: Direction confidence gate — skip trade if probability of correct direction is below 0.55.
Stage 3: Meta-label confidence gate — skip trade if meta-label probability is below 0.55.
Stage 4: Sentiment alignment overlay — boost size when sentiment agrees, dampen when it contradicts.
Stage 5: Position sizing — volatility-targeted within risk budget and weight caps.

[INFORMATION GAIN] The double gate at Stages 2 and 3 is crucial. Most signals that pass direction confidence also pass meta-label confidence. But the subset that passes only one gate — high directional probability but low meta confidence, or vice versa — is where false positives concentrate. The double gate cuts those ambiguous signals. In my tests, the double gate reduced trade count by roughly 35 percent while improving net Sharpe by 0.12 compared to a single gate.

The `VectorBTEngine` runs the full historical backtest: 100,000 dollar initial capital, 1x leverage, 10 basis point transaction cost.

### Phase 7 — Production Hardening (19:00–21:30)

This is the phase nobody else shows.

[INFORMATION GAIN] Seven categories of production infrastructure. Statistical rigor: `MultipleTestingCorrector` with FDR correction, `DeflatedSharpe` adjusting for selection bias, `BacktestOverfitDetector` using Probability of Backtest Overfitting and Minimum Backtest Length. Purged CV: `PurgedWalkForwardCV` with purge and embargo to prevent label leakage. Drift detection: `DriftMonitor` with 7 statistical tests monitoring rolling accuracy, feature distributions, and cumulative deviations. Regime detection: `RegimeDetector` using Hidden Markov Model with 3 states plus `RegimeAwarePositionSizer` that scales exposure based on regime probability. Execution realism: `TransactionCostModel`, `SlippageModel`, `MarketImpactModel` implementing Almgren-Chriss, `FillSimulator`, `CapacityEstimator`. Data quality: `DataValidator`, `QualityReport`, `UniverseManager`. Serving: ONNX inference engine plus FastAPI at `/predict` and `/health`.

This phase alone has more code than most people's entire trading systems. It is the difference between a research notebook and a deployable system.

### Phase 8 — Real Backtesting and Alpha (21:30–23:00)

Source: `src/m8_backtest/`, `src/m8_alpha/`

`LiveBacktester` runs the strategy with realistic costs, slippage, and leverage constraints plus a one-day signal lag to eliminate look-ahead bias. `Tearsheet` generates a professional performance report with 14 metrics including CAGR, Sharpe, Sortino, max drawdown, Calmar ratio, and Information Ratio.

`CrossSectionalAlpha` ranks stocks by ML factor score, goes long the top quintile, short the bottom — a classic long-short equity strategy built on the pipeline's output. `FactorModel` decomposes returns against the 5-factor Fama-French model to determine how much return comes from known factors versus genuine alpha.

### Phase 9 — Universe Expansion (23:00–24:00)

Source: `src/m9_experiment/tracker.py`

Multi-universe: S&P 100 plus Nifty 50. The `ExperimentTracker` logs every run to JSONL — model type, hyperparameters, all metrics, git commit hash, and timestamp. Full reproducibility for every single experiment ever run.

---

## SECTION 4 — THE ABLATION FRAMEWORK (24:00–26:00)

The thing that ties everything together:

```python
runner = AblationRunner(
    models=[ARIMA(), LSTM(), TiDE(), TFT()],
    cv=PurgedWalkForwardCV(n_splits=6, purge_window=5),
    metrics=['mae', 'directional_acc', 'sharpe']
)
results = runner.run(X, y)
results.summary_table()
```

That block benchmarks any set of models under purged walk-forward validation, computes all metrics, and produces a comparison table. Every single model comparison in this series uses this exact framework. Same data, same splits, same metrics every time.

[INFORMATION GAIN] The ablation runner also supports feature importance extraction across all models via the `feature_importance()` method in the ModelWrapper contract. After the benchmark, you know not just which model wins, but which features each model relies on. If a model's top features are calendar effects, that is a red flag — it might be fitting to day-of-week patterns that do not persist. If its top features are volatility ratios and momentum, that is more encouraging.

---

## SECTION 5 — THE CODE STRUCTURE (26:00–28:00)

The actual repo layout:

```
src/
├── data_pipeline.py      # YahooLoader, validation, caching
├── features.py           # FeatureEngineer, 45 features
├── orchestrator.py       # Pipeline orchestration
├── ablation.py           # AblationRunner, ModelWrapper contract
├── m1_forecasting/       # 14 forecasting models
├── m2_signals/           # Triple-barrier, meta-labeling
├── m3_sentiment/         # 6 sentiment models, aggregator
├── m4_returns/           # 7 fusion models, dataset builder
├── m5_risk/              # 3 vol models, 4 portfolio methods
├── m6_strategy/          # SignalCombiner, VectorBT backtest
├── m7_validation/        # Purged CV, deflated Sharpe, drift, regime
├── m8_backtest/          # LiveBacktester, Tearsheet
├── m8_alpha/             # CrossSectionalAlpha, FactorModel
└── m9_experiment/        # ExperimentTracker, universe management
config.yaml               # All parameters in one place
```

58 Python files. Everything parameterised through `config.yaml`. No hardcoded numbers.

---

## SECTION 6 — WHAT TO EXPECT (28:00–29:00)

Each video takes one module in full depth.

Video 2: why most ML backtests are lies, and how purged walk-forward CV fixes them.
Video 3: triple-barrier labeling from scratch.
Video 4: fine-tuning FinBERT with LoRA on free Colab.
Video 5: the full data pipeline with production-grade validation.
Video 6: all 45 features built and explained.
Video 7: the 14-model benchmark — which one actually wins.

And so on through Video 25: the deployment checklist before touching real capital.

[PERSONAL INSERT NEEDED] Add one thing specific to your build experience — a module that surprised you, a phase that took longer than expected, or a result that was counterintuitive.

---

## SECTION 7 — THE CLOSE (29:00–30:00)

That is the full architecture. You now know what all 10 phases do, how they connect, and what each one is responsible for. Every video from here is one deep dive into one piece of this.

Subscribe so you do not miss any of them. Drop a comment — which part of this system are you most curious about? The forecasting layer, the sentiment pipeline, the production hardening? I read every one.

See you in Video 2.
