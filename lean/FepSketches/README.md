# `FepSketches/` — Re-exports for the FEP_Lean monorepo

Convenience wrappers that expose the load-bearing structural facts of
the Policy Entanglement boundary fragment under the `FepSketches.*`
namespace, matching the convention used by sibling FEP_Lean / TSRCLean
packages.

## Files

* [`PolicyEntanglementBoundary.lean`](PolicyEntanglementBoundary.lean)
  — re-exports `stream_classification`, `mf_roundtrip_sketch`,
  `revertibility`, `entangledFamily_eGeodesic`,
  `couplingTax_purelyReflexive`.

The top-level [`../FepSketches.lean`](../FepSketches.lean) imports
this module and provides the `fepSketchesRoot` sanity theorem under
the `FepSketches` namespace.

## When to add a re-export

Add a re-export here when a downstream FEP_Lean / TSRCLean agent
depends on the fact and the `ActinfPolicyEntanglement.*` import path
is not appropriate.  Each re-export should:

1. Have the same statement as the original (no changes).
2. Be defined as a forwarding `theorem foo_reexport ... := foo` so
   the dependency on the boundary fragment is explicit.
3. Be added to [`README.md`](README.md) in this directory.

## Build cycle warning

This subdirectory imports `ActinfPolicyEntanglement` (the root).  Do
**not** add `import FepSketches.PolicyEntanglementBoundary` to the
`ActinfPolicyEntanglement.lean` root — Lake will detect the cycle.
The current setup deliberately keeps imports one-way:

```
ActinfPolicyEntanglement.*
       ↑                ↓
       └────────────────┘
           (forbidden)

FepSketches.PolicyEntanglementBoundary  →  ActinfPolicyEntanglement
FepSketches                              →  FepSketches.PolicyEntanglementBoundary
```
