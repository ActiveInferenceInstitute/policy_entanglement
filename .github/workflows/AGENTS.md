# AGENTS.md — `.github/workflows/`

- Keep every later step on `uv run --no-sync`: a re-syncing `uv run` resolves the
  default groups without `sim`, drops pymdp, and makes the simulation tests
  skip instead of run.
- The GNN job must check that the tag still resolves to the pinned commit before
  using the tree.
- Do not add `--with-mathlib` to the push gate; the Mathlib build is the
  documented optional release gate.
- Parent rules: [../AGENTS.md](../AGENTS.md).
