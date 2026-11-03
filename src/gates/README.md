# `src/gates/`

Parameterised release-gate logic, imported as `gates`.

| File | Role |
|---|---|
| `regression_gate.py` | Compares fresh pytest, coverage, dashboard-invariant and Lean-budget results with the recorded baseline; non-zero on any degradation. |
| `regression_baseline.py` | Baseline I/O and comparison helpers. |
| `regression_pytest.py` | Pytest subprocess runner and coverage parsers. |

The thin wrapper `scripts/regression_gate.py` re-exports these symbols; see
[`../../scripts/AGENTS.md`](../../scripts/AGENTS.md). The baseline is
`scripts/regression_baseline.json`, and the coverage floor is read from
`pyproject.toml`.
