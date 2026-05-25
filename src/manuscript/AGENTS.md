# AGENTS.md — `src/manuscript/`

Supporting library for assembling and validating manuscript-facing artifacts from Python (token lists, bibliography hooks, markdown rendering helpers tied to workflow around [`../manuscript/`](../manuscript/) at project root — `config.yaml`, sections, `.bib`). This **Python** tree is tooling; narrative sources remain under the sibling `manuscript/` directory consumed by Layer-1 rendering.

## Modules

| File / package | Role |
| --- | --- |
| `tokens.py` | Regex definitions for every `[[FIG:...]]` / `[[EQ:...]]` / `[[VAR:...]]` / `[[SEC:...]]` / `[[THM:...]]` / `[[LEAN:...]]` / `[@cite]` token plus `iter_tokens()` for the validator. |
| `registry.py` | Typed loaders for `manuscript/refs/{labels,citations}.yaml` (figures, equations, sections, theorems, citations); the `Registry` dataclass is the in-memory single source of truth. |
| `registry_facts.py` | Structural registry counts for `manuscript_variables.py` and output gates. |
| `lean_extract.py` | Live extraction of Lean source snippets from `lean/ActinfPolicyEntanglement/<Module>.lean` so `[[LEAN:label]]` embeds the actual proof / declaration text at render time. |
| `equation_numbering.py` | Single-pass auto-numbering: walks every section in source order, assigns each display equation `S.K`; `retag_display_math` injects / rewrites `\tag{S.K}` post-substitution. |
| `bibliography.py` | `auto_bibliography(citations, topic)` — emits Markdown bullet list grouped by `topic:`; powers `[[CITELIST:topic]]`. |
| `renderer.py` | The `render_section` / `render_all` entry points: resolve every token and run the equation auto-numbering pre-pass; called by [`scripts/inject_manuscript_variables.py`](../../scripts/inject_manuscript_variables.py). |
| `index_generator.py` | Auto-generated TOC builder consumed by [`scripts/generate_index.py`](../../scripts/generate_index.py). |
| `validation.py` | Tree orchestrator facade; delegates to `validation_{report,patterns,scan,checks}.py`. |
| `validation_report.py` | `ManuscriptValidationReport` dataclass and provenance class constants. |
| `validation_patterns.py` | Shared regex patterns for headings, hyperlinks, hardcoded refs. |
| `validation_scan.py` | Section discovery, hardcoded-ref scans, rendered-token leak checks. |
| `validation_checks.py` | Per-check validators (tokens, figures, Lean wiring, hyperlinks). |
| `validation_cli.py` | Library implementation of [`scripts/validate_manuscript.py`](../../scripts/validate_manuscript.py) (tree validation + rendered-token leaks + status gates). |
| `variable_ranges.py` | SSOT for closed-form `ANALYTICAL_VARIABLE_RANGES` shared by `validation_cli.EXPECTED_RANGES` and output gates. |
| `status.py` / `status_patterns.py` | Live project-status loading and stale-pattern detectors for docs and gates. |
| `pdf_validation.py` | PDF / TeX / log validation helpers consumed by [`scripts/validate_pdf.py`](../../scripts/validate_pdf.py). |
| `readiness.py` | Release-readiness orchestration; emitters in `readiness_emit.py`. |
| `readiness_emit.py` | Markdown/JSON/index writers for reviewer release artifacts. |
| `theorem_map.py` | Four-track theorem wiring table generator for [`scripts/generate_theorem_map.py`](../../scripts/generate_theorem_map.py). |
| `variables.py` | `build_manuscript_variables` / `write_manuscript_variables` for [`scripts/manuscript_variables.py`](../../scripts/manuscript_variables.py). |
| `stale_patterns.py` | Shared stale-reference regex constants for status and validation gates. |
| `output_gates/` | Release validators for `output/` artifacts (PNG metadata, CSV sidecars, pymdp bundles, manuscript-variable ranges); thin CLI: [`scripts/validate_outputs.py`](../../scripts/validate_outputs.py). |

## Rules

Same as parent [`AGENTS.md`](../AGENTS.md): library boundaries documented there,
no mocks in consuming tests, and the project-wide `src/` coverage floor is 95%.
`scripts/regression_gate.py` additionally enforces 95% minimum coverage on this
package's drift-critical status/PDF-validation modules.

## See also

- [`README.md`](README.md)
