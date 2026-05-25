# ISA — Robustness cluster module boundaries

**Project:** `actinf_policy_entanglement_lean`  
**Date:** 2026-05-25 (round-9)  
**Closes:** thermo-nuclear finding J7

## Goal

Decompose the reviewer-facing robustness branch into domain modules with a
stable public import surface (`simulation.robustness` facade).

## Import rule

External code imports from `simulation.robustness` only. Submodules under
`simulation/robustness_*.py` are package-internal unless re-exported by the
facade.

**Test exception:** `tests/test_robustness_runner.py` may import
`simulation.robustness_emit` directly for CSV/metadata round-trip tests;
production scripts and library code stay on the facade or runner entrypoint.

## Layering

```text
compute (numpy + analytical layer)
  → robustness_core, robustness_one_axis, robustness_interaction,
    robustness_controls, robustness_replicates
stats → robustness_stats
scenarios → robustness_scenarios (dataclasses + scenario builders)
emit → robustness_emit (CSV/JSON + figure metadata helpers)
runner → robustness_runner (run_robustness_pipeline glue)
script → scripts/simulate_robustness.py (bootstrap + main)
```

## Public API

Preserve `simulation.robustness.__all__` (33 symbols): dataclass re-exports,
suite runners, summarizers, long-horizon replicate helpers, and
`wilson_score_interval`.

## Non-goals

- No pymdp API changes
- No manuscript prose or `[[VAR:…]]` registry edits
- No Lean / Mathlib / output-gate invariant changes
- Do not merge replicate summaries into `long_horizon.py` (rollout vs sidecar)

## Verification

- `pytest tests/test_robustness*.py tests/test_output_gates_corruption.py`
- Coverage ≥ 95% on `src/`
- Regression gate 47/47 invariants unchanged
