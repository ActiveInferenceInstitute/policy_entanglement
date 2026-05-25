/-
  ActinfPolicyEntanglement.lean
  Root module of the Lean 4 package for Policy Entanglement in Active
  Inference.

  Companion to: "Policy Entanglement in Active Inference" (manuscript
  in `projects/actinf_policy_entanglement_lean/manuscript/`).

  Author: Daniel Ari Friedman, Active Inference Institute.
  Date:   May 2026.

  Loading this module brings every one of the 17 boundary submodules
  into scope so downstream agents can `import ActinfPolicyEntanglement`
  and access the entire framework. The boundary fragment is
  Mathlib-free, 0-strict-`sorry`, 0-axiom, 0-`unsafe`/`partial`/
  `noncomputable`; see
  `ActinfPolicyEntanglement/MathlibRefinementRoadmap.md` for the
  MathlibProofs plan that would discharge the analytic content of the
  witness/boundary theorem rows atop this skeleton without perturbing it.
-/
import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.Scalar
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
import ActinfPolicyEntanglement.Convexity
import ActinfPolicyEntanglement.MarkovBlanket
import ActinfPolicyEntanglement.SpectralWitnesses
import ActinfPolicyEntanglement.ConnectionsWitnesses
import ActinfPolicyEntanglement.FloatRealResidualWitness
-- FepSketches.* re-exports import this module; do not import them
-- here (would create a build cycle).

namespace ActinfPolicyEntanglement

/-- Root sanity theorem for the package; mirrors the `fepSketchesRoot`
convention used in the sibling `fep_lean` / template manuscript layout. -/
theorem actinfPolicyEntanglementRoot : True := True.intro

end ActinfPolicyEntanglement
