/-
  FepSketches.lean
  Top-level re-export hub for the policy entanglement boundary fragment,
  aligned with the `FepSketches.*` import path used next to
  `ActiveInferenceInstitute/fep_lean`.  Re-exports every submodule under
  `FepSketches.*` so downstream agents can depend on a single import.
-/
import FepSketches.PolicyEntanglementBoundary

namespace FepSketches

/-- Root sanity theorem mirroring the per-module convention. -/
theorem fepSketchesRoot : True := True.intro

end FepSketches
