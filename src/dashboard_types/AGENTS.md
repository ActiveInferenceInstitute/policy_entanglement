# AGENTS.md — `src/dashboard_types/`

Shared dashboard datatypes and the actinf dashboard builder consumed by
[`reporting.interactive_dashboard`](../reporting/_interactive_dashboard_local.py)
and [`scripts/build_dashboard.py`](../../scripts/build_dashboard.py).

## Modules

| File | Role |
| --- | --- |
| [`dashboard.py`](dashboard.py) | `Panel`, `Control`, `Invariant` datatypes; `build_dashboard_payload`, `build_dashboard`, CLI `main` |

## Conventions

- **Thin script:** `scripts/build_dashboard.py` delegates to `dashboard.main`.
- **Plotly payloads:** panels are JSON-serializable trace/layout dicts; no
  mocks in tests — use real sidecar JSON under `tmp_path`.
- **Invariants:** `evaluate_invariants()` returns pass/fail rows written to
  `output/reports/dashboard_invariants.txt` for the regression gate.

## Tests

[`tests/test_dashboard_types.py`](../../tests/test_dashboard_types.py),
[`tests/test_coverage_95_final.py`](../../tests/test_coverage_95_final.py)
(`test_dashboard_types_main_success_and_failure`).
