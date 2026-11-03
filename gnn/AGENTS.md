# AGENTS.md — `gnn/`

- Validate against the parser revision in `upstream.json`, never a live GNN
  checkout. A re-pin updates the tag and commit there.
- A spec change must be followed by the round-trip and conformance tests, and by
  regenerating `gnn/generated/BernoulliToyGnn.lean` when the Bernoulli spec
  changes.
- Do not put output JSON, figures or Python in this directory; those belong in
  `output/` and `src/gnn/`.
- Parent rules: [../AGENTS.md](../AGENTS.md).
