# `tests/` — No-mocks Python test suite

Mirrors [`../src/`](../src/) module-for-module.  Every test runs real
numerical computations on real `numpy` arrays.  No `MagicMock`, no
`mocker.patch`, no `unittest.mock`.

## Status

| Metric | Value |
|---|---|
| Test collection and pass/skip split | Live in [`../output/reports/test_results.json`](../output/reports/test_results.json) after the full suite runs |
| Coverage on `src/` | Live in [`../output/reports/coverage.json`](../output/reports/coverage.json); CI floor 95 % |
| Required coverage floor | 95 % |
| Lean-build gate | `tests/lean/test_lean_build.py` (auto-skipped if `lake` is missing) |
| Per-suite breakdown | [`../docs/reference/statistics_reference.md`](../docs/reference/statistics_reference.md) §7 |
| Live audit page | [`../docs/reference/veridical_status.md`](../docs/reference/veridical_status.md) |

## Running

```bash
# Full suite + coverage (run from the project directory):
uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=95

# Single file:
uv run pytest tests/test_decomposition.py -v

# Single test:
uv run pytest tests/test_bernoulli_toy.py::test_empirical_mi_matches_closed_form -v
```

## File map

| File | Module under test |
|---|---|
| [`test_joint_dist.py`](test_joint_dist.py) | `lean/joint_dist.py` |
| [`test_coupling.py`](test_coupling.py) | `lean/coupling.py` |
| [`test_free_energy.py`](test_free_energy.py) | `lean/free_energy.py` |
| [`test_geometry.py`](test_geometry.py) | `lean/geometry.py` |
| [`test_spectral.py`](test_spectral.py) | `lean/spectral.py` |
| [`test_bernoulli_toy.py`](test_bernoulli_toy.py) | `lean/bernoulli_toy.py` |
| [`test_heterogeneous.py`](test_heterogeneous.py) | `lean/heterogeneous.py` |
| [`test_decomposition.py`](test_decomposition.py) | `lean/decomposition.py` |
| [`test_simulation_specs.py`](test_simulation_specs.py) | `simulation/specs.py`, `simulation/builders.py` |
| [`test_simulation_pymdp.py`](test_simulation_pymdp.py) | `simulation/agents.py`, `simulation/inference.py`, `simulation/rollout.py`, `simulation/sweep.py` |
| [`test_simulation_free_energy.py`](test_simulation_free_energy.py) | `simulation/inference.py::FreeEnergyBundle` (VFE / EFE / entropy / coupling-term contracts) |
| [`test_hyperparameters.py`](test_hyperparameters.py) | `simulation/hyperparameters.py` (grid consistency, JSON mirror) |
| [`test_visualizations.py`](test_visualizations.py) | `visualizations/*.py` |
| [`test_free_energy_plots.py`](test_free_energy_plots.py) | `visualizations/free_energy_plots.py` |
| [`test_figure_scripts.py`](test_figure_scripts.py) | `scripts/generate_figures.py`, `scripts/simulate_pymdp.py` (smoke) |
| [`test_manuscript_registry.py`](test_manuscript_registry.py) | `manuscript/registry.py` |
| [`test_manuscript_renderer.py`](test_manuscript_renderer.py) | `manuscript/renderer.py` (every section file × every token kind) |
| [`test_manuscript_validation.py`](test_manuscript_validation.py) | `manuscript/validation.py` (hyperlinks, figure files, hardcoded-literal detector, malformed-YAML edge cases) |
| [`test_manuscript_section_theorem_refs.py`](test_manuscript_section_theorem_refs.py) | `manuscript/validation.py` cross-references to Lean theorems |
| [`test_manuscript_lean_extraction.py`](test_manuscript_lean_extraction.py) | manuscript ↔ Lean module extraction parity |
| [`test_manuscript_variables_pipeline.py`](test_manuscript_variables_pipeline.py) | `output/data/manuscript_variables.json` shape + range gates |
| [`test_equation_numbering.py`](test_equation_numbering.py) | `manuscript/equation_numbering.py` (per-section auto-numbering, retag, count parity) |
| [`test_american_english.py`](test_american_english.py) | prose-style docs / manuscript sources (American English gate outside code spans) |
| [`test_generate_index.py`](test_generate_index.py) | `scripts/generate_index.py` |
| [`test_logging_utils.py`](test_logging_utils.py) | `simulation/logging_utils.py` (JSONL run logger, runtime, status, schema) |
| [`test_notation_glossary.py`](test_notation_glossary.py) | `manuscript/S06_notation_and_concordance.md` ↔ preamble macros + Python idents + Lean abbrevs (drift gate) |
| [`test_pymdp_extras.py`](test_pymdp_extras.py) | `simulation/statistics.py` + `visualizations/{pymdp_extras,metadata}.py` + the no-hardcoded-numeric-literal detector |
| [`test_python_api_coverage.py`](test_python_api_coverage.py) | `docs/reference/python_api.md` ↔ every public `src/` identifier (documentation drift gate) |
| [`test_veridicality.py`](test_veridicality.py) | end-to-end audit chain: prose `[[VAR:...]]` ↔ JSON ↔ JSONL log ↔ Lean source |
| [`lean/test_lean_build.py`](lean/test_lean_build.py) | `cd lean && lake build` smoke |

## Conventions

* **Imports**: namespaced subpackage paths (`from lean.coupling import …`,
  `from simulation.specs import …`, `from visualizations.heatmaps import …`,
  `from manuscript.registry import …`) — `pythonpath` is set to `../src`
  by [`../pyproject.toml`](../pyproject.toml).
* **Fixtures**: use `np.random.default_rng(seed=…)` with an explicit
  fixed seed for any randomized test.
* **Numerical tolerances**: `1e-12` for exact arithmetic
  (e.g. `is_pmf` of a uniform), `1e-9` for KL / TC checks involving
  logs.
* **Boundary cases**: every module has tests for
  shape-mismatch / out-of-range / zero-mass inputs that should raise
  `ValueError` or `IndexError`.

## Notable invariants checked

| Invariant | Test |
|---|---|
| Total correlation ≥ 0; = 0 iff mean-field | `test_total_correlation_zero_for_mean_field`, `test_total_correlation_positive_for_correlated` |
| Total correlation = KL to m-projection (Prop 7.3) | `test_total_correlation_via_kl_matches_direct` |
| m-projection minimizes KL among mean-fields (Prop 7.2) | `test_m_projection_minimises_kl_against_random_candidate` |
| log-weight is affine in λ (Theorem 7.4) | `test_log_weight_affine_in_lambda_recovers_slope`, `test_coupling_log_weight_is_affine_in_lambda`, `test_is_e_geodesic_for_ising_K2` |
| Pythagorean residual ≈ 0 (Prop 7.5) | `test_pythagorean_residual_zero_for_any_reference` |
| Schmidt rank 1 ⇔ mean-field (Prop 8.1) | `test_schmidt_rank_one_for_outer_product`, `test_schmidt_rank_two_for_correlated_joint`, `test_schmidt_rank_one_iff_mean_field_holds_for_*` |
| Coupling tax ≥ 0; = 0 for pure-mode ensembles | `test_coupling_tax_zero_for_purely_reflexive`, `test_coupling_tax_zero_for_purely_planning`, `test_coupling_tax_positive_for_heterogeneous_at_nonzero_lambda` |
| O(λ²) coupling-tax bound (Theorem 9.1) | `test_coupling_tax_within_quadratic_bound_holds_for_small_lambda` |
| Closed-form vs empirical MI of K=2 Ising | `test_empirical_mi_matches_closed_form` |
| pymdp λ=0 free-energy baseline (TC=0, coupling=0, H(q)=ΣH(q^k)) | `test_free_energy_bundle_lambda_zero_baseline` |
| pymdp total correlation monotone in λ (Prop 7.3 inside POMDP) | `test_total_correlation_monotone_under_symmetric_coupling` |
| Joint-entropy sub-additivity at every λ | `test_joint_entropy_le_sum_marginal_entropies` |
| Bundle ↔ standalone helpers consistency | `test_efe_under_posterior_matches_explicit_helper`, `test_coupling_energy_matches_bundle_term` |
| Equation auto-numbering: source eq count = rendered tag count per section | `test_rendered_section_has_no_unnumbered_display_math`, `test_rendered_section_tags_match_section_number` |
| Reader-facing prose uses American English outside code identifiers and citation titles | `test_reader_facing_docs_use_american_english` |
| Hyperparameters JSON mirror equals source-of-truth constants | `test_summary_matches_manuscript_variables_json_when_present` |
