# Statistics Reference

*Latest generated audit.*

The full statistical methodology of the Policy Entanglement project
in one page: every grid, seed, agreement tolerance, sampling
contract, free-energy quantity, and the layered relationship
between pymdp's stochastic backend and the project's deterministic
analytical layer.

This page is the **statistics counterpart** to
[`guides/styleguide.md`](../guides/styleguide.md): the styleguide
says *what* the contract is, this page says *what each number means
and why it has the value it does*.

---

## 1 — Determinism contract

Every figure / sweep / simulation in this project is bit-reproducible
under fixed seeds.  The contract:

| Surface | Mechanism | Source-of-truth |
| --- | --- | --- |
| `numpy` global RNG | `deterministic_setup(seed=...)` at script top | `src/visualizations/setup.py` |
| pymdp 1.0.1 (JAX backend) | Deterministic FPI inference algorithm; no random sampling inside `infer_states` / `infer_policies` | `simulation.agents.build_pymdp_agent(inference_algo='fpi')` |
| Coupled rollout sampling | `np.random.default_rng(seed)` instantiated once per rollout | `simulation.rollout.simulate_coupled_rollout` |
| Figure global seed | `42` | `simulation.hyperparameters.FIGURE_GLOBAL_SEED` |
| Rollout seed (manuscript figure) | `0` | `simulation.hyperparameters.PYMDP_ROLLOUT_SEED` |

Two consecutive runs of the full pipeline produce **bit-identical**
artifacts (verified by `tests/test_simulation_pymdp.py::test_simulate_coupled_rollout_deterministic_under_fixed_seed`).

---

## 2 — Grid sizes (sample sizes)

Every "sample size" is a 1-D `linspace` count read from
`simulation.hyperparameters`.  Numerical agreement / convergence
contracts hinge on these counts:

| Quantity | Grid | Points | Reason for choice |
| --- | --- | ---: | --- |
| Closed-form vs empirical Ising MI | `PARAMETER_SWEEP_LAMBDAS` | `param_sweep_grid_points` | Grid count, range, and tolerance are mirrored into `manuscript_variables.json` from `simulation.hyperparameters`. |
| Heterogeneous coupling-tax envelope | `COUPLING_TAX_LAMBDAS` $\lambda \in [0,1.5]$ | 31 | Δλ = 0.05 — small-λ regime where the $O(\lambda^2)$ envelope dominates |
| Phase-band fill plot | `PHASE_DIAGRAM_LAMBDAS` $\lambda \in [0,4]$ | 401 | Δλ = 0.01 — sub-threshold-width sampling so transitions are pixel-accurate |
| $\lambda^\star(\Delta_{\rm util})$ closed form | `OPTIMAL_LAMBDA_DELTAS` $\Delta \in [-0.95, 0.95]$ | 191 | Δ = 0.01 — symmetric around 0; clipped from $\pm 1$ so $\operatorname{arctanh}$ stays finite |
| Schmidt rank vs λ | `SCHMIDT_RANK_LAMBDAS` $\lambda \in [0,4]$ | 81 | Δλ = 0.05 — adequate to localize the discontinuous rank jump at $\lambda = 0^+$ |
| Phase landscape / Schmidt entropy surface | `PHASE_LANDSCAPE_LAMBDAS × PHASE_LANDSCAPE_UTILITIES` | 41 × 21 | Smooth surface; single-pass colormap |
| Log-weight e-geodesic | `LOG_WEIGHT_FLOW_LAMBDAS` $\lambda \in [0,3]$ | 31 | Affine-in-λ regime; one decade of curvature |
| KL geodesic in 2-D summary | `KL_GEODESIC_LAMBDAS` $\lambda \in [0,4]$ | 21 | Coarse marker grid; visual clarity matters more than density |
| $\lambda^\star$ locus | `LAMBDA_STAR_UTILITIES × LAMBDA_STAR_GAMMAS` | 20 × 16 | Comparative-statics surface; outer-product geometry |
| pymdp grounded sweep | `PYMDP_SWEEP_LAMBDAS` $\lambda \in [0,4]$ | 21 | Each evaluation is one `Agent.infer_states` + `infer_policies` call (~40 ms each); 21 keeps total runtime ≤ 1 s |
| Coupled rollout horizon | `PYMDP_ROLLOUT_STEPS` | 10 | Long enough to see habit accumulation, short enough to fit four rows of the marginals heatmap |

**Cross-check:** every grid count appears in
`output/data/manuscript_variables.json` under a stable key
(`param_sweep_grid_points`, `pymdp_sweep_grid_points`, …) and is
referenced from manuscript prose via `[[VAR:key]]`.

---

## 3 — Numerical agreement / tolerance contracts

| Contract | Tolerance | Where enforced |
| --- | --- | --- |
| Closed-form vs empirical Ising MI residual | $\leq 10^{-6}$ over all 121 grid points | `scripts/validate_outputs.py::validate_sweep`, `tests/test_bernoulli_toy.py` |
| Joint policy posterior PMF normalization | $\sum q = 1.0$ to $10^{-7}$ | `lean.joint_dist.is_pmf(atol=1e-9)`; `tests/test_simulation_pymdp.py` |
| Joint marginal sums to 1 | $10^{-7}$ | every test of `joint_marginals` |
| pymdp marginal vs analytical mean-field at $\lambda = 0$ | $10^{-7}$ | `test_coupled_policy_posterior_lambda_zero_is_outer_product` |
| Schmidt rank discontinuity detector | $|s_\alpha| > 10^{-9}$ counts as nonzero | `lean.spectral.schmidt_rank(atol=1e-12)` |
| Tensor-train rank atol | $10^{-9}$ | `lean.spectral.tensor_train_ranks(atol=1e-12)` |
| Total correlation non-negativity | $\geq -10^{-9}$ (float-noise floor) | `tests/test_simulation_free_energy.py` |
| Free-energy decomposition baseline at $\lambda = 0$ | $|H(q) - \sum_k H(q^k)| \leq 10^{-10}$, $\|q - q^1 \otimes q^2\|_\infty \leq 10^{-10}$ | `validate_outputs.py::validate_free_energy_bundle`, `test_free_energy_bundle_lambda_zero_baseline` |
| Stream-PMF column-stochasticity (A, B[:, :, u], D) | $10^{-8}$ | `simulation.specs.StreamSpec.validate` |
| Output distribution after one step | renormalized to sum 1 | `simulation.rollout._sample_from_joint` |

`PARAMETER_SWEEP_AGREEMENT_TOLERANCE` is the only
agreement tolerance that the manuscript prose substitutes via
`[[VAR:param_sweep_agreement_tolerance]]`; the others are internal
contracts surfaced through tests rather than prose.

---

## 4 — Free-energy bundle: every observable

For every $\lambda$ on `PYMDP_SWEEP_LAMBDAS`, the call
`simulation.inference.free_energy_bundle(spec, [0, 0], lam)` returns
a frozen `FreeEnergyBundle` with the following fields:

| Field | Symbol | Definition | Units |
| --- | --- | --- | --- |
| `vfe_per_stream[k]` | $F[q^k_\lambda]$ | $\langle \log q^k - \log E_k + \gamma G_k\rangle_{q^k_\lambda}$ | nats |
| `vfe_total` | $\sum_k F[q^k_\lambda]$ | sum of `vfe_per_stream` | nats |
| `efe_per_stream[k]` | $G_k$ | pymdp's per-policy EFE vector for stream $k$ | nats (length-$U_k$ array) |
| `efe_under_posterior[k]` | $\langle G_k \rangle_{q^k_\lambda}$ | weighted average of `efe_per_stream[k]` against `q^k_\lambda` | nats |
| `joint_entropy` | $H(q_\lambda)$ | $-\sum_\pi q_\lambda(\pi) \log q_\lambda(\pi)$ | nats |
| `marginal_entropies[k]` | $H(q^k_\lambda)$ | $-\sum_{\pi^k} q^k_\lambda(\pi^k) \log q^k_\lambda(\pi^k)$ | nats |
| `total_correlation` | $I(q_\lambda)$ | $\sum_k H(q^k_\lambda) - H(q_\lambda)$ | nats |
| `coupling_term` | $\lambda \langle J\rangle_{q_\lambda}$ | $\lambda \sum_\pi q_\lambda(\pi) J(\pi)$ | nats |
| `action_distribution` | $q_\lambda$ flat | reshape of joint posterior | PMF on $\prod_k \Pi^k$ |

Every scalar is also written to
`output/simulations/pymdp_free_energy_bundle.csv`
(one row per λ; 12 columns at K=2).

### Statistical contracts on the bundle

* **Sub-additivity:** $H(q_\lambda) \leq \sum_k H(q^k_\lambda)$ at
  every λ (`test_joint_entropy_le_sum_marginal_entropies`).
* **Total-correlation positivity:** $I(q_\lambda) \geq -10^{-9}$
  everywhere (`validate_free_energy_bundle`).
* **λ = 0 baseline:** $I(q_0) = 0$, coupling term $= 0$,
  $H(q_0) = \sum_k H(q^k_0)$, $\text{vfe\_total}_0 = \sum_k F[q^k_0]$
  (`test_free_energy_bundle_lambda_zero_baseline`,
  `test_free_energy_decomposition_witness_at_lambda_zero`).
* **Monotonicity:** under symmetric Ising coupling at observations
  $(0, 0)$, $I(q_\lambda)$ is non-decreasing in $\lambda$
  (`test_total_correlation_monotone_under_symmetric_coupling`).
* **Bundle / helper consistency:** `free_energy_bundle.efe_under_posterior`
  agrees pointwise with the standalone
  `expected_free_energy_under_posterior` and
  `coupling_energy` helpers
  (`test_efe_under_posterior_matches_explicit_helper`,
  `test_coupling_energy_matches_bundle_term`).

### Decomposition relation (Theorem 5.1)

The manuscript's load-bearing identity

$$
F[q_\lambda] \;=\; \sum_k F[q^k_\lambda] \;+\; \lambda \langle J \rangle_{q_\lambda} \;+\; \gamma \lambda \langle K_c \rangle_{q_\lambda} \;-\; \log Z_E(\lambda) \;-\; I(q_\lambda)
$$

is *not* asserted symbolically over `Float` (the boundary Lean
fragment is type-only).  It is instead **numerically witnessed** at
every λ in the sweep — the bundle gives every right-hand-side term
directly, and the test suite verifies the identity at the λ = 0
baseline (where the coupling term and `I` are both zero, so the
identity collapses to `vfe_total == Σ F[q^k]`).

---

## 5 — Statistical methodology per figure

| Figure | Statistical content | Sample size | Method |
| --- | --- | ---: | --- |
| `ising_mi_curve` | Closed-form vs empirical MI residual | 121 | `lean.bernoulli_toy.{ising_mutual_information, empirical_mutual_information}` over `PARAMETER_SWEEP_LAMBDAS` |
| `free_energy_curve` | Free-energy curve, 4 utility levels | 4 × 121 | `lean.bernoulli_toy.ising_free_energy_curve` |
| `coupling_tax_quadratic` | $O(\lambda^2)$ envelope fit | 31 | `lean.heterogeneous.coupling_tax`; envelope constant from second grid point |
| `phase_diagram` | Phase-band fill | 401 | `lean.bernoulli_toy.coupling_phase_at` classification |
| `optimal_lambda` | Closed-form $\lambda^\star(\Delta)$ | 191 | `lean.bernoulli_toy.optimal_lambda` |
| `schmidt_rank` | Discontinuous rank vs λ | 81 | `lean.spectral.schmidt_rank(atol=1e-12)` |
| `phase_landscape`, `schmidt_entropy_surface` | Free-energy / entropy heatmap | 41 × 21 | `lean.bernoulli_toy.ising_free_energy_curve`, `lean.spectral.entanglement_entropy` |
| `joint_heatmap_lambda2` | Joint posterior at λ = 2 | 1 (single λ) | `lean.bernoulli_toy.ising_joint_posterior(2.0)` |
| `archetype_dendrogram` | Schmidt archetypes at λ = 3 | 1 | `lean.spectral.schmidt_decomposition` |
| `tensor_train_rank_surface` | TT-rank profile | 4 (K=2..5) | `lean.spectral.tensor_train_ranks(atol=1e-12)` |
| `log_weight_flow` | e-geodesic affineness | 31 × 4 | `lean.coupling.coupling_log_weight` |
| `kl_geodesic_simplex` | 2-D summary geodesic | 21 | `lean.coupling.entangled_posterior` projected to (aligned-mass, off-diagonal-disparity) |
| `lambda_star_locus` | Comparative-statics surface | 20 × 16 | `lean.bernoulli_toy.optimal_lambda(np.tanh(γ·u))` |
| `pymdp_total_correlation_curve` | Total correlation (pymdp grounded) | 21 | `simulation.inference.coupled_policy_posterior` → `lean.free_energy.total_correlation` |
| `pymdp_joint_lambda_{0,2,4}` | Joint posterior at sentinels | 1 each | `coupled_policy_posterior` |
| `pymdp_coupled_rollout` | Time-series of marginals + TC | `PYMDP_ROLLOUT_STEPS` | `simulation.rollout.simulate_coupled_rollout` with `PYMDP_ROLLOUT_SEED` and `PYMDP_ROLLOUT_LAMBDA` |
| `pymdp_free_energy_panel` | Four-panel free-energy dashboard | 21 | `simulation.inference.free_energy_curve` |
| `pymdp_vfe_decomposition` | Per-stream VFE + decomposition | 21 | bundle |
| `pymdp_efe_under_posterior` | $\langle G_k\rangle_{q^k_\lambda}$ | 21 | bundle |
| `pymdp_entropy_decomposition` | $H(q)$ vs $\sum H(q^k)$ + gap | 21 | bundle |
| `pymdp_action_distribution` | $q_\lambda(\pi)$ heatmap | 21 × 4 | bundle |

Every figure's caption in `manuscript/refs/labels.yaml` names the
exact function path + grid hyperparameter, so a reader can navigate
caption → code → test in one step.

---

## 6 — pymdp-grounded vs analytical layer: how they compose

```
┌──────────────────────────────────────────────────────────────────┐
│  pymdp 1.0.1 mean-field layer (per-stream, JAX-backed)           │
│    Agent(A,B,C,D, gamma, inference_algo='fpi')                   │
│    .infer_states(obs, prior)  ──▶  qs    (state posterior)       │
│    .infer_policies(qs)        ──▶  q_pi^k, G_k                   │
│  Output: per-stream policy PMFs `q_pi^k` and EFE vectors `G_k`.  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼  fed to analytical coupling layer
┌──────────────────────────────────────────────────────────────────┐
│  Analytical λ-coupling layer (numpy, project-owned)              │
│    coupled_policy_posterior(spec, obs, lam)                      │
│      = entangled_posterior(mf=q_pi^k, G=zeros, J, K_c, γ, λ)     │
│  Note: G=zeros because pymdp has already absorbed γ·G into q_pi.│
│  At λ=0 this collapses to the outer product of {q_pi^k}.        │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼  read off observables
┌──────────────────────────────────────────────────────────────────┐
│  Free-energy bundle / total correlation / Schmidt / archetypes   │
└──────────────────────────────────────────────────────────────────┘
```

The two layers are **statistically independent**: pymdp introduces no
hidden randomness (deterministic FPI), and the analytical layer is a
pure function of `(spec, obs, lam)`.  Reproducibility therefore
factors cleanly: pin `spec` + `obs` + `lam` and the entire downstream
chain is bit-identical.

---

## 7 — Test budget breakdown

| Category | Test file | Coverage |
| --- | --- | --- |
| Bernoulli closed forms | `test_bernoulli_toy.py` | K=2 closed-form MI, optimal λ, free-energy curve, phase classifier |
| Coupling layer | `test_coupling.py` | trivial / entangled prior + posterior, log-weight affineness |
| Decomposition theorem | `test_decomposition.py` | Theorem 5.1 RHS + λ=0 collapse |
| Figure-script smoke | `test_figure_scripts.py` | every `figure_*` in `generate_figures.py` + `simulate_pymdp.py` emits a valid PNG |
| Free energy / entropy | `test_free_energy.py` | `shannon_entropy`, KL, joint / marginal entropy, total correlation |
| Generate-index smoke | `test_generate_index.py` | INDEX.md round-trip from registry |
| Information geometry | `test_geometry.py` | mean-field membership, m-projection, Pythagorean residual |
| Heterogeneous (coupling tax) | `test_heterogeneous.py` | Theorem 9.1 numerical witness, mode predicates |
| Joint distribution helpers | `test_joint_dist.py` | PMF / non-negativity / normalize, marginalization, mean-field ⇄ joint |
| Manuscript renderer | `test_manuscript_renderer.py` | every token kind × every section × bibliography fallback |
| Manuscript validation | `test_manuscript_validation.py` | hyperlinks / images / hardcoded-literal detector / malformed YAML |
| Manuscript section/theorem refs | `test_manuscript_section_theorem_refs.py` | SEC / SECREF / THM / THMREF resolution + hardcoded-ref detector |
| Manuscript Lean extraction | `test_manuscript_lean_extraction.py` | `[[LEAN:...]]` source extraction parity |
| Manuscript registry | `test_manuscript_registry.py` | `labels.yaml` / `citations.yaml` typed loaders |
| Manuscript variables pipeline | `test_manuscript_variables_pipeline.py` | JSON shape + range gates |
| pymdp simulation harness | `test_simulation_pymdp.py` | per-stream EFE + posterior, λ-coupled joint, deterministic rollout |
| pymdp free-energy bundle | `test_simulation_free_energy.py` | every `FreeEnergyBundle` invariant + bundle ↔ helper agreement |
| pymdp summary statistics + extras | `test_pymdp_extras.py` | `BundleSummary` contracts, 4 dashboard PNGs, PNG metadata round-trip, no-hardcoded-literal detector |
| Free-energy plot smoke | `test_free_energy_plots.py` | 5 free-energy dashboard PNGs |
| Specs validation | `test_simulation_specs.py` | `StreamSpec` / `CoupledEnsembleSpec` shape + column-stochasticity |
| Spectral / archetypes | `test_spectral.py` | Schmidt rank / decomposition / TT ranks |
| Visualization helpers | `test_visualizations.py` | every reusable plot helper with deterministic input |
| Hyperparameters | `test_hyperparameters.py` | grid consistency + JSON mirror parity |
| Equation auto-numbering | `test_equation_numbering.py` | per-section S.K assignment + retag round-trip |
| Logging utils | `test_logging_utils.py` | JSONL emit, append, fresh, runtime, status |
| Notation glossary | `test_notation_glossary.py` | preamble macros + Python idents + Lean abbrevs all in §2a |
| Veridicality / audit chain | `test_veridicality.py` | prose VAR ↔ JSON ↔ JSONL log ↔ Lean source coherence |
| Python API coverage | `test_python_api_coverage.py` | every public `src/` identifier surfaces in `python_api.md` |
| Lean build smoke | `tests/lean/test_lean_build.py` | `lake build` 22/22 jobs green |
| Multi-K experiments | `tests/test_multi_k_experiments.py` | configured multi-K Ising sweep numerics + figures + summary keys |
| Robustness / ablation expansion | `tests/test_robustness.py` | one-axis stress scenarios, coupling ablations, and long-horizon replicate summaries |
| Long-horizon rollout (round 3) | `tests/test_long_horizon.py` | `LONG_HORIZON_STEPS` rollout converges; steady-state KL within tolerance |
| Revertibility (round 3) | `tests/test_revertibility.py` | m-projection KL identity across the sweep |
| Dashboard invariants (round 3 += 1) | `tests/test_invariants_and_dashboard.py` | 47 invariants registered |
| **Total (Python boundary + Lean smoke)** | live collection count from `output/reports/test_results.json`; 22/22 lake jobs green | live collection count from `uv run pytest --co -q`; pass/fail depends on optional dependency availability |

(Counts current as of the latest `uv run pytest tests/ -q` green
run; `tests/lean/test_lean_build.py` adds 1 lake-build smoke test
on top of the per-module Python suite.)

---

## See also

* [`guides/styleguide.md`](../guides/styleguide.md) — manuscript ↔ code contract.
* [`reference/architecture.md`](architecture.md) — two-layer / executable-track design.
* [`simulation/pomdp_simulation.md`](../simulation/pomdp_simulation.md) — pymdp 1.0.1 harness internals.
* [`reference/lean_reference.md`](lean_reference.md) — per-theorem Lean status.
