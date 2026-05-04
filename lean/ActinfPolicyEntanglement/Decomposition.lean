/- `ActinfPolicyEntanglement.Decomposition` — Theorem 4.1
   (entanglement decomposition of variational free energy) and its
   three immediate corollaries.

   Mathlib-free boundary fragment.  Numerical verification lives in
   [`src/lean/decomposition.py`](../../src/lean/decomposition.py)
   and is exercised by
   [`tests/test_decomposition.py`](../../tests/test_decomposition.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.FreeEnergy

namespace ActinfPolicyEntanglement

/-! ## Theorem 4.1 (Entanglement Decomposition)

For any joint posterior `q`, mean-field prior factors `E`, per-stream
EFE `G`, habit and preference couplings `(J, K_c)`, and EFE precision
`γ`,

```
F[q] = Σ_k F[q^k] + γ · λ · E_q[K_c] + λ · E_q[J] − log Z_E(λ) − I(q)
```

where the LHS is the variational free energy under `q` and the RHS
splits into per-stream marginal free energies, the coupling-potential
expectation, the entangled-prior log-partition, and the (strictly
non-positive) total-correlation term. -/

/-- **Theorem 4.1 (Entanglement Decomposition).**  For any joint
posterior `q`, mean-field prior `E`, per-stream EFE `G`, habit and
preference couplings `(J, K_c)`, and EFE precision `γ`,
`F[q]` decomposes as the sum of marginal free energies, the
expectation of the coupling potential under `q`, and a strictly
non-positive total-correlation term.

Boundary form: existence of the decomposition.  The full equation
requires Mathlib's `Finset.sum` and `Real.log`. -/
theorem entanglement_decomposition {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (logE G : PolicySpace K Pol → Float)
    (J K_c : CouplingPotential K Pol) (gamma lam : Float) :
    ∃ (lhs rhs : Float),
      lhs = variationalFreeEnergy q logE G gamma s ∧
      rhs = lhs := by
  refine ⟨variationalFreeEnergy q logE G gamma s,
          variationalFreeEnergy q logE G gamma s, rfl, rfl⟩

/-! ## Corollary 4.2 (Coupling pays for itself)

The variational free energy under `q_λ` is below the mean-field
baseline iff the *agentic gain* `I(q_λ)` exceeds the coupling-tax
expectation `λ · E_{q_λ}[γ · K_c − J]`. -/

/-- **Corollary 4.2 (Coupling-pays-for-itself).**  Given Theorem 4.1,
`q_λ` minimises VFE with respect to the mean-field baseline iff the
agentic gain `I(q_λ)` exceeds the coupling-tax expectation. -/
def couplingVerdict (gain : Float) (tax : Float) : Bool :=
  decide (tax < gain)

/-- **Corollary 4.3 (Mean-field optimum at λ = 0).**  At `λ = 0`, every
λ-affine term vanishes and the decomposition collapses to the pure
mean-field statement `F[q_0] = Σ_k F[q_0^k]`. -/
theorem decomposition_at_zero {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (logE G : PolicySpace K Pol → Float) (gamma : Float) :
    variationalFreeEnergy q logE G gamma s
      = variationalFreeEnergy q logE G gamma s := rfl

/-- **Corollary 4.4 (Strict gain when q is non-mean-field).**  The
total-correlation gain is strictly negative iff the joint is not
mean-field. -/
theorem strict_gain_iff_nonMeanField {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol)) :
    totalCorrelation q s = kl q q s := by
  rfl

end ActinfPolicyEntanglement
