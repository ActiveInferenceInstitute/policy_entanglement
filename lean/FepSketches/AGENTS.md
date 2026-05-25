# AGENTS.md — `FepSketches`

## Identity & Scope

`lean/FepSketches/PolicyEntanglementBoundary.lean` re-exports the
load-bearing boundary-fragment theorems from
`ActinfPolicyEntanglement/` under the `FepSketches.*` namespace,
matching the convention used alongside the
[`ActiveInferenceInstitute/fep_lean`](https://github.com/ActiveInferenceInstitute/fep_lean)
catalog in the [docxology/template](https://github.com/docxology/template)
monorepo.

The re-export is a **pure namespace alias** — no new theorem content,
no Mathlib imports, no `sorry`.  The boundary fragment it re-exports
is itself stock-Lean, Mathlib-free, and
zero-strict-`sorry`. See
[`../ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
for the additive MathlibProofs path that discharges the headline
real-valued decomposition and lays out the remaining row-specific
witness-payload work.

### Validation

```bash
cd lean && lake build       # 22/22 jobs green
```

### Adding a re-export

1. Identify a theorem in `ActinfPolicyEntanglement/<Module>.lean`
   that other monorepo packages will consume.
2. Add a one-line re-export in
   `lean/FepSketches/PolicyEntanglementBoundary.lean`:
   ```lean
   namespace FepSketches
   /-- Forwarder for `ActinfPolicyEntanglement.<Module>.<theorem_name>`. -/
   theorem theorem_name := ActinfPolicyEntanglement.<Module>.theorem_name
   end FepSketches
   ```
3. `lake build` to confirm.

### Optional Additive MathlibProofs Layer

Mathlib refinements live in a *separate* optional `MathlibProofs` Lake
library, not here.  That layer is independently buildable and now
carries the headline real-valued decomposition discharge; other witness
rows may cite it only after real sorry-free row-specific Mathlib source
builds green in that separate package. This re-export module remains
stock-Lean and Mathlib-free. The roadmap is
[`../ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).
