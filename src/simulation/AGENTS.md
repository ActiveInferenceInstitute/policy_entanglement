# AGENTS.md — `src/simulation/`

`inferactively-pymdp==1.0.1`-backed POMDP simulation harness for
coupled-policy active-inference ensembles, using the `pymdp` import/API.
Companion to the analytical mirrors in `src/lean/`.

## Module map

| File | Role |
|---|---|
| `specs.py` | `StreamSpec`, `CoupledEnsembleSpec` — pure data classes (no pymdp dep) |
| `builders.py` | Deterministic Ising K-stream toy + helpers |
| `agents.py` | `pymdp.agent.Agent` adapter from `inferactively-pymdp==1.0.1` (the *only* file that imports pymdp / jax) |
| `inference.py` | Per-stream EFE / policy-posterior + λ-coupled joint + `FreeEnergyBundle` (VFE per stream, expected-EFE under posterior, joint / marginal entropy, total correlation, coupling term, action distribution) + `free_energy_curve` |
| `rollout.py` | `RolloutStep`, `Rollout`, `simulate_coupled_rollout` |
| `sweep.py` | `LambdaSweepResult`, `lambda_sweep`, `total_correlation_curve`, `marginal_trajectory` |
| `statistics.py` | Reduce a list of `FreeEnergyBundle` records to a flat `BundleSummary` and a `QuantileEnvelope` over multi-seed sweeps; emit `[[VAR:...]]`-ready scalars via `summary_to_var_dict`. |
| `logging_utils.py` | Append-only JSONL `RunLogger` for structured pymdp run records. Disabled with `PYMDP_RUN_LOG_DISABLED=1`. |
| `hyperparameters.py` | **Facade** — import hyperparameters from here only. Re-exports domain modules below and hosts `grid_count()` / `figure_hyperparameter_summary()`. |
| `hyperparameters_grids.py` | `FigureGrid`, analytical figure λ/utility grids, `FIGURE_GLOBAL_SEED`. |
| `hyperparameters_pymdp.py` | pymdp sweep/rollout/ensemble knobs, `MULTI_K_*`, `LONG_HORIZON_*`. |
| `hyperparameters_robustness.py` | `ROBUSTNESS_*`, `COUPLING_ABLATION_*`. |
| `hyperparameters_experiments.py` | Revertibility grids, pymdp Agent knobs, BTAI, adversarial harness. |
| `hyperparameters_sentinels.py` | Sentinel λ tuples, Monte Carlo witness, pymdp tolerances. |
| `long_horizon.py` | $T = 100$ coupled-rollout harness with habit-accumulation diagnostics and tail-window KL convergence checks. |
| `multi_k_experiments.py` | $K \in \{3, 4, 5\}$ ensemble sweeps for the multi-stream Ising case (the K > 2 generalization). |
| `revertibility.py` | $m$-projection revertibility witness: two independent code paths on $D_{\mathrm{KL}}(q\,\|\,\hat m(q)) = I(q)$. |
| `robustness.py` | **Facade** — import robustness helpers from here only. Re-exports compute, scenario dataclasses, and Wilson stats. |
| `robustness_types.py` | Frozen dataclasses for robustness rows and summaries. |
| `robustness_scenario_builders.py` | Scenario lists, `_spec_for_*`, `coupling_ablation_spec()`, `_product_of_marginals()`. |
| `robustness_scenarios.py` | Stable re-export path for types + builders (import here, not submodules). |
| `robustness_core.py` | Shared λ-loop (`rows_for_spec`) for one-axis, interaction, and ablation sweeps. |
| `robustness_one_axis.py` | `run_robustness_suite`, `summarize_robustness_rows`. |
| `robustness_interaction.py` | Two-axis interaction suite run/summarize. |
| `robustness_controls.py` | Coupling ablation + fixed-marginal null control. |
| `robustness_replicates.py` | Long-horizon replicate sidecars, diagnostics, Wilson pass-rate summaries. |
| `robustness_stats.py` | Wilson score intervals (single-purpose). |
| `robustness_emit.py` | CSV writers and figure metadata for the robustness pipeline. |
| `robustness_runner.py` | `run_robustness_pipeline` glue (compute → emit → plots). |
| `btai_baseline.py` | Branching-Time AIF MCTS-based comparison baseline (shipped §13 empirical harness). |
| `adversarial.py` | Bounded-norm adversarial-perturbation harness with analytical Lipschitz bound (§20 Q11). |
| `cross_references.py` | Prose ↔ equation ↔ Lean cross-reference registry; every public numerical witness mapped to its theorem / equation / section / Lean / Mathlib / dashboard-invariant target. Integrity gated by `tests/test_cross_references.py`. |

## Rules

* `pymdp` is **optional**; `uv sync --group sim` installs
  `inferactively-pymdp==1.0.1`, which provides the `pymdp` import/API.
  Tests skip via the `requires_pymdp` marker when missing.
* Anything that touches `pymdp.agent.Agent` lives in `agents.py`.  The
  rest of the subpackage operates on numpy and the analytical layer
  (`coupling.entangled_posterior`).
* Keep deterministic seeds in every helper that involves randomness.
* The coupled posterior layering is fixed: pymdp provides the
  *mean-field* layer (per-stream `q_pi^k`), the analytical layer adds
  the cross-stream `λ·J` / `γ·λ·K_c` factors on top.  Do not pipe pymdp's
  EFE back into `entangled_posterior` — `coupled_policy_posterior`
  already passes zero-G for that reason.
* Every grid / seed / rollout horizon used by figure scripts must be
  read from `hyperparameters.py`; never write `np.linspace(0, 6, 121)`
  inline.  The constants flow through the JSON mirror into manuscript
  prose via `[[VAR:...]]`.
* `FreeEnergyBundle` is frozen — fields are computed once in
  `free_energy_bundle(spec, obs, lam)` and consumed by the figure
  pipeline (`scripts/simulate_pymdp.py::figure_pymdp_free_energies`)
  and the test suite.  λ = 0 invariants (TC = 0, coupling = 0,
  H(q) = ΣH(q^k)) are asserted by `tests/test_simulation_free_energy.py`.
