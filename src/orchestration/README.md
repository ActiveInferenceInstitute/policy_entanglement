# `src/orchestration/`

End-to-end pipeline coordination, imported as `orchestration`.

- `run_all.py` — the canonical pipeline runner: Lean budget, artifact and figure
  generation, manuscript variable hydration and validation, then the regression
  gate. `scripts/run_all.py` is the thin wrapper.
- `build_pdf.py` — PDF assembly and the combined-document copy. Wrapped by
  `scripts/build_pdf.py`.

Optional subgates (`--with-pdf`, `--with-mathlib`) are declared here and
documented in the root [`AGENTS.md`](../../AGENTS.md). Tests:
`tests/coverage/test_orchestration_coverage.py`.
