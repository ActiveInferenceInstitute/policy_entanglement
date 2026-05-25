# STYLE.md — Lean 4 code style for the boundary fragment

Style conventions for the **Mathlib-free** Lean 4 layer under
`lean/ActinfPolicyEntanglement/` and `lean/FepSketches/`.  These rules
are derived from the 17 submodules that ship in Phase 0 and are
designed to keep the boundary fragment readable, witness-friendly, and
straightforward to extend in a separate MathlibProofs layer.

This file complements:

* [`AGENTS.md`](AGENTS.md) — agent-facing constitution and adding-a-submodule workflow
* [`README.md`](README.md) — human-facing overview and submodule index
* [`ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](ActinfPolicyEntanglement/MathlibRefinementRoadmap.md) — MathlibProofs discharge plan

---

## 1. File header

Every `.lean` file under `ActinfPolicyEntanglement/` opens with a
module-level docstring:

```lean
/- `ActinfPolicyEntanglement.<Module>` — one-line purpose.

   Longer description (2–6 lines): what the module owns, which
   manuscript section it mirrors, which Python module is the
   numerical companion, and whether any theorem is in
   witness-consuming form.

   Mathlib-free, sorry-free, axiom-free. -/
```

The closing sentence "Mathlib-free, sorry-free, axiom-free" is
load-bearing: a CI grep on this phrase is one of the human-readable
signals that the file is part of the boundary fragment (the actual
gates live in `scripts/build_lean.py`).

## 2. Namespace structure

Every module wraps its declarations in a `namespace
ActinfPolicyEntanglement` block (or, for `FepSketches/*.lean`, a
`namespace FepSketches`).  Submodules that introduce a new
mathematical object — `Bipartite`, `Markov`, … — open a nested
namespace inside the main one, never at top level:

```lean
namespace ActinfPolicyEntanglement
namespace Bipartite

structure BipartiteJoint (Pol1 Pol2 : Type) where
  …

end Bipartite
end ActinfPolicyEntanglement
```

A nested namespace must always be `end`-closed in the same file that
opens it.

## 3. Reserved tokens and identifiers

Lean 4 reserves `Π` (uppercase Greek pi, dependent-product binder)
and `λ` (lambda binder) at the lexer level.  Substitutes used
throughout the boundary fragment:

| Mathematical symbol | Lean identifier |
|---|---|
| Π (a policy) | `pi` or `π` *inside* a string / docstring only; `Pol` when used as a *type* parameter |
| λ (coupling strength) | `lam` |
| q^λ (λ-entangled posterior) | `q_lam` |
| Π_k (k-th factor) | `Pol k` where `Pol : PolicyFactor K` |

Token renames must be applied **consistently across every file** that
references the symbol; partial renames cause cascading parse errors
several modules downstream.

## 4. Naming conventions

### Theorems

* `<concept>_<property>` — `couplingTax_nonneg`,
  `entangledPrior_at_zero`, `mfImage_isMeanField`.
* `<concept>_iff_<other_concept>` — `meanField_iff_totalCorrelation_eq_zero`.
* `<concept>_<property>_witness` — for witness-form theorems
  (`couplingTax_quadratic_bound` is the canonical Round-1 exception
  for historical compatibility; new witness theorems use the suffix).
* `_at_zero` for λ = 0 specializations,
  `_small_lambda_<bound>` for asymptotic-λ statements.

### Structures (witness payloads)

* `<Concept>Witness` — `MarkovBlanketSeparationWitness`,
  `UpperSemicontinuousRankWitness`,
  `SophisticatedInferenceEmbedding`, `BoundedQuadraticTax`,
  `LocalConcavityAtZero`, `SparsityRankEnvelope`.
* The fields of a witness `structure` are the **analytic content** the
  caller must supply (a constant `C` with non-negativity proof, a
  Taylor coefficient with a sign hypothesis, a limit hypothesis
  `Tendsto`, …) — see Section 6 below.

### Definitions

* Lower-camelCase: `couplingLogWeight`, `entangledPosteriorLogWeight`,
  `totalCorrelation`, `freeEnergy`, `couplingTax`.
* Type aliases use `abbrev`: `abbrev PolicyFactor (K : Nat) := …`.
* Predicates use `def … : Prop`: `def IsPMF`, `def IsMeanField`,
  `def IsHeterogeneous`.

### Inductives

* `<Concept>` with constructors that are mutually disjoint and
  exhaustive: `InferenceMode { vfe | efe | sophisticated }`,
  `CouplingPhase { disordered | mixed | frozen }`,
  `CouplingVerdict { pays | neutral | does_not_pay }`.

  > **Status note (current source):** these three are documented as the
  > *intended* inductive shape but are **not yet shipped as Lean
  > `inductive`s** in the boundary fragment. The current source realizes
  > them as predicates / scalars: `InferenceMode` via the
  > `IsPlanningStream` / `IsReflexiveStream` `Prop`s (`Heterogeneous`),
  > `CouplingPhase` via `couplingPhaseAt : Float → Nat` (`0/1/2`,
  > `BernoulliToy`), and `CouplingVerdict` via `couplingVerdict : … →
  > Bool` (`Decomposition`). Treat this subsection as the target
  > convention for any future promotion to inductives, not a description
  > of the present tree.

## 5. Section bars

Inside a long module, group related declarations with `/-! ## … -/`
section bars (Lean 4 documentation comments).  Example from
`Decomposition.lean`:

```lean
/-! ## Auxiliary bundles -/

def sumMarginalFreeEnergies …
def couplingCostTerm …

/-! ## Theorem 5.1 -/

theorem entanglement_decomposition …
```

These render as section headings in the LeanInk-generated HTML view
and are the recommended way to chunk a module that ships >5
declarations.

## 6. Witness-form theorems

The witness pattern is **the** boundary-fragment idiom for any
theorem whose full analytic content requires Mathlib.  Pattern:

```lean
/-- Witness payload for theorem X: the analytic content that, if
    supplied, lets the boundary fragment certify X without `sorry`.
    Each field is the part of the proof that requires Mathlib (a
    real-analytic bound, a measure-theoretic limit, a matrix-rank
    semicontinuity hypothesis, …). -/
structure XWitness where
  coefficient : Float
  coefficient_nonneg : 0.0 ≤ coefficient
  identity : ∀ arg, …

/-- Witness-form theorem X.  The boundary fragment certifies the
    algebraic skeleton; the analytic payload (`XWitness`) is supplied
    by the caller (Phase 0) or by a Mathlib-backed instance
    constructor (MathlibProofs layer). -/
theorem X_witness (w : XWitness) : …
```

Key invariants:

1. **No `sorry` inside the theorem.**  The proof reduces to algebraic
   manipulation of the witness fields plus core-Lean lemmas (`Nat.le`,
   `Float.add_comm`, `CommScalar.affine_diff`, …).
2. **No hidden assumptions.**  Anything the proof needs from analysis
   appears as a field of the witness `structure`.  Reviewers should
   be able to read the witness and recover the Mathlib API that would
   discharge it.
3. **Polymorphic scalar.**  Where possible, the theorem is
   polymorphic over `[CommScalar α]` so the witness can be
   re-discharged against `ℝ` in the MathlibProofs layer without re-stating the
   theorem.
4. **Mirror to the manuscript.**  Each witness-form theorem has a row
   in `manuscript/refs/labels.yaml` with `status: witness` and a
   `lean_module` / `lean_name` pair pointing to the live declaration.
   See the round-3 graduations (`SpectralWitnesses`,
   `ConnectionsWitnesses`) for canonical examples.

## 7. Polymorphism over `CommScalar`

The in-house `CommScalar α` typeclass (defined in `Scalar.lean`) is
preferred over hard-coded `Float` for any theorem whose statement
makes sense over a generic commutative ring.  Concrete `Float`
specializations belong only at **module boundaries** (where the
result is fed into a Python mirror or the numerical pipeline).

When in doubt: write the algebraic lemma on `[CommScalar α]`, and
add a separate Float specialization only if a downstream consumer
needs it.

## 8. Cycle hygiene

The Lake build will silently mis-resolve if a cycle is introduced.
Two rules are non-negotiable:

1. `ActinfPolicyEntanglement.lean` (root) **does not import**
   `FepSketches.*`.  Only the inverse direction is allowed
   (`FepSketches/PolicyEntanglementBoundary.lean` imports
   `ActinfPolicyEntanglement.*`).
2. Submodules under `ActinfPolicyEntanglement/` may import one
   another, but the dependency graph must remain a DAG.  Current
   layering (top imports bottom):
   ```
   ConnectionsWitnesses, SpectralWitnesses
       ↓
   Convexity, MarkovBlanket
       ↓
   Decomposition, BernoulliToy, Heterogeneous, Constructive, Geometry, Spectral
       ↓
   FreeEnergy, Coupling, JointDist, Monotonicity
       ↓
   Basic, Scalar
   ```

Adding a new edge that violates this layering will trigger a cycle
error from Lake.

## 9. Comments and docstrings

* Theorems and definitions get a single-line docstring at minimum;
  longer prose belongs in the module-level docstring or in the
  manuscript.
* Cross-references to the manuscript use the form
  `(Theorem 9.1; manuscript §9)` or `(Prop 7.5)`.
* Internal helper lemmas (declared `private` or with a `_` prefix
  in their name) may omit docstrings if their meaning is obvious from
  the statement.

## 10. Things to avoid

* `import Mathlib.…` — banned.  The hygiene gate in
  `scripts/build_lean.py` enforces this.
* `sorry` — banned outside docstrings.  The gate filters string
  mentions but counts every strict occurrence.
* `axiom` — banned beyond the stock kernel.
* `unsafe`, `partial`, `noncomputable` — banned.  If a definition
  appears to need them, factor the computable / total part out and
  push the analytic bit into a witness `structure`.
* `deriving Inhabited` on a structure whose fields lack `Inhabited`
  instances — Lean 4 will fail to synthesise.  Either provide the
  field-level instances or drop the `deriving` clause.
* `Π` or `λ` as identifiers — reserved binder tokens (see Section 3).

## 11. Mathlib refinement

When a MathlibProofs contributor discharges a witness theorem against
Mathlib, they do **not** edit the boundary fragment.  Instead they:

1. Add a sibling Lake library under `lean/MathlibProofs/` (or extend
   it if it already exists).
2. Import the relevant Mathlib facility and the boundary witness
   `structure` (`MathlibProofs.<Module>` imports
   `ActinfPolicyEntanglement.<Module>`).
3. Construct a canonical instance of the witness `structure` from
   Mathlib content, then re-export the boundary theorem specialized
   against `ℝ` with the payload supplied internally.
4. Update `manuscript/refs/labels.yaml` — flip `status: witness` to
   `status: proved` (or keep `witness` if only the payload is
   discharged but downstream still needs work).

Full layered plan in
[`ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).

---

**Current review anchor**: live Lean counts are generated by
`scripts/build_lean.py` and recorded in the release-readiness report;
keep this style guide semantic rather than date-stamped.
