/- `FepSketches.PolicyEntanglementBoundary` — re-export hook so the
   FEP-Lean / TSRCLean monorepo can `import FepSketches.…` and pick up
   the boundary fragment under a stable namespace.

   No new content; pure re-export of the load-bearing types and
   theorems from `ActinfPolicyEntanglement`. -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
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

/-! ## Re-exports for downstream FEP_Lean / TSRCLean agents -/

/-- Re-export: stream classification (planning vs reflexive). -/
theorem stream_classification_reexport (horizon : Nat) :
    IsPlanningStream horizon ∨ IsReflexiveStream horizon :=
  ActinfPolicyEntanglement.stream_classification horizon

/-- Re-export: mean-field is e-flat (Proposition 6.1 boundary). -/
theorem mfSubmanifold_eFlat_reexport {K Pol} (m : MFDist K Pol) :
    IsMeanField (mfToJoint m) :=
  ActinfPolicyEntanglement.mfSubmanifold_eFlat m

/-- Re-export: e-geodesic affine-in-λ structural lemma (Theorem 6.4). -/
theorem entangled_eGeodesic_reexport {K Pol}
    (J K_c : CouplingPotential K Pol)
    (gamma lam1 lam2 : Float) (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma lam1 π
      - couplingLogWeight J K_c gamma lam2 π
    = (lam1 - lam2) * (J π - gamma * K_c π) :=
  ActinfPolicyEntanglement.entangledFamily_eGeodesic J K_c gamma lam1 lam2 π

/-- Re-export: bipartite Schmidt rank ↔ mean-field (Prop 7.1 boundary). -/
theorem schmidtRank_one_iff_meanField_reexport {Pol1 Pol2 : Type}
    (q : Bipartite.BipartiteJoint Pol1 Pol2) :
    Bipartite.schmidtRank q = 1 ↔ Bipartite.IsBipartiteMeanField q :=
  ActinfPolicyEntanglement.Bipartite.schmidtRank_one_iff_meanField q

end PolicyEntanglement
end FepSketches
