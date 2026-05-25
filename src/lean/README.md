# `src/lean/`

NumPy analytical mirrors of every concept in the Lean 4 boundary
fragment under
[`../../lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/).
Pure compute — no `pymdp`, no `matplotlib`, no I/O.  Public symbols
are re-exported from `lean/__init__.py`.

See parent docs: [`../AGENTS.md`](../AGENTS.md), [`../README.md`](../README.md).
Subpackage rules: [`AGENTS.md`](AGENTS.md).

## Module map

| Module | Mirrors Lean | Exports |
|---|---|---|
| [`joint_dist.py`](joint_dist.py) | `JointDist` | `is_pmf`, `is_non_negative`, `normalize`, `mean_field_to_joint`, `joint_marginal`, `joint_marginals`, `is_mean_field`, `m_projection` |
| [`coupling.py`](coupling.py) | `Coupling` | `trivial_coupling`, `entangled_prior_unnormalised`, `entangled_prior`, `entangled_posterior`, `expected_value`, `entangled_log_weight_affine_in_lambda`, `coupling_log_weight` |
| [`free_energy.py`](free_energy.py) | `FreeEnergy` | `_safe_log` (numerical hygiene), `shannon_entropy`, `kl_divergence`, `joint_entropy`, `marginal_entropy`, `total_correlation`, `total_correlation_via_kl`, `free_energy`, `marginal_free_energy` |
| [`geometry.py`](geometry.py) | `Geometry` | `is_in_mean_field_submanifold`, `m_projection_minimises_kl`, `pythagorean_residual`, `is_e_geodesic`, `revertibility`, `coupling_pays_off`, `coupling_log_weight_affine_check` |
| [`spectral.py`](spectral.py) | `Spectral` | `Archetype`, `schmidt_rank`, `schmidt_decomposition`, `entanglement_entropy`, `schmidt_rank_one_iff_mean_field`, `tensor_train_ranks`, `entanglement_spectrum`, `archetype_marginal_pattern` |
| [`heterogeneous.py`](heterogeneous.py) | `Heterogeneous` | `InferenceMode`, `is_planning_stream`, `is_reflexive_stream`, `is_purely_reflexive`, `is_purely_planning`, `is_heterogeneous`, `coupling_norm_sq`, `fixed_reflexive_posterior`, `coupling_tax`, `quadratic_bound_curvature`, `coupling_tax_within_quadratic_bound` |
| [`bernoulli_toy.py`](bernoulli_toy.py) | `BernoulliToy` | `ising_coupling`, `symmetric_mean_field_prior`, `ising_mutual_information`, `ising_joint_posterior`, `empirical_mutual_information`, `optimal_lambda`, `ising_free_energy_curve`, `coupling_phase_at`, `is_mean_field_at_zero` |
| [`decomposition.py`](decomposition.py) | `Decomposition` | `DecompositionTerms`, `sum_marginal_free_energies`, `coupling_cost_term`, `coupling_prior_term`, `multi_information_term`, `total_correlation_gain` (Lean-named synonym), `entanglement_decomposition_rhs`, `free_energy_against_entangled_prior`, `decomposition_at_zero`, `coupling_pays_for_itself` |
| [`invariants.py`](invariants.py) | (no Lean mirror) | `SweepGrid`, `ising_invariants`, `free_energy_invariants`, `optimal_lambda_invariants`, `phase_invariants`, `marginal_invariants`, `decomposition_invariants`, `coupling_pays_invariants`, `affine_log_weight_invariants`, `all_invariants` — produce project-local `reporting.interactive_dashboard.Invariant` records for the dashboard / plaintext report |

## Conventions

* Public APIs require `numpy.typing.NDArray[np.float64]` (aliased
  `ArrayF`) or scalar / dataclass inputs and outputs; shape mismatches
  raise `ValueError` with informative messages.
* `_safe_log` (in `free_energy.py`) floors at `1e-300`; use it inside
  `∑ q · log q` patterns where zero entries should not propagate.
* `multi_information_term` is the preferred name; `total_correlation_gain`
  is the Lean-named synonym (`totalCorrelationGain`).
* `invariants.py` is the only module here that imports from
  `infrastructure/`; treat it as project-local glue, not an exemplar.
