# Lean 4 Boundary Fragment: Live `ActinfPolicyEntanglement` Source Excerpts and Validation Wiring

The Lean 4 boundary fragment — the type-checked statements of every
formal claim in this manuscript — lives under
[`lean/`](../lean/) of the companion repository.  This appendix
indexes the modules; the full source is in the companion repository.

## Package structure

```
lean/
├── lakefile.lean                ← Lake package definition
├── lean-toolchain               ← [[VAR:lean_toolchain_version]]
├── ActinfPolicyEntanglement.lean
├── ActinfPolicyEntanglement/    ← boundary-fragment submodules
│   ├── Basic.lean
│   ├── JointDist.lean
│   ├── Coupling.lean
│   ├── FreeEnergy.lean
│   ├── Geometry.lean
│   ├── Spectral.lean
│   ├── SpectralWitnesses.lean        ← prop_7_2, thm_7_3
│   ├── Heterogeneous.lean
│   ├── BernoulliToy.lean
│   ├── Decomposition.lean
│   ├── Constructive.lean
│   ├── Monotonicity.lean
│   ├── Convexity.lean                ← thm_4_3, prop_10_1
│   ├── MarkovBlanket.lean            ← prop_11_3
│   ├── ConnectionsWitnesses.lean     ← thm_11_1, prop_11_2
│   └── Scalar.lean
├── FepSketches.lean
└── FepSketches/
    └── PolicyEntanglementBoundary.lean   ← re-exports
```

## Mathlib-free boundary

The package compiles against a stock Lean 4 [[VAR:lean_toolchain_version]] with **no Mathlib
dependency** at the boundary layer.  This was a deliberate design
choice: the boundary fragment encodes the *type signatures* of every
analytic claim so that downstream agents can `lake build` immediately
and discharge witness payloads in a separate Mathlib4 layer without
changing the boundary theorem names.

## Status snapshot

Live `grep` count, source-of-truth verified on each render
(strict-form `sorry` count = blocking sorries in proof bodies; the
"sorry" mentions inside `/-! … -/` docstrings advertising
`sorry`-free status are not blocking and are not counted):

| Lean module | Defs | Theorems / Lemmas | Structures | Strict `sorry` | Manuscript section |
|---|---:|---:|---:|---:|---|
| `Basic`        |  3 |  1 | 0 | 0 | [[SECREF:setup]] |
| `JointDist`    |  5 |  0 | 0 | 0 | [[SECREF:setup]], [[SECREF:geometry]] |
| `Coupling`     |  3 |  2 | 0 | 0 | [[SECREF:lambda_deformation]] |
| `FreeEnergy`   |  8 |  1 | 0 | 0 | [[SECREF:decomposition]] |
| `Geometry`     |  0 |  4 | 0 | 0 | [[SECREF:geometry]] |
| `Spectral`     |  1 |  2 | 0 | 0 | [[SECREF:spectral]] |
| `SpectralWitnesses` | 0 | 3 | 2 | 0 | [[SECREF:spectral]] |
| `Heterogeneous`|  1 |  2 | 2 | 0 | [[SECREF:heterogeneous]] |
| `BernoulliToy` | 14 |  2 | 0 | 0 | [[SECREF:examples]], [[SECREF:app.bernoulli]] |
| `Decomposition`|  2 |  5 | 0 | 0 | [[SECREF:decomposition]], [[SECREF:app.proof_decomp]] |
| `Constructive` |  0 |  4 | 0 | 0 | [[SECREF:decomposition]], [[SECREF:geometry]] |
| `Monotonicity` |  0 | 16 | 0 | 0 | [[SECREF:decomposition]], [[SECREF:phase]] |
| `Convexity`    |  0 |  2 | 2 | 0 | [[SECREF:decomposition]], [[SECREF:comparative]] |
| `MarkovBlanket`|  0 |  2 | 1 | 0 | [[SECREF:connections_multi_agent_geometry]] |
| Connections / Witnesses | 0 | 4 | 2 | 0 | [[SECREF:connections]] |
| `Scalar`       |  0 |  6 | 0 | 0 | [[SECREF:lambda_deformation]] |

Totals: **[[VAR:lean_submodule_count]] boundary submodules**, **[[VAR:lean_def_count]] defs**, **[[VAR:lean_theorem_count]] theorems / lemmas**,
**[[VAR:lean_structure_count]] structures**, **0 strict `sorry`**, **0 axioms**
beyond stock Lean 4.

The current registry's `status` distribution is:
**0 `deferred`, 0 `sketch`, 0 strict `sorry`** — every numbered
theorem in the manuscript resolves through `[[LEAN:<label>]]` to a
live Lean source block in `lean/ActinfPolicyEntanglement/`.  The
witness-form theorems are tracked in
[`docs/reference/lean_reference.md`](../docs/reference/lean_reference.md)
and [`lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
as Mathlib4 analytic-discharge targets (i.e. work to derive the witness
payloads in a separate library, not new statements to ship).

## Building locally

```bash
cd lean
lake build
```

Expected: `Build completed successfully ([[VAR:lean_lake_jobs_total]] jobs).`  The [[VAR:lean_lake_jobs_total]] jobs are
the [[VAR:lean_submodule_count]] `ActinfPolicyEntanglement.*` submodules, the
`ActinfPolicyEntanglement` root, the
`FepSketches.PolicyEntanglementBoundary` re-export, the `FepSketches`
root, and two Lake-internal targets.

## FepSketches Re-exports for the Sibling fep_lean Layout

`lean/FepSketches/PolicyEntanglementBoundary.lean` re-exposes the
load-bearing structural facts under the `FepSketches.*` namespace,
matching the import layout used alongside the
[fep_lean](https://github.com/ActiveInferenceInstitute/fep_lean) catalog
[@friedman-2026-fep-lean] and the [research manuscript template monorepo](https://github.com/docxology/template)
(GitHub organization **docxology**).

## Where each manuscript theorem lives in Lean

The `lean_module` / `lean_name` columns of
[`manuscript/refs/labels.yaml`](refs/labels.yaml) are the wiring; the
renderer's `[[LEAN:<theorem-label>]]` token extracts the live source.
The 20 theorem rows with manuscript `[[THMREF:...]]` tokens resolve at
render time; the separate Float↔ℝ roadmap row resolves through the
registry but is not inlined in this Lean-code supplement:

* [[THMREF:thm_4_1]]   → `Decomposition.entanglement_decomposition`
* [[THMREF:thm_4_2]]   → `Decomposition.freeEnergy_closedForm_witness`
* [[THMREF:thm_4_3]]   → `Convexity.freeEnergy_convex_in_lam_witness`
* [[THMREF:cor_4_2]]   → `Decomposition.couplingVerdict_correct`
* [[THMREF:cor_4_3]]   → `Decomposition.couplingLogWeight_pointwise_at_zero`
* [[THMREF:cor_4_4]]   → `Decomposition.totalCorrelation_def_unfold`
* [[THMREF:prop_6_1]]  → `Geometry.mfImage_isMeanField`
* [[THMREF:prop_6_2]]  → `Geometry.mProjection_kl_eq_self_when_meanfield`
* [[THMREF:prop_6_3]]  → `FreeEnergy.totalCorrelation_eq_kl_to_mprojection`
* [[THMREF:thm_6_4]]   → `Geometry.entangledFamily_eGeodesic`
* [[THMREF:prop_6_5]]  → `Geometry.dualFlat_pythagorean_witness`
* [[THMREF:prop_7_1]]  → `Spectral.Bipartite.isBipartiteMeanField_factors`
* [[THMREF:prop_7_2]]  → `SpectralWitnesses.schmidtRank_upperSemicontinuous_witness`
* [[THMREF:thm_7_3]]   → `SpectralWitnesses.sparsityRank_tradeoff_witness`
* [[THMREF:thm_8_1]]   → `Heterogeneous.couplingTax_quadratic_bound`
* [[THMREF:cor_8_2]]   → `Heterogeneous.couplingTax_small_lambda_tolerance`
* [[THMREF:prop_10_1]] → `Convexity.freeEnergy_localConcavity_at_zero_witness`
* [[THMREF:thm_11_1]]  → `ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness`
* [[THMREF:prop_11_2]] → `ConnectionsWitnesses.sophisticatedInference_embedding_witness`
* [[THMREF:prop_11_3]] → `MarkovBlanket.markovBlanket_separation_identity_witness`

## The twenty live Lean companions

The blocks below are produced by `[[LEAN:<label>]]` tokens that
`src/manuscript/lean_extract.py` resolves against the live `.lean`
sources in `lean/ActinfPolicyEntanglement/`. Each block carries a
`-- From <file>:<line> [status: ...]` caption pointing at the exact
source coordinates so the supplement is a verbatim window onto the
formalization, not a hand-curated copy. If a registered theorem is
ever renamed in Lean, the next render either updates the inlined
source or fails fast with a `[[MISSING:LEAN:...]]` marker — there is
no way for the supplement to drift silently from the boundary
fragment.

### Decomposition fragment

#### Entanglement decomposition

[[LEAN:thm_4_1]]

#### Existence of optimal coupling

[[LEAN:thm_4_2]]

#### Coupling-pays-for-itself verdict

[[LEAN:cor_4_2]]

#### Mean-field at $\lambda = 0$

[[LEAN:cor_4_3]]

#### Total correlation unfolds to KL-self

[[LEAN:cor_4_4]]

### Geometry fragment

#### Mean-field submanifold is e-flat

[[LEAN:prop_6_1]]

#### m-projection minimizes KL

[[LEAN:prop_6_2]]

#### Total correlation equals KL to m-projection

[[LEAN:prop_6_3]]

#### e-geodesic family

[[LEAN:thm_6_4]]

#### Pythagorean witness on the dual-flat pair

[[LEAN:prop_6_5]]

### Spectral fragment

#### Bipartite mean-field ⇔ Schmidt rank 1

[[LEAN:prop_7_1]]

#### Schmidt rank upper-semicontinuous in $\lambda$

[[LEAN:prop_7_2]]

#### Sparsity-rank tradeoff for tensor-train coupling

[[LEAN:thm_7_3]]

### Convexity fragment

#### Convexity of $F$ in $\lambda$

[[LEAN:thm_4_3]]

#### Local concavity of $F$ at $\lambda = 0$

[[LEAN:prop_10_1]]

### Heterogeneous fragment

#### Coupling-tax quadratic bound

[[LEAN:thm_8_1]]

#### Small-$\lambda$ tolerance witness

[[LEAN:cor_8_2]]

### Connections fragment

#### Hierarchical AIF as the $\lambda \to \infty$ limit

[[LEAN:thm_11_1]]

#### Sophisticated-inference embedding

[[LEAN:prop_11_2]]

### Markov-blanket fragment

#### Markov-blanket separation identity $1 - I/H$

[[LEAN:prop_11_3]]

## How drift is prevented

The `[[LEAN:...]]` injection turns each Lean theorem in this appendix
into a *single source of truth* shared with the boundary fragment
itself:

1. `manuscript/refs/labels.yaml` declares the theorem registry with
   `lean_module` / `lean_name` for each entry.
2. At render time, `src/manuscript/lean_extract.py::load_lean_snippets`
   parses every `.lean` file under `lean/ActinfPolicyEntanglement/`
   and indexes each declaration by `(module, qualified_name)`.
3. `src/manuscript/renderer.py::_lean` resolves the registry pair
   against this index and emits a fenced Lean block carrying the
   source coordinates and the registry-declared status.
4. If the qualified name is missing or has been renamed, the renderer
   substitutes a `[[MISSING:LEAN:...]]` marker that `scripts/validate_manuscript.py`
   refuses to ship — so a Lean rename either flows through to the
   manuscript or fails CI.

This eliminates every form of stale-quote risk: the supplement above
*is* the boundary fragment, sliced theorem-by-theorem.

## How a witness is consumed today

The stock-Lean boundary is now zero-sorry **and zero-`deferred`**.  For a
`status: witness` theorem, the current source consumes a typed `structure`
whose fields bind the analytic payload to boundary-fragment primitives.  The
validated contract is:

1. The theorem row in `manuscript/refs/labels.yaml` names the live Lean
   declaration.
2. The Lean declaration type-checks without Mathlib and without hidden
   axioms.
3. The corresponding Python witness or pymdp run computes the same payload
   numerically.
4. The relevant test file and dashboard invariant fail if the numerical
   payload drifts.
5. The manuscript renderer embeds only the live Lean declaration, never a
   hand-written replacement.

Mathlib4 enters only at the analytic-discharge boundary described in
[[SECREF:lean_plan]]: a separate Mathlib-backed library may later construct
these witness structures from `Real`, `PMF`, KL, convexity, rank, and
measure-theoretic lemmas.  Until such a module builds, it is not cited as a
current result and is not rendered as source code.

---
