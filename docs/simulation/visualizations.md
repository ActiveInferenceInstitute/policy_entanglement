# Visualization subpackage

The `visualizations` subpackage under `src/visualizations/` collects
reusable plotting helpers used by every figure script.  Each submodule
covers one family of artifact so the calling figure script can import
only the helpers it needs.

| Submodule | Helpers | Purpose |
|---|---|---|
| `setup` | `deterministic_setup`, `ensure_outdir` | matplotlib + numpy seeding, output-dir helper |
| `heatmaps` | `plot_lambda_utility_heatmap`, `plot_schmidt_entropy_surface` | (λ, utility) phase / entropy heatmaps |
| `joint_plots` | `plot_joint_heatmap_with_marginals` | annotated 2-D joint + marginals + residual |
| `spectral_plots` | `plot_archetype_dendrogram`, `plot_tensor_train_rank_surface` | Schmidt archetypes, TT-rank surfaces |
| `trajectory_plots` | `plot_rollout_marginals` | per-stream marginal time-series + total correlation |
| `graphs` | `plot_coupling_graph`, `has_networkx`, `has_seaborn` | coupling-potential interaction graph (optional `viz` group) |
| `log_weight` | `plot_log_weight_flow` | e-geodesic affineness (Theorem 7.4) |

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

As of the latest generated audit, the registry figure count is reported
by `output/reports/release_readiness.json` and can be cross-checked from
`len(manuscript/refs/labels.yaml::figures)`.
See [`../guides/build_run.md`](../guides/build_run.md#figure-count-scoping)
for the authoritative scoping table that splits the figures across the
producing scripts.

### Scoping

| Scope | Count | Notes |
|---|---|---|
| `scripts/generate_figures.py` (headline analytical) | 15 | Mathlib-free pure-numpy plots |
| `scripts/simulate_pymdp.py` (pymdp dashboards + joints) | 14 | total-correlation curve, three joint snapshots, coupled rollout, plus the dashboards `pymdp_vfe_decomposition`, `pymdp_efe_under_posterior`, `pymdp_entropy_decomposition`, `pymdp_action_distribution`, `pymdp_summary_panel`, `pymdp_action_entropy`, `pymdp_kl_to_lambda_zero`, `pymdp_marginal_entropy_per_stream`, `pymdp_free_energy_panel` |
| `scripts/simulate_multi_k.py` (round 3 + K=5 expansion) | 3 | `multi_k_total_correlation`, `multi_k_aligned_mass`, `multi_k_tt_rank_profile` — configured multi-K Ising sweep |
| `scripts/simulate_long_horizon.py` (round 3) | 2 | `long_horizon_marginals`, `long_horizon_steady_state` — configured `LONG_HORIZON_STEPS` rollout + steady-state KL convergence |
| `scripts/simulate_revertibility.py` (round 3) | 1 | `revertibility_witness` — m-projection KL identity |
| `scripts/simulate_robustness.py` (robustness expansion) | 9 | robustness envelopes, half-saturation, decomposition residuals, ablation, interaction, replicate, seed-diagnostic, and threshold-sensitivity sidecars |
| `scripts/simulate_btai.py` | 1 | shipped BTAI baseline panel |
| `scripts/simulate_adversarial.py` | 1 | shipped adversarial-perturbation panel |
| `scripts/simulate_gnn.py` | 1 diagnostic | `gnn_bernoulli_roundtrip.png`; validated output, not a numbered manuscript figure |
| `manuscript/refs/labels.yaml::figures` (registry total) | 46 | paper-facing registered figure union; excludes the non-registry GNN diagnostic PNG |

### `scripts/generate_figures.py` (headline analytical) produces:

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
* `kl_geodesic_simplex.png` — KL geodesic walked across the simplex.
* `lambda_star_locus.png` — λ\* locus across (utility, γ) grid.

### `scripts/simulate_pymdp.py` adds:

* `pymdp_total_correlation_curve.png` — pymdp-grounded total-correlation curve.
* `pymdp_joint_lambda_{0.00,2.00,4.00}.png` — joint posterior at three λ values.
* `pymdp_coupled_rollout.png` — coupled rollout marginals + I(q_t) curve.
* `pymdp_vfe_decomposition.png`, `pymdp_efe_under_posterior.png`,
  `pymdp_entropy_decomposition.png`, `pymdp_action_distribution.png`,
  `pymdp_summary_panel.png`, `pymdp_action_entropy.png`,
  `pymdp_kl_to_lambda_zero.png`, `pymdp_marginal_entropy_per_stream.png`,
  `pymdp_free_energy_panel.png` — the free-energy dashboards.

### `scripts/simulate_multi_k.py` adds:

* `multi_k_total_correlation.png` — configured multi-K multi-information growth.
* `multi_k_aligned_mass.png` — aligned-policy mass concentration as K varies.
* `multi_k_tt_rank_profile.png` — TT bond-rank profile as K varies.

### `scripts/simulate_long_horizon.py` (round 3) adds:

* `long_horizon_marginals.png` — configured long-horizon coupled-rollout per-stream marginals.
* `long_horizon_steady_state.png` — steady-state KL convergence.

### `scripts/simulate_revertibility.py` (round 3) adds:

* `revertibility_witness.png` — m-projection KL identity at every λ on the sweep.

### `scripts/simulate_robustness.py` adds:

* `robustness_tc_envelopes.png` — one-axis-at-a-time TC envelopes.
* `robustness_half_saturation.png` — scenario-level half-saturation sensitivity.
* `robustness_decomposition_residuals.png` — decomposition residuals across stress scenarios.
* `coupling_ablation_summary.png` — aligned/null/anti-aligned/heterogeneous coupling ablation.
* `long_horizon_replicate_envelope.png` — replicate TC envelope over configured seeds.

### Reproducibility metadata

Every PNG carries a `tEXt`-chunk recording its generating function,
hyperparameter snapshot, git short SHA, and compact plotted-data
statistics via `metadata.figure_metadata` plus the shared
`visualizations._io._save_with_metadata` save path.
Reruns produce outputs that are **numerically identical modulo the
embedded PNG build timestamp** — the plotted values, axes, and
overlays match byte-for-byte once the timestamp is normalized.  The
prior "bit-identical" framing was tightened in round 1 to reflect
this caveat.  Consumers can verify provenance via
`metadata.read_figure_metadata(path)`. The automatic
`project.figure_statistics` block records figure size, axis labels,
axis limits, legend labels, line-series summaries, image-array
summaries, and collection summaries (scatter / mesh offsets, arrays,
and marker sizes when present) without embedding the full plotted
arrays.
The sibling `project.uncertainty_semantics` field mirrors the
`uncertainty:` class registered in `manuscript/refs/labels.yaml`, so a
reader can distinguish deterministic grids from canonical fixed-seed
trajectories, replicate envelopes, confidence intervals, and analytical
schematics without inferring stochastic status from the plot alone.

### Visual accessibility contract

`visualizations.setup.deterministic_setup()` applies the shared visual
contract before figure scripts draw anything:

* `Agg` backend for headless reproducibility.
* Okabe-Ito categorical colors plus perceptually uniform sequential
  maps (`viridis`, `magma`, `cividis`-style choices).
* Larger axis titles, labels, tick text, and label padding than
  matplotlib defaults, so raster figures remain readable in the
  manuscript and PDF.
* Tight bounding boxes through `_save_with_metadata`, with figures
  closed immediately after saving to keep the pipeline memory-stable.

When adding a figure, prefer a single clear statistical question over
a collage: trend, comparison, heatmap, posterior residual, trajectory,
or identity residual. Put enough information in the caption and
metadata that a reader can locate the source script, rerun it, and
audit the plotted scalar.  The caption contract follows the
self-contained-figure guidance of Rougier, Droettboom, and Bourne's
"Ten Simple Rules for Better Figures" while keeping every result tied
to this project's generated sidecars and validators.

Validate every figure is well-formed with:

```bash
uv run python scripts/validate_outputs.py
```
