# `src/visualizations/`

Reusable matplotlib plotting helpers consumed by every figure script
and the test suite.  This is the single subpackage allowed to write
PNGs; analytical / inference logic stays in [`../lean/`](../lean/) and
[`../simulation/`](../simulation/).  Public symbols are re-exported
from `visualizations/__init__.py`.

See parent docs: [`../AGENTS.md`](../AGENTS.md), [`../README.md`](../README.md).
Subpackage rules and matplotlib backend conventions: [`AGENTS.md`](AGENTS.md).

## Module map

| Module | Role | Exports |
|---|---|---|
| [`setup.py`](setup.py) | Deterministic backend / RNG / output-dir bootstrap | `deterministic_setup`, `ensure_outdir` |
| [`heatmaps.py`](heatmaps.py) | λ × utility / Schmidt-entropy heatmaps | `plot_lambda_utility_heatmap`, `plot_schmidt_entropy_surface` |
| [`joint_plots.py`](joint_plots.py) | Joint posterior + marginals + m-projection overlay | `plot_joint_heatmap_with_marginals` |
| [`spectral_plots.py`](spectral_plots.py) | Schmidt archetypes + tensor-train ranks | `plot_archetype_dendrogram`, `plot_tensor_train_rank_surface` |
| [`trajectory_plots.py`](trajectory_plots.py) | Rollout marginals over time | `plot_rollout_marginals` |
| [`graphs.py`](graphs.py) | Coupling-graph overlay (optional `networkx` / `seaborn`) | `has_networkx`, `has_seaborn`, `plot_coupling_graph` |
| [`log_weight.py`](log_weight.py) | Affine-log-weight flow lines | `plot_log_weight_flow` |
| [`geodesic.py`](geodesic.py) | KL geodesic / λ⋆-locus geometry plots | `plot_kl_geodesic_in_simplex`, `plot_lambda_star_locus` |
| [`free_energy_plots.py`](free_energy_plots.py) | Bundle dashboards (consume `FreeEnergyBundle` lists) | `plot_vfe_decomposition`, `plot_efe_under_posterior`, `plot_entropy_decomposition`, `plot_action_distribution_evolution`, `plot_free_energy_panel`, `plot_bundle_quantile_envelope` |
| [`pymdp_extras.py`](pymdp_extras.py) | Additional pymdp-grounded dashboards | `plot_action_entropy_curve`, `plot_kl_to_lambda_zero`, `plot_marginal_entropy_per_stream`, `plot_pymdp_summary_panel` |
| [`metadata.py`](metadata.py) | PNG `tEXt`-chunk reproducibility + plotted-statistics/font metadata | `FIGURE_METADATA_SCHEMA_VERSION`, `figure_metadata`, `figure_statistics`, `summarize_array`, `read_figure_metadata`, `has_project_metadata` |

## Conventions

* `MPLBACKEND=Agg` is set in `conftest.py`; each plot helper assumes a
  headless backend and closes its figure before returning.
* Every helper returns the resolved output path so the calling figure
  script can print it for the manifest collection.
* Optional dependencies (`seaborn`, `networkx`, `plotly`) come from the
  `viz` group; affected helpers degrade gracefully — check
  `has_networkx()` / `has_seaborn()` before relying on them.
* `metadata.figure_metadata(...)` is the canonical way to attach
  `project.*` `tEXt` chunks to PNGs (source script + function,
  hyperparameter snapshot, git rev, ISO timestamp, and
  `project.uncertainty_semantics`).  The shared save helper also embeds
  schema-v2 `project.figure_statistics` with axis limits, legend
  labels, line-series summaries, image-array summaries, scatter / mesh
  collection summaries, and actual font sizes for titles, labels,
  ticks, legends, and stat/provenance annotations.
  `_git_revision` shells out to `git rev-parse` and degrades to
  `"unknown"` outside a checkout.
