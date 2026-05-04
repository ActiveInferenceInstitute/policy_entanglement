# Testing strategy

## No-mocks policy

This project adheres to the parent template's *no-mocks* policy:

> All tests must use real numerical examples; no `MagicMock`,
> `mocker.patch`, `unittest.mock`, or any mocking framework.

The reasons:

1. **Numerical claims need numerical verification.**  Mocks give you
   the answer you wanted, not the answer the math gives you.
2. **The Lean side is full of `sorry` placeholders.**  The Python
   tests are the *sanity rail* that catches drift while Mathlib
   proofs land.
3. **Reproducibility.**  A test you can run by hand (with deterministic
   seeds) is easier to debug than one that lives behind a mock.

## Coverage

| Floor | Current | Test count |
|---|---|---|
| 90 % (CI gate) | **96.08 %** | **340** |

The 1357 statements across the four `src/` subpackages
(`lean/`, `simulation/`, `visualizations/`, `manuscript/`) are
exercised by the test suite; refresh with:

```bash
uv run --active --group sim --group viz pytest tests/ \
  --cov=src --cov-report=term --cov-fail-under=90 -q
```

Most uncovered lines are defensive guards that can only fire on
contradictory analytic input or on an optional dependency that is not
installed (pymdp / networkx / seaborn).  See
[`../reference/python_api.md`](../reference/python_api.md) for the API.

## What we test

| Property | Test file |
|---|---|
| `is_pmf` correctly detects normalised, non-normalised, and negative inputs | `test_joint_dist.py` |
| `mean_field_to_joint` is the outer product, recovers marginals | `test_joint_dist.py` |
| `entangled_prior` and `entangled_posterior` produce valid PMFs and concentrate at high λ | `test_coupling.py` |
| `entangled_log_weight_affine_in_lambda` returns the correct slope | `test_coupling.py` |
| Shannon entropy: uniform → log K, delta → 0 | `test_free_energy.py` |
| KL: self → 0, absolute-continuity violation → ∞ | `test_free_energy.py` |
| Total correlation: 0 ↔ mean-field, KL-form matches direct form | `test_free_energy.py` |
| `m_projection` minimises KL over mean-fields (Prop 6.2) | `test_geometry.py` |
| Pythagorean residual ≈ 0 for any reference | `test_geometry.py` |
| `{q_λ}` is e-geodesic at every vertex (Theorem 6.4) | `test_geometry.py` |
| `revertibility` returns the m-projection | `test_geometry.py` |
| Schmidt rank: 1 for outer-product, 2 for perfectly-correlated, > 2 for deeper coupling | `test_spectral.py` |
| Schmidt-rank-1 ⇔ mean-field (Prop 7.1) | `test_spectral.py` |
| Tensor-train ranks for K=3 perfectly-correlated and uniform | `test_spectral.py` |
| Closed-form Ising MI matches empirical TC | `test_bernoulli_toy.py` |
| Optimal λ is monotonic, saturating, even-extension | `test_bernoulli_toy.py` |
| Coupling tax is 0 for purely reflexive / planning ensembles, > 0 for heterogeneous | `test_heterogeneous.py` |
| Coupling tax stays inside its O(λ²) envelope (Theorem 8.1) | `test_heterogeneous.py` |
| Theorem 4.1 RHS is finite and reduces correctly at λ = 0 | `test_decomposition.py` |
| Coupling-pays-for-itself fires on TC increase | `test_decomposition.py` |

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
   --cov-fail-under=90
```

If you bump the coverage floor, sync
[`../pyproject.toml`](../../pyproject.toml) so local + CI stay aligned.
