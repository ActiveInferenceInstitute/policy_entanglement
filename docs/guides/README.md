# `docs/guides/` — Engineer-facing how-tos

Practical recipes for working with the project.

| File | Purpose |
|---|---|
| [`styleguide.md`](styleguide.md) | **Manuscript ↔ code contract hub** — the six hard requirements (configurable simulations, auto-injected variables, auto-numbered equations + figures, citation resolution, American English / evidence-first prose), each linking to its detail page under [`styleguide/`](styleguide/). |
| [`styleguide/hyperparameters.md`](styleguide/hyperparameters.md) | §1 hyperparameters source-of-truth (`src/simulation/hyperparameters.py` → JSON mirror) |
| [`styleguide/manuscript-variables.md`](styleguide/manuscript-variables.md) | §2 `[[VAR:...]]` substitution + the no-hardcoded-numbers regex catalog |
| [`styleguide/equations.md`](styleguide/equations.md) | §3 auto-numbered + cross-referenced equations (`[[EQ:...]]` / `[[EQREF:...]]`) |
| [`styleguide/figures.md`](styleguide/figures.md) | §4 figure registration + caption contract (method attribution) |
| [`styleguide/citations.md`](styleguide/citations.md) | §5 citation registry, inline + topic-grouped bibliographies |
| [`styleguide/prose.md`](styleguide/prose.md) | §6 American English + evidence-first prose contract |
| [`build_run.md`](build_run.md) | Full pipeline: `uv sync`, `lake build`, `pytest`, figure generation, manuscript injection |
| [`quickstart_recipes.md`](quickstart_recipes.md) | Copy-paste recipes for every common task |
| [`testing.md`](testing.md) | No-mocks policy, coverage targets (60 % infra / 90 % project), invariants checked |

Latest generated audit counts are checked by the build and pipeline gates,
not hand-maintained here:

- Boundary Lean inventory and hygiene: `scripts/build_lean.py`.
- Theorem/status counts and Mathlib readiness: generated theorem map plus
  `output/reports/release_readiness.json`.
- Python test count and coverage: `output/reports/test_results.json`.
- Figure, PDF, rendered-manuscript, runtime, and optional MathlibProofs
  release facts: `output/reports/release_readiness.json` and
  `output/MANIFEST.md`.
- Historical module/status deltas: `docs/CHANGELOG.md` and
  `docs/reference/veridical_status.md`.
