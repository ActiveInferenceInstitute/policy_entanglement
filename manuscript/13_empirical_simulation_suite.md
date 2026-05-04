# Empirical / Simulation Suite

This section pairs every theoretical claim of [[SECREF:decomposition]]–[[SECREF:phase]] with a *concrete*
computational experiment.  All experiments are reproduced by the
companion code under
[`src/`](../src/) and [`scripts/`](../scripts/); the deterministic
artefacts they emit live under [`output/`](../output/).

The suite is split into two layers:

1. **Closed-form / numeric core** — pure-NumPy code under
   [`src/lean/`](../src/lean/), tested with no mocks
   (≥ 175-test pytest suite, ≥ 90 % coverage).  Realises every quantity
   in the Lean boundary fragment.
2. **POMDP simulation harness** — the new `pymdp` 1.0.1 layer
   under [`src/simulation/`](../src/simulation/) that *grounds* the
   coupled-policy ensemble inside an actual partially-observed Markov
   decision process [@heins-2022].  See
   [`docs/simulation/pomdp_simulation.md`](../docs/simulation/pomdp_simulation.md)
   for the architecture diagram and full API.

Throughout, "λ-coupled" means the joint policy posterior obtained by
running the per-stream `pymdp` posteriors through
`coupling.entangled_posterior` with the manuscript's
$(J, K_c, \gamma, \lambda)$ parametrisation — i.e. the exact
analytical layer of [[SECREF:lambda_deformation.entangled_posterior]] sits on top of pymdp's mean-field engine.

## Two-stream Bernoulli (K=2) closed-form validation

- Sweep $\lambda \in [0, 6]$ on a fine grid; at each $\lambda$ compute
  the closed-form mutual information [[EQREF:ising_mi_closed_form]] and
  the empirical total correlation of the Ising joint posterior, and
  confirm they agree to $10^{-6}$.  Concrete values:
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
uv run python scripts/parameter_sweep.py        # 121-row CSV
uv run python scripts/manuscript_variables.py   # JSON of in-text values
```

[[FIG:ising_mi_curve]]

[[FIG:free_energy_curve]]

[[FIG:optimal_lambda]]

## pymdp 1.0.1 grounded coupled ensemble

The pymdp harness wraps each stream of the K=2 Ising toy as a separate
`pymdp.agent.Agent` with a 2-state, 2-action POMDP (identity
likelihood, hold/swap transitions, biased preference vector).  At each
λ value we extract the per-stream `q_pi^k` from pymdp and apply the
analytical λ-coupling on top — *layered*, not duplicated, so that
$\lambda = 0$ recovers the pure mean-field outer product exactly.

**Reproduce.**

```bash
uv run python scripts/simulate_pymdp.py
```

Emits the CSV at
[`output/simulations/pymdp_lambda_sweep.csv`](../output/simulations/pymdp_lambda_sweep.csv)
and the four figures below.

[[FIG:pymdp_total_correlation_curve]]

[[FIG:pymdp_joint_lambda_0]]

[[FIG:pymdp_joint_lambda_2]]

[[FIG:pymdp_joint_lambda_4]]

[[FIG:pymdp_coupled_rollout]]

## Heterogeneous VFE / EFE validation

This block exercises [[THMREF:thm_8_1]] (coupling-tax bound) numerically.

- Assign one stream `InferenceMode.VFE`, one `InferenceMode.EFE`.
- Sweep $\lambda \in [0, 1.5]$.
- Compute the *coupling tax* $D_{\mathrm{KL}}(q_{\mathrm{full}} \,\|\,
  q_{\mathrm{pinned}})$, fit the small-$\lambda$ slope, and confirm
  the $O(\lambda^2)$ envelope predicted by [[EQREF:coupling_tax_bound]].

[[FIG:coupling_tax_quadratic]]

## Phase structure (K=2, varying J shape)

- Vary $\lambda$ across the $(\lambda_c^{(1)}, \lambda_c^{(2)})$
  thresholds defined in [[SECREF:phase]].
- Visualise the disordered / mixed / frozen regimes as a 1-D phase
  band, and the joint $(F, \lambda)$ landscape as a heatmap.

[[FIG:phase_diagram]]

[[FIG:phase_landscape]]

## Spectral structure (Schmidt rank, archetypes)

- Verify [[THMREF:prop_7_1]] numerically (rank-1 iff mean-field) by sweeping
  $\lambda$.  At $\lambda = 0$ the rank is
  $r = [[VAR:ising_schmidt_rank_at_lam_0]]$; at $\lambda = 1$ it
  jumps to $r = [[VAR:ising_schmidt_rank_at_lam_1]]$.  The smooth
  analogue, the entanglement entropy, has
  $S_E(0) = [[VAR:ising_S_E_at_lam_0:.4f]]$,
  $S_E(1) = [[VAR:ising_S_E_at_lam_1:.4f]]$,
  $S_E(3) = [[VAR:ising_S_E_at_lam_3:.4f]]$.
- Decompose $q_\lambda$ at $\lambda = 3$ into Schmidt archetypes and
  visualise weights + pairwise overlaps.
- Sweep across stream counts $K \in \{2, 3, 4, 5\}$ and tabulate the
  tensor-train rank profile: K=2 gives $[[VAR:tt_ranks_K2]]$, K=3
  $[[VAR:tt_ranks_K3]]$, K=4 $[[VAR:tt_ranks_K4]]$, K=5
  $[[VAR:tt_ranks_K5]]$.

[[FIG:schmidt_rank]]

[[FIG:schmidt_entropy_surface]]

[[FIG:joint_heatmap_lambda2]]

[[FIG:archetype_dendrogram]]

[[FIG:tensor_train_rank_surface]]

## Information-geometric structure (e-geodesic)

- For each policy $\pi$, compute the unnormalised log-weight
  $\log q_\lambda(\pi) + \log Z(\lambda)$ across $\lambda \in [0, 3]$
  (see [[EQREF:e_geodesic]]).
- Plot one line per policy.

[[FIG:log_weight_flow]]

## Multi-stream coupling graph

For $K = 4$ Ising-style coupling, render the coupling potential $J$
as a graph over streams (edge weight = mean $|J|$ across all slot
pairs), illustrating the homogeneous all-to-all structure of the
symmetric coupling.

[[FIG:coupling_graph]]

## Software and numerical stack

The full reproducibility chain rests on four open-source Python
foundations and two Lean foundations:

* **NumPy** [@harris-2020] for the dense `(|\Pi^1| \times \cdots \times
  |\Pi^K|)` joint policy tensors,
* **SciPy** [@virtanen-2020] for special functions and linear-algebra
  decompositions,
* **Matplotlib** [@hunter-2007] for every figure under
  `output/figures/`,
* **JAX** [@bradbury-2018] for the pymdp 1.0.1 backend (used by
  `src/simulation/`),
* **Lean 4** [@demoura-ullrich-2021] and its eventual Mathlib
  refinement [@mathlib-2020] for the formalised theorem statements
  under `lean/ActinfPolicyEntanglement/`.

All five are pinned via the `uv` lockfile; the `sim` and `viz` groups
of [`pyproject.toml`](../pyproject.toml) declare the optional
extensions.

## Habit learning, revertibility, and connections to BTAI

The remaining experiments (long-horizon habit accumulation,
m-projection-back-to-mean-field as a revertibility test, and a
head-to-head comparison with Branching-Time AIF [@champion-2022]) are
tracked as future work in the companion paper
[`manuscript/15_companion_paper_outline.md`](15_companion_paper_outline.md).
The pymdp harness already provides the necessary hooks
(`simulate_coupled_rollout`, `marginal_trajectory`,
`total_correlation_curve`); the gap is the *task design*, not the
infrastructure.

---
