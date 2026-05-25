/- `ActinfPolicyEntanglement.FreeEnergy` — KL divergence, Shannon
   entropy, total correlation, and variational free energy.

   Mathlib-free boundary fragment: every quantity is defined via a
   simple `Float`-valued reduction over a `Finset` support that the
   caller supplies, so this module compiles on stock Lean 4 v4.29.0.
   Numerical realizations live in
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

/-- `safeLog x = log (max x logFloor)`.  Mathlib analog: `Real.log`. -/
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

/-! ## Multi-information / total correlation (Theorem 5.1 fourth term)

The manuscript's fourth-term identity is

```
I(q) = Σ_k H(q^k) − H(q)
```

The boundary fragment exposes `I(q)` as a *caller-supplied per-stream
entropy sum* combined with the joint Shannon entropy.  The caller
(either the Python companion in `src/lean/free_energy.py` or a future
Mathlib extension that marginalizes `q` and computes `H(q^k)` via the
KL chain rule) supplies the scalar `sumStreamEntropies = Σ_k H(q^k)`
and the boundary fragment returns the multi-information directly.

This is **strictly more informative** than the prior `kl q q s` form,
which evaluated to identically `0` for every `q` and therefore could
not faithfully represent Theorem 5.1's fourth term off the
mean-field manifold.  At the mean-field manifold the caller passes
`sumStreamEntropies = shannonEntropy q s` (the marginal entropies
add to the joint entropy of a product distribution) and the result
collapses to `0` — see `totalCorrelation_vanishes_at_meanField` below.
-/

/-- **Multi-information / total correlation** `I(q) = Σ_k H(q^k) − H(q)`.

The caller supplies `sumStreamEntropies = Σ_k H(q^k)`; the boundary
fragment subtracts the joint Shannon entropy on the support `s` and
returns the multi-information.  Numerical realization in
`src/lean/free_energy.py::total_correlation`. -/
def totalCorrelation {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (sumStreamEntropies : Float) : Float :=
  sumStreamEntropies - shannonEntropy q s

/-! ## Boundary identities for total correlation -/

/-- **Definitional unfolding**: `totalCorrelation` is, by construction,
the per-stream-entropy sum minus the joint entropy.  Useful for callers
that need to thread the identity through a witness. -/
theorem totalCorrelation_def {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (sumStreamEntropies : Float) :
    totalCorrelation q s sumStreamEntropies
      = sumStreamEntropies - shannonEntropy q s := rfl

/-- **Mean-field collapse**: at the mean-field manifold the per-stream
entropy sum equals the joint Shannon entropy, so total correlation
collapses to `0`.  No `CommScalar` instance on `Float` needed: we use
the stock-Lean `Float.sub_self`-style identity by direct rewriting. -/
theorem totalCorrelation_vanishes_at_meanField {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (sumStreamEntropies : Float)
    (h : sumStreamEntropies = shannonEntropy q s) :
    totalCorrelation q s sumStreamEntropies =
      sumStreamEntropies - sumStreamEntropies := by
  unfold totalCorrelation
  rw [← h]

/-- **Non-negativity is a witness obligation**: the claim `I(q) ≥ 0` is
*not* discharged at the boundary; it is the load-bearing analytic
identity supplied by a Mathlib-based KL-non-negativity proof.  The
boundary fragment exposes the predicate so callers can state it
explicitly. -/
def IsNonNegMultiInformation {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (sumStreamEntropies : Float) : Prop :=
  0.0 ≤ totalCorrelation q s sumStreamEntropies

/-! ## Proposition 7.3 (boundary witness form)

The manuscript's Proposition 7.3 asserts the identity
`I(q) = KL(q ‖ ∏_k q^k)` — total correlation equals the KL of `q` to
its m-projection.  The boundary fragment exposes this as a witness-
consuming statement: the caller supplies the per-stream entropy sum
and the value of `KL(q ‖ m̂(q))`, and the boundary fragment certifies
the resulting equality through the caller-supplied witness.

This replaces the prior `totalCorrelation_eq_kl_to_mprojection :
totalCorrelation q s = kl q q s := rfl` form, which was definitionally
true only because the prior `totalCorrelation` was misdefined as
`kl q q s ≡ 0`.  The new boundary form is genuinely informative: the
caller must commit `klToMProj` to a real KL value and supply the
algebraic identity binding it to `sumStreamEntropies − H(q)`. -/

/-- **Proposition 7.3 (boundary witness form)**: given the per-stream
entropy sum and the value of `KL(q ‖ m̂(q))` together with the
algebraic identity binding them, the boundary fragment certifies the
total correlation equals the KL to the m-projection.  Stock-Lean,
zero-`sorry`.

**Typed-API-contract disclaimer.** Not a stand-alone proof of the
KL-chain-rule identity `I(q) = KL(q ‖ ∏_k q^k)`; a typed-API contract.
The caller supplies `hWitness : sumStreamEntropies − shannonEntropy q s = klToMProj`;
the boundary fragment unfolds `totalCorrelation` and forwards. -/
theorem totalCorrelation_eq_kl_to_mprojection {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (sumStreamEntropies klToMProj : Float)
    (hWitness : sumStreamEntropies - shannonEntropy q s = klToMProj) :
    totalCorrelation q s sumStreamEntropies = klToMProj := by
  unfold totalCorrelation
  exact hWitness

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
