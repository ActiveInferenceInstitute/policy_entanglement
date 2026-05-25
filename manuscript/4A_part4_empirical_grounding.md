# Part IV — Empirical Grounding {-}

Part II states the identities; Part IV shows how they survive contact
with executable finite ensembles.  The empirical layer starts with the
closed-form Bernoulli toy, then uses the real
`pymdp.agent.Agent` class for per-stream inference and adds the
$\lambda$-coupling layer only after pymdp has produced its ordinary
per-stream posteriors.  That split is intentional: the harness does
not ask pymdp to know about policy entanglement, and it does not
replace pymdp with a mock.  It measures exactly what changes when an
ordinary mean-field active-inference engine is lifted into a coupled
joint policy posterior.

The empirical bridge is specified as a reproducibility checklist, not
as an informal simulation description.  The package provenance is the
pinned `inferactively-pymdp==1.0.1` distribution that provides the
`pymdp` import/API, with the JOSS paper, official repository, and
official documentation serving as the external source trail
[@heins-2022; @pymdp-developers-2026; @pymdp-docs-2026].  The local
model provenance is `src/simulation/specs.py` plus
`src/simulation/builders.py`: those modules materialize the POMDP
matrices $(A,B,C,D)$, the configured observation tuple
`[[VAR:pymdp_sweep_observations]]`, the ensemble precision
$\gamma=[[VAR:pymdp_ensemble_gamma:g]]$, and the coupling amplitude
$\lambda_{\mathrm{gen}}=[[VAR:pymdp_ensemble_coupling_lambda:g]]$.
Agent-level settings are likewise source-derived: policy length
[[VAR:pymdp_agent_policy_len]], inference algorithm
`[[VAR:pymdp_agent_inference_algo]]`, FPI iteration count
[[VAR:pymdp_agent_num_iter]], action selection
`[[VAR:pymdp_agent_action_selection]]`, and action precision
[[VAR:pymdp_agent_alpha:g]].  The emitted observables are CSV/JSONL/PNG
sidecars, then `scripts/manuscript_variables.py` mirrors their
current values into the `[[VAR:...]]` token system before the
manuscript is rendered.

The suite exercises the default $K=[[VAR:pymdp_ensemble_K]]$
Ising-style coupling and the configured multi-K sweep
$K \in \{[[VAR:multi_k_values_list]]\}$, runs both short and long-horizon
rollouts ($T=[[VAR:pymdp_rollout_steps]]$ and
$T=[[VAR:long_horizon_steps]]$, with the long-horizon trace explicitly
recording habit accumulation), and emits the $m$-projection
revertibility witness
($I(q) = D_{\mathrm{KL}}(q\,\|\,\hat m(q))$ to floating-point
tolerance).  Head-to-head comparison with branching-time AIF remains
the natural empirical follow-on.
Four chapters:

* **[[SECREF:empirical]]** — the closed-form K=2 Bernoulli toy,
  whose two algebraically-independent closed forms agree to
  floating-point tolerance (internal analytic consistency) *and* whose
  total correlation a genuine seeded finite-$N$ Monte-Carlo estimator
  (`empirical_mutual_information_montecarlo`) reproduces within its
  sampling-error band — the real finite-sample empirical witness,
  with convergence and $\sim\!4\sigma$ concentration gated in
  `tests/test_bernoulli_toy.py`;
  the $O(\lambda^2)$ heterogeneous coupling-tax envelope verified on
  the [[VAR:coupling_tax_grid_points]]-point coupling sweep; the
  spectral and phase-structure witnesses.
* **[[SECREF:pymdp_harness]]** — the [[VAR:pymdp_distribution_version]] grounded
  architecture: per-stream `Agent` construction, deterministic
  fixed-point-iteration inference, ensemble coupling layer, and the
  $\lambda$-sweep + coupled-rollout entry points.
* **[[SECREF:pymdp_free_energy]]** — the *full* free-energy bundle
  observable schema: per-stream VFE, expected EFE, joint and marginal
  entropies, total correlation, coupling term, action distribution —
  emitted at every $\lambda$ in the sweep.
* **[[SECREF:pymdp_validation]]** — three-tier validation gates
  (schema → range → identity), the `[[VAR:...]]` token system that
  pipes every numeric value from a real run into the manuscript
  prose, and the validator that fails CI on any hardcoded grid count,
  seed, or rollout horizon.

The empirical results regenerate from a single command
(`scripts/run_all.py`). The orchestrator first creates the empirical
sidecars, then materializes `manuscript_variables.json`, then renders
the manuscript.  This order matters: every numeric claim below is
injected after the current run has written the sidecar summaries it
depends on. Every emitted PNG carries reproducibility tEXt metadata
(source script, function, hyperparameter snapshot, git revision, ISO
timestamp, and compact plotted-data summaries).

---
