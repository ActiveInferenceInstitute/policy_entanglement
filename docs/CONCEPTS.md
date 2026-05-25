# Concepts — three-minute conceptual on-ramp

*Read this before the manuscript abstract if you're new to the
framework.  This page bridges the conceptual gap between
[`FAQ.md`](FAQ.md) and the technical
[`../manuscript/0A_abstract.md`](../manuscript/0A_abstract.md).*

---

## The one-line claim

**A single scalar `λ` tunes how *entangled* a multi-stream active-inference
agent's policy posterior is — from strict per-stream independence at
`λ = 0` to fully correlated joint policies as `λ → ∞`.**

That's it. Everything else — the closed-form decomposition, the
information geometry, the Lean formalization, the empirical witnesses —
is bookkeeping that makes this finite-policy-posterior claim precise
and verifiable. It is not a replacement for the Free Energy Principle
or active inference as a process theory; it is a structured posterior
family inside that broader variational setting. The manuscript now
keeps that distinction explicit: FEP supplies the variational framing,
active inference supplies the expected-free-energy process theory, and
policy entanglement studies finite posterior factorization after those
modeling commitments have been made.

The same distinction controls the relationship to other AIF variants.
The manuscript uses three labels: **exact** when the variant is a
literal slice of the posterior family, **parametric** when the modeler
must add an explicit factor or structural choice, and **analogical**
when the relationship is only a shared coupling pattern.  Mean-field
discrete AIF is exact at `λ = 0`; factor-graph message passing can
implement the coupling parametrically, with exact factor semantics only
after the policy factor is inserted into a specified graph;
hierarchical, sophisticated, branching-time, RGM, and Markov-blanket
readings are kept analogical unless their additional process-theory
content is explicitly built.

## The toy that makes it concrete

Two binary streams.  Four joint policies: `(0,0)`, `(0,1)`, `(1,0)`,
`(1,1)`.  Coupling potential `J` rewards the *aligned* pairs `(0,0)`
and `(1,1)` — pretend they're "both go left" or "both stay still".
The agent's joint policy posterior is:

```
q_λ(π¹, π²)  ∝  q^1_MF(π¹) · q^2_MF(π²) · exp( λ · J(π¹, π²) )
```

| `λ` | Joint posterior `q_λ` | Total correlation `I(q_λ)` | What it looks like |
|---:|---|---:|---|
| `0`   | `[0.25, 0.25, 0.25, 0.25]` | `0.0000`     | **Mean-field** — the two streams sample independently. |
| `1`   | `[0.44, 0.06, 0.06, 0.44]` | `0.33`       | **Mixed** — joint structure exists but there's still flexibility. |
| `4`   | `[0.50, 0.00, 0.00, 0.50]` | `0.69 = log 2` | **Frozen** — the joint has collapsed onto two aligned archetypes. |

The first three theorem families live between these two poles:

1. **Decomposition** ([[THMREF:thm_4_1]]):
   the joint variational free energy decomposes into
   *per-stream marginal free energy* + *coupling cost* + *correlation
   surcharge* (multi-information `I(q)`).
2. **Geometry** (the geometry theorem family):
   the mean-field set is an *e-flat submanifold*, the m-projection
   minimizes KL, and the Pythagorean identity
   `KL(q ‖ ref) = I(q) + KL(m̂(q) ‖ ref)` separates the
   "non-mean-field cost" from the "still-mean-field cost".
3. **Spectral** (the spectral theorem family):
   joint policies factor as products of per-stream marginals iff the
   joint has Schmidt rank 1; tuning `λ` traces a rank curve through
   policy space.

## How to read the rest of the project

| If you are… | …read next |
|---|---|
| New and want the elevator pitch | [`../README.md`](../README.md) → §"What it looks like in 20 lines" |
| Curious about the headline theorem | [`../manuscript/2D_decomposition.md`](../manuscript/2D_decomposition.md) |
| A mathematician or AIF researcher | [`READING_ORDER.md`](READING_ORDER.md), persona 1 |
| A Lean / formalization reader | [`READING_ORDER.md`](READING_ORDER.md), persona 2 |
| A software engineer | [`READING_ORDER.md`](READING_ORDER.md), persona 3 |
| Confused about jargon | [`glossary.md`](glossary.md) |

## What this document is not

This page deliberately *omits* the framework's full apparatus — the
EFE term `γ G_λ`, the preference-side coupling `K_c`, the per-stream
priors `E_k`, the log-partitions `Z_E(λ)` and `Z(λ)`, the
heterogeneous quadratic tax `C λ²`, the witness-structure
formalization idiom, the hierarchical / sophisticated embeddings,
and the bipartite / multi-K extensions.  Every one of those lives in
the manuscript or the docs.  This page is the *zero-jargon entry
slope* that the audit recommended adding for newcomers; it stops
deliberately at the K=2 binary toy so that the conceptual move (the
λ-deformation between independence and alignment) is unmistakable.

## A two-line orientation to the Lean side

The project has **two Lean packages** with complementary roles:

1. **`lean/ActinfPolicyEntanglement/`** — the *Float boundary fragment*.
   Compiles on stock Lean 4.29.0 with **no Mathlib dependency**, zero
   `sorry`, zero non-foundational axioms.  Its job is to give every
   numbered theorem a *typed* declaration that the manuscript
   renderer embeds via `[[LEAN:...]]` tokens — so prose and Lean
   cannot drift silently.  The bodies use `Float`; analytic content
   that requires `Real`/`PMF`/measure theory lives next door.

2. **`lean/MathlibProofs/`** — the *ℝ analytic kernel*.  A separate
   Mathlib-backed package that machine-checks the **headline
   Theorem 5.1** (the full S01 boxed free-energy identity) in
   $\mathbb{R}$, axiom-clean under foundational-only `#print axioms`,
   enforced via `scripts/build_mathlib_proofs.py` + the automatic
   pytest gate `tests/test_mathlib_axiom_audit.py`.

The Float boundary is the numerical shadow of the ℝ kernel.  The
single open residual is a *verified* error-bounded
Float$\leftrightarrow\mathbb{R}$ bridge, scoped multi-week research in
[`reference/methods_and_assumptions.md`](reference/methods_and_assumptions.md).
For a step-by-step verification recipe see
[`reference/HOW_TO_VERIFY.md`](reference/HOW_TO_VERIFY.md).

## Structural fifth representation

Supplemental section §S8 ships **Generalized Notation Notation (GNN)**
[Smékal & Friedman 2023] as a fifth structural-and-numerical
representation of the framework.  The bridge includes a project-owned
GNN parser, a K=2 Bernoulli round-trip from `gnn/bernoulli_toy.gnn.md`,
a Lean typed-contract emitter, and a `simulate_gnn.py` pipeline stage.
It does **not** prove theorems or promote any registry row: the
four-track proof contract (prose / equations / Python / Lean) remains
the analytic contract.  See
[`../manuscript/S08_gnn_generalized_notation_extension.md`](../manuscript/S08_gnn_generalized_notation_extension.md).
Note also that §20.Q8 uses the same acronym "GNN" to refer to *graph
neural networks*; the two meanings are orthogonal and explicitly
disambiguated at §S8.3.
