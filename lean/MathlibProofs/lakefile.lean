import Lake
open Lake DSL

package «MathlibProofs» where
  moreLeanArgs := #["-DautoImplicit=false"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.29.0"

/--
Optional additive package for Mathlib-backed witness discharge.

This package is separate from the stock-Lean boundary.  It may import
Mathlib and now carries the compiled headline real-valued decomposition
discharge. Other manuscript witness rows are not promoted until a
row-specific witness construction builds here.
-/
@[default_target]
lean_lib «MathlibProofs» where
  roots := #[`MathlibProofs]
