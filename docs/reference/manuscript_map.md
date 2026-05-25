# Manuscript ↔ code ↔ docs map

*Latest generated audit.* The historical round 2 pass added the
`Convexity` (§5.4 + §11.3) and `MarkovBlanket` (§19.3) Lean
submodules; round 3 added `SpectralWitnesses` (§8.1, §8.3) and
`ConnectionsWitnesses` (§17.2, §17.3), graduating the four
remaining `deferred` theorems to `witness` status.  Per-section rows
below reference all four round-2/round-3 modules.

A canonical lookup table that, for every numbered body section of the
manuscript plus supplements S01–S05 (part dividers and supplements
S06/S07 are not mapped here),
points to (a) the Lean module that formalizes its claims, (b) the
Python module that computes them, (c) the test file that verifies
them, and (d) the docs page that explains them in technical depth.

This is the navigation index for the project: from a single
manuscript citation, you can find every artifact in two clicks.

## Per-theorem four-track wiring

For every numbered theorem in the manuscript, the per-theorem table
maps (a) the registry label, (b) the manuscript token, (c) the Lean
qualified name that `[[LEAN:label]]` resolves to, (d) the Python
function that exhibits the numerical witness, (e) the pytest file
that gates the witness against floating tolerance, and (f) the proof
status (`proved`, `forwarder`, `boundary`, or `witness`).

The full table lives in
[`_theorem_map.md`](_theorem_map.md) and is **auto-generated** by
[`../../scripts/generate_theorem_map.py`](../../scripts/generate_theorem_map.py)
from
[`../../manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml). A
CI test asserts that re-running the generator produces no diff against
the on-disk file — any new theorem, renamed Lean declaration, or
changed Python / test companion fails the gate immediately.

→ **See the live table:** [`_theorem_map.md`](_theorem_map.md)

## Body sections

| Manuscript | Lean | Python | Tests | Docs |
|---|---|---|---|---|
| [§1 Motivation](../../manuscript/1B_motivation.md) | — | — | — | [`architecture.md`](architecture.md) |
| [§3 Setup, notation](../../manuscript/2B_setup.md) | [`Basic`](../../lean/ActinfPolicyEntanglement/Basic.lean), [`JointDist`](../../lean/ActinfPolicyEntanglement/JointDist.lean) | [`lean/joint_dist`](../../src/lean/joint_dist.py) | [`test_joint_dist`](../../tests/test_joint_dist.py) | [`math_reference.md`](math_reference.md) |
| [§4 λ-deformation](../../manuscript/2C_lambda_deformation.md) | [`Coupling`](../../lean/ActinfPolicyEntanglement/Coupling.lean) | [`lean/coupling`](../../src/lean/coupling.py) | [`test_coupling`](../../tests/test_coupling.py) | [`math_reference.md`](math_reference.md) §5 |
| [§5 Entanglement decomposition](../../manuscript/2D_decomposition.md) | [`Decomposition`](../../lean/ActinfPolicyEntanglement/Decomposition.lean), [`FreeEnergy`](../../lean/ActinfPolicyEntanglement/FreeEnergy.lean), [`Convexity`](../../lean/ActinfPolicyEntanglement/Convexity.lean) (§5.4 optimal-λ convexity) | [`lean/decomposition`](../../src/lean/decomposition.py), [`lean/free_energy`](../../src/lean/free_energy.py) | [`test_decomposition`](../../tests/test_decomposition.py), [`test_free_energy`](../../tests/test_free_energy.py), [`test_witness_theorems`](../../tests/test_witness_theorems.py) | [`decomposition_theorem.md`](../modules/decomposition_theorem.md) |
| [§6 Examples](../../manuscript/2E_examples.md) | [`BernoulliToy`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean) | [`lean/bernoulli_toy`](../../src/lean/bernoulli_toy.py) | [`test_bernoulli_toy`](../../tests/test_bernoulli_toy.py) | [`bernoulli_toy.md`](../modules/bernoulli_toy.md) |
| [§7 Information geometry](../../manuscript/2F_geometry.md) | [`Geometry`](../../lean/ActinfPolicyEntanglement/Geometry.lean) | [`lean/geometry`](../../src/lean/geometry.py) | [`test_geometry`](../../tests/test_geometry.py) | [`information_geometry.md`](../modules/information_geometry.md) |
| [§8 Spectral / TT structure](../../manuscript/2G_spectral.md) | [`Spectral`](../../lean/ActinfPolicyEntanglement/Spectral.lean), [`SpectralWitnesses`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) (§8.1 Prop 8.2, §8.3 Thm 8.3 — round-3 witnesses) | [`lean/spectral`](../../src/lean/spectral.py); round-3 multi-K experiments via [`scripts/simulate_multi_k.py`](../../scripts/simulate_multi_k.py) | [`test_spectral`](../../tests/test_spectral.py), [`test_witness_theorems`](../../tests/test_witness_theorems.py) | [`spectral_structure.md`](../modules/spectral_structure.md), [`spectral_witnesses.md`](../modules/spectral_witnesses.md) |
| [§9 Heterogeneous ensembles](../../manuscript/2H_heterogeneous.md) | [`Heterogeneous`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean) | [`lean/heterogeneous`](../../src/lean/heterogeneous.py) | [`test_heterogeneous`](../../tests/test_heterogeneous.py) | [`heterogeneous_ensembles.md`](../modules/heterogeneous_ensembles.md) |
| [§10 Phase structure](../../manuscript/2I_phase_structure.md) | [`BernoulliToy.couplingPhaseAt`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean) | [`lean/bernoulli_toy.coupling_phase_at`](../../src/lean/bernoulli_toy.py) | [`test_bernoulli_toy::test_coupling_phase_at_*`](../../tests/test_bernoulli_toy.py) | [`bernoulli_toy.md`](../modules/bernoulli_toy.md) |
| [§11 Comparative statics](../../manuscript/2J_comparative_statics.md) | [`Decomposition.couplingVerdict_correct`](../../lean/ActinfPolicyEntanglement/Decomposition.lean), [`Convexity.freeEnergy_localConcavity_at_zero_witness`](../../lean/ActinfPolicyEntanglement/Convexity.lean) (§11.3 sensitivity) | [`lean/decomposition.coupling_pays_for_itself`](../../src/lean/decomposition.py), [`lean/geometry.coupling_pays_off`](../../src/lean/geometry.py), [`lean/bernoulli_toy.ising_free_energy_curve`](../../src/lean/bernoulli_toy.py) | [`test_decomposition`](../../tests/test_decomposition.py), [`test_geometry`](../../tests/test_geometry.py), [`test_witness_theorems`](../../tests/test_witness_theorems.py) | [`decomposition_theorem.md`](../modules/decomposition_theorem.md) |
| [§12 Lean formalization plan](../../manuscript/3B_lean_formalization.md) | All 17 `ActinfPolicyEntanglement.*` submodules (including round-2 `Convexity` + `MarkovBlanket`, round-3 `SpectralWitnesses` + `ConnectionsWitnesses`, and the `FloatRealResidualWitness` roadmap scaffold) | — | — | [`lean_reference.md`](lean_reference.md), [`MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md) |
| [§13 Empirical / simulation suite](../../manuscript/4B_empirical_suite.md) | — | every `src/lean/*.py`, every `src/simulation/*.py` | every `tests/test_*.py` | [`testing.md`](../guides/testing.md), [`pomdp_simulation.md`](../simulation/pomdp_simulation.md), [`visualizations.md`](../simulation/visualizations.md) |
| [§14 pymdp POMDP harness](../../manuscript/4C_pymdp_harness.md) | — | [`simulation/`](../../src/simulation/) (pymdp grounding) | [`test_simulation_*`](../../tests/) | [`pomdp_simulation.md`](../simulation/pomdp_simulation.md) |
| [§15 pymdp free-energy bundle](../../manuscript/4D_pymdp_free_energy.md) | — | [`simulation/inference.py`](../../src/simulation/inference.py), [`simulation/statistics.py`](../../src/simulation/statistics.py) | [`test_simulation_free_energy`](../../tests/test_simulation_free_energy.py) | [`pomdp_simulation.md`](../simulation/pomdp_simulation.md) |
| [§16 pymdp validation + JSONL log](../../manuscript/4E_pymdp_validation.md) | — | [`simulation/logging_utils.py`](../../src/simulation/logging_utils.py) | [`test_logging_utils`](../../tests/test_logging_utils.py) | [`testing.md`](../guides/testing.md) |
| [§17 Connections — classical AIF](../../manuscript/5B_connections_aif.md) | [`ConnectionsWitnesses`](../../lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean) (§17.2 Thm 17.1, §17.3 Prop 17.2 — round-3 witnesses) | [`lean/decomposition`](../../src/lean/decomposition.py), [`simulation/inference`](../../src/simulation/inference.py); round-3 long-horizon experiment via [`scripts/simulate_long_horizon.py`](../../scripts/simulate_long_horizon.py) | [`test_witness_theorems`](../../tests/test_witness_theorems.py), [`test_long_horizon`](../../tests/test_long_horizon.py) | [`connections_witnesses.md`](../modules/connections_witnesses.md) |
| [§18 Connections — control / RL](../../manuscript/5C_connections_control_rl.md) | — | — | — | [`architecture.md`](architecture.md) |
| [§19 Connections — multi-agent / geometry](../../manuscript/5D_connections_multi_agent.md) | [`MarkovBlanket`](../../lean/ActinfPolicyEntanglement/MarkovBlanket.lean) (§19.3 separation identity) | [`lean/free_energy.total_correlation`](../../src/lean/free_energy.py), [`lean/free_energy.shannon_entropy`](../../src/lean/free_energy.py) | [`test_free_energy`](../../tests/test_free_energy.py), [`test_witness_theorems`](../../tests/test_witness_theorems.py) | [`architecture.md`](architecture.md) |
| [§20 Open questions](../../manuscript/6B_open_questions.md) | — | — | — | — |
| [§21 Discussion and outlook](../../manuscript/6C_discussion_and_outlook.md) | — | — | — | [`architecture.md`](architecture.md) |

## Appendices

| Manuscript | Maps to |
|---|---|
| [Appendix A — Full proof of Theorem 5.1](../../manuscript/S01_proof_of_decomposition_theorem.md) | [`decomposition_theorem.md`](../modules/decomposition_theorem.md), [`Decomposition.lean`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) |
| [Appendix B — Convexity of $F[q_\lambda]$](../../manuscript/S02_convexity_of_free_energy.md) | [`bernoulli_toy.md`](../modules/bernoulli_toy.md) §C.7 |
| [Appendix C — K=2 Bernoulli derivation](../../manuscript/S03_bernoulli_complete_derivation.md) | [`bernoulli_toy.md`](../modules/bernoulli_toy.md), [`BernoulliToy.lean`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean), [`lean/bernoulli_toy.py`](../../src/lean/bernoulli_toy.py) |
| [Appendix D — TT inference algorithm](../../manuscript/S04_tensor_train_inference_algorithm.md) | [`spectral_structure.md`](../modules/spectral_structure.md) |
| [Appendix E — Lean code skeleton](../../manuscript/S05_lean_code_skeleton.md) | [`lean_reference.md`](lean_reference.md), [`lean/`](../../lean/) |
| [Appendix §S6 — Notation concordance](../../manuscript/S06_notation_and_concordance.md) | [`glossary.md`](../glossary.md), [`math_reference.md`](math_reference.md) |
| [Appendix §S7 — Reference tables (claim strength + evidence ladder + module inventory + bundle stats + JSONL schema)](../../manuscript/S07_reference_tables.md) | [`veridical_status.md`](veridical_status.md), [`methods_and_assumptions.md`](methods_and_assumptions.md) |
| [Appendix §S8 — GNN as a Shipped Fifth Track (parser + verified round-trip + Lean typed-contract emitter; `empirical`)](../../manuscript/S08_gnn_generalized_notation_extension.md) | `src/gnn/`, `gnn/*.gnn.md`, `scripts/simulate_gnn.py`; upstream repo [`ActiveInferenceInstitute/GeneralizedNotationNotation`](https://github.com/ActiveInferenceInstitute/GeneralizedNotationNotation); citation: Smékal & Friedman 2023 (Zenodo `10.5281/zenodo.7803328`) |

## Theorems / propositions index

| Manuscript ID | Statement (short) | Lean | Python check |
|---|---|---|---|
| Theorem 5.1 | Entanglement decomposition | `Decomposition.entanglement_decomposition` | `decomposition.entanglement_decomposition_rhs` |
| Cor 5.2 | Coupling pays for itself | `Decomposition.couplingVerdict_correct` | `decomposition.coupling_pays_for_itself` |
| Cor 5.3 | Mean-field at λ = 0 | `Decomposition.couplingLogWeight_pointwise_at_zero` | `test_decomposition::test_decomposition_consistency_at_zero_lambda` |
| Cor 5.4 | Total-correlation unfold | `Decomposition.totalCorrelation_def_unfold` | (numerically: `total_correlation_gain` $\geq 0$) |
| Theorem 5.5 | Existence of optimal coupling (witness form) | `Decomposition.freeEnergy_closedForm_witness` | `decomposition.coupling_pays_for_itself` |
| **Theorem 5.6** | Convexity of F in λ (witness form, NEW round 2) | `Convexity.freeEnergy_convex_in_lam_witness` + `FreeEnergyConvexityWitness` structure | `bernoulli_toy.ising_free_energy_curve` (closed-form convex curve at K=2) |
| Prop 7.1 | MF submanifold is e-flat | `Geometry.mfImage_isMeanField` | (predicate: `is_mean_field`) |
| Prop 7.2 | m-projection minimizes KL | `Geometry.mProjection_kl_eq_self_when_meanfield` | `geometry.m_projection_minimises_kl` |
| Prop 7.3 | I(q) = KL(q ‖ ∏ q^k) | `FreeEnergy.totalCorrelation_eq_kl_to_mprojection` | `free_energy.total_correlation_via_kl` |
| Theorem 7.4 | {q_λ} is e-geodesic | `Geometry.entangledFamily_eGeodesic`, `Coupling.couplingLogWeight_affine_in_lam` | `geometry.is_e_geodesic` |
| Prop 7.5 | Pythagorean (witness form) | `Geometry.dualFlat_pythagorean_witness` | `geometry.pythagorean_residual` |
| Prop 8.1 | Bipartite mean-field factorization | `Spectral.Bipartite.isBipartiteMeanField_factors` (forward), `Spectral.Bipartite.factors_isBipartiteMeanField` (converse) | `spectral.schmidt_rank_one_iff_mean_field` |
| **Prop 8.2** | Rank upper-semicontinuous in λ (witness form, NEW round 3) | `SpectralWitnesses.schmidtRank_upperSemicontinuous_witness` + `UpperSemicontinuousRankWitness` structure | `spectral.schmidt_rank` (numerical detector); multi-K via `simulate_multi_k.py` |
| **Theorem 8.3** | Sparsity-rank tradeoff (witness form, NEW round 3) | `SpectralWitnesses.sparsityRank_tradeoff_witness` + `SparsityRankEnvelope` structure | `spectral.tensor_train_ranks` (numerical witness); multi-K via `simulate_multi_k.py` |
| Theorem 9.1 | O(λ²) coupling-tax bound (witness form) | `Heterogeneous.couplingTax_quadratic_bound` + `BoundedQuadraticTax` structure | `heterogeneous.coupling_tax_within_quadratic_bound` |
| Cor 9.2 | Reflexive-stream tolerance (witness form) | `Heterogeneous.couplingTax_small_lambda_tolerance` + `SmallLambdaTolerance` structure | (numerically: `coupling_tax` decreases) |
| **Prop 11.1** | Local concavity of F at λ = 0 (witness form, NEW round 2) | `Convexity.freeEnergy_localConcavity_at_zero_witness` + `LocalConcavityAtZero` structure | numerical Taylor fit consumed by `test_witness_theorems.py` |
| **Theorem 17.1** | Hierarchical AIF as λ → ∞ limit (witness form, NEW round 3) | `ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness` + `HierarchicalConcentrationWitness` structure | `decomposition.free_energy_against_entangled_prior`; long-horizon via `simulate_long_horizon.py` |
| **Prop 17.2** | Sophisticated inference embedding (witness form, NEW round 3) | `ConnectionsWitnesses.sophisticatedInference_embedding_witness` + `SophisticatedInferenceEmbedding` structure | `simulation.inference.coupled_policy_posterior` (numerical coupled-policy posterior under λ-deformation) |
| **Prop 19.3** | Markov-blanket separation `sep = 1 − I(q)/H(q)` (witness form, NEW round 2) | `MarkovBlanket.markovBlanket_separation_identity_witness` + `MarkovBlanketSeparationWitness` structure | `free_energy.total_correlation`, `free_energy.shannon_entropy` |
| Algebraic skeleton | `CommScalar α` ring-law typeclass + derived lemmas | `Scalar.CommScalar`, `Scalar.affine_diff`, `Scalar.affine_at_zero` | (typeclass; not directly Python-mirrored) |
| Monotonicity | structural lemmas (Nat / Or / List / Fin) | `Monotonicity.*` (constructive theorems) | (kernel-checked, no Python counterpart needed) |
| Constructive | boundary lemmas at λ=0 / trivial coupling | `Constructive.*` (`CommScalar`-polymorphic genuine `= 0` proofs) | (kernel-checked, no Python counterpart needed) |

## Figures

Generated by [`scripts/generate_figures.py`](../../scripts/generate_figures.py)
and [`scripts/simulate_pymdp.py`](../../scripts/simulate_pymdp.py).  Every
PNG is reproducible with `uv run python scripts/run_all.py`.

**Figure-count scoping.**  The table below catalogs **18 headline
figures** that the manuscript renders inline — the 15 analytical PNGs
produced by `generate_figures.py` (rows 1–13 here, where row 13 is
the coupling-potential graph, plus the KL-geodesic-simplex and
λ\*-locus rows at the bottom) plus 3 anchor pymdp panels from
`simulate_pymdp.py` (total-correlation curve, joint-snapshot triptych
counted as one inline row, coupled rollout).  The full registry in
[`../../manuscript/refs/labels.yaml::figures`](../../manuscript/refs/labels.yaml)
contains **46 total figure registry entries** (auto-derived via
`len(labels.figures)`); the table below shows only the 18-figure
headline subset that the manuscript renders inline.  The remaining
registry entries are non-inline cross-reference targets: additional
pymdp variant snapshots used in the dashboard / supplementary panels
(`pymdp_free_energy_panel`, `pymdp_vfe_decomposition`,
`pymdp_efe_under_posterior`, `pymdp_entropy_decomposition`,
`pymdp_action_distribution`, `pymdp_summary_panel`,
`pymdp_action_entropy`, `pymdp_kl_to_lambda_zero`,
`pymdp_marginal_entropy_per_stream`, plus the per-λ joint snapshots
counted individually as `pymdp_joint_lambda_0`, `pymdp_joint_lambda_2`,
`pymdp_joint_lambda_4` in the registry), the round-3 experiments
(`multi_k_total_correlation`, `multi_k_aligned_mass`,
`multi_k_tt_rank_profile`, `long_horizon_marginals`,
`long_horizon_steady_state`, `revertibility_witness`), the robustness
expansion produced by `simulate_robustness.py`, and the shipped BTAI /
adversarial panels (`btai_baseline`, `adversarial_sweep`).
The 15 / 18 / 46 split is documented in
[`../guides/build_run.md`](../guides/build_run.md#figure-count-scoping).

| Figure | Manuscript section(s) | Source function | Path |
|---|---|---|---|
| Closed-form vs empirical Ising MI | §6.1, §13 | `figure_ising_mi_curve` | `output/figures/ising_mi_curve.png` |
| Free-energy curve | §6.1, Appendix B, §13 | `figure_free_energy_curve` | `output/figures/free_energy_curve.png` |
| O(λ²) coupling tax | §9 (Theorem 9.1), §13 | `figure_coupling_tax_quadratic` | `output/figures/coupling_tax_quadratic.png` |
| 1-D phase diagram | §10, §13 | `figure_phase_diagram` | `output/figures/phase_diagram.png` |
| Optimal λ*(Δ) | §6.1, §11, §13 | `figure_optimal_lambda` | `output/figures/optimal_lambda.png` |
| Schmidt rank vs λ | §8.1 (Prop 8.1), §13 | `figure_schmidt_rank_vs_lambda` | `output/figures/schmidt_rank.png` |
| 2-D phase landscape `F(λ, util)` | §10, §13 | `figure_phase_landscape` | `output/figures/phase_landscape.png` |
| Schmidt entropy surface | §8, §13 | `figure_schmidt_entropy_surface` | `output/figures/schmidt_entropy_surface.png` |
| Joint heatmap with marginals (λ=2) | §6.1, §13 | `figure_joint_heatmap_with_marginals` | `output/figures/joint_heatmap_lambda2.png` |
| Archetype dendrogram | §8.2, §13 | `figure_archetype_dendrogram` | `output/figures/archetype_dendrogram.png` |
| Tensor-train rank surface | §8.3 (Theorem 8.3), §13 | `figure_tensor_train_ranks` | `output/figures/tensor_train_rank_surface.png` |
| Log-weight flow (e-geodesic) | §7 (Theorem 7.4), §13 | `figure_log_weight_flow` | `output/figures/log_weight_flow.png` |
| Coupling-potential graph | §19 (CEREBRUM, multi-agent connections), §13 | `figure_coupling_graph` | `output/figures/coupling_graph.png` |
| pymdp total correlation curve | §14 (pymdp harness), §13 | `simulate_pymdp.figure_pymdp_lambda_sweep` | `output/figures/pymdp_total_correlation_curve.png` |
| pymdp joint posterior at λ=0 / 2 / 4 | §14, §13 | `simulate_pymdp.figure_pymdp_lambda_sweep` | `output/figures/pymdp_joint_lambda_*.png` |
| pymdp coupled rollout (`PYMDP_ROLLOUT_STEPS`) | §14 (pymdp harness), §13 | `simulate_pymdp.figure_pymdp_rollout` | `output/figures/pymdp_coupled_rollout.png` |
| KL geodesic in the 2-D summary plane | §7 (Theorem 7.4), §13 | `figure_kl_geodesic_in_simplex` | `output/figures/kl_geodesic_simplex.png` |
| λ⋆(utility, γ) locus | §11, §13 | `figure_lambda_star_locus` | `output/figures/lambda_star_locus.png` |

## Manuscript-substituted variables

`scripts/manuscript_variables.py` writes
[`output/data/manuscript_variables.json`](../../output/data/manuscript_variables.json)
with the in-text numeric substitutions:

| Key | Computed from | Manuscript usage |
|---|---|---|
| `ising_mi_at_lam_05` | `ising_mutual_information(0.5)` | §6.1 numerical example |
| `ising_mi_at_lam_1` | `ising_mutual_information(1.0)` | §6.1 numerical example |
| `ising_mi_at_lam_2` | `ising_mutual_information(2.0)` | §6.1 numerical example |
| `ising_mi_saturation` | `ising_mutual_information(50.0)` | §6.1 saturation check |
| `lambda_star_delta_05` | `optimal_lambda(0.5)` | §11 worked example |
| `lambda_star_delta_09` | `optimal_lambda(0.9)` | §11 worked example |
| `ising_S_E_at_lam_{0,1,3}` | `entanglement_entropy(ising_joint_posterior(λ))` | §8 numerical witnesses |
| `ising_schmidt_rank_at_lam_{0,1}` | `schmidt_rank(ising_joint_posterior(λ))` | §8.1 (Prop 8.1) check |
| `tt_ranks_K{2,3,4,5}` | `tensor_train_ranks(...)` for symmetric Ising K-stream | §8.3 (Theorem 8.3) check |
| `pymdp_total_correlation_lam_{0,1,2,4}` | `total_correlation(coupled_policy_posterior(...))` | §14, §13 (pymdp grounding) — only present when `sim` group installed |

## Per-Lean-module four-track summary

One row per Lean submodule under [`lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/), showing the Python mirror, the test gate, and whether the module's claims are exercised by the pymdp harness as well as by analytical numerics.

| Lean module | Manuscript section | Python mirror | Test gate | pymdp grounding |
|---|---|---|---|---|
| `Basic` | §3 (setup, stream typology) | (no separate mirror; types only) | — | — |
| `Scalar` (typeclass) | §3 / §12 algebraic skeleton | (typeclass; no direct mirror) | (compile-time; exercised by `Monotonicity` + `Constructive`) | — |
| `JointDist` | §3 (joint vs mean-field PMFs) | [`lean/joint_dist`](../../src/lean/joint_dist.py) | [`test_joint_dist`](../../tests/test_joint_dist.py) | indirect (`coupled_policy_posterior` returns a `JointDist`) |
| `Coupling` | §4 (λ-deformation) | [`lean/coupling`](../../src/lean/coupling.py) | [`test_coupling`](../../tests/test_coupling.py) | direct — every `simulate_pymdp.py` row calls `entangled_posterior(mf=q_pi^k, …, λ)` |
| `FreeEnergy` | §5 / §7 (Bregman, total correlation) | [`lean/free_energy`](../../src/lean/free_energy.py) | [`test_free_energy`](../../tests/test_free_energy.py), [`test_simulation_free_energy`](../../tests/test_simulation_free_energy.py) | direct — total-correlation curve over pymdp sweep |
| `Geometry` | §7 (e/m-flatness, e-geodesic, Pythagorean) | [`lean/geometry`](../../src/lean/geometry.py) | [`test_geometry`](../../tests/test_geometry.py) | indirect — log-weight affineness witnessed on pymdp marginals |
| `Decomposition` | §5 (Theorem 5.1, the load-bearing identity) | [`lean/decomposition`](../../src/lean/decomposition.py) | [`test_decomposition`](../../tests/test_decomposition.py) | direct — RHS bundle terms recorded per-λ in `pymdp_free_energy_bundle.csv`; identity verified at λ = 0 baseline |
| `Spectral` | §8 (Schmidt rank, archetypes, TT) | [`lean/spectral`](../../src/lean/spectral.py) | [`test_spectral`](../../tests/test_spectral.py) | direct — Schmidt-rank discontinuity at λ = 0⁺ visible in `pymdp_joint_lambda_*.png` snapshots |
| `Heterogeneous` | §9 (Theorem 9.1, O(λ²) coupling tax) | [`lean/heterogeneous`](../../src/lean/heterogeneous.py) | [`test_heterogeneous`](../../tests/test_heterogeneous.py) | indirect — analytic curve plotted alongside pymdp empirical tax |
| `BernoulliToy` | §6 + App. C (closed-form K = 2) | [`lean/bernoulli_toy`](../../src/lean/bernoulli_toy.py) | [`test_bernoulli_toy`](../../tests/test_bernoulli_toy.py) | indirect — pymdp K = 2 Ising sweep is the empirical analog of the closed-form Bernoulli toy |
| `Monotonicity` | §12 (constructive sub-fragment) | (kernel-checked; no Python counterpart) | (compile-time) | — |
| `Constructive` | §12 (`CommScalar`-polymorphic boundary lemmas) | (realized in [`lean/decomposition`](../../src/lean/decomposition.py)) | (compile-time) | — |
| **`Convexity` (NEW round 2)** | §5.4 (Thm 5.6 convexity of F in λ); §11.3 (Prop 11.1 local concavity at λ = 0) | (witnesses fed by [`lean/bernoulli_toy.ising_free_energy_curve`](../../src/lean/bernoulli_toy.py); analytic Taylor fit) | [`test_witness_theorems`](../../tests/test_witness_theorems.py) | indirect — convexity of `pymdp_free_energy_bundle.vfe_total` over `PYMDP_SWEEP_LAMBDAS` |
| **`MarkovBlanket` (NEW round 2)** | §19.3 (Prop 19.3 Markov-blanket separation `sep = 1 − I(q)/H(q)`) | [`lean/free_energy.total_correlation`](../../src/lean/free_energy.py), [`lean/free_energy.shannon_entropy`](../../src/lean/free_energy.py) | [`test_free_energy`](../../tests/test_free_energy.py), [`test_witness_theorems`](../../tests/test_witness_theorems.py) | indirect — separation measure computed on the pymdp joint at every λ |
| **`SpectralWitnesses` (NEW round 3)** | §8.1 (Prop 8.2 Schmidt rank upper-semicontinuous in λ); §8.3 (Thm 8.3 sparsity-rank tradeoff) | (witnesses fed by [`lean/spectral.schmidt_rank`](../../src/lean/spectral.py) and [`lean/spectral.tensor_train_ranks`](../../src/lean/spectral.py); multi-K experiments via [`scripts/simulate_multi_k.py`](../../scripts/simulate_multi_k.py)) | [`test_spectral`](../../tests/test_spectral.py), [`test_witness_theorems`](../../tests/test_witness_theorems.py) | direct — the configured multi-K sweep exhibits the per-cut bond envelope numerically |
| **`ConnectionsWitnesses` (NEW round 3)** | §17.2 (Thm 17.1 hierarchical AIF as λ → ∞ limit); §17.3 (Prop 17.2 sophisticated-inference embedding) | (witnesses fed by [`lean/decomposition.free_energy_against_entangled_prior`](../../src/lean/decomposition.py) + [`simulation/inference.coupled_policy_posterior`](../../src/simulation/inference.py); long-horizon experiment via [`scripts/simulate_long_horizon.py`](../../scripts/simulate_long_horizon.py)) | [`test_witness_theorems`](../../tests/test_witness_theorems.py), [`test_long_horizon`](../../tests/test_long_horizon.py) | direct — configured `LONG_HORIZON_STEPS` rollout exhibits the steady-state concentration numerically |

A reader who wants to confirm a manuscript claim numerically can follow the **Python mirror** column to the analytical companion + its **test gate**.  A reader who wants to see the claim land in a real POMDP run follows the **pymdp grounding** column to the bundle / figure that records it. The two paths converge: at λ = 0 every analytical helper coincides bit-identically with the pymdp marginals (asserted by [`test_simulation_pymdp.py::test_coupled_policy_posterior_lambda_zero_is_outer_product`](../../tests/test_simulation_pymdp.py)).
