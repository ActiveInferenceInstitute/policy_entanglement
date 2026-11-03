# `src/dashboard_types/`

Shared dashboard datatypes and the dashboard builder, imported as
`dashboard_types`.

| File | Role |
|---|---|
| `types.py` | `Panel`, `Control`, `Invariant` datatypes and `evaluate()` dispatch. |
| `paths.py` | Project root and `output/` path constants. |
| `cli.py` | `parse_dashboard_args`. |
| `payload.py` | `build_dashboard_payload` — the numerical sweep over the Lean mirrors. |
| `panels.py` | `build_dashboard`, `write_dashboard`, and the CLI `main`. |
| `dashboard.py` | Re-export facade over the modules above. |

Consumed by `reporting.interactive_dashboard` and
`scripts/build_dashboard.py`. Tests:
`tests/test_dashboard_types.py` and
`tests/coverage/test_dashboard_coverage.py`.
