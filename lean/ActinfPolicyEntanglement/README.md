# `ActinfPolicyEntanglement/` — Lean Boundary Fragment

This directory is the Mathlib-free Lean 4 boundary fragment for the
Policy Entanglement framework. It compiles on the stock toolchain pinned
in [`../lean-toolchain`](../lean-toolchain), imports no `Mathlib`, and
keeps the strict hygiene budget at zero: no `sorry`, no `axiom`, no
`unsafe`, no `partial`, and no `noncomputable` declarations.

The boundary fragment is deliberately modest about what it certifies.
It proves the algebra that stock Lean can prove without Mathlib
(`CommScalar` re-groupings, affine-in-`lam` identities, boolean verdict
correctness, bipartite factorization equivalences) and exposes the
analytic payloads as witness-consuming APIs. A future
[`MathlibProofs`](../MathlibProofs/README.md) layer can supply those
witnesses without changing these files.

## Modules

| Module | Role | Load-bearing declarations |
|---|---|---|
| [`Basic.lean`](Basic.lean) | Shared finite-index vocabulary and discrete modes. | `StreamIdx`, `PolicyFactor`, `PolicySpace`, `InferenceMode`, `CouplingPhase`, `stream_classification` |
| [`Scalar.lean`](Scalar.lean) | Mathlib-free commutative scalar laws. | `CommScalar`, `mul_sub`, `sub_mul`, `sub_self`, `affine_diff`, `affine_at_zero`, `CommScalar Int` |
| [`JointDist.lean`](JointDist.lean) | Joint and mean-field policy PMFs as total functions. | `JointDist`, `MFDist`, `IsPMF`, `mfProductWeight`, `mfToJoint`, `IsMeanField` |
| [`Coupling.lean`](Coupling.lean) | Coupling potentials and λ-log-weight algebra. | `CouplingPotential`, `couplingLogWeight`, `entangledPosteriorLogWeight`, `couplingLogWeight_affine_in_lam`, `couplingLogWeight_at_zero` |
| [`FreeEnergy.lean`](FreeEnergy.lean) | Entropy, KL, VFE, and total-correlation boundary forms. | `shannonEntropy`, `kl`, `sumStreamEntropies`, `totalCorrelation`, `totalCorrelation_def`, `totalCorrelation_eq_kl_to_mprojection` |
| [`Geometry.lean`](Geometry.lean) | Mean-field geometry and e/m projection witnesses. | `mfImage_isMeanField`, `mProjection_kl_eq_self_when_meanfield`, `entangledFamily_eGeodesic`, `PythagoreanWitness`, `dualFlat_pythagorean_boundary_identity` |
| [`Spectral.lean`](Spectral.lean) | Bipartite factorization and rank-1 boundary predicates. | `Bipartite.IsBipartiteMeanField`, `HasSchmidtRankOne`, `schmidtRankOne_iff_isBipartiteMeanField` |
| [`Heterogeneous.lean`](Heterogeneous.lean) | Mixed VFE/EFE coupling-tax witnesses. | `HorizonProfile`, `couplingTax`, `BoundedQuadraticTax`, `SmallLambdaTolerance`, `couplingTax_quadratic_bound` |
| [`BernoulliToy.lean`](BernoulliToy.lean) | K=2 closed-form toy boundary objects. | `isingCoupling`, `isingMutualInformation`, `optimalLambda`, `isingFreeEnergyCurve`, `couplingPhaseAt` |
| [`Decomposition.lean`](Decomposition.lean) | Theorem 5.1 boundary and coupling-pays corollaries. | `entanglement_decomposition`, `entanglement_decomposition_four_terms_commute_skeleton`, `couplingVerdict_correct`, `freeEnergy_closedForm_witness` |
| [`Constructive.lean`](Constructive.lean) | Small constructive algebra lemmas over `CommScalar`. | `entangledPosteriorLogWeight_at_zero`, `couplingLogWeight_trivialCoupling`, `couplingTax_zero_at_zero` |
| [`Monotonicity.lean`](Monotonicity.lean) | Named constructive wrappers around Lean core order/list facts. | `nat_le_refl`, `nat_le_trans`, `list_length_append`, `fin_lt_size` |
| [`Convexity.lean`](Convexity.lean) | Convexity and local-concavity witness contracts. | `FreeEnergyConvexityWitness`, `freeEnergy_convex_in_lam_witness`, `LocalConcavityAtZero`, `freeEnergy_localConcavity_at_zero_witness` |
| [`MarkovBlanket.lean`](MarkovBlanket.lean) | Markov-blanket separation witness contract. | `MarkovBlanketSeparationWitness`, `markovBlanket_separation_identity_witness`, `markovBlanket_separation_saturates_at_meanField` |
| [`SpectralWitnesses.lean`](SpectralWitnesses.lean) | Spectral semicontinuity and sparsity-rank witness contracts. | `UpperSemicontinuousRankWitness`, `schmidtRank_upperSemicontinuous_witness`, `SparsityRankEnvelope`, `sparsityRank_tradeoff_witness` |
| [`ConnectionsWitnesses.lean`](ConnectionsWitnesses.lean) | Classical-AIF and sophisticated-inference witness contracts. | `HierarchicalConcentrationWitness`, `hierarchicalAIF_lambda_limit_witness`, `SophisticatedInferenceEmbedding`, `sophisticatedInference_embedding_witness` |

## How To Read The Boundary

Use the status words consistently:

* `proved` means Lean discharges the declaration directly in this
  Mathlib-free package.
* `boundary` means the declaration locks an algebraic or definitional
  interface while analytic measure/probability content remains outside
  the boundary.
* `witness` means a caller supplies a structured analytic witness and
  the boundary theorem re-publishes the promised identity.
* `forwarder` means the declaration delegates to a load-bearing theorem.

No current numbered manuscript theorem is `sketch` or `deferred`; those
are historical registry states only. The live status table is
[`../../docs/reference/veridical_status.md`](../../docs/reference/veridical_status.md),
and the per-theorem Lean inventory is
[`../../docs/reference/lean_reference.md`](../../docs/reference/lean_reference.md).

## Verification

Run both checks before editing downstream Python or manuscript prose:

```bash
cd ../
lake build
cd ..
uv run python scripts/build_lean.py
```

`scripts/build_lean.py` is the stricter gate: it runs Lake and scans the
boundary fragment for forbidden `sorry`, `axiom`, `unsafe`, `partial`,
`noncomputable`, and `Mathlib` regressions.
