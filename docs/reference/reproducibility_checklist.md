# Reviewer Reproducibility Checklist

*Latest generated audit.*

This checklist is the release-facing audit path for the manuscript. It
states what must be regenerated, validated, and inspected before a
reviewer treats the PDF as the current artifact.

## Commands

Run the full readiness gate from the project root:

```bash
uv sync --group sim --group viz --group lint
make readiness
```

**Expanded view — the underlying steps `run_all.py` performs
internally** (this is *not* literally what `make readiness` shells out
to; see the actual recipe below).  `make readiness` runs only the
seven commands in the recipe — `validate_manuscript.py`,
`validate_outputs.py`, `build_lean.py`, and `build_mathlib_proofs.py`
execute *inside* `run_all.py`, not as separate top-level invocations:

```bash
uv run python scripts/run_all.py --with-pdf --with-mathlib
# ↳ internally runs build_lean.py, validate_outputs.py,
#   validate_manuscript.py, and (with --with-mathlib) the MathlibProofs
#   build, among the canonical scripts
uv run python scripts/validate_pdf.py
uv run pytest tests/ --cov=src --cov-fail-under=95
uvx ruff check src/ scripts/ tests/
uvx ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/readiness_report.py
```

The literal `make readiness` recipe (from the `Makefile`) is exactly
the seven shell steps above; it does *not* separately invoke
`validate_manuscript.py`, `validate_outputs.py`, `build_lean.py`, or
`build_mathlib_proofs.py` as standalone commands.

## What Must Be True

| Layer | Required evidence |
|---|---|
| Lean boundary | `scripts/build_lean.py` passes; boundary modules contain zero `sorry`, zero `axiom`, zero `unsafe` / `partial` / `noncomputable`, and zero `Mathlib` imports. |
| MathlibProofs scope | `lean/MathlibProofs/` is a separate Mathlib-backed package; `scripts/run_all.py --with-mathlib` records its build and axiom audit in the readiness JSON. The manuscript may cite the compiled headline real-valued decomposition discharge when that gate passes, while other witness rows still require row-specific green Mathlib source before promotion. |
| Simulation inputs | Tunable grids, seeds, horizons, tolerances, and sentinel values live in `src/simulation/hyperparameters.py`. |
| Manuscript variables | Numeric prose flows through `[[VAR:...]]` tokens rendered from `output/data/manuscript_variables.json`; source prose must not hand-write empirical results or display references. |
| Figures | Every PNG in `output/figures/` is nonblank, large enough, and carries `project.source_script`, `project.source_function`, `project.hyperparameters`, `project.uncertainty_semantics`, and schema-v2 `project.figure_statistics`. |
| PDF | `scripts/build_pdf.py` renders with local Pandoc/XeLaTeX/BibTeX tooling; `scripts/validate_pdf.py` rejects unresolved tokens, raw dollar signs, undefined refs/citations, LaTeX log warnings/errors, missing glyphs, and margin drift. |
| Readiness report | `output/reports/release_readiness.md` summarizes the latest generated artifacts and worktree review slices without staging or committing anything; `output/reports/release_readiness.json` carries the same live counts for machine checks. |
| Release index | `output/reports/release_index.md` links the PDF, manifest, theorem map, release note, readiness report, and readiness JSON for reviewer navigation. |
| Release note | `output/reports/release_note.md` gives a reviewer-facing live snapshot and claim-strength ledger generated from current reports and registries. |

## Claim Strength Labels

Use these labels consistently in review notes and manuscript prose:

| Label | Meaning |
|---|---|
| `proved` | stock-Lean theorem row with no external analytic witness assumption; always read together with `faithfulness` (`substantive` versus `statement-restricted`) before treating it as proved as named |
| `witness` | typed Lean witness or witness-consuming theorem; analytic payload supplied externally |
| `empirical` | generated sidecar/figure result validated by output and test gates |
| `hypothesis` | interpretive biological, clinical, or alignment framing |
| `roadmap` | scoped future work, including Mathlib witness discharge |

## Artifact Inventory

Generated artifacts are disposable and must be recreated through scripts:

| Artifact family | Location | Producer |
|---|---|---|
| Analytical figures | `output/figures/` | `scripts/generate_figures.py` |
| pymdp / multi-K / horizon / revertibility sidecars | `output/simulations/` | `scripts/simulate_*.py` |
| Manuscript variables | `output/data/manuscript_variables.json` | `scripts/manuscript_variables.py` |
| Rendered markdown | `output/manuscript/` | `scripts/inject_manuscript_variables.py` |
| Combined PDF and TeX intermediates | `output/pdf/` | `scripts/build_pdf.py` |
| Pipeline manifest and reports | `output/MANIFEST.md`, `output/reports/` | `scripts/run_all.py`, regression/readiness scripts |

## Manual Review Points

Before release, inspect:

- The PDF front matter, theorem table, supplement code listings, and bibliography for visual coherence.
- Figure legends/stat boxes for overlap and readable font sizes.
- The Mathlib wording in the introduction, Lean methods section, discussion, and supplements; it must describe the separate headline proof-discharge layer accurately and avoid promoting non-headline witness rows without compiled row-specific source.
- Any changed research claim against its primary citation or generated artifact.

## Drift Debugging

| Symptom | First check |
|---|---|
| A number in prose looks stale | `output/data/manuscript_variables.json`, then `scripts/manuscript_variables.py`. |
| A theorem number looks stale | `manuscript/refs/labels.yaml`, then `scripts/generate_theorem_map.py`. |
| A figure caption disagrees with plotted data | PNG `project.hyperparameters`, `project.uncertainty_semantics`, and `project.figure_statistics` metadata. |
| The PDF shows `?`, `$`, or raw token syntax | `scripts/validate_pdf.py` output and `output/pdf/_combined_manuscript.log`. |
| A readiness count changed | Regenerate with `make readiness`; do not hand-edit generated status text. |
