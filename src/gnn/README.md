# README — `src/gnn/`

GNN-sourced round-trip for the K=2 Bernoulli toy plus the GNN-verified
production harness (fifth representation track).

```bash
uv run python scripts/simulate_gnn.py            # round-trip + harness conformance stage
uv run python scripts/gnn_to_pymdp.py --harness  # production-harness config from the spec
```

| Output | Path |
| --- | --- |
| Round-trip sidecar | `output/data/gnn_bernoulli_roundtrip.json` |
| Production-conformance sidecar | `output/data/gnn_production_conformance.json` |
| Figure | `output/figures/gnn_bernoulli_roundtrip.png` |

Conformance evidence: `gnn/production_ensemble.gnn.md` is compared elementwise
against the harness build (`simulation.builders.make_ising_ensemble` under the
`simulation.hyperparameters` constants); the upstream release under test is
pinned in `gnn/upstream.json` and the project parser is checked against the real
upstream parser of that pinned tree.

Details: [`AGENTS.md`](AGENTS.md) · Manuscript §S08 · DOI https://doi.org/10.5281/zenodo.20418904
