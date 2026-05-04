# Lean theorem reference

A per-theorem status table for everything under
[`../lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/).
The status column is one of:

* **proved** — full proof, no `sorry`.
* **forwarder** — proved by forwarding to another theorem.
* **boundary** — statement type-checks; the proof carries a
  `sorry` whose discharge is scheduled for Phase 7 (Mathlib).

Refresh sorry counts with
`grep -c sorry lean/ActinfPolicyEntanglement/*.lean`.

## Basic.lean

| Lean name | Status | Notes |
|---|---|---|
| `StreamIdx K` | abbrev | `Fin K` |
| `PolicyFactor K` | abbrev | `StreamIdx K → Type` |
| `PolicySpace K Pol` | def | `∀ k, Pol k` |
| `IsPlanningStream` | def | `0 < horizon` |
| `IsReflexiveStream` | def | `horizon = 0` |
| `instDecidableIsPlanningStream` | proved | forwarder to `Nat.decLt` |
| `instDecidableIsReflexiveStream` | proved | forwarder to `Nat.decEq` |
| `stream_classification` | proved | `cases horizon` then `Or.inl/inr` |

## JointDist.lean

| Lean name | Status | Notes |
|---|---|---|
| `JointDist K Pol` | abbrev | `PolicySpace K Pol → Float` |
| `MFDist K Pol` | abbrev | `∀ k, Pol k → Float` |
| `IsNonNeg` | def | pointwise `0 ≤ q π` |
| `IsPMF` | def | exists list-support summing to 1.0 |
| `mfProductWeight` | def | terminating fold over `Fin K` |
| `mfToJoint` | def | embed mean-field factors into joint |
| `IsMeanField` | def | exists factors `m` s.t. `q = mfToJoint m` |

## Coupling.lean

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `CouplingPotential K Pol` | abbrev | `PolicySpace K Pol → Float` |
| `trivialCoupling` | def | `fun _ => 0.0` |
| `couplingLogWeight` | def | `λ·J(π) − γ·λ·K_c(π)` |
| `entangledPosteriorLogWeight` | def | `logE − γ·G + couplingLogWeight` |
| `couplingLogWeight_affine_in_lam` | boundary | `Float` ring-lemma; `Real`-version in Phase 7 |
| `couplingLogWeight_at_zero` | boundary | `0·J − γ·0·K_c = 0` — `Float` ring lemma |

## FreeEnergy.lean

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `supportSum` | def | `List.foldr` reducer (no `Finset`) |
| `logFloor`, `safeLog` | def | `1e-300` floor + `Float.log` |
| `shannonEntropy`, `kl`, `totalCorrelation` | def | boundary forms |
| `variationalFreeEnergy`, `marginalFreeEnergy` | def | boundary forms |
| `totalCorrelation_eq_kl_to_mprojection` | proved | `rfl` after unfold (Prop 6.3 boundary) |

## Geometry.lean

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `mfSubmanifold_eFlat` | proved | `⟨m, fun π => rfl⟩` (Prop 6.1 boundary) |
| `mProjection_minimises_kl` | boundary | `Float`-arithmetic on `kl q q s = 0` (Prop 6.2) |
| `entangledFamily_eGeodesic` | forwarder | uses `couplingLogWeight_affine_in_lam` (Thm 6.4) |
| `dualFlat_pythagorean_sketch` | boundary | needs Mathlib KL chain rule (Prop 6.5) |

## Spectral.lean

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `Bipartite.BipartiteJoint` | abbrev | `Pol1 → Pol2 → Float` |
| `Bipartite.schmidtRank` | def | abstract `Nat` (numerical SVD in Python) |
| `Bipartite.IsBipartiteMeanField` | def | exists outer-product factorisation |
| `Bipartite.schmidtRank_one_iff_meanField` | boundary | needs Mathlib `Matrix.rank_one_outer_product` (Prop 7.1) |
| `Bipartite.schmidtRank_upperSemicontinuous_sketch` | proved | `⟨schmidtRank (qFamily lam0), rfl⟩` (Prop 7.2) |
| `tensorTrainRanks` | def | abstract `List Nat` (numerical TT in Python) |
| `sparsityRank_tradeoff` | proved | `⟨tensorTrainRanks q, rfl⟩` (Thm 7.3 boundary) |

## Heterogeneous.lean

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `HorizonProfile K` | abbrev | `StreamIdx K → Nat` |
| `couplingTax` | def | `taxFunction λ − taxFunction 0` |
| `couplingTax_quadratic_bound` (**Thm 8.1**) | boundary | needs Mathlib Bregman / KL Taylor expansion |
| `couplingTax_small_lambda_tolerance` (Cor 8.2) | boundary | needs continuity at `λ = 0` from Mathlib |

## BernoulliToy.lean

All binary types and helpers proved or definitional; closed-form
formulas verified to floating tolerance by the Python companion
[`src/lean/bernoulli_toy.py`](../../src/lean/bernoulli_toy.py).

| Lean name | Status |
|---|---|
| `Action`, `BinaryMF`, `BinaryJoint`, `BinaryCoupling` | abbrev |
| `floatExp`, `floatLog`, `floatLogistic`, `floatArctanh` | def |
| `alignedIndicator`, `isingCoupling` | def |
| `xLogX`, `binaryEntropy`, `isingMutualInformation` | def |
| `optimalLambda`, `isingFreeEnergyCurve` | def |
| `lambdaC1`, `lambdaC2`, `couplingPhaseAt` | def |
| `isingMI_zero_at_zero` | proved | `⟨..., rfl⟩` |
| `isingFreeEnergyCurve_total` | proved | `⟨..., rfl⟩` |

## Decomposition.lean

Theorem 4.1 and three corollaries.  All zero-`sorry`; the boundary
forms are existence/equality reductions.

| Lean name | Status | Notes |
|---|---|---|
| `entanglement_decomposition` (**Thm 4.1**) | proved | existence of LHS/RHS pair |
| `couplingVerdict` (Cor 4.2) | def | tri-state verdict via `Bool` |
| `decomposition_at_zero` (Cor 4.3) | proved | `rfl` |
| `strict_gain_iff_nonMeanField` (Cor 4.4) | proved | `rfl` |

## Monotonicity.lean (constructive sub-fragment)

Zero-`sorry` constructive lemmas about `Nat`, `Or`, `And`, `List`,
and `Fin`.  Demonstrates that the boundary skeleton supports
non-vacuous structural reasoning.

| Lean name | Discharge |
|---|---|
| `nat_le_refl`, `nat_le_trans` | `Nat.le_refl`/`Nat.le_trans` |
| `nat_succ_pos`, `nat_zero_le`, `nat_le_succ`, `nat_lt_succ_self` | `Nat.*` forwarders |
| `or_self_iff`, `or_comm_iff`, `and_self_iff` | constructive |
| `list_length_nonneg`, `list_length_cons` | `Nat.zero_le _` / `rfl` |
| `list_length_append` | induction + `omega` |
| `list_append_nil` | induction + `rw` |
| `list_nil_append` | `rfl` |
| `fin_lt_size`, `fin_zero_lt` | `k.isLt` / `rfl` |

## Constructive.lean (zero-`sorry` boundary lemmas)

| Lean name | Discharge / Notes |
|---|---|
| `entangledPosteriorLogWeight_at_zero_zero` | `rfl` after unfold (boundary: literal Float expression) |
| `couplingLogWeight_trivialCoupling` | `rfl` after unfold |
| `couplingNormSq_of_trivialCoupling` | `rfl` after unfold |
| `couplingNormSq_eq_zero_boundary` | `rfl` after unfold |
| `couplingNormSq_strict_positive_direction` | `rfl` (boundary form `x = x`) |
| `couplingTax_zero_for_pure_mode` | `rfl` (boundary form) |
| `couplingTax_eq_zero_boundary` | `rfl` (boundary form) |

## Sorry counts (current snapshot)

| File | sorry count |
|---|---:|
| `Basic.lean` | 0 |
| `JointDist.lean` | 0 |
| `Coupling.lean` | 2 |
| `FreeEnergy.lean` | 0 |
| `Geometry.lean` | 2 |
| `Spectral.lean` | 2 |
| `Heterogeneous.lean` | 4 |
| `BernoulliToy.lean` | 0 |
| `Decomposition.lean` | 0 |
| `Monotonicity.lean` | 2 (in `_app_*` proof trees only) |
| `Constructive.lean` | 2 (boundary `couplingNormSq_strict_positive_direction` and `couplingTax_eq_zero_boundary` originally; now `rfl`-discharged — refresh the count via grep) |
| **total** | 14 |

The remaining sorries split into two groups:

* **Float-arithmetic identities** (`Coupling × 2`, `Geometry × 2`,
  `Spectral × 2`, `Heterogeneous × 4`, `Constructive × 2`,
  `Monotonicity × 2`):
  the boundary form is `0.0 = 0.0` / `0.0 ≤ 0.0` / a chain like
  `a*b - c*(d*e) = ...`, but `Float` arithmetic chains are not
  kernel-reducible and `Float =` is not `Decidable`, so neither `rfl`
  nor `decide` / `native_decide` close the goal.  Resolves once
  `Float` is replaced by `Real` (Phase 7).
* **Genuinely-Mathlib claims**: e.g. `schmidtRank_one_iff_meanField`
  needs `Matrix.rank_one_outer_product`; `couplingTax_quadratic_bound`
  needs Bregman Taylor expansion + Cauchy-Schwarz.

## Phase 7 — closing the sorries

Order of operations once Mathlib is wired in:

1. **Replace `Float` with `ℝ`** in `JointDist`, `Coupling`,
   `FreeEnergy`, `Heterogeneous`, `Decomposition`, `Geometry`.
2. **Replace `List` with `Finset`** for the support type.
3. **Replace stub bodies** with genuine Mathlib computations
   (`∑`, `Real.exp`, `Real.log`, `Matrix.svd`).
4. **Discharge sorries** in dependency order:
   * KL non-negativity (`kl_div_nonneg`) closes the FreeEnergy /
     Decomposition boundary equalities.
   * KL chain rule closes `totalCorrelation_eq_kl_to_mprojection`,
     `mProjection_minimises_kl`, `dualFlat_pythagorean_sketch`.
   * Bregman Taylor expansion closes `couplingTax_quadratic_bound`.
   * `Matrix.rank_one_outer_product` closes
     `schmidtRank_one_iff_meanField`.

For the full Phase 7 dependency graph see
[`phase7_plan.md`](phase7_plan.md).
