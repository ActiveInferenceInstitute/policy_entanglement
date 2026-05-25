/- `FepSketches.PolicyEntanglementBoundary` — re-export hook so a
   template or fep_lean-adjacent checkout can `import FepSketches.…` and
   pick up the boundary fragment under a stable namespace.

   No new content; pure re-export of the load-bearing types and
   theorems from `ActinfPolicyEntanglement`. Mathlib-free, sorry-free,
   axiom-free. -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Scalar
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.FreeEnergy
import ActinfPolicyEntanglement.Geometry
import ActinfPolicyEntanglement.Spectral
import ActinfPolicyEntanglement.Heterogeneous
import ActinfPolicyEntanglement.BernoulliToy
import ActinfPolicyEntanglement.Decomposition
import ActinfPolicyEntanglement.Monotonicity
import ActinfPolicyEntanglement.Constructive

namespace FepSketches
namespace PolicyEntanglement

open ActinfPolicyEntanglement

/-- Root sanity theorem under the FepSketches namespace. -/
theorem fepSketchesPolicyEntanglementRoot : True := True.intro

/-! ## Re-exports for downstream `fep_lean` / template consumers -/

/-- Re-export: stream classification (planning vs reflexive). -/
theorem stream_classification_reexport (horizon : Nat) :
    IsPlanningStream horizon ∨ IsReflexiveStream horizon :=
  ActinfPolicyEntanglement.stream_classification horizon

/-- Re-export: the mean-field *image* is mean-field (Prop 7.1,
`prop_6_1`; definitional membership only — NOT e-flatness, see the
upstream `mfImage_isMeanField` doc-comment). -/
theorem mfImage_isMeanField_reexport {K Pol} (m : MFDist K Pol) :
    IsMeanField (mfToJoint m) :=
  ActinfPolicyEntanglement.mfImage_isMeanField m

/-- Re-export: e-geodesic affine-in-λ structural lemma (Theorem 7.4).
Polymorphic over `[CommScalar α]`; downstream consumers instantiate
the scalar type. -/
theorem entangled_eGeodesic_reexport {α : Type} [CommScalar α] {K Pol}
    (J K_c : CouplingPotential α K Pol)
    (gamma lam1 lam2 : α) (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma lam1 π
      - couplingLogWeight J K_c gamma lam2 π
    = (lam1 - lam2) * (J π - gamma * K_c π) :=
  ActinfPolicyEntanglement.entangledFamily_eGeodesic J K_c gamma lam1 lam2 π

/-- Re-export: bipartite mean-field factorization (Prop 7.1 forward
boundary). The full Schmidt-rank-1 characterization lives in the
`MathlibProofs` extension. -/
theorem isBipartiteMeanField_factors_reexport {Pol1 Pol2 : Type}
    (q : Bipartite.BipartiteJoint Pol1 Pol2)
    (h : Bipartite.IsBipartiteMeanField q) :
    ∃ (u : Pol1 → Float) (v : Pol2 → Float),
      ∀ π1 π2, q π1 π2 = u π1 * v π2 :=
  ActinfPolicyEntanglement.Bipartite.isBipartiteMeanField_factors q h

/-- Re-export: O(λ²) coupling-tax envelope witness (Theorem 9.1). -/
theorem couplingTax_quadratic_bound_reexport (taxFunction : Float → Float)
    (witness : BoundedQuadraticTax taxFunction) :
    ∃ (C : Float), 0.0 ≤ C ∧
      ∀ lam, couplingTax taxFunction lam ≤ C * lam * lam :=
  ActinfPolicyEntanglement.couplingTax_quadratic_bound taxFunction witness

end PolicyEntanglement
end FepSketches
