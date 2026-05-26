# AGENTS.md — `scripts/`

**Publication:** DOI https://doi.org/10.5281/zenodo.20301239 · claim matrix [`../docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv`](../docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv)

## Constitution (thin-orchestrator rules)

1. **No business logic.**  If a function does math, it belongs in
   [`../src/`](../src/), not here.  This file should be the script's
   *only* logic-bearing layer:
   ```python
   results = src_module.compute(...)
   plt.plot(results)
   plt.savefig(out)
   print(out)
   ```
2. **One script = one workflow.**  Don't bundle independent
   workflows into a single script.  If you'd run them at different
   cadences, they should be different scripts.
3. **Return / print output paths.**  The pipeline collects manifest
   entries by reading stdout.  Print one path per line, no commentary.
4. **Headless matplotlib.**  Set `MPLBACKEND=Agg` before importing
   `pyplot`.
5. **Deterministic outputs.**  Fix seeds; don't use `time` or process
   IDs in filenames.
6. **Output paths under `../output/`.**  This directory is disposable;
   never write into `src/`, `tests/`, or `manuscript/`.

## Adding a script

1. Create `scripts/<verb>_<noun>.py` (e.g. `generate_figures.py`,
   `compute_archetype_table.py`).
2. Top-of-file boilerplate (prefer the shared bootstrap):
   ```python
   import os, sys
   from pathlib import Path
   os.environ.setdefault("MPLBACKEND", "Agg")
   THIS_DIR = Path(__file__).resolve().parent
   PROJECT_ROOT = THIS_DIR.parent
   sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
   from _bootstrap import ensure_project_paths  # noqa: E402
   ensure_project_paths(project_root=PROJECT_ROOT)
   ```
   All analysis scripts use this bootstrap.  Exceptions: `build_lean.py`,
   `build_mathlib_proofs.py`, and `check_concordance.py`
   (subprocess-only paths). `parameter_sweep.py` also inserts the repo root
   for template imports. `run_all.py` and `regression_gate.py` are thin
   wrappers that bootstrap + re-export
   :mod:`orchestration.run_all` / :mod:`gates.regression_gate` from
   ``../src/`` (business logic lives there).
3. Imports go after the `sys.path` insert (use `# noqa: E402`).
4. End with `if __name__ == "__main__": main()`.
5. Update [`README.md`](README.md) with the new script's row.

## Common workflows

| Want to … | Edit |
|---|---|
| add a manuscript figure | `generate_figures.py` (or `simulate_pymdp.py` for pymdp-grounded ones) |
| compute in-text variables | `manuscript_variables.py` |
| publish a CSV table | new script `compute_<table>.py` writing to `../output/data/` |
| change a grid / seed / rollout horizon | edit [`../src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py); scripts read from there |
| run the full pipeline end-to-end | `run_all.py` (canonical `SCRIPTS` order, exits non-zero on any failure) |
| run release PDF gates | `build_pdf.py` then `validate_pdf.py`, or `run_all.py --with-pdf` |
| check optional MathlibProofs scaffold | `build_mathlib_proofs.py`, or `run_all.py --with-mathlib` for release-manifest recording |
| validate every artifact | `validate_outputs.py` (thin CLI → `manuscript.output_gates`) |
| validate manuscript completeness | `validate_manuscript.py` (tokens, citations, links, hardcoded refs, numeric ranges) |
| render manuscript with auto-numbered eqs | `inject_manuscript_variables.py` |

## Script roster (current)

| Script | Stage | What it does |
|---|---|---|
| `build_lean.py` | Lean | `lake build` + sorry / axiom / unsafe budget gate |
| `build_mathlib_proofs.py` | Lean | optional additive `lean/MathlibProofs/` scaffold build |
| `build_pdf.py` | PDF | standalone combined PDF render wrapper |
| `generate_figures.py` | figures | 15 analytical PNGs (incl. coupling-potential graph) |
| `manuscript_variables.py` | data | numeric mirror → `output/data/manuscript_variables.json` |
| `dump_archetypes.py` | data | Schmidt-archetype CSV |
| `parameter_sweep.py` | data | configurable closed-form λ sweep — CLI-overridable grid, utilities, phase thresholds (defaults reproduce the canonical 121-row sweep) |
| `simulate_pymdp.py` | sim + figures | pymdp 1.0.1 run → 14 PNGs + 2 CSVs + summary JSON (lambda sweep, rollout, free-energy bundle, and dashboards) |
| `simulate_multi_k.py` | sim + figures | configured multi-stream sweep → per-K CSV + 3 PNGs + JSON summary |
| `simulate_long_horizon.py` | sim + figures | configured habit-accumulation rollout → CSV + 2 PNGs + JSON summary |
| `simulate_revertibility.py` | sim + figures | m-projection witness (Prop 7.3 / Theorem 5.1) → CSV + PNG + JSON summary |
| `simulate_robustness.py` | sim + figures | robustness, ablation, and replicate sidecars → CSVs, PNGs, and JSON summaries for one-axis, two-axis, ablation, and long-horizon diagnostics |
| `build_dashboard.py` | sim + web | interactive multi-view Plotly dashboard at `output/web/dashboard.html` (six panels, three live controls), companion plaintext `output/reports/dashboard_invariants.txt` + `output/reports/dashboard_summary.txt` + `output/data/dashboard_payload.json`. Every grid / utility / threshold is a CLI flag; exits non-zero on any invariant failure. |
| `generate_index.py` | manuscript | regenerate `manuscript/INDEX.md` from registry |
| `generate_theorem_map.py` | manuscript | regenerate `docs/reference/_theorem_map.md` four-track wiring table |
| `generate_audit_matrix.py` | manuscript | regenerate `docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv` claim ledger |
| `inject_manuscript_variables.py` | manuscript | resolve every `[[…]]` token, auto-number every `$$..$$` |
| `validate_outputs.py` | gate | thin CLI → `manuscript.output_gates/` package |
| `validate_manuscript.py` | gate | tokens / citations / links / hardcoded refs / numeric ranges |
| `validate_pdf.py` | gate | PDF text / TeX / LaTeX log / margin validation |
| `run_all.py` | meta | runs the canonical pipeline from its live `SCRIPTS` table; `--with-pdf` inserts `build_pdf.py` and `validate_pdf.py` before `regression_gate.py`, then `readiness_report.py` after regression; `--with-mathlib` adds the optional MathlibProofs build after the boundary Lean gate |

## Template monorepo integration

When this project is symlinked under `template/projects/`:

* **Analysis allowlist:** `manuscript/config.yaml` → `analysis.scripts: [run_all.py]` so stage 4 does not run every script lexicographically.
* **Tests-before-analysis:** template stage 3 runs before stage 4; `conftest.py` bootstraps missing `output/` artifacts idempotently.
* **PDF:** use `run_all.py --with-pdf` (or `make pipeline-pdf`) — not `scripts/03_render_pdf.py`, which bypasses the registry injector.
* **Copy outputs:** after `--with-pdf`, template stage 9 copies `projects/.../output/` → root `output/pdf/` (combined PDF at `output/pdf/actinf_policy_entanglement_lean_combined.pdf`).
| `readiness_report.py` | report | writes reviewer-facing release-readiness Markdown/JSON plus a small release index under `output/reports/` |

## Anti-patterns

* Hard-coding numerical computations inline (do them in `src/`).
* Writing intermediate `.npy` files into the project tree (use
  `tmp_path` or `output/`).
* Printing logs / debug output mixed with output paths (the
  pipeline parses stdout — keep it path-only).
