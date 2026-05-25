# `docs/reference/` — Cross-cutting references

Authoritative tables for the project as a whole — every reader will
visit at least one of these.

*Latest generated audit.* Live theorem/status counts come from the
generated theorem map and `manuscript/refs/labels.yaml`; live pytest,
PDF, figure, artifact, and optional MathlibProofs gate facts come from
`output/reports/release_readiness.json`,
`output/reports/test_results.json`, and `output/MANIFEST.md`.

| File | Purpose |
|---|---|
| [`architecture.md`](architecture.md) | Two-layer / executable-track architecture, file-layout map |
| [`math_reference.md`](math_reference.md) | Glossary of formal objects (PMFs, marginals, KL, TC, free energies, geometry, sign conventions) |
| [`statistics_reference.md`](statistics_reference.md) | Determinism contract, grid sizes, agreement tolerances, free-energy bundle, per-figure statistical methodology, test-budget breakdown |
| [`methods_orchestration.md`](methods_orchestration.md) | Dependency-ordered pipeline narrative: stage groups, manuscript-variable timing, figure provenance, and drift debugging |
| [`reproducibility_checklist.md`](reproducibility_checklist.md) | Reviewer-facing release gate: commands, artifacts, PDF validation, figure metadata, and worktree review slices |
| [`veridical_status.md`](veridical_status.md) | Live audit page — Lean build state, pymdp run state, per-theorem status table, manuscript-variable provenance chain, three-tier validation summary, drift-debug walk-throughs |
| [`methods_audit.md`](methods_audit.md) | Lean + pymdp methods audit: what is proved, what is witness-form, and how the real pymdp adapter is validated |
| [`lean_reference.md`](lean_reference.md) | Per-theorem status table + sorry inventory (Lean 4 boundary fragment); per-file rows for all boundary submodules including `SpectralWitnesses` and `ConnectionsWitnesses` |
| [`invariants_reference.md`](invariants_reference.md) | Per-invariant catalog (47 dashboard invariants by family, witnessing each manuscript theorem at the numerical layer); mirrors `output/reports/dashboard_invariants.txt` |
| [`four_track_coherence.md`](four_track_coherence.md) | The auto-injection contract: how prose, equations, code, and Lean are kept in lockstep by CI gates ("show, not tell") |
| [`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md) | Lean-side Mathlib refinement roadmap (lives next to the Lean source it refines); witness-payload-discharge plan for the current registry |
| [`_theorem_map.md`](_theorem_map.md) | **Auto-generated** per-theorem four-track wiring (21 rows; do not hand-edit) |
| [`python_api.md`](python_api.md) | API index — quick-jump table to one of the four per-subpackage references |
| [`python_api_lean.md`](python_api_lean.md) | Per-function signatures: `src/lean/` (analytical mirrors of the Lean fragment) |
| [`python_api_simulation.md`](python_api_simulation.md) | Per-function signatures: `src/simulation/` (pymdp harness + bundle aggregation) |
| [`python_api_visualizations.md`](python_api_visualizations.md) | Per-function signatures: `src/visualizations/` (figure helpers + PNG metadata) |
| [`python_api_manuscript.md`](python_api_manuscript.md) | Per-function signatures: `src/manuscript/` (auto-injection + four-track CI gate) |
| [`manuscript_map.md`](manuscript_map.md) | Section-by-section + per-theorem map: manuscript ↔ Lean ↔ Python ↔ tests ↔ docs |
