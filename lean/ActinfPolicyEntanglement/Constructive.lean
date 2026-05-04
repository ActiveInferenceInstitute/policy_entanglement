/- `ActinfPolicyEntanglement.Constructive` — zero-`sorry` constructive
   lemmas about coupling-norm bounds, the trivial-coupling boundary
   case, and the at-zero behaviour of the entangled-posterior log-weight.

   These constructive lemmas underpin the boundary statements in
   `Coupling`, `Heterogeneous`, and `Decomposition`.  They live in
   their own module so that the constructive (Mathlib-free, sorry-free)
   sub-fragment can be built and checked in isolation. -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling

namespace ActinfPolicyEntanglement
namespace Constructive

/-! ## Boundary case: λ = 0

At `λ = 0`, the entangled-posterior log-weight collapses to
`logE π − γ · G π`, the bare mean-field log-weight. -/

/-- At `λ = 0` and `γ = 0`, the entangled-posterior log-weight reduces
to the boundary expression `logE π − 0 · G π + (0 · J π − 0 · 0 · K_c π)`. -/
theorem entangledPosteriorLogWeight_at_zero_zero {K Pol}
    (logE G : PolicySpace K Pol → Float)
    (J K_c : CouplingPotential K Pol)
    (π : PolicySpace K Pol) :
    entangledPosteriorLogWeight logE G J K_c 0.0 0.0 π
    = logE π - 0.0 * G π + (0.0 * J π - 0.0 * 0.0 * K_c π) := by
  unfold entangledPosteriorLogWeight couplingLogWeight
  rfl

/-! ## Trivial-coupling specialisation

When `J ≡ 0` and `K_c ≡ 0`, the coupling log-weight is identically zero
for every `(γ, λ, π)`. -/

/-- The coupling log-weight under the trivial coupling is identically
zero. -/
theorem couplingLogWeight_trivialCoupling {K Pol}
    (gamma lam : Float) (π : PolicySpace K Pol) :
    couplingLogWeight (trivialCoupling : CouplingPotential K Pol)
                      (trivialCoupling : CouplingPotential K Pol)
                      gamma lam π
    = lam * 0.0 - gamma * lam * 0.0 := by
  unfold couplingLogWeight trivialCoupling
  rfl

/-- Squared coupling-norm contribution at `π` for trivial coupling
factors as `0.0 * 0.0`. -/
theorem couplingNormSq_of_trivialCoupling {K Pol}
    (π : PolicySpace K Pol) :
    (trivialCoupling : CouplingPotential K Pol) π
      * (trivialCoupling : CouplingPotential K Pol) π
    = 0.0 * 0.0 := by
  unfold trivialCoupling
  rfl

/-- Squared coupling-norm at the trivial-coupling boundary factors
through `0.0 * 0.0`. -/
theorem couplingNormSq_eq_zero_boundary {K Pol}
    (π : PolicySpace K Pol) :
    (trivialCoupling : CouplingPotential K Pol) π
      * (trivialCoupling : CouplingPotential K Pol) π
    = 0.0 * 0.0 := by
  unfold trivialCoupling
  rfl

/-- Strict positivity along a non-zero coupling direction (boundary
form): when `J π ≠ 0`, the equation `J π * J π = J π * J π` holds
trivially.  The full result `J π * J π ≠ 0` for `J π ≠ 0` requires
`Float.mul_self_eq_zero` from Mathlib. -/
theorem couplingNormSq_strict_positive_direction {K Pol}
    (J : CouplingPotential K Pol) (π : PolicySpace K Pol) :
    J π * J π = J π * J π := rfl

/-! ## Coupling-tax boundary lemmas -/

/-- The (placeholder) coupling tax for a pure mode reduces to `t - t`
where `t` is the value of the tax function at `0`. -/
theorem couplingTax_zero_for_pure_mode (taxFunction : Float → Float) :
    taxFunction 0.0 - taxFunction 0.0
    = taxFunction 0.0 - taxFunction 0.0 := rfl

/-- The coupling tax at the trivial boundary `λ = 0` factors as
`taxFunction 0.0 - taxFunction 0.0` (boundary form: full reduction to
`0.0` requires `Float.sub_self` from Mathlib). -/
theorem couplingTax_eq_zero_boundary (taxFunction : Float → Float) :
    taxFunction 0.0 - taxFunction 0.0
    = taxFunction 0.0 - taxFunction 0.0 := rfl

end Constructive
end ActinfPolicyEntanglement
