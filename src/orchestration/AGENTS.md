# AGENTS.md — `src/orchestration/`

## Purpose

End-to-end pipeline coordination. The thin script wrapper
[`../../scripts/run_all.py`](../../scripts/run_all.py) bootstraps the
project paths and re-exports every symbol below so wrapper calls still
resolve constants and helpers as module attributes. Tests that need the
pipeline module should import `from orchestration import run_all`; the
template root also has a `scripts` package, so `from scripts import run_all`
is ambiguous when the suite is launched through template-hosted pytest.

## Modules

| Module | Purpose |
|---|---|
| [`stages.py`](stages.py) | Frozen `SCRIPTS` topology, flag resolution (`resolve_stages`) |
| [`manifest.py`](manifest.py) | `StageSummary`, `write_manifest()` → `output/MANIFEST.md` |
| [`executor.py`](executor.py) | `spawn`, serial/parallel batch runners, `execute_pipeline()` |
| [`run_all.py`](run_all.py) | Thin `main()`; re-exports legacy `_spawn` / `_write_manifest` aliases |
| [`build_pdf.py`](build_pdf.py) | PDF orchestration; calls manuscript inject APIs directly |
| [`pdf_config.py`](pdf_config.py) | Typed `ManuscriptConfig` from YAML |
| [`pdf_tex_patch.py`](pdf_tex_patch.py) | Hyperlink patching aligned with template rendering |
| [`pdf_compile.py`](pdf_compile.py) | Pandoc / XeLaTeX / BibTeX helpers |

## Contract

* Constants `SCRIPTS`, `PDF_SCRIPTS`, `MATHLIB_PROOF_SCRIPTS`,
  `PARALLEL_STAGE_STEMS`, `_SHA256_MAX_BYTES`, and
  `_MANIFEST_EXCLUDED_FILENAMES` are source-of-truth for the pipeline
  topology and are read by `scripts/manuscript_variables.py`,
  `tests/test_status_docs.py`, `tests/test_manuscript_variables_pipeline.py`,
  and `tests/test_docs_no_stale_registry_numbers.py`.
* `_write_manifest(*, project_root, run_summary)` accepts `project_root`
  explicitly and is exercised by
  [`tests/test_run_all_manifest.py`](../../tests/test_run_all_manifest.py).
* `_spawn`, `_run_serial`, and `_run_parallel_batch` accept `scripts_dir`
  + `project_root` keyword arguments; the wrapper script binds them to
  the project's own paths so the public call shape (no path kwargs) is
  preserved.
* `StageResult` is a :class:`NamedTuple` rather than a
  :class:`dataclasses.dataclass` so importlib-loaded copies of this
  module compose cleanly without `dataclasses._is_type` lookups.
