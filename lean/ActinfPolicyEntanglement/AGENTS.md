# AGENTS.md — `ActinfPolicyEntanglement/`

## Identity & Scope

Lean 4 boundary fragment for the Policy Entanglement project.
**Sixteen** submodules under `lean/ActinfPolicyEntanglement/` plus the
`ActinfPolicyEntanglement.lean` root, building on **stock Lean 4
v4.29.0** with **no Mathlib dependency**, **no `sorry`**, **no
`axiom`**, and **no `unsafe` / `partial` / `noncomputable`**. Phase 0
is complete: every numbered manuscript theorem (21 total) has a live
Lean companion — 11 witness, 5 proved, 1 forwarder, 3 boundary.

The Mathlib-witness analytic content (KL chain rule, matrix SVD,
Bregman Taylor expansion, measure-tightness, recursive Bellman
embedding) lives outside the boundary; when a Mathlib extension is
added it composes on top of the witness/boundary theorem rows
(`couplingTax_quadratic_bound`, `entanglement_decomposition`,
`dualFlat_pythagorean_witness`, `freeEnergy_convex_in_lam_witness`,
`freeEnergy_localConcavity_at_zero_witness`,
`markovBlanket_separation_identity_witness`,
`schmidtRank_upperSemicontinuous_witness`,
`sparsityRank_tradeoff_witness`,
`hierarchicalAIF_lambda_limit_witness`,
`sophisticatedInference_embedding_witness`) without disturbing the
core.

## Submodule map (live, source-of-truth verified)

| Module | Round | Witness payload / notes |
|---|---|---|
| `Basic.lean` | 1 | core types (`PolicyFactor`, `InferenceMode`, `CouplingPhase`, …), stream-mode trichotomy. |
| `Scalar.lean` | 1 | abstract `CommScalar α` typeclass + algebraic lemmas (`affine_diff`, `sub_self`, `mul_sub`, …); ships an `Int` instance. |
| `JointDist.lean` | 1 | joint / mean-field PMFs, marginalization, m-projection. |
| `Coupling.lean` | 1 | coupling potentials `J` / `K_c`, λ-entangled prior / posterior, e-geodesic affineness. |
| `FreeEnergy.lean` | 1 | variational + marginal free energies, entropies, total correlation, MF ↔ I = 0 equivalence. |
| `Geometry.lean` | 1 | e/m-flatness, m-projection (Prop 7.2), Pythagorean witness (Prop 7.5), e-geodesic (Thm 7.4). |
| `Spectral.lean` | 1 | `Bipartite.schmidtRank`, `Bipartite.entanglementEntropy`, archetypes, bipartite MF factorization (Prop 8.1). |
| `Heterogeneous.lean` | 1 | `couplingTax`, `BoundedQuadraticTax`, `SmallLambdaTolerance`; Theorem 9.1 + Corollary 9.2. |
| `BernoulliToy.lean` | 1 | K = 2 Ising toy: closed-form MI, optimal λ, phase predicates. |
| `Decomposition.lean` | 1 | **Theorem 5.1** entanglement decomposition; `couplingVerdict`, mean-field at λ = 0, strict-gain identity. |
| `Constructive.lean` | 1 | constructive existence helpers consumed by the witness-form theorems. |
| `Monotonicity.lean` | 1 | order / monotonicity lemmas on `Nat`, `Or`, `And`, `List`, `Fin`. |
| `Convexity.lean` | 2 | `FreeEnergyConvexityWitness`, `LocalConcavityAtZero`; witness-form Thm 5.6 + Prop 11.1. |
| `MarkovBlanket.lean` | 2 | `MarkovBlanketSeparationWitness`; witness-form Prop 19.3 (separation as `1 − I/H`). |
| `SpectralWitnesses.lean` | 3 | `UpperSemicontinuousRankWitness`, `SparsityRankEnvelope`; witness-form Prop 8.2 + Thm 8.3. |
| `ConnectionsWitnesses.lean` | 3 | `HierarchicalConcentrationWitness`, `SophisticatedInferenceEmbedding`; witness-form Thm 17.1 + Prop 17.2. |

Live aggregate (verified by the comment-stripped declaration scan in
`scripts/manuscript_variables.py`):
**76 theorems / lemmas, 11 structures, 39 defs, 126 counted
declarations, 0 strict `sorry`, 0 axioms, 22/22 lake jobs green.**

## Repository Constitution

1. **Stock Lean only.**  Do not add `import Mathlib...` to any module
   in this directory.  Mathlib refinement, when added, lives in a
   separate `MathlibProofs` library inside `lean/`.
2. **Hygiene budget = 0.**  No `sorry`, no `axiom`, no
   `unsafe` / `partial` / `noncomputable`.  Enforced by
   `scripts/build_lean.py`.
3. **Reserved tokens.**  `Π` and `λ` are Lean 4 binder tokens; use
   `Pol`, `q_lam`, `lam` as substitutes.
4. **CommScalar abstraction.**  Algebraic lemmas live on the in-house
   `CommScalar α` typeclass (`Scalar.lean`); concrete instances pin
   `α := Float` only at module boundaries.
5. **Witness boundary.**  Theorems whose full proof requires Mathlib
   are stated in *witness-consuming* form: the caller supplies the
   analytic witness (e.g. a real-valued bound), and the boundary
   fragment certifies the resulting decomposition without `sorry`.
6. **Cross-track parity.**  Every Lean concept has a Python mirror
   under `src/lean/<module>.py` and a Python test in
   `tests/test_<module>.py`.

## Cross-Track Invariants

| Concept | Lean module | Python module |
|---|---|---|
| Joint / mean-field PMFs | `JointDist` | [`src/lean/joint_dist.py`](../../src/lean/joint_dist.py) |
| Abstract scalar laws | `Scalar` | (implicit — `numpy.float64`) |
| Coupling potentials, λ-entangled posterior | `Coupling` | [`src/lean/coupling.py`](../../src/lean/coupling.py) |
| Free energies, entropies, total correlation | `FreeEnergy` | [`src/lean/free_energy.py`](../../src/lean/free_energy.py) |
| e/m-flatness, m-projection, Pythagorean | `Geometry` | [`src/lean/geometry.py`](../../src/lean/geometry.py) |
| Bipartite mean-field, archetypes | `Spectral` | [`src/lean/spectral.py`](../../src/lean/spectral.py) |
| Heterogeneous VFE/EFE, coupling tax | `Heterogeneous` | [`src/lean/heterogeneous.py`](../../src/lean/heterogeneous.py) |
| K=2 Bernoulli toy | `BernoulliToy` | [`src/lean/bernoulli_toy.py`](../../src/lean/bernoulli_toy.py) |
| Theorem 5.1 entanglement decomposition | `Decomposition` | [`src/lean/decomposition.py`](../../src/lean/decomposition.py) |
| Constructive existence helpers | `Constructive` | (no Python — boundary witnesses) |
| Order / monotonicity lemmas | `Monotonicity` | (implicit via `numpy` order) |
| Convexity of F in λ; local concavity at λ = 0 | `Convexity` | (witness-side; numerical mirror in [`src/lean/free_energy.py`](../../src/lean/free_energy.py) and [`scripts/parameter_sweep.py`](../../scripts/parameter_sweep.py)) |
| Markov-blanket separation as `1 − I/H` | `MarkovBlanket` | (witness-side; numerical mirror in [`src/lean/free_energy.py`](../../src/lean/free_energy.py) — `shannon_entropy`, `total_correlation`) |
| Schmidt-rank USC, sparsity-rank tradeoff | `SpectralWitnesses` | (witness-side, no direct Python mirror) |
| Hierarchical AIF limit, sophisticated inference | `ConnectionsWitnesses` | (witness-side, no direct Python mirror) |

## Validation Checklist

```bash
# Lean: stock-Lean, sorry-free, axiom-free build
cd lean && lake build                            # 22/22 jobs
cd .. && uv run python scripts/build_lean.py     # hygiene budget gate

# Python: full env, full tests
uv sync --group sim --group viz
uv run pytest tests/ --cov=src --cov-fail-under=95  # live count in output/reports/test_results.json

# Pipeline: every artifact + manuscript validator
uv run python scripts/run_all.py                 # exits 0 end-to-end
```

## Separate MathlibProofs Layer

The **17 boundary modules** are stable. The separate
`lean/MathlibProofs/` package is the only place Mathlib imports belong:
it now proves the headline real-valued decomposition, while remaining
witness-payload discharge claims still require real sorry-free Mathlib
source and a green separate build. No `deferred` row remains in
`manuscript/refs/labels.yaml`; MathlibProofs work is purely additive
and never permits Mathlib imports inside this boundary directory. Plan:
[`MathlibRefinementRoadmap.md`](MathlibRefinementRoadmap.md).

## How Agents Should Work

| Want to … | Edit | Then run |
|---|---|---|
| add a Lean theorem | a file in this directory | `cd lean && lake build` (then `python scripts/build_lean.py` for hygiene) |
| add an algebraic lemma reusable across modules | `Scalar.lean` | `cd lean && lake build` |
| add a constructive existence helper | `Constructive.lean` | `cd lean && lake build` |
| add an order / monotonicity lemma | `Monotonicity.lean` | `cd lean && lake build` |
| add a convexity / concavity witness | `Convexity.lean` | `cd lean && lake build` |
| add a Markov-blanket witness | `MarkovBlanket.lean` | `cd lean && lake build` |
| add a spectral USC / tensor-rank witness | `SpectralWitnesses.lean` | `cd lean && lake build` |
| add a hierarchical / sophisticated-inference witness | `ConnectionsWitnesses.lean` | `cd lean && lake build` |
| mirror a theorem to Python | `src/lean/<module>.py` + `tests/test_<module>.py` | `uv run pytest tests/test_<module>.py` |
| register a theorem for the manuscript | `manuscript/refs/labels.yaml` under `theorems:` (set `lean_module` + `lean_name`) | `uv run python scripts/inject_manuscript_variables.py` (the renderer extracts the live source) |
