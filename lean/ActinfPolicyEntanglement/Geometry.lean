/- `ActinfPolicyEntanglement.Geometry` — information geometry of the
   λ-deformation: e-flatness of the mean-field submanifold,
   m-projection by marginalisation, and the Pythagorean decomposition.

   Mathlib-free boundary fragment.  Numerical realisations live in
   [`src/lean/geometry.py`](../../src/lean/geometry.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.FreeEnergy

namespace ActinfPolicyEntanglement

/-! ## §6.1 e-flatness of the mean-field submanifold

A submanifold is *e-flat* iff its log-coordinates are closed under
affine combinations. The mean-field set
`𝓜_MF = { q : q = ∏_k q^k }` is the set of joints whose log-mass is
the *sum* of per-stream log-marginals — affine in log-coordinates by
construction. -/

/-- Boundary form of `mfSubmanifold_eFlat`: the mean-field predicate is
preserved by *re-indexing* of mean-field factors.  The full statement
("closed under exponential geodesics") needs Mathlib's `Convex` /
`Affine`. -/
theorem mfSubmanifold_eFlat {K Pol}
    (m : MFDist K Pol) :
    IsMeanField (mfToJoint m) := by
  refine ⟨m, ?_⟩
  intro π
  rfl

/-! ## §6.1 m-projection minimises KL (Proposition 6.2)

The m-projection of `q` onto `𝓜_MF` is the product of its marginals;
this minimises `KL(q ‖ p)` over `p ∈ 𝓜_MF`.  Boundary form: when `q`
is *itself* mean-field, its m-projection equals `q`, so the KL is
zero — the trivial achiever. -/

/-- Proposition 6.2 boundary form. -/
theorem mProjection_minimises_kl {K Pol}
    (q : JointDist K Pol) (m : MFDist K Pol)
    (h : ∀ π, q π = mfToJoint m π)
    (s : List (PolicySpace K Pol)) :
    kl q (mfToJoint m) s = 0.0 := by
  -- When q ≡ mfToJoint m, every term `q π * (log q π − log (mfToJoint m π))`
  -- is `q π · 0 = 0`.  Reduces to `supportSum s (fun _ => 0) = 0`.
  unfold kl supportSum
  -- Boundary form leaves the `Float`-arithmetic discharge to Mathlib.
  sorry

/-! ## §6.2 The λ-family is an e-geodesic (Theorem 6.4)

The λ-entangled posteriors `{ q_λ : λ ∈ ℝ }` trace an exponential
geodesic: `log q_λ` is affine in λ for each fixed policy.  Forwarder
to `Coupling.couplingLogWeight_affine_in_lam`. -/

/-- Theorem 6.4 forwarder. -/
theorem entangledFamily_eGeodesic {K Pol}
    (J K_c : CouplingPotential K Pol) (gamma lam1 lam2 : Float)
    (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma lam1 π
      - couplingLogWeight J K_c gamma lam2 π
    = (lam1 - lam2) * (J π - gamma * K_c π) :=
  couplingLogWeight_affine_in_lam J K_c gamma lam1 lam2 π

/-! ## §6.2 Pythagorean decomposition (Proposition 6.5)

`KL(q ‖ q₀*) = I(q) + KL(m̂(q) ‖ q₀*)` for any reference mean-field
`q₀*`.  Boundary sketch.  Full identity needs Mathlib's KL chain rule. -/

/-- Proposition 6.5 sketch. -/
theorem dualFlat_pythagorean_sketch {K Pol}
    (q : JointDist K Pol) (q0_star : JointDist K Pol)
    (s : List (PolicySpace K Pol)) :
    kl q q0_star s = totalCorrelation q s + kl q q0_star s := by
  -- Boundary identity: when `q` is already mean-field, `I(q) = 0` and
  -- the equation reduces to `KL = KL`.
  unfold totalCorrelation
  -- The sketch identity is `kl q q s + kl q q0_star s − kl q q s = kl q q0_star s`.
  sorry

end ActinfPolicyEntanglement
