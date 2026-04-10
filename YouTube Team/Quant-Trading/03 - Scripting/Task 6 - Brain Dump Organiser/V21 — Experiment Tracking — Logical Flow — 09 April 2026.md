# V21 — Experiment Tracking — Logical Flow — 09 April 2026

**Title:** Systematic Experimentation: How to Track 1000 Backtests
**Target Length:** ~40 minutes

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** After 3 months of research, I had tested 200+ model configurations across 14 architectures. Different hyperparameters, different feature sets, different training windows. And I could not remember which combination produced the best Sharpe, what learning rate I used for the LSTM that worked in fold 3, or why I abandoned XGBoost two weeks ago. I built an ExperimentTracker backed by JSON-lines that logs every single run with its config, metrics, notes, and git commit hash. Now I can reproduce any experiment from any point in the research process and compare runs side by side.

## 2. WHY TRACKING MATTERS (2:00–8:00)

Quant research without experiment tracking is like cooking without writing down recipes. You might make something great once, but you cannot reliably reproduce it or build on it.

The specific failure modes I encountered before building the tracker: First, the irreproducibility problem. I found a configuration that gave Sharpe 1.4 on fold 2. Two days later I tried to recreate it and could not — I had changed the feature set in between and forgotten which version I used. Second, the rediscovery problem. I spent two weeks testing an LSTM variant, abandoned it because the Sharpe was mediocre, forgot about it, and then spent another week testing essentially the same thing three months later. Third, the comparison problem. Which is better: LSTM with 64 hidden units and 0.001 learning rate, or LSTM with 128 hidden units and 0.0005 learning rate? Without structured logs, you are relying on memory and scattered notebook outputs.

**[INFORMATION GAIN]** Professional quant teams track every experiment by default. At Renaissance Technologies, every model variant ever tested is logged with its configuration and results. This is not bureaucracy — it is competitive advantage. The accumulated experiment history becomes a knowledge base that prevents redundant work and enables systematic exploration. My ExperimentTracker is a simplified version of what production quant firms use (MLflow, Weights & Biases, custom internal tools).

## 3. THE EXPERIMENTTRACKER CLASS (8:00–18:00)

The implementation in `src/m9_experiment/tracker.py` has two core components: Run objects and the ExperimentTracker.

A Run represents a single experiment. It has: run_id (auto-incremented like "run-0001"), name (descriptive label like "lstm_momentum_ablation"), module (which phase, e.g., "m1_forecasting"), model (architecture, e.g., "LSTM"), config (dictionary of all hyperparameters), tags (list of labels like ["ablation", "lstm"]), metrics (dictionary of results), notes (list of research observations), artifacts (paths to saved files), timestamps (start, end), and status (running, completed, failed).

Key Run methods: `log_metric(key, value)` adds a metric. `log_metrics(dict)` adds multiple. `add_note(text)` records a research insight. `add_artifact(name, path)` links a saved model or plot. `end(status)` finalizes and persists the run.

The ExperimentTracker manages persistence. All runs are stored as JSON-lines (one JSON object per line) in `experiments.jsonl`. This format is append-only, human-readable, and survives crashes (each line is independently parseable).

Key Tracker methods: `start_run(name, module, model, config, tags)` creates and returns a Run. `to_dataframe()` loads all completed runs into a pandas DataFrame for analysis. `filter_runs(module, model, tags)` returns a subset. `compare(run_ids, metrics)` shows side-by-side comparison. `best_run(metric, higher_is_better)` finds the top performer. `export_journal(path)` generates a Markdown research summary grouped by module.

## 4. STRUCTURED WORKFLOW EXAMPLE (18:00–26:00)

Here is how a typical research session looks with the tracker:

Phase 1 — Hyperparameter sweep for LSTM forecasting. Start 9 runs: 3 hidden sizes (32, 64, 128) × 3 learning rates (0.0001, 0.001, 0.01). Each run logs: model name, hidden_size, learning_rate, dropout, training_loss, validation_loss, out-of-sample Sharpe, out-of-sample MAE, training time, git commit hash.

After the sweep, `tracker.to_dataframe()` gives a table where each row is a run and columns include all metrics. Sort by Sharpe descending. The best combination: 64 hidden units, 0.001 learning rate, Sharpe 0.82. The worst: 128 hidden units, 0.01 learning rate, Sharpe -0.3 (diverged during training).

Add a note to the best run: "64 hidden units sweet spot — smaller undertrained, larger overfitted on small dataset. Learning rate 0.01 causes divergence with gradient clipping at 1.0."

**[INFORMATION GAIN]** The note is often more valuable than the metric. Three months from now, you will not remember why 128 hidden units failed. The note saves you from re-running the same failed experiment. I have a rule: every run with unexpected results (good or bad) gets a note explaining why. The notes accumulate into institutional knowledge.

## 5. ABLATION STUDIES WITH NESTED RUNS (26:00–32:00)

Ablation studies test the marginal contribution of each component. The tracker supports nested runs via the `parent_run` field.

Example: the module ablation from V13. Parent run: "full_pipeline_ablation". Child runs: "M1_only", "M1_M2", "M1_M2_M3", "full_pipeline". Each child run logs: which modules are active, the resulting Sharpe, max drawdown, and turnover.

The comparison table shows incremental improvement:
- M1 only: Sharpe 0.52
- M1 + M2 (meta-label gate): Sharpe 0.67 (+0.15)
- M1 + M2 + M3 (sentiment overlay): Sharpe 0.70 (+0.03)
- Full pipeline (vol-targeted sizing): Sharpe 0.78 (+0.08)

The nested structure lets you see that M2 (meta-label confidence gating) provides the most marginal value. Sentiment adds little. Volatility-targeted position sizing provides the second-largest improvement by managing risk.

**[INFORMATION GAIN]** Ablation studies are the most underrated technique in quant research. Most researchers add components and test the final result. They do not know which component actually helps. I have seen systems where removing one module increased Sharpe because the module was adding noise, not signal. Without ablation, you never discover this.

## 6. REPRODUCING AND EXPORTING (32:00–38:00)

Every run stores the git commit hash via `git rev-parse HEAD` at start time. This means: to reproduce any experiment exactly, check out the stored commit, load the stored config, and run. No guessing about code versions.

The `export_journal()` method generates a Markdown file grouped by module with all runs, metrics, and notes. Example output:

Module: m1_forecasting
- run-0001: LSTM, hidden=64, lr=0.001, Sharpe=0.82, note: sweet spot config
- run-0002: LSTM, hidden=128, lr=0.01, Sharpe=-0.3, note: diverged, lr too high
- run-0003: TiDE, hidden=64, Sharpe=0.91, note: best overall forecaster

This journal is a persistent record of all research decisions. You can share it with collaborators, reference it in publications, or use it to onboard someone new to the project.

The `compare()` method produces a formatted table comparing 2-5 specific runs on selected metrics. This is useful for final model selection: compare the top 3 candidates on Sharpe, Sortino, max drawdown, and training time to make an informed choice.

**[INFORMATION GAIN]** The tracker also enables trend analysis across time. By plotting Sharpe ratio of the best run per week over 3 months, you can see whether your research is making progress (Sharpe trending up) or going in circles (Sharpe flat). If flat for 3+ weeks, it is time to change direction entirely — not tweak hyperparameters.

## 7. THE CLOSE (38:00–40:00)

Experiment tracking converts ad-hoc research into systematic knowledge accumulation. Every run is logged, every insight is captured, every result is reproducible. The ExperimentTracker backed by JSON-lines is lightweight (no database, no server) but powerful enough to manage hundreds of experiments without losing anything.

Next video: factor analysis. Your strategy returns 15% annually. But where does that return come from? We decompose it into market beta, size factor, value factor, momentum, and the residual alpha that is genuinely your edge.

[NEEDS MORE] Your actual experiments.jsonl with real run data. The Markdown journal export. A screenshot of the comparison table for your top 3 models.
