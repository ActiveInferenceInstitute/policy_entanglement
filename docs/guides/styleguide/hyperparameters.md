# §1 — Configurable simulations: the hyperparameters module

Back to the styleguide hub: [`../styleguide.md`](../styleguide.md).

## Where the constants live

[`src/simulation/hyperparameters.py`](../../../src/simulation/hyperparameters.py)
declares every grid + scalar:

| Constant | Type | Used by |
| --- | --- | --- |
| `PARAMETER_SWEEP_LAMBDAS` | `FigureGrid(0.0, 6.0, 121)` | `figure_ising_mi_curve`, `figure_free_energy_curve`, `parameter_sweep.py` |
| `COUPLING_TAX_LAMBDAS` | `FigureGrid(0.0, 1.5, 31)` | `figure_coupling_tax_quadratic` |
| `PHASE_DIAGRAM_LAMBDAS` | `FigureGrid(0.0, 4.0, 401)` | `figure_phase_diagram` |
| `OPTIMAL_LAMBDA_DELTAS` | `FigureGrid(-0.95, 0.95, 191)` | `figure_optimal_lambda` |
| `SCHMIDT_RANK_LAMBDAS` | `FigureGrid(0.0, 4.0, 81)` | `figure_schmidt_rank_vs_lambda` |
| `PHASE_LANDSCAPE_LAMBDAS` × `PHASE_LANDSCAPE_UTILITIES` | `41×21` grid | `figure_phase_landscape`, `figure_schmidt_entropy_surface` |
| `LOG_WEIGHT_FLOW_LAMBDAS` | `FigureGrid(0.0, 3.0, 31)` | `figure_log_weight_flow` |
| `KL_GEODESIC_LAMBDAS` | `FigureGrid(0.0, 4.0, 21)` | `figure_kl_geodesic_in_simplex` |
| `LAMBDA_STAR_UTILITIES` × `LAMBDA_STAR_GAMMAS` | `20×16` grid | `figure_lambda_star_locus` |
| `PYMDP_SWEEP_LAMBDAS` | `FigureGrid(0.0, 4.0, 21)` | `simulate_pymdp.py` |
| `PYMDP_ROLLOUT_STEPS` / `PYMDP_ROLLOUT_SEED` / `PYMDP_ROLLOUT_LAMBDA` | scalars | `figure_pymdp_rollout` |
| `PYMDP_SWEEP_OBSERVATIONS` | `(0, 0)` | `simulate_pymdp.py`, `manuscript_variables.py` |
| `FIGURE_GLOBAL_SEED` | `42` | `deterministic_setup(...)` in every figure script |
| `PHASE_LAMBDA_C1` / `PHASE_LAMBDA_C2` | `0.5 / 2.5` | phase fill-bands, illustrative thresholds |
| `COUPLING_TAX_PROBE_LAMBDA` | `0.05` | small-λ slope fit |
| Sentinel λ tuples | `ISING_MI_SENTINEL_LAMBDAS`, `SPECTRAL_SENTINEL_LAMBDAS`, … | manuscript prose `[[VAR:...]]` substitutions |

## How scripts consume them

```python
# scripts/generate_figures.py
from simulation import hyperparameters as H
deterministic_setup(seed=int(H.FIGURE_GLOBAL_SEED))

def figure_ising_mi_curve() -> Path:
    lams = H.PARAMETER_SWEEP_LAMBDAS.values()  # ← never a literal
    ...
```

## The mirror into JSON

[`scripts/manuscript_variables.py`](../../../scripts/manuscript_variables.py)
calls `H.figure_hyperparameter_summary()` and writes every key into
`output/data/manuscript_variables.json`.  The sentinel-λ helpers
inside the same script (`_bernoulli_facts`, `_spectral_facts`, …)
read sentinel tuples from `H` rather than hardcoding the λ values.

## What the tests assert

[`tests/test_hyperparameters.py`](../../../tests/test_hyperparameters.py)
asserts:

* every `FigureGrid` is well-formed and produces an array of the
  advertised length;
* every key inside `figure_hyperparameter_summary()` is present;
* the mirrored values in `manuscript_variables.json` equal the
  source-of-truth constants exactly (no drift).

## Adding a new hyperparameter

1. Add the constant to `src/simulation/hyperparameters.py`.
2. Add it to `figure_hyperparameter_summary()` so it lands in the JSON.
3. Reference it from the script (`H.MY_NEW_GRID.values()`).
4. Reference its mirrored key inside the manuscript via
   `[[VAR:my_new_grid_points]]` (or whatever the JSON key is).
5. Run `uv run pytest tests/test_hyperparameters.py` to confirm.
