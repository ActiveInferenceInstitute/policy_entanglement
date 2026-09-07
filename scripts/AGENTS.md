# AGENTS.md — `scripts/`

**Publication:** DOI https://doi.org/10.5281/zenodo.20418904 · claim matrix [`../docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv`](../docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv)

## Thin-orchestrator contract

Every script in this directory is a **thin orchestrator**: argparse +
shared path bootstrap + a single delegated call into a
[`../src/`](../src/) entrypoint. All business, data, plot, and analysis
logic lives in `src/` (importable and tested); a script's only
logic-bearing layer is the delegation itself:

```python
results = src_module.compute(...)
plt.plot(results)
plt.savefig(out)
print(out)
```

The rules:

1. **No business logic.** If a function does math, it belongs in
   [`../src/`](../src/), not here.
2. **One script = one workflow.** Don't bundle independent workflows
   into a single script. If you'd run them at different cadences, they
   should be different scripts.
3. **Return / print output paths.** The pipeline collects manifest
   entries by reading stdout. Print one path per line, no commentary.
4. **Headless matplotlib.** Set `MPLBACKEND=Agg` before importing
   `pyplot`.
5. **Deterministic outputs.** Fix seeds; don't use `time` or process
   IDs in filenames.
6. **Output paths under `../output/`.** This directory is disposable;
   never write into `src/`, `tests/`, or `docs/manuscript/`.

## Script inventory (current)

Roster order mirrors the canonical pipeline in
`src/orchestration/stages.py::SCRIPTS`, then release extras, then
standalone scripts.

| Script | Stage | Delegates to | What it does |
|---|---|---|---|
| `build_lean.py` | Lean | `lean.build_gate` | `lake build` + sorry / axiom / unsafe budget gate |
| `generate_figures.py` | figures | `visualizations.analytical_figures` | 15 analytical PNGs (incl. coupling-potential graph) |
| `dump_archetypes.py` | data | `lean.spectral`, `lean.bernoulli_toy` | Schmidt-archetype CSV |
| `parameter_sweep.py` | data | `simulation.parameter_sweep` | configurable closed-form λ sweep — CLI-overridable grid, utilities, phase thresholds (defaults reproduce the canonical sweep) |
| `simulate_pymdp.py` | sim + figures | `simulation.pymdp_pipeline`, `visualizations.pymdp_figures` | pymdp 1.0.1 run → 14 PNGs + 2 CSVs + summary JSON (lambda sweep, rollout, free-energy bundle, and dashboards) |
| `simulate_multi_k.py` | sim + figures | `simulation.multi_k_pipeline` | configured multi-stream sweep → per-K CSV + 3 PNGs + JSON summary |
| `simulate_long_horizon.py` | sim + figures | `simulation.long_horizon_pipeline` | configured habit-accumulation rollout → CSV + 2 PNGs + JSON summary |
| `simulate_revertibility.py` | sim + figures | `simulation.revertibility_pipeline` | m-projection witness (Prop 7.3 / Theorem 5.1) → CSV + PNG + JSON summary |
| `simulate_robustness.py` | sim + figures | `simulation.robustness_runner` | robustness, ablation, and replicate sidecars → CSVs, PNGs, and JSON summaries for one-axis, two-axis, ablation, and long-horizon diagnostics |
| `simulate_btai.py` | sim + figures | `visualizations.btai_plots` | shipped BTAI baseline worked run → `btai_baseline.json` + PNG |
| `simulate_adversarial.py` | sim + figures | `visualizations.adversarial_plots` | adversarial-perturbation (ε, λ) grid sweep → JSON + PNG |
| `simulate_gnn.py` | sim + figures | `gnn.runner` | GNN fifth-track round-trip: reconstructs the K=2 Bernoulli/Ising MI curve from `gnn/bernoulli_toy.gnn.md` → JSON sidecar + PNG + emitted Lean contract |
| `manuscript_variables.py` | data | `manuscript.variables` | numeric mirror → `output/data/manuscript_variables.json` |
| `build_dashboard.py` | sim + web | `dashboard_types.dashboard` | interactive multi-view Plotly dashboard at `output/web/dashboard.html` (six panels, three live controls), companion plaintext `output/reports/dashboard_invariants.txt` + `output/reports/dashboard_summary.txt` + `output/data/dashboard_payload.json`. Every grid / utility / threshold is a CLI flag; exits non-zero on any invariant failure. |
| `generate_index.py` | manuscript | `manuscript.index_generator` | regenerate `docs/manuscript/INDEX.md` from registry |
| `generate_theorem_map.py` | manuscript | `manuscript.theorem_map` | regenerate `docs/reference/_theorem_map.md` four-track wiring table |
| `inject_manuscript_variables.py` | manuscript | `manuscript.renderer` (+ `manuscript.registry`, `manuscript.bibliography`) | resolve every `[[…]]` token, auto-number every `$$…$$` |
| `validate_outputs.py` | gate | `manuscript.output_gates` | thin CLI → `manuscript.output_gates/` package |
| `validate_manuscript.py` | gate | `manuscript.validation_cli` | tokens / citations / links / hardcoded refs / numeric ranges |
| `regression_gate.py` | gate | `gates.regression_gate` | compares current run metrics against `regression_baseline.json` |
| `build_pdf.py` | PDF (release extra) | `orchestration.build_pdf` | standalone combined PDF render wrapper |
| `validate_pdf.py` | gate (release extra) | `manuscript.pdf_validation` | PDF text / TeX / LaTeX log / margin validation |
| `readiness_report.py` | report (release extra) | `manuscript.readiness` | writes reviewer-facing release-readiness Markdown/JSON plus a small release index under `output/reports/` |
| `build_mathlib_proofs.py` | Lean (release extra) | `lean.mathlib_proofs_gate` | optional additive `lean/MathlibProofs/` build + hygiene audit |
| `gnn_to_pymdp.py` | standalone | `gnn.parser`, `gnn.bridge` | emits the pymdp-style harness configuration (streams, policy cardinalities, habit priors, coupling tensor) as JSON from a `.gnn` source file |
| `check_concordance.py` | standalone | self-contained (no `src/` import) | report-only four-track concordance coherence check |
| `generate_audit_matrix.py` | standalone | `manuscript.audit_matrix` | regenerate `docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv` claim ledger (`--write` / `--check`) |

Non-script members of this directory: `_bootstrap.py` (shared
`ensure_project_paths` helper imported by every other script) and
`regression_baseline.json` (committed gate baseline consumed by
`regression_gate.py`).

## Pipeline tail order

`run_all.py` runs the canonical `SCRIPTS` order and the **default
pipeline ends with `regression_gate.py`**. Release extras do not
change that tail: `--with-pdf` inserts `build_pdf.py` and
`validate_pdf.py` before `regression_gate.py`, then appends
`readiness_report.py` after regression; `--with-mathlib` adds the
optional MathlibProofs build after the boundary Lean gate.

## Adding a script

1. Create `scripts/<verb>_<noun>.py` (e.g. `generate_figures.py`,
   `compute_archetype_table.py`).
2. Top-of-file boilerplate (prefer the shared bootstrap):
   ```python
   import os, sys
   from pathlib import Path
   os.environ.setdefault("MPLBACKEND", "Agg")
   THIS_DIR = Path(__file__).resolve().parent
   PROJECT_ROOT = THIS_DIR.parent
   sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
   from _bootstrap import ensure_project_paths  # noqa: E402
   ensure_project_paths(project_root=PROJECT_ROOT)
   ```
   Every analysis script uses this bootstrap. Sole exception:
   `check_concordance.py` (self-contained text scanner with no `src/`
   imports). `run_all.py` and `regression_gate.py` are thin wrappers
   that bootstrap + re-export
   :mod:`orchestration.run_all` / :mod:`gates.regression_gate` from
   `../src/` (business logic lives there).
3. Imports go after the `sys.path` insert (use `# noqa: E402`).
4. End with `if __name__ == "__main__": main()`.
5. Update [`README.md`](README.md) with the new script's row, and add
   the script to this inventory table. A script missing from either
   file breaks the roster-completeness contract.

## Common workflows

| Want to … | Edit |
|---|---|
| add a manuscript figure | `generate_figures.py` (or `simulate_pymdp.py` for pymdp-grounded ones) |
| compute in-text variables | `manuscript_variables.py` |
| publish a CSV table | new script `compute_<table>.py` writing to `../output/data/` |
| change a grid / seed / rollout horizon | edit [`../src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py); scripts read from there |
| run the full pipeline end-to-end | `run_all.py` (canonical `SCRIPTS` order, exits non-zero on any failure) |
| run release PDF gates | `build_pdf.py` then `validate_pdf.py`, or `run_all.py --with-pdf` |
| check optional MathlibProofs scaffold | `build_mathlib_proofs.py`, or `run_all.py --with-mathlib` for release-manifest recording |
| validate every artifact | `validate_outputs.py` (thin CLI → `manuscript.output_gates`) |
| validate manuscript completeness | `validate_manuscript.py` (tokens, citations, links, hardcoded refs, numeric ranges) |
| render manuscript with auto-numbered eqs | `inject_manuscript_variables.py` |

## Gotchas

* The pipeline parses script stdout for manifest paths — keep printed
  output path-only (no logs / debug commentary mixed in).
* `../output/` is disposable and regenerated; never hand-edit it and
  never commit transient outputs from it.
* Re-exports at script module level (`run_all.py`,
  `regression_gate.py`, `manuscript_variables.py`,
  `simulate_adversarial.py`, `simulate_btai.py`,
  `generate_theorem_map.py`, `readiness_report.py`,
  `build_dashboard.py`) exist because tests import the scripts as
  modules and assert on those names — keep them stable.
* `scripts/regression_baseline.json` is committed state consumed by
  the regression gate; regenerate it deliberately, never as a side
  effect of a normal run.

## Template monorepo integration

When this project is symlinked under `template/projects/`:

* **Analysis allowlist:** `docs/manuscript/config.yaml` → `analysis.scripts: [run_all.py]` so stage 4 does not run every script lexicographically.
* **Tests-before-analysis:** template stage 3 runs before stage 4; `conftest.py` bootstraps missing `output/` artifacts idempotently.
* **PDF:** use `run_all.py --with-pdf` (or `make pipeline-pdf`) — not `scripts/03_render_pdf.py`, which bypasses the registry injector.
* **Copy outputs:** after `--with-pdf`, template stage 9 copies `projects/.../output/` → root `output/pdf/` (combined PDF at `output/pdf/actinf_policy_entanglement_lean_combined.pdf`).

## Anti-patterns

* Hard-coding numerical computations inline (do them in `src/`).
* Writing intermediate `.npy` files into the project tree (use
  `tmp_path` or `output/`).
* Printing logs / debug output mixed with output paths (the
  pipeline parses stdout — keep it path-only).
* Adding a script without updating both [`README.md`](README.md) and
  this inventory.
