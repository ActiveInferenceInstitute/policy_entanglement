# GNN conformance

`gnn conformance (pinned)` is the `gnn-conformance` job in
`.github/workflows/ci.yml` and reads `gnn/upstream.json`, which pins
`ActiveInferenceInstitute/Generalized_Notation_Notation` at `v5.0.3`
(`8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`).

The job fetches that commit into `$RUNNER_TEMP/gnn`, fails if the `v5.0.3`
tag no longer resolves to it, and then runs
`uv run --no-sync python -m pytest -q tests/test_gnn_upstream_conformance.py`.
That test extracts `src/gnn` from the pinned commit with `git archive`, checks
the executed parser's SHA-256 against the pinned blob, parses the three
specs `gnn/bernoulli_toy.gnn.md`, `gnn/k_stream_ensemble.gnn.md` and
`gnn/production_ensemble.gnn.md` with the pinned `MarkdownGNNParser` requiring
no errors or warnings, and compares the normalized digests field by field
with the project-owned parser in `src/gnn/parser.py`; a spaced-heading mutant
proves the comparison is not vacuous. It does not scan the rest of the
repository for `*.gnn.md`.
