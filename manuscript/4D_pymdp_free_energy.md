# pymdp Free-Energy Bundle Observables and Auto-Injected Summary Statistics

For every $\lambda$ in the
$[[VAR:pymdp_sweep_grid_points]]$-point pymdp sweep
([[SECREF:pymdp_harness]]) we read off a complete
*free-energy bundle* — every observable that downstream prose,
figures, or tests might want — via
`simulation.inference.free_energy_curve`.
The bundle is a frozen dataclass.  Its fields are deliberately named
after the mathematical observable they expose, so manuscript prose,
tests, and figures can all point at the same values:

* `vfe_per_stream[k]`: $F[q^k_\lambda] =
  \langle \log q^k - \log E_k + \gamma G_k\rangle_{q^k_\lambda}$,
  in nats.
* `vfe_total`: $\sum_k F[q^k_\lambda]$, the sum of streamwise VFE.
* `efe_per_stream[k]`: pymdp's per-policy $G_k$ vector for stream $k$.
* `efe_under_posterior[k]`: $\langle G_k\rangle_{q^k_\lambda}$, the
  posterior-weighted EFE for stream $k$.
* `joint_entropy` and `marginal_entropies[k]`: $H(q_\lambda)$ and
  $H(q^k_\lambda)$, in nats.
* `total_correlation`: $I(q_\lambda)=\sum_k H(q^k_\lambda)-H(q_\lambda)$.
* `coupling_term`: $\lambda\langle J\rangle_{q_\lambda}
  = \lambda\sum_\pi q_\lambda(\pi)J(\pi)$.
* `decomposition_lhs`, `decomposition_rhs`, and
  `decomposition_residual`: the positive-$\lambda$
  [[THMREF:thm_4_1]] numerical witness computed with
  `free_energy_against_entangled_prior` and
  `entanglement_decomposition_rhs(...).total`.  The witness passes
  zero per-stream `G` vectors because pymdp has already absorbed EFE
  into the per-stream policy posterior before the project adds
  cross-stream coupling.
* `action_distribution`: the flattened PMF $q_\lambda$ on
  $\prod_k \Pi^k$.

Every scalar is also written to
`output/simulations/pymdp_free_energy_bundle.csv` (one row per
$\lambda$; columns as in the table above for
$K = [[VAR:pymdp_ensemble_K]]$ streams).

## Statistical contracts

The bundle satisfies six numerical invariants verified by
`tests/test_simulation_free_energy.py`:

* **Sub-additivity:** $H(q_\lambda) \leq \sum_k H(q^k_\lambda)$ at
  every $\lambda$.
* **Total-correlation positivity:** $I(q_\lambda) \geq 0$ everywhere
  (float-noise floor
  $-[[VAR:pymdp_coupling_zero_tolerance:.0e]]$).
* **$\lambda = 0$ baseline:** $I(q_0) = 0$, coupling term = 0,
  $H(q_0) = \sum_k H(q^k_0)$, and `vfe_total` = $\sum_k F[q^k_0]$.
* **Monotonicity:** under the symmetric Ising coupling at observations
  $(0, 0)$, $I(q_\lambda)$ is non-decreasing in $\lambda$ — the
  empirical witness of [[THMREF:prop_6_3]] inside a real POMDP.
* **Bundle / helper consistency:** the bundle's `efe_under_posterior`
  and `coupling_term` agree pointwise with the standalone
  `expected_free_energy_under_posterior` and `coupling_energy`
  helpers respectively.
* **Positive-$\lambda$ decomposition witness:** the full sweep's
  maximum residual
  $|\mathrm{LHS}-\mathrm{RHS}|$ is
  $[[VAR:pymdp_decomposition_residual_max:.2e]]$ nats, below the
  configured tolerance
  $[[VAR:pymdp_decomposition_residual_tolerance:.0e]]$.

## Summary statistics across the sweep

The bundle is reduced to a flat summary record by
[`simulation.statistics.pymdp_summary_statistics`](../src/simulation/statistics.py),
mirrored to
[`output/simulations/pymdp_summary.json`](../output/simulations/pymdp_summary.json),
and merged into `manuscript_variables.json` so every auto-injected value flows
from a real pipeline run.  The full 12-statistic reference table
(sweep grid, total-correlation range and half-saturation point,
VFE extrema, coupling-term range, entropy bounds, aligned-corner mass,
KL divergences, action entropy, mode probability) is in
[[SECREF:app.bundle_stats]] (supplement).

Every value in [[SECREF:app.bundle_stats]] is computed once per pipeline run and re-injected on the next render — no number there is typed by hand.

## Visualizations

Nine dashboards are emitted by
`scripts/simulate_pymdp.py::figure_pymdp_free_energies`.  The first
is a six-panel summary, the next four magnify each free-energy
pillar, and the final four expose the additional auto-injected
statistics (action entropy, KL to mean-field baseline, per-stream
marginal entropy).  Decomposition plots report **positive**
$I(q_\lambda)$ (multi-information) next to $\sum_k F[q^k_\lambda]$ and the
coupling observable $\lambda\langle J\rangle_{q_\lambda}$ —
consistent with [[THMREF:thm_4_1]]'s explicit ``{+}I`` term —
while acknowledging that ``FreeEnergyBundle`` alone omits
priors/\,$\log Z_E(\lambda)$ bookkeeping from [[SECREF:decomposition]], so stacking only
those three curves is illustrative rather than claiming identity with
global $F[q_\lambda]$ absent the remaining terms.

Every PNG carries reproducibility tEXt with the
source function, hyperparameter snapshot, git revision, and ISO
timestamp — readable via
[`visualizations.metadata.read_figure_metadata`](../src/visualizations/metadata.py).

[[FIG:pymdp_summary_panel]]

[[FIG:pymdp_free_energy_panel]]

[[FIG:pymdp_vfe_decomposition]]

[[FIG:pymdp_efe_under_posterior]]

[[FIG:pymdp_entropy_decomposition]]

[[FIG:pymdp_action_distribution]]

[[FIG:pymdp_action_entropy]]

[[FIG:pymdp_kl_to_lambda_zero]]

[[FIG:pymdp_marginal_entropy_per_stream]]

## [[THMREF:thm_4_1]] Numerical Witness

The manuscript's load-bearing identity [[EQREF:tc_decomp]]

is *not* asserted symbolically over `Float` (the boundary Lean
fragment is type-only).  It is instead numerically witnessed at
every $\lambda$ in the sweep.  The test suite first verifies the
$\lambda = 0$ sanity collapse, where coupling and
$I(q_\lambda)$ vanish; then
`test_pymdp_decomposition_witness_holds_across_positive_lambda_grid`
checks the full positive-$\lambda$ sweep by comparing
`free_energy_against_entangled_prior` to
`entanglement_decomposition_rhs(...).total`.  This is the same
bookkeeping used by the analytical companion, with one pymdp-specific
correction: the per-stream `G` vectors are zeroed in the decomposition
call because pymdp has already baked EFE into the per-stream
posteriors that serve as the mean-field base.  The resulting maximum
residual is
$[[VAR:pymdp_decomposition_residual_max:.2e]]$, and
`scripts/validate_outputs.py` fails if any row exceeds
$[[VAR:pymdp_decomposition_residual_tolerance:.0e]]$.

## Anchored figure index for the pymdp free-energy bundle

The free-energy bundle of this section produces the following
sweep-resolved dashboards, each generated by
`scripts/simulate_pymdp.py` and validated against
`pymdp_summary.json`:
[[FIGREF:pymdp_action_distribution]] (joint action distribution
evolution across the $\lambda$ sweep),
[[FIGREF:pymdp_action_entropy]] (action entropy + mode probability
across $\lambda$),
[[FIGREF:pymdp_efe_under_posterior]] (expected free energy under the
coupled posterior),
[[FIGREF:pymdp_entropy_decomposition]] (joint vs marginal entropy
decomposition),
[[FIGREF:pymdp_free_energy_panel]] (four-panel free-energy dashboard),
[[FIGREF:pymdp_kl_to_lambda_zero]] (KL to the $\lambda = 0$ mean-field
baseline),
[[FIGREF:pymdp_marginal_entropy_per_stream]] (per-stream marginal
entropy), and
[[FIGREF:pymdp_summary_panel]] (six-panel summary dashboard).  Each is
embedded above at its primary generation point; this paragraph
provides the canonical anchor index for the bundle's figure family.

---
