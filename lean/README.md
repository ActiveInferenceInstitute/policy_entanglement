# `lean/` — Lean 4 boundary fragment

Machine-checked types, definitions and theorem statements for the
Policy Entanglement framework.  The package is **Mathlib-free** at this
layer so it builds on a stock Lean toolchain (pinned to
`leanprover/lean4:v4.29.0` via [`lean-toolchain`](lean-toolchain)).

**Current boundary state.** The boundary fragment ships **17 submodules**
(plus the package root and the `FepSketches` re-export) certifying a
live Lean companion for every numbered manuscript theorem (11 witness,
5 proved, 1 forwarder, 3 boundary — no `deferred`, no `sketch`).
The additive MathlibProofs refinement plan is described in
[`ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).

## Build

```bash
cd lean
lake build           # 22/22 jobs green; sorry-free / axiom-free
```

## Layout

```
lean/
├── lakefile.lean                    ← Lake package definition
├── lean-toolchain                   ← v4.29.0 (matches fep_lean release pin)
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
| [`Scalar`](ActinfPolicyEntanglement/Scalar.lean) | In-house `CommScalar α` typeclass + algebraic lemmas reused across modules |
| [`JointDist`](ActinfPolicyEntanglement/JointDist.lean) | `PolicyFactor`, `PolicySpace`, `JointDist`, `MFDist`, `IsPMF`, marginalization, m-projection |
| [`Coupling`](ActinfPolicyEntanglement/Coupling.lean) | Coupling potentials `J` / `K_c`, `trivialCoupling`, λ-entangled prior / posterior log-weight, e-geodesic affineness |
| [`FreeEnergy`](ActinfPolicyEntanglement/FreeEnergy.lean) | `shannonEntropy`, `kl`, `variationalFreeEnergy`, `marginalFreeEnergy`, `totalCorrelation`, mean-field iff `I=0`, total correlation = KL to m-projection |
| [`Geometry`](ActinfPolicyEntanglement/Geometry.lean) | Mean-field submanifold predicate, m-projection minimizes KL (Prop 7.2), e-geodesic structural lemma (Thm 7.4), Pythagorean witness, revertibility |
| [`Spectral`](ActinfPolicyEntanglement/Spectral.lean) | Bipartite mean-field factorization, rank-one witness predicate, and Schmidt-rank-one ↔ mean-field boundary lemmas |
| [`Heterogeneous`](ActinfPolicyEntanglement/Heterogeneous.lean) | `StreamModes`, `IsPurelyReflexive` / `IsPurelyPlanning` / `IsHeterogeneous`, `couplingTax`, `couplingNormSq`, **Theorem 9.1** O(λ²) bound |
| [`BernoulliToy`](ActinfPolicyEntanglement/BernoulliToy.lean) | K=2 Ising worked example: `isingCoupling`, `isingMutualInformation`, `optimalLambda`, `isingFreeEnergyCurve`, phase predicates |
| [`Decomposition`](ActinfPolicyEntanglement/Decomposition.lean) | **Theorem 5.1** entanglement decomposition; `couplingVerdict`, `couplingPaysForItself`, mean-field reduction at λ = 0 |
| [`Constructive`](ActinfPolicyEntanglement/Constructive.lean) | Constructive existence helpers (witnesses) used by witness-form boundary theorems |
| [`Monotonicity`](ActinfPolicyEntanglement/Monotonicity.lean) | Order / monotonicity lemmas used by free-energy and coupling-tax bounds |
| [`Convexity`](ActinfPolicyEntanglement/Convexity.lean) | **Round 2.** `FreeEnergyConvexityWitness`, `LocalConcavityAtZero`; witness-form Theorem 5.6 (convexity of F in λ) and Proposition 11.1 (local concavity at λ = 0). |
| [`MarkovBlanket`](ActinfPolicyEntanglement/MarkovBlanket.lean) | **Round 2.** `MarkovBlanketSeparationWitness`; witness-form Proposition 19.3 (Markov-blanket separation as `1 − I/H`). |
| [`SpectralWitnesses`](ActinfPolicyEntanglement/SpectralWitnesses.lean) | **Round 3.** `UpperSemicontinuousRankWitness`, `SparsityRankEnvelope`; witness-form Propositions 8.2 (Schmidt-rank upper-semicontinuity) and Theorem 8.3 (sparsity-rank tradeoff). |
| [`ConnectionsWitnesses`](ActinfPolicyEntanglement/ConnectionsWitnesses.lean) | **Round 3.** `HierarchicalConcentrationWitness`, `SophisticatedInferenceEmbedding`; witness-form Theorem 17.1 (hierarchical AIF as λ → ∞) and Proposition 17.2 (sophisticated-inference embedding). |

## Status categories

Every numbered manuscript theorem has a live Lean companion in one of
four status categories (see
[`../manuscript/refs/labels.yaml`](../manuscript/refs/labels.yaml) for
the per-theorem mapping; no `deferred` or `sketch` rows remain):

| Status | Count | Meaning |
|---|---:|---|
| `witness` | 11 | Witness-consuming form; caller supplies the analytic payload. |
| `proved` | 5 | Boundary proof exists for the registered boundary statement; row-level `faithfulness:` distinguishes substantive rows from statement-restricted rows (currently 2 substantive / 3 statement-restricted). |
| `boundary` | 3 | Typed boundary rows: some are definitional boundary facts and some are witness-threaded contracts; use per-row `faithfulness:` before claiming stand-alone proof strength. |
| `forwarder` | 1 | Re-exports a theorem from another module. |
| **Total** | **21** | |

## FepSketches re-exports

`FepSketches.PolicyEntanglementBoundary` re-exposes the load-bearing
structural facts under the `FepSketches.*` namespace so downstream
fep_lean / template consumers can import a single namespace instead of
chasing each submodule.  See [`FepSketches/`](FepSketches/).

## Build cycle / token gotchas

* **No cycle**: `ActinfPolicyEntanglement.lean` (root) does NOT import
  `FepSketches.*` — that would create
  `Actinf → FepSketches.PolicyEntanglementBoundary → Actinf`.
  Instead, `FepSketches.lean` imports the boundary submodule directly.
* **Reserved tokens**: Lean 4 treats `Π` (uppercase Greek pi) and
  `λ` (lambda) as binder tokens.  Never use them as identifiers; use
  `Pol`, `q_lam`, `lam`, etc.

## Sorry / axiom / unsafe budget

The boundary fragment is **0 strict `sorry`, 0 axiom, 0
unsafe / partial / noncomputable**, enforced on every CI run by
[`scripts/build_lean.py`](../scripts/build_lean.py).  Theorems whose
full analytic content (KL chain rule, SVD, Bregman Taylor) requires
Mathlib are stated in *witness-consuming* form: the caller (or a
separate additive `MathlibProofs` layer) supplies the analytic witness, and
the boundary fragment certifies the resulting decomposition without
introducing a `sorry` of its own.  See
[`docs/reference/lean_reference.md`](../docs/reference/lean_reference.md)
for the per-theorem status table and
[`ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
for the Mathlib-enrichment plan.

## Cross-references

* Numerical companion: [`../src/`](../src/)
* Manuscript sections: [`../manuscript/`](../manuscript/)
* Architecture / math reference: [`../docs/`](../docs/)
* Agent workflow: [`AGENTS.md`](AGENTS.md)
* Lean code style (header / naming / witness-form idiom / layering): [`STYLE.md`](STYLE.md)
* MathlibProofs discharge plan: [`ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
