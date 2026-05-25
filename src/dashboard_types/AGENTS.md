# AGENTS.md — `src/dashboard_types/`

Shared dashboard datatypes and the actinf dashboard builder consumed by
[`reporting.interactive_dashboard`](../reporting/_interactive_dashboard_local.py)
and [`scripts/build_dashboard.py`](../../scripts/build_dashboard.py).

## Modules

| File | Role |
| --- | --- |
| [`types.py`](types.py) | `Panel`, `Control`, `Invariant` datatypes and `evaluate()` dispatch |
| [`paths.py`](paths.py) | Project root and `output/` path constants |
| [`cli.py`](cli.py) | `parse_dashboard_args` |
| [`payload.py`](payload.py) | `build_dashboard_payload` — numerical sweep over Lean mirrors |
| [`panels.py`](panels.py) | `build_dashboard`, `write_dashboard`, CLI `main` |
| [`dashboard.py`](dashboard.py) | Backward-compatible re-export facade |

## Conventions

- **Thin script:** `scripts/build_dashboard.py` delegates to `dashboard.main`.
- **Plotly payloads:** panels are JSON-serializable trace/layout dicts; no
  mocks in tests — use real sidecar JSON under `tmp_path`.
- **Invariants:** `evaluate_invariants()` returns pass/fail rows written to
  `output/reports/dashboard_invariants.txt` for the regression gate.

## Tests

[`tests/test_dashboard_types.py`](../../tests/test_dashboard_types.py),
[`tests/coverage/test_coverage_95_final.py`](../../tests/coverage/test_coverage_95_final.py)
(`test_dashboard_types_main_success_and_failure`).
