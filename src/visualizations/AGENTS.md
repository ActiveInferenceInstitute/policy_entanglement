# AGENTS.md — `src/visualizations/`

Reusable plotting helpers used by every figure script.

## Module map

| File | Helpers |
|---|---|
| `setup.py` | `deterministic_setup`, `ensure_outdir` |
| `heatmaps.py` | `plot_lambda_utility_heatmap`, `plot_schmidt_entropy_surface` |
| `joint_plots.py` | `plot_joint_heatmap_with_marginals` |
| `spectral_plots.py` | `plot_archetype_dendrogram`, `plot_tensor_train_rank_surface` |
| `trajectory_plots.py` | `plot_rollout_marginals` |
| `graphs.py` | `plot_coupling_graph`, `has_networkx`, `has_seaborn` |
| `log_weight.py` | `plot_log_weight_flow` |

## Rules

* Always set `MPLBACKEND=Agg` before importing matplotlib (the figure
  scripts already do this; tests rely on it via `conftest.py`).
* Each helper returns the resolved output path so the calling figure
  script can print it for the manifest.
* Optional dependencies (`seaborn`, `networkx`, `plotly`) come from the
  `viz` group.  The affected helpers degrade gracefully — check
  `has_networkx()` / `has_seaborn()` before relying on them.
* Helpers must accept arbitrary `(λ, utility)` arrays — do not hard-code
  shapes; the coverage tests pass `random` matrices through every
  function.
