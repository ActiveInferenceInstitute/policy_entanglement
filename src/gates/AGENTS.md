# AGENTS.md — `src/gates/`

## Purpose

Parameterised pipeline-gate logic. The thin script wrapper
[`../../scripts/regression_gate.py`](../../scripts/regression_gate.py)
bootstraps the project paths and re-exports every symbol below so the
existing tests (which load the wrapper via
:func:`importlib.util.spec_from_file_location`) continue to resolve
helpers as module attributes.

The package name `gates` (not `validation`) avoids the namespace
collision with [`src/manuscript/validation.py`](../manuscript/validation.py),
which would otherwise shadow `import validation` because
`scripts/_bootstrap.py` puts `src/manuscript/` on `sys.path` as a
bare-import-friendly entry.

## Modules

| Module | Purpose |
|---|---|
| [`regression_gate.py`](regression_gate.py) | Compares fresh pytest + coverage + dashboard-invariant + Lean-budget snapshots against `scripts/regression_baseline.json`; returns non-zero on any silent degradation. Pure helpers (`_parse_pytest_counts`, `_critical_module_coverage_issues`, `_coverage_percent_from_json`, `_count_invariants`, `_coverage_fail_under`) take no project state; orchestrator (`gate`) takes `project_root`, `scripts_dir`, optional `baseline_path`, and `update_baseline`. |

## Contract

* Pure helpers (`_parse_pytest_counts`, `_critical_module_coverage_issues`,
  `_coverage_percent_from_json`, `_count_invariants`, `_coverage_fail_under`) accept all paths as
  arguments and have no module-level side effects — they are exercised by
  [`tests/test_regression_gate.py`](../../tests/test_regression_gate.py) and
  [`tests/coverage/test_coverage_95_final.py`](../../tests/coverage/test_coverage_95_final.py).
* `gate()` derives `output/reports/*` paths from `project_root` and runs
  `build_lean.py` via `subprocess` (no Lean import dependency in this layer).
* `CRITICAL_COVERAGE_MODULES` is the per-module coverage floor for **five**
  release-blocking modules (`status`, `pdf_validation`, `metadata`,
  `parameter_sweep` at **95%**; `btai_plots` at **90%**). Override with the
  second argument to `_critical_module_coverage_issues` in tests.
* Total ``src/`` coverage floor is read once from
  ``pyproject.toml`` → ``tool.coverage.report.fail_under`` via
  :func:`_coverage_fail_under` (currently **95%**).
* The baseline JSON is authored under `scripts/regression_baseline.json` so
  the gate contract is co-located with the CLI (callers pass the path in).
* Before each gate pytest subprocess, `_clear_bytecode_cache()` removes
  stale `__pycache__` / `.pyc` artifacts. The gate intentionally omits
  `--import-mode=importlib` (duplicates module paths and depresses
  measured `src/` coverage without adding staleness protection beyond
  the cache purge).
