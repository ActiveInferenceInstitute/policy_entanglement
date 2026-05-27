# AGENTS.md — `src/reporting/`

Interactive dashboard compatibility layer for invariant dashboards and the
plaintext release report. Prefers template `infrastructure.reporting` when the
parent repo is on `PYTHONPATH`; falls back to a local implementation for
standalone private checkouts.

Parent: [`../AGENTS.md`](../AGENTS.md)

## Publication

- DOI: https://doi.org/10.5281/zenodo.20419509
- Source: https://github.com/ActiveInferenceInstitute/policy_entanglement

## Module map

| File | Role |
| --- | --- |
| `interactive_dashboard.py` | Facade — re-exports `InteractiveDashboard`, `Invariant`, `Panel`, `Control` |
| `_interactive_dashboard_local.py` | Standalone dashboard builder when infrastructure is absent |
| `_interactive_dashboard_compat.py` | Template/local adapter shims |
| `_interactive_dashboard_fallback.py` | Minimal fallback panels for headless gates |

## Consumers

- [`../lean/invariants.py`](../lean/invariants.py) — builds `Invariant` records
- [`../../scripts/build_dashboard.py`](../../scripts/build_dashboard.py) — HTML + plaintext invariants
- Gates: `tests/test_invariants_and_dashboard.py`, `scripts/regression_gate.py`

## Rules

- Business logic for invariant *definitions* stays in `src/lean/invariants.py`.
- This package owns presentation / evaluation wiring only.
- Do not hard-code pytest counts or PDF metrics in these docs.
