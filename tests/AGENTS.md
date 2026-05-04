# AGENTS.md — `tests/`

## Constitution

1. **No mocks.**  The template-wide rule.  Use real arrays
   (`np.random.default_rng(seed=42).dirichlet(...)`), real files
   (`tmp_path`), real subprocesses.
2. **Bare imports.**  `from coupling import …` — never relative.
3. **One assertion focus per test.**  A test name should describe the
   property being checked; the body should not branch on multiple
   independent properties.
4. **Numerical tolerances** as described in [`README.md`](README.md):
   `1e-12` for exact, `1e-9` for log-arithmetic.
5. **Cover the error path.**  For every public function, add at least
   one negative test (shape mismatch, zero mass, out-of-range index).
6. **Coverage floor: 90 %.**  Run
   `pytest tests/ --cov=src --cov-fail-under=90` before commit.

## Adding a test

1. Pick or create the file `test_<module>.py` matching the module
   under test.
2. Use a small, deterministic example you can derive by hand if
   possible.  For random sampling use `np.random.default_rng(seed=…)`.
3. Add the test name to the "Notable invariants" table in
   [`README.md`](README.md) of this directory if it checks a
   manuscript theorem.

## Cross-track invariant

Every numerically-verifiable statement in
[`../lean/ActinfPolicyEntanglement/`](../lean/ActinfPolicyEntanglement/)
should have a corresponding test here that runs the matching Python
function and checks the property to floating-point tolerance.  This
test acts as the *sanity rail* for the Lean theorem when its `sorry`
is later discharged via Mathlib.

## Anti-patterns to avoid

* `pytest.skip("temporary")` without a tracking issue — fail loudly.
* `assert ... or True` — always make the assertion strict.
* `random.seed(...)` without a default RNG — use
  `np.random.default_rng(seed=...)` for full determinism.
* Asserting on inexact-equality of floats with `==` — use `abs(a-b) < tol`
  or `np.allclose`.
