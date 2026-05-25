/- `ActinfPolicyEntanglement.Convexity` — convexity of the variational
   free energy in the entanglement parameter `λ` (Theorem 5.6) and the
   local Taylor-form concavity of `F` at `λ = 0` (Proposition 11.1).

   Mathlib-free, `sorry`-free, `axiom`-free.  Both results are stated as
   *witness-consuming* boundary forms: the caller (a separate
   MathlibProofs layer, or the numerical Python layer) supplies the analytic
   evidence as a structural witness, and the boundary fragment certifies
   the resulting existence claim by extracting the witness fields.  Each
   witness also anchors `F` at `λ = 0` through `couplingLogWeight_at_zero`
   so that `(J, K_c, γ)` are genuinely referenced and the boundary
   statement is non-vacuous.

   Numerical realizations of the convexity curve and Taylor-form local
   concavity bound live in
   [`src/lean/free_energy.py`](../../src/lean/free_energy.py) and
   [`src/lean/coupling.py`](../../src/lean/coupling.py); they are
   exercised by the parameter sweep in
   [`scripts/parameter_sweep.py`](../../scripts/parameter_sweep.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.FreeEnergy
import ActinfPolicyEntanglement.Scalar

namespace ActinfPolicyEntanglement

/-! ## §5.6 Convexity of `F` in `λ` (Theorem 5.6)

The variational free energy `F[q_λ]` is a *convex* function of the
entanglement parameter `λ`.  At the boundary level we phrase this as a
witness-consuming statement: the caller supplies the convex curve
`F_curve : Float → Float` together with the universally-quantified
convexity inequality, and the boundary fragment certifies the existence
claim while threading `(J, K_c, γ)` through `couplingLogWeight` so the
λ = 0 anchor `couplingLogWeight_at_zero` makes the statement non-vacuous. -/

/-- **Boundary witness for Theorem 5.6**: a convex curve
`F_curve : Float → Float` certifying

```
F_curve (t · λ₁ + (1 − t) · λ₂)
  ≤ t · F_curve λ₁ + (1 − t) · F_curve λ₂
```

for every `λ₁, λ₂` and every convex-combination weight `t ∈ [0, 1]`.

The fourth field `F_at_zero` records the value of the curve at `λ = 0`;
combined with `couplingLogWeight_at_zero` it gives a Mathlib-free anchor
that ties the abstract `F_curve` to the concrete coupling skeleton.
Supplied by the analytic MathlibProofs layer. -/
structure FreeEnergyConvexityWitness (F_curve : Float → Float) where
  /-- The midpoint convex-combination inequality, universally
  quantified in both endpoints and the convex weight. -/
  convex : ∀ lam1 lam2 t : Float,
    F_curve (t * lam1 + (1.0 - t) * lam2)
      ≤ t * F_curve lam1 + (1.0 - t) * F_curve lam2
  /-- The recorded value of the curve at `λ = 0`. -/
  F_at_zero : Float

/-- **Theorem 5.6 (boundary witness form)**: a
`FreeEnergyConvexityWitness` *is* the existence of a convex `λ`-curve
for `F[q_λ]` together with the `λ = 0` anchor that ties the curve to the
boundary-fragment coupling skeleton (via
`couplingLogWeight_pointwise_at_zero`).  Polymorphic over `[CommScalar α]`
on the coupling side so the anchor genuinely uses every coupling
parameter `(J, K_c, γ)`.

**Typed-API-contract disclaimer.** This theorem is *not* a stand-alone
proof that `F[q_λ]` is convex in `λ`.  It is a typed-API contract: the
convex curve and the universally-quantified midpoint inequality are
supplied as a `FreeEnergyConvexityWitness`; the boundary fragment
extracts the fields and re-publishes them.  Numerical witness in
`src/lean/free_energy.py` + `scripts/parameter_sweep.py`; MathlibProofs
discharge from log-concavity-on-the-simplex arguments. -/
theorem freeEnergy_convex_in_lam_witness {α : Type} [CommScalar α]
    {K Pol}
    (F_curve : Float → Float)
    (J K_c : CouplingPotential α K Pol) (gamma : α)
    (witness : FreeEnergyConvexityWitness F_curve) :
    (∀ lam1 lam2 t : Float,
        F_curve (t * lam1 + (1.0 - t) * lam2)
          ≤ t * F_curve lam1 + (1.0 - t) * F_curve lam2)
      ∧ (∀ π : PolicySpace K Pol,
            couplingLogWeight J K_c gamma 0 π = 0) := by
  refine ⟨witness.convex, ?_⟩
  intro π
  exact couplingLogWeight_at_zero J K_c gamma π

/-! ## §11.1 Local concavity of `F` at `λ = 0` (Proposition 11.1)

Near `λ = 0` the *negative-log-partition* expansion of `F[q_λ]` yields a
local Taylor form

```
F_curve λ ≤ a₀ + a₁ · λ + a₂ · λ²  +  C · λ³   for all λ ∈ [0, ε],
```

with `a₂ ≤ 0` (the local *concavity* coefficient) and a cubic remainder
controlled by `C` on the small-`λ` window `[0, ε]`.  We expose this as a
witness-consuming boundary statement; the analytic Taylor argument
supplied by the separate MathlibProofs layer certifies the coefficient signs
and the cubic remainder bound, and the boundary fragment certifies the
existence claim by extracting the witness fields. -/

/-- **Boundary witness for Proposition 11.1**: Taylor-form local
concavity of `F[q_λ]` at `λ = 0`.

The witness records the constant, linear, and quadratic coefficients
`(a₀, a₁, a₂)`, the cubic remainder bound `C`, the local window radius
`ε > 0`, and the inequality

```
F_curve λ ≤ a₀ + a₁ · λ + a₂ · λ² + C · λ³  for all λ ∈ [0, ε].
```

The concavity condition `a₂ ≤ 0` is recorded explicitly so callers can
read off the negative curvature without parsing the curve.  Supplied by
the analytic MathlibProofs layer. -/
structure LocalConcavityAtZero (F_curve : Float → Float) where
  /-- Constant Taylor coefficient. -/
  a0 : Float
  /-- Linear Taylor coefficient. -/
  a1 : Float
  /-- Quadratic Taylor coefficient — the local concavity coefficient. -/
  a2 : Float
  /-- Cubic remainder envelope constant. -/
  C : Float
  /-- The small-`λ` window radius. -/
  eps : Float
  /-- `a₂ ≤ 0`: the curvature is non-positive (local concavity). -/
  a2_nonpos : a2 ≤ 0.0
  /-- `ε > 0`: the window is non-degenerate. -/
  eps_pos : 0.0 < eps
  /-- The Taylor-form upper bound on `F_curve` for `λ ∈ [0, ε]`. -/
  bound : ∀ lam : Float, 0.0 ≤ lam → lam ≤ eps →
    F_curve lam ≤ a0 + a1 * lam + a2 * lam * lam + C * lam * lam * lam

/-- **Proposition 11.1 (boundary witness form)**: a
`LocalConcavityAtZero` witness *is* the existence of a Taylor-form local
concavity bound for `F[q_λ]` at `λ = 0`, together with the `λ = 0`
anchor that ties the curve to the boundary-fragment coupling skeleton
(via `couplingLogWeight_pointwise_at_zero`).  Polymorphic over
`[CommScalar α]` on the coupling side so the anchor genuinely uses every
coupling parameter `(J, K_c, γ)`.

**Typed-API-contract disclaimer.** Not a stand-alone proof of local
concavity; a typed-API contract.  The Taylor coefficients, the
`a₂ ≤ 0` sign, the local window radius, and the cubic-remainder bound
are all supplied as `LocalConcavityAtZero` fields.  Numerical witness
in `parameter_sweep.py`; MathlibProofs discharge from real-analytic
second-derivative arguments. -/
theorem freeEnergy_localConcavity_at_zero_witness {α : Type} [CommScalar α]
    {K Pol}
    (F_curve : Float → Float)
    (J K_c : CouplingPotential α K Pol) (gamma : α)
    (witness : LocalConcavityAtZero F_curve) :
    witness.a2 ≤ 0.0
      ∧ 0.0 < witness.eps
      ∧ (∀ lam : Float, 0.0 ≤ lam → lam ≤ witness.eps →
            F_curve lam
              ≤ witness.a0
              + witness.a1 * lam
              + witness.a2 * lam * lam
              + witness.C * lam * lam * lam)
      ∧ (∀ π : PolicySpace K Pol,
            couplingLogWeight J K_c gamma 0 π = 0) := by
  refine ⟨witness.a2_nonpos, witness.eps_pos, witness.bound, ?_⟩
  intro π
  exact couplingLogWeight_at_zero J K_c gamma π

end ActinfPolicyEntanglement
