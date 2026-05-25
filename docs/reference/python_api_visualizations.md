# Python API: subpackage `visualizations/`

*Latest generated audit.* The figure suite routes
publication typography, colors, panel sizes, in-figure statistic
boxes, and PNG metadata through shared helpers so every generated PNG
has the same visual and audit contract.

matplotlib / seaborn / plotly figure helpers + PNG reproducibility
metadata. Pure I/O + plotting; no numerical work — every numerical
input is computed by `lean/`, `simulation/`, or `manuscript/`.

Imports: `from visualizations.<module> import …` (`pythonpath = src/`).

Companion: [`../simulation/visualizations.md`](../simulation/visualizations.md) (figure-helper guide).

---

## Subpackage `visualizations/`

`seaborn`, `networkx`, `plotly` are optional deps (`uv sync --group viz`);
the `graphs.plot_coupling_graph` helper returns `None` when networkx is
missing.  All other helpers work on stock matplotlib.

### `setup.py`

```python
@dataclass(frozen=True)
class FigureStyle:
    single: tuple[float, float]
    wide: tuple[float, float]
    two_panel: tuple[float, float]
    dashboard_2x2: tuple[float, float]
    dashboard_2x3: tuple[float, float]
    title_size: float
    label_size: float
    tick_size: float
    legend_size: float
    annotation_size: float
    provenance_size: float
    theorem_badge_size: float
    def strip(n_streams: int) -> tuple[float, float]

PUBLICATION_STYLE: FigureStyle
def palette_color(index: int) -> str
def deterministic_setup(*, seed: int = 0, dpi: int = 170,
                         save_dpi: int = 300) -> None
def ensure_outdir(path: Path | str) -> Path
```

`FigureStyle`, `PUBLICATION_STYLE`, and `palette_color` are the
single source of truth for publication plot sizing, minimum font
sizes, and the Okabe-Ito colorblind-safe categorical palette.

### `annotations.py` (shared figure-annotation helpers)

```python
# Apply the standard λ axis label + faint grid.
def apply_lambda_axis(ax: Axes, *, label: str | None = None) -> None

# Place a small badge naming the theorem the figure witnesses.
def pin_theorem(ax: Axes, label: str, *, loc: str = "upper right") -> None

# One-line provenance footer (script::function · k=v, k=v).
def add_provenance_footer(fig: Figure, *, script: str, function: str,
                          hyperparameters: Mapping[str, Any] | None = None) -> None

# Dashed vertical lines at critical λ values (phase / coupling-tax plots).
def mark_critical_lambdas(ax: Axes, lambdas, *,
                          labels: tuple[str, ...] | None = None,
                          colors: tuple[str, ...] | None = None) -> None

# Compact in-panel statistics or audit metadata.
def add_stats_box(
    ax: Axes,
    lines: Mapping[str, Any] | Sequence[tuple[str, Any] | str],
    *,
    loc: str = "lower right",
) -> None

# Horizontal dashed mean-field baseline (typically y=0 for TC / log-weight / KL residual figures).
def add_mean_field_baseline(ax: Axes, value: float = 0.0, *, label: str | None = None) -> None

# Shade a horizontal tolerance band [center - hw, center + hw] across the axis.
def add_tolerance_band(
    ax: Axes, center: float, half_width: float, *,
    color: str = "#56B4E9", label: str | None = None,
) -> None

# Mark a half-saturation coupling value on a λ-vs-I axis.
def add_saturation_marker(
    ax: Axes, lam_half: float, value_at_half: float, *,
    label: str = r"$\lambda_{1/2}$",
) -> None

# Claim-strength badge: empirical | witness | hypothesis | analytical.
def add_claim_strength_tag(ax: Axes, kind: str, *, loc: str = "lower left") -> None

# Standardized axis-label constants used across the figure suite.
LAMBDA_LABEL: str            # r"Coupling $\lambda$"
LAMBDA_MATH: str             # r"$\lambda$"
UTILITY_LABEL: str           # utility surplus
GAMMA_LABEL: str             # EFE precision
FREE_ENERGY_LABEL: str       # F[q_λ]  [nats]
MI_LABEL: str                # I(λ)  [nats]
TOTAL_CORRELATION_LABEL: str # I(q_λ)  [nats]
ENTROPY_LABEL: str           # S_E(λ)  [nats]
```

### `heatmaps.py`

```python
def plot_lambda_utility_heatmap(*, lams, utilities, score: ArrayF,
                                 title: str, cbar_label: str,
                                 out_path, cmap: str = "viridis",
                                 metadata=None) -> Path
def plot_schmidt_entropy_surface(*, lams, utilities, entropies: ArrayF,
                                  out_path, metadata=None) -> Path
```

### `joint_plots.py`

```python
def plot_joint_heatmap_with_marginals(*, q: ArrayF, title: str, out_path,
                                       xticklabels=None, yticklabels=None,
                                       metadata=None) -> Path
```

### `spectral_plots.py`

```python
def plot_archetype_dendrogram(*, weights, overlap_matrix: ArrayF, out_path, metadata=None) -> Path
def plot_tensor_train_rank_surface(*, k_values, rank_profiles, out_path, metadata=None) -> Path
```

### `trajectory_plots.py`

```python
def plot_rollout_marginals(*, marginals_per_stream: Sequence[ArrayF],
                            titles: Sequence[str],
                            total_correlations: ArrayF,
                            out_path, metadata=None) -> Path
```

### `graphs.py`

```python
def has_seaborn() -> bool
def has_networkx() -> bool
def plot_coupling_graph(*, coupling_j: ArrayF, out_path,
                         threshold: float = 0.0, metadata=None) -> Path | None
```

### `geodesic.py`

```python
def plot_kl_geodesic_in_simplex(*, lams, joints: Sequence[ArrayF],
                                 out_path, metadata=None) -> Path
def plot_lambda_star_locus(*, utilities, gammas,
                            lambda_star: ArrayF, out_path, metadata=None) -> Path
```

### `log_weight.py`

```python
def plot_log_weight_flow(*, lams, log_weights: ArrayF, out_path,
                          pi_labels: Sequence[str] | None = None,
                          metadata=None) -> Path
```

### `free_energy_plots.py`

Six plots that consume a list of `simulation.inference.FreeEnergyBundle`
(or, in the last case, a `simulation.statistics.QuantileEnvelope`):

```python
def plot_vfe_decomposition(bundles, *, out_path, metadata=None) -> Path
def plot_efe_under_posterior(bundles, *, out_path, metadata=None) -> Path
def plot_entropy_decomposition(bundles, *, out_path, metadata=None) -> Path
def plot_action_distribution_evolution(bundles, *, out_path, metadata=None) -> Path
def plot_free_energy_panel(bundles, *, out_path, metadata=None) -> Path
def plot_bundle_quantile_envelope(
    envelope, *, out_path,
    field_label=r"Total correlation $I(q_\lambda)$ [nats]",
    metadata=None,
) -> Path
```

### `pymdp_extras.py`

Four additional dashboards over a bundle list:

```python
def plot_action_entropy_curve(bundles, *, out_path, metadata=None) -> Path
def plot_kl_to_lambda_zero(bundles, *, out_path, metadata=None) -> Path
def plot_marginal_entropy_per_stream(bundles, *, out_path, metadata=None) -> Path
def plot_pymdp_summary_panel(bundles, *, out_path,
                              summary: BundleSummary | None = None,
                              metadata=None) -> Path
```

### `metadata.py` (PNG reproducibility tEXt)

```python
FIGURE_METADATA_SCHEMA_VERSION: int
VALID_UNCERTAINTY_SEMANTICS: frozenset[str]

def figure_metadata(*, source_script: str, source_function: str,
                    hyperparameters: Mapping[str, Any] | None = None,
                    statistics: Mapping[str, Any] | None = None,
                    extra: Mapping[str, Any] | None = None,
                    project_root: Path | None = None) -> dict[str, str]
def summarize_array(values: Any) -> dict[str, Any]
def figure_statistics(fig: Any) -> dict[str, Any]
def read_figure_metadata(png_path: Path) -> dict[str, str]
def has_project_metadata(png_path: Path) -> bool
```

`figure_metadata` builds a stable `project.*` tEXt block embedded
into every emitted PNG via Matplotlib's `savefig(metadata=...)`:
source script + function, hyperparameter snapshot (JSON),
optional statistics (JSON), git revision, ISO-8601 UTC timestamp. The
shared save helper adds `project.figure_statistics` automatically.
Schema v2 records figure size, axes, labels, limits, legend labels,
line summaries, image-array summaries, collection summaries for scatter
/ mesh artists, and actual Matplotlib font sizes for titles, axis
labels, tick labels, legends, and stat/provenance annotations.

### `multi_k_plots.py` (T1/T2/T3 wave-1 helpers)

Figure helpers consumed by `scripts/simulate_multi_k.py`,
`scripts/simulate_long_horizon.py`, and
`scripts/simulate_revertibility.py`. Inputs are pre-computed records
emitted by the corresponding `simulation/` modules.

```python
# T1 — K>2 multi-K experiments
def plot_multi_k_total_correlation(
    results_by_k: Mapping[int, Sequence], *, out_path, metadata=None,
) -> Path
def plot_multi_k_tt_rank_profile(
    results_by_k, *, out_path, lam_index=-1, metadata=None,
) -> Path
def plot_multi_k_aligned_mass(
    results_by_k, *, out_path, metadata=None,
) -> Path

# T2 — long-horizon habit-accumulation rollout
def plot_long_horizon_marginals(result, *, out_path, metadata=None) -> Path
def plot_long_horizon_steady_state(result, *, out_path, metadata=None) -> Path

# T3 — m-projection / revertibility witness
def plot_revertibility_witness(records, *, out_path, metadata=None) -> Path
```

### `robustness_plots.py` (stress-test sidecar figures)

Figure helpers consumed by `scripts/simulate_robustness.py`. Inputs are
pre-computed robustness rows, ablation rows, or long-horizon replicate
results; the functions only arrange panels, legends, statistic boxes,
and PNG metadata-compatible matplotlib artists.

```python
def plot_robustness_tc_envelopes(rows, *, out_path, metadata=None) -> Path
def plot_robustness_half_saturation(summaries, *, out_path, metadata=None) -> Path
def plot_robustness_decomposition_residuals(summaries, *, out_path, metadata=None) -> Path
def plot_coupling_ablation_summary(rows, *, out_path, metadata=None) -> Path
def plot_marginal_null_control_summary(rows, *, out_path, metadata=None) -> Path
def plot_long_horizon_replicate_envelope(results, *, out_path, metadata=None) -> Path
def plot_interaction_robustness_summary(summaries, *, out_path, metadata=None) -> Path
def plot_long_horizon_seed_diagnostics(diagnostics, *, tolerance, out_path, metadata=None) -> Path
def plot_long_horizon_threshold_sensitivity(
    diagnostics, *, thresholds, canonical_tolerance, out_path, metadata=None
) -> Path
```

### `pymdp_figures.py` (pymdp simulation figures)

Importable figure builders for the pymdp POMDP pipeline. Re-exported by
``scripts/simulate_pymdp.py`` for backwards-compatible test entry points.

Module constants: ``SOURCE_SCRIPT``, ``FIG_DIR``, ``SIM_DIR``, ``LOGGER``.

```python
def build_metadata(source_function: str, **extra: object) -> dict[str, Any]
def hyperparam_snapshot(**extra: object) -> dict[str, Any]
def figure_pymdp_lambda_sweep() -> tuple[Path, Path]
def figure_pymdp_rollout() -> Path
def figure_pymdp_free_energies() -> tuple[Path, Path, *tuple[Path, ...]]
```

### `analytical_figures.py` (closed-form / lean mirror figures)

Thin orchestrators that compute analytical quantities via `lean/` and
`simulation.hyperparameters`, then delegate plotting to the shared
visualization helpers. Each `figure_*` returns the written PNG path;
`emit_all_figures` runs the full analytical figure suite.

```python
def figure_ising_mi_curve() -> Path
def figure_free_energy_curve() -> Path
def figure_coupling_tax_quadratic() -> Path
def figure_phase_diagram() -> Path
def figure_optimal_lambda() -> Path
def figure_schmidt_rank_vs_lambda() -> Path
def figure_phase_landscape() -> Path
def figure_schmidt_entropy_surface() -> Path
def figure_joint_heatmap_with_marginals() -> Path
def figure_archetype_dendrogram() -> Path
def figure_tensor_train_ranks() -> Path
def figure_log_weight_flow() -> Path
def figure_kl_geodesic_in_simplex() -> Path
def figure_lambda_star_locus() -> Path
def figure_coupling_graph() -> Path | None
def emit_all_figures() -> list[Path]
```

---
