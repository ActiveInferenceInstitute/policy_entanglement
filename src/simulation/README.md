# `src/simulation/`

`inferactively-pymdp==1.0.1`-backed POMDP simulation harness for
coupled-policy active-inference ensembles, using the `pymdp` import/API.
Companion to the analytical mirrors in [`../lean/`](../lean/).  Public
symbols are re-exported from `simulation/__init__.py`.

See parent docs: [`../AGENTS.md`](../AGENTS.md), [`../README.md`](../README.md).
Subpackage rules and pymdp guard-rails: [`AGENTS.md`](AGENTS.md).

## Module map

| Module | Role | Exports |
|---|---|---|
| [`specs.py`](specs.py) | Pure data classes (no pymdp dep) | `StreamSpec`, `CoupledEnsembleSpec` |
| [`builders.py`](builders.py) | Deterministic Ising K-stream toys + helpers | `two_state_identity_likelihood`, `two_action_swap_transitions`, `make_bernoulli_stream`, `ising_coupling_tensor`, `make_ising_ensemble` |
| [`agents.py`](agents.py) | `pymdp.agent.Agent` adapter from `inferactively-pymdp==1.0.1` — **the only file that imports `pymdp` / `jax`** | `pymdp_available`, `build_pymdp_agent`, `build_pymdp_agents`, `PYMDP_INSTALL_HINT` |
| [`inference.py`](inference.py) | Per-stream EFE / policy-posterior, λ-coupled joint, free-energy bundle | `per_stream_efe`, `per_stream_policy_posterior`, `coupled_policy_posterior`, `FreeEnergyBundle`, `variational_free_energy`, `expected_free_energy_under_posterior`, `coupling_energy`, `free_energy_bundle`, `free_energy_curve` |
| [`rollout.py`](rollout.py) | Coupled rollouts under a fixed seed | `RolloutStep`, `Rollout`, `simulate_coupled_rollout` |
| [`sweep.py`](sweep.py) | λ-sweep across the coupled posterior | `LambdaSweepResult`, `lambda_sweep`, `total_correlation_curve`, `marginal_trajectory` |
| [`statistics.py`](statistics.py) | Reduce a list of `FreeEnergyBundle` to scalars + quantile envelopes | `BundleSummary`, `QuantileEnvelope`, `pymdp_summary_statistics`, `summary_to_var_dict`, `quantile_envelope_over_sweeps`, `is_monotone_nondecreasing`, `total_correlation_saturation_index` |
| [`logging_utils.py`](logging_utils.py) | Append-only JSONL run logger (the only module here that touches disk) | `RunLogger`, `TimedRecord`, `default_logger` |
| [`hyperparameters.py`](hyperparameters.py) | **Single source of truth** for every grid / seed / sentinel / horizon | `FigureGrid`, `PARAMETER_SWEEP_LAMBDAS`, `COUPLING_TAX_LAMBDAS`, `PHASE_DIAGRAM_LAMBDAS`, `OPTIMAL_LAMBDA_DELTAS`, `SCHMIDT_RANK_LAMBDAS`, `PHASE_LANDSCAPE_LAMBDAS`, `PHASE_LANDSCAPE_UTILITIES`, `LOG_WEIGHT_FLOW_LAMBDAS`, `KL_GEODESIC_LAMBDAS`, `LAMBDA_STAR_UTILITIES`, `LAMBDA_STAR_GAMMAS`, `PYMDP_SWEEP_LAMBDAS`, `grid_count`, `figure_hyperparameter_summary` |
| [`long_horizon.py`](long_horizon.py) | $T=100$ coupled-rollout harness with habit-accumulation + tail-window KL diagnostics | `LongHorizonResult`, `long_horizon_rollout`, `long_horizon_summary`, `tail_window_kl`, `tail_window_kl_statistics`, `trajectory_tc_nonneg`, `trajectory_tc_finite`, `recompute_total_correlations`, `trajectory_marginals_are_pmfs`, `tc_trajectory_recomputable` |
| [`multi_k_experiments.py`](multi_k_experiments.py) | $K \in \{3, 4, 5\}$ ensemble sweeps for the multi-stream Ising case | `MultiKResult`, `run_multi_k_sweep`, `multi_k_joint_snapshot`, `multi_k_summary` |
| [`revertibility.py`](revertibility.py) | $m$-projection revertibility witness: two-route consistency on $D_{\mathrm{KL}}(q\,\|\,\hat m(q)) = I(q)$ | `RevertibilityRecord`, `m_projection_witness`, `revertibility_test`, `revertibility_summary`, `revertibility_kl_equals_multiinformation_witness` |
| [`robustness.py`](robustness.py) | One-axis / two-axis / coupling-ablation / marginal-null-control / replicate-seed robustness sidecars | `RobustnessScenario`, `RobustnessRow`, `RobustnessScenarioSummary`, `InteractionRobustnessScenario`, `InteractionRobustnessRow`, `InteractionRobustnessSummary`, `CouplingAblationRow`, `MarginalNullControlRow`, `LongHorizonReplicateRecord`, `LongHorizonSeedDiagnostic`, `LongHorizonThresholdSensitivityRow`, `run_robustness_suite`, `summarize_robustness_rows`, `run_interaction_robustness_suite`, `summarize_interaction_robustness_rows`, `run_coupling_ablation`, `run_marginal_null_control`, `robustness_scenarios`, `interaction_robustness_scenarios`, `wilson_score_interval` |
| [`btai_baseline.py`](btai_baseline.py) | Branching-Time AIF MCTS-based comparison baseline (shipped §13 empirical harness) | `BTAIScenario`, `BTAIObservable`, `BTAIRunResult`, `BTAITreeNode`, `run_btai_scenario`, `joint_marginals`, `total_correlation`, `ucb_score`, `kl_against_reference`, `sample_complexity_exponent`, `default_btai_scenarios`, `default_mcts_budgets`, `pymdp_grounded_efe_fn` |
| [`adversarial.py`](adversarial.py) | Bounded-norm adversarial-perturbation harness with analytical Lipschitz bound (§20 Q11) | `AdversarialScenario`, `AdversarialObservable`, `analytical_lipschitz_bound`, `coupling_covariance`, `variance_under_q`, `rank_one_adversary`, `uniform_random_adversary`, `sparse_single_adversary`, `build_adversary`, `perturbed_posterior`, `measure_drift`, `run_full_sweep`, `empirical_lipschitz_constant`, `kl_divergence`, `default_epsilon_grid`, `default_lambda_grid`, `default_adversarial_scenarios` |
| [`cross_references.py`](cross_references.py) | Prose ↔ equation ↔ Lean cross-reference registry (every public numerical witness mapped to its theorem / equation / section / Lean / Mathlib / dashboard-invariant target) | `CrossReference`, `CROSS_REFERENCES`, `cross_reference_for`, `as_metadata_dict`, `to_markdown_table` |

## Conventions

* `pymdp` is **optional**; `uv sync --group sim` installs
  `inferactively-pymdp==1.0.1`, which provides the `pymdp` import/API.
  Tests skip via the `requires_pymdp` marker when missing.
* The coupled-posterior layering is fixed: pymdp owns the per-stream
  mean-field policy posterior; the analytical layer in
  `lean/coupling.py` adds the cross-stream `λ·J` / `γ·λ·K_c` factors.
  `coupled_policy_posterior` already passes zero-G to
  `entangled_posterior` so pymdp's EFE is not double-counted.
* `FreeEnergyBundle` is frozen and computed once per `(spec, obs, λ)`;
  every figure / statistic consumer reuses the same record.
* `RunLogger` is gated by `PYMDP_RUN_LOG_DISABLED=1` for headless runs.
