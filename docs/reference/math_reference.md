# Mathematical reference

*Latest generated audit.*  The historical round-3 pass graduated
the four remaining `deferred` theorems (`prop_7_2`, `thm_7_3`,
`thm_11_1`, `prop_11_2`) to `witness` status via two new modules
`SpectralWitnesses.lean` and `ConnectionsWitnesses.lean`; the
spectral / TT and §17 connection identities are now all live in the
boundary fragment.

A glossary of the formal objects used in the framework, with the Lean
type, the Python representation, and the manuscript section that
introduces each.  See [`../manuscript/2B_setup.md`](../../manuscript/2B_setup.md)
for the canonical definitions in prose.

> **Sign conventions.** The free energy `F`, the expected free energy
> `G`, and the preference potential `K_c` are all sign-sensitive — the
> standard active-inference convention treats `G` as a *cost* and `F`
> as a *bound to minimize*, but a few historically common
> alternatives flip a sign or two. The single source of truth for
> which convention this project uses (in prose, equations, Python,
> and Lean) is **§S6.1** in
> [`manuscript/S06_notation_and_concordance.md`](../../manuscript/S06_notation_and_concordance.md)
> (anchor: [`notation.sign_conventions`](../../manuscript/S06_notation_and_concordance.md#sign-conventions-secnotationsignconventions)).
> Manuscript prose cross-references that subsection via
> `[[SECREF:notation.sign_conventions]]` (used in §3, §5, and §7).

## 1. Policy spaces

| Object | Meaning | Lean | Python |
|---|---|---|---|
| `K : ℕ` | Number of streams | `K : Nat` | `q.ndim` |
| `Π^k` | Per-stream policy factor | `Pol k : Type` | `q.shape[k]` |
| `Π = ∏_k Π^k` | Joint policy space | `PolicySpace K Pol` | implicit (the joint ndarray axes) |

## 2. Distributions

| Object | Meaning | Lean | Python |
|---|---|---|---|
| `q(π)` | Joint distribution | `JointDist K Pol` | `np.ndarray` of shape `(|Π¹|, …, |Π^K|)` |
| `q^k(π^k)` | Per-stream marginal | —  (manuscript-level; no boundary decl) | `joint_marginal(q, k)` |
| `(q^1, …, q^K)` | All marginals (m-projection bundle) | —  (manuscript-level; no boundary decl) | `joint_marginals(q)` |
| `m(π) = ∏_k m_k(π^k)` | Mean-field joint from marginals | `JointDist.mfToJoint m` | `mean_field_to_joint([m1,…,mK])` |
| `IsMeanField q` | `q` factorizes | `IsMeanField q : Prop` | `is_mean_field(q)` |
| `m-proj(q)` | m-projection of `q` | `JointDist.mfToJoint` (factors are manuscript-level) | `m_projection(q)` |

## 3. Coupling potentials

| Object | Meaning | Lean | Python |
|---|---|---|---|
| `J(π)` | Habit (prior-side) potential | `CouplingPotential K Pol` | `np.ndarray` (joint shape) |
| `K_c(π)` | Preference (EFE-side) potential | `CouplingPotential K Pol` | `np.ndarray` (joint shape) |
| Trivial coupling | Zero everywhere | `trivialCoupling` | `trivial_coupling(shape)` |
| Labeled coupling | `J` or `K_c` tagged with role | `LabelledCoupling { potential, role }` | (no Python analog today) |

## 4. λ-entangled distributions

Manuscript §4.2:

* **Prior**: `E_λ(π) ∝ (∏_k E_k(π^k)) · exp(λ · J(π))`.
* **Posterior**: `q_λ(π) ∝ E_λ(π) · exp(-γ · (∑_k G_k(π^k) + λ · K_c(π)))`.

| Operation | Lean | Python |
|---|---|---|
| Prior log-weight | `entangledPriorLogWeight E J λ π` | `coupling_log_weight(J, Kc, γ, λ)` (subset) |
| Posterior log-weight | `entangledPosteriorLogWeight E G J K_c γ λ π` | (computed inside `entangled_posterior`) |
| Normalized prior | (Mathlib-refinement payload) | `entangled_prior(mf, J, λ)` |
| Normalized posterior | (Mathlib-refinement payload) | `entangled_posterior(mf, G, J, K_c, γ, λ)` |

## 5. Information-theoretic quantities

| Object | Definition | Lean | Python |
|---|---|---|---|
| `H(p)` | Shannon entropy | `FreeEnergy.shannonEntropy` (boundary) | `shannon_entropy(p)` |
| `D_KL(q ‖ p)` | KL divergence | `FreeEnergy.kl` (boundary) | `kl_divergence(q, p)` |
| `H(q)` | Joint entropy | `FreeEnergy.shannonEntropy` (applied to the joint) | `joint_entropy(q)` |
| `H(q^k)` | Marginal entropy | `FreeEnergy.shannonEntropy` (applied to a marginal; no dedicated decl) | `marginal_entropy(q, k)` |
| `I(q) = ∑_k H(q^k) − H(q)` | Total correlation | `totalCorrelation` (boundary) | `total_correlation(q)` |
| `I(q) = D_KL(q ‖ ∏ q^k)` | Total correlation via KL | `totalCorrelation_eq_kl_to_mprojection` (theorem) | `total_correlation_via_kl(q)` |

## 6. Free energies

| Object | Definition | Lean | Python |
|---|---|---|---|
| `F[q]` | Variational free energy: `γ·𝔼[G] − 𝔼[log E] − H(q)` | `FreeEnergy.variationalFreeEnergy` | `free_energy(q, prior, G, γ)` |
| `F[q^k]` | Per-stream marginal free energy | `marginalFreeEnergy q E G γ k` | `marginal_free_energy(q, mf, G, γ, k)` |

## 7. Geometry

| Concept | Statement | Lean | Python |
|---|---|---|---|
| Mean-field submanifold `ℳ_MF` is e-flat (Prop 7.1) | log-mixtures of MF stay in MF up to log Z | `mfImage_isMeanField` | (predicate) |
| m-projection minimizes KL (Prop 7.2) | `KL(q ‖ mfToJoint m) = KL(q ‖ q)` when `q = mfToJoint m` | `mProjection_kl_eq_self_when_meanfield` | `m_projection_minimises_kl(q, p)` |
| Total correlation = KL to m-projection (Prop 7.3) | `I(q) = D_KL(q ‖ ∏ q^k)` | `totalCorrelation_eq_kl_to_mprojection` | `total_correlation_via_kl` |
| {q_λ} is e-geodesic (Theorem 7.4) | log-weight is affine in λ | `entangledFamily_eGeodesic` (polymorphic over `[CommScalar α]`) | `is_e_geodesic` |
| Pythagorean (Prop 7.5) | `KL(q ‖ ref) = I(q) + KL(m-proj(q) ‖ ref)` | `dualFlat_pythagorean_witness` (witness form) | `pythagorean_residual` |
| Revertibility | m-projection always lands in `ℳ_MF` | — (Python witness: lean.geometry.revertibility; no boundary decl) | `revertibility(q)` |

## 8. Spectral / tensor-network

| Concept | Statement | Lean | Python |
|---|---|---|---|
| Schmidt rank | `# {s_α : s_α > 0}` of SVD of `q ∈ Π¹×Π²` | (Mathlib-refinement payload; numerical witness via `schmidt_rank`) | `schmidt_rank(q)` |
| Bipartite mean-field factorization (Prop 8.1) | `q π¹ π² = u(π¹)·v(π²)` ↔ `IsBipartiteMeanField q` | `Bipartite.isBipartiteMeanField_factors` (forward), `Bipartite.factors_isBipartiteMeanField` (converse) | `schmidt_rank_one_iff_mean_field` |
| Schmidt-rank upper-semicontinuity in λ (Prop 8.2, round-3 witness) | `r(λ) ≤ liminf_{λ' → λ} r(λ')` with `r(0) = 1` anchor | `SpectralWitnesses.schmidtRank_upperSemicontinuous_witness` + `UpperSemicontinuousRankWitness` | `schmidt_rank(q)` (numerical) + `simulate_multi_k.py` |
| Entanglement entropy | `−∑ p_α log p_α` with `p_α = s_α² / ∑ s²` | (Mathlib-refinement payload; numerical witness via `entanglement_entropy`) | `entanglement_entropy` |
| Archetype | `(weight, u_α, v_α)` triple | (witness-form via `Spectral.Bipartite`; full algebra is a Mathlib-refinement payload) | `dataclass Archetype` |
| Tensor-train ranks | Bond dim across each cut | (Mathlib-refinement payload; numerical witness via `tensor_train_ranks`) | `tensor_train_ranks` |
| Sparsity-rank tradeoff (Thm 8.3, round-3 witness) | Per-cut bond bound `bond_bound k ≥ cut_rank k` envelope | `SpectralWitnesses.sparsityRank_tradeoff_witness` + `SparsityRankEnvelope` | `tensor_train_ranks(q)` (numerical) + `simulate_multi_k.py` |

## 9. Heterogeneous ensembles

| Concept | Statement | Lean | Python |
|---|---|---|---|
| Stream mode | Planning vs. reflexive (by horizon) | `IsPlanningStream`, `IsReflexiveStream` (with `instDecidableIsPlanningStream`, `instDecidableIsReflexiveStream`) | `enum InferenceMode` |
| Mode trichotomy | Every stream is exactly planning or reflexive | `stream_classification` (theorem) | `is_purely_reflexive`, `is_purely_planning`, `is_heterogeneous` |
| Coupling tax | KL divergence between fully-adaptive and pinned posteriors | `couplingTax` | `coupling_tax` |
| `‖K_c‖²` | Coupling norm | `couplingNormSq_of_trivialCoupling` (theorem; no standalone def) | `coupling_norm_sq` |
| **Theorem 9.1**: tax ≤ C · λ² · ‖K_c‖² | O(λ²) envelope | `couplingTax_quadratic_bound` | `coupling_tax_within_quadratic_bound` |

## 10. K=2 Ising worked example

| Concept | Lean | Python |
|---|---|---|
| Coupling | `isingCoupling` | `ising_coupling()` |
| Closed-form MI: `log 2 − H_b(σ(λ))` | `isingMutualInformation` | `ising_mutual_information(λ)` |
| Empirical MI from posterior | (verified by tests) | `empirical_mutual_information(λ)` |
| Optimal coupling: `λ* = 2·arctanh(Δ/Δmax)` | `optimalLambda` | `optimal_lambda(δ, δmax)` |
| Free-energy curve | `isingFreeEnergyCurve` | `ising_free_energy_curve(λ, utility)` |
| Phase from `λ` | `couplingPhaseAt` | `coupling_phase_at(λ, λc1, λc2)` |

## 11. Convexity and local concavity (NEW, round 2)

| Concept | Statement | Lean | Python |
|---|---|---|---|
| **Theorem 5.6**: `F[q_λ]` is convex in λ (witness form) | `F_curve(t·λ₁ + (1−t)·λ₂) ≤ t·F_curve(λ₁) + (1−t)·F_curve(λ₂)` | `Convexity.FreeEnergyConvexityWitness`, `Convexity.freeEnergy_convex_in_lam_witness` | `bernoulli_toy.ising_free_energy_curve` (closed-form convex curve at K=2) |
| **Prop 11.1**: Taylor-form local concavity of `F[q_λ]` at λ = 0 | `F_curve(λ) ≤ a₀ + a₁·λ + a₂·λ² + C·λ³` for `λ ∈ [0, ε]` with `a₂ ≤ 0` and `ε > 0` | `Convexity.LocalConcavityAtZero`, `Convexity.freeEnergy_localConcavity_at_zero_witness` | analytic Taylor fit; consumed by `tests/test_witness_theorems.py` |
| First derivative of `F` along the family | `dF/dλ = ⟨J⟩_E − ⟨J⟩_q + γ·⟨K_c⟩_q` (see `[[EQ:dF_dlambda]]`) | (analytic; expressed in manuscript) | implicit in `decomposition.entanglement_decomposition_rhs` |
| Second derivative (Fisher form) | `d²F/dλ² = Var_E(J) − Var_q(J − γ·K_c)` (see `[[EQ:d2F_dlambda2]]`) | (analytic; expressed in manuscript) | numerical second-difference of `ising_free_energy_curve` |

## 12. Markov-blanket separation (NEW, round 2)

| Concept | Statement | Lean | Python |
|---|---|---|---|
| **Prop 19.3**: Markov-blanket separation measure | `sep(q) = 1 − I(q) / H(q)` with `H(q) > 0`; saturates at 1 when `q` is mean-field, shrinks to 0 as coupling tightens | `MarkovBlanket.MarkovBlanketSeparationWitness`, `MarkovBlanket.markovBlanket_separation_identity_witness` | composition of `free_energy.total_correlation(q) / free_energy.shannon_entropy(q.flatten())` |
| Witness tie-ins | `Hq = shannonEntropy q s ∧ Iq = totalCorrelation q s sumStreamEntropies ∧ Iq ≥ 0 ∧ sep = 1 − Iq/Hq` | `MarkovBlanketSeparationWitness.{Hq_eq, Iq_eq, Iq_nonneg, sep_eq}` | numerical agreement at floating tolerance (`tests/test_witness_theorems.py`) |

The Markov-blanket separation is a *dimensionless* invariant of the
joint policy posterior: `sep = 1` corresponds to a fully mean-field
joint (the internal-external statistical separation is *complete*),
while `sep → 0` corresponds to the maximally-coupled regime in which
internal and external dynamics share all their information.

## 13. Hierarchical-AIF and sophisticated-inference embeddings (NEW, round 3)

| Concept | Statement | Lean | Python |
|---|---|---|---|
| **Theorem 17.1**: Hierarchical AIF as `λ → ∞` limit (witness form) | For every `ε > 0` there exists `λ₀ > 0` such that `λ ≥ λ₀ ⇒ kl (qFamily λ) q_∞ s ≤ ε` (concentration onto a hierarchical-AIF limit posterior) | `ConnectionsWitnesses.HierarchicalConcentrationWitness`, `ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness` | `decomposition.free_energy_against_entangled_prior` over `simulate_long_horizon.py`; the configured `LONG_HORIZON_STEPS` rollout emits `long_horizon_steady_state_kl` as the empirical concentration envelope |
| **Prop 17.2**: Sophisticated-inference embedding (witness form) | A sophisticated-inference source embeds into `JointDist K Pol` with VFE preserved on the embedded image | `ConnectionsWitnesses.SophisticatedInferenceEmbedding`, `ConnectionsWitnesses.sophisticatedInference_embedding_witness` | `simulation.inference.coupled_policy_posterior` — numerical coupled-policy posterior under λ-deformation |

Round 3 closes the four originally-deferred §8 / §17 theorems via two
new Lean submodules (`SpectralWitnesses.lean`, `ConnectionsWitnesses.lean`),
all Mathlib-free and in witness form.  See
[`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
for the payload-discharge plan.

## 14. Multi-K, long-horizon, and revertibility variables (NEW, round 3)

Derived variables emitted by the simulation scripts and
injected into the manuscript via `[[VAR:...]]` tokens:

| Variable | Source | Meaning |
|---|---|---|
| `multi_information_K3_lambda_2` | `simulate_multi_k.py` (K=3 sentinel) | Multi-information `I(q_λ)` at the configured K=3 sentinel λ |
| `multi_information_K4_lambda_2` | `simulate_multi_k.py` (K=4 sentinel) | Multi-information `I(q_λ)` at the configured K=4 sentinel λ |
| `multi_information_K5_lambda_2` | `simulate_multi_k.py` (K=5 sentinel) | Multi-information `I(q_λ)` at the configured K=5 sentinel λ |
| `long_horizon_steady_state_kl` | `simulate_long_horizon.py` | Backward-compatible headline for the strict max tail-window KL, computed as $D_{\mathrm{KL}}(q_t^k\|\bar q^k_{\mathrm{tail}})$ over the trailing window |
| `long_horizon_adjacent_kl_max` | `simulate_long_horizon.py` | Separately reported adjacent-step KL $D_{\mathrm{KL}}(q_t^k\|q_{t-1}^k)$, not used as the habit criterion |
| `long_horizon_habit_accumulation` | `simulate_long_horizon.py` | Confirms habit accumulation criterion satisfied |
| `revertibility_max_kl_residual` | `simulate_revertibility.py` | Max residual of `D_KL(q ‖ m-proj(q)) − I(q)` across the configured sweep — round-trip identity |
| `revertibility_max_marginal_diff` | `simulate_revertibility.py` | Max L∞ deviation of `m-proj(q)`'s marginals from `q`'s marginals — confirms m-projection preserves marginals |
| `revertibility_all_revertible` | `simulate_revertibility.py` | Every configured λ probe round-trips through m-projection cleanly |
| `robustness_decomposition_residual_max` | `simulate_robustness.py` | Max decomposition residual across one-axis robustness scenarios |
| `coupling_ablation_null_tc_max` | `simulate_robustness.py` | Null-coupling flatline sentinel for the ablation suite |
| `long_horizon_replicate_habit_pass_rate` | `simulate_robustness.py` | Fraction of configured long-horizon replicate seeds satisfying the habit criterion |

Numerical witnesses for the round-3 graduations live in
[`tests/test_multi_k_experiments.py`](../../tests/test_multi_k_experiments.py),
[`tests/test_long_horizon.py`](../../tests/test_long_horizon.py), and
[`tests/test_revertibility.py`](../../tests/test_revertibility.py).
