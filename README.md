# Policy Entanglement in Active Inference

A research project that develops a **tunable mean-field deformation framework**
for multi-stream policy ensembles in active inference. A single scalar
coupling parameter `λ ∈ [0, ∞)` interpolates between strict mean-field
factorisation (`λ = 0`) and arbitrary structured joint policy distributions
(`λ → ∞`), with a closed-form *entanglement decomposition* of variational
free energy and an information-geometric / spectral / formal-verification
treatment.

This project is one of the active projects under the
[`docxology/template`](https://github.com/docxology/template) two-layer
architecture.  It now contains **three** parallel implementations of the same
mathematics, each in its own subpackage:

| Track | Path | Purpose |
|---|---|---|
| **Lean 4** boundary fragment | [`lean/`](lean/) | Machine-checked types and theorem statements; Mathlib-free, builds on stock Lean 4 v4.29.0 |
| **Python analytical companion** | [`src/lean/`](src/lean/) | Numerical realisation of every quantity in the Lean modules, with dense PMF arithmetic on finite policy spaces |
| **pymdp 1.0.1 POMDP harness** | [`src/simulation/`](src/simulation/) | Runs the analytical setting inside grounded POMDP agents (specs, builders, agents, inference, rollout, sweep) |
| **Visualizations** | [`src/visualizations/`](src/visualizations/) | Reusable plotting helpers (heatmaps, joint plots, spectral, trajectory, graph, log-weight flow) |
| Manuscript | [`manuscript/`](manuscript/) | Modular markdown sections rendered to PDF by the template pipeline |
| Figures | [`scripts/`](scripts/) | Thin orchestrators producing every manuscript figure |
| Documentation | [`docs/`](docs/) | Architecture, math reference, Lean / Python API, build / run guides, **POMDP simulation guide** |

## Quick start

`uv` manages the environment.  The new `sim` and `viz` groups bring in
`pymdp 1.0.1` and the visualization stack respectively:

```bash
# Default (core + dev + viz):
uv sync

# Add the pymdp simulation harness:
uv sync --group sim --group viz

# Lean build (boundary fragment, no Mathlib needed):
cd lean && lake build                              # 16/16 jobs green

# Python tests (340 tests, ≥90% coverage on src/):
uv run pytest tests/ --cov=src --cov-report=term-missing

# Generate every manuscript figure (21 PNGs):
uv run python scripts/generate_figures.py

# Run the pymdp POMDP simulation:
uv run python scripts/simulate_pymdp.py

# Compute the in-manuscript variable substitutions:
uv run python scripts/manuscript_variables.py

# Run *everything* end-to-end (figures + sim + sweep + validate):
uv run python scripts/run_all.py
```

See [`docs/guides/build_run.md`](docs/guides/build_run.md) for the full pipeline,
[`docs/reference/architecture.md`](docs/reference/architecture.md) for the layered design,
[`docs/reference/math_reference.md`](docs/reference/math_reference.md) for the mathematics,
[`docs/simulation/pomdp_simulation.md`](docs/simulation/pomdp_simulation.md) for the new
pymdp harness, and [`docs/simulation/visualizations.md`](docs/simulation/visualizations.md)
for the figure helpers.

## Status

| Layer | State |
|---|---|
| Lean 4 build | ✅ 16/16 jobs green; new `Monotonicity.lean` adds **constructive (no-`sorry`) theorems** alongside the legacy boundary stubs |
| Python tests | ✅ 340 / 340 passing, 96.08 % coverage on `src/` |
| Manuscript | ✅ 24 modular sections (`00_abstract.md` … `99_bibliography.md` plus 5 appendices) |
| Figures | ✅ 13 core figures + 5 pymdp-grounded figures + KL/λ⋆ extras (21 total) (with `--group sim`) |
| pymdp harness | ✅ end-to-end λ-sweep + deterministic coupled rollouts via pymdp 1.0.1 |

## Project layout

```
.
├── README.md            ← (this file)
├── AGENTS.md            ← Agent / contributor cheat-sheet
├── pyproject.toml       ← uv-managed Python packaging + pytest + coverage config
├── lean/                ← Lean 4 package (boundary fragment + FepSketches re-exports)
├── manuscript/          ← Modular markdown sections + config + preamble
├── docs/                ← Modular technical documentation
├── src/
│   ├── lean/            ← Analytical mirrors of the Lean modules
│   ├── simulation/      ← pymdp 1.0.1 POMDP harness (specs, builders, agents, …)
│   └── visualizations/  ← Reusable plotting helpers (heatmaps, joint, spectral, …)
├── tests/               ← 340 tests (pure-numpy + pymdp-marked + viz)
├── scripts/             ← Thin orchestrators (figures, sim, sweeps, manuscript vars)
└── output/              ← Generated artefacts (figures, data, simulations)
```

## Citation

Friedman, D. A. (2026). *Policy Entanglement in Active Inference: A
Tunable Mean-Field Deformation Framework for Multi-Stream Policy
Ensembles, with Information-Geometric, Spectral, and
Lean-Formalization Treatments.* Active Inference Institute (working
manuscript).

## License

CC-BY-4.0 for the manuscript.  MIT-style for the code (matches the
parent template repository).
