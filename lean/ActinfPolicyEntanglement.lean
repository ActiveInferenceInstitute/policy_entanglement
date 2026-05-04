/-
  ActinfPolicyEntanglement.lean
  Root module of the Lean 4 package for Policy Entanglement in Active
  Inference.

  Companion to: "Policy Entanglement in Active Inference" (manuscript
  in `projects/actinf_policy_entanglement_lean/manuscript/`).

  Author: Daniel Ari Friedman, Active Inference Institute.
  Date:   May 2026.

  Loading this module brings every submodule into scope so downstream
  agents can `import ActinfPolicyEntanglement` and access the entire
  framework (Phases 1–6 of the §12 roadmap).
-/
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
-- FepSketches.* re-exports import this module; do not import them
-- here (would create a build cycle).

namespace ActinfPolicyEntanglement

/-- Root sanity theorem for the package; mirrors the `tsrcLeanRoot` and
`fepSketchesRoot` conventions used elsewhere in the monorepo. -/
theorem actinfPolicyEntanglementRoot : True := True.intro

end ActinfPolicyEntanglement
