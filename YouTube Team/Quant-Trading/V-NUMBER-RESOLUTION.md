# V-Number Resolution — RESOLVED

**Created:** 13 April 2026  
**Resolved:** 14 April 2026  
**Status:** ✅ RESOLVED — Script V-numbers are the Production Standard

---

## Root Cause

Two V-number orderings exist because **Task 1 (Content Research)** defined the 26-video series in a **viewer-journey order** (breadth → depth, beginner → advanced), while **Task 6 (Brain Dump)** organized content in **pipeline-build order** (the sequence the quant system modules were coded). Both cover the same codebase but structure the 26 episodes differently.

Tasks 4–5 (titles, thumbnails) followed Task 1's viewer-journey ordering.  
Tasks 6–11 (scripts, hooks, community posts) followed the pipeline-build ordering.

V0–V7 are **identical** in both orderings. V8–V25 diverge.

---

## Decision: Script V-Numbers = Production V-Numbers

| Factor | Script Ordering | Canonical Ordering |
|--------|----------------|-------------------|
| Files using it | **156** (Tasks 6–11: 26 files each × 6 task folders) | 4 (Task 1, Task 4, Task 5, FIIRE) |
| Contains actual script content | ✅ | ❌ |
| All tasks internally consistent | ✅ | ✅ |
| Cross-references (CTAs, hooks → scripts) | ✅ All match | N/A |

**Script ordering wins.** Renaming 156 files would be destructive, error-prone, and break cross-task references. The 4 canonical-ordered files will be updated with a mapping header.

---

## Complete Topic-by-Topic Mapping

### V0–V7: Identical in Both Orderings ✅

| Prod V# | Topic | Title Sync |
|---------|-------|------------|
| V0 | Channel Trailer | ✅ Done |
| V1 | Architecture Reveal | ✅ Available |
| V2 | Backtesting Lies | ✅ SYNCED |
| V3 | Triple-Barrier Labeling | ✅ Available |
| V4 | FinBERT LoRA Fine-Tuning | ✅ Available |
| V5 | Data Pipeline | ✅ SYNCED |
| V6 | 45 Trading Features | ✅ Available |
| V7 | Testing 14 Forecasting Models | ✅ Available |

### V8–V25: Divergent — Mapped by Topic

| Prod V# (Script) | Script Topic | Canonical V# | Canonical Topic | Title Reuse |
|---|---|---|---|---|
| **V8** | Meta-Labeling | V10 | Meta-Labeling | ✅ Use Title V10 section |
| **V9** | Sentiment Aggregation | V11 | Sentiment Showdown | ✅ Use Title V11 section |
| **V10** | Fusion Layer | V13 | Multi-Input Fusion | ✅ Use Title V13 section |
| **V11** | Volatility Estimation | V15 | GARCH + ML | ✅ Use Title V15 section |
| **V12** | Portfolio Construction | V16 | Portfolio Optimization | ✅ Use Title V16 section |
| **V13** | VectorBT Backtesting | V18 | VectorBT | ✅ Use Title V18 section |
| **V14** | Regime Detection | V19 | HMM Regimes | ✅ Use Title V19 section |
| **V15** | Drift Monitoring | V20 | Drift Detection | ✅ Use Title V20 section |
| **V16** | Transaction Costs | V21 | Market Impact (Almgren-Chriss) | ✅ Use Title V21 section |
| **V17** | Position Sizing | V17 | Signal Gating + Position Sizing | ✅ Same V# — use Title V17 section |
| **V18** | Multiple Testing Correction | — | *No canonical equivalent* | ❌ NEEDS NEW TITLES |
| **V19** | Deflated Sharpe & PBO | — | *No canonical equivalent* | ❌ NEEDS NEW TITLES |
| **V20** | Performance Tearsheet | — | *No canonical equivalent* | ❌ NEEDS NEW TITLES |
| **V21** | Experiment Tracking | V24 | MLOps for Trading | ✅ Use Title V24 section |
| **V22** | Factor Analysis | V23 | Factor Investing / Alpha (partial) | ⚠️ Partial — borrow from Title V23 |
| **V23** | Cross-Sectional Alpha | V23 | Factor Investing / Alpha | ✅ Use Title V23 section |
| **V24** | Live Backtester & Paper Trading | — | *No canonical equivalent* | ❌ NEEDS NEW TITLES |
| **V25** | Deployment Checklist | V25 | Final Results | ⚠️ Close — use Title V25 section |

### Summary

- **21 clean 1:1 topic matches** → titles can be reused directly
- **1 partial match** (Script V22 ↔ Canonical V23) → borrow relevant titles
- **4 scripts with NO title coverage** → V18, V19, V20, V24 need title generation

---

## Canonical-Only Topics (No Dedicated Scripts)

These 5 topics were planned in Task 1 but the script phase covered them within parent videos:

| Canonical V# | Topic | Where Content Lives in Scripts |
|---|---|---|
| V8 | LSTM vs Transformer deep dive | Folded into Script V7 (14 Models) |
| V9 | Modern MLPs (DLinear, N-BEATS, etc.) | Folded into Script V7 (14 Models) |
| V12 | LoRA tutorial (step-by-step) | Folded into Script V4 (FinBERT LoRA) |
| V14 | GMU vs Cross-Attention | Folded into Script V10 (Fusion Layer) |
| V22 | Fantasy vs Reality (real costs) | Partially in Script V16 (Transaction Costs) + V20 (Performance Tearsheet) |

**These are candidates for future "deep dive" bonus episodes.** Titles and thumbnails already exist for them.

---

## Action Items

### Immediate (Title Sync for V8+)
For each script V8–V25, use the **Title Reuse** column above to find the correct section in the title file. The V-number in the title file DIFFERS from the production V-number — always follow this mapping.

### Title Generation Needed
Create 20 title options each for:
- V18 — Multiple Testing Correction
- V19 — Deflated Sharpe & PBO
- V20 — Performance Tearsheet
- V24 — Live Backtester & Paper Trading

### Thumbnail Remapping Needed
The thumbnail file uses canonical V-numbers. Use this mapping to assign thumbnail concepts to production V-numbers:
- Script V8 (Meta-Labeling) → use Thumbnail V10 concepts
- Script V9 (Sentiment) → use Thumbnail V11 concepts
- Script V10 (Fusion) → use Thumbnail V13 concepts
- ...and so on per the mapping table above
- Scripts V18, V19, V20, V24 → need new thumbnail concepts

### FIIRE Remapping Needed
The FIIRE categorization file uses canonical V-numbers. Remap categories to production V-numbers using the mapping table above.

### Files to Update (Header Note)
Add a V-number mapping note to the top of:
1. Title file (Task 4) — note that V-numbers differ from script/production V-numbers
2. Thumbnail file (Task 5) — same note
3. FIIRE Categorization — same note

---

## Quick-Lookup: "I have a Script V#, what Title V# do I need?"

```
Script V0–V7  → Title V0–V7  (same)
Script V8     → Title V10
Script V9     → Title V11
Script V10    → Title V13
Script V11    → Title V15
Script V12    → Title V16
Script V13    → Title V18
Script V14    → Title V19
Script V15    → Title V20
Script V16    → Title V21
Script V17    → Title V17  (same)
Script V18    → [NO TITLES — needs generation]
Script V19    → [NO TITLES — needs generation]
Script V20    → [NO TITLES — needs generation]
Script V21    → Title V24
Script V22    → Title V23  (partial match)
Script V23    → Title V23
Script V24    → [NO TITLES — needs generation]
Script V25    → Title V25
```
- **V17 — Signal→Trades** (execution bridge)
- **V22 — Fantasy vs Reality** (backtest reality check)

Some hook/script topics don't appear in the title file:
- **Performance Tearsheet** (Hook V20)
- **Experiment Tracking** (Hook V21)
- **Live Backtester** (Hook V24)

## Resolution Options

1. **Adopt the title file ordering as canonical** — Renumber all hook/script files from V8+ to match the title file's topic assignments
2. **Adopt the hook/script ordering as canonical** — Re-map titles in the title file to match the hook V-numbers
3. **Create a master mapping** — Keep both numbering schemes but create an explicit lookup table

## What Was Done

- V2 and V5 titles synced (these are consistent between files) ✅
- V8-V24 title sync BLOCKED until mapping is resolved
