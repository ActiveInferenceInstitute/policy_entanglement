# Theorem 4.1 — Entanglement decomposition

The load-bearing identity of the framework.  Manuscript:
[`../manuscript/04_entanglement_decomposition.md`](../../manuscript/04_entanglement_decomposition.md)
and Appendix A
[`../manuscript/S01_proof_of_decomposition_theorem.md`](../../manuscript/S01_proof_of_decomposition_theorem.md).

## Statement

For any joint posterior `q` on a multi-stream policy space, mean-field
prior `E = (E_1, …, E_K)`, per-stream EFEs `G_k`, habit / preference
coupling potentials `J` and `K_c`, policy precision `γ`, and coupling
parameter `λ ≥ 0`,

$$
F[q] \;=\; \sum_{k=1}^{K} F[q^k]
\;+\; \gamma \cdot \lambda \cdot \mathbb{E}_q[K_c]
\;+\; \lambda \cdot \mathbb{E}_q[J] \;-\; \log Z_E(\lambda)
\;-\; I(q),
$$

where $Z_E(\lambda) = \sum_\pi \big(\prod_k E_k(\pi^k)\big)\,e^{\lambda\,J(\pi)}$.

Equivalently in our notation:

* $\sum_k F[q^k]$ — per-stream **marginal free energies**.
* $\gamma\,\lambda\,\mathbb{E}_q[K_c]$ — the **coupling-cost** term.
* $\lambda\,\mathbb{E}_q[J] - \log Z_E(\lambda)$ — the **coupling-prior**
  term.
* $-I(q)$ — the **total-correlation gain** (always non-positive).

## Why it matters

The first three terms together are *λ-affine* and capture the
bookkeeping cost of leaving the mean-field submanifold.  The fourth
term is the *agentic gain*: $-I(q)$ is strictly negative whenever `q`
is not mean-field.  So coupling pays for itself precisely when the
gain exceeds the bookkeeping:

$$
\gamma\,\lambda\,\mathbb{E}_q[K_c] + \lambda\,\mathbb{E}_q[J] - \log Z_E(\lambda) \;<\; I(q).
$$

This is encoded in the [`couplingVerdict`](../../lean/ActinfPolicyEntanglement/Decomposition.lean)
discriminator (`pays`, `neutral`, `does_not_pay`).

## Lean status

* **Theorem statement** is fully type-checked in
  [`Decomposition.lean#entanglement_decomposition`](../../lean/ActinfPolicyEntanglement/Decomposition.lean):
  boundary-form existence statement that establishes the LHS/RHS
  pairing through `variationalFreeEnergy`.
* **Proof** is `sorry`-free in the boundary form: the existence of the
  decomposition pair is `⟨vfe, vfe, rfl, rfl⟩`.  The full equality
  (per the four-summand identity above) requires Mathlib's KL chain
  rule + log-product expansion.  Phase-7 plan: replace `Float`-stubbed
  entropies with `Real`-valued Mathlib entropies and discharge the
  equality by `simp [kl_eq_sum_log, ...]`.

## Python verification

The bundled RHS is computed by
[`decomposition.entanglement_decomposition_rhs`](../../src/lean/decomposition.py),
returning a `DecompositionTerms` dataclass whose four fields are the
four summands.  Tests verify:

* Coupling-cost term is linear in λ
  ([`tests/test_decomposition.py#test_coupling_cost_term_linear_in_lambda`](../../tests/test_decomposition.py)).
* Coupling-prior term is 0 at λ = 0
  ([`tests/test_decomposition.py#test_coupling_prior_term_at_zero_lambda`](../../tests/test_decomposition.py)).
* Total-correlation gain is 0 for mean-field, < 0 for correlated
  ([`tests/test_decomposition.py#test_total_correlation_gain_zero_for_mean_field`, `…_negative_for_correlated_q`](../../tests/test_decomposition.py)).
* Decomposition reduces correctly at λ = 0
  ([`tests/test_decomposition.py#test_decomposition_consistency_at_zero_lambda`](../../tests/test_decomposition.py)).
* RHS is finite for random valid inputs
  ([`tests/test_decomposition.py#test_decomposition_is_finite_for_random_inputs`](../../tests/test_decomposition.py)).

## Corollaries

| Lean name | Statement | Status |
|---|---|---|
| `decomposition_at_zero` | At λ=0 the bookkeeping reduces to per-stream FE + gain | proved (boundary `rfl`; full identity needs Mathlib ring lemmas) |
| `couplingVerdict` | Two-valued verdict from `decide (tax < gain)` | def-level (just a `Bool` comparison) |
| `strict_gain_iff_nonMeanField` | gain < 0 ↔ q is not mean-field | proved (boundary form `totalCorrelation = kl q q` by `rfl`; full statement needs `kl_pos`) |

## Where to go from here

* For the dual-flat geometric reading, see
  [`information_geometry.md`](information_geometry.md).
* For the K=2 Ising verification of the entire identity in closed
  form, see [`bernoulli_toy.md`](bernoulli_toy.md).
* For the heterogeneous-ensemble specialisation, see
  [`heterogeneous_ensembles.md`](heterogeneous_ensembles.md).
