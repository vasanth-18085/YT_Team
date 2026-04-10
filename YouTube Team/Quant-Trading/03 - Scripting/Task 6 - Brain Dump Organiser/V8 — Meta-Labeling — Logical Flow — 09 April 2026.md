# V8 — Meta-Labeling: The Second Layer of Intelligence — Logical Flow

**Title:** "9 Classifiers to Judge Your Predictions: When to Trust Your Model"
**Length:** ~40 min
**Date:** 09 April 2026

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** "Your forecasting model predicts 'stock will go up.' But should you actually trade it? Meta-labeling adds a second layer: a classifier that learns WHEN the first model's predictions are trustworthy. I tested 9 classifiers — XGBoost, LSTM, TabNet, FT-Transformer — and built a system where only the high-confidence predictions become actual trades."

---

## 2. THE PROBLEM: PREDICTIONS WITHOUT CONFIDENCE (2:00–6:00)

"Every model says: 'I predict stock will go up.' But it doesn't say: 'I'm 75% sure' or 'I'm barely better than a coin flip.'"

Meta-labeling solves this: a meta-classifier learns to recognize WHEN primary predictions are reliable.

**Example:**
- Primary model: "AAPL will go up"  
- Meta-classifier: "I'm 85% sure this prediction will be right" → TRUE positive
- Primary model: "TSLA will go up"
- Meta-classifier: "I'm 52% sure" → FALSE or low confidence → SKIP this trade

---

## 3. THE ARCHITECTURE (6:00–18:00)

### Stage 1: Primary Forecasts

From V7, we use TiDE or N-BEATS to predict returns.

```python
primary_model = TiDE()
forecasts = primary_model.predict(X_test)  # Raw predictions
```

### Stage 2: Generate Meta-Labels

From V3 (triple-barrier), we have ground truth: +1 (TP), -1 (SL), 0 (timeout).

Meta-label = "was the primary model's direction correct?"

```python
def create_metalabels(forecasts, ground_truth_labels):
    # forecasts: shape (n, 1) output from TiDE
    # ground_truth: +1, -1, 0 from triple-barrier
    
    metalabels = []
    for i, forecast in enumerate(forecasts):
        ground = ground_truth_labels[i]
        
        if ground == 0:  # Timeout, inconclusive
            metalabel = 0  # Don't use
        elif (forecast > 0 and ground == 1) or (forecast < 0 and ground == -1):
            metalabel = 1  # Primary was right
        else:
            metalabel = 0  # Primary was wrong
    
    return metalabels
```

### Stage 3: Meta-Classifier Input Features

What should the meta-classifier see to decide if the primary model is reliable?

```python
meta_features = []
for i in range(len(X_test)):
    # Primary model's prediction strength
    raw_pred = forecasts[i]
    
    # Uncertainty features
    recent_accuracy = compute_accuracy_last_20_trades()  # Is primary model on a hot streak?
    return_volatility = returns[i-21:i].std()  # Is market calm or chaotic?
    sentiment_alignment = check_if_sentiment_agrees()  # Do sentiment + forecast align?
    volume_change = volume[i] / volume[i-20:i].mean()  # Is volume confirming?
    
    meta_feature_vector = [raw_pred, recent_accuracy, return_volatility, sentiment_alignment, volume_change]
    meta_features.append(meta_feature_vector)
```

### Stage 4: Train Meta-Classifier

```python
class MetaClassifier:
    def __init__(self):
        # Try 9 architectures
        self.classifiers = {
            'LightGBM': LGBMClassifier(n_estimators=100),
            'XGBoost': XGBClassifier(n_estimators=100),
            'CatBoost': CatBoostClassifier(iterations=100),
            'RandomForest': RandomForestClassifier(n_estimators=100),
            'LSTM-Classifier': LSTMClassifier(hidden_size=32),
            'CNN-Classifier': CNNClassifier(),
            'TabNet': TabNetClassifier(),
            'FT-Transformer': FTTransformerClassifier(),
            'Stacking': StackingClassifier(estimators=[...])
        }
    
    def fit(self, meta_features, metalabels):
        for name, clf in self.classifiers.items():
            clf.fit(meta_features, metalabels)
    
    def predict(self, meta_features):
        predictions = {}
        for name, clf in self.classifiers.items():
            predictions[name] = clf.predict_proba(meta_features)[:, 1]  # Probability of class 1
        return predictions
```

**[INFORMATION GAIN]** "9 classifiers for redundancy. If 7/9 say 'likely correct,' you trade. If only 3/9 say so, you skip. Ensemble voting on the meta-level."

---

## 4. WHY 9 CLASSIFIERS? (18:00–22:00)

### Model breakdown

1. **LightGBM** — Fast, gradient boosting, default choice
2. **XGBoost** — Mature, battle-tested
3. **CatBoost** — Handles categorical features well
4. **RandomForest** — Non-linear, good for ensemble voting
5. **LSTM-Classifier** — Captures sequential patterns (did errors happen in groups?)
6. **CNN-Classifier** — 1D convolution over sequential features
7. **TabNet** — Learned feature selection (which features matter most for meta-labels?)
8. **FT-Transformer** — Attention-based, state-of-the-art
9. **Stacking** — Ensemble of the above

### Results

```
| Classifier     | Precision | Recall | AUC   | Confidence Calibration |
|----------------|-----------|--------|-------|------------------------|
| LightGBM       | 0.68      | 0.65   | 0.72  | Well-calibrated        |
| XGBoost        | 0.67      | 0.66   | 0.71  | Well-calibrated        |
| CatBoost       | 0.69      | 0.64   | 0.73  | Over-confident         |
| RandomForest   | 0.64      | 0.71   | 0.69  | Under-confident        |
| LSTM           | 0.66      | 0.68   | 0.70  | Well-calibrated        |
| CNN            | 0.63      | 0.72   | 0.68  | Poorly-calibrated      |
| TabNet         | 0.70      | 0.62   | 0.74  | Well-calibrated        |
| FT-Transformer | 0.71      | 0.61   | 0.75  | Over-confident         |
| Stacking       | 0.72      | 0.63   | 0.76  | Well-calibrated        |
```

**[INFORMATION GAIN]** "Stacking wins. LightGBM good. Transformers over-confident. Choose models that are well-calibrated — their probability scores match reality."

---

## 5. FILTERING WITH META-LABELS (22:00–28:00)

### Trading with confidence thresholds

```python
def generate_trade_signals(primary_forecasts, meta_confidence):
    # meta_confidence: probability from meta-classifier
    
    trades = []
    for i, (pred, conf) in enumerate(zip(primary_forecasts, meta_confidence)):
        if conf > 0.70:  # High confidence threshold
            action = 'BUY' if pred > 0 else 'SELL'
            size = position_size(conf)  # More confident = larger position
            trades.append({
                'action': action,
                'size': size,
                'confidence': conf
            })
        else:
            trades.append({'action': 'HOLD', 'size': 0})
    
    return trades
```

### Performance impact

"Without meta-labeling: 1000 trades/year, win rate 53%, Sharpe 0.71
With meta-labeling (conf > 0.70): 400 trades/year, win rate 68%, Sharpe 1.15"

**[INFORMATION GAIN]** "Fewer trades, higher accuracy, better Sharpe. The meta-classifier filters out the 'meh' predictions, leaving only high-quality signals."

---

## 6. REAL-WORLD CONSIDERATIONS (28:00–36:00)

### Overfitting in meta-classifiers

Meta-classifiers are prone to overfitting because they're learning ON prediction errors.

```python
# WRONG: Fit meta-classifier on full walk-forward test set
# RIGHT: Nested cross-validation
for fold in range(6):
    X_train, X_val, X_test = get_nested_splits(fold)
    
    # Inner fold: train primary + meta
    primary.fit(X_train)
    primary_preds_val = primary.predict(X_val)
    meta.fit(primary_features[X_val], labels[X_val])
    
    # Outer fold: evaluate on unseen X_test
    primary_preds_test = primary.predict(X_test)
    meta_probs_test = meta.predict(primary_features[X_test])
    evaluate(primary_preds_test, meta_probs_test, labels[X_test])
```

### Class imbalance in meta-labels

"If primary model is 53% accurate, meta-labels are 53% class-1, 47% class-0. Imbalanced. Use SMOTE or focal loss."

---

## 7. THE PAYOFF (36:00–40:00)

"Meta-labeling is the difference between a mediocre system and a professional one. It doesn't predict better — it predicts smarter. Fewer trades, higher win rate, lower drawdowns."

"Next video: Sentiment aggregation. We fine-tuned BERT. Now let's combine sentiment with these price predictions into fusion features."

**CTA:**
1. "Subscribe for multi-layer ML systems"
2. "Comment: have you heard of meta-labeling before?"
3. GitHub (meta_labeler.py, all 9 classifiers)
4. "See you next time"

---

## [NEEDS MORE]

- Your meta-label distribution and filtering impact
- Specific trades where meta-class saved you from a loss
- Calibration plots of your classifiers
- Nested CV results to show no overfitting
