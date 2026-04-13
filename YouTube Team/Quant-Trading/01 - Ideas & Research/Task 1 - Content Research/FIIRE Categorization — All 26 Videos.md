# MLQuant — FIIRE Content Categorization

**Created:** 13 April 2026  
**Updated:** 13 April 2026  
**Framework:** FIIRE Method (from YT Channel Playbook — Paddy Galloway / Nate Black)

> **⚠️ V-NUMBER NOTE:** The main table uses CANONICAL V-numbers (from Task 1 Content Research). Script/hook files use PRODUCTION V-numbers which differ from V8 onwards. See `V-NUMBER-RESOLUTION.md` for the mapping.
>
> **4 production-only videos** (Prod V18, V19, V20, V24) were not in the canonical plan. Their FIIRE categories are in the Addendum section below.

---

## Categories

| Type | Purpose | MLQuant Application |
|------|---------|---------------------|
| **Tinder** | Trending/timely — catches fire fast, burns out | Ride current ML/AI hype waves |
| **Kindling** | Core content — keeps the fire consistent | System-building narrative, model comparisons |
| **Logs** | Evergreen — searches well long-term | Technique explainers, tooling, reference content |
| **Flint** | Experimental — tests new directions | Niche architectures, unconventional approaches |

---

## All 26 Videos Categorized

### TINDER (5 videos — 19%)
| Video | Title | Why Tinder |
|-------|-------|------------|
| V4 | We Read the Market WITHOUT a Single Price Chart | NLP/LLM hype makes sentiment-from-text timely |
| V8 | They Got It ALL WRONG About Transformers for Stocks | Transformer debate is hot, contrarian take drives clicks |
| V9 | These Transformer Killers Are HIDDEN in Plain Sight | MLP-vs-Transformer discourse is peak-hype right now |
| V12 | I Fine-Tuned FinBERT WITHOUT a Single GPU | LoRA/fine-tuning is trending across all ML |
| V23 | How Quant Funds Make Money (No One Taught This) | Factor investing getting mainstream retail attention |

### KINDLING (7 videos — 27%)
| Video | Title | Why Kindling |
|-------|-------|-------------|
| V0 | I Built 44 ML Trading Models — All Free on GitHub | Channel trailer — sets the series premise |
| V7 | I Tested 14 Models on ONLY Real Stock Data | Core model shootout — the channel's identity |
| V11 | VADER DOESN'T Matter for Finance. THIS Model Does. | Core comparison content, backbone of sentiment arc |
| V13 | 90% of Traders Predict Markets The Wrong Way | Fusion concept — core system differentiator |
| V17 | 99% Of ML Models Never Become Real Trades | Signal-to-trade bridge — core system building |
| V22 | This Kills Most Strategies… Why Nobody Fixes It | Reality check — core value proposition of the channel |
| V25 | I Built 44 ML Models to Beat the S&P 500 | Series finale — payoff for the whole journey |

### LOGS (12 videos — 46%)
| Video | Title | Why Logs |
|-------|-------|---------|
| V1 | I Built a 44-Model Trading System (Full Architecture) | System architecture — evergreen reference |
| V2 | The Backtest Lie That's Costing You Real Money | "Backtesting mistakes" is a perennial search query |
| V3 | ML Models DON'T Matter… But Your Labels Do | Triple barrier labeling — evergreen ML finance concept |
| V5 | The CSV File Lie Every ML Trader Still Believes | Data pipeline fundamentals — always searchable |
| V6 | Every Trading Feature for ML Explained (All 45) | Feature engineering encyclopedia — peak search value |
| V10 | 99% of Traders Don't Know Meta-Labeling Exists | Specific technique — high search intent |
| V15 | I Built a Hybrid Vol Model. It Beat Everything. | GARCH is a staple quant finance topic |
| V16 | 4 Methods That Fix 90% of Portfolio Problems | Portfolio construction — evergreen finance |
| V18 | I Backtested 44 Models WITHOUT Writing a Single Loop | VectorBT tool tutorial — highly searchable |
| V20 | 99% of Traders Never Check for Model Drift | MLOps/drift monitoring — growing evergreen topic |
| V21 | Execute Large Trades WITHOUT Moving Price | Market impact/execution — timeless trading concept |
| V24 | Your Model Doesn't Matter. Your Pipeline Does. | MLOps pipeline — evergreen and searchable |

### FLINT (2 videos — 8%)
| Video | Title | Why Flint |
|-------|-------|----------|
| V14 | Why Nobody Uses Neural Gating (They Should) | Niche architecture comparison — testing audience appetite for deep technical content |
| V19 | 99% of ML Models Trade Blind (This One Doesn't) | HMM regime detection — unconventional for the audience |

---

## Balance Assessment

```
Tinder:   ████░░░░░░░░░░░░░░ 19%  (5/26)
Kindling: ██████░░░░░░░░░░░░ 27%  (7/26)
Logs:     ████████████░░░░░░ 46%  (12/26)
Flint:    ██░░░░░░░░░░░░░░░░  8%  (2/26)
```

**Verdict:** Logs-heavy, which is correct for a first series building an evergreen technical catalog. The 5 Tinder videos ride current AI/ML hype and should be published when their topics are peaking. The 2 Flint videos test whether the audience wants deep architecture content — if they perform well, expand this category in Season 2.

**Scheduling implication:** Publish Tinder videos (V4, V8, V9, V12, V23) when their topics trend. Don't hold them for sequential order — timing matters more than sequence for Tinder content. Logs and Kindling can follow the series order.

---

## ADDENDUM — Production-Only Videos (FIIRE Categories)

These 4 videos exist in the production/script pipeline but had no corresponding canonical video entry.

### KINDLING (+1 → 8 total, 27%)
| Video | Title | Why Kindling |
|-------|-------|-------------|
| Prod V24 | Paper Trading Found 3 Bugs My Backtest Missed | Core bridge from backtest to live — essential system-building step; defines the channel's "we go further" promise |

### LOGS (+2 → 14 total, 47%)
| Video | Title | Why Logs |
|-------|-------|---------|
| Prod V18 | The Statistical Check That Killed 6 of My Strategies | "Multiple testing correction" is highly searchable among quant researchers — evergreen statistical method |
| Prod V20 | Stop Looking at Equity Curves. Use This Instead. | "Strategy tearsheet", "evaluate trading strategy" are perennial search queries — tool/reference content |

### FLINT (+1 → 3 total, 10%)
| Video | Title | Why Flint |
|-------|-------|----------|
| Prod V19 | Your Sharpe Ratio Is a Lie. Here's the Real One. | Deflated Sharpe Ratio is niche advanced statistics — tests audience appetite for hardcore statistical rigor |

---

## Updated Balance Assessment (Including Production-Only Videos)

The full production series has 26 videos. The canonical plan has 26 entries, but 5 canonical topics were folded into parent scripts and 4 production-only topics replaced them. Counting PRODUCTION videos only:

```
Tinder:   ████░░░░░░░░░░░░░░ 17%  (5/30 entries, but 5/26 production videos)
Kindling: ██████░░░░░░░░░░░░ 27%  (8/30 entries, maps to 8/26 production)
Logs:     ████████████████░░ 47%  (14/30 entries, maps to 14/26 production)
Flint:    ███░░░░░░░░░░░░░░░ 10%  (3/30 entries, maps to 3/26 production)
```

| Category | Canonical | +Prod-Only | Production Total | Target | Status |
|----------|-----------|------------|-----------------|--------|--------|
| Tinder | 5 | +0 | 5 (19%) | 15–25% | ✅ |
| Kindling | 7 | +1 | 8 (31%) | 25–35% | ✅ |
| Logs | 12 | +2 | 14 (54%) | 40–50% | ⚠️ Slightly high |
| Flint | 2 | +1 | 3 (12%) | 5–15% | ✅ |

**Note:** Logs at 54% is 4% above the 50% target ceiling. This is acceptable for a first series building an evergreen technical catalog. The slight overshoot comes from production-only videos being reference/tool content. Can be rebalanced in Season 2.
