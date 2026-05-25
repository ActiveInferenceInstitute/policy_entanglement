# Module: `Convexity`

Boundary witness-form definitions and theorems for the convexity-related
results on the variational free energy `F[q_λ]` in the entanglement
parameter `λ`.  Manuscript anchors:
[`../manuscript/2D_decomposition.md`](../../manuscript/2D_decomposition.md)
§5.4 (`decomposition.optimal` — Theorem 5.6, convexity of `F` in `λ`) and
[`../manuscript/2J_comparative_statics.md`](../../manuscript/2J_comparative_statics.md)
§11.3 (`comparative.sensitivity` — Proposition 11.1, local concavity at
`λ = 0`).  Supplementary derivation:
[`../manuscript/S02_convexity_of_free_energy.md`](../../manuscript/S02_convexity_of_free_energy.md).

## Overview

`Convexity` packages **two** convexity-related analytic obligations
that were historically outside the boundary fragment into current
`witness` status:

* **Theorem 5.6** (`thm_4_3`, *Convexity of `F[q_λ]` in `λ`*) — the
  *global* convex shape of the λ-curve.
* **Proposition 11.1** (`prop_10_1`, *Local concavity of `F[q_λ]` at
  `λ = 0`*) — the *Taylor-form* local concavity bound on a window
  `λ ∈ [0, ε]`.

Both results are stated as **Mathlib-free, witness-consuming boundary
theorems**: the caller (a separate MathlibProofs layer, or the numerical
Python layer) supplies the analytic evidence as a structural witness,
and the boundary fragment certifies the resulting existence claim by
extracting the witness fields.  Each theorem also threads the coupling
parameters `(J, K_c, γ)` through `couplingLogWeight` and re-anchors
`F` at `λ = 0` via `couplingLogWeight_at_zero`, so the witness is
genuinely tied to the boundary-fragment coupling skeleton (not a
floating, ignorable parameter).

The **third** convexity-related result — a full Mathlib-discharged
proof of convexity derived from log-concavity of `J − γ·K_c` and the
log-sum-exp partition function — remains MathlibProofs-refinement
work (witness-payload discharge, not deferred coverage).  The
witness-form theorems in this module are the closest the boundary
fragment can get to those identities without `import Mathlib`; they
keep the manuscript citation chain unbroken while leaving the analytic
content as a single named obligation on the witness side.

The module is `Mathlib`-free, `sorry`-free, and `axiom`-free.  It
follows the *witness-structure idiom* introduced in
[`Heterogeneous.lean`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean)
(`BoundedQuadraticTax`, `SmallLambdaTolerance`).

## Definitions provided

| Lean name | Kind | Purpose |
|---|---|---|
| `FreeEnergyConvexityWitness` | `structure` | Carries (i) the universally-quantified midpoint convex-combination inequality `F_curve (t·λ₁ + (1−t)·λ₂) ≤ t·F_curve λ₁ + (1−t)·F_curve λ₂` and (ii) the value `F_at_zero` of the curve at `λ = 0`.  Two fields. |
| `LocalConcavityAtZero` | `structure` | Carries the Taylor-form coefficients `(a₀, a₁, a₂)`, the cubic remainder bound `C`, the window radius `ε > 0`, the sign condition `a₂ ≤ 0`, and the upper bound `F_curve λ ≤ a₀ + a₁·λ + a₂·λ² + C·λ³` for `λ ∈ [0, ε]`.  Eight fields. |
| `freeEnergy_convex_in_lam_witness` | `theorem` | Boundary witness form of Theorem 5.6. |
| `freeEnergy_localConcavity_at_zero_witness` | `theorem` | Boundary witness form of Proposition 11.1. |

## Key theorems

### `freeEnergy_convex_in_lam_witness` (Theorem 5.6 — `thm_4_3`)

```lean
theorem freeEnergy_convex_in_lam_witness {α : Type} [CommScalar α]
    {K Pol}
    (F_curve : Float → Float)
    (J K_c : CouplingPotential α K Pol) (gamma : α)
    (witness : FreeEnergyConvexityWitness F_curve) :
    (∀ lam1 lam2 t : Float,
        F_curve (t * lam1 + (1.0 - t) * lam2)
          ≤ t * F_curve lam1 + (1.0 - t) * F_curve lam2)
      ∧ (∀ π : PolicySpace K Pol,
            couplingLogWeight J K_c gamma 0 π = 0)
```

Polymorphic over `[CommScalar α]` on the coupling side so the
λ = 0 anchor `couplingLogWeight_at_zero` *genuinely uses every coupling
parameter* `(J, K_c, γ)`.  The body is two-line: the convexity
inequality is read off the witness's `convex` field, and the anchor
forwards to `couplingLogWeight_at_zero` from
[`Coupling.lean`](../../lean/ActinfPolicyEntanglement/Coupling.lean).

### `freeEnergy_localConcavity_at_zero_witness` (Proposition 11.1 — `prop_10_1`)

```lean
theorem freeEnergy_localConcavity_at_zero_witness {α : Type} [CommScalar α]
    {K Pol}
    (F_curve : Float → Float)
    (J K_c : CouplingPotential α K Pol) (gamma : α)
    (witness : LocalConcavityAtZero F_curve) :
    witness.a2 ≤ 0.0
      ∧ 0.0 < witness.eps
      ∧ (∀ lam : Float, 0.0 ≤ lam → lam ≤ witness.eps →
            F_curve lam
              ≤ witness.a0 + witness.a1 * lam
                + witness.a2 * lam * lam + witness.C * lam * lam * lam)
      ∧ (∀ π : PolicySpace K Pol,
            couplingLogWeight J K_c gamma 0 π = 0)
```

The conjunction packages the three load-bearing facts of the
Taylor-form local concavity statement (sign of `a₂`, non-degenerate
window, Taylor-bound inequality) with the boundary-fragment anchor at
`λ = 0`.

## Wiring

| Track | Resolves to |
|---|---|
| Manuscript section (Thm 5.6) | [`§5.4 Optimal coupling`](../../manuscript/2D_decomposition.md) (`decomposition.optimal`), with the worked supplementary derivation in [`S02 Convexity of free energy`](../../manuscript/S02_convexity_of_free_energy.md). |
| Manuscript section (Prop 11.1) | [`§11.3 Sensitivity to potential structure`](../../manuscript/2J_comparative_statics.md) (`comparative.sensitivity`). |
| Lean module | [`Convexity.lean`](../../lean/ActinfPolicyEntanglement/Convexity.lean) (2 structures, 2 theorems, zero `sorry`, zero `axiom`). |
| Registry labels | `thm_4_3` (Thm 5.6) and `prop_10_1` (Prop 11.1) in [`manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml); both are current `status: witness` rows. |
| Python sanity rails | [`src/lean/free_energy`](../../src/lean/free_energy.py) (free-energy curve evaluation) and [`src/lean/coupling`](../../src/lean/coupling.py) (`couplingLogWeight`-equivalents); exercised by the parameter sweep in [`scripts/parameter_sweep.py`](../../scripts/parameter_sweep.py). |
| Tests | [`tests/test_free_energy.py`](../../tests/test_free_energy.py) and the parameter-sweep invariants in [`tests/test_invariants_and_dashboard.py`](../../tests/test_invariants_and_dashboard.py). |

## Examples / use-cases (witness construction)

A Mathlib-side caller that wishes to certify Theorem 5.6 on a
specific free-energy curve constructs a `FreeEnergyConvexityWitness`
by supplying the analytic inequality as an explicit argument:

```lean
def myConvexityWitness
    (analyticConvexity :
      ∀ lam1 lam2 t : Float,
        myFreeEnergyCurve (t * lam1 + (1.0 - t) * lam2)
          ≤ t * myFreeEnergyCurve lam1
            + (1.0 - t) * myFreeEnergyCurve lam2) :
    FreeEnergyConvexityWitness myFreeEnergyCurve where
  convex := analyticConvexity
  F_at_zero := myFreeEnergyCurve 0.0
```

and then invokes

```lean
example : ... := freeEnergy_convex_in_lam_witness
                   myFreeEnergyCurve J K_c gamma
                   (myConvexityWitness analyticConvexity)
```

to discharge the global convexity claim *while threading the coupling
skeleton through the anchor*.  An analogous construction for
`LocalConcavityAtZero` discharges Proposition 11.1: the caller supplies
the three Taylor coefficients, the cubic envelope, and the small-`λ`
inequality on `[0, ε]`.

On the **numerical** side, the parameter sweep generates the actual
convex curve over a grid of λ-values and verifies the chord-above-curve
inequality at every sampled triple `(λ₁, λ₂, t)`; the same trace
fits a quadratic at `λ = 0` and checks the negative-curvature sign.
This is the empirical mirror of what the witness structures formalize.

## Cross-references

* [`free_energy.md`](free_energy.md) — `variationalFreeEnergy` is the
  underlying primitive whose λ-curve this module proves convex /
  locally concave at zero.
* [`coupling.md`](coupling.md) — `couplingLogWeight_at_zero` is the
  anchor that makes both witness theorems non-vacuous on the coupling
  side.
* [`heterogeneous_ensembles.md`](heterogeneous_ensembles.md) — the
  witness-structure idiom (`BoundedQuadraticTax`,
  `SmallLambdaTolerance`) introduced for Theorem 9.1 is reused here for
  Theorem 5.6 / Proposition 11.1.
* [`markov_blanket.md`](markov_blanket.md) — additional witness-form
  theorem (Proposition 19.3) graduated in the same round.
* [`decomposition_theorem.md`](decomposition_theorem.md) — Theorem 5.1
  consumes `variationalFreeEnergy` and is the upstream identity whose
  convexity properties this module certifies.
* [`../reference/lean_reference.md`](../reference/lean_reference.md) —
  per-theorem status table; the Mathlib refinement roadmap for fully
  discharging convexity from log-concavity of `J − γ·K_c` via Mathlib
  lives in [`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).
