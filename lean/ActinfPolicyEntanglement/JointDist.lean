/- `ActinfPolicyEntanglement.JointDist` — joint and mean-field
   distributions on the policy space.  Mathlib-free; uses `Float` for
   masses and `List` for the policy support so the boundary fragment
   compiles on stock Lean 4 v4.29.0.

   Numerical realizations live in
   [`src/lean/joint_dist.py`](../../src/lean/joint_dist.py). -/

import ActinfPolicyEntanglement.Basic

namespace ActinfPolicyEntanglement

/-! ## Distributions over policy spaces

We use plain `Float`-valued mass functions.  Normalization is supplied
by the `IsPMF` predicate, which records the (necessarily finite)
support as a `List` to stay Mathlib-free. -/

/-- An (abstract) joint distribution on the policy space: a real-valued
mass function. -/
abbrev JointDist (K : Nat) (Pol : PolicyFactor K) : Type :=
  PolicySpace K Pol → Float

/-- A mean-field (factorized) distribution: one mass function per
stream. -/
abbrev MFDist (K : Nat) (Pol : PolicyFactor K) : Type :=
  ∀ k : StreamIdx K, Pol k → Float

/-- Predicate: every value of `q` is non-negative. -/
def IsNonNeg {K Pol} (q : JointDist K Pol) : Prop :=
  ∀ π : PolicySpace K Pol, 0.0 ≤ q π

/-- Predicate: `q` has a finite support `support : List (PolicySpace K Pol)`
on which its values sum to `1.0`.  Mathlib analog: `PMF` /
`Finset.sum`. -/
def IsPMF {K Pol} (q : JointDist K Pol) : Prop :=
  ∃ (support : List (PolicySpace K Pol)),
    support.foldr (fun π acc => acc + q π) 0.0 = 1.0

/-! ## Mean-field embedding

The product (mean-field) joint induced by per-stream factors. -/

/-- Reduce `m k (π k)` over `[0, K)`. -/
def mfProductWeight {K Pol} (m : MFDist K Pol)
    (π : PolicySpace K Pol) : Float :=
  let rec go (i : Nat) (acc : Float) : Float :=
    if h : i < K then
      go (i + 1) (acc * m ⟨i, h⟩ (π ⟨i, h⟩))
    else acc
  termination_by K - i
  go 0 1.0

/-- Joint distribution induced by mean-field factors. -/
def mfToJoint {K Pol} (m : MFDist K Pol) : JointDist K Pol :=
  fun π => mfProductWeight m π

/-- A joint is *mean-field* if it equals the product of its marginals.
The witnessing mean-field factors are existentially quantified. -/
def IsMeanField {K Pol} (q : JointDist K Pol) : Prop :=
  ∃ m : MFDist K Pol, ∀ π, q π = mfToJoint m π

end ActinfPolicyEntanglement
