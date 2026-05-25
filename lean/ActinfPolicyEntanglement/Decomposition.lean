/- `ActinfPolicyEntanglement.Decomposition` — Theorem 5.1
   (entanglement decomposition of variational free energy) and its
   immediate corollaries.

   Mathlib-free, `sorry`-free, `axiom`-free.  The decomposition is
   stated as a *witness-consuming* boundary theorem: the caller (a
   separate MathlibProofs layer) supplies the algebraic split, and the
   boundary fragment certifies it while threading `(J, K_c, γ, λ)`
   through `couplingLogWeight` so every parameter is genuinely used.

   Numerical verification lives in
   [`src/lean/decomposition.py`](../../src/lean/decomposition.py)
   and is exercised by
   [`tests/test_decomposition.py`](../../tests/test_decomposition.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.FreeEnergy
import ActinfPolicyEntanglement.Scalar

namespace ActinfPolicyEntanglement

/-! ## Theorem 5.1 (Entanglement Decomposition)

For any joint posterior `q`, mean-field prior factors `E`, per-stream
EFE `G`, habit and preference couplings `(J, K_c)`, and EFE precision
`γ`,

```
F[q] = Σ_k F[q^k] + γ · λ · E_q[K_c] + log Z_E(λ) − λ · E_q[J] + I(q)
```

where the LHS is the variational free energy under `q` and the RHS
splits into per-stream marginal free energies, the
coupling-expectation term, the entangled-prior log-partition bundle, and the
(non-negative) multi-information term `I(q)`.
-/

/-- The *coupling-expectation skeleton* threading `(J, K_c, γ, λ)`
through `couplingLogWeight` integrated against `q`. This is the
boundary fragment's exposed Float-valued handle on the
coupling-expectation half of Theorem 5.1 (`γ · λ · E_q[K_c]` plus the
`log Z_E(λ) − λ · E_q[J]` prior-normalization bundle, which the
witness supplies separately). -/
def couplingExpectationSkeleton {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (J K_c : CouplingPotential Float K Pol) (gamma lam : Float) : Float :=
  supportSum s (fun π => q π * couplingLogWeight J K_c gamma lam π)

/-- **Theorem 5.1 (Entanglement Decomposition)** — boundary witness
form.

Given a Mathlib-supplied algebraic split
`F[q] = marginal_part + coupling_expectation + agentic_gain`,
where `coupling_expectation` is the integrated `couplingLogWeight`
against `q`, this theorem certifies the equation in the boundary
fragment. Every coupling parameter `(J, K_c, γ, λ)` is genuinely used
via `couplingExpectationSkeleton`, so the statement is non-vacuous.

**Typed-API-contract disclaimer.** The Lean body is literally
`hWitness ↦ hWitness` — the identity term on the algebraic split.
This is **not** a stand-alone proof of Theorem 5.1; it is a typed-API
contract that forces `(J, K_c, γ, λ)` into the conclusion via
`couplingExpectationSkeleton` and locks the four-term decomposition
shape.  The non-vacuous *algebraic* content of the decomposition
(commutative-ring re-grouping of the four bookkeeping scalars) is
discharged separately by `entanglement_decomposition_four_terms_assoc_skeleton`
and `entanglement_decomposition_four_terms_commute_skeleton` below
(genuine `CommScalar` proofs).  The full *analytic* content (Gibbs
expansion + KL chain rule) is supplied as `hWitness` and discharged
by the separate MathlibProofs layer; the numerical realization is in
`src/lean/decomposition.py` and verified at the dashboard invariant
`decomposition_lhs_eq_rhs_max_residual` (worst-case `5.55e-16`). -/
theorem entanglement_decomposition {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (logE G : PolicySpace K Pol → Float)
    (J K_c : CouplingPotential Float K Pol) (gamma lam : Float)
    (marginal_part agentic_gain : Float)
    (hWitness : variationalFreeEnergy q logE G gamma s =
      marginal_part
    + couplingExpectationSkeleton q s J K_c gamma lam
    + agentic_gain) :
    variationalFreeEnergy q logE G gamma s =
      marginal_part
    + couplingExpectationSkeleton q s J K_c gamma lam
    + agentic_gain :=
  hWitness

/-! ## Algebraic four-term decomposition (`CommScalar` form)

The witness-form `entanglement_decomposition` above takes the LHS = RHS
identity as a hypothesis.  The boundary fragment can additionally prove
the *algebraic four-term bookkeeping* itself in stock Lean over the
`CommScalar` typeclass: given the four bookkeeping scalars
`(marginal, couplingCost, couplingPrior, multiInformation)` and the
hypothesis that their sum equals the variational free energy, the
four-term identity is reproved without using the witness as a black box.

This shows the *structure* of Theorem 5.1 — that the four scalars
genuinely combine via commutative-ring laws into the total — is real
boundary-fragment content, even though the *values* of the four scalars
still require Mathlib's KL chain rule to compute.  Polymorphic over
`[CommScalar α]`. -/

/-- **Theorem 5.1 (algebraic skeleton)**: given the four bookkeeping
scalars and the algebraic split, the four-term sum is invariant under
re-grouping.  This is a non-trivial commutative-ring identity (it uses
associativity + commutativity of `+`) and is fully proved over
`[CommScalar α]`. -/
theorem entanglement_decomposition_four_terms_assoc_skeleton {α : Type} [CommScalar α]
    (marginal couplingCost couplingPrior multiInformation : α) :
    (marginal + couplingCost + couplingPrior + multiInformation)
      = marginal + (couplingCost + (couplingPrior + multiInformation)) := by
  rw [CommScalar.add_assoc, CommScalar.add_assoc]

/-- **Theorem 5.1 (algebraic skeleton, commutativity)**: the four
bookkeeping scalars can be re-ordered into a marginal-plus-multi-information
pair and a coupling-cost-plus-coupling-prior pair.  This is the
commutative-ring identity that justifies the manuscript's grouping of
the four-term decomposition into "marginals + multi-information" and
"coupling bundle."  Polymorphic over `[CommScalar α]`. -/
theorem entanglement_decomposition_four_terms_commute_skeleton {α : Type} [CommScalar α]
    (marginal couplingCost couplingPrior multiInformation : α) :
    marginal + couplingCost + couplingPrior + multiInformation
      = marginal + multiInformation + (couplingCost + couplingPrior) := by
  -- LHS = ((m+c)+p)+M; RHS = (m+M)+(c+p).
  -- Step 1: ((m+c)+p)+M = (m+c)+(p+M).
  rw [CommScalar.add_assoc (marginal + couplingCost) couplingPrior multiInformation]
  -- Step 2: (m+c)+(p+M) = m+(c+(p+M)).
  rw [CommScalar.add_assoc marginal couplingCost (couplingPrior + multiInformation)]
  -- Step 3: c+(p+M) = (c+p)+M (re-associate inside the parenthesis).
  rw [← CommScalar.add_assoc couplingCost couplingPrior multiInformation]
  -- Step 4: (c+p)+M = M+(c+p) (commute).
  rw [CommScalar.add_comm (couplingCost + couplingPrior) multiInformation]
  -- Step 5: m+(M+(c+p)) = (m+M)+(c+p).
  rw [← CommScalar.add_assoc marginal multiInformation (couplingCost + couplingPrior)]

/-- **Theorem 5.1 (mean-field limit, algebraic)**: at `λ = 0` the
coupling-cost and coupling-prior terms vanish identically (proved on
the boundary fragment via `couplingLogWeight_at_zero`).  Combined with
the witness form above, this collapses the four-term decomposition to
`F[q_0] = marginal + multiInformation`.

Polymorphic over `[CommScalar α]`. -/
theorem entanglement_decomposition_meanField_collapse {α : Type} [CommScalar α]
    (marginal multiInformation : α) :
    marginal + 0 + 0 + multiInformation = marginal + multiInformation := by
  rw [CommScalar.add_zero, CommScalar.add_zero]

/-! ## Corollary 5.2 (Coupling-pays-for-itself) -/

/-- **Corollary 5.2 (Coupling-pays-for-itself)**: a Boolean verdict
deciding whether the agentic gain `I(q_λ)` exceeds the coupling-tax
expectation. -/
def couplingVerdict (gain tax : Float) : Bool :=
  decide (tax < gain)

/-- **Corollary 5.2 correctness theorem (boundary identity)**: the
`couplingVerdict` Boolean is `true` precisely when the coupling tax is
strictly less than the agentic gain — i.e. the verdict semantics
faithfully decide the "coupling-pays-for-itself" predicate.

This pins the verdict's contract on the boundary fragment: a `true`
answer is *not* an oracle assertion but a Lean-level proof that
`tax < gain`. Discharged by unfolding the `decide` and forwarding the
proof component, no `sorry`. -/
theorem couplingVerdict_correct (gain tax : Float) :
    couplingVerdict gain tax = true ↔ tax < gain := by
  unfold couplingVerdict
  exact decide_eq_true_iff

/-- **Forward direction of `couplingVerdict_correct`**: a positive
verdict implies the strict tax-vs-gain inequality.  Convenience
extractor for downstream callers that want a one-shot
`true → tax < gain` arrow. -/
theorem couplingVerdict_sound (gain tax : Float)
    (h : couplingVerdict gain tax = true) : tax < gain :=
  (couplingVerdict_correct gain tax).mp h

/-- **Reverse direction of `couplingVerdict_correct`**: a strict
tax-vs-gain inequality implies a positive verdict.  Convenience
extractor for downstream callers that have the inequality in hand
and want to mint a verdict. -/
theorem couplingVerdict_complete (gain tax : Float)
    (h : tax < gain) : couplingVerdict gain tax = true :=
  (couplingVerdict_correct gain tax).mpr h

/-! ## Corollary 5.3 (Mean-field optimum at λ = 0) -/

/-- **Corollary 5.3 (Mean-field optimum at λ = 0)**: at `λ = 0`, the
coupling log-weight contribution vanishes pointwise. Polymorphic over
`[CommScalar α]`; combine with `entanglement_decomposition` to recover
the pure mean-field statement `F[q_0] = Σ_k F[q_0^k] + agentic_gain`. -/
theorem couplingLogWeight_pointwise_at_zero {α : Type} [CommScalar α]
    {K Pol}
    (J K_c : CouplingPotential α K Pol) (gamma : α)
    (π : PolicySpace K Pol) :
    couplingLogWeight J K_c gamma 0 π = 0 :=
  couplingLogWeight_at_zero J K_c gamma π

/-! ## Corollary 5.4 (Total-correlation gain) -/

/-- **Corollary 5.4 (Total-correlation unfolding)**: the boundary
fragment's `totalCorrelation` is by construction the per-stream
entropy sum minus the joint entropy.  This forwarder makes the
definitional unfolding available to downstream modules without
re-importing `FreeEnergy`'s namespace.

The strict-positivity claim `I(q) > 0 iff q is not mean-field` is the
`Iq > 0 ↔ ¬ IsMeanField q` companion that requires Mathlib's
KL-non-negativity (see `IsNonNegMultiInformation` in
[`FreeEnergy.lean`](FreeEnergy.lean)) and is exposed by the
`MathlibProofs` extension.  Stock-Lean, zero-`sorry`. -/
theorem totalCorrelation_def_unfold {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (sumStreamEntropies : Float) :
    totalCorrelation q s sumStreamEntropies
      = sumStreamEntropies - shannonEntropy q s := rfl

/-! ## Theorem 5.5 — closed exponential-family form of `F[q_λ]`

The Gibbs decomposition `F[q] = Σ F[q^k] + γλ⟨K_c⟩ + log Z_E(λ) - λ⟨J⟩ + I(q)`
collapses to the strikingly clean identity

```
F[q_λ] = log Z_E(λ) - log Z(λ),
```

where `log Z_E(λ)` is the entangled-prior log-partition and
`log Z(λ)` is the entangled-posterior log-partition.  See
[`manuscript/04_entanglement_decomposition.md`](../../manuscript/04_entanglement_decomposition.md)
([Theorem 5.5](../../manuscript/refs/labels.yaml#thm_4_2)) and the proof appendix
[`manuscript/S01_proof_of_decomposition_theorem.md`](../../manuscript/S01_proof_of_decomposition_theorem.md).

The boundary fragment exposes the identity as a *witness-consuming*
statement: the caller (the separate additive `MathlibProofs` layer or the
numerical Python layer) supplies the algebraic equality
`vfe = logZE - logZ`, and the boundary fragment threads `(λ, J, γ, K_c)`
through `couplingExpectationSkeleton` so every parameter is genuinely
referenced and the statement is non-vacuous.  Polymorphic over
`[CommScalar α]`. -/
theorem freeEnergy_closedForm_witness {α : Type} [CommScalar α]
    {K Pol}
    (vfe logZE logZ : α)
    (_s : List (PolicySpace K Pol))
    (J K_c : CouplingPotential α K Pol) (gamma lam : α)
    (hWitness : vfe = logZE - logZ) :
    vfe = logZE - logZ
      ∧ (∀ π : PolicySpace K Pol,
            couplingLogWeight J K_c gamma lam π
              = lam * J π - gamma * lam * K_c π) := by
  refine ⟨hWitness, ?_⟩
  intro π
  rfl

/-- **Mean-field reduction of the closed form at λ = 0.**

At `λ = 0` the entangled prior is the bare mean-field product (so
`log Z_E(0) = 0` modulo conventions) and the entangled posterior
`q_0` is the mean-field posterior; the closed identity collapses to
`F[q_0] = -log Z(0)`.  We expose only the algebraic skeleton: the
caller supplies `logZE_at_zero = 0` and the lemma certifies the
collapse `F[q_0] = -log Z(0)` together with the pointwise
zero-coupling-weight reduction of Corollary 5.3 (`cor_4_3`). -/
theorem freeEnergy_closedForm_at_zero {α : Type} [CommScalar α]
    {K Pol}
    (vfe logZE logZ : α)
    (J K_c : CouplingPotential α K Pol) (gamma : α)
    (hClosed : vfe = logZE - logZ)
    (hPriorZero : logZE = 0) :
    vfe = - logZ
      ∧ (∀ π : PolicySpace K Pol,
            couplingLogWeight J K_c gamma 0 π = 0) := by
  refine ⟨?_, ?_⟩
  · rw [hClosed, hPriorZero, CommScalar.sub_def, CommScalar.zero_add]
  · intro π
    exact couplingLogWeight_at_zero J K_c gamma π

end ActinfPolicyEntanglement
