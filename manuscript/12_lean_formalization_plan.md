# Lean Formalization Plan

This section gives a phased, prioritized formalization roadmap for the FEP-Lean repository. The plan is designed for incremental development — each phase produces machine-checked artifacts that lock in the result and enable downstream proofs without revisiting earlier ones.

## Mathlib4 prerequisites (already available)

- `MeasureTheory.ProbabilityMeasure` and `PMF` for finite probability distributions.
- `MeasureTheory.Integral.Bochner` for expectations.
- `Mathlib.Probability.Entropy` for Shannon entropy.
- `Mathlib.Probability.Information.Kullback` for KL divergence.
- `Mathlib.LinearAlgebra.Matrix.Spectrum` and SVD-related machinery (limited; may need extension).
- `Mathlib.Analysis.Convex` for convexity arguments.

## Phase 1: Foundational types and operations

```lean
import Mathlib.Probability.Information.Kullback
import Mathlib.Probability.MassFunction
import Mathlib.LinearAlgebra.Matrix

namespace ActiveInference.PolicyEntanglement

variable (n : ℕ) (Π : Fin n → Type) [∀ k, Fintype (Π k)] [∀ k, DecidableEq (Π k)]

/-- The joint policy space. -/
def PolicySpace : Type := (k : Fin n) → Π k

/-- Joint distribution over the policy space. -/
abbrev JointDist := PMF (PolicySpace n Π)

/-- Mean-field (factorized) distribution. -/
abbrev MFDist := (k : Fin n) → PMF (Π k)

/-- Embedding of mean-field distribution into joint distribution. -/
def MFDist.toJoint (q : MFDist n Π) : JointDist n Π := PMF.product q

/-- Marginal of a joint distribution on stream k. -/
def JointDist.marginal (q : JointDist n Π) (k : Fin n) : PMF (Π k) := PMF.map (· k) q

/-- Marginals as mean-field distribution. -/
def JointDist.marginals (q : JointDist n Π) : MFDist n Π := fun k => q.marginal k

end ActiveInference.PolicyEntanglement
```

## Phase 2: Coupling and entangled prior

```lean
/-- Coupling potential: a real-valued function on joint policies. -/
def CouplingPotential := PolicySpace n Π → ℝ

/-- The λ-entangled prior. -/
noncomputable def entangledPrior
  (E : MFDist n Π) (J : CouplingPotential n Π) (λ : ℝ≥0) : JointDist n Π :=
  let unnormalized : PolicySpace n Π → ℝ≥0 :=
    fun π => (∏ k, E k (π k)) * Real.exp (λ * J π) -- needs careful coercion
  ⟨unnormalized.normalize, by sorry /- normalization proof -/⟩
```

## Phase 3: Information-theoretic quantities

```lean
/-- Total correlation (multi-information). -/
noncomputable def totalCorrelation (q : JointDist n Π) : ℝ :=
  (∑ k, entropy (q.marginal k)) - entropy q

/-- Variational free energy under a joint distribution and EFE. -/
noncomputable def freeEnergy
  (q : JointDist n Π) (E : JointDist n Π) (G : PolicySpace n Π → ℝ) (γ : ℝ) : ℝ :=
  γ * (q.expectation G) - q.expectation (Real.log ∘ E.pmf) - entropy q
```

## Phase 4: Core lemmas (Theorems 4.1, 4.2, 6.1–6.4)

Targeted theorems, in dependency order:

```lean
/-- (Prop 6.2) Marginalization is the m-projection onto the MF submanifold. -/
theorem marginalization_eq_m_projection (q : JointDist n Π) :
  ∀ p : MFDist n Π, klDiv q (p.toJoint) ≥ klDiv q (q.marginals.toJoint) := sorry

/-- (Prop 6.3) Total correlation = KL to the m-projection. -/
theorem totalCorrelation_eq_kl_to_marginals (q : JointDist n Π) :
  totalCorrelation q = klDiv q (q.marginals.toJoint) := sorry

/-- Mean-field iff zero total correlation. -/
theorem mf_iff_zero_totalCorrelation (q : JointDist n Π) :
  (∃ p : MFDist n Π, q = p.toJoint) ↔ totalCorrelation q = 0 := sorry

/-- (Theorem 4.1) Entanglement decomposition of free energy. -/
theorem entanglement_decomposition
  (q : JointDist n Π) (E : MFDist n Π) (G : (k : Fin n) → Π k → ℝ)
  (J K_c : CouplingPotential n Π) (γ λ : ℝ) :
  freeEnergy q (entangledPrior E J λ) (fun π => (∑ k, G k (π k)) + λ * K_c π) γ =
    (∑ k, freeEnergyMarginal (q.marginal k) (E k) (G k) γ) +
    λ * (γ * q.expectation K_c - q.expectation J) -
    totalCorrelation q := by sorry

/-- (Theorem 6.4) The λ-family is an e-geodesic. -/
theorem entangledPosterior_e_geodesic
  (E : MFDist n Π) (G : (k : Fin n) → Π k → ℝ) (J K_c : CouplingPotential n Π) :
  ∀ π, ∃ a b : ℝ, ∀ λ,
    Real.log (entangledPosterior E G J K_c λ π) = a + b * λ + normalizer λ := sorry
```

## Phase 5: Spectral results (Schmidt rank, K=2)

For $K = 2$, formalize the Schmidt decomposition and prove:

```lean
/-- For K = 2, the Schmidt rank of q. -/
noncomputable def schmidtRank (q : JointDist 2 Π) : ℕ := sorry  -- via matrix SVD

/-- (Prop 7.1) Schmidt rank 1 iff mean-field. -/
theorem schmidtRank_one_iff_mf (q : JointDist 2 Π) :
  schmidtRank q = 1 ↔ ∃ p : MFDist 2 Π, q = p.toJoint := sorry
```

## Phase 6: Heterogeneous bound ([[THMREF:thm_8_1]])

Formalize the $O(\lambda^2)$ suboptimality bound for VFE-only streams. This requires:

- A formalization of one-step gradient descent on free energy.
- The coordinate-descent step in coupled inference.
- Taylor expansion in $\lambda$.

This is the most involved phase — but it is the theorem that *justifies* mixed reflexive/planning architectures, and so is worth the effort.

## Phase 0 (achieved): Mathlib-free boundary fragment

The full boundary fragment compiles on stock Lean 4 v4.29.0 with no
Mathlib dependency and **16/16 lake jobs green**.  Per-module surface
is summarised in the table below, and *two* constructive sub-fragments
exercise the boundary skeleton without a single `sorry`:

* **`Monotonicity.lean`** — 16 structural lemmas covering λ=0
  reductions, stream classification, pure-mode coupling-tax
  invariants, and structural identities on the spectral and
  coupling-norm constants.
* **`Constructive.lean`** — 14 complementary lemmas covering
  stream-mode totality, λ=γ=0 collapse of the posterior log-weight,
  coupling-norm structural identities, spectral / TT-rank boundary
  identities, and pure-mode coupling-tax composition.

Both modules are proved by definitional unfolding plus
`rfl` / `decide` / `native_decide` / case analysis, demonstrating
that the boundary skeleton supports *non-vacuous* structural reasoning
even before Mathlib lands.  The decidability instances added to
`Basic.lean` (`Decidable (IsPlanningStream …)`,
`Decidable (IsReflexiveStream …)`) make stream-mode classification
computable in the kernel.

Implementation status as of `lean/ActinfPolicyEntanglement/`,
Lean 4 v4.29.0:

| Module | Theorems / definitions | Sorries |
|---|---|---|
| `Basic` | `InferenceMode`, `CouplingPhase`, `CouplingRole`, `CouplingVerdict`, `StreamIdx`, `IsPlanningStream`, `IsReflexiveStream`, `stream_classification` | 0 |
| `JointDist` | `PolicySpace`, `JointDist`, `MFDist`, `IsPMF`, `MFDist.toJoint`, `IsMeanField`, `JointDist.marginal{,s}`, `mf_roundtrip_sketch`, `mf_implies_marginalization_recovery` | 0 |
| `Coupling` | `CouplingPotential`, `LabelledCoupling`, `trivialCoupling`, `entangledPriorLogWeight`, `entangledPosteriorLogWeight`, `entangledPosterior_logWeight_affine_in_lambda`, `entangledPrior_at_zero`, `entangledPosterior_at_zero` | 3 (Float arithmetic — Mathlib-deferred) |
| `FreeEnergy` | `shannonEntropy`, `klDivergence`, `jointEntropy`, `marginalEntropy`, `totalCorrelation`, `freeEnergy`, `marginalFreeEnergy`, `totalCorrelation_nonneg`, `meanField_iff_totalCorrelation_eq_zero`, `totalCorrelation_eq_kl_to_mprojection` | 1 |
| `Geometry` | `InMeanFieldSubmanifold`, `mfSubmanifold_eFlat`, `mProjection`, `mProjection_minimises_kl`, `entangledFamily_eGeodesic`, `dualFlat_pythagorean_sketch`, `revertibility` | 0 |
| `Spectral` | `Bipartite.schmidtRank`, `entanglementEntropy`, `schmidtRank_one_iff_meanField`, `schmidtRank_upperSemicontinuous_sketch`, `tensorTrainRanks`, `entanglementSpectrum`, `Archetype`, `sparsityRank_tradeoff` | 1 |
| `Heterogeneous` | `StreamModes`, `IsPurelyReflexive`, `IsPurelyPlanning`, `IsHeterogeneous`, `couplingNormSq`, `couplingTax`, `couplingTax_nonneg`, `couplingTax_quadratic_bound` ([[THMREF:thm_8_1]]), `couplingTax_small_lambda_tolerance`, `couplingTax_purelyReflexive`, `couplingTax_purelyPlanning` | 2 |
| `BernoulliToy` | `Action`, `binaryFactor`, `BinaryJoint`, `BinaryMF`, `alignedIndicator`, `isingCoupling`, `floatExp`, `floatLog`, `floatLogistic`, `binaryEntropy`, `isingMutualInformation`, `isingMI_zero_at_zero`, `optimalLambda`, `isingFreeEnergyCurve`, `lambdaC1`, `lambdaC2`, `couplingPhaseAt`, `isingFreeEnergyCurve_total` | 0 |
| `Decomposition` | `sumMarginalFreeEnergies`, `couplingCostTerm`, `couplingPriorTerm`, `totalCorrelationGain`, `entanglementDecompositionRHS`, `entanglement_decomposition` (**[[THMREF:thm_4_1]]**), `couplingVerdict`, `decomposition_at_zero`, `strict_gain_iff_nonMeanField` | 4 |
| `Monotonicity` (new) | `entangledPriorLogWeight_at_zero_eq_zero`, `entangledPosteriorLogWeight_at_zero`, `trivialCoupling_eq_zero`, `entangledPriorLogWeight_trivialCoupling`, `couplingTax_purelyReflexive_anyParams`, `couplingTax_purelyPlanning_anyParams`, `stream_classification_decidable`, `reflexive_not_planning`, `planning_not_reflexive`, `couplingNormSq_trivial`, `couplingNormSq_nonneg_boundary`, `schmidtRank_boundary_eq_one`, `tensorTrainRanks_boundary_eq_one`, `totalCorrelation_boundary_eq_zero`, `totalCorrelationGain_boundary`, `posterior_unfolds_at_zero_gamma` | **0** (constructive, no Mathlib) |

Total: ~80 declarations, 11 sorries — *all* Mathlib-deferred (Real
arithmetic, KL chain rule, SVD).  The new `Monotonicity` module
proves 16 structural lemmas constructively to demonstrate that the
boundary skeleton is non-vacuous: stream classification, λ=0
reductions, pure-mode coupling-tax invariants, and structural
identities on the spectral / coupling-norm constants all hold by
definitional unfolding.

## Estimate of effort

- Phase 1: 1–2 weeks (mostly reuses mathlib).
- Phase 2: 2–3 weeks (normalization proofs are tedious but routine).
- Phase 3: 2 weeks (entropy/KL on PMF is well-supported).
- Phase 4: 4–6 weeks (the core decomposition theorems).
- Phase 5: 4–8 weeks (Schmidt machinery may need new mathlib contributions).
- Phase 6: 6–12 weeks (Taylor expansion in measure-theoretic setting is delicate).

**Total: approximately 6 months of focused effort** for an experienced Lean contributor. The decomposition theorem ([[THMREF:thm_4_1]]) is achievable as a first standalone result in roughly 8–10 weeks. We propose this as the *first-publishable-result* milestone for the FEP-Lean repository.

---
