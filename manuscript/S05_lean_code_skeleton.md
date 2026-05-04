# Lean Code Skeleton

The Lean 4 boundary fragment — the type-checked statements of every
formal claim in this manuscript — lives under
[`lean/`](../lean/) of the companion repository.  This appendix
indexes the modules; the full source is in the companion repository.

## Package structure

```
lean/
├── lakefile.lean                ← Lake package definition
├── lean-toolchain               ← v4.29.0
├── ActinfPolicyEntanglement.lean
├── ActinfPolicyEntanglement/    ← boundary-fragment submodules
│   ├── Basic.lean
│   ├── JointDist.lean
│   ├── Coupling.lean
│   ├── FreeEnergy.lean
│   ├── Geometry.lean
│   ├── Spectral.lean
│   ├── Heterogeneous.lean
│   ├── BernoulliToy.lean
│   └── Decomposition.lean
├── FepSketches.lean
└── FepSketches/
    └── PolicyEntanglementBoundary.lean   ← re-exports
```

## Mathlib-free boundary

The package compiles against a stock Lean 4 v4.29.0 with **no Mathlib
dependency** at the boundary layer.  This was a deliberate design
choice: the boundary fragment encodes the *type signatures* of every
analytic claim so that downstream agents can `lake build` immediately
and refine proofs incrementally as Mathlib's KL / entropy / SVD
machinery becomes available.

## Status snapshot

| Lean module | Theorems / Defs | `sorry` count | Manuscript section |
|---|---:|---:|---|
| `Basic` | 4 inductives + 2 preds + 1 thm | 0 | [[SECREF:setup]] |
| `JointDist` | 8 defs + 2 thms | 0 | [[SECREF:setup]], [[SECREF:geometry]] |
| `Coupling` | 4 defs + 3 thms | 3 | [[SECREF:lambda_deformation]] |
| `FreeEnergy` | 6 defs + 3 thms | 1 | [[SECREF:decomposition]] |
| `Geometry` | 2 defs + 4 thms | 0 | [[SECREF:geometry]] |
| `Spectral` | 4 defs + 2 thms | 1 | [[SECREF:spectral]] |
| `Heterogeneous` | 6 defs + 5 thms | 2 | [[SECREF:heterogeneous]] |
| `BernoulliToy` | 11 defs + 2 thms | 0 | [[SECREF:examples]], [[SECREF:app.bernoulli]] |
| `Decomposition` | 5 defs + 4 thms | 3 | [[SECREF:decomposition]], [[SECREF:app.proof_decomp]] |

The 10 remaining `sorry`s in the boundary fragment are intentional
placeholders whose discharge is scheduled for Phase 7 (Mathlib
enrichment).  Of the 17 boundary-form sorries that the initial Lean
draft carried, 7 have already been closed (those that reduced to
`0.0 ≤ 0.0` provable via `native_decide`, or `0.0 = 0.0` provable by
`rfl` after `unfold`).  The remaining 10 split into Float-arithmetic
identities (provable once `Float → Real`) and genuinely-Mathlib
claims (KL-positivity, rank-1 ⇔ MF, etc.).  See
[`docs/reference/lean_reference.md`](../docs/reference/lean_reference.md) for the
per-theorem status table and Mathlib refinement plan.

## Building locally

```bash
cd lean
lake build
```

Expected: `Build completed successfully (14 jobs).`  The 14 jobs are
the 9 `ActinfPolicyEntanglement.*` submodules, the
`ActinfPolicyEntanglement` root, the
`FepSketches.PolicyEntanglementBoundary` re-export, the `FepSketches`
root, and two Lake-internal targets.

## FEP_Lean / TSRCLean re-exports

`lean/FepSketches/PolicyEntanglementBoundary.lean` re-exposes the
load-bearing structural facts under the `FepSketches.*` namespace,
matching the convention used by sibling FEP_Lean / TSRCLean packages
in the [docxology/template](https://github.com/docxology/template)
monorepo.

## Refining a `sorry` (Phase 7 procedure)

When Mathlib is wired in:

1. Add `import Mathlib...` to the relevant submodule.
2. Replace `Float` with `ℝ` (`Real`) and `0.0`/`1.0` boundary stubs
   with genuine Mathlib computations.
3. Replace `sorry` with the genuine proof using
   `Mathlib.Probability.Entropy.Basic`,
   `Mathlib.Analysis.SpecialFunctions.Log.Basic`, etc.
4. Sync the corresponding Python sanity check — the Python suite at
   [`tests/`](../tests/) numerically verifies the analytic content
   already, so any divergence between proof and computation is
   caught immediately.

---
