# `tests/` — No-mocks Python test suite

Mirrors [`../src/`](../src/) module-for-module.  Every test runs real
numerical computations on real `numpy` arrays.  No `MagicMock`, no
`mocker.patch`, no `unittest.mock`.

## Status

| Metric | Value |
|---|---|
| Tests collected | 119 |
| Passing | 119 |
| Coverage on `src/` | 98.37 % |
| Required coverage floor | 90 % |

## Running

```bash
# Full suite + coverage (run from the project directory):
uv run pytest tests/ --cov=src --cov-report=term-missing

# Single file:
uv run pytest tests/test_decomposition.py -v

# Single test:
uv run pytest tests/test_bernoulli_toy.py::test_empirical_mi_matches_closed_form -v
```

## File map

| File | Module under test |
|---|---|
| [`test_joint_dist.py`](test_joint_dist.py) | `joint_dist.py` |
| [`test_coupling.py`](test_coupling.py) | `coupling.py` |
| [`test_free_energy.py`](test_free_energy.py) | `free_energy.py` |
| [`test_geometry.py`](test_geometry.py) | `geometry.py` |
| [`test_spectral.py`](test_spectral.py) | `spectral.py` |
| [`test_bernoulli_toy.py`](test_bernoulli_toy.py) | `bernoulli_toy.py` |
| [`test_heterogeneous.py`](test_heterogeneous.py) | `heterogeneous.py` |
| [`test_decomposition.py`](test_decomposition.py) | `decomposition.py` |

## Conventions

* **Imports**: bare module names (`from coupling import …`) — `pythonpath`
  is set to `../src` by [`../pyproject.toml`](../pyproject.toml).
* **Fixtures**: use `np.random.default_rng(seed=…)` with an explicit
  fixed seed for any randomised test.
* **Numerical tolerances**: `1e-12` for exact arithmetic
  (e.g. `is_pmf` of a uniform), `1e-9` for KL / TC checks involving
  logs.
* **Boundary cases**: every module has tests for
  shape-mismatch / out-of-range / zero-mass inputs that should raise
  `ValueError` or `IndexError`.

## Notable invariants checked

| Invariant | Test |
|---|---|
| Total correlation ≥ 0; = 0 iff mean-field | `test_total_correlation_zero_for_mean_field`, `test_total_correlation_positive_for_correlated` |
| Total correlation = KL to m-projection (Prop 6.3) | `test_total_correlation_via_kl_matches_direct` |
| m-projection minimises KL among mean-fields (Prop 6.2) | `test_m_projection_minimises_kl_against_random_candidate` |
| log-weight is affine in λ (Theorem 6.4) | `test_log_weight_affine_in_lambda_recovers_slope`, `test_coupling_log_weight_is_affine_in_lambda`, `test_is_e_geodesic_for_ising_K2` |
| Pythagorean residual ≈ 0 (Prop 6.5) | `test_pythagorean_residual_zero_for_any_reference` |
| Schmidt rank 1 ⇔ mean-field (Prop 7.1) | `test_schmidt_rank_one_for_outer_product`, `test_schmidt_rank_two_for_correlated_joint`, `test_schmidt_rank_one_iff_mean_field_holds_for_*` |
| Coupling tax ≥ 0; = 0 for pure-mode ensembles | `test_coupling_tax_zero_for_purely_reflexive`, `test_coupling_tax_zero_for_purely_planning`, `test_coupling_tax_positive_for_heterogeneous_at_nonzero_lambda` |
| O(λ²) coupling-tax bound (Theorem 8.1) | `test_coupling_tax_within_quadratic_bound_holds_for_small_lambda` |
| Closed-form vs empirical MI of K=2 Ising | `test_empirical_mi_matches_closed_form` |
