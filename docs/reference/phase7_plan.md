# Phase 7 — Mathlib refinement plan

The Mathlib-free Lean 4 boundary fragment under
[`../../lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/)
deliberately leaves analytic content (KL non-negativity, log
identities, SVD rank, Bregman geometry) as `sorry` placeholders.
"Phase 7" is the consolidated work plan to discharge those sorries
once Mathlib is brought in.

## Inventory of sorries

See [`lean_reference.md`](lean_reference.md) for the per-theorem
table.  Today's snapshot:

```
Coupling.lean         3
Decomposition.lean    3
FreeEnergy.lean       1
Heterogeneous.lean    2
Spectral.lean         1
Monotonicity.lean     0
total                12
```

Refresh with `grep -c sorry lean/ActinfPolicyEntanglement/*.lean`.

## Refinement order (oldest plan)

1. **Replace `Float` with `ℝ`** in `JointDist`, `Coupling`,
   `FreeEnergy`, `Heterogeneous`, `Decomposition`.
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

## Effort estimate

See §12 of the manuscript ([`12_lean_formalization_plan.md`](../../manuscript/12_lean_formalization_plan.md))
for a phased estimate (~6 months total for an experienced Lean
contributor; the entanglement-decomposition theorem alone is the
*first-publishable-result* milestone at ~8–10 weeks).

## Constructive Phase 0 (already in place)

The new `Monotonicity.lean` module ships **16 constructive
(no-`sorry`) theorems** that exercise the boundary skeleton in a
different direction from the headline-theorem files: stream
classification, λ=0 reductions, pure-mode coupling-tax invariants,
and structural identities on the spectral / coupling-norm constants
all hold by definitional unfolding without Mathlib.  These remain in
place as a sanity rail once the Mathlib refinement begins.
