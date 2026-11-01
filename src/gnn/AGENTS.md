# AGENTS.md — `src/gnn/`

Fifth-track **empirical** GNN round-trip: parse a `.gnn.md` spec, reconstruct
the K=2 Bernoulli mutual-information curve through the general machinery,
compare to the closed-form oracle, verify the **production pymdp harness** against
its GNN specification, and emit sidecars + optional Lean shell.

Parent: [`../AGENTS.md`](../AGENTS.md) · API: [`../../docs/reference/python_api_gnn.md`](../../docs/reference/python_api_gnn.md)

## Publication

- DOI: https://doi.org/10.5281/zenodo.20418904
- Source: https://github.com/ActiveInferenceInstitute/policy_entanglement
- Claim ledger: [`../../docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv`](../../docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv)

## Module map

| File | Role |
| --- | --- |
| `parser.py` | Parse `gnn/*.gnn.md` into typed stream/coupling records |
| `model.py` | Internal GNN graph representation (no closed-form shortcuts) |
| `bridge.py` | General reconstruction path — **must not** import closed-form MI |
| `harness.py` | Production-harness binding: GNN declarations → `simulation.specs` ensembles + conformance report |
| `upstream.py` | Pinned upstream release identity (`gnn/upstream.json`), digest normalization, pinned-parser driver |
| `runner.py` | Round-trip + production-conformance orchestration, negative controls, sidecar JSON |
| `lean_emit.py` | Optional Lean structure emission for the Bernoulli toy |
| `__init__.py` | Public exports |

## Specifications

| Spec | Subject |
| --- | --- |
| `gnn/bernoulli_toy.gnn.md` | K=2 Ising toy (policy level) driving the MI round-trip and the Lean contract |
| `gnn/k_stream_ensemble.gnn.md` | Classical K=3 chain extension (pairwise `Jab` coupling graph) |
| `gnn/production_ensemble.gnn.md` | Production K=2 ensemble of the pymdp harness: per-stream `A`/`B`/`C`/`D`, `J`, `gamma`, plus the declared multi-K family |
| `gnn/upstream.json` | Custody pin: canonical upstream release tag + commit, and the parser module/class under test |

Use the canonical `## ActInfOntologyAnnotation` section spelling: upstream
ignores the spaced variant, so the shipped specs use the canonical form and the
project parser keeps the spaced spelling only as a documented alias.

## Orchestration

- Stage entry: [`../../scripts/simulate_gnn.py`](../../scripts/simulate_gnn.py)
- Sidecars: `output/data/gnn_bernoulli_roundtrip.json`, `output/data/gnn_production_conformance.json`
- Generator: [`../../scripts/gnn_to_pymdp.py`](../../scripts/gnn_to_pymdp.py) (policy-level config); `--harness` emits the production-harness config
- Manuscript: [`../../manuscript/S08_gnn_generalized_notation_extension.md`](../../manuscript/S08_gnn_generalized_notation_extension.md)
- Gates: `tests/test_gnn_parser.py`, `tests/test_gnn_round_trip.py`, `tests/test_gnn_concordance.py`, `tests/test_gnn_harness_conformance.py`, `tests/test_gnn_upstream_conformance.py`, `tests/test_simulate_gnn.py`

## Rules

- Keep the comparison oracle (`ising_mutual_information`) in `runner.py` only — not in `bridge.py`.
- Registry row stays **empirical**; do not promote GNN track to `proved`.
- Live counts and residuals → `output/reports/test_results.json` / sidecar JSON, not folder docs.
- The upstream pin is a **custody pin** (`gnn/upstream.json`): keep the canonical release (tag + full commit) pinned; re-pinning is a deliberate change that moves the recorded commit and re-runs the conformance test.
- Never import upstream GNN code from `src/` — the conformance test runs the real upstream parser out-of-process against the **pinned** tree (`git archive <commit> src/gnn` onto the checkout's interpreter), so the bytes under test are the pinned release's bytes.
- The conformance check must stay non-vacuous: the upstream test's spaced-section mutant must diverge, and the harness control-swap must produce a non-zero residual.
- No thresholds in the conformance comparison: production arrays are small rational matrices, so declared and built ensembles must agree exactly.
- `POLICY_ENTANGLEMENT_GNN_ROOT` selects an upstream checkout explicitly; when unset the sibling checkout is used and an unavailable checkout skips the upstream test with a reason.
