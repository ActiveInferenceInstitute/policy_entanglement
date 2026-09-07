# Python API reference

*Latest generated audit.*  The current public `src/<subpackage>/`
surface spans analytical mirrors, pymdp simulations, visualization
helpers, manuscript rendering/validation, local dashboard/reporting,
and release-status auditors.
When a public identifier is added, update the relevant per-subpackage
page in this directory and keep the package facade in sync.

Per-function signatures and contracts for the five subpackages of
[`../../src/`](../../src/), split across one file per subpackage so each
page is self-contained and easy to grep:

| Subpackage | Purpose | Detailed reference |
|---|---|---|
| [`src/lean/`](../../src/lean/) | Analytical mirrors of the Lean boundary fragment | [`python_api_lean.md`](python_api_lean.md) |
| [`src/simulation/`](../../src/simulation/) | pymdp 1.0.1 POMDP harness | [`python_api_simulation.md`](python_api_simulation.md) |
| [`src/visualizations/`](../../src/visualizations/) | Reusable plotting helpers | [`python_api_visualizations.md`](python_api_visualizations.md) |
| [`src/manuscript/`](../../src/manuscript/) | Auto-injection + validation toolkit | [`python_api_manuscript.md`](python_api_manuscript.md) |
| [`src/gnn/`](../../src/gnn/) | GNN fifth-track parser + round-trip + Lean typed-contract emitter | [`python_api_gnn.md`](python_api_gnn.md) |
| [`src/reporting/`](../../src/reporting/) | Standalone dashboard/reporting helpers | This page |

## Module index by subpackage

* **`lean/`** — `joint_dist.py`, `coupling.py`, `free_energy.py`,
  `geometry.py`, `spectral.py`, `bernoulli_toy.py`, `heterogeneous.py`,
  `decomposition.py`, `invariants.py`.
* **`simulation/`** — `specs.py`, `builders.py`, `agents.py`,
  `inference.py`, `hyperparameters.py` (facade; domain splits
  `hyperparameters_{grids,pymdp,robustness,experiments,sentinels}.py`),
  `statistics.py`,
  `logging_utils.py`, `rollout.py`, `sweep.py`, `long_horizon.py`,
  `multi_k_experiments.py`, `revertibility.py`, `robustness.py`,
  `btai_baseline.py`, `adversarial.py`, `cross_references.py`.
* **`visualizations/`** — `setup.py`, `heatmaps.py`, `joint_plots.py`,
  `spectral_plots.py`, `trajectory_plots.py`, `graphs.py`,
  `geodesic.py`, `log_weight.py`, `free_energy_plots.py`,
  `pymdp_extras.py`, `metadata.py`, `multi_k_plots.py`,
  `robustness_plots.py`, `annotations.py`, `analytical_figures.py`.
* **`docs/manuscript/`** — `registry.py`, `tokens.py`, `renderer.py`,
  `bibliography.py`, `lean_extract.py`, `equation_numbering.py`,
  `validation.py`, `variable_ranges.py`, `status.py`, `pdf_validation.py`, `variables.py`,
  `output_gates/`.
* **`gnn/`** — `parser.py`, `model.py`, `bridge.py`, `runner.py`,
  `lean_emit.py`.
* **`dashboard_types/`** — `dashboard.py` (shared dashboard datatypes +
  builder consumed by `scripts/build_dashboard.py`).
* **`orchestration/`** — `run_all.py` (library pipeline runner for
  `scripts/run_all.py`).
* **`gates/`** — `regression_gate.py` (library regression gate for
  `scripts/regression_gate.py`).
* **`reporting/`** — `interactive_dashboard.py`,
  `_interactive_dashboard_compat.py`, `_interactive_dashboard_fallback.py`.

## Subpackage `lean/`

→ Full reference: [`python_api_lean.md`](python_api_lean.md).

Numerical companions to the Lean boundary fragment. Each module
mirrors a `lean/ActinfPolicyEntanglement/<Module>.lean` file. Joint /
mean-field PMF arithmetic, coupling potentials, free energies,
information geometry, spectral decomposition, and the K=2 Bernoulli
closed form all live here.

## Subpackage `simulation/`

→ Full reference: [`python_api_simulation.md`](python_api_simulation.md).

pymdp-grounded POMDP harness, structured JSONL run logging, and the
auto-injected hyperparameter registry. The free-energy bundle
(VFE / EFE / entropy / coupling-term / TC) and quantile-envelope
aggregation are also here.

## Subpackage `visualizations/`

→ Full reference: [`python_api_visualizations.md`](python_api_visualizations.md).

Pure I/O + plotting; no numerical work. Every figure carries
reproducibility metadata (source script + function, hyperparameter
snapshot, git revision, ISO timestamp) via `metadata.py`.

## Subpackage `docs/manuscript/`

→ Full reference: [`python_api_manuscript.md`](python_api_manuscript.md).

Token rendering, equation auto-numbering, Lean-source extraction,
and the manuscript validator with the four-track-coherence CI gate
(`validate_lean_wiring`). See
[`four_track_coherence.md`](four_track_coherence.md) for the contract.

## Subpackage `reporting/`

Project-local dashboard and invariant-reporting helpers. This package is
the standalone-safe reporting dependency used by `lean.invariants` and
`scripts/build_dashboard.py`; it does not import the parent template.

### `interactive_dashboard.py`

Public identifiers: `PLOTLY_CDN`, `Control`, `Panel`, `Invariant`,
`InteractiveDashboard`.

`Control` and `Panel` are small dataclasses for dashboard controls and
Plotly-compatible panel payloads. `Invariant` evaluates numeric contracts
such as equality, ordering, finite/nonnegative values, monotonicity, and
array closeness. `InteractiveDashboard` writes the dashboard HTML, panel
JSON, invariant text report, and summary JSON consumed by the release
pipeline. `PLOTLY_CDN` pins the Plotly CDN URL embedded in the HTML.

When the parent template is on ``PYTHONPATH``, HTML assembly delegates to
``infrastructure.reporting._interactive_html.render_interactive_dashboard_html``;
otherwise ``_interactive_dashboard_fallback.render_interactive_dashboard_html``
supplies the same contract.

### `dashboard_types/dashboard.py`

Importable dashboard builder and shared datatypes (`Panel`, `Control`,
`Invariant`) used by `scripts/build_dashboard.py` and
`reporting.interactive_dashboard`.

Path constants: `DASHBOARD_PROJECT_ROOT`, `WEB_DIR`, `DATA_DIR`, `REP_DIR`.

```python
def parse_dashboard_args(argv: list[str] | None = None) -> argparse.Namespace
def build_dashboard_payload(args: argparse.Namespace) -> dict[str, Any]
def build_dashboard(args: argparse.Namespace, payload: dict[str, Any]) -> Any
def write_dashboard(args: argparse.Namespace) -> dict[str, Path]
```

> Release-readiness orchestration lives in
> [`docs/manuscript/readiness.py`](python_api_manuscript.md#readinesspy)
> (consumed by `scripts/readiness_report.py`); the `reporting/`
> subpackage covers only the standalone dashboard helpers above.

### `dashboard_types/payload.py`

Typed payload dataclass shared by the dashboard builder and the JSON
emitter.

```python
@dataclass
class DashboardPayload: ...
```

### `dashboard_types/panel_builders.py`

Per-panel builder functions composing the six dashboard views from
sweep / invariant series.

```python
def mi_curves_panel(...) -> Panel
def joint_heatmap_panel(...) -> Panel
def entropy_decomp_panel(...) -> Panel
def fe_curves_panel(...) -> Panel
def phase_panel(...) -> Panel
def schmidt_panel(...) -> Panel
```

### `dashboard_types/plotly_traces.py`

Shared Plotly trace/layout primitives used by the panel builders.

```python
def scatter_line(...) -> go.Scatter
def scatter_markers(...) -> go.Scatter
def axis_layout(...) -> dict[str, Any]
```

### `orchestration/run_all.py`

Importable end-to-end pipeline runner consumed by `scripts/run_all.py`.
Stage order is the module-level `SCRIPTS` list; optional `PDF_SCRIPTS` and
`MATHLIB_PROOF_SCRIPTS` extend the DAG when requested.

```python
class StageResult(NamedTuple): ...
class StageSummary(TypedDict): ...
def build_parser() -> argparse.ArgumentParser
```

### `orchestration/build_pdf.py`

Combined-PDF renderer consumed by `scripts/build_pdf.py`. Regenerates the
injected manuscript tree, merges sections, and runs the local Pandoc/XeLaTeX
pass audited by `scripts/validate_pdf.py`.

```python
COMBINED_STEM: str
def inject_rendered_manuscript(*, project_root: Path) -> int
def regenerate_injected_manuscript(*, project_root: Path) -> int
def render_combined_pdf(*, project_root: Path) -> int
```

### `orchestration/pdf_config.py`

Typed `ManuscriptConfig` loaded from `docs/manuscript/config.yaml`,
providing Pandoc metadata arguments and the LaTeX author block.

```python
@dataclass
class ManuscriptConfig: ...
    def pandoc_metadata_args(self, *, project_root: Path) -> list[str]
    def author_block(self) -> str
def latex_text(value: str) -> str
def latex_href_url(value: str) -> str
```

### `orchestration/pdf_compile.py`

Pandoc/XeLaTeX compile helpers used by `render_combined_pdf`.

```python
def run_command(cmd: Sequence[str], *, cwd: Path, stdout_path: Path | None = None) -> None
def run_bibtex(*, pdf_dir: Path) -> None
def insert_preamble_into_tex(*, combined_tex: Path, preamble_tex: Path) -> None
def shorten_caption_aux_entries(*, combined_tex: Path) -> None
def pandoc_to_tex(*, combined_md: Path, combined_tex: Path, pdf_dir: Path,
                  preamble_tex: Path, config: ManuscriptConfig, project_root: Path) -> None
def latex_to_pdf(*, combined_tex: Path, pdf_dir: Path, pdf_path: Path,
                 xelatex_stdout: Path) -> Path
```

### `orchestration/pdf_tex_patch.py`

Combined-TeX post-processing: red-hyperlink patching aligned with the
template renderer and preamble insertion / artifact cleanup.

```python
def patch_red_hyperlinks(...) -> None
def postprocess_combined_tex(*, combined_tex: Path, config: ManuscriptConfig) -> None
```

### `orchestration/stages.py`

Pipeline stage graph and resolution (`SCRIPTS`, `PDF_SCRIPTS`,
`MATHLIB_PROOF_SCRIPTS`, `PARALLEL_STAGE_STEMS`).

```python
@dataclass(frozen=True)
class StageFlags: ...
def stage_stem(script: str) -> str
def included(stem: str, flags: StageFlags) -> bool
def resolve_stages(flags: StageFlags, scripts: list[tuple[str, str]] | None = None) -> list[tuple[str, str]]
```

### `orchestration/executor.py`

Stage execution (serial + parallel batches) and manifest summaries.

```python
class StageResult(NamedTuple): ...
@dataclass
class ExecutionOutcome: ...
def spawn(script: str, *, capture: bool, scripts_dir: Path, project_root: Path) -> StageResult
def run_serial(script: str, *, scripts_dir: Path, project_root: Path) -> int
def run_parallel_batch(scripts: list[str], *, max_workers: int, scripts_dir: Path, project_root: Path) -> list[StageResult]
def execute_pipeline(*, flags: StageFlags, project_root: Path, scripts_dir: Path,
                     parallel: bool, max_workers: int,
                     write_pre_regression_manifest: bool,
                     scripts: list[tuple[str, str]] | None = None,
                     parallel_stems: frozenset[str] | None = None) -> ExecutionOutcome
```

### `orchestration/manifest.py`

`output/MANIFEST.md` writer (stage timings, hashes, skipped large files).

```python
class StageSummary(TypedDict): ...
def write_manifest(*, project_root: Path, run_summary: dict[str, Any]) -> Path
```

### `gates/regression_gate.py`

Thin orchestrator facade for the pipeline regression gate (consumed by
`scripts/regression_gate.py`). Baseline I/O lives in
`gates/regression_baseline.py`; pytest subprocess runners in
`gates/regression_pytest.py`.

```python
def gate(*, project_root: Path, scripts_dir: Path, baseline_path: Path | None = None, update_baseline: bool = False) -> int
```

Re-exports for unit tests: `_parse_pytest_counts`, `_critical_module_coverage_issues`,
`_write_fresh_test_results`, `_coverage_fail_under`, `_load_baseline`, `_load_test_results`.

### `gates/regression_baseline.py`

Baseline JSON load/save and refresh helpers.

```python
def load_baseline(baseline_path: Path) -> dict[str, Any]
def load_test_results(test_results_path: Path) -> dict[str, Any] | None
def refresh_baseline(baseline: dict[str, Any], *, baseline_path: Path, project_root: Path, ...) -> None
```

### `gates/regression_pytest.py`

Fresh pytest+coverage snapshot, invariant parsing, Lean budget parse.

```python
CRITICAL_COVERAGE_MODULES: dict[str, float]
def coverage_fail_under(project_root: Path) -> float
def parse_pytest_counts(output: str) -> dict[str, int]
def coverage_percent_from_json(path: Path) -> float
def critical_module_coverage_issues(path: Path, thresholds: dict[str, float] | None = None) -> list[str]
def clear_bytecode_cache(project_root: Path) -> int
def write_fresh_test_results(*, project_root: Path, test_results_path: Path, pytest_log_path: Path, coverage_json_path: Path) -> dict[str, Any] | None
def count_invariants(invariants_path: Path) -> tuple[int, int] | None
def lean_budget_snapshot(*, project_root: Path, scripts_dir: Path) -> dict[str, int] | None
```

## Conventions

* `ArrayF = numpy.typing.NDArray[numpy.float64]`.
* `Sequence[ArrayF]` is used for the K-tuple of per-stream marginals
  (or per-stream EFEs).
* Joint distributions are dense `ndarray`s with one axis per stream.
* Errors raised: `ValueError` for shape / value mismatches,
  `IndexError` for out-of-range indices.
* Determinism: every randomness-bearing helper takes an explicit seed;
  module-level RNGs are forbidden.
* Imports: every consumer uses the canonical namespaced subpackage path:
  `from lean.joint_dist import …`, `from simulation.specs import …`,
  `from visualizations.heatmaps import …`,
  `from manuscript.registry import …`. `pythonpath` is set to `src/`
  (see `pyproject.toml`); intra-subpackage imports use the relative
  form (`from .joint_dist import …` inside `src/lean/coupling.py`).
