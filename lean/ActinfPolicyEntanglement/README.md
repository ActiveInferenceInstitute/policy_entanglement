# `ActinfPolicyEntanglement/` — Boundary fragment

The Mathlib-free Lean 4 modules that implement every typed object and
theorem statement of the Policy Entanglement framework.  Each submodule
mirrors a section of the manuscript and a sibling Python module.

## File-by-file

### [`Basic.lean`](Basic.lean)

Foundation types shared by every other module.

* `inductive InferenceMode { vfe | efe | sophisticated }` — what mode
  a stream uses (manuscript §2.2).
* `inductive CouplingPhase { disordered | mixed | frozen }` —
  cognitive phase of a coupled ensemble (manuscript §9).
* `inductive CouplingRole { habit | preference }` — role of a coupling
  potential (manuscript §11.12 / CEREBRUM).
* `inductive CouplingVerdict { pays | neutral | does_not_pay }` —
  the three-valued outcome of a coupling-pays-for-itself check.
* `abbrev StreamIdx (K : Nat) := Fin K`.
* `def IsPlanningStream`, `def IsReflexiveStream`,
  `theorem stream_classification` — every stream is reflexive or
  planning (proven by `cases`).

### [`JointDist.lean`](JointDist.lean)

Joint and mean-field policy distributions over finite policy spaces.
Mathlib-free: distributions are `α → Float` mass functions; the
predicate `IsPMF` records normalisation as a hypothesis.

* `abbrev PolicyFactor (K : Nat) := StreamIdx K → Type`.
* `def PolicySpace (K) (Pol : PolicyFactor K) := ∀ k, Pol k`.
* `abbrev JointDist`, `abbrev MFDist`.
* `def IsNonNeg`, `def IsPMF`, `def IsMeanField`.
* `def MFDist.toJointPointwise`, `def MFDist.toJoint`.
* `def JointDist.marginal`, `def JointDist.marginals`.
* `theorem mf_roundtrip_sketch`, `theorem mf_implies_marginalization_recovery`.

### [`Coupling.lean`](Coupling.lean)

Coupling potentials and the λ-entangled prior / posterior log-weights.

* `abbrev CouplingPotential`.
* `structure LabelledCoupling { potential, role }`.
* `def trivialCoupling` (zero everywhere; recovers mean-field at λ=0).
* `def entangledPriorLogWeight`, `def entangledPosteriorLogWeight`.
* `theorem entangledPosterior_logWeight_affine_in_lambda` — the
  *structural* core of Theorem 6.4 (e-geodesic).
* `theorem entangledPrior_at_zero`, `theorem entangledPosterior_at_zero` —
  boundary cases at λ=0.

### [`FreeEnergy.lean`](FreeEnergy.lean)

Information-theoretic quantities: entropy, KL, total correlation,
variational and marginal free energies.

* `def shannonEntropy`, `def klDivergence`.
* `def jointEntropy`, `def marginalEntropy`.
* `def totalCorrelation` — `I(q) = ∑_k H(q^k) − H(q)`.
* `def freeEnergy`, `def marginalFreeEnergy`.
* `theorem totalCorrelation_nonneg`.
* `theorem meanField_iff_totalCorrelation_eq_zero` — Prop 6.1 of the
  manuscript.
* `theorem totalCorrelation_eq_kl_to_mprojection` — Prop 6.3.

### [`Geometry.lean`](Geometry.lean)

Information geometry of the entanglement manifold.

* `def InMeanFieldSubmanifold`, `def mProjection`.
* `theorem mfSubmanifold_eFlat` (Prop 6.1).
* `theorem mProjection_minimises_kl` (Prop 6.2).
* `theorem entangledFamily_eGeodesic` (Theorem 6.4) — proved from
  the affineness lemma in `Coupling`.
* `theorem dualFlat_pythagorean_sketch` (manuscript §6.2).
* `theorem revertibility` — m-projection produces a mean-field
  (constructive `⟨q.marginals, rfl⟩`).

### [`Spectral.lean`](Spectral.lean)

Spectral / tensor-network structure.

* `Bipartite.schmidtRank`, `Bipartite.entanglementEntropy`.
* `theorem schmidtRank_one_iff_meanField` (Prop 7.1).
* `theorem schmidtRank_upperSemicontinuous_sketch` (Prop 7.2).
* `def tensorTrainRanks`, `def entanglementSpectrum`.
* `structure Archetype { weight, uα, vα }`.
* `theorem sparsityRank_tradeoff` (Theorem 7.3).

### [`Heterogeneous.lean`](Heterogeneous.lean)

Coupling tax for mixed VFE/EFE ensembles.

* `abbrev StreamModes (K : Nat) := StreamIdx K → InferenceMode`.
* `def reflexiveStreams`, `def planningStreams`.
* `def IsPurelyReflexive`, `def IsPurelyPlanning`, `def IsHeterogeneous`.
* `def couplingNormSq`, `def couplingTax`.
* `theorem couplingTax_nonneg`.
* `theorem couplingTax_quadratic_bound` — **Theorem 8.1**, the O(λ²)
  envelope.
* `theorem couplingTax_small_lambda_tolerance` (Corollary 8.2).
* `theorem couplingTax_purelyReflexive`,
  `theorem couplingTax_purelyPlanning` — pure-mode reductions.

### [`BernoulliToy.lean`](BernoulliToy.lean)

K = 2 closed-form worked example.

* `abbrev Action := Bool`, `def binaryFactor`.
* `def alignedIndicator`, `def isingCoupling`.
* `def floatExp`, `def floatLog`, `def floatTanh` — boundary stubs
  for `Real.exp` / `Real.log` / `Real.tanh` (replaced by Mathlib in
  Phase 7).
* `def isingMutualInformation` — closed form
  `log 2 − log(1 + e^{-λ}) − (λ/2) tanh(λ/2)`.
* `def optimalLambda`, `def isingFreeEnergyCurve`.
* `def lambdaC1`, `def lambdaC2`, `def couplingPhaseAt`.
* `theorem isingMI_zero_at_zero`, `theorem isingFreeEnergyCurve_total`.

### [`Decomposition.lean`](Decomposition.lean)

Theorem 4.1 — the core entanglement decomposition.

* `def sumMarginalFreeEnergies`, `def couplingCostTerm`,
  `def couplingPriorTerm`, `def totalCorrelationGain`.
* `def entanglementDecompositionRHS` — bundled RHS of Theorem 4.1.
* `theorem entanglement_decomposition` — **Theorem 4.1**.
* `def couplingVerdict` — Corollary 4.2 (coupling-pays-for-itself).
* `theorem decomposition_at_zero` — Corollary 4.3 (mean-field at λ=0).
* `theorem strict_gain_iff_nonMeanField` — Corollary 4.4.

## Cross-references

* Numerical companion: see [`../../src/`](../../src/).
* Manuscript sections: see [`../../manuscript/`](../../manuscript/).
* Per-theorem Mathlib refinement plan:
  [`../../docs/reference/lean_reference.md`](../../docs/reference/lean_reference.md).
