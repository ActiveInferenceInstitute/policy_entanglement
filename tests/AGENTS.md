# AGENTS.md — `tests/`

## Constitution

1. **No mocks.**  The template-wide rule.  Use real arrays
   (`np.random.default_rng(seed=42).dirichlet(...)`), real files
   (`tmp_path`), real subprocesses.
2. **Namespaced imports.**  `from lean.coupling import …`,
   `from simulation.specs import …`,
   `from visualizations.heatmaps import …`,
   `from manuscript.registry import …`. Bare imports are not supported.
3. **One assertion focus per test.**  A test name should describe the
   property being checked; the body should not branch on multiple
   independent properties.
4. **Numerical tolerances** as described in [`README.md`](README.md):
   `1e-12` for exact, `1e-9` for log-arithmetic.
5. **Cover the error path.**  For every public function, add at least
   one negative test (shape mismatch, zero mass, out-of-range index).
6. **Coverage floor: 95 %.**  Run
   `pytest tests/ --cov=src --cov-fail-under=95` before commit.
7. **Test budget = live full-suite count from `output/reports/test_results.json`.**
   See
   [`../docs/reference/statistics_reference.md`](../docs/reference/statistics_reference.md)
   for the per-suite breakdown.  When adding a new module, slot its
   tests into the matching named file (`test_simulation_*.py`,
   `test_manuscript_*.py`, …) rather than creating one-test-per-file.

Library-refactor coverage tests (import `src/` directly):

| File | Covers |
|---|---|
| `test_build_gate_unit.py` | `lean.build_gate` scanners |
| `test_validation_cli_gate.py` | `manuscript.validation_cli` |
| `test_orchestration_unit.py` | `orchestration.build_pdf`, `orchestration.run_all` |
| `coverage/test_coverage_library_gaps.py` | cross-cutting library branches |

## Mathlib / Lean tests

Tests that invoke real `lake` against `lean/MathlibProofs/` serialize through
[`lean._lake_lock.mathlib_proofs_lock`](../src/lean/_lake_lock.py). Prefer the
unit tests in `test_mathlib_proofs_gate_unit.py` (fake `lake` in `tmp_path`) over
adding new concurrent live-`lake` subprocess tests. Live axiom audit:
`test_mathlib_axiom_audit.py` (honest xfail when `lake` is absent).

See [`PATTERNS.md`](PATTERNS.md) for lock and orchestration-boundary rules.

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
test acts as the *sanity rail* for the Lean theorem; the boundary
fragment is sorry-free, but witness-form theorems
(`entanglement_decomposition`, `couplingTax_quadratic_bound`,
`dualFlat_pythagorean_witness`) require the Python tests to validate
that the witness shape matches the analytic claim.

## Anti-patterns to avoid

* `pytest.skip("temporary")` without a tracking issue — fail loudly.
* `assert ... or True` — always make the assertion strict.
* `random.seed(...)` without a default RNG — use
  `np.random.default_rng(seed=...)` for full determinism.
* Asserting on inexact-equality of floats with `==` — use `abs(a-b) < tol`
  or `np.allclose`.
