# Mathlib4 Analytic-Discharge Roadmap

> **STATUS UPDATE (2026-05-19) — read first; the per-row table below is
> partly historical.** The central analytic content is **no longer
> future work**: `MathlibProofs.free_energy_decomposition_full` machine-
> checks, in ℝ, the *full* manuscript S01 free-energy identity for
> `thm_4_1` (composing the axiom-clean general-`K` kernel
> `entanglement_decomposition_generalK`), `#print axioms` foundational-
> only, enforced by `scripts/build_mathlib_proofs.py`. Rows below whose
> discharge is described as "once `Float` is replaced by `ℝ`" for the
> KL-chain-rule / finite-sum algebra are therefore **done in the
> separate `MathlibProofs` ℝ package** and the prose here is retained
> only as the pre-discharge record.
>
> **The single genuine remaining item is the verified
> Float↔ℝ bridge** — precisely scoped (the exact obstruction: Lean
> `Float` is opaque `@[extern]`, Mathlib has no rounding model; the two
> sound routes — a Flocq-style formal IEEE-754 model, or a verified
> interval re-implementation) in the **normative ledger**
> [`docs/reference/methods_and_assumptions.md`](../../docs/reference/methods_and_assumptions.md)
> (§ "The honest residual — Float↔ℝ"). That bridge is genuine
> multi-week research and is **deliberately not fabricated** in any
> session: a green build that assumes the error bound, or a vacuous
> rounding model disconnected from Lean's actual `Float`, is the exact
> `sorryAx`-laundering this project's integrity machinery exists to
> reject (and has rejected — see `docs/CHANGELOG.md`). Undertake it as
> its own deliberate project, verified by the `#print axioms` audit + a
> self-designed negative control, never as a loop patch.

**Status:** the Mathlib-free boundary fragment is complete. All 21
numbered theorems carry a live Lean companion. This roadmap scopes the
separate Mathlib4 work that would *discharge* the analytic-content
hypotheses currently passed as `structure` parameters.

**Project**: `actinf_policy_entanglement_lean`
**Document status**: current scope note plus additive proof-engineering roadmap; current source code lives in the boundary fragment.
**Audience**: contributors tasked with replacing witness/boundary analytic payloads with constructive Mathlib4-backed proofs.

---

## What this document is *not*

This roadmap does **not** describe a current gap in the live tree. The
boundary fragment under [`./`](.) is:

* **Mathlib-free** — compiles on stock Lean 4 v4.29.0 with zero Mathlib imports,
* **0 strict `sorry`** — every `.lean` file in the boundary fragment is free of blocking `sorry`s (the only mentions of the word live in docstrings advertising this fact),
* **0 `axiom`** beyond the stock Lean kernel,
* **0 `unsafe` / `partial` / `noncomputable`** declarations,
* **17 boundary submodules** plus the package root and the `FepSketches` re-export,
* **22 / 22** lake jobs green via `cd lean && lake build`.

Every numbered manuscript theorem (21 total) now has a live Lean companion:
**11 witness-form**, **5 proved**, **1 forwarder**, **3 boundary**. There
are no current `sketch` or `deferred` theorem rows. The authoritative live snapshot is in
[`../../docs/reference/lean_reference.md`](../../docs/reference/lean_reference.md)
and the per-theorem wiring is in
[`../../docs/reference/_theorem_map.md`](../../docs/reference/_theorem_map.md).

The remaining refinement work is *analytic-content discharge*: each
witness/boundary theorem currently accepts or exposes an analytic payload as a
`structure` parameter (KL chain rule, Bregman Taylor, real-analytic
continuity, matrix rank semicontinuity, tensor-train rank composition,
measure tightness, recursive Bellman update). This roadmap describes
how each of those payloads would be constructed from Mathlib.

---

## Hygiene budget (boundary, current)

```text
Build:                    22/22 lake jobs green
Strict sorries:           0     (verified by scripts/build_lean.py)
Axioms:                   0
unsafe/partial/noncomp:   0
Modules:                  17 .lean files under lean/ActinfPolicyEntanglement/
                          + 1 FepSketches re-export
```

Refresh the live count with:

```bash
uv run python scripts/build_lean.py
```

The `build_lean.py` script counts only **strict** `sorry` / `axiom` /
`unsafe` declarations (filtering out comments and string mentions); it is
the authoritative gate.

---

## Theorem-status budget

From [`../../manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml):

| Status | Count | Meaning |
|---|---:|---|
| `proved` | 5 | Boundary proof exists for the registered boundary statement; row-level `faithfulness:` distinguishes substantive rows from statement-restricted rows. |
| `boundary` | 3 | Typed boundary rows: either definitional boundary facts or witness-threaded contracts. |
| `witness` | 11 | Same shape; explicitly named as a witness theorem. |
| `forwarder` | 1 | Re-exports a theorem from another module. |
| `sketch` | 0 | All sketches graduated. |
| `deferred` | 0 | All deferred rows graduated to `witness`. |
| **Total** | **21** | |

---

## Analytic-discharge targets and requirements

Each row below names a live theorem whose real-valued Mathlib4
discharge would prove analytic content beyond the current
Mathlib-free boundary. Some rows are current `witness` rows, some are
`boundary` rows, and one is a proved boundary theorem whose stronger
matrix-rank refinement belongs in the Mathlib layer. None of these rows
implies a `sorry` in the boundary fragment today; they are all *over
and above* what the live code already certifies.

| Live theorem | Module . name | Witness contract | Mathlib discharge plan |
|---|---|---|---|
| `thm_4_1` (Entanglement decomposition) | `Decomposition.entanglement_decomposition` | `EntanglementDecomposition` (four-term algebraic split) | Gibbs algebra; would discharge via finite-sum manipulation (`Finset.sum_comm` + `MeasureTheory.integral_add`) in Mathlib once `Float` is replaced by `ℝ`. |
| `prop_6_5` (Pythagorean) | `Geometry.dualFlat_pythagorean_witness` | `(klVal, tcVal, residual)` triple + identity | KL chain rule (Mathlib has partial coverage in `Mathlib.InformationTheory.KullbackLeibler.Basic`; the chain-rule lemma is not yet a single named result). |
| `thm_8_1` (Heterogeneous coupling tax) | `Heterogeneous.couplingTax_quadratic_bound` | `BoundedQuadraticTax {C, C_nonneg, bound}` | Bregman Taylor expansion — **not yet in Mathlib**; would build atop `Mathlib.Analysis.Convex.SpecificFunctions.Deriv` and `Mathlib.Analysis.Calculus.Taylor`. |
| `cor_8_2` (Small-λ tolerance) | `Heterogeneous.couplingTax_small_lambda_tolerance` | `SmallLambdaTolerance {lamMax, lamMax_pos, bound}` | Same Bregman-Taylor toolkit as `thm_8_1`; once `thm_8_1` is discharged, this follows from real-analytic continuity at λ = 0 (`Mathlib.Analysis.Calculus.ContDiff`). |
| `prop_7_1` (Bipartite mean-field, converse) | `Spectral.Bipartite.schmidtRankOne_iff_isBipartiteMeanField` | Matrix-outer-product structure | `Matrix.rank_one_outer_product` (or equivalent) — available in Mathlib once `Float` is replaced by `ℝ` and `Coupling` is moved to `Matrix`-valued joints. |
| `prop_7_2` (Schmidt rank USC) | `SpectralWitnesses.schmidtRank_upperSemicontinuous_witness` | `UpperSemicontinuousRankWitness` (USC of rank under matrix convergence) | `Mathlib.Topology.Semicontinuous` + `Matrix.rank_lowerSemicontinuous` (partial — Mathlib has lower-semicontinuity of rank; upper-semicontinuity of `Schmidt`-rank requires the contrapositive specialization). |
| `thm_7_3` (Sparsity-rank tradeoff) | `SpectralWitnesses.sparsityRank_tradeoff_witness` | `SparsityRankEnvelope` (support graph + TT-rank envelope) | Tensor-train rank composition — **not in Mathlib**; needs new development atop `Mathlib.LinearAlgebra.TensorProduct` and `Mathlib.LinearAlgebra.Matrix.Spectrum`. |
| `thm_4_3` (Convexity of F in λ) | `Convexity.freeEnergy_convex_in_lam_witness` | `FreeEnergyConvexityWitness` (curve + convexity hypothesis) | Convexity from second-derivative non-negativity — available via `Mathlib.Analysis.Convex.SpecificFunctions.Deriv.convexOn_of_deriv2_nonneg`. |
| `prop_10_1` (Local concavity at λ=0) | `Convexity.freeEnergy_localConcavity_at_zero_witness` | `LocalConcavityAtZero` (Taylor coefficients with `a₂ ≤ 0`) | Taylor expansion — available via `Mathlib.Analysis.Calculus.Taylor` / `Mathlib.Analysis.Calculus.ContDiff`. |
| `prop_11_3` (Markov-blanket separation as 1 − I/H) | `MarkovBlanket.markovBlanket_separation_identity_witness` | `MarkovBlanketSeparationWitness` (entropy / total-correlation tie-ins plus `sep = 1 − I/H`) | Direct identity plus KL non-negativity for `Iq ≥ 0`; the algebraic part discharges immediately once `Float` is replaced by `ℝ`. |
| `thm_11_1` (Hierarchical concentration) | `ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness` | `HierarchicalConcentrationWitness` (limit witness `Tendsto`) | Measure-theoretic tightness / Cauchy concentration — available via `Mathlib.MeasureTheory.Measure.Tight` and `Mathlib.Topology.MetricSpace.Basic`. |
| `prop_11_2` (Sophisticated inference embedding) | `ConnectionsWitnesses.sophisticatedInference_embedding_witness` | `SophisticatedInferenceEmbedding` (embedding type + VFE-preservation identity) | Categorical / type-theoretic embedding + recursive Bellman update — needs new categorical infrastructure (no direct Mathlib counterpart); composes once `entangledPrior` is `ℝ`-valued. |

Additional already-complete boundary/proved theorems (`cor_4_4`, `thm_4_2`, `prop_6_1`)
are already discharged on the boundary by definitional unfolding plus
`rfl`; their `boundary` / `proved` status reflects the absence of a
Mathlib-strength analytic upgrade requirement.

---

## Mathlib-import dependency order

The analytic payload targets above are not independent. A single
refinement library would discharge them in the following dependency
order; each layer assumes its predecessors have been imported and
specialized against `ℝ`.

```
Layer 0 — scalar substitution
  Replace `Float` with `ℝ` (Mathlib.Data.Real.Basic) throughout
  JointDist, Coupling, FreeEnergy, Heterogeneous, Decomposition,
  Geometry, Bipartite, Spectral, Convexity, MarkovBlanket,
  SpectralWitnesses, ConnectionsWitnesses. Replace
  `List (PolicySpace K Pol)` with `Finset (PolicySpace K Pol)`.

Layer 1 — pure-arithmetic identities
  • prop_11_3  Markov-blanket separation  (Real arithmetic only)

Layer 2 — KL bookkeeping
  • Mathlib.InformationTheory.KullbackLeibler.Basic
  • Mathlib.Probability.Entropy.Basic
  ⇓ discharges
  • thm_4_1   entanglement decomposition  (finite-sum + KL non-neg)
  • prop_6_5  dual-flat pythagorean       (KL chain rule)

Layer 3 — convexity from second derivative
  • Mathlib.Analysis.Convex.SpecificFunctions.Deriv
  • Mathlib.Analysis.Calculus.ContDiff
  ⇓ discharges
  • thm_4_3   free-energy convexity in λ
  • prop_10_1 local concavity at λ = 0

Layer 4 — Bregman Taylor expansion (new development atop Layer 3)
  • Mathlib.Analysis.Calculus.Taylor
  ⇓ discharges
  • thm_8_1   heterogeneous coupling tax  (Bregman quadratic bound)
  • cor_8_2   small-λ tolerance           (real-analytic continuity at 0)

Layer 5 — matrix rank semicontinuity
  • Mathlib.LinearAlgebra.Matrix.Rank
  • Mathlib.Topology.Semicontinuous
  ⇓ discharges
  • prop_7_1  bipartite mean-field        (matrix-outer-product structure)
  • prop_7_2  Schmidt rank USC            (semicontinuity of rank)

Layer 6 — tensor-train rank composition (new development atop Layer 5)
  • Mathlib.LinearAlgebra.TensorProduct
  • Mathlib.LinearAlgebra.Matrix.Spectrum
  ⇓ discharges
  • thm_7_3   sparsity-rank tradeoff

Layer 7 — measure-theoretic limits
  • Mathlib.MeasureTheory.Measure.Tight
  • Mathlib.Topology.MetricSpace.Basic
  • Mathlib.Order.Filter.Basic
  ⇓ discharges
  • thm_11_1  hierarchical AIF as λ → ∞

Layer 8 — categorical / recursive-update infrastructure
  • Mathlib.CategoryTheory.* (or hand-rolled categorical scaffolding)
  • Recursive Bellman + KL-control identities (new development)
  ⇓ discharges
  • prop_11_2 sophisticated-inference embedding
```

Layers 0–3 are nearly mechanical once the scalar substitution is in
place. Layers 4 and 6 require new Mathlib development (Bregman Taylor
and tensor-train rank composition are not yet first-class Mathlib4
citizens). Layer 8 is the most open-ended and would likely live in a
project-local module that uses Mathlib only for its `Real`/`EReal`
arithmetic.

---

## Refinement workflow

Each Mathlib-refinement task follows the same shape:

1. **Add a sibling library** under `lean/MathlibProofs/` (or extend the
   existing witness module by importing Mathlib). The boundary
   fragment itself stays untouched.
2. **Provide the canonical witness instance** — construct a term of
   the relevant witness `structure` from the Mathlib facility named in
   the table above.
3. **Re-export the witness-form theorem against `ℝ`** by specializing
   the polymorphic statement with the new instance.
4. **Update `labels.yaml`** — flip the theorem's `status` from
   `witness` to `proved` (or, if only the payload is discharged but a
   downstream identity still needs work, keep `witness` and add a
   reference to the Mathlib-backed instance).
5. **Re-run the renderer** — `[[LEAN:label]]` tokens automatically pick
   up the new module / name pair.

---

## Acceptance gates for the Mathlib refinement

A Mathlib-refinement milestone is considered discharged when:

1. The relevant witness `structure` has a canonical Mathlib-backed
   instance constructor in `lean/MathlibProofs/`.
2. The witness-form theorem is re-exported against `ℝ` with the
   payload supplied internally rather than as a caller hypothesis.
3. `labels.yaml` is updated with the new `lean_module` / `lean_name` /
   `status` triple.
4. The renderer's `[[LEAN:<label>]]` token resolves to the new
   declaration (next manuscript build embeds the live source).
5. `scripts/build_lean.py` still reports **0 strict `sorry`, 0
   axioms, 0 `unsafe`/`partial`/`noncomputable`** for the boundary
   fragment. Any Mathlib-backed theorem cited by the manuscript must
   also be `sorry`-free in its own local build.
6. `tests/test_theorem_map_generated.py` passes with the regenerated
   `docs/reference/_theorem_map.md`.

---

## Constructive Boundary Pieces Already in Place

Two constructive sub-fragments ship with the boundary skeleton:

* **`Monotonicity.lean`** — 16 theorems / lemmas, structural lemmas on
  `Nat`, `Or`, `And`, `List`, and `Fin`. Constructive forwarders to
  core Lean's arithmetic / list primitives. Sorry-free.
* **`Constructive.lean`** — boundary lemmas about `couplingLogWeight`,
  `entangledPosteriorLogWeight`, and trivial coupling. Sorry-free; uses
  witness-form for any analytic content.

These remain in place as a sanity rail once Mathlib refinement begins,
demonstrating that the boundary skeleton supports non-vacuous
structural reasoning even without Mathlib.

## Decidability instances

`Basic.lean` ships with two decidability instances that let downstream
code do case analysis on stream mode without classical logic:

* `instDecidableIsPlanningStream` — forwarder to `Nat.decLt`
* `instDecidableIsReflexiveStream` — forwarder to `Nat.decEq`

---

## Effort estimate

See §12 of the manuscript
([`../../manuscript/3B_lean_formalization.md`](../../manuscript/3B_lean_formalization.md))
for the current scope and priority order (~6 months total for an experienced Lean
contributor; KL bookkeeping discharge of `thm_4_1` is the
*first-publishable-result* milestone at ~8–10 weeks).

---

## Current Boundary State

The live boundary fragment under [`./`](.) ships **17 submodules** with
**0 strict `sorry`, 0 axioms, 0 `unsafe`/`partial`/`noncomputable`, and
no Mathlib import** on stock Lean 4 v4.29.0, certifying a live Lean
companion for **every** numbered manuscript theorem (11 witness, 5
proved, 1 forwarder, 3 boundary). The Mathlib4 discharge work
described above is the additive plan to discharge the analytic content
of the witness/boundary theorem rows on top of that boundary without
touching any existing file.

---

**Last reviewed**: 2026-05-12
**See also**:
[`../../docs/reference/lean_reference.md`](../../docs/reference/lean_reference.md) (per-theorem status),
[`../../docs/reference/_theorem_map.md`](../../docs/reference/_theorem_map.md) (four-track wiring),
[`../../docs/reference/veridical_status.md`](../../docs/reference/veridical_status.md) (live state).
