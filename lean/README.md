# `lean/` — Lean 4 boundary fragment

Machine-checked types, definitions and theorem statements for the
Policy Entanglement framework.  The package is **Mathlib-free** at this
layer so it builds on a stock Lean toolchain (pinned to
`leanprover/lean4:v4.29.0` via [`lean-toolchain`](lean-toolchain)).

## Build

```bash
cd lean
lake build           # 14/14 jobs green; only deliberate `sorry` warnings
```

## Layout

```
lean/
├── lakefile.lean                    ← Lake package definition
├── lean-toolchain                   ← v4.29.0 (matches FEP_Lean release env)
├── lake-manifest.json               ← Generated lockfile
├── ActinfPolicyEntanglement.lean    ← Root module: imports every submodule
├── ActinfPolicyEntanglement/        ← Boundary-fragment submodules (see below)
├── FepSketches.lean                 ← Top-level FepSketches re-export hub
└── FepSketches/                     ← FepSketches.* re-exports
```

## Submodule index

| Submodule | Purpose |
|---|---|
| [`Basic`](ActinfPolicyEntanglement/Basic.lean) | `InferenceMode`, `CouplingPhase`, `CouplingRole`, `CouplingVerdict`, `StreamIdx`, stream classification |
| [`JointDist`](ActinfPolicyEntanglement/JointDist.lean) | `PolicyFactor`, `PolicySpace`, `JointDist`, `MFDist`, `IsPMF`, marginalisation, m-projection |
| [`Coupling`](ActinfPolicyEntanglement/Coupling.lean) | Coupling potentials `J` / `K_c`, `LabelledCoupling`, λ-entangled prior / posterior log-weight, e-geodesic affineness |
| [`FreeEnergy`](ActinfPolicyEntanglement/FreeEnergy.lean) | `shannonEntropy`, `klDivergence`, `freeEnergy`, `marginalFreeEnergy`, `totalCorrelation`, mean-field iff `I=0`, total correlation = KL to m-projection |
| [`Geometry`](ActinfPolicyEntanglement/Geometry.lean) | Mean-field submanifold predicate, m-projection minimises KL (Prop 6.2), e-geodesic structural lemma (Thm 6.4), Pythagorean sketch, revertibility |
| [`Spectral`](ActinfPolicyEntanglement/Spectral.lean) | `Bipartite.schmidtRank`, `entanglementEntropy`, `Archetype`, `tensorTrainRanks`, `entanglementSpectrum`, sparsity-rank tradeoff |
| [`Heterogeneous`](ActinfPolicyEntanglement/Heterogeneous.lean) | `StreamModes`, `IsPurelyReflexive` / `IsPurelyPlanning` / `IsHeterogeneous`, `couplingTax`, `couplingNormSq`, **Theorem 8.1** O(λ²) bound |
| [`BernoulliToy`](ActinfPolicyEntanglement/BernoulliToy.lean) | K=2 Ising worked example: `isingCoupling`, `isingMutualInformation`, `optimalLambda`, `isingFreeEnergyCurve`, phase predicates |
| [`Decomposition`](ActinfPolicyEntanglement/Decomposition.lean) | **Theorem 4.1** entanglement decomposition; `couplingVerdict`, `couplingPaysForItself`, mean-field reduction at λ = 0 |

## FepSketches re-exports

`FepSketches.PolicyEntanglementBoundary` re-exposes the load-bearing
structural facts under the `FepSketches.*` namespace so downstream
FEP_Lean / TSRCLean agents can import a single namespace instead of
chasing each submodule.  See [`FepSketches/`](FepSketches/).

## Build cycle / token gotchas

* **No cycle**: `ActinfPolicyEntanglement.lean` (root) does NOT import
  `FepSketches.*` — that would create
  `Actinf → FepSketches.PolicyEntanglementBoundary → Actinf`.
  Instead, `FepSketches.lean` imports the boundary submodule directly.
* **Reserved tokens**: Lean 4 treats `Π` (uppercase Greek pi) and
  `λ` (lambda) as binder tokens.  Never use them as identifiers; use
  `Pol`, `q_lam`, `lam`, etc.

## Sorry budget

Boundary-form `sorry` placeholders are intentional — they hold the
type signature of an analytic claim that requires Mathlib's KL
machinery, log identities, or SVD lemmas.  They are not bugs; they
are TODO markers for Phase 7 (Mathlib enrichment).  See
[`docs/reference/lean_reference.md`](../docs/reference/lean_reference.md) for the
per-theorem status table and [`docs/reference/phase7_plan.md`](../docs/reference/phase7_plan.md)
for the discharge order.

## Cross-references

* Numerical companion: [`../src/`](../src/)
* Manuscript sections: [`../manuscript/`](../manuscript/)
* Architecture / math reference: [`../docs/`](../docs/)
