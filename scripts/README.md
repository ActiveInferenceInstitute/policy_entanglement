# `scripts/` — Thin orchestrators

Per the template's *thin orchestrator* pattern, every script in this
directory:

1. Bootstraps project paths via the shared `_bootstrap.py` helper.
2. Delegates all compute to a `src/` entrypoint (business logic never
   lives here).
3. Handles I/O (file writes, plotting, JSON serialization) and prints
   output paths to stdout, one per line, for the pipeline manifest.

Scripts must not implement algorithms. See
[`AGENTS.md`](AGENTS.md) for the contract and
[`../AGENTS.md`](../AGENTS.md) for the constitution.

## Files

Inventory table order mirrors the canonical pipeline in
`src/orchestration/stages.py::SCRIPTS`, then release extras, then
standalone scripts and helpers.

| Script | Purpose | Delegates to | Run command |
|---|---|---|---|
| [`build_lean.py`](build_lean.py) | `lake build` + sorry / axiom / unsafe budget gate | `lean.build_gate` | `uv run python scripts/build_lean.py` |
| [`generate_figures.py`](generate_figures.py) | Renders all 15 analytical manuscript figures (+ optional coupling graph) | `visualizations.analytical_figures` | `uv run python scripts/generate_figures.py` |
| [`dump_archetypes.py`](dump_archetypes.py) | Dumps K=2 Schmidt archetypes at a λ-sweep | `lean.spectral`, `lean.bernoulli_toy` | `uv run python scripts/dump_archetypes.py` |
| [`parameter_sweep.py`](parameter_sweep.py) | Closed-form sweep (MI, FE, rank, entropy, phase); CLI-overridable grid, defaults = canonical sweep | `simulation.parameter_sweep` (grid from `simulation.hyperparameters`) | `uv run python scripts/parameter_sweep.py` |
| [`simulate_pymdp.py`](simulate_pymdp.py) | pymdp 1.0.1 POMDP run: λ-sweep + rollout + free-energy bundle | `simulation.pymdp_pipeline`, `visualizations.pymdp_figures` | `uv run python scripts/simulate_pymdp.py` |
| [`simulate_multi_k.py`](simulate_multi_k.py) | Configured multi-stream ensemble sweep (per-K λ-sweep, TT-rank profile, aligned mass) | `simulation.multi_k_pipeline` | `uv run python scripts/simulate_multi_k.py` |
| [`simulate_long_horizon.py`](simulate_long_horizon.py) | Configured long-horizon coupled rollout (habit accumulation) | `simulation.long_horizon_pipeline` | `uv run python scripts/simulate_long_horizon.py` |
| [`simulate_revertibility.py`](simulate_revertibility.py) | m-projection back-to-mean-field witness (Prop 7.3 / Theorem 5.1 identity) | `simulation.revertibility_pipeline` | `uv run python scripts/simulate_revertibility.py` |
| [`simulate_robustness.py`](simulate_robustness.py) | Robustness, ablation, and long-horizon replicate sidecars | `simulation.robustness_runner` | `uv run python scripts/simulate_robustness.py` |
| [`simulate_btai.py`](simulate_btai.py) | Shipped BTAI baseline worked run over the registered MCTS budget grid | `visualizations.btai_plots` (compute in `simulation.btai_baseline`) | `uv run python scripts/simulate_btai.py` |
| [`simulate_adversarial.py`](simulate_adversarial.py) | Shipped adversarial-perturbation sweep over the registered (ε, λ) grid | `visualizations.adversarial_plots` (compute in `simulation.adversarial`) | `uv run python scripts/simulate_adversarial.py` |
| [`simulate_gnn.py`](simulate_gnn.py) | GNN fifth-track round-trip: reconstructs the K=2 Bernoulli/Ising MI curve from `gnn/bernoulli_toy.gnn.md` | `gnn.runner` | `uv run python scripts/simulate_gnn.py` |
| [`manuscript_variables.py`](manuscript_variables.py) | Computes every in-text `[[VAR:…]]` substitution; mirrors `simulation.hyperparameters` | `manuscript.variables` | `uv run python scripts/manuscript_variables.py` |
| [`build_dashboard.py`](build_dashboard.py) | Interactive multi-view Plotly dashboard + plaintext invariants + JSON payload | `dashboard_types.dashboard` | `uv run python scripts/build_dashboard.py` |
| [`generate_index.py`](generate_index.py) | Regenerates `docs/manuscript/INDEX.md` from the registry | `manuscript.index_generator` | `uv run python scripts/generate_index.py` |
| [`generate_theorem_map.py`](generate_theorem_map.py) | Auto-generates the per-theorem four-track wiring table | `manuscript.theorem_map` | `uv run python scripts/generate_theorem_map.py` |
| [`inject_manuscript_variables.py`](inject_manuscript_variables.py) | Resolves every `[[…]]` token, auto-numbers every `$$…$$` block | `manuscript.renderer` (+ `manuscript.registry`, `manuscript.bibliography`) | `uv run python scripts/inject_manuscript_variables.py` |
| [`validate_outputs.py`](validate_outputs.py) | Post-pipeline gate: PNGs / JSON / CSVs / free-energy bundle invariants | `manuscript.output_gates` | `uv run python scripts/validate_outputs.py` |
| [`validate_manuscript.py`](validate_manuscript.py) | Manuscript completeness gate: tokens / citations / links / hardcoded refs / numeric ranges | `manuscript.validation_cli` | `uv run python scripts/validate_manuscript.py` |
| [`regression_gate.py`](regression_gate.py) | Compares current run metrics against `regression_baseline.json` (test count, coverage, invariants, Lean hygiene) | `gates.regression_gate` | `uv run python scripts/regression_gate.py` |
| [`build_pdf.py`](build_pdf.py) | Renders the combined PDF with local Pandoc/XeLaTeX/BibTeX tooling (release extra) | `orchestration.build_pdf` | `uv run python scripts/build_pdf.py` |
| [`validate_pdf.py`](validate_pdf.py) | Release-PDF gate: PDF text / TeX / LaTeX log / margin validation (release extra) | `manuscript.pdf_validation` | `uv run python scripts/validate_pdf.py` |
| [`readiness_report.py`](readiness_report.py) | Reviewer-facing release-readiness Markdown/JSON + release index (release extra) | `manuscript.readiness` | `uv run python scripts/readiness_report.py` |
| [`build_mathlib_proofs.py`](build_mathlib_proofs.py) | Optional additive `lean/MathlibProofs/` build + hygiene audit (release extra) | `lean.mathlib_proofs_gate` | `uv run python scripts/build_mathlib_proofs.py` |
| [`gnn_to_pymdp.py`](gnn_to_pymdp.py) | Emits the pymdp-style harness configuration as JSON from a `.gnn` source file | `gnn.parser`, `gnn.bridge` | `uv run python scripts/gnn_to_pymdp.py [gnn/bernoulli_toy.gnn.md]` |
| [`check_concordance.py`](check_concordance.py) | Report-only four-track concordance coherence check | self-contained scanner over `src/`, `lean/`, and manuscript labels (no `src/` import) | `uv run python scripts/check_concordance.py` |
| [`generate_audit_matrix.py`](generate_audit_matrix.py) | Regenerates the claim-audit matrix CSV | `manuscript.audit_matrix` | `uv run python scripts/generate_audit_matrix.py --write` (or `--check`) |
| `_bootstrap.py` | Shared path bootstrap (`ensure_project_paths`); imported by every other script, never run directly | — | — |
| `regression_baseline.json` | Committed gate baseline consumed by `regression_gate.py`; not a script | — | — |

## Running

```bash
# from the project directory:
uv run python scripts/generate_figures.py
uv run python scripts/manuscript_variables.py
uv run python scripts/dump_archetypes.py
uv run python scripts/parameter_sweep.py

# Sanity-check the artifacts after the above ran:
uv run python scripts/validate_outputs.py

# Full dependency-ordered pipeline: Lean gate, figures, empirical
# producers, manuscript variables + injection, output/manuscript
# validation, ending with the regression gate:
uv run python scripts/run_all.py

# Full pipeline plus PDF rendering/validation and the readiness report:
uv run python scripts/run_all.py --with-pdf

# Full release pipeline plus optional MathlibProofs build:
uv run python scripts/run_all.py --with-pdf --with-mathlib
```

Every script is **idempotent** — running it again overwrites the
existing outputs.

## Orchestration placement

`run_all.py` is the canonical local CI shape. It keeps dependency
edges explicit:

1. Build and hygiene-check Lean before trusting theorem tables.
2. Render deterministic analytical figures.
3. Run write-isolated empirical producers in the parallel-eligible
   batch (`dump_archetypes.py` through `simulate_gnn.py`).
4. Compute manuscript variables after all empirical sidecar summaries
   exist.
5. Build dashboard/report artifacts and generated indexes.
6. Inject manuscript variables only after all data producers have run.
7. Validate output artifacts, validate manuscript references, then run
   the regression gate against the committed baseline — the default
   pipeline **ends with `regression_gate.py`**.
8. Release extras do not change that tail: `--with-pdf` inserts
   `build_pdf.py` and `validate_pdf.py` before the regression gate and
   appends `readiness_report.py` after it; `--with-mathlib` adds the
   optional `lean/MathlibProofs/` build after the boundary Lean gate.

For a reader-facing explanation of the same pipeline, see
[`../docs/reference/methods_orchestration.md`](../docs/reference/methods_orchestration.md).

## Adding a script

Follow [`AGENTS.md`](AGENTS.md) ("Adding a script"), and update the
inventory table above with the new script's row — every script in this
directory must have one.
