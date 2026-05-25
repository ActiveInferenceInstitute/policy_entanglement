# `src/manuscript/`

Python helpers for assembling and validating the manuscript: token
regexes, registry loaders, equation auto-numbering, Lean-source
extraction, citation/bibliography helpers, the rendering entry points,
and the validator suite.  Author-facing markdown sources live one
level up under [`../../manuscript/`](../../manuscript/); this Python
tree is tooling.  Public symbols are re-exported from
`manuscript/__init__.py`.

See parent docs: [`../AGENTS.md`](../AGENTS.md), [`../README.md`](../README.md).
Subpackage rules: [`AGENTS.md`](AGENTS.md).

## Module map

| Module | Role | Exports |
|---|---|---|
| [`tokens.py`](tokens.py) | Regex catalog + single-pass token iterator | `FIG_RE`, `FIGREF_RE`, `EQ_RE`, `EQREF_RE`, `VAR_RE`, `CITATION_RE`, `CITELIST_RE`, `SEC_RE`, `SECREF_RE`, `THM_RE`, `THMREF_RE`, `LEAN_RE`, `iter_tokens` |
| [`registry.py`](registry.py) | Typed YAML loaders for `manuscript/refs/{labels,citations}.yaml` | `Figure`, `Equation`, `Citation`, `Section`, `TheoremEntry`, `LabelsRegistry`, `CitationRegistry`, `Registry`, `load_labels`, `load_citations`, `load_registry` |
| [`equation_numbering.py`](equation_numbering.py) | Single-pass `S.K` auto-numbering pre-pass + retagger | `file_to_section_number`, `precompute_equation_numbers`, `assign_within_section_numbers`, `retag_display_math`, `section_equation_count` |
| [`lean_extract.py`](lean_extract.py) | Live extraction of theorems / declarations from `lean/ActinfPolicyEntanglement/<Module>.lean` | `LeanSnippet`, `load_lean_snippets`, `render_lean_snippet` |
| [`bibliography.py`](bibliography.py) | `[[CITELIST:topic]]` resolver + BibTeX writer | `auto_bibliography`, `write_references_bib` |
| [`renderer.py`](renderer.py) | Token resolver + per-section / whole-tree renderer | `RenderResult`, `render_section`, `render_all` |
| [`validation.py`](validation.py) | Pure-function validators (tokens, links, figures, ranges, hardcoded refs/numerics, rendered-token leaks, provenance, section refs, Lean wiring) | `ManuscriptValidationReport`, `VARIABLE_PROVENANCE_CLASSES`, `validate_undefined_tokens`, `validate_hyperlinks`, `validate_figure_files`, `validate_variables_against_ranges`, `find_hardcoded_refs`, `find_rendered_token_leaks`, `validate_rendered_token_leaks`, `find_hardcoded_numeric_literals`, `validate_section_references`, `validate_lean_wiring`, `variable_provenance_summary`, `classify_variable_provenance`, `collect_section_subheadings`, `collect_top_level_sections`, `section_paths`, `validate_manuscript_tree` |

## Conventions

* No `pymdp`, no `numpy`-heavy computation, no plotting.  Inputs are
  YAML / Markdown / JSON; outputs are Markdown / TeX-fragments / typed
  reports.
* The `Registry` dataclass is the in-memory single source of truth for
  every label-bearing token; nothing is hardcoded outside the YAML.
* `[[VAR:key]]` substitution reads `output/data/manuscript_variables.json`
  produced by `scripts/manuscript_variables.py`; the validator's
  range-check layer guards against drift.
* `[[LEAN:label]]` re-extracts source text from
  [`../../lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/)
  on every render, so a Lean refactor flows straight into the rendered
  manuscript with no manual copy-paste.
