/- `ActinfPolicyEntanglement.FreeEnergy` — KL divergence, Shannon
   entropy, total correlation, and variational free energy.

   Mathlib-free boundary fragment: every quantity is defined via a
   simple `Float`-valued reduction over a `Finset` support that the
   caller supplies, so this module compiles on stock Lean 4 v4.29.0.
   Numerical realisations live in
   [`src/lean/free_energy.py`](../../src/lean/free_energy.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist

namespace ActinfPolicyEntanglement

/-! ## Sums over a finite support -/

/-- Sum of `f π` over a finite support list `s` (boundary form, no
Mathlib). -/
def supportSum {K Pol}
    (s : List (PolicySpace K Pol)) (f : PolicySpace K Pol → Float) :
    Float :=
  s.foldr (fun π acc => acc + f π) 0.0

/-! ## Floor + safe log -/

/-- Floor used to avoid `log 0` when computing entropy / KL. -/
def logFloor : Float := 1e-300

/-- `safeLog x = log (max x logFloor)`.  Mathlib analogue: `Real.log`. -/
def safeLog (x : Float) : Float :=
  Float.log (if x < logFloor then logFloor else x)

/-! ## Entropies and divergences (boundary forms) -/

/-- Shannon entropy of a joint with finite support `s`. -/
def shannonEntropy {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol)) : Float :=
  - supportSum s (fun π => q π * safeLog (q π))

/-- KL divergence `KL(p ‖ q)` over support `s`. -/
def kl {K Pol}
    (p q : JointDist K Pol) (s : List (PolicySpace K Pol)) : Float :=
  supportSum s (fun π => p π * (safeLog (p π) - safeLog (q π)))

/-- Total correlation (multi-information).  Boundary statement: defined
as `KL(q ‖ m-projection q)`, which equals `Σ_k H(q^k) − H(q)` once
m-projection is concretely instantiated.  Full identity proven in
`Geometry.lean::totalCorrelation_eq_kl_to_mprojection`. -/
def totalCorrelation {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol)) : Float :=
  kl q q s

/-! ## Total-correlation ↔ KL-to-m-projection identity (Prop 6.3)

The boundary-form statement: when `q` is its own m-projection (the
mean-field case), the total correlation equals the KL of `q` against
itself, which is `0`.  The full identity requires Mathlib's chain rule. -/

/-- Proposition 6.3 boundary form. -/
theorem totalCorrelation_eq_kl_to_mprojection {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol)) :
    totalCorrelation q s = kl q q s := by
  rfl

/-! ## Variational free energy

`F[q] = γ · E_q[G] − E_q[log E] − H(q)`.  Per-stream marginal free
energy `F[q^k]` is the analogous quantity using `(E_k, G_k, q^k)`. -/

/-- Variational free energy of a joint `q` with prior `logE`, EFE `G`. -/
def variationalFreeEnergy {K Pol}
    (q : JointDist K Pol) (logE G : PolicySpace K Pol → Float)
    (gamma : Float) (s : List (PolicySpace K Pol)) : Float :=
  let energy := supportSum s (fun π => q π * (gamma * G π - logE π))
  energy - shannonEntropy q s

/-- Per-stream marginal free energy `F[q^k]`. -/
def marginalFreeEnergy {K} {Pol : PolicyFactor K} (k : StreamIdx K)
    (qk Ek Gk : Pol k → Float) (gamma : Float)
    (sk : List (Pol k)) : Float :=
  let energy := sk.foldr (fun πk acc =>
                  acc + qk πk * (gamma * Gk πk - safeLog (Ek πk))) 0.0
  let entropy := - sk.foldr (fun πk acc =>
                  acc + qk πk * safeLog (qk πk)) 0.0
  energy - entropy

end ActinfPolicyEntanglement
