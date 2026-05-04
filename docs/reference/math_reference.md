# Mathematical reference

A glossary of the formal objects used in the framework, with the Lean
type, the Python representation, and the manuscript section that
introduces each.  See [`../manuscript/02_setup_and_assumptions.md`](../../manuscript/02_setup_and_assumptions.md)
for the canonical definitions in prose.

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
| `q^k(π^k)` | Per-stream marginal | `JointDist.marginal q k` | `joint_marginal(q, k)` |
| `(q^1, …, q^K)` | All marginals (m-projection bundle) | `JointDist.marginals q` | `joint_marginals(q)` |
| `m(π) = ∏_k m_k(π^k)` | Mean-field joint from marginals | `MFDist.toJoint m` | `mean_field_to_joint([m1,…,mK])` |
| `IsMeanField q` | `q` factorises | `IsMeanField q : Prop` | `is_mean_field(q)` |
| `m-proj(q)` | m-projection of `q` | `JointDist.marginals q` ▸ `MFDist.toJoint` | `m_projection(q)` |

## 3. Coupling potentials

| Object | Meaning | Lean | Python |
|---|---|---|---|
| `J(π)` | Habit (prior-side) potential | `CouplingPotential K Pol` | `np.ndarray` (joint shape) |
| `K_c(π)` | Preference (EFE-side) potential | `CouplingPotential K Pol` | `np.ndarray` (joint shape) |
| Trivial coupling | Zero everywhere | `trivialCoupling` | `trivial_coupling(shape)` |
| Labelled coupling | `J` or `K_c` tagged with role | `LabelledCoupling { potential, role }` | (no Python analogue today) |

## 4. λ-entangled distributions

Manuscript §3.2:

* **Prior**: `E_λ(π) ∝ (∏_k E_k(π^k)) · exp(λ · J(π))`.
* **Posterior**: `q_λ(π) ∝ E_λ(π) · exp(-γ · (∑_k G_k(π^k) + λ · K_c(π)))`.

| Operation | Lean | Python |
|---|---|---|
| Prior log-weight | `entangledPriorLogWeight E J λ π` | `coupling_log_weight(J, Kc, γ, λ)` (subset) |
| Posterior log-weight | `entangledPosteriorLogWeight E G J K_c γ λ π` | (computed inside `entangled_posterior`) |
| Normalised prior | (Phase 7) | `entangled_prior(mf, J, λ)` |
| Normalised posterior | (Phase 7) | `entangled_posterior(mf, G, J, K_c, γ, λ)` |

## 5. Information-theoretic quantities

| Object | Definition | Lean | Python |
|---|---|---|---|
| `H(p)` | Shannon entropy | `shannonEntropy` (boundary) | `shannon_entropy(p)` |
| `D_KL(q ‖ p)` | KL divergence | `klDivergence` (boundary) | `kl_divergence(q, p)` |
| `H(q)` | Joint entropy | `jointEntropy` | `joint_entropy(q)` |
| `H(q^k)` | Marginal entropy | `marginalEntropy` | `marginal_entropy(q, k)` |
| `I(q) = ∑_k H(q^k) − H(q)` | Total correlation | `totalCorrelation` (boundary) | `total_correlation(q)` |
| `I(q) = D_KL(q ‖ ∏ q^k)` | Total correlation via KL | `totalCorrelation_eq_kl_to_mprojection` (theorem) | `total_correlation_via_kl(q)` |

## 6. Free energies

| Object | Definition | Lean | Python |
|---|---|---|---|
| `F[q]` | Variational free energy: `γ·𝔼[G] − 𝔼[log E] − H(q)` | `freeEnergy q E G γ` | `free_energy(q, prior, G, γ)` |
| `F[q^k]` | Per-stream marginal free energy | `marginalFreeEnergy q E G γ k` | `marginal_free_energy(q, mf, G, γ, k)` |

## 7. Geometry

| Concept | Statement | Lean | Python |
|---|---|---|---|
| Mean-field submanifold `ℳ_MF` is e-flat (Prop 6.1) | log-mixtures of MF stay in MF up to log Z | `mfSubmanifold_eFlat` (sketch) | (predicate) |
| m-projection minimises KL (Prop 6.2) | `KL(q ‖ m-proj(q)) ≤ KL(q ‖ p)` ∀ MF `p` | `mProjection_minimises_kl` | `m_projection_minimises_kl(q, p)` |
| Total correlation = KL to m-projection (Prop 6.3) | `I(q) = D_KL(q ‖ ∏ q^k)` | `totalCorrelation_eq_kl_to_mprojection` | `total_correlation_via_kl` |
| {q_λ} is e-geodesic (Theorem 6.4) | log-weight is affine in λ | `entangledFamily_eGeodesic` | `is_e_geodesic` |
| Pythagorean (Prop 6.5) | `KL(q ‖ ref) = I(q) + KL(m-proj(q) ‖ ref)` | `dualFlat_pythagorean_sketch` | `pythagorean_residual` |
| Revertibility | m-projection always lands in `ℳ_MF` | `revertibility` | `revertibility(q)` |

## 8. Spectral / tensor-network

| Concept | Statement | Lean | Python |
|---|---|---|---|
| Schmidt rank | `# {s_α : s_α > 0}` of SVD of `q ∈ Π¹×Π²` | `Bipartite.schmidtRank` | `schmidt_rank(q)` |
| Schmidt rank 1 ⇔ MF (Prop 7.1) | Bipartite rank-1 ↔ outer-product | `schmidtRank_one_iff_meanField` | `schmidt_rank_one_iff_mean_field` |
| Entanglement entropy | `−∑ p_α log p_α` with `p_α = s_α² / ∑ s²` | `Bipartite.entanglementEntropy` | `entanglement_entropy` |
| Archetype | `(weight, u_α, v_α)` triple | `structure Archetype` | `dataclass Archetype` |
| Tensor-train ranks | Bond dim across each cut | `tensorTrainRanks` | `tensor_train_ranks` |

## 9. Heterogeneous ensembles

| Concept | Statement | Lean | Python |
|---|---|---|---|
| Stream mode | VFE / EFE / sophisticated | `InferenceMode` | `enum InferenceMode` |
| Pure / heterogeneous | All same / mixed | `IsPurelyReflexive`, `IsPurelyPlanning`, `IsHeterogeneous` | `is_purely_reflexive`, `is_purely_planning`, `is_heterogeneous` |
| Coupling tax | KL divergence between fully-adaptive and pinned posteriors | `couplingTax` | `coupling_tax` |
| `‖K_c‖²` | Coupling norm | `couplingNormSq` | `coupling_norm_sq` |
| **Theorem 8.1**: tax ≤ C · λ² · ‖K_c‖² | O(λ²) envelope | `couplingTax_quadratic_bound` | `coupling_tax_within_quadratic_bound` |

## 10. K=2 Ising worked example

| Concept | Lean | Python |
|---|---|---|
| Coupling | `isingCoupling` | `ising_coupling()` |
| Closed-form MI: `log 2 − H_b(σ(λ))` | `isingMutualInformation` | `ising_mutual_information(λ)` |
| Empirical MI from posterior | (verified by tests) | `empirical_mutual_information(λ)` |
| Optimal coupling: `λ* = 2·arctanh(Δ/Δmax)` | `optimalLambda` | `optimal_lambda(δ, δmax)` |
| Free-energy curve | `isingFreeEnergyCurve` | `ising_free_energy_curve(λ, utility)` |
| Phase from `λ` | `couplingPhaseAt` | `coupling_phase_at(λ, λc1, λc2)` |
