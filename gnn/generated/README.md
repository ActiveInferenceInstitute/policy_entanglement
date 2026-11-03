# `gnn/generated/`

[`BernoulliToyGnn.lean`](BernoulliToyGnn.lean) is the Lean typed contract
emitted by `src/gnn/lean_emit.py` from `gnn/bernoulli_toy.gnn.md`. Its header
says it is generated and must not be edited by hand.

It is a typed contract, not a proof: type-checking it certifies the structural
signature of the GNN-specified model, not any analytic claim. Regenerate with
`uv run python scripts/simulate_gnn.py`.
