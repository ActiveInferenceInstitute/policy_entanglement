# `MathlibProofs/` — Mathlib4 Scope Note

This directory records the Mathlib4 scope for the policy-entanglement
project. It now contains an independently buildable Lake package with
the headline real-valued free-energy decomposition
(`MathlibProofs.free_energy_decomposition_full`), the general-$K$
finite-KL kernel (`MathlibProofs.entanglement_decomposition_generalK`),
supporting KL / cross-term lemmas, and two small Mathlib rank-plumbing
theorems (`MathlibProofs.vecMulVec_rank_le_one`,
`MathlibProofs.rank_le_one_of_pointwise_factorization`).  The package
builds with 0 `sorry` / `axiom` and is audited by
`scripts/build_mathlib_proofs.py` for foundational-only `#print axioms`
on the keystone declarations. This is the *real-ℝ idealization* of the
headline decomposition; it is still **not** a verified
Float$\leftrightarrow\mathbb{R}$ bridge, and it does not automatically
promote the remaining witness-form rows. The stock-Lean boundary
fragment in [`../ActinfPolicyEntanglement/`](../ActinfPolicyEntanglement/)
remains the validated fast theorem surface; this package is the
separate analytic discharge layer.

## Current Contract

The current boundary build uses stock Lean 4 v4.29.0 under
[`../ActinfPolicyEntanglement/`](../ActinfPolicyEntanglement/) and enforces:

* 0 strict `sorry`;
* 0 `axiom`;
* 0 `unsafe` / `partial` / `noncomputable`;
* 0 `Mathlib` imports in the boundary fragment.

Witness-form theorems expose their analytic payloads as typed `structure`
fields. The boundary fragment checks the API shape and theorem wiring; it
does not pretend that KL chain rules, Bregman expansions, SVD facts, or
measure-tightness lemmas have already been derived inside Mathlib. The
current MathlibProofs theorems prove the headline real-valued
decomposition and validate the separate-package route for future
row-specific witness payloads.

The optional scaffold can be checked with:

```bash
uv run python scripts/build_mathlib_proofs.py
```

That command is separate from `scripts/build_lean.py`; it must not become a
way to smuggle Mathlib imports into the boundary package.

## Where Mathlib4 Belongs

Mathlib4 belongs in a **separate additive library** that imports the boundary
fragment and constructs the existing witness structures from Mathlib lemmas.
That separation is deliberate:

| Reason | Consequence |
|---|---|
| Boundary theorem names stay stable. | Manuscript `[[LEAN:<label>]]` tokens keep resolving to the same declarations. |
| The stock-Lean hygiene gate remains fast and strict. | Accidental Mathlib imports cannot hide `sorry` / axiom regressions in the boundary. |
| Analytic dependencies are explicit. | Each witness says exactly which KL, entropy, convexity, rank, or tightness fact is still external to the boundary. |

## Mathlib4 Target Map

| Boundary witness payload | Mathlib4 area |
|---|---|
| finite KL / entropy chain rule | PMF / finite-measure probability, finite sums, logarithms, and KL-style entropy identities |
| convexity and local Taylor behavior in `λ` | Convex analysis, differentiability / Taylor expansion, real logarithm and exponential facts |
| Bregman / quadratic coupling-tax envelope | Taylor and local convex-analysis primitives; no current Mathlib Bregman module is assumed by the manuscript |
| rank and spectral continuity | Matrix rank, semicontinuity, tensor-product and finite-dimensional linear-algebra infrastructure |
| hierarchical concentration and recursive embedding | measure tightness, KL convergence, and recursive fixed-point infrastructure |

## Implemented Slices

The built slice is intentionally scoped:

| Declaration | Source dependency | What it proves | What it does not prove |
|---|---|---|---|
| `MathlibProofs.free_energy_decomposition_full` | finite real PMFs, log/exp, normalization, general-K KL kernel, cross-term lemmas | the full S01 real-valued free-energy decomposition for the genuine entangled posterior | no Float bridge; no automatic promotion of other witness rows |
| `MathlibProofs.entanglement_decomposition_generalK` | finite sums over strictly-positive normalized real distributions | multi-information non-negativity, KL chain-rule split, and m-projection minimality for general `K` | no Float bridge; no SVD / convexity / tightness payloads |
| `MathlibProofs.klReal_split_via_intermediate` | finite KL algebra | KL split through an intermediate distribution | no standalone theorem-row promotion beyond the compiled headline discharge |
| `MathlibProofs.crossTerm_matches_K2` / `MathlibProofs.crossTerm_matches_of_equal_marginals` | finite marginal algebra | the cross-term identities used by the capstone proof | no Float bridge |
| `MathlibProofs.vecMulVec_rank_le_one` | `Mathlib.LinearAlgebra.Matrix.Rank` / `Matrix.rank_vecMulVec_le` | any matrix outer product has rank at most one | no Proposition 8.1 promotion by itself; no KL/entropy witness is discharged |
| `MathlibProofs.rank_le_one_of_pointwise_factorization` | same rank API plus extensional equality to `Matrix.vecMulVec` | any pointwise-factorized matrix has rank at most one | still no Proposition 8.1 promotion; this is readiness plumbing, not the row-specific discharge |
| `MathlibProofs.klReal_nonneg` | `Real.log_le_sub_one_of_pos`, finite sums over a `Fintype` | KL divergence is non-negative for strictly-positive real finite distributions with both sums equal to one | no Float bridge by itself |
| `MathlibProofs.klReal_self_eq_zero` | real division/log simplification | KL self-distance is zero under strict positivity | no boundary theorem row is promoted |
| `MathlibProofs.klReal_minimises_of_pythagorean` | `klReal_nonneg` plus a supplied Pythagorean identity | m-projection minimality follows from the Pythagorean decomposition and KL non-negativity | the Pythagorean identity itself remains a supplied hypothesis |

## Next Integration Slice

The next coherent slice is real log-partition and convexity:
`thm_4_2`, `thm_4_3`, `prop_10_1`, `thm_8_1`, and `cor_8_2`. Matrix
rank rows and recursive/limit rows should follow once those foundations
exist.

The generated readiness table in
[`../../docs/reference/_theorem_map.md`](../../docs/reference/_theorem_map.md#mathlib4-discharge-readiness)
is the audit-facing checklist for this sequence. It is generated from
the theorem registry and fails if a newly registered theorem lacks a
Mathlib-readiness decision.

Any additional theorem file added here must be a real `.lean` source file
with a local Lake configuration, a Mathlib-compatible toolchain, and a green
`lake build` before the manuscript may cite it as source for a boundary
witness. Draft pseudo-code is not kept in this directory because it is too
easy for readers to confuse it with validated Lean.
