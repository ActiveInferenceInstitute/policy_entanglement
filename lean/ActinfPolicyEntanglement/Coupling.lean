/- `ActinfPolicyEntanglement.Coupling` — coupling potentials and the
   λ-entangled prior / posterior log-weights.

   Mathlib-free, `sorry`-free, `axiom`-free. Polymorphic over a
   `CommScalar α` typeclass (defined in `Scalar.lean`) so the
   algebraic theorems are provable in stock Lean 4. Numerical
   realizations live in [`src/lean/coupling.py`](../../src/lean/coupling.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Scalar

namespace ActinfPolicyEntanglement

/-! ## Coupling potentials

A coupling potential is a scalar function on the joint policy space.
Two flavours:
* `J`   — *habit coupling* (prior side)
* `K_c` — *preference coupling* (EFE side) -/

/-- A coupling potential: scalar score on the joint policy. The value
type `α` is left abstract; concrete instantiations supply a
`CommScalar α` instance. -/
abbrev CouplingPotential (α : Type) (K : Nat) (Pol : PolicyFactor K) : Type :=
  PolicySpace K Pol → α

/-- A *trivial* coupling potential vanishes everywhere. -/
def trivialCoupling {α : Type} [Zero α] {K Pol} :
    CouplingPotential α K Pol :=
  fun _ => 0

/-! ## λ-entangled prior / posterior log-weights

The entangled prior is `E_λ(π) ∝ ∏_k E_k(π^k) · exp(λ · J(π))`. The
entangled posterior is `q_λ(π) ∝ E_λ(π) · exp(-γ · G_λ(π))` with
`G_λ(π) = Σ_k G_k(π^k) + λ · K_c(π)`.

Working at the *log-weight* level keeps everything affine in λ and
avoids the partition-function bookkeeping until normalization. -/

/-- Log-weight contribution of the coupling alone:
`λ · J(π) − γ · λ · K_c(π)`. The definition only requires `Mul` and
`Sub`, so it applies directly to native `Float` (no `CommScalar`
instance needed for *evaluation*; the algebraic *theorems* below
require the full `CommScalar α` structure). -/
def couplingLogWeight {α : Type} [Mul α] [Sub α] {K Pol}
    (J K_c : CouplingPotential α K Pol)
    (gamma lam : α) : PolicySpace K Pol → α :=
  fun π => lam * J π - gamma * lam * K_c π

/-- Unnormalized log-weight of the λ-entangled posterior at policy `π`. -/
def entangledPosteriorLogWeight {α : Type} [Add α] [Mul α] [Sub α] {K Pol}
    (logE : PolicySpace K Pol → α)
    (G : PolicySpace K Pol → α)
    (J K_c : CouplingPotential α K Pol)
    (gamma lam : α) : PolicySpace K Pol → α :=
  fun π => logE π - gamma * G π + couplingLogWeight J K_c gamma lam π

/-! ## Affineness in λ (Theorem 7.4 boundary form)

Both algebraic identities below are now provable on stock Lean 4
because they are stated in `[CommScalar α]` and the ring laws are
typeclass methods. -/

/-- The coupling log-weight is affine in `λ` for every fixed policy:
at two values `lam1, lam2`, the difference factors as
`(lam1 − lam2) · (J(π) − γ · K_c(π))`. This is the boundary statement
of Theorem 7.4 (`entangledFamily_eGeodesic`). -/
theorem couplingLogWeight_affine_in_lam {α : Type} [CommScalar α] {K Pol}
    (J K_c : CouplingPotential α K Pol) (gamma lam1 lam2 : α)
    (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma lam1 π
      - couplingLogWeight J K_c gamma lam2 π
    = (lam1 - lam2) * (J π - gamma * K_c π) := by
  unfold couplingLogWeight
  exact CommScalar.affine_diff lam1 lam2 gamma (J π) (K_c π)

/-- Coupling log-weight at `λ = 0` is identically zero (no coupling). -/
theorem couplingLogWeight_at_zero {α : Type} [CommScalar α] {K Pol}
    (J K_c : CouplingPotential α K Pol) (gamma : α)
    (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma 0 π = 0 := by
  unfold couplingLogWeight
  exact CommScalar.affine_at_zero gamma (J π) (K_c π)

end ActinfPolicyEntanglement
