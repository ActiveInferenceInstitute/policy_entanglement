# `src/` — Python numerical companion

A five-subpackage Python companion to the Lean boundary fragment.
Used by:

* the test suite ([`../tests/`](../tests/)),
* the figure scripts ([`../scripts/`](../scripts/)),
* the manuscript renderer ([`../scripts/inject_manuscript_variables.py`](../scripts/inject_manuscript_variables.py)),
* and downstream agents that want to verify a Lean claim numerically.

`pythonpath` is set to `src/` by
[`../pyproject.toml`](../pyproject.toml), so every consumer uses the
canonical namespaced subpackage path:

```python
from lean.coupling import entangled_posterior
from simulation.specs import CoupledEnsembleSpec
from visualizations.heatmaps import plot_lambda_utility_heatmap
from manuscript.registry import load_registry
from reporting.interactive_dashboard import Invariant
```

Intra-subpackage imports use the relative form
(`from .coupling import …` inside `src/lean/free_energy.py`).
Bare imports (`from coupling import …`) are no longer supported.

## Subpackage map

### [`lean/`](lean/) — analytical mirrors of the Lean boundary fragment

| Module | Mirrors Lean | Contents |
|---|---|---|
| [`lean/joint_dist.py`](lean/joint_dist.py) | `JointDist` | `is_pmf`, `is_non_negative`, `normalize`, `mean_field_to_joint`, `joint_marginal`, `joint_marginals`, `is_mean_field`, `m_projection` |
| [`lean/coupling.py`](lean/coupling.py) | `Coupling` | `trivial_coupling`, `entangled_prior_unnormalised`, `entangled_prior`, `entangled_posterior`, `expected_value`, `entangled_log_weight_affine_in_lambda`, `coupling_log_weight` |
| [`lean/free_energy.py`](lean/free_energy.py) | `FreeEnergy` | `shannon_entropy`, `kl_divergence`, `joint_entropy`, `marginal_entropy`, `total_correlation`, `total_correlation_via_kl`, `free_energy`, `marginal_free_energy` |
| [`lean/geometry.py`](lean/geometry.py) | `Geometry` | `is_in_mean_field_submanifold`, `m_projection_minimises_kl`, `pythagorean_residual`, `is_e_geodesic`, `revertibility`, `coupling_pays_off`, `coupling_log_weight_affine_check` |
| [`lean/spectral.py`](lean/spectral.py) | `Spectral` | `Archetype`, `schmidt_rank`, `schmidt_decomposition`, `entanglement_entropy`, `schmidt_rank_one_iff_mean_field`, `tensor_train_ranks`, `entanglement_spectrum`, `archetype_marginal_pattern` |
| [`lean/bernoulli_toy.py`](lean/bernoulli_toy.py) | `BernoulliToy` | `ising_coupling`, `symmetric_mean_field_prior`, `ising_mutual_information`, `ising_joint_posterior`, `empirical_mutual_information`, `optimal_lambda`, `ising_free_energy_curve`, `coupling_phase_at`, `is_mean_field_at_zero` |
| [`lean/heterogeneous.py`](lean/heterogeneous.py) | `Heterogeneous` | `InferenceMode`, `is_planning_stream`, `is_reflexive_stream`, `is_purely_reflexive`, `is_purely_planning`, `is_heterogeneous`, `coupling_norm_sq`, `fixed_reflexive_posterior`, `coupling_tax`, `quadratic_bound_curvature`, `coupling_tax_within_quadratic_bound` |
| [`lean/decomposition.py`](lean/decomposition.py) | `Decomposition` | `DecompositionTerms`, `sum_marginal_free_energies`, `coupling_cost_term`, `coupling_prior_term`, `multi_information_term`, `total_correlation_gain`, `entanglement_decomposition_rhs`, `free_energy_against_entangled_prior`, `decomposition_at_zero`, `coupling_pays_for_itself` |
| [`lean/invariants.py`](lean/invariants.py) | (no Lean mirror — numerical-witness layer) | `SweepGrid`, `ising_invariants`, `free_energy_invariants`, `optimal_lambda_invariants`, `phase_invariants`, `marginal_invariants`, `decomposition_invariants`, `coupling_pays_invariants`, `affine_log_weight_invariants`, `all_invariants` (depends on project-local `reporting.interactive_dashboard.Invariant`) |

### [`simulation/`](simulation/) — pymdp 1.0.1 POMDP harness

| Module | Contents |
|---|---|
| [`simulation/specs.py`](simulation/specs.py) | `StreamSpec`, `CoupledEnsembleSpec` |
| [`simulation/builders.py`](simulation/builders.py) | `two_state_identity_likelihood`, `two_action_swap_transitions`, `make_bernoulli_stream`, `ising_coupling_tensor`, `make_ising_ensemble` |
| [`simulation/agents.py`](simulation/agents.py) | `pymdp_available`, `build_pymdp_agent`, `build_pymdp_agents`, `PYMDP_INSTALL_HINT` |
| [`simulation/inference.py`](simulation/inference.py) | `per_stream_efe`, `per_stream_policy_posterior`, `coupled_policy_posterior`, `FreeEnergyBundle`, `variational_free_energy`, `expected_free_energy_under_posterior`, `coupling_energy`, `free_energy_bundle`, `free_energy_curve` |
| [`simulation/rollout.py`](simulation/rollout.py) | `RolloutStep`, `Rollout`, `simulate_coupled_rollout` |
| [`simulation/sweep.py`](simulation/sweep.py) | `LambdaSweepResult`, `lambda_sweep`, `total_correlation_curve`, `marginal_trajectory` |
| [`simulation/statistics.py`](simulation/statistics.py) | `BundleSummary`, `QuantileEnvelope`, `pymdp_summary_statistics`, `summary_to_var_dict`, `quantile_envelope_over_sweeps`, `is_monotone_nondecreasing`, `total_correlation_saturation_index` (reduce a list of `FreeEnergyBundle` records to scalars / quantile envelopes for `manuscript_variables.json`) |
| [`simulation/logging_utils.py`](simulation/logging_utils.py) | `RunLogger`, `TimedRecord`, `default_logger` (append-only JSONL run log; **only `simulation/` module that touches disk** — append-only, gated by `PYMDP_RUN_LOG_DISABLED`) |
| [`simulation/hyperparameters.py`](simulation/hyperparameters.py) | `FigureGrid`, `PARAMETER_SWEEP_LAMBDAS`, `COUPLING_TAX_LAMBDAS`, `PHASE_DIAGRAM_LAMBDAS`, `PYMDP_SWEEP_LAMBDAS`, `PYMDP_ROLLOUT_*`, sentinel-λ tuples, `grid_count`, `figure_hyperparameter_summary` (single source of truth for every grid / seed / horizon) |

### [`visualizations/`](visualizations/) — matplotlib figure helpers

| Module | Contents |
|---|---|
| [`visualizations/setup.py`](visualizations/setup.py) | `deterministic_setup`, `ensure_outdir` |
| [`visualizations/heatmaps.py`](visualizations/heatmaps.py) | `plot_lambda_utility_heatmap`, `plot_schmidt_entropy_surface` |
| [`visualizations/joint_plots.py`](visualizations/joint_plots.py) | `plot_joint_heatmap_with_marginals` |
| [`visualizations/spectral_plots.py`](visualizations/spectral_plots.py) | `plot_archetype_dendrogram`, `plot_tensor_train_rank_surface` |
| [`visualizations/trajectory_plots.py`](visualizations/trajectory_plots.py) | `plot_rollout_marginals` |
| [`visualizations/graphs.py`](visualizations/graphs.py) | `has_seaborn`, `has_networkx`, `plot_coupling_graph` |
| [`visualizations/log_weight.py`](visualizations/log_weight.py) | `plot_log_weight_flow` |
| [`visualizations/geodesic.py`](visualizations/geodesic.py) | `plot_kl_geodesic_in_simplex`, `plot_lambda_star_locus` |
| [`visualizations/free_energy_plots.py`](visualizations/free_energy_plots.py) | `plot_vfe_decomposition`, `plot_efe_under_posterior`, `plot_entropy_decomposition`, `plot_action_distribution_evolution`, `plot_free_energy_panel`, `plot_bundle_quantile_envelope` (consume `FreeEnergyBundle` lists) |
| [`visualizations/pymdp_extras.py`](visualizations/pymdp_extras.py) | `plot_action_entropy_curve`, `plot_kl_to_lambda_zero`, `plot_marginal_entropy_per_stream`, `plot_pymdp_summary_panel` (additional pymdp-grounded dashboards driven by bundle lists + summary statistics) |
| [`visualizations/metadata.py`](visualizations/metadata.py) | `figure_metadata`, `read_figure_metadata`, `has_project_metadata` (PNG `tEXt`-chunk reproducibility metadata: source script + function, hyperparameter snapshot, git rev, ISO timestamp) |

### [`manuscript/`](manuscript/) — auto-injection / validation toolkit

| Module | Contents |
|---|---|
| [`manuscript/registry.py`](manuscript/registry.py) | `Figure`, `Equation`, `Citation`, `Section`, `TheoremEntry`, `LabelsRegistry`, `CitationRegistry`, `Registry`, `load_registry` |
| [`manuscript/tokens.py`](manuscript/tokens.py) | `FIG_RE`, `FIGREF_RE`, `EQ_RE`, `EQREF_RE`, `VAR_RE`, `CITATION_RE`, `CITELIST_RE`, `SEC_RE`, `SECREF_RE`, `THM_RE`, `THMREF_RE`, `LEAN_RE`, `iter_tokens` |
| [`manuscript/renderer.py`](manuscript/renderer.py) | `RenderResult`, `render_section`, `render_all` |
| [`manuscript/equation_numbering.py`](manuscript/equation_numbering.py) | `file_to_section_number`, `precompute_equation_numbers`, `assign_within_section_numbers`, `retag_display_math`, `section_equation_count` (auto-numbers display equations as `S.K`) |
| [`manuscript/lean_extract.py`](manuscript/lean_extract.py) | `LeanSnippet`, `load_lean_snippets`, `render_lean_snippet` (live extraction of theorems from `lean/ActinfPolicyEntanglement/<Module>.lean`) |
| [`manuscript/bibliography.py`](manuscript/bibliography.py) | `auto_bibliography`, `write_references_bib` |
| [`manuscript/validation.py`](manuscript/validation.py) | `ManuscriptValidationReport`, `validate_undefined_tokens`, `validate_hyperlinks`, `validate_figure_files`, `validate_variables_against_ranges`, `find_hardcoded_refs`, `find_hardcoded_numeric_literals`, `validate_section_references`, `validate_lean_wiring`, `collect_section_subheadings`, `collect_top_level_sections`, `section_paths`, `validate_manuscript_tree` |

### [`reporting/`](reporting/) — project-local dashboard/report helpers

| Module | Contents |
|---|---|
| [`reporting/interactive_dashboard.py`](reporting/interactive_dashboard.py) | `Control`, `Panel`, `Invariant`, `InteractiveDashboard` (standalone-safe HTML/JSON/plaintext dashboard and invariant-report builder used by `scripts/build_dashboard.py` and `lean/invariants.py`) |

## Conventions

* **Inputs**: `numpy.ndarray[float64]` (use `np.asarray(..., dtype=np.float64)`).
* **Outputs**: float, ndarray, list, or dataclass — never `None` (except
  the optional `viz`-group plots that gracefully degrade to `None`).
* **Validation**: shape mismatches raise `ValueError` with a helpful
  message; out-of-range indices raise `IndexError`.
* **Determinism**: no module-level RNG; tests use
  `np.random.default_rng(seed=…)`.
* **Numerical hygiene**: `_safe_log` in `lean/free_energy.py` floors at
  `1e-300` so `q · log q` is stable at zero entries.

## Coverage snapshot

Refresh with `uv run pytest tests/ --cov=src --cov-report=term`; full
contract is in [`../docs/reference/python_api.md`](../docs/reference/python_api.md).

## Quick example

```python
import numpy as np
from lean.coupling import entangled_posterior
from lean.free_energy import total_correlation
from lean.spectral import schmidt_rank

mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
J  = np.array([[0.5, -0.5], [-0.5, 0.5]])      # Ising coupling
Kc = np.zeros((2, 2))
G  = [np.zeros(2), np.zeros(2)]

q = entangled_posterior(mf, G, J, Kc, gamma=0.0, lam=2.0)
print("total correlation:", total_correlation(q))   # > 0
print("schmidt rank:    ", schmidt_rank(q))         # 2
```
