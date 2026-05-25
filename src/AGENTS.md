# AGENTS.md — `src/`

## Layout

Python companion package for the Policy Entanglement project, organized
into five subpackages — the four domain subpackages each have their own
`AGENTS.md`, while `reporting/` is a small local support package:

| Subpackage | Path | Purpose |
|---|---|---|
| `lean` | [`src/lean/`](lean/) | Analytical mirrors of the Lean 4 boundary fragment (joint distributions, coupling, free energies, geometry, spectral, heterogeneous, Bernoulli toy, decomposition theorem) plus a numerical-witness layer (`invariants.py`) feeding the dashboard |
| `simulation` | [`src/simulation/`](simulation/) | pymdp 1.0.1 POMDP harness for coupled-policy ensembles (specs, builders, agents, inference, rollout, sweep, statistics) — also owns the `hyperparameters.py` source-of-truth, the `FreeEnergyBundle` (VFE / EFE / entropy / coupling-term / TC / action-distribution), and the JSONL `RunLogger` |
| `visualizations` | [`src/visualizations/`](visualizations/) | Reusable plotting helpers (heatmaps, joint plots, spectral, trajectory, graph, log-weight, free-energy dashboards, pymdp-extra dashboards) plus the PNG `tEXt` reproducibility-metadata helpers |
| `manuscript` | [`src/manuscript/`](manuscript/) | Manuscript registry, token renderer, equation auto-numbering pipeline, citation / bibliography helpers, Lean-source extraction, validators, release output gates (`output_gates/`, `registry_facts.py`, `stale_patterns.py`, `status_patterns.py`) |
| `reporting` | [`src/reporting/`](reporting/) | Dashboard HTML/JSON/plaintext emission; prefers `infrastructure.reporting.interactive_dashboard` when the repo root is on `PYTHONPATH`, otherwise falls back to `_interactive_dashboard_local.py` |
| `dashboard_types` | [`src/dashboard_types/`](dashboard_types/) | Shared `Panel`, `Control`, and `Invariant` dataclasses consumed by `lean/invariants.py` and `reporting/` |
| `gates` | [`src/gates/`](gates/) | Parameterised pipeline gate logic (`regression_gate.py` — pytest-count parsing, coverage-floor inspection, dashboard-invariant + Lean-budget snapshots) re-exported by the thin script wrapper. Name avoids the `manuscript/validation.py` collision on the bare-import sys.path |
| `orchestration` | [`src/orchestration/`](orchestration/) | End-to-end pipeline runner (`run_all.py` — canonical `SCRIPTS` order, `PDF_SCRIPTS` / `MATHLIB_PROOF_SCRIPTS` extensions, parallel producer batch, `MANIFEST.md` writer) re-exported by the thin script wrapper |

## Constitution

1. **Pure compute, no I/O.**  Every module under `src/` is a library:
   takes ndarrays, returns ndarrays / floats / dataclasses.  Print, save,
   plot — none of that.  I/O lives in [`../scripts/`](../scripts/).
   Documented exceptions:
   * `visualizations/` writes PNGs (figure helpers) and reads PNG `tEXt`
     metadata back (`metadata.read_figure_metadata`); driven by scripts
     and tests, never imported by `lean/` or `simulation/`.
   * `simulation/logging_utils.py` appends JSONL records to
     `output/logs/pymdp_runs.jsonl` so `coupled_policy_posterior` calls
     leave a structured audit trail.  Disable with
     `PYMDP_RUN_LOG_DISABLED=1` or pass `enabled=False`.
   * `visualizations/metadata._git_revision` shells out to `git
     rev-parse --short HEAD` for PNG provenance; degrades to
     `"unknown"` outside a git checkout.
2. **No mocks, no stubs.**  Tests pass real arrays through the actual
   computations.  If you need configurable behavior, add a parameter,
   don't add a mock.
3. **Namespaced imports.**  `src/` is on `pythonpath`; every test and
   script uses the canonical subpackage path:
   `from lean.coupling import …`, `from simulation.specs import …`,
   `from visualizations.heatmaps import …`,
   `from manuscript.registry import …`. Intra-subpackage imports use
   the relative form (`from .coupling import …`). Bare imports
   (`from coupling import …`) are not supported.
4. **Type hints everywhere.**  Public signatures use
   `numpy.typing.NDArray[np.float64]` aliased as `ArrayF`.
5. **Validate at boundaries.**  Public entry points raise
   `ValueError` / `IndexError` on shape / index issues with
   informative messages.
6. **Determinism.**  No `time`, no module-level randomness.  RNGs are
   created locally with explicit seeds in tests.
7. **Coverage floor: 95 %.**  Each new function lands with tests in
   `tests/test_<module>.py`.

## Cross-subpackage rules

* `lean/` is the analytical core — no `pymdp`, no `matplotlib`,
  no `seaborn` / `networkx`.  Phase-transition λ constants live in
  `lean/phase_constants.py` (re-exported by `simulation/hyperparameters.py`).
  `lean/invariants.py` imports `Invariant` from `dashboard_types.dashboard`
  (pure dataclass; no HTML/reporting dependency).
* `dashboard_types/` holds shared dashboard dataclasses only; no I/O,
  no imports from domain subpackages.
* `reporting/` may import `dashboard_types` and optionally
  `infrastructure.reporting.interactive_dashboard`; it must not import
  from `simulation/` or `manuscript/`.
* `simulation/` may import from `lean/` but **not** from
  `visualizations/` or `manuscript/`.  Shared TC metrics live in
  `simulation/metrics.py`; robustness scenario builders in
  `simulation/robustness_scenarios.py`; Wilson intervals in
  `simulation/robustness_stats.py`; orchestration in
  `simulation/robustness.py`.
* `visualizations/` may import from `lean/` (for analytical helpers
  used in plot construction) and may consume `simulation` outputs at
  call time, but does no inference of its own.
* `manuscript/` is purely textual — no `pymdp`, no `numpy`-heavy
  computation, no plotting.  It loads YAML registries, reads the
  pre-computed `output/data/manuscript_variables.json`, and rewrites
  Markdown.  Release gates live in `manuscript/output_gates/` (split validators:
  `artifact_validators.py`, `pymdp_validators.py`, `png_validation.py`,
  `csv_helpers.py`, `constants.py`) and `registry_facts.py`; shared stale
  regexes in `stale_patterns.py`; status-doc helpers in `status_patterns.py`.

## Mirror invariant

For every concept that lives in
[`../lean/ActinfPolicyEntanglement/<Module>.lean`](../lean/ActinfPolicyEntanglement/),
provide an executable Python implementation in `src/lean/<module>.py`
and a test in `tests/test_<module>.py`.  This is the load-bearing
sanity rail for the eventual Mathlib-backed Lean proofs.

## Numerical pitfalls

* **`log(0)`**: use `_safe_log` (in `lean/free_energy.py`) when computing
  `∑ q · log q`; floors at `1e-300` so zero entries don't blow up.
* **Floating divisions**: `normalize()` raises if the total mass is
  ≤ 0.  Never divide by an unchecked sum.
* **Schmidt rank**: choose the SVD threshold deliberately
  (`atol=1e-9` works for most cases; `1e-12` is too tight for the
  Ising posterior at finite λ where the small singular value is
  ~1e-10).
* **Multi-information term in Theorem 5.1**:
  Prefer `multi_information_term`; `total_correlation_gain` is the Lean-named
  synonym (`totalCorrelationGain`). Both return `+I(q)` as in Gibbs `tc_decomp`.
* **`free_energy_against_entangled_prior`**: Uses manuscript
  `G_\lambda = \sum_k G_k + \lambda K_c` against normalized `E_\lambda`; matches
  `entanglement_decomposition_rhs(...).total` (see `tests/test_decomposition.py`).
* **pymdp double-EFE**: `coupled_policy_posterior` passes `zero_G` to
  `entangled_posterior` because pymdp's `q_pi` already absorbs the
  per-stream EFE.  Do not "fix" this by piping `per_stream_efe`'s
  output back in — that double-counts the bias.
