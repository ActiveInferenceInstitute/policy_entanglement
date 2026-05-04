# Manuscript ↔ code ↔ docs map

A canonical lookup table that, for every section of the manuscript,
points to (a) the Lean module that formalises its claims, (b) the
Python module that computes them, (c) the test file that verifies
them, and (d) the docs page that explains them in technical depth.

This is the navigation index for the project: from a single
manuscript citation, you can find every artefact in two clicks.

## Body sections

| Manuscript | Lean | Python | Tests | Docs |
|---|---|---|---|---|
| [§1 Motivation](../../manuscript/01_motivation_and_position.md) | — | — | — | [`architecture.md`](architecture.md) |
| [§2 Setup, notation](../../manuscript/02_setup_and_assumptions.md) | [`Basic`](../../lean/ActinfPolicyEntanglement/Basic.lean), [`JointDist`](../../lean/ActinfPolicyEntanglement/JointDist.lean) | [`lean/joint_dist`](../../src/lean/joint_dist.py) | [`test_joint_dist`](../../tests/test_joint_dist.py) | [`math_reference.md`](math_reference.md) |
| [§3 λ-deformation](../../manuscript/03_lambda_deformation.md) | [`Coupling`](../../lean/ActinfPolicyEntanglement/Coupling.lean) | [`lean/coupling`](../../src/lean/coupling.py) | [`test_coupling`](../../tests/test_coupling.py) | [`math_reference.md`](math_reference.md) §4 |
| [§4 Entanglement decomposition](../../manuscript/04_entanglement_decomposition.md) | [`Decomposition`](../../lean/ActinfPolicyEntanglement/Decomposition.lean), [`FreeEnergy`](../../lean/ActinfPolicyEntanglement/FreeEnergy.lean) | [`lean/decomposition`](../../src/lean/decomposition.py), [`lean/free_energy`](../../src/lean/free_energy.py) | [`test_decomposition`](../../tests/test_decomposition.py), [`test_free_energy`](../../tests/test_free_energy.py) | [`decomposition_theorem.md`](../modules/decomposition_theorem.md) |
| [§5 Examples](../../manuscript/05_examples_and_worked_cases.md) | [`BernoulliToy`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean) | [`lean/bernoulli_toy`](../../src/lean/bernoulli_toy.py) | [`test_bernoulli_toy`](../../tests/test_bernoulli_toy.py) | [`bernoulli_toy.md`](../modules/bernoulli_toy.md) |
| [§6 Information geometry](../../manuscript/06_information_geometry.md) | [`Geometry`](../../lean/ActinfPolicyEntanglement/Geometry.lean) | [`lean/geometry`](../../src/lean/geometry.py) | [`test_geometry`](../../tests/test_geometry.py) | [`information_geometry.md`](../modules/information_geometry.md) |
| [§7 Spectral / TT structure](../../manuscript/07_spectral_and_tensor_network.md) | [`Spectral`](../../lean/ActinfPolicyEntanglement/Spectral.lean) | [`lean/spectral`](../../src/lean/spectral.py) | [`test_spectral`](../../tests/test_spectral.py) | [`spectral_structure.md`](../modules/spectral_structure.md) |
| [§8 Heterogeneous ensembles](../../manuscript/08_heterogeneous_inference.md) | [`Heterogeneous`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean) | [`lean/heterogeneous`](../../src/lean/heterogeneous.py) | [`test_heterogeneous`](../../tests/test_heterogeneous.py) | [`heterogeneous_ensembles.md`](../modules/heterogeneous_ensembles.md) |
| [§9 Phase structure](../../manuscript/09_phase_structure.md) | [`BernoulliToy.couplingPhaseAt`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean) | [`lean/bernoulli_toy.coupling_phase_at`](../../src/lean/bernoulli_toy.py) | [`test_bernoulli_toy::test_coupling_phase_at_*`](../../tests/test_bernoulli_toy.py) | [`bernoulli_toy.md`](../modules/bernoulli_toy.md) |
| [§10 Comparative statics](../../manuscript/10_comparative_statics.md) | [`Decomposition.couplingVerdict`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) | [`lean/decomposition.coupling_pays_for_itself`](../../src/lean/decomposition.py), [`lean/geometry.coupling_pays_off`](../../src/lean/geometry.py) | [`test_decomposition`](../../tests/test_decomposition.py), [`test_geometry`](../../tests/test_geometry.py) | [`decomposition_theorem.md`](../modules/decomposition_theorem.md) |
| [§11 Connections (incl. pymdp)](../../manuscript/11_connections_to_existing_frameworks.md) | — | [`simulation/`](../../src/simulation/) (pymdp grounding) | [`test_simulation_*`](../../tests/) | [`pomdp_simulation.md`](../simulation/pomdp_simulation.md) |
| [§12 Lean formalization plan](../../manuscript/12_lean_formalization_plan.md) | All `ActinfPolicyEntanglement.*` + `Monotonicity` + `Constructive` | — | — | [`lean_reference.md`](lean_reference.md) |
| [§13 Empirical / simulation suite](../../manuscript/13_empirical_simulation_suite.md) | — | every `src/lean/*.py`, every `src/simulation/*.py` | every `tests/test_*.py` | [`testing.md`](../guides/testing.md), [`pomdp_simulation.md`](../simulation/pomdp_simulation.md), [`visualizations.md`](../simulation/visualizations.md) |
| [§14 Open questions](../../manuscript/14_open_theoretical_questions.md) | — | — | — | — |
| [§15 Outline](../../manuscript/15_companion_paper_outline.md) | — | — | — | this file |
| [§16 Discussion](../../manuscript/16_discussion_worldview.md) | — | — | — | [`architecture.md`](architecture.md) |
| [§17 Closing](../../manuscript/17_closing_remarks.md) | — | — | — | — |

## Appendices

| Manuscript | Maps to |
|---|---|
| [Appendix A — Full proof of Theorem 4.1](../../manuscript/S01_proof_of_decomposition_theorem.md) | [`decomposition_theorem.md`](../modules/decomposition_theorem.md), [`Decomposition.lean`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) |
| [Appendix B — Convexity of $F[q_\lambda]$](../../manuscript/S02_convexity_of_free_energy.md) | [`bernoulli_toy.md`](../modules/bernoulli_toy.md) §C.7 |
| [Appendix C — K=2 Bernoulli derivation](../../manuscript/S03_bernoulli_complete_derivation.md) | [`bernoulli_toy.md`](../modules/bernoulli_toy.md), [`BernoulliToy.lean`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean), [`lean/bernoulli_toy.py`](../../src/lean/bernoulli_toy.py) |
| [Appendix D — TT inference algorithm](../../manuscript/S04_tensor_train_inference_algorithm.md) | [`spectral_structure.md`](../modules/spectral_structure.md) |
| [Appendix E — Lean code skeleton](../../manuscript/S05_lean_code_skeleton.md) | [`lean_reference.md`](lean_reference.md), [`lean/`](../../lean/) |

## Theorems / propositions index

| Manuscript ID | Statement (short) | Lean | Python check |
|---|---|---|---|
| Prop 4.1 (Theorem 4.1) | Entanglement decomposition | `Decomposition.entanglement_decomposition` | `decomposition.entanglement_decomposition_rhs` |
| Cor 4.2 | Coupling pays for itself | `Decomposition.couplingVerdict` | `decomposition.coupling_pays_for_itself` |
| Cor 4.3 | Mean-field at λ = 0 | `Decomposition.decomposition_at_zero` | `test_decomposition::test_decomposition_consistency_at_zero_lambda` |
| Cor 4.4 | Strict gain ⇔ non-MF | `Decomposition.strict_gain_iff_nonMeanField` | (numerically: `total_correlation_gain` < 0) |
| Prop 6.1 | MF submanifold is e-flat | `Geometry.mfSubmanifold_eFlat` | (predicate: `is_mean_field`) |
| Prop 6.2 | m-projection minimises KL | `Geometry.mProjection_minimises_kl` | `geometry.m_projection_minimises_kl` |
| Prop 6.3 | I(q) = KL(q ‖ ∏ q^k) | `FreeEnergy.totalCorrelation_eq_kl_to_mprojection` | `free_energy.total_correlation_via_kl` |
| Theorem 6.4 | {q_λ} is e-geodesic | `Geometry.entangledFamily_eGeodesic`, `Coupling.couplingLogWeight_affine_in_lam` | `geometry.is_e_geodesic` |
| Prop 6.5 | Pythagorean | `Geometry.dualFlat_pythagorean_sketch` | `geometry.pythagorean_residual` |
| Prop 7.1 | Schmidt rank 1 ⇔ MF | `Spectral.Bipartite.schmidtRank_one_iff_meanField` | `spectral.schmidt_rank_one_iff_mean_field` |
| Prop 7.2 | Rank upper-semicontinuous in λ | `Spectral.Bipartite.schmidtRank_upperSemicontinuous_sketch` | (deferred to Phase 7) |
| Theorem 7.3 | Sparsity-rank tradeoff | `Spectral.sparsityRank_tradeoff` | (deferred to Phase 7) |
| Theorem 8.1 | O(λ²) coupling-tax bound | `Heterogeneous.couplingTax_quadratic_bound` | `heterogeneous.coupling_tax_within_quadratic_bound` |
| Cor 8.2 | Reflexive-stream tolerance | `Heterogeneous.couplingTax_small_lambda_tolerance` | (numerically: `coupling_tax` decreases) |
| Monotonicity | structural lemmas (Nat / Or / List / Fin) | `Monotonicity.*` (15 constructive theorems) | (kernel-checked, no Python counterpart needed) |
| Constructive | boundary lemmas at λ=0 / trivial coupling | `Constructive.*` (7 theorems, 5 proved by `rfl`) | (kernel-checked, no Python counterpart needed) |

## Figures

Generated by [`scripts/generate_figures.py`](../../scripts/generate_figures.py)
and [`scripts/simulate_pymdp.py`](../../scripts/simulate_pymdp.py).  Every
PNG is reproducible with `uv run python scripts/run_all.py`.

| Figure | Manuscript section(s) | Source function | Path |
|---|---|---|---|
| Closed-form vs empirical Ising MI | §5.1, §13 | `figure_ising_mi_curve` | `output/figures/ising_mi_curve.png` |
| Free-energy curve | §5.1, Appendix B, §13 | `figure_free_energy_curve` | `output/figures/free_energy_curve.png` |
| O(λ²) coupling tax | §8 (Theorem 8.1), §13 | `figure_coupling_tax_quadratic` | `output/figures/coupling_tax_quadratic.png` |
| 1-D phase diagram | §9, §13 | `figure_phase_diagram` | `output/figures/phase_diagram.png` |
| Optimal λ*(Δ) | §5.1, §10, §13 | `figure_optimal_lambda` | `output/figures/optimal_lambda.png` |
| Schmidt rank vs λ | §7.1 (Prop 7.1), §13 | `figure_schmidt_rank_vs_lambda` | `output/figures/schmidt_rank.png` |
| 2-D phase landscape `F(λ, util)` | §9, §13 | `figure_phase_landscape` | `output/figures/phase_landscape.png` |
| Schmidt entropy surface | §7, §13 | `figure_schmidt_entropy_surface` | `output/figures/schmidt_entropy_surface.png` |
| Joint heatmap with marginals (λ=2) | §5.1, §13 | `figure_joint_heatmap_with_marginals` | `output/figures/joint_heatmap_lambda2.png` |
| Archetype dendrogram | §7.2, §13 | `figure_archetype_dendrogram` | `output/figures/archetype_dendrogram.png` |
| Tensor-train rank surface | §7.3 (Theorem 7.3), §13 | `figure_tensor_train_ranks` | `output/figures/tensor_train_rank_surface.png` |
| Log-weight flow (e-geodesic) | §6 (Theorem 6.4), §13 | `figure_log_weight_flow` | `output/figures/log_weight_flow.png` |
| Coupling-potential graph | §11.12 (CEREBRUM), §13 | `figure_coupling_graph` | `output/figures/coupling_graph.png` |
| pymdp total correlation curve | §11.1 (pymdp), §13 | `simulate_pymdp.figure_pymdp_lambda_sweep` | `output/figures/pymdp_total_correlation_curve.png` |
| pymdp joint posterior at λ=0 / 2 / 4 | §13 | `simulate_pymdp.figure_pymdp_lambda_sweep` | `output/figures/pymdp_joint_lambda_*.png` |
| pymdp coupled rollout (T=10) | §11.1 (pymdp), §13 | `simulate_pymdp.figure_pymdp_rollout` | `output/figures/pymdp_coupled_rollout.png` |
| KL geodesic in the 2-D summary plane | §6 (Theorem 6.4), §13 | `figure_kl_geodesic_in_simplex` | `output/figures/kl_geodesic_simplex.png` |
| λ⋆(utility, γ) locus | §10, §13 | `figure_lambda_star_locus` | `output/figures/lambda_star_locus.png` |

## Manuscript-substituted variables

`scripts/manuscript_variables.py` writes
[`output/data/manuscript_variables.json`](../../output/data/manuscript_variables.json)
with the in-text numeric substitutions:

| Key | Computed from | Manuscript usage |
|---|---|---|
| `ising_mi_at_lam_05` | `ising_mutual_information(0.5)` | §5.1 numerical example |
| `ising_mi_at_lam_1` | `ising_mutual_information(1.0)` | §5.1 numerical example |
| `ising_mi_at_lam_2` | `ising_mutual_information(2.0)` | §5.1 numerical example |
| `ising_mi_saturation` | `ising_mutual_information(50.0)` | §5.1 saturation check |
| `lambda_star_delta_05` | `optimal_lambda(0.5)` | §10 worked example |
| `lambda_star_delta_09` | `optimal_lambda(0.9)` | §10 worked example |
| `ising_S_E_at_lam_{0,1,3}` | `entanglement_entropy(ising_joint_posterior(λ))` | §7 numerical witnesses |
| `ising_schmidt_rank_at_lam_{0,1}` | `schmidt_rank(ising_joint_posterior(λ))` | §7.1 (Prop 7.1) check |
| `tt_ranks_K{2,3,4,5}` | `tensor_train_ranks(...)` for symmetric Ising K-stream | §7.3 (Theorem 7.3) check |
| `pymdp_total_correlation_lam_{0,1,2,4}` | `total_correlation(coupled_policy_posterior(...))` | §11.1, §13 (pymdp grounding) — only present when `sim` group installed |
