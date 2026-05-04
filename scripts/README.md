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
| [`generate_figures.py`](generate_figures.py) | Renders every manuscript figure | `../output/figures/{ising_mi_curve, free_energy_curve, coupling_tax_quadratic, phase_diagram, optimal_lambda, schmidt_rank}.png` |
| [`manuscript_variables.py`](manuscript_variables.py) | Computes in-text variable substitutions | `../output/data/manuscript_variables.json` |
| [`dump_archetypes.py`](dump_archetypes.py) | Dumps K=2 Schmidt archetypes at a λ-sweep | `../output/data/ising_archetypes.csv` |
| [`parameter_sweep.py`](parameter_sweep.py) | Sweeps every key quantity (MI, FE, rank, entropy, phase) over a fine λ-grid | `../output/data/parameter_sweep.csv` |
| [`validate_outputs.py`](validate_outputs.py) | Post-pipeline gate that re-checks every artefact under `output/` | exit code 0 / 1 |
| [`run_all.py`](run_all.py) | End-to-end orchestrator; runs every script above in order then validates | exit code 0 / 1 |

## Running

```bash
# from the project directory:
uv run python scripts/generate_figures.py
uv run python scripts/manuscript_variables.py
uv run python scripts/dump_archetypes.py
uv run python scripts/parameter_sweep.py

# Sanity-check the artefacts after the above ran:
uv run python scripts/validate_outputs.py
```

All five scripts are **idempotent** — running them again overwrites
the existing outputs.

## Figure inventory

| Figure | Source function | Theorem / Prop |
|---|---|---|
| `ising_mi_curve.png` | `figure_ising_mi_curve` | K=2 Ising MI: closed form vs numeric (manuscript §5.1) |
| `free_energy_curve.png` | `figure_free_energy_curve` | F[q_λ] vs λ for a utility sweep (Appendix B) |
| `coupling_tax_quadratic.png` | `figure_coupling_tax_quadratic` | O(λ²) coupling-tax bound (Theorem 8.1) |
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
* **DPI**: `dpi=150` for figures, `savefig.dpi=300` for PDF crispness.
* **Determinism**: `np.random.seed(42)` at module import; per-figure
  RNGs use explicit seeds.
* **Print paths**: every script that writes artefacts prints the
  resulting path(s) to stdout, one per line, so the rendering pipeline
  can collect them.  `validate_outputs.py` instead exits with a status
  code — any non-zero exit is a CI gate failure.

## CI / pipeline placement

In the parent template's 10-stage pipeline:

* **Stage 4 (Run analysis)** — `generate_figures.py`,
  `manuscript_variables.py`, `dump_archetypes.py`,
  `parameter_sweep.py`.
* **Stage 6 (Validate output)** — `validate_outputs.py`.
