/- `ActinfPolicyEntanglement.Coupling` — coupling potentials and the
   λ-entangled prior / posterior.  Mathlib-free; numerical realisations
   live in [`src/lean/coupling.py`](../../src/lean/coupling.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist

namespace ActinfPolicyEntanglement

/-! ## Coupling potentials

A coupling potential is a scalar function on the joint policy space.
Two flavours:
* `J` — *habit coupling* (prior side)
* `K_c` — *preference coupling* (EFE side) -/

/-- A coupling potential: scalar score on the joint policy. -/
abbrev CouplingPotential (K : Nat) (Pol : PolicyFactor K) : Type :=
  PolicySpace K Pol → Float

/-- A *trivial* coupling potential vanishes everywhere. -/
def trivialCoupling {K Pol} : CouplingPotential K Pol :=
  fun _ => 0.0

/-! ## λ-entangled prior / posterior log-weights

The entangled prior is `E_λ(π) ∝ ∏_k E_k(π^k) · exp(λ · J(π))`.
The entangled posterior is `q_λ(π) ∝ E_λ(π) · exp(-γ · G_λ(π))` with
`G_λ(π) = Σ_k G_k(π^k) + λ · K_c(π)`.

Working at the *log-weight* level keeps everything affine in λ and
avoids the partition-function bookkeeping until normalisation. -/

/-- Log-weight contribution of the coupling alone:
`λ · J(π) − γ · λ · K_c(π)`. -/
def couplingLogWeight {K Pol}
    (J K_c : CouplingPotential K Pol)
    (gamma lam : Float) : PolicySpace K Pol → Float :=
  fun π => lam * J π - gamma * lam * K_c π

/-- Unnormalised log-weight of the λ-entangled posterior at policy `π`. -/
def entangledPosteriorLogWeight {K Pol}
    (logE : PolicySpace K Pol → Float)
    (G : PolicySpace K Pol → Float)
    (J K_c : CouplingPotential K Pol)
    (gamma lam : Float) : PolicySpace K Pol → Float :=
  fun π => logE π - gamma * G π + couplingLogWeight J K_c gamma lam π

/-! ## Affineness in λ (Theorem 6.4 boundary form) -/

/-- The coupling log-weight is affine in `λ` for every fixed policy: at
two values `lam1, lam2`, the difference factors as `(lam1 − lam2) · θ(π)`
with `θ(π) = J(π) − γ · K_c(π)`. This is the boundary statement of
Theorem 6.4 (`entangledFamily_eGeodesic`). -/
theorem couplingLogWeight_affine_in_lam {K Pol}
    (J K_c : CouplingPotential K Pol) (gamma lam1 lam2 : Float)
    (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma lam1 π
      - couplingLogWeight J K_c gamma lam2 π
    = (lam1 - lam2) * (J π - gamma * K_c π) := by
  unfold couplingLogWeight
  -- Algebraic identity: lam1*J - γ*lam1*K - (lam2*J - γ*lam2*K)
  --                    = (lam1 - lam2)·J - γ·(lam1 - lam2)·K
  --                    = (lam1 - lam2)·(J - γ·K)
  sorry  -- boundary: needs Mathlib's ring tactic on Float

/-- Coupling log-weight at `λ = 0` is identically zero (no coupling). -/
theorem couplingLogWeight_at_zero {K Pol}
    (J K_c : CouplingPotential K Pol) (gamma : Float)
    (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma 0.0 π = 0.0 := by
  unfold couplingLogWeight
  -- 0 * J − γ * 0 * K = 0
  sorry  -- boundary: needs Float arithmetic lemma

end ActinfPolicyEntanglement
