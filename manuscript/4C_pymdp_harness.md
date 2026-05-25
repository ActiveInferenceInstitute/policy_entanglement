# pymdp 1.0.1 POMDP Harness: Architecture, Lambda Sweep, and Deterministic Rollout

This sub-section documents the **architecture** of the pymdp grounding
layer — how the manuscript's analytical λ-coupling sits *on top of* a
real `pymdp.agent.Agent` and what each piece contributes.  Every
POMDP symbol below ($A$, $B$, $C$, $D$, $\gamma$, $T$, $q_\pi^k$) is
cataloged in the unified notation glossary ([[SECREF:notation]])
with its LaTeX, Python, and pymdp-keyword counterparts.  The
free-energy observables it produces are the subject of
[[SECREF:pymdp_free_energy]]; the validation / logging contract that
gates the entire chain is [[SECREF:pymdp_validation]].

## Architecture: layered, not duplicated

The pymdp harness wraps each stream of the
$K = [[VAR:pymdp_ensemble_K]]$ Ising toy as a separate
`pymdp.agent.Agent` with a 2-state, 2-action POMDP — identity
likelihood ($A = I$), hold/swap transitions ($B$), biased preference
vector ($C$), and uniform initial prior ($D$); ensemble precision
$\gamma = [[VAR:pymdp_ensemble_gamma:g]]$, generative-model coupling
$\lambda_{\mathrm{gen}} = [[VAR:pymdp_ensemble_coupling_lambda:g]]$.

```
┌──────────── pymdp [[VAR:pymdp_distribution_version]] mean-field layer (per-stream) ──────────────┐
│  Agent(A, B, C, D, gamma, inference_algo='fpi')   ← deterministic   │
│    .infer_states([obs], prior)  ──▶ qs                              │
│    .infer_policies(qs)          ──▶ q_pi^k, G_k                     │
│  Output: per-stream policy PMF q_pi^k and EFE vector G_k.           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  fed to analytical layer
┌──────── analytical λ-coupling layer (numpy, project-owned) ────────┐
│  coupled_policy_posterior(spec, obs, lam)                          │
│    = entangled_posterior(mf=q_pi^k, G=zeros, J, K_c, γ, λ)         │
│  Note: G=zeros because pymdp has already absorbed γ·G into q_pi.   │
│  At λ=0 this collapses *exactly* to the outer product of q_pi^k.   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  read off observables
┌────────────── free-energy bundle and observables ──────────────────┐
└─────────────────────────────────────────────────────────────────────┘
```

The free-energy bundle readout is detailed in [[SECREF:pymdp_free_energy]].

**Adapter boundary.**  The harness does not patch pymdp internals and
does not require pymdp to natively support structured joint policy
posteriors.  pymdp supplies each stream's `Agent.infer_states` and
`Agent.infer_policies` result; the project adapter then forms
$q_\lambda$ by applying the manuscript's
`entangled_posterior` construction to those per-stream policy
posteriors.  The validation gates therefore test two claims
separately: the per-stream calls agree with the documented pymdp API,
and the repository's coupling layer preserves the $\lambda = 0$
mean-field baseline before adding cross-stream dependence.

**Reproducibility checklist.**  The software package is
`inferactively-pymdp==1.0.1`, installed through the project's `sim`
dependency group and cited through both the JOSS software paper and
the official repository / documentation
[@heins-2022; @pymdp-developers-2026; @pymdp-docs-2026].  The POMDP
state/action primitives are not prose-only: `StreamSpec` and
`CoupledEnsembleSpec` validate the $A$, $B$, $C$, and $D$ arrays
before each `Agent` is built, and the default Ising ensemble is
constructed in `make_ising_ensemble`.  The policy horizon and
inference settings are exactly the hyperparameters mirrored into the
manuscript: `policy_len=[[VAR:pymdp_agent_policy_len]]`,
`inference_algo="[[VAR:pymdp_agent_inference_algo]]"`,
`num_iter=[[VAR:pymdp_agent_num_iter]]`,
`action_selection="[[VAR:pymdp_agent_action_selection]]"`,
`alpha=[[VAR:pymdp_agent_alpha:g]]`,
`use_states_info_gain=[[VAR:pymdp_agent_use_states_info_gain]]`, and
`use_param_info_gain=[[VAR:pymdp_agent_use_param_info_gain]]`.  The
sweep uses observations `[[VAR:pymdp_sweep_observations]]`, and the
rollout uses seed `[[VAR:pymdp_rollout_seed]]`; all additional random
draws are routed through `np.random.default_rng`.  Output variables
are the per-$\lambda$ policy posterior, EFE vector, free-energy
bundle, total correlation, action distribution, coupled rollout
trajectory, JSONL run-log fields, and rendered PNG metadata.  The
single rerun command is:

```bash
uv run python scripts/simulate_pymdp.py
```

Three contracts are load-bearing:

1. **No double-counting.**  pymdp's `q_pi^k` already contains the
   per-stream `γ · G_k` softmax bias.  The analytical layer therefore
   passes `zero_G` to `entangled_posterior` so the coupling potentials
   `λ · J` and `γ · λ · K_c` are added *once*, not twice.
2. **λ = 0 sentinel.**  At $\lambda = 0$ the *marginals* of the
   coupled joint posterior reproduce pymdp's per-stream policy
   posteriors to floating tolerance
   ($[[VAR:pymdp_marginal_agreement_tolerance:.0e]]$); the joint
   factorizes by construction (since
   $\exp(\lambda \cdot J) = 1$ pointwise).
   This marginal-agreement check is asserted by
   `tests/test_simulation_pymdp.py::test_coupled_policy_posterior_lambda_zero_is_outer_product`.
   The free-energy-bundle test
   `test_free_energy_bundle_lambda_zero_baseline` checks the stronger
   implications: total correlation
   $< [[VAR:pymdp_tc_zero_tolerance:.0e]]$, coupling term
   $< [[VAR:pymdp_coupling_zero_tolerance:.0e]]$, and joint entropy
   equals the sum of marginal entropies to
   $[[VAR:pymdp_entropy_add_tolerance:.0e]]$.
3. **Determinism.**  The harness configures pymdp [[VAR:pymdp_distribution_version]] with
   `inference_algo="[[VAR:pymdp_agent_inference_algo]]"` for
   `infer_states` and `infer_policies`; there is no random sampling
   inside those calls, so the entire chain is reproducible under fixed
   `(spec, obs, lam, seed)`.

**Note on precision.**  `inferactively-pymdp==1.0.1` provides the pymdp
import/API, whose JAX path uses `float32` for per-stream inference
(`infer_states`, `infer_policies`).  The harness recasts the
resulting policy posteriors $q^k_\pi$ and EFE values $G_k(\pi)$ to
`float64` at the analytical-layer boundary in
[`src/simulation/inference.py`](../src/simulation/inference.py), so
downstream observables (the entangled posterior, free-energy bundle,
total correlation) are computed in double precision.  Cross-platform
numerical differences attributable to the JAX backend are bounded by
$[[VAR:pymdp_single_stream_float_tolerance:.0e]]$ in single-stream
observables; the numerical identities verified in
[[SECREF:pymdp_validation]] hold at the
$[[VAR:pymdp_single_stream_float_tolerance:.0e]]$ tolerance.

**Scope of the sub-`float32` gates (stated precisely).**  pymdp's
inference runs in JAX `float32` (machine $\varepsilon \approx
1.2\times10^{-7}$).  The tight decomposition-residual and
total-correlation-zero gates (at $10^{-9}$/$10^{-7}$) therefore do
**not** certify pymdp's `float32` numbers directly: they are evaluated
on the recast-to-`float64` *analytical coupling layer* (the zeroed-$G$
algebraic path), where the per-stream `float32` quantities enter only
through the recast boundary above.  These gates verify the
analytical-layer algebra (the decomposition identity, $I\ge 0$, the
$\lambda=0$ baselines); pymdp's `float32` contribution is bounded
separately at the single-stream
$[[VAR:pymdp_single_stream_float_tolerance:.0e]]$ tolerance, not at
$10^{-9}$.  No claim is made that the raw `float32` pymdp pipeline
satisfies the $10^{-9}$ identities.

## The static λ-sweep

Sweep parameters: $\lambda \in [[[VAR:pymdp_sweep_lambda_min:g]],
[[VAR:pymdp_sweep_lambda_max:g]]]$
on a $[[VAR:pymdp_sweep_grid_points]]$-point grid at fixed
observations $o = (0, 0)$.  Hyperparameters are sourced from
[`src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py)
(`PYMDP_SWEEP_LAMBDAS`, `PYMDP_SWEEP_OBSERVATIONS`).

The artifact is a $[[VAR:pymdp_sweep_grid_points]]$-row CSV at
[`output/simulations/pymdp_lambda_sweep.csv`](../output/simulations/pymdp_lambda_sweep.csv);
the visual rendering is the total-correlation curve plus three
sentinel-λ heatmap snapshots.

The four sentinel total correlations along the sweep — auto-injected
from
[`scripts/manuscript_variables.py`](../scripts/manuscript_variables.py)
on every render — are:

| $\lambda$ | $I(q_\lambda)$ | Interpretation |
|---:|---:|---|
| $0$ | $[[VAR:pymdp_total_correlation_lam_0:.6f]]$ nats | Mean-field baseline (exact zero by construction) |
| $1$ | $[[VAR:pymdp_total_correlation_lam_1:.4f]]$ nats | Sub-saturation: coupling gain growing rapidly |
| $2$ | $[[VAR:pymdp_total_correlation_lam_2:.4f]]$ nats | Past half-saturation $\lambda_{1/2} \approx [[VAR:pymdp_summary_lambda_at_half_saturation:.3f]]$ |
| $4$ | $[[VAR:pymdp_total_correlation_lam_4:.4f]]$ nats | Approaches sweep maximum $I_{\max} \approx [[VAR:pymdp_summary_tc_max:.4f]]$ |

The $\lambda$-column labels above are the sentinel values
$\{[[VAR:pymdp_total_correlation_sentinel_lambdas]]\}$ exposed by
`PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS` in
[`src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py);
changes to that tuple require regenerating this table.  (The full
12-statistic table is in [[SECREF:app.bundle_stats]] of the
supplement.)

[[FIG:pymdp_total_correlation_curve]]

[[FIG:pymdp_joint_lambda_0]]

[[FIG:pymdp_joint_lambda_2]]

[[FIG:pymdp_joint_lambda_4]]

## Deterministic coupled rollout

A second probe of the harness: a $T = [[VAR:pymdp_rollout_steps]]$-step
coupled rollout under coupling $\lambda = [[VAR:pymdp_rollout_lambda:g]]$
and seed $[[VAR:pymdp_rollout_seed]]$.  At each step the harness:

1. Lets each stream see its observation and runs pymdp's per-stream
   inference (`per_stream_policy_posterior`).
2. Builds the λ-coupled joint via the analytical layer
   (`coupled_policy_posterior`).
3. Samples one joint action from the coupled posterior with a
   seeded `np.random.default_rng`.
4. Advances each stream's hidden state under the sampled action's
   `B` matrix and samples the next observation.

Numerically identical reproducibility of the sampled action sequence
and hidden-state trajectory under fixed seed is asserted by
`tests/test_simulation_pymdp.py::test_simulate_coupled_rollout_deterministic_under_fixed_seed`.

[[FIG:pymdp_coupled_rollout]]

**Reproduce.**

```bash
uv run python scripts/simulate_pymdp.py
```

Emits the CSV + figures referenced above as well as the
free-energy bundle artifacts of [[SECREF:pymdp_free_energy]] and the
structured run-log records of [[SECREF:pymdp_validation]].

## Anchored figure index for the pymdp harness

The harness emits a coupled-rollout trajectory plot and two
sentinel joint-policy heatmaps that anchor the deterministic rollout
discipline of this section:
[[FIGREF:pymdp_coupled_rollout]] (the coupled-rollout trajectory),
[[FIGREF:pymdp_joint_lambda_2]] (joint policy at $\lambda = 2$),
[[FIGREF:pymdp_joint_lambda_4]] (joint policy at $\lambda = 4$), and
[[FIGREF:pymdp_total_correlation_curve]] (total correlation curve
over the sweep).  Each is also embedded above at its primary
generation point; this paragraph exists so the harness section is the
canonical anchor index for them.

---
