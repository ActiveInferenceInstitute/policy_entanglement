# Test Patterns Reference

Testing conventions for the actinf zero-mock suite. See also
[`AGENTS.md`](AGENTS.md) and [`README.md`](README.md).

## Zero-Mock Enforcement

Forbidden everywhere under `tests/`:

- `unittest.mock`, `MagicMock`, `create_autospec`, `@patch`, `mocker.patch`
- Synthetic result objects that bypass real algorithms
- Stubbed algorithm bodies

Use real `numpy` arrays, `tmp_path` files, and subprocess CLI calls.

### Allowed orchestration boundaries

- **`pytest.MonkeyPatch`** on module attributes (`subprocess.run`, `PATH`,
  `load_project_status`, …) when the test still executes real library code
- **Fake `lake` scripts** in `tmp_path/bin` for Lean gate unit tests (no mock
  of Python logic — only the external toolchain)
- **`REGRESSION_GATE_USE_EXISTING_TEST_REPORT=1`** for regression-gate tests
  that must not re-run the full suite

Examples: [`test_mathlib_proofs_gate_unit.py`](test_mathlib_proofs_gate_unit.py),
[`test_coverage_95_final.py`](test_coverage_95_final.py),
[`test_regression_gate.py`](test_regression_gate.py).

## Mathlib / Lean Serialization

MathlibProofs tests that invoke real `lake build` or `lake env lean` share
`output/.cache/mathlib_proofs.lake.lock` via
[`lean._lake_lock.mathlib_proofs_lock`](../src/lean/_lake_lock.py). Do not
nest lock contexts in one process (macOS `flock` is not re-entrant).

Live Mathlib audit: [`test_mathlib_axiom_audit.py`](test_mathlib_axiom_audit.py)
(xfails honestly when `lake` is absent).

## Fixtures

Shared session fixtures live in [`conftest.py`](conftest.py):

- `actinf_project_root` — project directory
- `lake_available` — whether `lake` is on `PATH`

Prefer `np.random.default_rng(seed=…)` over legacy `random.seed`.

## Markers

- `@pytest.mark.requires_pymdp` — needs `uv sync --group sim`
- `@pytest.mark.slow` — long-horizon or full-grid sweeps (optional CI skip)

## Coverage Push Files

| File | Role |
| --- | --- |
| `test_coverage_95_final.py` | Refactored library branches (gates, orchestration, readiness) |
| `test_coverage_library_gaps.py` | Cross-cutting error paths |
| `test_branch_coverage_push.py` | Conditional branches in lean/simulation gates |

Run the 95 % gate before commit:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=95 -q
```
