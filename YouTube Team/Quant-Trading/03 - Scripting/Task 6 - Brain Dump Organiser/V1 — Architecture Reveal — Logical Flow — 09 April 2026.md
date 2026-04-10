# V1 — Full Architecture Reveal — Logical Flow

**Title:** "I Built a 44-Model Trading System (Full Architecture)"
**Length:** ~30 min
**Date:** 09 April 2026

---

## 1. THE HOOK (0:00–1:00)

**[INFORMATION GAIN]** "This is what a REAL ML trading system looks like. Not a Jupyter notebook with LSTM stock prediction. Not a single model backtested on cherry-picked data. This is 44 machine learning models across 10 phases, chained together into a pipeline that goes from raw Yahoo Finance data all the way to paper-traded portfolio returns."

Show the end result FIRST:
- Flash an equity curve (ML system vs benchmark)
- Flash an ablation comparison table
- Flash the GitHub repo file tree (58 Python files, 10 notebooks, 30+ docs pages)

"Over the next 24 videos, I'll build every single piece. Today — the full architecture."

---

## 2. WHY A PIPELINE, NOT A MODEL (1:00–3:00)

**[INFORMATION GAIN]** "Professional quant funds don't use a single model. They use a pipeline. Data engineers clean the data, researchers build prediction models, risk managers size positions, execution teams handle trading. This repo mirrors that structure in code."

The key design principles:
1. **Modular pipeline architecture** — each phase operates independently with a well-defined interface
2. **Ablation studies** — swap any model in/out without touching other phases
3. **Walk-forward validation** — no lookahead bias, purged + embargoed cross-validation everywhere
4. **Composability** — each module's output feeds naturally into the next

**The ModelWrapper contract** — every single model in the system implements this:
```python
class ModelWrapper(ABC):
    name: str = "BaseModel"           # Displayed in ablation tables
    def fit(self, X_train, y_train):  # Train
    def predict(self, X_test):        # Predict → np.ndarray
    def get_params(self) -> dict:     # Hyper-params for logging
    def feature_importance(self):     # If available
```
**[INFORMATION GAIN]** "This contract is the glue. Because every model follows the same interface, I can run `AblationRunner.run(models=[...], X, y)` and get automatic walk-forward evaluation for ANY model I plug in. ARIMA, LSTM, Transformer, LightGBM — they all look the same to the runner."

---

## 3. THE 10-PHASE WALKTHROUGH (3:00–20:00)

### Phase 0 — Data Pipeline (3:00–5:00)

**Code:** `src/data_pipeline.py`, `src/features.py`, `config.yaml`

**What it does:**
- `YahooLoader` — downloads OHLCV from Yahoo Finance, caches as Parquet (not CSV — Parquet is 3-5x smaller and 10x faster to read)
- `FeatureEngineer` — transforms raw OHLCV into 45+ features across 4 groups:
  - **Technical indicators:** RSI (7, 14, 21), MACD (12/26/9), Bollinger Bands (20), ATR (14), ADX (14), CCI (20), Stochastic (14), Williams %R (14), OBV, Ichimoku
  - **Rolling statistics:** lagged returns (1, 5, 10, 21 days), rolling volatility (5, 10, 21, 63 days), rolling momentum (5, 21, 63 days)
  - **Calendar features:** day of week, month, quarter, month start/end
  - **Price structure:** intraday range, candle body ratio, shadow ratios
- `make_targets()` — forward log returns at horizons 1d and 5d

**[INFORMATION GAIN]** Column naming convention: `{indicator}_{params}_{timeframe}` — e.g., `rsi_14_1d`. This is future-proof for multi-timeframe stacking.

**Config-driven:** Everything parameterized in `config.yaml`. RSI periods, MACD windows, vol lookbacks — change the config, the pipeline adapts. No hardcoded magic numbers.

### Phase 1 — Time-Series Forecasting (5:00–8:00)

**Code:** `src/m1_forecasting/models.py`, `src/m1_forecasting/sequence.py`

**14 models in 4 tiers:**
- **Tier A (Statistical):** ARIMA(1,0,1), Prophet
- **Tier B (Recurrent/Conv):** LSTM, GRU, TCN, TCN-LSTM (hybrid)
- **Tier C (Modern MLP):** DLinear, N-BEATS, N-HiTS, TiDE
- **Tier D (Transformer/Foundation):** PatchTST, TFT, iTransformer, Chronos-Tiny

Input: `(n, 60, F)` — 60-day lookback windows of all features
Output: `(n,)` — predicted 1-day forward log return

**[INFORMATION GAIN]** The shared PyTorch training loop (in `ForecastingWrapper._pytorch_fit`):
- Last 15% of training data used as internal validation for early stopping (doesn't touch the outer walk-forward val set)
- Loss function factory: Huber (default), MSE, quantile, log-cosh
- LR scheduler factory: cosine with warmup (default), plateau, cosine
- Gradient clipping, weight decay, configurable everything

**Spoiler for later videos:** "The simplest models in Tier C often beat the Transformers in Tier D on financial data. I'll show you exactly why in Videos 7-9."

### Phase 2 — Signal Generation (8:00–10:30)

**Code:** `src/m2_signals/triple_barrier.py`, `src/m2_signals/meta_label.py`

**Triple-Barrier Labeling** (López de Prado, AFML Ch. 3):
- For each event: 3 barriers — take-profit (+2σ), stop-loss (-2σ), timeout (10 days)
- EWMA volatility with 21-day lookback sets barrier width
- Labels: +1 (hit take-profit), -1 (hit stop-loss), 0 (timeout)
- CUSUM filter removes non-event days (noise)

**[INFORMATION GAIN]** "Standard labels are useless — stock went up, stock went down. Triple-barrier says: did this trade HIT your profit target, your stop loss, or time out? That's what you actually need to know when trading."

**Meta-Labeling** (AFML Ch. 3):
- Primary model says: BUY or SELL (the side)
- Meta-label classifier says: is this signal CORRECT or WRONG? (binary P(correct))
- 9 classifiers: LightGBM, XGBoost, CatBoost, Random Forest, LSTM-Classifier, CNN-Classifier, TabNet, FT-Transformer, Stacking
- Focal loss for class imbalance, SMOTE oversampling, isotonic calibration
- Bet size = meta-label probability × base position

### Phase 3 — Sentiment Analysis (10:30–13:00)

**Code:** `src/m3_sentiment/`

**6 models:**
- VADER+LogReg (rule-based baseline)
- 5 LoRA fine-tuned transformers: FinBERT, DistilBERT, FinBERT-tone, RoBERTa, DeBERTa-v3-small

**[INFORMATION GAIN]** Two-stage fine-tuning:
1. Polarity pre-training on general sentiment
2. FNSPID fine-tuning with LoRA — financial news sentiment labeled via price-action (triple-barrier labels on news dates)

LoRA config: rank=8, alpha=16, 5 epochs, batch 16, lr=2e-4. Runs on free Colab.

**Pipeline:** Raw articles → per-model scores → `SentimentAggregator` (daily ticker-level features with 3-day recency half-life) → `PriceImpactAnalyzer` (event study: does sentiment actually predict returns?)

### Phase 4 — Multi-Input Data Fusion (13:00–15:00)

**Code:** `src/m4_returns/fusion.py`, `src/m4_returns/dataset.py`

The problem: you now have 4 feature groups — technical, forecast, signal, sentiment. How to combine?

**`FusionDataset.build()`** — aligns all inputs into `(X_fused, y, group_sizes)` where `group_sizes = [n_tech, n_forecast, n_signal, n_sentiment]`

**7 fusion architectures:**
- **Tree-based:** LightGBM-Fusion, CatBoost-Fusion, Stacking-Fusion
- **Neural:** MultiHead-MLP, MultiInput-TCN, GMU-Fusion, CrossAttn-Fusion

**[INFORMATION GAIN]** The neural models respect feature group boundaries — GMU-Fusion uses per-modality gates (learns HOW MUCH to trust each data source), CrossAttn-Fusion uses attention over group embeddings. These aren't just concatenation — they're architecturally aware of what each feature means.

### Phase 5 — Risk & Portfolio (15:00–17:00)

**Code:** `src/m5_risk/volatility.py`, `src/m5_risk/portfolio.py`

**3 volatility models:**
- GARCH-Vol (auto-select p,q by AIC over {1,2,3}×{1,2,3})
- GARCH-LGB-Vol (GARCH residuals + technical features → LightGBM)
- LSTM-Vol (sequence-to-volatility neural model)

→ Outputs: predicted σ̂, VaR at 95%, CVaR at 95%

**4 portfolio methods:**
- MeanVariance (max-Sharpe via PyPortfolioOpt)
- HRP (clustering-based, no covariance inversion)
- BlackLitterman (ML predictions as Bayesian prior views)
- RiskParity (equal risk contribution)

Config: max single-stock weight = 25%, daily VaR limit = 2%, rebalance weekly (Fridays), transaction cost = 10bps

### Phase 6 — Strategy & Backtest (17:00–18:30)

**Code:** `src/m6_strategy/combiner.py`, `src/m6_strategy/backtest.py`

**SignalCombiner — 5-stage gating pipeline:**
1. Raw directional signal from fused prediction (sign of predicted return)
2. Direction confidence gate (P(correct direction) > 0.55)
3. Meta-label confidence gate (P(signal correct) > 0.55)
4. Sentiment alignment overlay (boost if sentiment agrees, dampen if disagrees)
5. Position sizing: volatility-targeted + risk budget + portfolio weight cap

→ `VectorBTEngine` runs the backtest: $100K initial, 1x leverage, 10bps transaction cost

### Phase 7 — Production Hardening (18:30–21:00)

**7 sub-modules — this is what nobody else shows:**

- **Statistical Rigor:** `MultipleTestingCorrector` (FDR correction), `DeflatedSharpe` (adjusts for selection bias), `BacktestOverfitDetector` (PBO + MinBTL)
- **Purged CV:** `PurgedWalkForwardCV` — purge + embargo around label boundaries
- **Drift Detection:** `DriftMonitor` — KS tests, CUSUM on rolling metrics, alerts
- **Regime Detection:** `RegimeDetector` (HMM with 2-3 states), `RegimeAwarePositionSizer`
- **Execution Realism:** `TransactionCostModel`, `SlippageModel`, `MarketImpactModel` (Almgren-Chriss), `FillSimulator`, `CapacityEstimator`
- **Data Quality:** `DataValidator`, `QualityReport`, `UniverseManager`
- **Serving:** ONNX inference engine + FastAPI endpoint (`/predict`, `/health`)

### Phase 8 — Real Backtesting & Alpha (21:00–22:30)

**Code:** `src/m8_backtest/`, `src/m8_alpha/`

- `LiveBacktester` — backtest with realistic costs, slippage, leverage constraints
- `Tearsheet` — professional performance report
- `CrossSectionalAlpha` — rank stocks by ML factor, long top quintile, short bottom
- `FactorModel` — 5-factor alpha model

### Phase 9 — Universe Expansion (22:30–23:30)

**Code:** `src/m9_experiment/tracker.py`

- Multi-universe: S&P 100 (US) + Nifty 50 (India)
- `ExperimentTracker` — JSONL logging of every run (params, metrics, timestamps)
- Journal export for structured research documentation

---

## 4. THE CODE STRUCTURE (23:30–26:00)

Show the actual repo layout:
- `src/` — 25 Python modules, ~58 files total
- `notebooks/` — 10 Jupyter notebooks (one per phase), each self-contained
- `docs/` — Full MkDocs site with phase guides, API reference, glossary
- `GUIDE.md` — 17-part zero-to-hero guide (assumes Python, teaches everything else)
- `config.yaml` — single config file drives the entire system
- `Makefile` — `make data`, `make backtest`, `make docs`, `make clean`

**[INFORMATION GAIN]** "The learning path is: GUIDE.md → Docs Site → Notebooks → Source Code. You don't need a finance background. You don't need deep learning expertise. You don't even need a GPU — CPU works for everything."

---

## 5. SERIES ROADMAP (26:00–28:00)

Quick visual of the 25-video journey:
- **Act 1 (V1-V4):** Architecture, backtesting lies, triple-barrier, FinBERT — the hook
- **Act 2 (V5-V9):** Data pipeline, features, 14 models, LSTM vs Transformer, modern MLPs — building from scratch
- **Act 3 (V10-V14):** Meta-labeling, sentiment showdown, LoRA tutorial, fusion, GMU vs CrossAttn — the secret sauce
- **Act 4 (V15-V18):** GARCH+ML, portfolio optimization, signal gating, VectorBT — where theory meets money
- **Act 5 (V19-V23):** HMM regimes, drift detection, market impact, realistic backtest, factor investing — what nobody shows
- **Act 6 (V24-V25):** MLOps + experiment tracking, final results — grand finale

---

## 6. CTA + CLOSE (28:00–30:00)

- "All code is on GitHub — link below"
- "Next video: Why 90% of ML backtests are lies, and how to fix yours"
- Subscribe + notifications

---

## [NEEDS MORE]

- **Live demo moment:** Can you run `PipelineOrchestrator.run_all()` and screen-record the output? Even 30 seconds of the pipeline running through phases with timing printouts would be powerful.
- **Flash of results:** The ablation table from Phase 1 (14 models compared) — even blurred or quick-flashed — creates massive curiosity for V7.
- **Personal framing:** "I built this because..." — the origin story. One paragraph of WHY.
- **Comparison to competitors:** "Most ML trading tutorials stop at LSTM stock prediction. This system has 10 phases AFTER that."
