# `FepSketches/` — Re-exports (sibling `fep_lean` layout)

Convenience wrappers that expose the load-bearing structural facts of
the Policy Entanglement boundary fragment under the `FepSketches.*`
namespace, matching the import layout used next to
[`ActiveInferenceInstitute/fep_lean`](https://github.com/ActiveInferenceInstitute/fep_lean).

## Files

* [`PolicyEntanglementBoundary.lean`](PolicyEntanglementBoundary.lean)
  — re-exports `stream_classification`, `mfImage_isMeanField`,
  `entangledFamily_eGeodesic`,
  `Bipartite.isBipartiteMeanField_factors`, and
  `couplingTax_quadratic_bound` under the `FepSketches` namespace.

The top-level [`../FepSketches.lean`](../FepSketches.lean) imports
this module and provides the `fepSketchesRoot` sanity theorem under
the `FepSketches` namespace.

## When to add a re-export

Add a re-export here when a downstream fep_lean / template consumer
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
