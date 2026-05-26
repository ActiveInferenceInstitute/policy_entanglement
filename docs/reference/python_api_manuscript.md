# Python API: subpackage `manuscript/`

*Latest generated audit.*

Auto-injection + validation toolkit: registry loader, token renderer,
Lean-source extractor, equation auto-numbering, manuscript validator
with the four-track-coherence CI gate.

Imports: `from manuscript.<module> import …` (`pythonpath = src/`).

Companion: [`four_track_coherence.md`](four_track_coherence.md) (the "show, not tell" contract),
[`../guides/styleguide.md`](../guides/styleguide.md) (token usage in prose).

## Live derived variables (from `scripts/manuscript_variables.py`)

The orchestrator script
[`scripts/manuscript_variables.py`](../../scripts/manuscript_variables.py)
emits `output/data/manuscript_variables.json`. Round 2 added one new
helper and renamed/derived two scalars:

| Helper / key | What it does | Notes |
|---|---|---|
| `_run_all_facts()` | Inspects `scripts/run_all.py::SCRIPTS` at import time and emits `run_all_script_count` (the number of orchestrator stages). | Manuscript prose uses `[[VAR:run_all_script_count]]` instead of hardcoding the stage count; the current value is generated into `output/data/manuscript_variables.json`. |
| `lean_structure_count` | Counts `structure` declarations in comment-stripped boundary-fragment source (was `lean_inductive_count`). | Current value: **11**, including `FloatRealResidualWitness`. |
| `lean_total_declarations` | Live-derived in `_lean_facts()` as `lean_def_count + lean_theorem_count + lean_structure_count`. | Current value: **126** (= 39 + 76 + 11). Previously a manually-typed integer; now any component can change and the total stays honest. |
| `lean_submodule_count` | Static count of `.lean` files under `lean/ActinfPolicyEntanglement/`. | Current value: **17**, including `FloatRealResidualWitness`. |
| `lean_lake_jobs_total` | Static count of lake jobs. | Current value: **22**. |
| `_registry_facts()` | Counts canonical manuscript section files, citation entries, rendered bibliography entries, and theorem statuses from the registries. | Emits `manuscript_section_file_count`, `theorem_registry_count`, and `theorem_status_*_count` so status summaries in prose are tokenized. |

The signature `lean.geometry.pythagorean_residual(q, mf_reference)`
(round 1 fix: argument named `mf_reference`, not the older
`mean_field_reference`) is consumed by
`manuscript_variables.py::_alignment_and_phase_facts`; the older
`schmidt_gap` key was replaced by `tt_ranks_K{2,3,4,5}` in
`_tensor_train_facts()` to surface the full TT-rank profile rather
than a one-dimensional gap proxy.

---

## Subpackage `manuscript/`

Auto-injection + validation toolkit consumed by
[`scripts/inject_manuscript_variables.py`](../../scripts/inject_manuscript_variables.py)
and [`scripts/validate_manuscript.py`](../../scripts/validate_manuscript.py).

### `registry.py`

```python
@dataclass(frozen=True)
class Figure:
    label: str; path: str; caption: str; short: str
    sections: tuple[str, ...]; source: str; number: int

@dataclass(frozen=True)
class Equation:
    label: str; latex: str; name: str
    sections: tuple[str, ...]; number: int

@dataclass(frozen=True)
class Citation:
    key: str; authors: str; year: int; title: str; venue: str
    volume: str = ""; pages: str = ""; doi: str = ""; url: str = ""
    note: str = ""; topic: str = ""
    def render_inline(self) -> str            # "(Author year)"
    def render_bibliography(self) -> str       # Markdown bullet line

@dataclass(frozen=True)
class Section:
    label: str; number: str; title: str; file: str; parent: str

@dataclass(frozen=True)
class TheoremEntry:
    label: str; kind: str; number: str; name: str; section: str
    def render_block(self) -> str             # "**Kind N (Name).**"
    def render_inline(self) -> str            # "Kind N"

@dataclass(frozen=True)
class LabelsRegistry:
    figures: dict[str, Figure]
    equations: dict[str, Equation]
    sections: dict[str, Section]              # added in v0.3
    theorems: dict[str, TheoremEntry]         # added in v0.3

@dataclass(frozen=True)
class CitationRegistry:
    entries: dict[str, Citation]
    topic_order: tuple[str, ...]
    topic_titles: dict[str, str]

@dataclass(frozen=True)
class Registry:
    labels: LabelsRegistry
    citations: CitationRegistry

def load_labels(path: Path) -> LabelsRegistry
def load_citations(path: Path) -> CitationRegistry
def load_registry(refs_dir: Path) -> Registry
```

### `tokens.py`

```python
FIG_RE: re.Pattern        # [[FIG:label]]
FIGREF_RE: re.Pattern     # [[FIGREF:label]]
EQ_RE: re.Pattern         # [[EQ:label]]
EQREF_RE: re.Pattern      # [[EQREF:label]]
SEC_RE: re.Pattern        # [[SEC:label]]      → "§<n> <title>"
SECREF_RE: re.Pattern     # [[SECREF:label]]   → "§<n>"
THM_RE: re.Pattern        # [[THM:label]]      → "**<Kind> <n> (<Name>).**"
THMREF_RE: re.Pattern     # [[THMREF:label]]   → "<Kind> <n>"
VAR_RE: re.Pattern        # [[VAR:key]] or [[VAR:key:fmt]]
CITATION_RE: re.Pattern   # [@citekey]
CITELIST_RE: re.Pattern   # [[CITELIST:topic]]
LEAN_RE: re.Pattern       # [[LEAN:label]]

def iter_tokens(text: str) -> Iterator[tuple[str, str, tuple[int, int]]]
```

### `renderer.py`

```python
@dataclass
class RenderResult:
    text: str
    missing_figures: list[str]
    missing_equations: list[str]
    missing_citations: list[str]
    missing_variables: list[str]
    @property
    def is_complete(self) -> bool

def render_section(text: str, *, registry: Registry,
                   variables: Mapping[str, Any],
                   manuscript_dir: Path) -> RenderResult

def render_all(*, manuscript_dir: Path, output_dir: Path,
               registry: Registry,
               variables_path: Path) -> dict[str, RenderResult]
```

### `bibliography.py`

```python
def auto_bibliography(reg: CitationRegistry,
                      topic: str = "all") -> str

def write_references_bib(reg: CitationRegistry, path: Path) -> None
```

### `lean_extract.py`

Auto-extracts Lean theorem signatures from
`lean/ActinfPolicyEntanglement/*.lean` so `[[LEAN:label]]` tokens can
embed live source.  Pure-string parser (no Lean toolchain required).

```python
@dataclass(frozen=True)
class LeanSnippet:
    label: str            # registry label (`thm_4_1`, …)
    module: str           # Lean module name (`Decomposition`)
    qualified_name: str   # full Lean name (`Bipartite.<...>`)
    keyword: str          # `theorem` / `def` / `lemma` / `instance`
    docstring: str
    body: str
    file_path: Path
    start_line: int

def load_lean_snippets(lean_dir: Path) -> dict[tuple[str, str], LeanSnippet]
def render_lean_snippet(snip: LeanSnippet, *, status: str = "") -> str
```

### `equation_numbering.py`

Auto-numbers every display equation as `S.K` (S = section number from
the registry, K = within-section position).  Single source-order pass.

```python
def file_to_section_number(registry: Registry) -> dict[str, str]
def precompute_equation_numbers(*, manuscript_dir: Path,
                                 registry: Registry) -> dict[str, str]
def section_equation_count(text: str) -> int
def assign_within_section_numbers(text: str
    ) -> list[tuple[int, int, str, str | None]]
def retag_display_math(text: str, section_number: str) -> str
```

### `validation.py` (facade)

Implementation split across ``validation_report.py`` (report model),
``validation_patterns.py`` (regex constants), ``validation_scan.py``
(section discovery and hardcoded-ref scanners), and
``validation_checks.py`` (field validators). The public import surface
below is unchanged.

```python
@dataclass
class ManuscriptValidationReport:
    section_files: list[str]
    undefined_tokens: dict[str, list[tuple[str, str]]]
    broken_links: dict[str, list[str]]
    missing_figure_files: dict[str, list[str]]
    out_of_range_variables: dict[str, str]
    missing_headings: list[str]
    empty_captions: list[str]
    bad_section_refs: dict[str, list[str]]
    hardcoded_refs: dict[str, list[str]]
    hardcoded_numeric_literals: dict[str, list[str]]
    hardcoded_rendered_source_fields: dict[str, list[str]]
    tokens_in_code_fences: dict[str, list[str]]
    broken_lean_wiring: dict[str, str]   # NEW (four-track gate)
    @property
    def is_clean(self) -> bool

VARIABLE_PROVENANCE_CLASSES: tuple[str, ...]

def section_paths(manuscript_dir: Path) -> list[Path]
def collect_top_level_sections(manuscript_dir: Path) -> set[int]
def collect_section_subheadings(manuscript_dir: Path) -> dict[int, set[int]]
def validate_undefined_tokens(text, registry, variables) -> list[tuple[str, str]]
def validate_hyperlinks(text: str, base: Path) -> list[str]
def validate_figure_files(text: str, manuscript_dir: Path) -> list[str]
def validate_variables_against_ranges(variables, ranges) -> dict[str, str]
def validate_section_references(text, *, top_level, subsections) -> list[str]
def validate_lean_wiring(registry, lean_dir) -> dict[str, str]   # NEW
def find_hardcoded_refs(text: str) -> list[str]
def find_registry_tokens_in_code_fences(text: str) -> list[str]
def find_rendered_token_leaks(text: str) -> list[str]
def find_hardcoded_numeric_literals(text: str) -> list[str]
def find_hardcoded_rendered_source_literals(text: str) -> list[str]
def validate_registry_source_fields(registry: Registry) -> dict[str, list[str]]
def validate_rendered_token_leaks(rendered_dir: Path) -> dict[str, list[str]]
def classify_variable_provenance(key: str, *,
                                  hyperparameter_keys=None) -> str
def variable_provenance_summary(variables, *,
                                hyperparameter_keys=None) -> dict[str, int]
def validate_manuscript_tree(*, manuscript_dir, registry, variables,
                              variable_ranges=None,
                              lean_dir=None) -> ManuscriptValidationReport
```

Public hardcoded-result detector constants include
`HARDCODED_RESULT_WITH_UNIT_RE`, `HARDCODED_SCI_TOL_RE`,
`HARDCODED_LINSPACE_RE`, and `HARDCODED_THEOREM_COUNT_RE`, extending
the earlier grid/seed/horizon/ensemble patterns.

Strict rendered-source detector constants include
`HARDCODED_FIG_EQ_RE`, `HARDCODED_APPENDIX_RE`, `HARDCODED_TABLE_RE`,
`HARDCODED_SEC_WORD_RE`, and
`HARDCODED_T_VALUE_RE`. Together with the section/theorem reference
patterns, these support `find_hardcoded_rendered_source_literals`,
which scans paper-facing source fields for raw references such as
hand-written theorem numbers, figure numbers, equation numbers,
section symbols, appendix letters, and rollout horizons. Source files
must use registry tokens (`[[THMREF:...]]`, `[[FIGREF:...]]`,
`[[SECREF:...]]`, `[[EQREF:...]]`) or neutral headings; rendered
`output/` files are allowed to contain resolved labels and values.

Fence-safety constants `FENCED_CODE_RE` and
`FORBIDDEN_CODE_FENCE_TOKEN_RE` drive
`find_registry_tokens_in_code_fences`, which blocks cross-reference,
equation, figure, theorem, citation, and Lean-source registry tokens
inside backtick or tilde fenced code while still allowing
`[[VAR:...]]` JSON examples.

`find_rendered_token_leaks` and `validate_rendered_token_leaks` are the
post-injection leak gate: they strip fenced and inline code examples from
rendered Markdown, then fail on raw `[[VAR:...]]`, `[[SECREF:...]]`,
`[[THMREF:...]]`, `[[FIG:...]]`, `[[EQ:...]]`, `[[LEAN:...]]`,
`[[CITELIST:...]]`, or `[[MISSING:...]]` markers in paper-facing prose.

`VARIABLE_PROVENANCE_CLASSES`, `classify_variable_provenance`, and
`variable_provenance_summary` provide the compact audit summary printed
by `scripts/validate_manuscript.py`: hyperparameter-derived,
source-scan-derived, registry-derived, analytic-computation,
sidecar-derived, and uncategorized variable counts.

`find_hardcoded_numeric_literals` is the **no-hardcoded-vars CI gate**:
flags inline patterns like `121-point grid`, `21 grid points`,
`seed = 42`, `T = 10 steps`, empirical results (`I(λ=2) = 0.4421`),
rollout horizons (`rollout of 10 steps`), and `K = N streams`
references outside protected regions (headings, fenced code, inline
code spans, `[[...]]` token bodies). Every flagged literal must be
replaced with a `[[VAR:<key>]]` token sourced from
`output/data/manuscript_variables.json` —
see [`../guides/styleguide/manuscript-variables.md`](../guides/styleguide/manuscript-variables.md).

`validate_lean_wiring` is the **four-track coherence CI gate**: for
every theorem in `manuscript/refs/labels.yaml::theorems` whose
`lean_module` / `lean_name` fields are populated, it confirms that
the qualified name actually resolves to a declaration in the live
boundary fragment under `lean/ActinfPolicyEntanglement/`. A renamed
or missing Lean theorem fails the gate immediately, so the prose
(via `[[LEAN:...]]` injection), the equation registry, the Python
companion, and the Lean source cannot drift apart silently — see
[`four_track_coherence.md`](four_track_coherence.md) for the full
contract.

### `_resolvers.py`

```python
UNCERTAINTY_CAPTION_TEXT: dict[str, str]
```

`UNCERTAINTY_CAPTION_TEXT` maps supported uncertainty semantics to the
standard caption prose injected into rendered figure/manuscript text.

### `status.py`

Live status helpers used by `scripts/validate_manuscript.py` and
`tests/test_status_docs.py` to keep volatile README / AGENTS / docs
counts synchronized with generated artifacts.

```python
@dataclass(frozen=True)
class ProjectStatus:
    tests_total: int
    tests_passed: int
    tests_skipped: int
    tests_failed: int
    coverage_percent: float
    pdf_pages: int
    pdf_size_bytes: int
    @property
    def pdf_size_mb(self) -> float
    @property
    def test_summary(self) -> str
    @property
    def pdf_summary(self) -> str

def load_project_status(project_root: Path) -> ProjectStatus
def stale_reference_issues(project_root: Path) -> list[str]
def mathlibproofs_claim_issues(project_root: Path) -> list[str]
def stale_status_issues(project_root: Path,
                        status: ProjectStatus | None = None) -> list[str]
```

`load_project_status` reads `output/reports/test_results.json` plus
`pdfinfo` for the combined PDF. `stale_reference_issues` scans
current-facing source/docs for retired theorem display numbers.
`mathlibproofs_claim_issues` rejects prose that cites the optional
`MathlibProofs` scaffold as a current proof result. `stale_status_issues`
scans high-traffic docs and every page under `docs/` for stale pytest/PDF
literals.

### `pdf_validation.py`

Release-PDF validators consumed by
[`scripts/validate_pdf.py`](../../scripts/validate_pdf.py). The scanner
checks the rendered PDF text plus `_combined_manuscript.md`, TeX, and
LaTeX logs for unresolved tokens, raw `$` delimiters, missing markers,
undefined references/citations, log warnings/errors, and the compact
margin contract.

```python
@dataclass(frozen=True)
class PdfValidationIssue:
    source: str
    line: int
    message: str
    excerpt: str
    def format(self) -> str

EXPECTED_PDF_MARGINS_IN: dict[str, float]

def scan_pdf_text(text: str, *, source: str = "pdf text") -> list[PdfValidationIssue]
def scan_markdown_artifact(text: str, *,
                           source: str = "combined markdown") -> list[PdfValidationIssue]
def scan_tex_artifact(text: str, *,
                      source: str = "combined tex") -> list[PdfValidationIssue]
def scan_latex_log(text: str, *, source: str = "latex log") -> list[PdfValidationIssue]
def extract_pdf_text(pdf_path: Path, *,
                     template_root: Path | None = None) -> str
def parse_geometry_margins(preamble_text: str) -> dict[str, float]
def validate_preamble_margins(preamble_path: Path) -> list[PdfValidationIssue]
def validate_pdf_artifacts(*, project_root: Path,
                           pdf_path: Path | None = None,
                           template_root: Path | None = None) -> list[PdfValidationIssue]
```

### `variables.py`

Thin facade for the manuscript-variable builder consumed by
``scripts/manuscript_variables.py``. Domain producers live in
``variables_analytical.py``, ``variables_pipeline.py``, and
``variables_sidecars.py``.

```python
PROJECT_ROOT: Path
def build_manuscript_variables(project_root: Path | None = None) -> dict[str, Any]
def build_float_real_residual(project_root: Path | None = None) -> dict[str, float]
def write_float_real_residual(
    output_path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> Path
def write_manuscript_variables(
    output_path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> Path
def _format_lambda_key(lam: float) -> str
def _format_lambda_list(values: tuple[float, ...]) -> str
```

### `variables_analytical.py`

Closed-form Bernoulli, spectral, alignment, motor-attention, coupling-tax,
tensor-train, and sentinel-list producers.

```python
def format_lambda_key(lam: float) -> str
def format_lambda_list(values: tuple[float, ...]) -> str
def bernoulli_facts() -> dict[str, float]
def spectral_facts() -> dict[str, float]
def alignment_and_phase_facts() -> dict[str, float]
def motor_attention_facts() -> dict[str, float]
def coupling_tax_curvature() -> dict[str, float]
def tensor_train_facts() -> dict[str, list[int]]
def sentinel_list_facts() -> dict[str, str | int | float]
```

### `variables_pipeline.py`

Orchestrator counts, Lean declaration scans, registry facts, toolchain pins.

```python
def run_all_facts(project_root: Path) -> dict[str, int]
def strip_lean_comments(src: str) -> str
def count_lean_declarations(project_root: Path, pattern: str) -> int
def lean_facts(project_root: Path) -> dict[str, int]
def registry_facts(project_root: Path) -> dict[str, int]
def toolchain_facts(project_root: Path) -> dict[str, str]
```

### `variables_sidecars.py`

JSON sidecar readers, pymdp facts, GNN round-trip facts, hyperparameter snapshot.

```python
SCALAR_SIDECAR_SENTINEL_RE: re.Pattern[str]
JSON_SIDECAR_REGISTRY: tuple[tuple[str, str, SidecarReader], ...]
def scalar_json_sidecar(path: Path, sentinel_key: str) -> dict[str, object]
def numeric_only_json_sidecar(path: Path, sentinel_key: str) -> dict[str, object]
def json_sidecar_facts(project_root: Path) -> dict[str, object]
def pymdp_facts() -> dict[str, float] | dict[str, str]
def gnn_facts(project_root: Path) -> dict[str, object]
def hyperparameter_facts() -> dict[str, object]
```

### `publication_metadata.py`

Publication canon checks (canonical repository URL, pending DOI banners).

```python
CANONICAL_SOURCE_REPOSITORY: str
WRONG_SOURCE_REPOSITORY: str
UNRESOLVED_SOURCE_REPOSITORY: str
UNRESOLVED_PUBLICATION_DOI: str
UNRESOLVED_ZENODO_RECORD: str
DEFAULT_PUBLICATION_METADATA_PATHS: tuple[str, ...]
DEFAULT_PUBLICATION_REPOSITORY_PATHS: tuple[str, ...]
DEFAULT_PUBLICATION_BANNER_PATHS: tuple[str, ...]
def publication_metadata_issues(project_root: Path, ...) -> list[str]
```

### `readiness.py`

Release-readiness orchestrator consumed by ``scripts/readiness_report.py``.
Emits ``output/reports/release_readiness.{md,json}``, ``release_note.md``,
and ``release_index.md``. Pure audit helpers live in ``readiness_audit.py``.

Hygiene regex constants: ``FORBIDDEN_MATHLIB_LOCAL_TOKENS``,
``MANIFEST_STAGE_RE``, ``MANIFEST_TOTAL_RE``.

```python
def write_release_readiness(project_root: Path) -> Path
def refresh_release_readiness_runtime_budget(project_root: Path) -> None
```

### `readiness_audit.py`

Pure audit helpers for manifest timings, MathlibProofs hygiene, figure/PDF
audits, and git worktree summaries.

```python
def status_counts(lines: list[str]) -> dict[str, int]
def as_float(value: object, default: float = 0.0) -> float
def as_int(value: object, default: int = 0) -> int
def runtime_stage_dicts(runtime_budget: dict[str, object], key: str = "stages") -> list[dict[str, Any]]
def runtime_failed_stage_names(runtime_budget: dict[str, object]) -> list[str]
def format_stage_list(stages: list[dict[str, Any]]) -> str
def optional_json(path: Path) -> dict[str, object]
def git_status_lines(project_root: Path) -> list[str]
def theorem_status_counts(project_root: Path) -> dict[str, int]
def manifest_stage_timings(manifest_path: Path | None = None, *, project_root: Path | None = None) -> dict[str, object]
def mathlib_proofs_status(project_root: Path, runtime_budget: dict[str, object] | None = None) -> dict[str, object]
def registered_figure_paths(project_root: Path) -> set[str]
def figure_audit(project_root: Path, figures: list[Path]) -> dict[str, object]
def pdf_artifact_audit(project_root: Path, status) -> dict[str, object]
def reconcile_runtime_budget(runtime_budget: dict[str, object], *, status, test_results: dict[str, object]) -> dict[str, object]
```

### `index_generator.py`

Auto-generated manuscript table-of-contents builder consumed by
``scripts/generate_index.py``.

```python
def build_index_text(*, project_root: Path) -> str
def write_index(*, project_root: Path) -> Path
```

### `validation_cli.py`

Manuscript completeness gate consumed by ``scripts/validate_manuscript.py``.

```python
EXPECTED_RANGES: dict[str, tuple[float, float]]
def build_parser(*, project_root: Path) -> argparse.ArgumentParser
def main(argv: Sequence[str] | None, *, project_root: Path) -> int
```

### `registry_facts.py`

Single source for registry structural counts consumed by
``scripts/manuscript_variables.py`` and ``manuscript.output_gates``.

```python
THEOREM_STATUS_KEYS: tuple[str, ...]
VALID_FAITHFULNESS: frozenset[str]

def registry_structural_facts(project_root: Path) -> dict[str, int]
def registry_structural_count_gates(project_root: Path) -> dict[str, tuple[float, float]]
```

### `variable_ranges.py`

Closed-form manuscript variable range SSOT shared by
``validation_cli.EXPECTED_RANGES`` and ``output_gates.constants``.

```python
ANALYTICAL_VARIABLE_RANGES: dict[str, tuple[float, float]]
def merge_required_variables(*extensions: dict[str, tuple[float, float]]) -> dict[str, tuple[float, float]]
```

### `output_gates/` package

Release validators for ``output/`` artifacts (figures, CSV sidecars,
manuscript-variable ranges). Consumed by the thin CLI
``scripts/validate_outputs.py``.  Import surface:
``from manuscript import output_gates`` (re-exports below).

#### `output_gates/constants.py`

Path constants: ``PROJECT_ROOT``, ``SRC_DIR``, ``OUTPUT_DIR``,
``PNG_HEADER``.

Figure contract constants:
``MIN_FIGURE_METADATA_SCHEMA_VERSION``, ``MIN_FIGURE_WIDTH``,
``MIN_FIGURE_HEIGHT``, ``MIN_TITLE_FONT_SIZE``, ``MIN_AXIS_FONT_SIZE``,
``MIN_TICK_FONT_SIZE``, ``MIN_LEGEND_FONT_SIZE``,
``MIN_ANNOTATION_FONT_SIZE``, ``VALID_UNCERTAINTY_SEMANTICS``,
``REQUIRED_FIGURES``, ``OPTIONAL_FIGURES``, ``REQUIRED_VARIABLES``.

```python
def registry_count_gates() -> dict[str, tuple[float, float]]
```

#### `output_gates/png_validation.py`

```python
def check_png(path: Path, *, optional: bool = False) -> int
def check_png_semantic_metadata(path: Path, info: dict[str, str]) -> int
```

#### `output_gates/csv_helpers.py`

```python
def parameter_sweep_required_columns(utilities: Sequence[float] | None = None) -> set[str]
def read_csv_rows(path: Path) -> list[dict[str, str]]
def grid_values(rows: Sequence[dict[str, str]], column: str) -> list[float]
def rows_match_grid(
    rows: Sequence[dict[str, str]],
    *,
    column: str,
    expected: Sequence[float],
    tol: float,
) -> bool
```

#### `output_gates/pymdp_validators.py` (facade)

Re-exports pymdp sidecar validators from domain modules below.
Import surface unchanged for ``scripts/validate_outputs.py`` and tests.

#### `output_gates/pymdp_sweep_validators.py`

```python
def validate_sweep() -> int
def validate_free_energy_bundle() -> int
def validate_multi_k_sweep() -> int
```

#### `output_gates/pymdp_long_horizon_validators.py`

```python
def validate_long_horizon() -> int
def validate_long_horizon_replicates() -> int
def validate_long_horizon_seed_diagnostics() -> int
def validate_long_horizon_threshold_sensitivity() -> int
```

#### `output_gates/pymdp_revertibility_validators.py`

```python
def validate_revertibility() -> int
def validate_run_log() -> int
```

#### `output_gates/pymdp_robustness_validators.py`

```python
def validate_robustness_suite() -> int
def validate_coupling_ablation() -> int
def validate_marginal_null_control() -> int
def validate_interaction_robustness() -> int
```

#### Legacy pymdp validator surface (re-exported)

All ``validate_*`` entry points above are also available via
``from manuscript.output_gates import pymdp_validators``:

```python
def validate_sweep() -> int
def validate_free_energy_bundle() -> int
def validate_multi_k_sweep() -> int
def validate_long_horizon() -> int
def validate_revertibility() -> int
def validate_robustness_suite() -> int
def validate_coupling_ablation() -> int
def validate_marginal_null_control() -> int
def validate_interaction_robustness() -> int
def validate_long_horizon_replicates() -> int
def validate_long_horizon_seed_diagnostics() -> int
def validate_long_horizon_threshold_sensitivity() -> int
def validate_run_log() -> int
```

#### `output_gates/sweep_validation.py`

Shared TC / H-gap / decomposition-residual validators for pymdp sweep
sidecars. Consumed by ``pymdp_validators.py``.

```python
def finite(value: float) -> bool
def validate_lambda_zero_mean_field_row(
    row: Mapping[str, object],
    *,
    tc_col: str,
    zero_tol: float,
) -> None
def validate_tc_decomposition_group(
    group: list[dict[str, str]],
    *,
    label: str,
    grid,
    tol: float,
    entropy_tol: float,
    zero_tol: float,
    monotonic_tc: bool = False,
    check_lhs_rhs: bool = False,
    check_decomposition: bool = True,
    finite_columns: tuple[str, ...] = (),
    after_group: Callable[[list[dict[str, str]], list[float]], int] | None = None,
) -> int
```

Optional ``check_decomposition=False`` skips lhs/rhs/residual checks (multi-K sweeps).
Optional ``after_group`` hook validates domain-specific columns after the shared TC pass.

#### `output_gates/artifact_validators.py` + ``__init__.py``

```python
def validate_figures() -> int
def validate_variables() -> int
def main() -> int
```

### `stale_patterns.py`

Shared compiled regexes for stale theorem/figure references in PNG
metadata and prose gates.

```python
STALE_FIGURE_REFERENCE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...]
STALE_FIGURE_REFERENCE_REGEXES: tuple[re.Pattern[str], ...]
```

### `status_patterns.py`

Helpers extracted from ``status.py`` for stale onboarding-doc literals
and live metric table comparisons.

```python
class LiveStatus(Protocol): ...

STATUS_DOCS: tuple[str, ...]

def status_doc_paths(root: Path) -> list[Path]
def stale_doc_patterns(live: LiveStatus | None) -> dict[str, str]
def stale_literal_issues(text: str, rel: str, patterns: dict[str, str]) -> list[str]
def live_status_line_issues(rel: str, line_no: int, line: str, live: LiveStatus) -> list[str]
```

---
