# AGENTS.md — `src/gnn/`

Fifth-track **empirical** GNN round-trip: parse a `.gnn.md` spec, reconstruct
the K=2 Bernoulli mutual-information curve through the general machinery,
compare to the closed-form oracle, and emit sidecar + optional Lean shell.

Parent: [`../AGENTS.md`](../AGENTS.md) · API: [`../../docs/reference/python_api.md`](../../docs/reference/python_api.md)

## Publication

- DOI: https://doi.org/10.5281/zenodo.20419149
- Source: https://github.com/ActiveInferenceInstitute/policy_entanglement
- Claim ledger: [`../../docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv`](../../docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv)

## Module map

| File | Role |
| --- | --- |
| `parser.py` | Parse `gnn/*.gnn.md` into typed stream/coupling records |
| `model.py` | Internal GNN graph representation (no closed-form shortcuts) |
| `bridge.py` | General reconstruction path — **must not** import closed-form MI |
| `runner.py` | Round-trip orchestration, negative control, sidecar JSON |
| `lean_emit.py` | Optional Lean structure emission for the Bernoulli toy |
| `__init__.py` | Public exports |

## Orchestration

- Stage entry: [`../../scripts/simulate_gnn.py`](../../scripts/simulate_gnn.py)
- Sidecar: `output/data/gnn_bernoulli_roundtrip.json`
- Manuscript: [`../../manuscript/S08_gnn_generalized_notation_extension.md`](../../manuscript/S08_gnn_generalized_notation_extension.md)
- Gates: `tests/test_gnn_round_trip.py`, `tests/test_gnn_concordance.py`

## Rules

- Keep comparison oracle (`ising_mutual_information`) in `runner.py` only — not in `bridge.py`.
- Registry row stays **empirical**; do not promote GNN track to `proved`.
- Live counts and residuals → `output/reports/test_results.json` / sidecar JSON, not folder docs.
