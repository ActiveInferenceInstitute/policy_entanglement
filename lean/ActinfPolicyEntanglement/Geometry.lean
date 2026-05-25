/- `ActinfPolicyEntanglement.Geometry` — information geometry of the
   λ-deformation: e-flatness of the mean-field submanifold,
   m-projection by marginalization, and the Pythagorean decomposition.

   Mathlib-free, `sorry`-free, `axiom`-free.  The algebraic theorems
   (e-geodesic affinity) are stated polymorphically over the
   `CommScalar α` typeclass; the probability-theoretic claims
   (m-projection, Pythagorean) are stated as *witness-consuming*
   boundary forms whose load-bearing identities are supplied by a
   separate MathlibProofs layer.  Numerical realizations live in
   [`src/lean/geometry.py`](../../src/lean/geometry.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.FreeEnergy
import ActinfPolicyEntanglement.Scalar

namespace ActinfPolicyEntanglement

/-! ## §6.1 e-flatness of the mean-field submanifold

A submanifold is *e-flat* iff its log-coordinates are closed under
affine combinations. The mean-field set
`𝓜_MF = { q : q = ∏_k q^k }` is the set of joints whose log-mass is
the *sum* of per-stream log-marginals — affine in log-coordinates by
construction. -/

/-- **`mfImage_isMeanField`** (registry `prop_6_1`, Prop 7.1,
`faithfulness: statement-restricted`).  This theorem proves only that
the product distribution induced by mean-field marginals *is*
mean-field — definitional membership `IsMeanField (mfToJoint m)`,
discharged by `rfl`.  It does **NOT** prove the named manuscript
proposition "the MF submanifold is e-flat" (closure under exponential
geodesics / affine-in-θ); that real-analytic content is the open
target scoped to the separate Mathlib layer (cf.
`entangledFamily_eGeodesic` for the affine-in-λ identity).  The name
was deliberately changed from the prior `mfSubmanifold_eFlat` so the
declaration's name states what it actually proves. -/
theorem mfImage_isMeanField {K Pol}
    (m : MFDist K Pol) :
    IsMeanField (mfToJoint m) := by
  refine ⟨m, ?_⟩
  intro _π
  rfl

/-! ## §6.1 m-projection minimizes KL (Proposition 6.2)

The m-projection of `q` onto `𝓜_MF` is the product of its marginals;
this minimizes `KL(q ‖ p)` over `p ∈ 𝓜_MF`.  Boundary form: when `q`
is *itself* mean-field, `KL(q ‖ mfToJoint m) = KL(q ‖ q)` as
*structural* equality, because the integrands match term-by-term.

The further reduction `KL(q ‖ q) = 0` requires Mathlib's `Real.log`
arithmetic and is exposed by the `MathlibProofs` extension. -/

/-- Pointwise-equality of integrands implies equality of `supportSum`s.
Stock-Lean discharge via `congrArg` + `funext`. -/
private theorem supportSum_pointwise_eq {K Pol}
    (s : List (PolicySpace K Pol))
    {f g : PolicySpace K Pol → Float}
    (h : ∀ π, f π = g π) :
    supportSum s f = supportSum s g :=
  congrArg (supportSum s) (funext h)

/-- **`mProjection_kl_eq_self_when_meanfield`** (registry `prop_6_2`,
Prop 7.2, `faithfulness: statement-restricted`).  This theorem proves
only the conditional equality `KL(q ‖ mfToJoint m) = KL(q ‖ q)` *under
the hypothesis* `h : q = mfToJoint m` (i.e. `q` is already mean-field).
It does **NOT** prove the named manuscript proposition that the
m-projection *minimises* KL — the information-projection optimality
`∀ p ∈ M_MF, D_KL(q‖m̂(q)) ≤ D_KL(q‖p)` is the open analytic target
for the separate Mathlib layer.  The name was deliberately changed
from the prior `mProjection_minimises_kl` so the declaration's name
states what it actually proves (an equality when `q` is already the
projection, not a minimality result). -/
theorem mProjection_kl_eq_self_when_meanfield {K Pol}
    (q : JointDist K Pol) (m : MFDist K Pol)
    (h : ∀ π, q π = mfToJoint m π)
    (s : List (PolicySpace K Pol)) :
    kl q (mfToJoint m) s = kl q q s := by
  unfold kl
  apply supportSum_pointwise_eq
  intro π
  rw [← h π]

/-! ## §7.2 The λ-family is an e-geodesic (Theorem 7.4)

The λ-entangled posteriors `{ q_λ : λ ∈ ℝ }` trace an exponential
geodesic: `log q_λ` is affine in λ for each fixed policy. Forwarder
to `Coupling.couplingLogWeight_affine_in_lam`.  Polymorphic over any
`[CommScalar α]`. -/

/-- **Theorem 7.4** (forwarder).  Polymorphic over `[CommScalar α]`. -/
theorem entangledFamily_eGeodesic {α : Type} [CommScalar α] {K Pol}
    (J K_c : CouplingPotential α K Pol) (gamma lam1 lam2 : α)
    (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma lam1 π
      - couplingLogWeight J K_c gamma lam2 π
    = (lam1 - lam2) * (J π - gamma * K_c π) :=
  couplingLogWeight_affine_in_lam J K_c gamma lam1 lam2 π

/-! ## §6.2 Pythagorean decomposition (Proposition 6.5)

For any reference mean-field `q₀*`,
`KL(q ‖ q₀*) = I(q) + KL(m̂(q) ‖ q₀*)`.

Boundary witness form: given a Mathlib-supplied identity
`klVal = tcVal + residual` together with three *tie-in* identities that
commit `klVal`, `tcVal`, and `residual` to boundary-fragment primitives,
the boundary fragment certifies the Pythagorean decomposition.

**Round-4 tie-in upgrade.** Prior to round 4 the witness was the
literal identity term `hWitness ↦ hWitness` (the `id` function) with
three free `Float` parameters — a caller could satisfy it with any
three numbers that happened to add up.  This module now wraps the
identity in a `PythagoreanWitness` structure whose three scalars must
equal `kl q q0_star s`, `totalCorrelation q s sumStreamEntropies`, and
`kl (mfToJoint mhat) q0_star s` respectively.  Free-`Float`
satisfaction is no longer possible.  The analytic identity itself
remains a witness field; the separate MathlibProofs layer discharges it
from the KL chain rule (see
[`MathlibRefinementRoadmap.md`](MathlibRefinementRoadmap.md)). -/

/-- **Witness payload for Proposition 6.5** (Pythagorean
decomposition). Binds the three scalars to boundary-fragment
primitives so a caller cannot satisfy the contract with arbitrary
Floats. Round-4 tie-in upgrade: replaces the prior `id`-function
witness with a structure that anchors `klVal`, `tcVal`, and
`residual` to `kl`, `totalCorrelation`, and `kl ∘ mfToJoint`. -/
structure PythagoreanWitness {K Pol}
    (q q0_star : JointDist K Pol) (mhat : MFDist K Pol)
    (s : List (PolicySpace K Pol)) (sumStreamEntropies : Float) where
  /-- The KL value to be decomposed. -/
  klVal : Float
  /-- The total correlation term. -/
  tcVal : Float
  /-- The residual KL from the m-projection to the reference. -/
  residual : Float
  /-- **Tie-in (1)**: `klVal` is the KL from `q` to the reference
  `q0_star`, computed via the boundary-fragment `kl` primitive. -/
  klVal_eq : klVal = kl q q0_star s
  /-- **Tie-in (2)**: `tcVal` is the genuine total correlation of `q`,
  computed via the boundary-fragment `totalCorrelation` primitive. -/
  tcVal_eq : tcVal = totalCorrelation q s sumStreamEntropies
  /-- **Tie-in (3)**: `residual` is the KL from the m-projection
  `mfToJoint mhat` to the reference `q0_star`. -/
  residual_eq : residual = kl (mfToJoint mhat) q0_star s
  /-- **Pythagorean identity** (analytic content; separate MathlibProofs
  payload).  This field captures `KL(q ‖ q₀*) = I(q) + KL(m̂(q) ‖ q₀*)`. -/
  pythagorean : klVal = tcVal + residual

/-- **Proposition 6.5 (boundary witness, round-4 tie-in upgrade)**:
extracts the Pythagorean identity from a `PythagoreanWitness`.  The
three scalars are now *committed* to boundary-fragment primitives
(`kl`, `totalCorrelation`, `mfToJoint`) via three tie-in equalities —
a caller can no longer satisfy the contract with arbitrary `Float`s.

**Typed-API-contract disclaimer.** The analytic Pythagorean identity
itself (the `pythagorean` field) remains a witness payload supplied
by the caller; the separate MathlibProofs layer discharges it from the
KL chain rule.  This theorem is **not** a stand-alone proof of the
Pythagorean decomposition; it certifies that *if* a caller supplies
witnesses that genuinely compute the boundary primitives, *then* the
extracted identity types-check.  The mathematical content lives in
the manuscript appendix S01 + the Python numerical companion in
[`src/lean/geometry.py`](../../src/lean/geometry.py) (which verifies
the identity on randomly sampled joints + reference mean-fields). -/
theorem dualFlat_pythagorean_witness {K Pol}
    {q q0_star : JointDist K Pol} {mhat : MFDist K Pol}
    {s : List (PolicySpace K Pol)} {sumStreamEntropies : Float}
    (w : PythagoreanWitness q q0_star mhat s sumStreamEntropies) :
    w.klVal = w.tcVal + w.residual := w.pythagorean

/-- **Corollary (round-4 boundary identity)**: when a `PythagoreanWitness`
is in scope, the explicit boundary-primitive form of the Pythagorean
decomposition follows by rewriting the three tie-in fields.  This
forwarder demonstrates that the structure's tie-ins are non-vacuous:
the `Float` equality at the level of boundary primitives is genuine,
not just abstract `klVal = tcVal + residual` with free parameters. -/
theorem dualFlat_pythagorean_boundary_identity {K Pol}
    {q q0_star : JointDist K Pol} {mhat : MFDist K Pol}
    {s : List (PolicySpace K Pol)} {sumStreamEntropies : Float}
    (w : PythagoreanWitness q q0_star mhat s sumStreamEntropies) :
    kl q q0_star s
      = totalCorrelation q s sumStreamEntropies
        + kl (mfToJoint mhat) q0_star s := by
  rw [← w.klVal_eq, ← w.tcVal_eq, ← w.residual_eq]
  exact w.pythagorean

end ActinfPolicyEntanglement
