# Theorem 5.1 — Entanglement decomposition

The load-bearing identity of the framework.  Manuscript:
[`../manuscript/2D_decomposition.md`](../../manuscript/2D_decomposition.md)
and Appendix A
[`../manuscript/S01_proof_of_decomposition_theorem.md`](../../manuscript/S01_proof_of_decomposition_theorem.md).

## Statement

For any joint posterior `q` on a multi-stream policy space, mean-field
prior `E = (E_1, …, E_K)`, per-stream EFEs `G_k`, habit / preference
coupling potentials `J` and `K_c`, policy precision `γ`, and coupling
parameter `λ ≥ 0`,

$$
F[q_\lambda] \;=\; \sum_{k=1}^{K} F[q^k_\lambda]
\;+\; \gamma \cdot \lambda \cdot \mathbb{E}_{q_\lambda}[K_c]
\;+\; \log Z_E(\lambda) \;-\; \lambda \cdot \mathbb{E}_{q_\lambda}[J]
\;+\; I(q_\lambda),
$$

where $Z_E(\lambda) = \sum_\pi \big(\prod_k E_k(\pi^k)\big)\,e^{\lambda\,J(\pi)}$.

(This is the canonical form registered as `equations::tc_decomp` in
[`manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml) and
proved as a boxed identity in
[`manuscript/S01_proof_of_decomposition_theorem.md`](../../manuscript/S01_proof_of_decomposition_theorem.md);
the [[EQ:tc_decomp]] token resolves to exactly this equation in every
manuscript render.)

Equivalently in our notation:

* $\sum_k F[q^k_\lambda]$ — per-stream **marginal free energies**.
* $\gamma\,\lambda\,\mathbb{E}_{q_\lambda}[K_c]$ — the **coupling-cost**
  term (paid to the habit / preference coupling).
* $\log Z_E(\lambda) - \lambda\,\mathbb{E}_{q_\lambda}[J]$ — the
  **coupling-prior** term (the log-partition surplus minus the
  realized $J$-expectation).
* $+\,I(q_\lambda)$ — the **multi-information penalty**, *non-negative*
  and zero iff $q_\lambda$ is mean-field.

## Why it matters

The first three terms together are *λ-affine* and capture the
bookkeeping cost of leaving the mean-field submanifold.  The fourth
term, $+\,I(q_\lambda) \geq 0$, is a **non-negative penalty** that
records the entropy surplus relative to independent streams with the
same marginals.  In the displayed Gibbs expansion the
total-correlation appears with a **plus** sign: departures from
factorization always *cost* free energy in this bookkeeping.  The
*agentic gain* is hidden in the other terms — specifically in the
combination $\lambda\,\mathbb{E}_{q_\lambda}[J] - \log Z_E(\lambda) -
\gamma\,\lambda\,\mathbb{E}_{q_\lambda}[K_c]$.  Coupling pays for
itself precisely when this explicit gain exceeds the
multi-information penalty:

$$
\lambda\,\mathbb{E}_{q_\lambda}[J] - \log Z_E(\lambda) - \gamma\,\lambda\,\mathbb{E}_{q_\lambda}[K_c] \;>\; I(q_\lambda).
$$

This is encoded in the [`couplingVerdict`](../../lean/ActinfPolicyEntanglement/Decomposition.lean)
discriminator, a two-valued `Bool` defined as `decide (tax < gain)`:
`true` precisely when the coupling tax is strictly less than the
agentic gain, `false` otherwise.  Its `true ↔ tax < gain` contract is
proved as `couplingVerdict_correct` (with one-shot extractors
`couplingVerdict_sound` and `couplingVerdict_complete`).

## Lean status

* **Theorem statement** is fully type-checked in
  [`Decomposition.lean#entanglement_decomposition`](../../lean/ActinfPolicyEntanglement/Decomposition.lean):
  a *witness-consuming* boundary theorem.  The caller supplies the
  Mathlib-side algebraic split as a hypothesis

  ```lean
  (hWitness : variationalFreeEnergy q logE G gamma s =
    marginal_part
  + couplingExpectationSkeleton q s J K_c gamma lam
  + agentic_gain)
  ```

  and the theorem certifies the same equation in the boundary
  fragment.  Every coupling parameter `(J, K_c, γ, λ)` is genuinely
  used via `couplingExpectationSkeleton`, so the statement is
  non-vacuous.
* **Proof** at the Float boundary fragment is a typed witness: the
  Lean body is literally `hWitness` — the identity term on the algebraic
  split.  The non-vacuous algebraic content (commutative-ring
  re-grouping of the four bookkeeping scalars) is discharged
  separately by `entanglement_decomposition_four_terms_assoc_skeleton` and
  `entanglement_decomposition_four_terms_commute_skeleton`.

* **Mathlib ℝ-discharge status (2026-05-19, post-Pass-11).**  The
  central analytic content of Theorem 5.1 is **machine-checked in
  $\mathbb{R}$** by `MathlibProofs.free_energy_decomposition_full` for the
  genuine entangled posterior $q_\lambda$ — positivity and unit mass
  *proved* from the definitions, $\log Z_E$ the genuine definitional
  log-normalizer, the multi-information term discharged through the
  axiom-clean general-$K$ kernel `entanglement_decomposition_generalK`.
  Foundational-only `#print axioms` (`[propext, Classical.choice, Quot.sound]`
  only — no `sorryAx`, no project-axiom), two independent negative
  controls (the `logZE` definitional body and the `γλ⟨K_c⟩` coupling
  term each make the build fail when neutralised), enforced via
  `scripts/build_mathlib_proofs.py` and the automatic pytest gate
  `tests/test_mathlib_axiom_audit.py`.  The Float boundary fragment is
  the typed numerical shadow; the ℝ kernel is where the analytic
  mathematics lives.  Single open residual: a *verified* error-bounded
  Float$\leftrightarrow\mathbb{R}$ bridge, scoped multi-week research
  in [`../reference/methods_and_assumptions.md`](../reference/methods_and_assumptions.md).

## Python verification

The bundled RHS is computed by
[`decomposition.entanglement_decomposition_rhs`](../../src/lean/decomposition.py),
returning a `DecompositionTerms` dataclass whose four fields are the
four summands ($\sum_k F[q^k_\lambda]$, the coupling-cost,
the coupling-prior bundled as $\log Z_E(\lambda) - \lambda\,\mathbb{E}_q[J]$,
and the multi-information $+\,I(q_\lambda)$).  Tests verify:

* Coupling-cost term is linear in λ
  ([`tests/test_decomposition.py#test_coupling_cost_term_linear_in_lambda`](../../tests/test_decomposition.py)).
* Coupling-prior term is 0 at λ = 0
  ([`tests/test_decomposition.py#test_coupling_prior_term_at_zero_lambda`](../../tests/test_decomposition.py)).
* Multi-information term is 0 for mean-field, $>0$ for typical correlated
  joints ([`tests/test_decomposition.py`](../../tests/test_decomposition.py)).
* Decomposition reduces correctly at λ = 0
  ([`tests/test_decomposition.py#test_decomposition_consistency_at_zero_lambda`](../../tests/test_decomposition.py)).
* RHS is finite for random valid inputs
  ([`tests/test_decomposition.py#test_decomposition_is_finite_for_random_inputs`](../../tests/test_decomposition.py)).

## Corollaries

| Lean name | Statement | Status |
|---|---|---|
| `entanglement_decomposition_four_terms_assoc_skeleton` | `(marginal + couplingCost + couplingPrior + multiInformation) = marginal + (couplingCost + (couplingPrior + multiInformation))` — associativity re-grouping | proved (`CommScalar`-polymorphic) |
| `entanglement_decomposition_four_terms_commute_skeleton` | `marginal + couplingCost + couplingPrior + multiInformation = marginal + multiInformation + (couplingCost + couplingPrior)` — commutative re-ordering into the manuscript's two-pair grouping | proved (`CommScalar`-polymorphic) |
| `entanglement_decomposition_meanField_collapse` | `marginal + 0 + 0 + multiInformation = marginal + multiInformation` — λ = 0 collapse | proved (`CommScalar`-polymorphic) |
| `couplingLogWeight_pointwise_at_zero` | At λ=0, the coupling log-weight contribution vanishes pointwise (forwarder to `couplingLogWeight_at_zero`) | proved (`CommScalar`-polymorphic) |
| `couplingVerdict` | Two-valued `Bool` verdict `decide (tax < gain)` | def-level (`Bool` comparison) |
| `couplingVerdict_correct` | `couplingVerdict gain tax = true ↔ tax < gain` (the verdict's contract) | proved |
| `couplingVerdict_sound` | `couplingVerdict gain tax = true → tax < gain` (forward extractor) | proved |
| `couplingVerdict_complete` | `tax < gain → couplingVerdict gain tax = true` (reverse extractor) | proved |
| `totalCorrelation_def_unfold` | `totalCorrelation q s sumStreamEntropies = sumStreamEntropies - shannonEntropy q s := rfl` (definitional unfolding forwarder); the strict-positivity claim needs Mathlib `kl_pos` | proved (`rfl`); strict form is a Mathlib-refinement payload |
| `freeEnergy_closedForm_witness` | Theorem 5.5 (`thm_4_2`), closed exponential-family form: given `hWitness : vfe = logZE - logZ`, certifies `vfe = logZE - logZ ∧ ∀ π, couplingLogWeight J K_c γ λ π = λ·J π − γ·λ·K_c π` | witness (`CommScalar`-polymorphic) |
| `freeEnergy_closedForm_at_zero` | Mean-field reduction of the closed form at λ = 0: given `hClosed` + `logZE = 0`, certifies `vfe = - logZ ∧ ∀ π, couplingLogWeight J K_c γ 0 π = 0` | proved (`CommScalar`-polymorphic) |

## Where to go from here

* For the dual-flat geometric reading, see
  [`information_geometry.md`](information_geometry.md).
* For the K=2 Ising verification of the entire identity in closed
  form, see [`bernoulli_toy.md`](bernoulli_toy.md).
* For the heterogeneous-ensemble specialization, see
  [`heterogeneous_ensembles.md`](heterogeneous_ensembles.md).
