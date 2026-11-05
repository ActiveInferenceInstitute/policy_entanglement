# `.github/workflows/`

[`ci.yml`](ci.yml) runs on pushes and pull requests to `main`, with
`concurrency` cancelling a superseded run on the same ref.

| Job | What it runs |
|---|---|
| `ci` — "Pipeline gates, lint, and Lean budget" | Installs the pinned Lean toolchain with elan, syncs `uv --frozen --group sim`, then `scripts/run_all.py`, `ruff check`, `ruff format --check` and `mypy src/ scripts/`. Timeout 180 minutes. |
| `gnn conformance (pinned)` | Provisions the parser checkout named by `gnn/upstream.json` and runs the conformance tests with `POLICY_ENTANGLEMENT_GNN_ROOT` set. Timeout 30 minutes. |

The `ci` job deselects the live Mathlib axiom-audit test through
`PYTEST_ADDOPTS`; that build is the optional release gate
(`scripts/run_all.py --with-mathlib`).
