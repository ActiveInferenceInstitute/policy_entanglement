# Thermo-nuclear Code Quality Review — round 7

**Project:** `actinf_policy_entanglement_lean`  
**Date:** 2026-05-25  
**Prior pass:** round-6 thermo-nuclear (2026-05-23) — library split into `src/gates/`, `src/orchestration/`, `src/manuscript/output_gates/`

## Executive summary

Round-7 decomposed the two largest remaining Python monoliths (`pymdp_validators.py` at 807 lines, `validation.py` at 795 lines), moved revertibility script I/O into `src/simulation/revertibility_pipeline.py`, relocated six coverage-meta test modules under `tests/coverage/`, and completed follow-on splits (dashboard package, readiness emitters, JSON sidecar registry, shared TC helper wiring). **1417** tests pass; `src/` coverage **95.34%** (floor 95%).

## Findings (rubric order)

### 1. Structural regressions since round-6

| ID | Severity | Evidence | Remedy | Disposition |
|----|----------|----------|--------|-------------|
| R1 | LOW | Split pymdp validators broke `OUTPUT_DIR` monkeypatching in gate tests (submodules bound `OUTPUT_DIR` at import) | Central `tests/output_gates_helpers.patch_output_dir` patches all gate modules | **Applied** |

No other structural regressions identified.

### 2. Code-judo / simplification opportunities

| ID | Severity | Evidence | Proposed remedy | Disposition |
|----|----------|----------|-----------------|-------------|
| J1 | HIGH | `output_gates/pymdp_validators.py` — 807 lines, 13 validators | Split into sweep / long-horizon / revertibility / robustness modules; 41-line facade | **Applied** |
| J2 | HIGH | `manuscript/validation.py` — 795 lines mixed scan + check + tree | Split into `validation_report`, `validation_patterns`, `validation_scan`, `validation_checks`; 210-line facade | **Applied** |
| J3 | MEDIUM | `scripts/simulate_revertibility.py` — 165 lines inline CSV/JSON/plot I/O | `simulation/revertibility_pipeline.py` + 48-line script wrapper | **Applied** |
| J4 | MEDIUM | Six `test_coverage_*.py` at repo `tests/` root (~2.2k LOC meta-tests) | Move to `tests/coverage/`; `tests/coverage/README.md`; shared `output_gates_helpers.py` | **Applied** |
| J5 | MEDIUM | `dashboard_types/dashboard.py` (776), `readiness.py` (708), `variables.py` (696) | Split dashboard into `types`/`paths`/`cli`/`payload`/`panels`; `readiness_emit.py`; `_JSON_SIDECAR_REGISTRY` | **Applied** (partial — `hyperparameters.py` still deferred) |
| J8 | HIGH | `validate_free_energy_bundle` duplicated TC/decomposition loops | `validate_tc_decomposition_group` with `check_lhs_rhs` + `finite_columns` | **Applied** |
| J6 | MEDIUM | `reporting/_interactive_dashboard_local.py` (646) duplicates template infra | Prefer `infrastructure.reporting` when on PYTHONPATH | **Applied** (round-8) |
| J7 | LOW | `simulation/robustness*.py` four-module cluster | Consolidate orchestration vs stats after robustness ISA | **Deferred** |

### 3. Spaghetti / branching growth

None introduced in round-7. Facade re-exports preserve import paths; no new ad-hoc conditionals in shared paths.

### 4. Boundary / type-contract problems

| ID | Severity | Evidence | Remedy | Disposition |
|----|----------|----------|--------|-------------|
| B1 | LOW | `validation_checks.py` initially missing `HYPERLINK_RE` import after split | Added explicit pattern imports | **Applied** |

### 5. File-size concerns

| Module | Before | After |
|--------|--------|-------|
| `pymdp_validators.py` | 807 | 41 (facade) |
| `pymdp_sweep_validators.py` | — | 212 |
| `pymdp_long_horizon_validators.py` | — | 251 |
| `pymdp_revertibility_validators.py` | — | 131 |
| `pymdp_robustness_validators.py` | — | 274 |
| `validation.py` | 795 | 210 (facade) |
| `validation_scan.py` | — | 314 |
| `validation_checks.py` | — | 315 |
| `validation_report.py` | — | 81 |
| `validation_patterns.py` | — | 42 |
| `simulate_revertibility.py` | 165 | 30 |
| `dashboard.py` (facade) | 776 | 78 |
| `dashboard_types/panels.py` | — | 483 |
| `readiness_emit.py` | — | 210 |

No file crosses the 1k-line rubric threshold.

### 6. Modularity

Round-7 aligns manuscript validation and pymdp output gates with the round-6 pattern: thin script/CLI facades, domain modules under `src/`, backward-compatible re-exports.

### 7. Legibility

Updated API reference docs: `docs/reference/python_api_manuscript.md`, `docs/reference/python_api_simulation.md`.

## Verification (round-7)

| Gate | Result |
|------|--------|
| `pytest tests/ --cov=src --cov-fail-under=95` | 1417 passed, 1 skipped; **95.34%** |
| `scripts/regression_gate.py` | green (baseline refreshed) |
| `ruff check src/ scripts/ tests/` | clean |
| `mypy src/ scripts/` | clean |

## Remaining debt (round-8+ candidates)

1. ~~`hyperparameters.py` (588 lines, high fan-in)~~ — **Applied** round-8 (facade + five domain modules)
2. ~~Merge six coverage modules into domain files~~ — **Applied** round-8 (three domain files under `tests/coverage/`)
3. ~~`_interactive_dashboard_local.py` trim vs template `infrastructure.reporting`~~ — **Applied** round-8 (`_interactive_dashboard_compat` + fallback)
4. `simulation/robustness*.py` four-module cluster — consolidate orchestration vs stats after robustness ISA

## Round-8 additions (2026-05-25)

| Item | Change |
|------|--------|
| `hyperparameters_{grids,pymdp,robustness,experiments,sentinels}.py` | Domain split; `hyperparameters.py` facade unchanged import surface |
| `manuscript/variable_ranges.py` | SSOT for `ANALYTICAL_VARIABLE_RANGES`; gates + CLI share ranges |
| `tests/coverage/test_{manuscript,orchestration,dashboard}_coverage.py` | Six meta-test modules merged into three |
| `reporting/_interactive_dashboard_{compat,fallback}.py` | Infra-first HTML; local module ~340 LOC |

## Verification (round-8)

| Gate | Result |
|------|--------|
| `pytest tests/ --cov=src --cov-fail-under=95` | **1419 passed**, 1 skipped; **95.34%** |
| `scripts/regression_gate.py --update-baseline` | green — 47/47 invariants, baseline refreshed |
| `ruff check src/ tests/` | clean |
| `mypy` (round-8 touched modules) | clean |
| `mypy src/ scripts/` (round-8 follow-up) | **clean** (154 files) |

## Round-8 follow-up (2026-05-25)

| Item | Change |
|------|--------|
| `validate_tc_decomposition_group` | `check_decomposition=False` for sweeps without residual columns |
| `pymdp_sweep_validators.validate_multi_k_sweep` | Uses shared TC helper + `_multi_k_sweep_row_extras` hook |
| `gnn/bridge.py` | mypy-clean `nditer` broadcast via `cast(Any, …)` |
| `tests/coverage/test_dashboard_coverage.py` | Removed spurious cross-domain imports |

## Related

- [`docs/CHANGELOG.md`](../CHANGELOG.md) — round-7 entry  
- [`docs/_audit/README.md`](README.md) — audit vault index  
- Round-6 baseline: [`scripts/regression_baseline.json`](../../scripts/regression_baseline.json)
