# Empirical Simulation Suite: Bernoulli Validation, Coupling-Tax Envelope, Phase Diagram, and Spectral Structure

This section pairs every theoretical claim of [[SECREF:decomposition]]–[[SECREF:phase]] with a *concrete*
computational experiment.  All experiments are reproduced by the
companion code under
[`src/`](../src/) and [`scripts/`](../scripts/); the deterministic
artifacts they emit live under [`output/`](../output/).

The evidence boundary is deliberately narrow.  The simulations validate
finite, discrete, binary / Ising-style policy families implemented by
this repository; the theorem rows provide stock-Lean boundary or
witness contracts; and the generated CSV/JSON sidecars, PNG metadata,
manuscript variables, validators, and tests make each result
auditable.  They do not establish a biological, clinical, or alignment
process theory.  When later sections draw those analogies, their claim
strength is `hypothesis` unless the paragraph names a primary citation
or a generated artifact that directly supports it.

The suite is split across **two computational layers**:

1. **Closed-form / numeric core** — pure-NumPy code under
   [`src/lean/`](../src/lean/), tested with no mocks (≥ 95 % coverage;
   deterministic seeds throughout).  Realizes every quantity in the
   Lean boundary fragment ([[SECREF:lean_plan]]).  Drives every
   experiment in *this* section: closed-form Bernoulli validation,
   heterogeneous coupling-tax envelope, phase diagram, Schmidt
   spectrum, e-geodesic flow, and the multi-stream coupling graph.
2. **POMDP simulation harness** — the `pymdp` 1.0.1 layer under
   [`src/simulation/`](../src/simulation/) that *grounds* the coupled
   policy ensemble inside an actual partially-observed Markov
   decision process [@heins-2022], instantiated for the baseline
   $K = [[VAR:pymdp_ensemble_K]]$-stream Ising toy.  Architecture, the
   free-energy bundle of derived observables, and the validation /
   logging contract are documented separately across the three pymdp
   sub-sections [[SECREF:pymdp_harness]], [[SECREF:pymdp_free_energy]],
   and [[SECREF:pymdp_validation]].

Throughout, "λ-coupled" means the joint policy posterior obtained by
running the per-stream `pymdp` posteriors through
`coupling.entangled_posterior` with the manuscript's
$(J, K_c, \gamma, \lambda)$ parametrization — i.e. the exact
analytical layer of [[SECREF:lambda_deformation.entangled_posterior]] sits on top of pymdp's mean-field engine.

**How to read the figures.**  Following the scientific-visualization
discipline of making each figure answer a single question
[@rougier-2014], each plot is meant to be an auditable result rather
than decoration.  Curves show monotonicity, saturation, or identity
residuals; heatmaps show where the same scalar changes across a
controlled grid; joint heatmaps show the posterior, its marginals, and
the residual from independence in one view.  Captions name the
generated artifact, the invariant it witnesses, and one uncertainty
semantics class: deterministic grid, canonical fixed seed, replicate
envelope, confidence interval, or analytical schematic.  The PNG
metadata records the same source script, generating function,
hyperparameter snapshot, uncertainty semantics, and compact
plotted-data statistics.  Thus a figure can be checked in three
passes: read the caption, inspect the sidecar CSV or JSON, and read
the PNG `project.*` metadata.

**Evidence ledger.**  The empirical suite is organized so that each
headline claim has a directly inspectable artifact and a corresponding
test gate:

| Claim checked | Primary artifact | Gate that catches drift |
|---|---|---|
| Closed-form Ising mutual information equals empirical total correlation | [`output/data/parameter_sweep.csv`](../output/data/parameter_sweep.csv) | `tests/test_bernoulli_toy.py`, `tests/test_invariants_and_dashboard.py` |
| The coupling-tax curve follows the $O(\lambda^2)$ envelope | [`output/figures/coupling_tax_quadratic.png`](../output/figures/coupling_tax_quadratic.png) + `coupling_tax_curvature_C` | `tests/test_heterogeneous_ensemble.py`, `tests/test_witness_theorems.py` |
| Schmidt rank / entropy record the departure from mean-field | [`output/data/ising_archetypes.csv`](../output/data/ising_archetypes.csv) | `tests/test_spectral.py`, `tests/test_multi_k_experiments.py` |
| pymdp-grounded coupling starts as an outer product and then gains total correlation | [`output/simulations/pymdp_lambda_sweep.csv`](../output/simulations/pymdp_lambda_sweep.csv) | `tests/test_simulation_pymdp.py`, `tests/test_simulation_free_energy.py` |
| Long-horizon rollout reaches a steady tail and accumulates habit mass | [`output/simulations/pymdp_long_horizon.csv`](../output/simulations/pymdp_long_horizon.csv) | `tests/test_long_horizon.py`, `tests/test_tail_window_kl.py` |
| m-projection revertibility realizes $I(q)=D_{\mathrm{KL}}(q\|\hat m(q))$ | [`output/simulations/pymdp_revertibility.csv`](../output/simulations/pymdp_revertibility.csv) | `tests/test_revertibility.py`, `tests/test_witness_theorems.py` |
| One-axis robustness preserves the λ = 0 anchor while exposing context / precision / preference / coupling sensitivity | [`output/simulations/pymdp_robustness.csv`](../output/simulations/pymdp_robustness.csv) + [`output/data/robustness_summary.json`](../output/data/robustness_summary.json) | `tests/test_robustness.py`, `tests/test_robustness_plots.py` |
| Coupling ablations and fixed-marginal null controls separate cross-stream dependence from marginal drift | [`output/simulations/pymdp_coupling_ablation.csv`](../output/simulations/pymdp_coupling_ablation.csv) + [`output/simulations/pymdp_marginal_null_control.csv`](../output/simulations/pymdp_marginal_null_control.csv) | `tests/test_robustness.py`, `tests/test_robustness_plots.py` |
| Long-horizon replicate seeds and threshold probes expose stationarity sensitivity rather than tuning one headline cutoff | [`output/simulations/pymdp_long_horizon_replicates.csv`](../output/simulations/pymdp_long_horizon_replicates.csv) + [`output/simulations/pymdp_long_horizon_threshold_sensitivity.csv`](../output/simulations/pymdp_long_horizon_threshold_sensitivity.csv) | `tests/test_robustness.py`, `tests/test_metadata_pure.py` |
| BTAI baseline runs end-to-end on the K=2 task and emits the three tracked observables across the MCTS budget grid | [`output/data/btai_baseline.json`](../output/data/btai_baseline.json) | `tests/test_btai_baseline.py`, `tests/test_simulate_btai_adversarial.py` |
| Adversarial (ε,λ)-grid measures KL drift against the first-order Lipschitz bound across three adversary classes | [`output/data/adversarial_sweep.json`](../output/data/adversarial_sweep.json) | `tests/test_adversarial.py`, `tests/test_simulate_btai_adversarial.py` |

## Two-stream Bernoulli (K=2) closed-form validation

- Sweep $\lambda \in [[[VAR:param_sweep_lambda_min:g]],
  [[VAR:param_sweep_lambda_max:g]]]$ on a
  $[[VAR:param_sweep_grid_points]]$-point grid; at each $\lambda$
  compute the closed-form mutual information [[EQREF:ising_mi_closed_form]]
  and the empirical total correlation of the Ising joint posterior,
  and confirm they agree to
  $[[VAR:param_sweep_agreement_tolerance:.0e]]$.  Concrete values:
  $I(0.5) = [[VAR:ising_mi_at_lam_05:.4f]]$,
  $I(1) = [[VAR:ising_mi_at_lam_1:.4f]]$,
  $I(2) = [[VAR:ising_mi_at_lam_2:.4f]]$ nats; the saturation is
  $I(\infty) = [[VAR:ising_mi_saturation:.4f]] \approx \log 2$.
- Sweep $\Delta_{\mathrm{util}}$ and plot
  $\lambda^\star = 2 \cdot \operatorname{arctanh}(\Delta_{\mathrm{util}})$
  (see [[EQREF:optimal_lambda]]); for $\Delta_{\mathrm{util}} = 0.5$
  the optimal coupling is $\lambda^\star \approx [[VAR:lambda_star_delta_05:.4f]]$,
  for $\Delta_{\mathrm{util}} = 0.9$ it is
  $\lambda^\star \approx [[VAR:lambda_star_delta_09:.4f]]$.
- Verify the existence and convexity claims of [[SECREF:decomposition]] by numerical
  fixed-point iteration on the free-energy curve.

**Reproduce.**

```bash
uv run python scripts/parameter_sweep.py        # closed-form grid CSV
uv run python scripts/manuscript_variables.py   # JSON of in-text values
```

The grid count, λ range, and agreement tolerance are sourced from
[`src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py)
(`PARAMETER_SWEEP_LAMBDAS`,
`PARAMETER_SWEEP_AGREEMENT_TOLERANCE`); the
$[[VAR:param_sweep_grid_points]]$-row CSV at
[`output/data/parameter_sweep.csv`](../output/data/parameter_sweep.csv)
is the artifact.

[[FIG:ising_mi_curve]]

[[FIG:free_energy_curve]]

[[FIG:optimal_lambda]]

## Heterogeneous VFE / EFE coupling-tax bound

This block exercises [[THMREF:thm_8_1]] (coupling-tax bound) numerically.

- Assign one stream `InferenceMode.VFE`, one `InferenceMode.EFE`.
- Sweep $\lambda \in [[[VAR:coupling_tax_lambda_min:g]],
  [[VAR:coupling_tax_lambda_max:g]]]$ on a
  $[[VAR:coupling_tax_grid_points]]$-point grid.
- Compute the *coupling tax* $D_{\mathrm{KL}}(q_{\mathrm{full}} \,\|\,
  q_{\mathrm{pinned}})$, fit the small-$\lambda$ slope at the probe
  $\lambda_{\mathrm{probe}} = [[VAR:coupling_tax_probe_lambda:g]]$,
  and confirm the $O(\lambda^2)$ envelope predicted by
  [[EQREF:coupling_tax_bound]].  The empirical curvature constant
  is $C \approx [[VAR:coupling_tax_curvature_C:.4f]]$.

[[FIG:coupling_tax_quadratic]]

## Phase Structure of the $K=2$ Ising Toy: Disordered, Mixed, and Frozen Regimes

- Vary $\lambda$ across the phase-band thresholds
  $(\lambda_c^{(1)}, \lambda_c^{(2)}) = ([[VAR:phase_lambda_c1:g]], [[VAR:phase_lambda_c2:g]])$
  defined in [[SECREF:phase]], holding $J$ and $K_c$ fixed.
- Visualize the disordered / mixed / frozen regimes as a 1-D phase band.

[[FIG:phase_diagram]]

The 2-D free-energy landscape $F(\lambda, \Delta_{\mathrm{util}})$ is sampled on a
$[[VAR:phase_landscape_lambda_points]] \times [[VAR:phase_landscape_utility_points]]$
linspace grid over
$[[[VAR:phase_landscape_lambda_min:g]], [[VAR:phase_landscape_lambda_max:g]]]
\times
[[[VAR:phase_landscape_utility_min:g]], [[VAR:phase_landscape_utility_max:g]]]$
(`simulation.hyperparameters.PHASE_LANDSCAPE_LAMBDAS`,
`PHASE_LANDSCAPE_UTILITIES`); each cell is one call to
`lean.bernoulli_toy.ising_free_energy_curve`.  The U-shaped low-utility band
(cf. [[SECREF:phase]]) gives way to monotone-decreasing curves at high utility, and the
locus of $\lambda^\star$ is the color minimum at each utility column
(cf. [[EQREF:optimal_lambda]]).

[[FIG:phase_landscape]]

## Spectral structure (Schmidt rank, archetypes)

- Verify [[THMREF:prop_7_1]] numerically (rank-1 iff mean-field) by sweeping
  $\lambda$.  At $\lambda = 0$ the rank is
  $r = [[VAR:ising_schmidt_rank_at_lam_0]]$; at $\lambda = 1$ it
  jumps to $r = [[VAR:ising_schmidt_rank_at_lam_1]]$.  The smooth
  analog, the entanglement entropy, has
  $S_E(0) = [[VAR:ising_S_E_at_lam_0:.4f]]$,
  $S_E(1) = [[VAR:ising_S_E_at_lam_1:.4f]]$,
  $S_E(3) = [[VAR:ising_S_E_at_lam_3:.4f]]$.
- Decompose $q_\lambda$ at $\lambda = 3$ into Schmidt archetypes and
  visualize weights + pairwise overlaps.
- Sweep across stream counts $K \in \{[[VAR:tt_rank_stream_counts]]\}$ and tabulate the
  tensor-train rank profile: the configured entries give
  $[[VAR:tt_ranks_K2]]$, $[[VAR:tt_ranks_K3]]$,
  $[[VAR:tt_ranks_K4]]$, and $[[VAR:tt_ranks_K5]]$.

[[FIG:schmidt_rank]]

[[FIG:schmidt_entropy_surface]]

[[FIG:joint_heatmap_lambda2]]

[[FIG:archetype_dendrogram]]

[[FIG:tensor_train_rank_surface]]

## Information-geometric structure (e-geodesic)

- For each policy $\pi$, compute the unnormalized log-weight
  $\log q_\lambda(\pi) + \log Z(\lambda)$ on a
  $[[VAR:log_weight_flow_grid_points]]$-point sweep across
  $\lambda \in [[[VAR:log_weight_flow_lambda_min:g]],
  [[VAR:log_weight_flow_lambda_max:g]]]$ (see [[EQREF:e_geodesic]]).
- Plot one line per policy.

[[FIG:log_weight_flow]]

## Multi-stream coupling graph

For the largest configured multi-stream Ising-style coupling, render the coupling potential $J$
as a graph over streams (edge weight = mean $|J|$ across all slot
pairs), illustrating the homogeneous all-to-all structure of the
symmetric coupling.

[[FIG:coupling_graph]]

## $K > 2$ ensembles

The harness exercises the framework on the configured multi-stream set
$K \in \{[[VAR:multi_k_values_list]]\}$
multi-stream Ising ensembles (`scripts/simulate_multi_k.py`,
one `output/simulations/pymdp_K*_sweep.csv` file per configured $K$). At
$\lambda = [[VAR:multi_k_sentinel_lambda:g]]$ the
total correlation is
$I(q_{[[VAR:multi_k_sentinel_lambda:g]]}) \approx [[VAR:multi_information_K3_lambda_2:.4f]]$
nats for the first configured multi-K ensemble and
$I(q_{[[VAR:multi_k_sentinel_lambda:g]]}) \approx [[VAR:multi_information_K4_lambda_2:.4f]]$
nats for the second; the largest configured ensemble reaches
$I(q_{[[VAR:multi_k_sentinel_lambda:g]]}) \approx [[VAR:multi_information_K5_lambda_2:.4f]]$
nats.  Together these rows are the empirical witness that the entanglement
decomposition theorem ([[THMREF:thm_4_1]]) carries over from the K=2
slice to higher stream counts.  Aligned-corner mass and the tensor-
train rank profile at the sweep maximum are recorded in
[`output/data/multi_k_summary.json`](../output/data/multi_k_summary.json):
the first configured multi-K ensemble reaches aligned mass
$[[VAR:multi_k_K3_aligned_mass_at_lambda_max:.4f]]$ at
$\lambda = [[VAR:multi_k_K3_lambda_max:g]]$ with maximum bond
dimension $[[VAR:multi_k_K3_tt_rank_max_at_lambda_max]]$; the second
ensemble reaches aligned mass
$[[VAR:multi_k_K4_aligned_mass_at_lambda_max:.4f]]$ at
$\lambda = [[VAR:multi_k_K4_lambda_max:g]]$ with maximum bond
dimension $[[VAR:multi_k_K4_tt_rank_max_at_lambda_max]]$; and the
largest configured ensemble reaches aligned mass
$[[VAR:multi_k_K5_aligned_mass_at_lambda_max:.4f]]$ with maximum bond
dimension $[[VAR:multi_k_K5_tt_rank_max_at_lambda_max]]$.

[[FIG:multi_k_total_correlation]]

[[FIG:multi_k_aligned_mass]]

[[FIG:multi_k_tt_rank_profile]]

## Long-horizon rollouts and trajectory stationarity

A deterministic $T = [[VAR:long_horizon_steps]]$-step coupled rollout
at $\lambda = [[VAR:long_horizon_lambda:g]]$ and seed
$[[VAR:long_horizon_seed]]$
(`scripts/simulate_long_horizon.py`,
`output/simulations/pymdp_long_horizon.csv`) provides the long-horizon
counterpart to the $T = [[VAR:pymdp_rollout_steps]]$ rollout in
[[SECREF:pymdp_harness]].  The steady-state KL is computed against
the trailing-window mean
$\bar q^k_{\mathrm{tail}}$, not against the immediately preceding
step: for each stream and
$t \ge T - [[VAR:long_horizon_tail_window]]$ we record
$D_{\mathrm{KL}}(q_t^k \| \bar q^k_{\mathrm{tail}})$, then report
first-tail, mean-tail, and max-tail summaries.  The strict max-tail
bound is
$[[VAR:long_horizon_tail_kl_window_max:.4f]]$ nats, under the
steady-state tolerance
$[[VAR:long_horizon_steady_state_tol:g]]$; adjacent-step KL is also
stored separately, with max
$[[VAR:long_horizon_adjacent_kl_max:.4f]]$ nats, so the two
semantics are not conflated.  The per-stream marginal trajectory
reaches a stable steady state, summarised by
$[[VAR:long_horizon_habit_accumulation:.4f]]$.  **Honest scope (no
over-claim):** the rollout agents perform **no parameter learning**
(the `A`/`B`/`D` matrices are static); this quantity is therefore a
*trajectory-stationarity* / steady-state diagnostic — the coupled
marginals *converge and stay put* — and is **not** evidence of habit
*formation* (which would require learning dynamics the harness does not
run).  It is consistent with [[SECREF:heterogeneous.habit]]'s
prediction but is a stationarity check, not an independent
demonstration of habit accumulation; a divergent-rollout negative
control (a rollout that should *fail* stationarity at the same
tolerance) is the open discriminating hardening.  Total correlation traces from initial
$[[VAR:long_horizon_tc_initial:.4f]]$ to final
$[[VAR:long_horizon_tc_final:.4f]]$ nats with mean
$[[VAR:long_horizon_tc_mean:.4f]]$ across the
$T = [[VAR:long_horizon_steps]]$ trajectory.

[[FIG:long_horizon_marginals]]

[[FIG:long_horizon_steady_state]]

## $m$-projection revertibility witness

The revertibility test (`scripts/simulate_revertibility.py`,
`output/simulations/pymdp_revertibility.csv`) verifies the
$m$-projection identity of [[THMREF:prop_6_2]] and [[THMREF:prop_6_3]]
numerically: for every $\lambda$ in
$[[VAR:revertibility_num_lambdas]]$-point sweep, the entangled
posterior is marginalized back to its mean-field $m$-projection and
the residual $I(q_\lambda) - D_{\mathrm{KL}}(q_\lambda\,\|\,\hat m(q_\lambda))$
is computed.  Across the full sweep the maximum $\mathrm{KL}$ residual
is $[[VAR:revertibility_max_kl_residual:.2e]]$ and the maximum
marginal-difference is $[[VAR:revertibility_max_marginal_diff:.2e]]$ —
i.e. the Pythagorean / KL-equals-multi-information identity
$I(q) = D_{\mathrm{KL}}(q\,\|\,\hat m(q))$ holds to floating-point
tolerance ($\le [[VAR:revertibility_max_kl_residual:.2e]]$ maximum
residual).  The summary identity flags
`revertibility_all_kl_identity_holds` and
`revertibility_all_marginals_match` both evaluate to **true**, closing
the analytical revertibility loop opened in [[SECREF:geometry]].

[[FIG:revertibility_witness]]

## Robustness and ablation stress tests

The main pymdp figures answer the cleanest canonical question: what
happens when the configured binary observation context, precision,
preference strength, and aligned Ising coupling are held fixed while
$\lambda$ varies?  The stress-test suite asks the reviewer-facing
follow-up: which pieces are invariants of the construction, and which
are contingent on that canonical slice?

`scripts/simulate_robustness.py` runs one-axis-at-a-time perturbations
rather than a Cartesian explosion.  It sweeps the
[[VAR:robustness_observation_context_count]] observation contexts, the
[[VAR:robustness_gamma_count]] precision values, the
[[VAR:robustness_preference_strength_count]] preference-strength
values, and the [[VAR:robustness_coupling_scale_count]]
coupling-scale values over the configured
[[VAR:robustness_sweep_grid_points]]-point robustness grid.  The result
is [[VAR:robustness_row_count:.0f]] rows across
[[VAR:robustness_scenario_count:.0f]] scenarios.  The invariant that
matters most is structural: $\lambda = 0$ remains the mean-field anchor
and the decomposition residual remains below
[[VAR:pymdp_decomposition_residual_tolerance:.0e]]
(observed maximum
[[VAR:robustness_decomposition_residual_max:.2e]]).  The null coupling
row is the negative control: its maximum total correlation is
[[VAR:robustness_null_coupling_tc_max:.2e]], so the positive envelopes
in the other rows are not an artifact of the plotting or posterior
normalization code.

[[FIG:robustness_tc_envelopes]]

[[FIG:robustness_half_saturation]]

[[FIG:robustness_decomposition_residuals]]

The ablation branch then changes the *role* of the coupling potential
itself.  Aligned coupling, null coupling, anti-aligned coupling, and a
heterogeneous small-tax $K_c$ matrix share the same $\lambda$ grid.
The checks that persist are the structural ones: the $\lambda = 0$
anchor is invariant, null coupling stays flat, non-null sign or role
changes can still create dependence, and the decomposition residual
remains closed
([[VAR:coupling_ablation_decomposition_residual_max:.2e]] maximum).
What changes is the archetypal allocation: the aligned-mass shift
across ablation variants at the sweep endpoint is
[[VAR:coupling_ablation_aligned_mass_shift:.4f]], which is a concrete
way to see that the stress suite is not merely re-plotting the same
posterior under four names.

[[FIG:coupling_ablation_summary]]

The fixed-marginal null control then asks a sharper diagnostic
question: if we preserve each stream's posterior but replace the joint
with the product of those marginals, does the dependence signal
disappear?  It does.  Across the same robustness $\lambda$ grid, the
control's maximum total correlation is
[[VAR:robustness_null_control_max_tc:.2e]], while the maximum amount of
total correlation removed from the entangled joint is
[[VAR:robustness_null_control_tc_removed_max:.4f]].  This is the
negative-control counterpart to the positive coupling sweeps: the
effect is carried by cross-stream joint structure, not by a hidden
change in either stream's marginal posterior.

[[FIG:marginal_null_control_summary]]

The appendix interaction branch adds a deliberately narrow two-axis
suite rather than a full Cartesian grid.  It crosses observation
context with coupling scale, precision $\gamma$ with preference
strength, and coupling variant with coupling scale — the three
interactions most likely to change a reviewer-facing interpretation of
the canonical sweep.  Across
[[VAR:interaction_robustness_scenario_count:.0f]] targeted scenarios
and [[VAR:interaction_robustness_row_count:.0f]] rows, the worst
decomposition residual is
[[VAR:interaction_robustness_decomposition_residual_max:.2e]], and the
null-variant flatline remains bounded by
[[VAR:interaction_robustness_null_variant_tc_max:.2e]].  These results
are reported as supporting stress evidence, not as new theorem claims.

[[FIG:interaction_robustness_summary]]

Finally, the long-horizon robustness sidecar leaves the canonical
fixed-seed rollout untouched and adds the configured replicate seeds
$\{[[VAR:long_horizon_replicate_seeds_list]]\}$.  The median/IQR
envelope reports trajectory sensitivity without changing the main
deterministic figure.  Across those seeds, the habit-accumulation pass
rate is [[VAR:long_horizon_replicate_habit_pass_rate:.2f]]
(Wilson 95% interval
[[[VAR:long_horizon_replicate_habit_pass_rate_ci_low:.2f]],
[[VAR:long_horizon_replicate_habit_pass_rate_ci_high:.2f]]]), the final
total-correlation mean is
[[VAR:long_horizon_replicate_tc_final_mean:.4f]], and the maximum
tail-window KL is
[[VAR:long_horizon_replicate_tail_kl_window_max:.4f]].  The companion
seed-diagnostics sidecar then records the per-seed failure mode and
threshold sensitivity over
$\{[[VAR:long_horizon_diagnostic_thresholds_list]]\}$, making the
observed pass rate a transparent sensitivity result rather than a
tuned headline.  The dedicated threshold-sensitivity figure reports
the full pass-rate range
([[VAR:long_horizon_replicate_threshold_pass_rate_min:.2f]] to
[[VAR:long_horizon_replicate_threshold_pass_rate_max:.2f]]) across
the configured probes, so the canonical threshold is visible as one
registered choice among the diagnostics rather than an implicit
post-hoc cutoff.

[[FIG:long_horizon_replicate_envelope]]

[[FIG:long_horizon_seed_diagnostics]]

[[FIG:long_horizon_threshold_sensitivity]]

## Software and numerical stack

The reproducibility chain rests on `inferactively-pymdp==1.0.1`, which
provides the pymdp import/API [@heins-2022] with its JAX backend
[@bradbury-2018] for per-stream POMDP inference, NumPy
[@harris-2020] and SciPy [@virtanen-2020] for the dense joint-policy
tensors and spectral decompositions of the analytical layer,
matplotlib [@hunter-2007] (`Agg` backend) for every figure, and
pytest with a no-mocks policy for the test-infrastructure gate; Lean 4
[@demoura-ullrich-2021] hosts the type-checked boundary fragment under
`lean/ActinfPolicyEntanglement/`, while Mathlib [@mathlib-2020] is
reserved for the separate optional `lean/MathlibProofs/` package.  All
pins are resolved by `uv` through [`pyproject.toml`](../pyproject.toml);
the dependency list is deliberately minimal — losing JAX disables the
pymdp grounding, losing Lean disables the formal-verification track, losing NumPy
makes the analytical and empirical decompositions disagree on the
seventh significant figure.  Detailed version pins, optional-group
boundaries (`sim`, `viz`), and resolution notes are listed in
[`docs/guides/build_run.md`](../docs/guides/build_run.md).

Three reference tables collect the load-bearing per-module / per-statistic / per-JSONL-field metadata in [[SECREF:app.reference_tables]]: Lean module inventory ([[SECREF:app.lean_modules]]), pymdp bundle statistics ([[SECREF:app.bundle_stats]]), and JSONL run-log schema ([[SECREF:app.jsonl_schema]]).

## Head-to-head BTAI baseline and adversarial-perturbation harnesses

Two comparison harnesses originally scoped as follow-on work are now
implemented, unit-tested, and run as pipeline stages emitting auditable
sidecars.

**Branching-Time AIF (BTAI) baseline** [@champion-2022]
(`scripts/simulate_btai.py` → `output/data/btai_baseline.json`;
`src/simulation/btai_baseline.py`; `tests/test_btai_baseline.py`).  A
Monte-Carlo-tree-search BTAI agent is driven by the project's real
[[VAR:pymdp_distribution_version]] per-stream expected free energy and sweeps the
configured budget grid
$B_{\mathrm{MCTS}} \in \{[[VAR:btai_mcts_min_budget:.0f]], \dots, [[VAR:btai_mcts_max_budget:.0f]]\}$
([[VAR:btai_num_budgets:.0f]] budgets), recording the per-step joint
policy posterior, its total correlation, and the KL of the MCTS
visitation posterior against the closed-form $K=2$ Bernoulli reference
at $\lambda = [[VAR:btai_reference_lambda:g]]$.  **Honest scope (no
over-claim):** UCB-MCTS estimates the lowest-EFE *joint action* rather
than the soft policy posterior, so the visitation posterior concentrates
(total correlation $\approx [[VAR:btai_total_correlation_at_max_budget:.4f]]$
nats at the largest budget) and the measured sample-complexity exponent
of its KL against the soft reference is
$[[VAR:btai_sample_complexity_exponent:.3f]]$.  The worked run therefore
*ships and exercises* the three tracked observables; the full
compute-matched hypothesis test of [[SECREF:discussion]] (whether BTAI
attains the exact posterior as $B_{\mathrm{MCTS}} \to \infty$ at a
unit sample-complexity exponent) remains author-led analysis, not a
claim made here.

[[FIG:btai_baseline]]

**Adversarial-perturbation sweep** ([[SECREF:open_questions]] Q11;
`scripts/simulate_adversarial.py` → `output/data/adversarial_sweep.json`;
`src/simulation/adversarial.py`; `tests/test_adversarial.py`).  The
configured $(\varepsilon, \lambda)$-grid runs all three adversary
classes (analytical worst-case rank-one, uniform-random, and sparse
single-cell) over [[VAR:adversarial_num_scenarios:.0f]] scenarios
([[VAR:adversarial_epsilon_grid_points:.0f]] $\varepsilon$ values $\times$
[[VAR:adversarial_lambda_grid_points:.0f]] $\lambda$ values $\times$ 3
classes) on the $K=2$ Ising task, comparing the measured KL drift
$D_{\mathrm{KL}}(q_\lambda \,\|\, q_\lambda^{J+\Delta J})$ against the
first-order Lipschitz bound
$\lambda\,\varepsilon\,\operatorname{Var}_{q_\lambda}(J)^{1/2}$.  The
first-order bound holds for a fraction
$[[VAR:adversarial_bound_holds_fraction:.3f]]$ of scenarios (empirical
Lipschitz constant $[[VAR:adversarial_empirical_lipschitz:.3f]]$); it is
loose at small $\varepsilon$ and is exceeded (worst ratio
$[[VAR:adversarial_max_bound_ratio:.2f]]$) in the large-$\varepsilon$
regime where the linearization saturates — a regime the sidecar
surfaces rather than absorbs.

[[FIG:adversarial_sweep]]

## Anchored figure index

The empirical suite produces a family of cross-referenced figures
distributed across the closed-form ([[SECREF:examples]]), geometry
([[SECREF:geometry]]), spectral ([[SECREF:spectral]]), heterogeneous
([[SECREF:heterogeneous]]), phase ([[SECREF:phase]]), and
comparative-statics ([[SECREF:comparative]]) sections, as well as
the pymdp harness ([[SECREF:pymdp_harness]]), pymdp free-energy
([[SECREF:pymdp_free_energy]]), and validation
([[SECREF:pymdp_validation]]) sections downstream.  Anchor index for
the suite's figures that are generated by this section's analyses but
cross-referenced from other body sections:
[[FIGREF:archetype_dendrogram]] (Schmidt archetype dendrogram, also cross-referenced from [[SECREF:spectral.archetypes]]),
[[FIGREF:coupling_tax_quadratic]] ($O(\lambda^2)$ coupling-tax envelope, also cross-referenced from [[SECREF:heterogeneous]]),
[[FIGREF:joint_heatmap_lambda2]] ($K=2$ joint heatmap with marginals, also cross-referenced from [[SECREF:examples.bernoulli]]),
[[FIGREF:log_weight_flow]] (log-weight $e$-geodesic flow, also cross-referenced from [[SECREF:geometry]]),
[[FIGREF:long_horizon_steady_state]] (long-horizon steady-state KL convergence, also cross-referenced from [[SECREF:heterogeneous.habit]]),
[[FIGREF:multi_k_aligned_mass]] (aligned mass concentration as $K$ varies, also cross-referenced from [[SECREF:phase]]),
[[FIGREF:optimal_lambda]] (alignment-inversion $\lambda^\star(\Delta_{\mathrm{align}})$, also cross-referenced from [[SECREF:examples.bernoulli]]),
[[FIGREF:phase_diagram]] (1-D phase diagram, also cross-referenced from [[SECREF:phase]]),
[[FIGREF:schmidt_rank]] (Schmidt rank vs $\lambda$, also cross-referenced from [[SECREF:spectral.bipartite]]), and
[[FIGREF:tensor_train_rank_surface]] (tensor-train rank surface, also cross-referenced from [[SECREF:spectral.multistream_tt]]).
Each figure is also independently anchored at its primary referencing
subsection; this paragraph exists so the empirical-suite section is
the *single* place a reader can locate every empirical figure
regardless of which downstream section motivated its generation.

---
