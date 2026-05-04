/-
  FepSketches.lean
  Top-level FEP_Lean / TSRCLean re-export hub for the policy
  entanglement boundary fragment.  Re-exports every submodule under the
  `FepSketches.*` namespace so downstream agents can depend on a single
  import.
-/
import FepSketches.PolicyEntanglementBoundary

namespace FepSketches

/-- Root sanity theorem mirroring the per-module convention. -/
theorem fepSketchesRoot : True := True.intro

end FepSketches
