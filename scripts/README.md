# `scripts/` — Thin orchestrators

Per the template's *thin orchestrator* pattern, every script in this
directory:

1. Imports compute methods from [`../src/`](../src/).
2. Handles I/O (file writes, plotting, JSON serialisation).
3. Prints output paths to stdout, one per line, for the pipeline
   manifest.

Scripts must not implement algorithms.  See
[`../AGENTS.md`](../AGENTS.md) for the constitution.

## Files

| Script | What it does | Outputs |
|---|---|---|
| [`build_lean.py`](build_lean.py) | `cd lean && lake build` + sorry / axiom / unsafe budget gate | exit code 0 / 1 |
| [`build_mathlib_proofs.py`](build_mathlib_proofs.py) | Optional additive `lean/MathlibProofs/` scaffold build | exit code 0 / 1 |
| [`build_pdf.py`](build_pdf.py) | Render the combined PDF with local Pandoc/XeLaTeX/BibTeX tooling | `../output/pdf/actinf_policy_entanglement_lean_combined.pdf` |
| [`generate_figures.py`](generate_figures.py) | Renders every analytical manuscript figure | analytical PNGs in `../output/figures/` (+ optional coupling graph) |
| [`manuscript_variables.py`](manuscript_variables.py) | Computes every in-text variable substitution + mirrors `simulation.hyperparameters` | `../output/data/manuscript_variables.json` |
| [`dump_archetypes.py`](dump_archetypes.py) | Dumps K=2 Schmidt archetypes at a λ-sweep | `../output/data/ising_archetypes.csv` |
| [`parameter_sweep.py`](parameter_sweep.py) | Closed-form sweep (MI, FE, rank, entropy, phase) on the configured hyperparameter grid | `../output/data/parameter_sweep.csv` |
| [`simulate_pymdp.py`](simulate_pymdp.py) | pymdp 1.0.1 POMDP run: λ-sweep + rollout + free-energy bundle | pymdp PNGs (`pymdp_*`) + `pymdp_lambda_sweep.csv` + `pymdp_free_energy_bundle.csv` |
| [`simulate_multi_k.py`](simulate_multi_k.py) | Configured multi-stream ensemble experiments — per-K λ-sweep, TT-rank profile, aligned-mass | one `pymdp_K*_sweep.csv` per configured K + `multi_k_*` PNGs + `multi_k_summary.json` |
| [`simulate_long_horizon.py`](simulate_long_horizon.py) | Configured long-horizon coupled rollout (habit-accumulation witness) | `pymdp_long_horizon.csv` + `long_horizon_*` PNGs + `long_horizon_summary.json` |
| [`simulate_revertibility.py`](simulate_revertibility.py) | m-projection back-to-mean-field witness (Prop 7.3 / Theorem 5.1 identity) | `pymdp_revertibility.csv` + `revertibility_witness.png` + `revertibility_summary.json` |
| [`simulate_robustness.py`](simulate_robustness.py) | Robustness, ablation, and long-horizon replicate sidecars | one-axis, two-axis, ablation, replicate, seed-diagnostic, and threshold-sensitivity CSV/PNG/JSON sidecars |
| [`simulate_btai.py`](simulate_btai.py) | Shipped BTAI baseline worked run over the registered MCTS budget grid | `btai_baseline.json` + `btai_baseline.png` |
| [`simulate_adversarial.py`](simulate_adversarial.py) | Shipped adversarial-perturbation sweep over the registered $(\varepsilon,\lambda)$ grid | `adversarial_sweep.json` + `adversarial_sweep.png` |
| [`build_dashboard.py`](build_dashboard.py) | Interactive multi-view Plotly dashboard + plaintext invariants + JSON payload | `../output/web/dashboard.html`, `../output/reports/dashboard_*.txt`, `../output/data/dashboard_payload.json` |
| [`generate_index.py`](generate_index.py) | Regenerate `manuscript/INDEX.md` from the registry | `manuscript/INDEX.md` |
| [`generate_theorem_map.py`](generate_theorem_map.py) | Auto-generate the per-theorem four-track wiring table | `../docs/reference/_theorem_map.md` |
| [`inject_manuscript_variables.py`](inject_manuscript_variables.py) | Resolve every `[[…]]` token, auto-number every `$$..$$` block | rendered files in `../output/manuscript/` |
| [`validate_outputs.py`](validate_outputs.py) | Post-pipeline gate: PNGs / JSON / CSVs / free-energy bundle invariants | exit 0 / 1 |
| [`validate_manuscript.py`](validate_manuscript.py) | Manuscript completeness gate: tokens / citations / links / hardcoded refs / numeric ranges | exit 0 / 1 |
| [`validate_pdf.py`](validate_pdf.py) | Release-PDF gate: PDF text / TeX / LaTeX log / margin validation | exit 0 / 1 |
| [`regression_gate.py`](regression_gate.py) | Compares current run metrics against `regression_baseline.json` (test count, coverage, critical validator-module coverage, invariants, Lean hygiene) | exit 0 / 1 |
| [`run_all.py`](run_all.py) | End-to-end orchestrator; runs the canonical pipeline from its live `SCRIPTS` table, writes `output/MANIFEST.md`, and ends with `regression_gate.py`; `--with-pdf` and `--with-mathlib` add release subgates without changing the default pipeline | exit 0 / 1 + `../output/MANIFEST.md` |
| [`readiness_report.py`](readiness_report.py) | Summarizes live gate artifacts, runtime budget, optional MathlibProofs state, and suggested review slices | `../output/reports/release_readiness.md`, `release_readiness.json`, `release_index.md` |

## Running

```bash
# from the project directory:
uv run python scripts/generate_figures.py
uv run python scripts/manuscript_variables.py
uv run python scripts/dump_archetypes.py
uv run python scripts/parameter_sweep.py

# Sanity-check the artifacts after the above ran:
uv run python scripts/validate_outputs.py

# Full dependency-ordered pipeline, including manuscript injection,
# output validation, manuscript validation, and regression gate:
uv run python scripts/run_all.py

# Full dependency-ordered pipeline plus PDF rendering/validation:
uv run python scripts/run_all.py --with-pdf

# Full release pipeline plus optional MathlibProofs build:
uv run python scripts/run_all.py --with-pdf --with-mathlib
```

Every script is **idempotent** — running it again overwrites
the existing outputs.

## Figure inventory

| Figure | Source function | Theorem / Prop |
|---|---|---|
| `ising_mi_curve.png` | `figure_ising_mi_curve` | K=2 Ising MI: closed form vs numeric (manuscript §5.1) |
| `free_energy_curve.png` | `figure_free_energy_curve` | F[q_λ] vs λ for a utility sweep (Appendix B) |
| `coupling_tax_quadratic.png` | `figure_coupling_tax_quadratic` | O(λ²) coupling-tax bound (Theorem 9.1) |
| `phase_diagram.png` | `figure_phase_diagram` | Coupling-phase diagram (manuscript §9) |
| `optimal_lambda.png` | `figure_optimal_lambda` | Closed-form λ*(Δ) (manuscript §10) |
| `schmidt_rank.png` | `figure_schmidt_rank_vs_lambda` | Schmidt rank vs λ (Prop 7.1) |

## Adding a figure

1. Add a `figure_<name>() -> Path` function in `generate_figures.py`
   that:
   * Imports compute helpers from `../src/…`.
   * Plots with the established `figsize`, `dpi`, palette.
   * Writes to `OUTPUT_DIR / "<name>.png"`.
   * Returns the output path.
2. Append the path to the `figures` list in `main()`.
3. Update the inventory above and the manuscript section that embeds
   it.

## Conventions

* **Headless backend**: `os.environ.setdefault("MPLBACKEND", "Agg")`
  is set at the top of every plotting script.
* **DPI**: use `visualizations.setup.deterministic_setup`; current defaults are tuned for PDF crispness and embedded figure readability.
* **Determinism**: `np.random.seed(42)` at module import; per-figure
  RNGs use explicit seeds.
* **Print paths**: every script that writes artifacts prints the
  resulting path(s) to stdout, one per line, so the rendering pipeline
  can collect them.  `validate_outputs.py` instead exits with a status
  code — any non-zero exit is a CI gate failure.

## Orchestration placement

`run_all.py` is the canonical local CI shape.  It keeps dependency
edges explicit:

1. Build and hygiene-check Lean before trusting theorem tables.
2. Render deterministic analytical figures.
3. Run write-isolated empirical producers in the parallel-eligible
   batch (`dump_archetypes.py` through `simulate_revertibility.py`).
4. Compute manuscript variables after all empirical sidecar summaries
   exist.
5. Build dashboard/report artifacts and generated indexes.
6. Inject manuscript variables only after all data producers have run.
7. Validate output artifacts, validate manuscript references, then run
   the regression gate against the committed baseline.
8. For release builds, pass `--with-pdf` to insert `build_pdf.py` and
   `validate_pdf.py` before the regression gate; pass `--with-mathlib`
   to add the separate optional `lean/MathlibProofs/` build after the
   boundary Lean gate.

For a reader-facing explanation of the same pipeline, see
[`../docs/reference/methods_orchestration.md`](../docs/reference/methods_orchestration.md).
