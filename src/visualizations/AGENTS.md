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
| `geodesic.py` | `plot_kl_geodesic_in_simplex`, `plot_lambda_star_locus` |
| `free_energy_plots.py` | `plot_vfe_decomposition`, `plot_efe_under_posterior`, `plot_entropy_decomposition`, `plot_action_distribution_evolution`, `plot_free_energy_panel`, `plot_bundle_quantile_envelope` (consumes a list of `simulation.inference.FreeEnergyBundle`) |
| `pymdp_extras.py` | `plot_action_entropy_curve`, `plot_kl_to_lambda_zero`, `plot_marginal_entropy_per_stream`, `plot_pymdp_summary_panel` (additional pymdp-grounded dashboards driven by bundle lists + `simulation.statistics`) |
| `metadata.py` | `FIGURE_METADATA_SCHEMA_VERSION`, `figure_metadata`, `figure_statistics`, `summarize_array`, `read_figure_metadata`, `has_project_metadata` (PNG `tEXt`-chunk reproducibility metadata: source script + function, hyperparameter snapshot, uncertainty semantics, git rev, ISO timestamp, legend labels, line/image/collection summaries, and schema-v2 font-size summaries).  Reads PNGs back via PIL. |

## Rules

* Always set `MPLBACKEND=Agg` before importing matplotlib (the figure
  scripts already do this; tests rely on it via `conftest.py`).
* Each helper returns the resolved output path so the calling figure
  script can print it for the manifest.
* Save figures through `visualizations._io._save_with_metadata`; it
  applies tight layout, embeds `project.figure_statistics`, closes the
  figure, and keeps PNG metadata consistent across scripts.  Every PNG
  must also carry `project.uncertainty_semantics`, inferred by
  `figure_metadata` unless a script passes an explicit class.
* Optional dependencies (`seaborn`, `networkx`, `plotly`) come from the
  `viz` group.  The affected helpers degrade gracefully — check
  `has_networkx()` / `has_seaborn()` before relying on them.
* Helpers must accept arbitrary `(λ, utility)` arrays — do not hard-code
  shapes; the coverage tests pass `random` matrices through every
  function.
