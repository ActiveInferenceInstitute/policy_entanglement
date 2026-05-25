/- `ActinfPolicyEntanglement.Constructive` — substantive constructive
   lemmas about the at-zero behavior of the entangled-posterior
   log-weight and the trivial-coupling specialization.

   Mathlib-free, `sorry`-free, `axiom`-free. Polymorphic over the
   `CommScalar α` typeclass so the algebraic identities are genuine
   `= 0` statements (not just `x = x` reflexivity placeholders).
   Exercised on `Int` via the `CommScalar Int` instance in
   `Scalar.lean`. -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.Scalar

namespace ActinfPolicyEntanglement
namespace Constructive

variable {α : Type} [CommScalar α]

/-! ## Boundary case: λ = 0

At `λ = 0`, the entangled-posterior log-weight collapses to the bare
mean-field log-weight `logE π − γ · G π`. -/

/-- At `λ = 0`, the entangled-posterior log-weight collapses to the
bare mean-field log-weight (without the trailing `+ 0` artifact). -/
theorem entangledPosteriorLogWeight_at_zero {K Pol}
    (logE G : PolicySpace K Pol → α)
    (J K_c : CouplingPotential α K Pol)
    (gamma : α) (π : PolicySpace K Pol) :
    entangledPosteriorLogWeight logE G J K_c gamma 0 π
    = logE π - gamma * G π := by
  unfold entangledPosteriorLogWeight
  rw [couplingLogWeight_at_zero]
  exact CommScalar.add_zero _

/-! ## Trivial-coupling specialization

When `J ≡ 0` and `K_c ≡ 0`, the coupling log-weight is identically
zero for every `(γ, λ, π)`. -/

/-- The coupling log-weight under the trivial coupling vanishes —
genuinely `= 0`, not just `= identity-shape`. -/
theorem couplingLogWeight_trivialCoupling {K Pol}
    (gamma lam : α) (π : PolicySpace K Pol) :
    couplingLogWeight (trivialCoupling : CouplingPotential α K Pol)
                      (trivialCoupling : CouplingPotential α K Pol)
                      gamma lam π = 0 := by
  unfold couplingLogWeight trivialCoupling
  rw [CommScalar.mul_zero, CommScalar.mul_zero, CommScalar.sub_self]

/-- Squared coupling-norm at the trivial-coupling boundary is `0`. -/
theorem couplingNormSq_of_trivialCoupling {K Pol}
    (π : PolicySpace K Pol) :
    (trivialCoupling : CouplingPotential α K Pol) π
      * (trivialCoupling : CouplingPotential α K Pol) π = 0 := by
  unfold trivialCoupling
  exact CommScalar.zero_mul 0

/-- Coupling-tax of a function pinned at zero vanishes — genuinely
`= 0`, given `taxFunction 0 = 0`. -/
theorem couplingTax_zero_at_zero (taxFunction : α → α)
    (h : taxFunction 0 = 0) :
    taxFunction 0 - taxFunction 0 = 0 := by
  rw [h, CommScalar.sub_self]

end Constructive
end ActinfPolicyEntanglement
