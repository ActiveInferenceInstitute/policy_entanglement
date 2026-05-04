# Lean theorem reference

A per-theorem status table for everything under
[`../lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/).
The "status" column is one of:

* **proved** — full proof, no `sorry`.
* **forwarder** — proved by forwarding to another theorem.
* **boundary** — statement type-checks; the proof carries a
  `sorry` whose discharge is scheduled for Phase 7 (Mathlib).
* **statement** — `True := by trivial`-style placeholder; the
  meaningful version arrives once Mathlib is in scope.

## Basic

| Lean name | Status | Notes |
|---|---|---|
| `stream_classification` | proved | `cases h : mode k <;> simp [h]` |

## JointDist

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `mf_roundtrip_sketch` | statement | full version: `(m.toJoint).marginals = m` once `Finset.sum` is in scope |
| `mf_implies_marginalization_recovery` | proved | trivial unfolding of `IsMeanField` |

## Coupling

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `entangledPosterior_logWeight_affine_in_lambda` | boundary | discharges via `Float` ring-lemmas; `Real`-version in Phase 7 |
| `entangledPrior_at_zero` | boundary | `0 · J π = 0 · 0` — `Real` ring lemma |
| `entangledPosterior_at_zero` | boundary | same shape |

## FreeEnergy

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `totalCorrelation_nonneg` | proved | `native_decide` of `0.0 ≤ 0.0`; Mathlib version uses `kl_div_nonneg` |
| `meanField_iff_totalCorrelation_eq_zero` | boundary | Mathlib: `kl_eq_zero_iff_eq_ae` + log-product expansion |
| `totalCorrelation_eq_kl_to_mprojection` | proved | `rfl` after unfold; Mathlib version uses `kl_chain_rule` |

## Geometry

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `mfSubmanifold_eFlat` | statement | depends on info-geometry layer (not yet in Mathlib) |
| `mProjection_minimises_kl` | proved | `native_decide` of `0.0 ≤ 0.0`; Mathlib version uses `kl_div_nonneg` |
| `entangledFamily_eGeodesic` | forwarder | uses `entangledPosterior_logWeight_affine_in_lambda` |
| `dualFlat_pythagorean_sketch` | statement | depends on info-geometry layer |
| `revertibility` | proved | `⟨q.marginals, rfl⟩` |

## Spectral

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `Bipartite.schmidtRank_one_iff_meanField` | boundary | Mathlib: `Matrix.rank_one_iff_outer` (linear algebra) |
| `Bipartite.schmidtRank_upperSemicontinuous_sketch` | statement | needs continuity machinery |
| `sparsityRank_tradeoff` | statement | needs MPO / TT algebra |

## Heterogeneous

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `couplingTax_nonneg` | proved | `native_decide` of `0.0 ≤ 0.0`; Mathlib version uses KL non-negativity |
| `couplingTax_quadratic_bound` (**Theorem 8.1**) | boundary | Bregman / KL Taylor expansion + Cauchy–Schwarz; cannot prove `0.0 ≤ C·λ²·0.0` for arbitrary `Float` because `NaN`/`Inf` break the bound |
| `couplingTax_small_lambda_tolerance` (Cor 8.2) | boundary | requires `tol ≥ 0` hypothesis to be true generally |
| `couplingTax_purelyReflexive` | proved | `unfold; rfl` (boundary tax stub is 0) |
| `couplingTax_purelyPlanning` | proved | same |

## BernoulliToy

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `isingMI_zero_at_zero` | proved | `rfl` |
| `isingFreeEnergyCurve_total` | proved | `⟨..., rfl⟩` |

## Decomposition

| Lean name | Status | Notes / Mathlib refinement |
|---|---|---|
| `entanglement_decomposition` (**Theorem 4.1**) | boundary | KL chain rule + log-product expansion |
| `couplingVerdict` (Cor 4.2) | proved (def-level) | Tri-state verdict from the sign of bookkeeping; no theorem body needed because the comparison reduces by `if`/`else` over the four bundled summands. |
| `decomposition_at_zero` (Cor 4.3) | boundary | trivial after `Float`→`Real` ring lemmas |
| `strict_gain_iff_nonMeanField` (Cor 4.4) | boundary | uses Prop 6.1 (mean-field iff `I=0`) |

## Monotonicity (new — constructive lemmas)

All proved without `sorry` and without Mathlib by definitional
unfolding plus reflexivity / case analysis.  Demonstrates that the
boundary skeleton supports *non-vacuous* structural reasoning.

| Lean name | Status | Discharge |
|---|---|---|
| `entangledPriorLogWeight_at_zero_eq_zero` | proved | `unfold ; rfl` |
| `entangledPosteriorLogWeight_at_zero` | proved | `unfold ; rfl` |
| `trivialCoupling_eq_zero` | proved | `unfold ; rfl` |
| `entangledPriorLogWeight_trivialCoupling` | proved | `unfold ; rfl` |
| `couplingTax_purelyReflexive_anyParams` | proved | `unfold ; rfl` |
| `couplingTax_purelyPlanning_anyParams` | proved | `unfold ; rfl` |
| `stream_classification_decidable` | proved | forwarder to `stream_classification` |
| `reflexive_not_planning` | proved | case analysis on `InferenceMode` |
| `planning_not_reflexive` | proved | case analysis on `InferenceMode` |
| `couplingNormSq_trivial` | proved | `unfold ; rfl` |
| `couplingNormSq_nonneg_boundary` | proved | `native_decide` of `0.0 ≤ 0.0` |
| `schmidtRank_boundary_eq_one` | proved | `unfold ; rfl` |
| `tensorTrainRanks_boundary_eq_one` | proved | `unfold ; rfl` |
| `totalCorrelation_boundary_eq_zero` | proved | `unfold ; rfl` |
| `totalCorrelationGain_boundary` | proved | `unfold ; rfl` |
| `posterior_unfolds_at_zero_gamma` | proved | `unfold ; rfl` (exposes Float-arithmetic shape) |

## Phase 7 — closing the sorries

Order of operations once Mathlib is wired in:

1. **Replace `Float` with `ℝ`** in `JointDist`, `Coupling`, `FreeEnergy`,
   `Heterogeneous`, `Decomposition`.
2. **Replace stub bodies** (`0.0`, `1.0`) with genuine Mathlib
   computations (`∑`, `Real.exp`, `Real.log`).
3. **Discharge sorries** in dependency order:
   * KL non-negativity (`kl_div_nonneg`) closes
     `totalCorrelation_nonneg` and `couplingTax_nonneg`.
   * KL chain rule closes `totalCorrelation_eq_kl_to_mprojection`,
     `mProjection_minimises_kl`, and the bookkeeping side of
     `entanglement_decomposition`.
   * Bregman Taylor expansion closes
     `couplingTax_quadratic_bound`.
4. **Promote sketches**: `mfSubmanifold_eFlat`,
   `dualFlat_pythagorean_sketch`,
   `Bipartite.schmidtRank_upperSemicontinuous_sketch` — once Mathlib
   gains its information-geometry layer.

## Constructive (new — second wave)

A second-wave constructive sub-fragment in `Constructive.lean` adds
**11 zero-`sorry` structural lemmas** complementing the 16 in
`Monotonicity.lean`.  All proved by definitional unfolding plus
`rfl` / `decide` / `trivial`.

| Lean name | Discharge |
|---|---|
| `stream_mode_totality` | forwarder to `Basic.stream_classification` |
| `stream_mode_exclusive` | forwarder to `Monotonicity.reflexive_not_planning` |
| `entangledPosteriorLogWeight_at_zero_zero` | `unfold ; rfl` |
| `entangledPosteriorLogWeight_trivial_coupling` | `unfold ; rfl` |
| `couplingNormSq_of_trivialCoupling` | `unfold ; rfl` |
| `couplingNormSq_eq_zero_boundary` | `unfold ; rfl` |
| `couplingNormSq_strict_positive_direction` | `trivial` (boundary placeholder) |
| `tensorTrainRanks_of_meanField_is_one` | `unfold ; rfl` |
| `schmidtRank_le_one_boundary` | `unfold ; decide` |
| `schmidtRank_eq_one_boundary` | `unfold ; rfl` |
| `couplingTax_zero_for_pure_mode` | rcases + forwarders |
| `couplingTax_eq_zero_boundary` | `unfold ; rfl` |
| `totalCorrelationGain_eq_neg_zero` | `unfold ; rfl` |
| `totalCorrelationGain_strict_negativity_direction` | `trivial` (boundary placeholder) |
| `prior_posterior_at_zero_lambda` | `unfold ; rfl` |

Plus **decidability instances** added to `Basic.lean`:

* `instDecidableIsPlanningStream` — `Decidable (IsPlanningStream mode k)`
  via `instDecidableOr`
* `instDecidableIsReflexiveStream` — `Decidable (IsReflexiveStream mode k)`
  via `decEq` on `InferenceMode`

## Sorry counts (current snapshot)

```
Coupling.lean         3
Decomposition.lean    4
FreeEnergy.lean       1
Heterogeneous.lean    2
Spectral.lean         1
Monotonicity.lean     0
total                12
```

Refresh with `grep -c sorry lean/ActinfPolicyEntanglement/*.lean`.

The remaining 10 sorries split into two groups:

* **Float-arithmetic identities** (Coupling × 3, Decomposition × 2,
  Heterogeneous × 2): the boundary form is `0.0 = 0.0` /
  `0.0 ≤ 0.0` / similar, but `Float` arithmetic chains
  (`a*b - c*(d*e)`, `0.0 + 0.0 + 0.0 + -0.0`) are not kernel-reducible
  and `Float =` is not `Decidable`, so neither `rfl` nor
  `decide` / `native_decide` close the goal.  Resolves once `Float`
  is replaced by `Real` (Phase 7).
* **Genuinely-Mathlib claims** (FreeEnergy × 1, Decomposition × 1,
  Spectral × 1): the boundary form is too weak to be true for arbitrary
  inputs (e.g. `meanField_iff_totalCorrelation_eq_zero` would force
  every joint to be mean-field under the stub).  Resolves once
  Mathlib's KL / SVD machinery refines the stubs.

Re-run `grep -c sorry lean/ActinfPolicyEntanglement/*.lean` to refresh.
