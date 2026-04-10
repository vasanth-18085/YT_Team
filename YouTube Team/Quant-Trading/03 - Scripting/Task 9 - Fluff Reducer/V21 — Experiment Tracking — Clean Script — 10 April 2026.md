# V21 — Experiment Tracking — Clean Script

**Title:** Systematic Experimentation: How to Track 1,000 Backtests
**Target Length:** ~40 minutes
**Date:** 10 April 2026

---

## SECTION 1 — HOOK (0:00–2:00)

You ran 50 experiments. Which one was best? Why? Can you reproduce it?

[INFORMATION GAIN] Without structured tracking, research becomes memory-driven and non-reproducible. Experiment tracking turns model development into an auditable process.

---

## SECTION 2 — WHY MEMORY-BASED RESEARCH FAILS (2:00–8:00)

Common failure modes:
- best run not reproducible
- hyperparameters undocumented
- code version mismatch
- accidental data leakage not traceable

In quant trading, this is fatal because slight differences in data windows or costs can invert conclusions.

---

## SECTION 3 — TRACKER SCHEMA DESIGN (8:00–16:00)

Minimum fields per run:
1. timestamp
2. dataset window
3. model type
4. hyperparameters
5. metrics (gross + net)
6. code commit hash
7. random seed
8. notes

```python
from dataclasses import dataclass

@dataclass
class ExperimentRecord:
    timestamp: str
    model_type: str
    params: dict
    sharpe_gross: float
    sharpe_net: float
    max_dd: float
    fold_std: float
    git_commit: str
    seed: int
    notes: str
```

---

## SECTION 4 — JSONL LOGGER IMPLEMENTATION (16:00–24:00)

```python
import json
from pathlib import Path

class ExperimentTracker:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, record: dict):
        with self.path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(record, default=str) + '\n')

    def load_all(self):
        if not self.path.exists():
            return []
        with self.path.open('r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]
```

Query utility:

```python
def filter_runs(runs, min_sharpe=1.0, max_dd=-0.25):
    return [r for r in runs
            if r['sharpe_net'] >= min_sharpe and r['max_dd'] >= max_dd]
```

[INFORMATION GAIN] JSONL is underrated for solo quant research: append-only, diff-friendly, grep-friendly, and easy to parse without database overhead.

---

## SECTION 5 — RESEARCH JOURNAL LAYER (24:00–31:00)

Tracker stores metrics. Journal stores reasoning.

Template:

```markdown
# Week N
## Hypothesis
## What changed
## Result summary
## Failure analysis
## Decision
## Next test
```

[INFORMATION GAIN] Most edge comes from disciplined negative learning: what failed and why. Metrics alone do not capture this.

---

## SECTION 6 — REPRODUCIBILITY CHECKLIST (31:00–36:00)

Every run must include:
- git commit hash
- data snapshot identifier
- config hash
- random seed
- package versions

```python
import hashlib

def config_hash(cfg: dict):
    s = json.dumps(cfg, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()[:12]
```

---

## SECTION 7 — CLOSE (36:00–40:00)

Experiment tracking turns "I think this is better" into "here is the evidence and exact run to reproduce." That is professional research behavior.

Next video: factor analysis, where we decompose strategy returns to see what is true alpha vs factor exposure.

---

## Information Gain Score

**Score: 8/10**

Practical value from schema design, append-only logging strategy, and reproducibility controls.

**Before filming, add:**
1. Your actual tracker file sample
2. One failed experiment with full audit trail
3. Weekly journal snippet with decision outcome
