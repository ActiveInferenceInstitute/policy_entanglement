# pymdp Validation: Three-Tier CI Gates, Structured JSONL Run Log, and Bit-Reproducibility Contract

The pymdp harness ([[SECREF:pymdp_harness]]) and free-energy bundle
([[SECREF:pymdp_free_energy]]) are the *runtime layer*.  This
sub-section documents the **validation gates** that protect the
manuscript from drift between the runtime and what is asserted in
prose, plus the **structured run log** that records every load-bearing
quantity for post-hoc audit.

## Three-tier validation

Every pymdp artifact passes through three CI gates.  Any one failing
fails the pipeline:

| Tier | What it asserts | Source |
|---|---|---|
| **Numerical contracts** (pytest, no mocks) | shape / type / determinism / λ = 0 baseline / sub-additivity / monotonicity / bundle ↔ helper agreement | [`tests/test_simulation_pymdp.py`](../tests/test_simulation_pymdp.py), [`tests/test_simulation_free_energy.py`](../tests/test_simulation_free_energy.py) |
| **Output gates** (`scripts/validate_outputs.py`) | every PNG header is valid; every JSON key in expected range; the closed-form vs empirical MI residual ≤ $[[VAR:param_sweep_agreement_tolerance:.0e]]$; the free-energy bundle's λ = 0 baseline (TC = 0, coupling = 0, $H(q) = \sum_k H(q^k)$) and TC ≥ 0 everywhere | [`scripts/validate_outputs.py`](../scripts/validate_outputs.py) |
| **Manuscript completeness** (`scripts/validate_manuscript.py`) | every `[[FIG:<label>]]`, `[[EQ:<label>]]`, `[[VAR:<key>]]`, `[@<citekey>]`, `[[SECREF:<label>]]`, `[[THMREF:<label>]]` resolves; every numeric variable lies in its expected range; no hardcoded `§N.M` outside permitted sites | [`scripts/validate_manuscript.py`](../scripts/validate_manuscript.py) |

Run all three with the orchestrator:

```bash
uv run python scripts/run_all.py
```

([[VAR:run_all_script_count]] scripts in canonical order, exits non-zero on any failure.)

The reader-facing order is:

| Stage group | Role in the evidence chain |
|---|---|
| Lean + analytical prelude | Build the boundary fragment and render pure-NumPy analytical figures. |
| Empirical producer batch | Write the Bernoulli, pymdp, multi-K, long-horizon, and revertibility sidecars. |
| Variable materialization | Convert hyperparameters plus current sidecar summaries into `output/data/manuscript_variables.json`. |
| Manuscript rendering | Substitute `[[VAR:...]]`, figure, theorem, section, citation, and equation tokens into `output/manuscript/`. |
| Gates | Validate artifacts, validate prose, then compare test / coverage / invariant / Lean-budget metrics against the regression baseline. |

This is a dependency order, not just a convenience order.  In
particular, `manuscript_variables.py` runs after the empirical
sidecars because it reads the multi-K, long-horizon, and
revertibility summaries.  A clean run therefore cannot render prose
from a previous run's sidecar values.

**Dual-tolerance contract.**  Two tolerances coexist in the harness:
(i) a stricter **sentinel cross-check** at the
[[VAR:bernoulli_verification_lambdas_count]] $\lambda$ values
$\{[[VAR:bernoulli_verification_lambdas]]\}$ asserts that the
closed-form mutual information matches the *numeric* total correlation
of the same closed-form joint to $< [[VAR:bernoulli_verification_tolerance:.0e]]$
— an **internal analytic-consistency** check (two algebraically
independent closed forms of the same quantity must agree to numerical
precision), *not* an independent empirical confirmation; the genuine
finite-$N$ seeded Monte-Carlo estimate
(`empirical_mutual_information_montecarlo`, §[[SECREF:empirical]]) is
the separate sampling-based witness (`tests/test_bernoulli_toy.py`);
(ii) a looser
**parameter-sweep CI gate** at
$[[VAR:param_sweep_agreement_tolerance:.0e]]$ asserts the
same match across the full $[[VAR:param_sweep_grid_points]]$-point
$(\lambda, \Delta)$ parameter sweep (`scripts/validate_outputs.py`).
Both tolerances are real and report distinct guarantees: the sentinel
check pins exact analytical agreement at hand-picked $\lambda$, the
sweep gate bounds drift across the entire grid.

## Structured run log (JSONL)

Every pymdp script emits one structured-record line per (script,
λ-sweep, observation, rollout) call to
[`output/logs/pymdp_runs.jsonl`](../output/logs/pymdp_runs.jsonl)
via `simulation.logging_utils.RunLogger`.  Each record is a single
JSON object on its own line (JSONL), with the schema:

The full field schema (13 fields: `timestamp`, `script`, `event`, `section`,
hyperparameters `K`/`gamma`/`lam`/`seed`/`T`, `observations`, grid descriptors,
bundle observables, λ=0 sentinels, `sampled_actions`, `runtime_ms`, `status`) is
in [[SECREF:app.jsonl_schema]] (supplement).

Inspect with `jq`:

```bash
# Show every record's runtime + status:
jq -c '{timestamp, section, runtime_ms, status}' \
   output/logs/pymdp_runs.jsonl

# Extract the λ = 0 free-energy baseline:
jq 'select(.section=="figure_pymdp_free_energies") |
    {coupling_term_at_lambda_zero, joint_entropy_at_lambda_zero,
     marginal_entropy_sum_at_lambda_zero}' \
   output/logs/pymdp_runs.jsonl
```

The validator
[`scripts/validate_outputs.py::validate_run_log`](../scripts/validate_outputs.py)
fails CI if:

* the JSONL file is malformed,
* fewer than three records are present,
* any required `section` (`figure_pymdp_lambda_sweep`,
  `figure_pymdp_rollout`, `figure_pymdp_free_energies`) is missing,
* any record lacks a `timestamp`.

## Software and source provenance

The pymdp validation layer is intentionally standalone-local.  The
release environment is refreshed with:

```bash
uv sync --group sim --group viz --group lint
```

The `sim` group supplies `inferactively-pymdp==1.0.1`; the lockfile
records the exact wheel / source archive, and the methods prose cites
the JOSS paper plus the official source and documentation
[@heins-2022; @pymdp-developers-2026; @pymdp-docs-2026].  The only
module allowed to import `pymdp`/JAX is
[`src/simulation/agents.py`](../src/simulation/agents.py); the no-mock
test policy forbids replacing that boundary with `MagicMock`,
`unittest.mock`, `mocker.patch`, or equivalent fake call paths.  A
clean collection run therefore proves that `lean.invariants`, the
dashboard builder, and the pymdp harness import from this checkout
without requiring a parent template on `PYTHONPATH`.

## Reproducibility contract

Two consecutive `run_all.py` invocations on the same code produce
**numerically identical** CSVs and JSON variable dumps.  PNG rasters
are bit-identical modulo the `project.timestamp` and
`project.git_revision` `tEXt` metadata chunks, which embed run-time
provenance for audit purposes; the JSONL run log similarly records
per-run wall-clock timestamps.  Strict byte-level reproducibility
across the metadata chunks requires pinning these to a
`SOURCE_DATE_EPOCH`-style fixed value at run time.  The guarantees
that make this contract possible:

* `pymdp.agent.Agent(inference_algo='fpi')` — deterministic FPI, no
  random sampling inside `infer_states` / `infer_policies`.
* All RNG-bearing calls go through `np.random.default_rng(seed=...)`
  with seeds pinned in
  [`src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py)
  (`FIGURE_GLOBAL_SEED = [[VAR:figure_global_seed]]`,
  `PYMDP_ROLLOUT_SEED = [[VAR:pymdp_rollout_seed]]`).
* `MPLBACKEND=Agg` is set at every figure-script entrypoint to
  prevent platform-dependent figure rasterisation.
* Every grid count / λ range / rollout horizon flows from the
  hyperparameters module, then through the JSON mirror, then into
  prose via `[[VAR:<key>]]` — there is no place a number can drift.

## Test budget snapshot

| Suite | Coverage |
|---|---|
| `tests/test_simulation_pymdp.py` | per-stream EFE / posterior PMFs, λ = 0 baseline, monotonicity, deterministic rollout |
| `tests/test_simulation_free_energy.py` | every `FreeEnergyBundle` invariant + bundle ↔ helper agreement |
| `tests/test_simulation_specs.py` | `StreamSpec` / `CoupledEnsembleSpec` shape + column-stochasticity validation |
| `tests/test_free_energy_plots.py` | every dashboard PNG header, on real bundle data |
| `tests/test_figure_scripts.py` | every `figure_*` function in `simulate_pymdp.py` smoke-tested |
| `tests/test_logging_utils.py` | structured JSONL emission, runtime measurement, status propagation, schema |
| `tests/test_multi_k_experiments.py` | configured multi-K ensemble sweeps $K \in \{[[VAR:multi_k_values_list]]\}$: TC monotonicity, aligned-mass growth, TT-rank profile, $\lambda = 0$ mean-field baseline |
| `tests/test_long_horizon.py` | $T=[[VAR:long_horizon_steps]]$ long-horizon rollout: deterministic reproducibility, tail-window steady-state KL bound, habit-accumulation monotonicity |
| `tests/test_revertibility.py` | `revertibility_kl_equals_multiinformation`: $I(q_\lambda) = D_{\mathrm{KL}}(q_\lambda\,\|\,\hat m(q_\lambda))$ to floating-point tolerance ($\le [[VAR:revertibility_max_kl_residual:.2e]]$ maximum residual) on every $\lambda$ in the sweep — an **internal analytic-consistency** check of [[THMREF:prop_6_3]] (both sides are the *same* finite-sum quantity via `total_correlation_via_kl`; true by construction, *not* an independent empirical witness) |
| `tests/test_robustness.py` | one-axis robustness scenarios, targeted two-axis interactions, coupling ablations, fixed-marginal null controls, long-horizon replicate summaries, Wilson intervals, and threshold-sensitivity summaries |
| `tests/test_robustness_plots.py` / `tests/test_metadata_pure.py` | stress-test figure writers and metadata semantics for robustness envelopes, ablation summaries, null-control figures, replicate envelopes, and threshold-sensitivity plots |

See the full per-suite breakdown in
[`docs/reference/statistics_reference.md`](../docs/reference/statistics_reference.md).

---
