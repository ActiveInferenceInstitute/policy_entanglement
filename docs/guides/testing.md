# Testing strategy

## No-mocks policy

This project adheres to the parent template's *no-mocks* policy:

> All tests must use real numerical examples; no `MagicMock`,
> `mocker.patch`, `unittest.mock`, or any mocking framework.

The reasons:

1. **Numerical claims need numerical verification.**  Mocks give you
   the answer you wanted, not the answer the math gives you.
2. **The Lean side exposes witness-form analytic obligations instead
   of hidden `sorry` placeholders.**  The Python tests are the sanity
   rail that catches drift while the separate MathlibProofs layer is
   developed.
3. **Reproducibility.**  A test you can run by hand (with deterministic
   seeds) is easier to debug than one that lives behind a mock.

## Coverage

| Floor | Current | Test count |
|---|---|---|
| ≥ 95 % (CI gate) | live % from gate | live collection count from `output/reports/test_results.json` |

Coverage and test count are tracked in
[`../reference/veridical_status.md`](../reference/veridical_status.md);
the release reports provide the live values for the current checkout.
To inspect them directly:

```bash
cd projects/actinf_policy_entanglement_lean
uv run pytest --co -q | tail -1                    # collected count
uv run pytest tests/ --cov=src -q | tail -3        # coverage line
```

The seven `src/` packages (`lean/`, `simulation/`, `visualizations/`,
`manuscript/`, `gates/`, `orchestration/`, `dashboard_types/`) are
exercised by the test suite. Prefer **direct library imports**
(`from gates.regression_gate import …`, `from orchestration.run_all import …`)
so coverage attributes to `src/` rather than only hitting thin
`scripts/` wrappers via subprocess.

Refresh with:

```bash
uv run --active --group sim --group viz pytest tests/ \
  --cov=src --cov-report=term --cov-fail-under=95 -q
```

Most uncovered lines are defensive guards that can only fire on
contradictory analytic input or on an optional dependency that is not
installed (pymdp / networkx / seaborn).  See
[`../reference/python_api.md`](../reference/python_api.md) for the API.

## What we test

| Property | Test file |
|---|---|
| `is_pmf` correctly detects normalized, non-normalized, and negative inputs | `test_joint_dist.py` |
| `mean_field_to_joint` is the outer product, recovers marginals | `test_joint_dist.py` |
| `entangled_prior` and `entangled_posterior` produce valid PMFs and concentrate at high λ | `test_coupling.py` |
| `entangled_log_weight_affine_in_lambda` returns the correct slope | `test_coupling.py` |
| Shannon entropy: uniform → log K, delta → 0 | `test_free_energy.py` |
| KL: self → 0, absolute-continuity violation → ∞ | `test_free_energy.py` |
| Total correlation: 0 ↔ mean-field, KL-form matches direct form | `test_free_energy.py` |
| `m_projection` minimizes KL over mean-fields (Prop 7.2) | `test_geometry.py` |
| Pythagorean residual ≈ 0 for any reference | `test_geometry.py` |
| `{q_λ}` is e-geodesic at every vertex (Theorem 7.4) | `test_geometry.py` |
| `revertibility` returns the m-projection | `test_geometry.py` |
| Schmidt rank: 1 for outer-product, 2 for perfectly-correlated, > 2 for deeper coupling | `test_spectral.py` |
| Schmidt-rank-1 ⇔ mean-field (Prop 8.1) | `test_spectral.py` |
| Tensor-train ranks for K=3 perfectly-correlated and uniform | `test_spectral.py` |
| Closed-form Ising MI matches empirical TC | `test_bernoulli_toy.py` |
| Optimal λ is monotonic, saturating, even-extension | `test_bernoulli_toy.py` |
| Coupling tax is 0 for purely reflexive / planning ensembles, > 0 for heterogeneous | `test_heterogeneous.py` |
| Coupling tax stays inside its O(λ²) envelope (`thm_8_1`) | `test_heterogeneous.py` |
| Entanglement-decomposition RHS is finite and reduces correctly at λ = 0 (`thm_4_1`) | `test_decomposition.py` |
| Coupling-pays-for-itself fires on TC increase | `test_decomposition.py` |

## Round-3 lock-down tests (2026-05-12)

A set of **35 round-3-added tests** pin the round-3 invariants
on top of the round-2 baseline; together with the round-2 set the
total of round-checkpoint lock-down tests is well over 45.  Key
additions:

| Invariant | Test |
|---|---|
| `lean_structure_count == 11` (includes `FloatRealResidualWitness` scaffold plus round-2/round-3 witness structures) | `test_manuscript_variables_pipeline.py::test_lean_structure_count_is_eleven` |
| `lean_total_declarations == lean_def_count + lean_theorem_count + lean_structure_count` (current live total: 126 = 39 + 76 + 11) | `test_manuscript_variables_pipeline.py::test_lean_total_declarations_is_derived` |
| Legacy key `lean_inductive_count` has been removed | `test_manuscript_variables_pipeline.py::test_lean_inductive_count_renamed_to_structure_count` |
| `[[VAR:run_all_script_count]]` resolves and equals `len(run_all.SCRIPTS)` | `test_manuscript_variables_pipeline.py::test_run_all_script_count_present` |
| New `SpectralWitnesses.lean` and `ConnectionsWitnesses.lean` modules build successfully (their existence is asserted via the structure-count test and the lake-build smoke gate) | `tests/lean/test_lean_build.py` |
| Multi-K Ising sweep numerics (`multi_k_summary.json`, the three multi-K figures) reproduce under fixed seed | [`tests/test_multi_k_experiments.py`](../../tests/test_multi_k_experiments.py) |
| Long-horizon rollout converges; `long_horizon_steady_state_kl ≤ tol` | [`tests/test_long_horizon.py`](../../tests/test_long_horizon.py) |
| Revertibility KL identity `D_KL(q_λ ‖ \hat m(q_λ)) = I(q_λ)` holds across the revertibility sweep | [`tests/test_revertibility.py`](../../tests/test_revertibility.py) |
| 47 dashboard invariants registered (round-3 += 1 over round-2's 46) | [`tests/test_invariants_and_dashboard.py`](../../tests/test_invariants_and_dashboard.py) |
| `mi_derivative_covariance` equation registered in `labels.yaml` | covered by `test_manuscript_registry.py` + `test_equation_numbering.py` (registry round-trip) |

## Determinism

* No global RNG; tests use `np.random.default_rng(seed=42)` (or
  similar) when randomness is needed.
* Tolerances are explicit (`1e-12` for exact, `1e-9` for log-arithmetic).
* No `time.sleep`, no `pytest.skipif(condition based on env)`.

## Running locally

```bash
# from the project directory:
uv run pytest tests/ --cov=src --cov-report=term-missing
```

## CI

The parent template's GitHub Actions workflow runs:

```bash
uv run pytest projects/actinf_policy_entanglement_lean/tests/ \
   --cov=projects/actinf_policy_entanglement_lean/src \
   --cov-fail-under=95
```

If you bump the coverage floor, sync
[`../pyproject.toml`](../../pyproject.toml) so local + CI stay aligned.
