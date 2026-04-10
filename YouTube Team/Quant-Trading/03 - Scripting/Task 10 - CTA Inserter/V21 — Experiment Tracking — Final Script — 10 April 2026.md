# V21 — Experiment Tracking — Final Script

**Title:** Systematic Experimentation: How to Track 1000 Backtests
**Target Length:** 25-35 minutes
**Date:** 10 April 2026

---

## SECTION 1 — THE HOOK (0:00–2:00)

After 3 months of research I had tested over 200 model configurations across 14 architectures. Different hyperparameters, different feature sets, different training windows. And I could not remember which combination produced the best Sharpe, what learning rate I had used for the LSTM that worked in fold 3, or why I had abandoned XGBoost two weeks earlier.

[INFORMATION GAIN] I built an ExperimentTracker backed by JSON-lines storage that logs every single run with its full configuration, all metrics, research notes, artifact paths, and the git commit hash at the time of the run. Now I can reproduce any experiment from any point in the research process. I can compare runs side by side. I can filter by module, model type, or tag. And I can export a complete research journal that documents every decision. The tracker has prevented me from re-running the same failed experiment at least 4 times — saving roughly 20 hours of compute and my sanity.

---

## SECTION 2 — WHY TRACKING MATTERS (2:00–8:00)

Quant research without experiment tracking is like cooking without writing down recipes. You might make something great once but you cannot reliably reproduce it or build on it.

Let me describe three specific failure modes I encountered before building the tracker.

The irreproducibility problem. I found a configuration that gave Sharpe 1.4 on fold 2. I was excited. I tweaked the feature set to explore a variation. Two days later I wanted to go back to the 1.4 configuration and could not. I had changed three things since then — the feature list, the lookback window, and the dropout rate — and I could not remember the exact combination. I spent 6 hours trying to reproduce it. I never did.

The rediscovery problem. I spent two weeks testing an LSTM variant with attention layers. The Sharpe was 0.5, which was mediocre. I abandoned it and moved on. Three months later, I had an idea: what if I added attention to the LSTM? I spent another week implementing and testing essentially the same thing I had already tried and rejected. If I had a log saying LSTM plus attention equals Sharpe 0.5, tried and failed, I would have skipped it immediately.

The comparison problem. Which is better: LSTM with 64 hidden units and learning rate 0.001, or LSTM with 128 hidden units and learning rate 0.0005? Without structured logs, the answer came from scattered Jupyter notebook cells, mental notes, and occasionally a screenshot. Not reproducible, not reliable, not scalable.

[INFORMATION GAIN] Professional quant teams log every experiment by default. At firms like Renaissance Technologies, Two Sigma, and DE Shaw, every model variant ever tested is stored with its configuration and results. This is not bureaucracy. It is competitive advantage. The accumulated experiment history becomes a searchable knowledge base that prevents redundant work, enables systematic exploration, and lets new team members understand the full research history in hours instead of months.

---


[CTA 1]
If you want to set up experiment tracking for your own system, the free starter pack has the Run dataclass spec, the query patterns, and the comparison dashboard template. In the description.

## SECTION 3 — THE RUN AND EXPERIMENTTRACKER CLASSES (8:00–18:00)

The implementation lives in `src/m9_experiment/tracker.py`. There are two core components: Run objects and the ExperimentTracker that manages them.

A Run represents a single experiment. It is a dataclass with these fields:

```python
@dataclass
class Run:
    run_id: str          # auto-incremented: "run-0001"
    name: str            # descriptive: "lstm_momentum_ablation"
    module: str          # which phase: "m1_forecasting"
    model: str           # architecture: "LSTM"
    config: dict         # all hyperparameters
    tags: list[str]      # labels: ["ablation", "lstm"]
    metrics: dict        # results logged during run
    notes: list[str]     # research observations
    artifacts: dict      # paths to saved files
    start_time: str      # ISO timestamp
    end_time: str | None
    status: str          # "running", "completed", "failed"
```

The config dictionary stores every parameter that defines the experiment: hidden_size, learning_rate, dropout, batch_size, training_window, feature_list, target variable, walk-forward fold IDs. This is the complete recipe. With the config plus the git commit hash, you can reproduce the run exactly.

Key Run methods:

```python
def log_metric(self, key: str, value: float):
    """Add a single metric."""
    self.metrics[key] = value

def log_metrics(self, metrics: dict):
    """Add multiple metrics at once."""
    self.metrics.update(metrics)

def add_note(self, text: str):
    """Record a research insight."""
    self.notes.append(f"[{datetime.now().isoformat()}] {text}")

def add_artifact(self, name: str, path: str):
    """Link a saved model, plot, or data file."""
    self.artifacts[name] = str(path)

def end(self, status: str = "completed"):
    """Finalize the run and save."""
    self.status = status
    self.end_time = datetime.now().isoformat()
```

The ExperimentTracker manages persistence using JSON-lines format — one JSON object per line in `experiments.jsonl`. This format has three crucial properties. It is append-only: new runs are appended to the end of the file. It is human-readable: you can open the file in any text editor and read the runs. And it is crash-safe: each line is independently parseable, so if the process crashes mid-write, you lose at most one run, not the entire history.

```python
class ExperimentTracker:
    def __init__(self, store_path: str = "experiments.jsonl"):
        self.store_path = Path(store_path)
        self._run_counter = self._count_existing_runs()

    def start_run(
        self,
        name: str,
        module: str,
        model: str,
        config: dict,
        tags: list[str] | None = None,
    ) -> Run:
        self._run_counter += 1
        run = Run(
            run_id=f"run-{self._run_counter:04d}",
            name=name,
            module=module,
            model=model,
            config=config,
            tags=tags or [],
            metrics={},
            notes=[],
            artifacts={},
            start_time=datetime.now().isoformat(),
            end_time=None,
            status="running",
        )
        return run
```

[INFORMATION GAIN] Why JSON-lines instead of a database like SQLite or a cloud service like MLflow? Because the overhead matters. Setting up MLflow requires a server, network configuration, and authentication. SQLite requires schema design and migration management. JSON-lines requires nothing — it is a flat text file. For a solo researcher or a small team, the simplicity of JSONL outweighs any scalability concern. I have 400 runs in my file and it loads into a DataFrame in 200 milliseconds. The simplicity of the format also means I can grep through it, pipe it to jq, or read it on any machine without installing dependencies.

---

## SECTION 4 — QUERYING AND COMPARING RUNS (18:00–26:00)

The `to_dataframe()` method loads all completed runs into a pandas DataFrame where each row is a run and columns include all fields plus flattened metrics:

```python
def to_dataframe(self) -> pd.DataFrame:
    """Load all completed runs as a DataFrame for analysis."""
    runs = self._load_all()
    rows = []
    for run in runs:
        row = {
            "run_id": run.run_id,
            "name": run.name,
            "module": run.module,
            "model": run.model,
            "status": run.status,
            "start_time": run.start_time,
        }
        row.update(run.config)    # flatten config
        row.update(run.metrics)   # flatten metrics
        rows.append(row)
    return pd.DataFrame(rows)
```

This is where the power emerges. With 200 runs as a DataFrame, you can sort by Sharpe descending and instantly see the best configuration. You can filter to a specific module: `df[df.module == "m1_forecasting"]`. You can group by model type and compute the average Sharpe per architecture to see which family of models works best. You can scatter plot learning_rate versus Sharpe to visualise the hyperparameter landscape.

The `filter_runs()` method provides shorthand for common queries:

```python
def filter_runs(
    self,
    module: str | None = None,
    model: str | None = None,
    tags: list[str] | None = None,
    status: str = "completed",
) -> list[Run]:
```

And the `compare()` method generates a formatted side-by-side comparison:

```python
def compare(self, run_ids: list[str], metrics: list[str] | None = None) -> pd.DataFrame:
    """Side-by-side comparison of specific runs."""
```

Here is a typical workflow. I just finished a hyperparameter sweep: 9 runs of LSTM with 3 hidden sizes times 3 learning rates. I want the comparison table.

```python
tracker = ExperimentTracker()
df = tracker.to_dataframe()
lstm_runs = df[df.model == "LSTM"].sort_values("sharpe", ascending=False)
top_3 = lstm_runs.head(3).run_id.tolist()
comparison = tracker.compare(top_3, metrics=["sharpe", "sortino", "max_drawdown", "training_time"])
```

The output: a clean table showing run-0042 (hidden=64, lr=0.001) with Sharpe 0.82, run-0045 (hidden=128, lr=0.0005) with Sharpe 0.76, and run-0039 (hidden=32, lr=0.001) with Sharpe 0.68. Decision: 64 hidden units at 0.001 learning rate is the sweet spot.

[INFORMATION GAIN] The `add_note` method is often more valuable than the metrics. I have a rule: every run with unexpected results — good or bad — gets a note explaining the likely reason. Three months from now I will not remember why 128 hidden units with learning rate 0.01 produced Sharpe negative 0.3. The note I wrote at the time — "diverged during training, gradient explosion with clip=1.0, lr too high for this architecture" — saves me from re-running the same failed experiment. Notes accumulate into institutional knowledge.

---


[CTA 2]
The experiment tracking setup guide is in the free starter pack. Link in the description.

## SECTION 5 — ABLATION STUDIES WITH THE TRACKER (26:00–32:00)

Ablation studies test the marginal contribution of each pipeline component. The tracker supports this through the tags and comparison workflow.

The ablation from video 13 tested 4 configurations: M1 only (forecasting without gates), M1 plus M2 (add meta-label gating), M1 plus M2 plus M3 (add sentiment overlay), and full pipeline (add vol-targeted sizing from M5). Each configuration is a run with a specific tag.

```python
# Parent configuration
configs = [
    {"name": "M1_only", "modules": ["M1"], "tags": ["ablation"]},
    {"name": "M1_M2", "modules": ["M1", "M2"], "tags": ["ablation"]},
    {"name": "M1_M2_M3", "modules": ["M1", "M2", "M3"], "tags": ["ablation"]},
    {"name": "full_pipeline", "modules": ["M1", "M2", "M3", "M5"], "tags": ["ablation"]},
]

for cfg in configs:
    run = tracker.start_run(
        name=cfg["name"], module="pipeline",
        model="ensemble", config=cfg, tags=cfg["tags"]
    )
    result = run_pipeline(cfg["modules"])
    run.log_metrics(result)
    run.add_note(f"Ablation: active modules = {cfg['modules']}")
    run.end()
```

The ablation comparison table:

M1 only: Sharpe 0.52. M1 plus M2: Sharpe 0.67 (plus 0.15). M1 plus M2 plus M3: Sharpe 0.70 (plus 0.03). Full pipeline: Sharpe 0.78 (plus 0.08).

The incremental Sharpe column reveals exactly where value is created. M2, the meta-label confidence gate, provides the largest marginal improvement at plus 0.15. This makes sense — filtering out low-confidence trades prevents many losing trades while keeping high-confidence winners. M3, the sentiment overlay, adds only 0.03 — most of the information was already captured by the directional forecast. M5, volatility-targeted position sizing, adds 0.08 — managing risk adds as much value as a forecasting improvement.

[INFORMATION GAIN] Ablation studies are the most underrated technique in quant research. Most researchers add components and test only the final result. They do not know which component actually helps. I have seen systems where removing one module increased Sharpe because the module was adding noise, not signal. The module passed a standalone backtest but degraded the ensemble. Without ablation, you would never discover this — you would be carrying dead weight that increases complexity without adding value.

The `best_run()` method finds the top performer:

```python
def best_run(self, metric: str = "sharpe", higher_is_better: bool = True) -> Run:
    """Find the run with the best value of the specified metric."""
```

And the `export_journal()` method generates a complete Markdown research summary:

```python
def export_journal(self, path: str | None = None) -> str:
    """Generate Markdown research journal grouped by module."""
```

---

## SECTION 6 — THE RESEARCH JOURNAL AND REPRODUCIBILITY (32:00–38:00)

The `export_journal()` method creates a permanent record of all research decisions. The output is a Markdown file grouped by module with every run, its metrics, and its notes. Example excerpt:

```markdown
## Module: m1_forecasting

### run-0001: LSTM (hidden=64, lr=0.001)
- Sharpe: 0.82 | Sortino: 1.12 | Max DD: -15.3%
- Note: sweet spot config — smaller hidden sizes undertrained,
  larger overfitted on this dataset size
- Note: learning rate 0.001 optimal — 0.01 causes gradient explosion

### run-0002: LSTM (hidden=128, lr=0.01)
- Sharpe: -0.30 | Sortino: -0.41 | Max DD: -38.2%
- Note: diverged during training — lr too high with gradient clip at 1.0
- Status: FAILED

### run-0015: TiDE (hidden=64)
- Sharpe: 0.91 | Sortino: 1.34 | Max DD: -12.1%
- Note: best overall forecaster — temporal fusion approach captures
  both short and long patterns
```

This journal serves multiple purposes. For you: it is a searchable reference of everything you tried and learned. For collaborators: it is an onboarding document that explains the full research history. For reproducibility: every run stores the git commit hash, so checking out that commit plus loading the stored config exactly recreates the experiment.

The git integration:

```python
import subprocess
git_hash = subprocess.check_output(
    ["git", "rev-parse", "HEAD"]
).decode().strip()
run.config["git_commit"] = git_hash
```

Every run automatically captures the code state. If you need to reproduce run-0015: checkout the commit, load the config, and run. No guessing about which version of the feature engineering code was active, which preprocessing step was applied, or which training window was used.

[INFORMATION GAIN] The tracker enables a meta-analysis that most researchers never do: trend plotting. Compute the best Sharpe per week across all runs. Plot it over time. If the Sharpe is trending upward over 3 months, your research is making progress — you are learning from each experiment and converging on better configurations. If the Sharpe is flat for 3 or more weeks despite daily experiments, you are going in circles — tweaking hyperparameters without structural improvement. That is the signal to change direction entirely: try a different architecture, different features, or different target definition. Without the tracker, you cannot see this trend because you do not have the historical data to compute it.

---

## SECTION 7 — THE CLOSE (38:00–40:00)

Experiment tracking converts ad-hoc research into systematic knowledge accumulation. Every run is logged, every insight is captured, every result is reproducible. The ExperimentTracker backed by JSON-lines is lightweight — no database, no server, no authentication — but powerful enough to manage hundreds of experiments.

Three numbers from this video. 200 experiments tracked in 3 months of research. 4 redundant experiments prevented, saving roughly 20 hours of compute. And 200 milliseconds to load all 400 runs into a DataFrame for analysis.

Next video: factor analysis. Your strategy returns 15 percent annually. But how much of that is genuine alpha versus exposure to well-known risk factors like market beta, size, and value? We decompose the returns using a 5-factor model and find out whether the edge is real or just factor exposure in disguise.

---

## Information Gain Score

**Score: 7/10**

Strong on the practical failure modes (irreproducibility, rediscovery, comparison), the JSONL simplicity argument, the ablation workflow, and the research trend analysis insight. The code walkthroughs show the full API surface.

**Before filming, add:**
1. Your actual experiments.jsonl content — scroll through real run entries on screen
2. A live demo of the comparison table for your top 3 forecasting models
3. The exported Markdown journal — scroll through it showing the accumulated knowledge
4. The research progress trend chart (best Sharpe per week over 3 months)
