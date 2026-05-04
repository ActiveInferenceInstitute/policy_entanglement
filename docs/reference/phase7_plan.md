# Phase 7 — Mathlib refinement plan

The Mathlib-free Lean 4 boundary fragment under
[`../../lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/)
deliberately leaves analytic content (KL non-negativity, log
identities, SVD rank, Bregman geometry) as `sorry` placeholders.
"Phase 7" is the consolidated work plan to discharge those sorries
once Mathlib is brought in.

## Inventory of sorries

See [`lean_reference.md`](lean_reference.md) for the per-theorem
table.  Refresh the live count with:

```bash
grep -c sorry lean/ActinfPolicyEntanglement/*.lean
```

Current snapshot (post-restoration, May 2026):

```
Basic.lean            0
JointDist.lean        0
Coupling.lean         2
FreeEnergy.lean       0
Geometry.lean         2
Spectral.lean         2
Heterogeneous.lean    4
BernoulliToy.lean     0
Decomposition.lean    0
Monotonicity.lean     2  (in nested proof trees)
Constructive.lean     2  (boundary placeholders)
total                14
```

## Refinement order

1. **Replace `Float` with `ℝ`** in `JointDist`, `Coupling`,
   `FreeEnergy`, `Heterogeneous`, `Decomposition`, `Geometry`.
2. **Replace `List (PolicySpace K Pol)` with `Finset (PolicySpace K Pol)`**
   for the support type.  This unlocks `Finset.sum` and the standard
   information-theory API.
3. **Replace stub bodies** (`0.0`, `1.0`) with genuine Mathlib
   computations (`∑`, `Real.exp`, `Real.log`, `Matrix.svd`).
4. **Discharge sorries** in dependency order:
   * `Float`-arithmetic boundary equalities (≈10 sorries) all close
     once the `Float`→`Real` replacement is done — `Real` is a `Field`
     and `ring` / `linarith` discharge the remaining algebraic shapes.
   * KL non-negativity (`MeasureTheory.kl_div_nonneg`) closes the
     FreeEnergy / Decomposition KL-bookkeeping sorries.
   * KL chain rule closes `totalCorrelation_eq_kl_to_mprojection`,
     `mProjection_minimises_kl`, `dualFlat_pythagorean_sketch`.
   * Bregman Taylor expansion + Cauchy-Schwarz close
     `couplingTax_quadratic_bound` and `couplingTax_small_lambda_tolerance`.
   * `Matrix.rank_one_outer_product` (or its equivalent) closes
     `Bipartite.schmidtRank_one_iff_meanField`.
5. **Promote sketches**: `Bipartite.schmidtRank_upperSemicontinuous_sketch`
   becomes a real upper-semicontinuity theorem once Mathlib's
   `UpperSemicontinuous.const_sub` is in scope.

## Effort estimate

See §12 of the manuscript
([`12_lean_formalization_plan.md`](../../manuscript/12_lean_formalization_plan.md))
for a phased estimate (~6 months total for an experienced Lean
contributor; the entanglement-decomposition theorem alone is the
*first-publishable-result* milestone at ~8–10 weeks).

## Constructive Phase 0 (already in place)

Two constructive sub-fragments ship with the boundary skeleton:

* **`Monotonicity.lean`** — structural lemmas on `Nat`, `Or`,
  `And`, `List`, and `Fin`.  Constructive forwarders to core Lean's
  arithmetic / list primitives.  Mostly sorry-free; two boundary
  Float-arithmetic chains carry placeholders.
* **`Constructive.lean`** — boundary lemmas about
  `couplingLogWeight`, `entangledPosteriorLogWeight`, and trivial
  coupling.  Five proved by `rfl` after `unfold`; two boundary
  Float-arithmetic placeholders.

These remain in place as a sanity rail once the Mathlib refinement
begins, demonstrating that the boundary skeleton supports
non-vacuous structural reasoning even without Mathlib.

## Decidability instances

`Basic.lean` ships with two decidability instances that let
downstream code do case analysis on stream mode without classical
logic:

* `instDecidableIsPlanningStream` — forwarder to `Nat.decLt`
* `instDecidableIsReflexiveStream` — forwarder to `Nat.decEq`
