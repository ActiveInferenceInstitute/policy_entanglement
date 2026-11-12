# `gnn/` — Generalized Notation Notation sources

| File | Role |
|---|---|
| `bernoulli_toy.gnn.md` | The K=2 Bernoulli/Ising toy declaration, section `ActInfPolicyEntanglement_K2_Ising`. |
| `k_stream_ensemble.gnn.md` | The K-stream policy-ensemble declaration. |
| `production_ensemble.gnn.md` | The production-harness declaration. |
| `upstream.json` | Pinned parser: repository, tag `v5.1.0`, commit `75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf`, parser module and class. The `gnn` arm reads and validates it with the shipped GNN–FEP reader (`python -m gnn.importers`). |
| [`generated/`](generated/README.md) | The Lean typed contract emitted from the Bernoulli toy. |

Round-trip and emission: `uv run python scripts/simulate_gnn.py`. Structural
config: `uv run python scripts/gnn_to_pymdp.py`. The conformance tests are
`tests/test_gnn_upstream_conformance.py` and `tests/test_simulate_gnn.py`.

The package side of the bridge is [`../src/gnn/AGENTS.md`](../src/gnn/AGENTS.md).
