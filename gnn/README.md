# `gnn/` — Generalized Notation Notation sources

| File | Role |
|---|---|
| `bernoulli_toy.gnn.md` | The K=2 Bernoulli/Ising toy declaration, section `ActInfPolicyEntanglement_K2_Ising`. |
| `k_stream_ensemble.gnn.md` | The K-stream policy-ensemble declaration. |
| `production_ensemble.gnn.md` | The production-harness declaration. |
| `upstream.json` | Pinned parser: repository, tag `v5.0.3`, commit `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`, parser module and class. |
| [`generated/`](generated/README.md) | The Lean typed contract emitted from the Bernoulli toy. |

Round-trip and emission: `uv run python scripts/simulate_gnn.py`. Structural
config: `uv run python scripts/gnn_to_pymdp.py`. The conformance tests are
`tests/test_gnn_upstream_conformance.py` and `tests/test_simulate_gnn.py`.

The package side of the bridge is [`../src/gnn/AGENTS.md`](../src/gnn/AGENTS.md).
