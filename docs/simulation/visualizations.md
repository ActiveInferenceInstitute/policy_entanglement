# Visualization subpackage

The `visualizations` subpackage under `src/visualizations/` collects
reusable plotting helpers used by every figure script.  Each submodule
covers one family of artefact so the calling figure script can import
only the helpers it needs.

| Submodule | Helpers | Purpose |
|---|---|---|
| `setup` | `deterministic_setup`, `ensure_outdir` | matplotlib + numpy seeding, output-dir helper |
| `heatmaps` | `plot_lambda_utility_heatmap`, `plot_schmidt_entropy_surface` | (λ, utility) phase / entropy heatmaps |
| `joint_plots` | `plot_joint_heatmap_with_marginals` | annotated 2-D joint + marginals + residual |
| `spectral_plots` | `plot_archetype_dendrogram`, `plot_tensor_train_rank_surface` | Schmidt archetypes, TT-rank surfaces |
| `trajectory_plots` | `plot_rollout_marginals` | per-stream marginal time-series + total correlation |
| `graphs` | `plot_coupling_graph`, `has_networkx`, `has_seaborn` | coupling-potential interaction graph (optional `viz` group) |
| `log_weight` | `plot_log_weight_flow` | e-geodesic affineness (Theorem 6.4) |

## Install

The optional plotting dependencies (`seaborn`, `networkx`, `plotly`)
ship in the `viz` group:

```bash
uv sync --group viz
```

The bare matplotlib helpers (heatmaps, joint plots, trajectories,
log-weight) work on stock matplotlib; only `plot_coupling_graph`
requires `networkx`.

## Figure manifest

`scripts/generate_figures.py` produces the following PNGs under
`output/figures/`:

* Legacy 6 (`ising_mi_curve`, `free_energy_curve`,
  `coupling_tax_quadratic`, `phase_diagram`, `optimal_lambda`,
  `schmidt_rank`).
* `phase_landscape.png` — F(λ, utility) heatmap.
* `schmidt_entropy_surface.png` — S_E(λ, utility) heatmap.
* `joint_heatmap_lambda2.png` — annotated K=2 Ising joint at λ=2.
* `archetype_dendrogram.png` — Schmidt archetype weights + overlap.
* `tensor_train_rank_surface.png` — TT ranks across K=2..5.
* `log_weight_flow.png` — e-geodesic straight lines.
* `coupling_graph.png` — K=4 coupling-potential graph.

`scripts/simulate_pymdp.py` adds:

* `pymdp_total_correlation_curve.png` — pymdp-grounded total-correlation curve.
* `pymdp_joint_lambda_{0.00,2.00,4.00}.png` — joint posterior at three λ values.
* `pymdp_coupled_rollout.png` — coupled rollout marginals + I(q_t) curve.

Validate every figure is well-formed with:

```bash
uv run python scripts/validate_outputs.py
```
