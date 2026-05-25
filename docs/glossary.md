# Glossary — project jargon

*Latest generated audit.*

A reader-facing glossary for the project's *engineering* jargon —
phrases that show up across `docs/`, the AGENTS files, and the
manuscript's methodology sections but that aren't formal mathematical
symbols.

For the *mathematical* glossary (PMFs, KL, TC, free energies, geometry
objects, sign conventions), see
[`manuscript/S06_notation_and_concordance.md`](../manuscript/S06_notation_and_concordance.md)
(canonical) and
[`reference/math_reference.md`](reference/math_reference.md) (cross-track).

## A–F

- **Active inference (AIF).**  A normative framework for control under
  uncertainty in which an agent minimizes a single quantity — variational
  free energy on past + present, expected free energy on the future.
  This project formalizes a *coupled* generalization in which `K`
  streams are tied together by a deformation parameter `λ`.

- **Boundary fragment.**  The Lean 4 layer of the project: the 16
  submodules under
  [`lean/ActinfPolicyEntanglement/`](../lean/ActinfPolicyEntanglement/)
  that ship 0 `sorry`, 0 axioms, 0 Mathlib imports.  "Boundary" because
  it states each theorem at the *boundary* between algebraic primitives
  (which Lean 4 can prove) and analytic content (which belongs in a
  separate Mathlib4 discharge layer).  The boundary fragment is the
  contract that discharge layer must satisfy.

- **Boundary-form theorem.**  A theorem whose statement is in the
  boundary fragment but whose proof body extracts a witness `structure`
  (or relies only on type-level / `decide` reasoning).  Contrast with
  *witness-form*: a witness-form theorem is the same idea but the
  hypothesis is packaged as a typeclass-style `structure`.  See
  [`reference/lean_reference.md`](reference/lean_reference.md) for the
  full taxonomy.

- **Coupling tax.**  The `O(λ²)` envelope on the free-energy surplus
  incurred by leaving the mean-field submanifold.  Stated in the
  theorem registry as `thm_8_1` and carried by the witness structure
  `BoundedQuadraticTax` in
  [`Heterogeneous.lean`](../lean/ActinfPolicyEntanglement/Heterogeneous.lean).
  Numerical witness: `quadratic_bound` in
  [`src/lean/heterogeneous.py`](../src/lean/heterogeneous.py).

- **Decomposition (`thm_4_1`).**  The load-bearing identity of the
  project: `F[q_λ]` decomposes into per-stream marginal free energies +
  coupling cost + coupling-prior + multi-information.  See
  [`modules/decomposition_theorem.md`](modules/decomposition_theorem.md).

- **Deferred (status, retired).**  Historical theorem
  status meaning "stated in the manuscript, no live Lean companion".
  The current registry has no `deferred` theorem rows; every numbered
  theorem has a live Lean companion.

- **Entanglement entropy.**  The Shannon entropy of the squared
  Schmidt singular values of a K = 2 joint posterior.  Quantifies how
  far the joint is from a mean-field factorization, bounded above by
  `log(min |Π^k|)`.

- **e-flat / m-flat.**  The two flat connections on the policy
  manifold under information geometry: the *e-affine* family carries
  `log q_λ = log q_0 + λ J(π) − log Z(λ)` (an affine line in log-space),
  the *m-flat* submanifold consists of mean-field distributions
  (fixed marginal mixtures).  See
  [`modules/information_geometry.md`](modules/information_geometry.md).

- **Four-track coherence.**  The project's "show, not tell" contract:
  every claim lives simultaneously in (1) manuscript prose, (2) the
  LaTeX equation registry, (3) Python numerical companions, (4) Lean
  boundary theorems.  Drift between any two tracks is a CI failure.
  See [`reference/four_track_coherence.md`](reference/four_track_coherence.md).

## G–M

- **`fep_lean`.**  An external Lean catalog layout into which this
  project's boundary fragment is re-exported (via the
  `FepSketches.PolicyEntanglementBoundary` shim).  Adds 0 theorems
  and 0 structures; produces 1 extra lake job (the 21st).

- **Habit accumulation.**  The empirical phenomenon — pinned by the
  round-3 long-horizon experiment
  ([`scripts/simulate_long_horizon.py`](../scripts/simulate_long_horizon.py)) —
  in which per-stream marginals concentrate on the dominant archetype
  under coupled rollout.  Empirical sidecar for the hierarchical-AIF
  concentration-analog witness (`thm_11_1`), not a proof of the full
  hierarchical-AIF process theory.

- **Hyperparameter.**  A configurable scalar / grid / seed used by a
  simulation or figure script.  All defaults live in
  [`src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py)
  and are mirrored to JSON for the manuscript variable bundle.  See
  [`guides/styleguide/hyperparameters.md`](guides/styleguide/hyperparameters.md).

- **Injection token.**  A `[[…]]` placeholder in `manuscript/*.md` that
  the renderer resolves at build time from a registry (variables, labels,
  citations, Lean snippets).  Seven token namespaces:
  `[[VAR:key]]`, `[[EQ:label]]` / `[[EQREF:label]]`,
  `[[FIG:label]]` / `[[FIGREF:label]]`,
  `[[THMREF:label]]` / `[[THM:label]]`,
  `[[LEAN:label]]`, `[[SECREF:label]]`,
  Pandoc citation keys such as `[@key]` / `[@k1; @k2]`, and
  `[[CITELIST:topic]]`.
  See [`guides/styleguide.md`](guides/styleguide.md).

- **Mathlib refinement.**  The separate analytic-discharge layer that
  would construct each witness-form theorem's payload from Mathlib4.  The
  roadmap lives in
  [`MathlibRefinementRoadmap.md`](../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md);
  it is not cited as current source until a real Mathlib-backed module
  builds cleanly.

- **m-projection.**  The closest mean-field distribution (in KL) to a
  joint `q`; constructed by taking marginals and re-multiplying.  The
  *revertibility* identity says `KL(q ‖ m-proj(q)) = TC(q) = I(q)` —
  round-3 invariant `revertibility_kl_equals_multiinformation`.

- **Multi-information / total correlation.**  The KL divergence from a
  joint to the product of its marginals: `I(q) = TC(q) =
  KL(q ‖ ∏ q^k) = Σ H(q^k) − H(q)`.  Non-negative, zero iff `q` is
  mean-field.

## N–S

- **No-mocks policy.**  An absolute rule for this project: every test
  uses real numerical examples, real files, and real pymdp runs.  No
  `MagicMock`, no `mocker.patch`, no `unittest.mock`.  HTTP tests use
  `pytest-httpserver`; PDF tests use `reportlab`; file I/O uses
  `tmp_path`.  See [`guides/testing.md`](guides/testing.md).

- **Proved (status).**  Theorem with a fully-discharged Lean proof
  (no `sorry`, no witness `structure` hypothesis).  Five theorems carry
  the `proved` status.

- **pymdp 1.0.1.**  The Python active-inference import/API this project
  uses as its empirical grounding layer.  The installed distribution is
  `inferactively-pymdp==1.0.1`, pinned in the `sim` group of
  `pyproject.toml`.  K = 2 streams by default; configured multi-K sweeps
  use `MULTI_K_VALUES`.

- **Round (1, 2, 3).**  Internal review cadence.  Each round closes
  with a green `scripts/run_all.py` and a freshly-rendered PDF.  See
  [`CHANGELOG.md`](CHANGELOG.md) for the per-round delta.

- **`run_all.py`.**  The orchestrator that walks the live `SCRIPTS` table
  end-to-end in dependency order.  Exit code 0 is the canonical
  "veridical status" green light.  Lives at
  [`scripts/run_all.py`](../scripts/run_all.py).

- **Sanity rail.**  The Python numerical companion under
  [`src/lean/`](../src/lean/): pure-numpy mirrors of the Lean boundary
  primitives, exercised by the live full-suite test collection.  Catches
  arithmetic drift between the Lean statements and the empirical
  workflow.

- **Schmidt rank.**  The number of non-zero singular values of a
  K = 2 joint posterior viewed as a matrix.  Rank 1 ⇔ the joint is
  mean-field.  Generalises to *tensor-train rank* for K > 2.

- **Sketch (status, retired in round 3).**  Historical theorem status
  meaning "the Lean row is a typed witness contract rather than a
  stand-alone analytic proof".
  Round 3 emptied this row by graduating `cor_4_2` and `prop_6_1` to
  `proved`.

- **Sorry-free.**  No `sorry` keyword anywhere in the boundary
  fragment.  Enforced by
  [`scripts/build_lean.py`](../scripts/build_lean.py).

- **Stream.**  One factor in a `K`-stream policy ensemble.  Stream
  indices are `StreamIdx K = Fin K`; per-stream policies live in
  `PolicyFactor K = StreamIdx K → Type`; joint policies live in
  `PolicySpace K Pol = ∀ k, Pol k`.

## T–Z

- **Theorem registry.**  The `theorems:` section of
  [`manuscript/refs/labels.yaml`](../manuscript/refs/labels.yaml).
  Twenty entries, each carrying a `status:` field (one of
  `proved` / `witness` / `boundary` / `forwarder` /
  `sketch` (empty) / `deferred` (empty)).  The
  status-distribution table is auto-injected into the manuscript via
  `[[VAR:theorem_status_table]]`.

- **Tensor-train (TT) rank.**  A sequence of `K − 1` bond
  dimensions, one per cut, that controls the compressibility of a
  K-stream joint posterior under the matrix-product / tensor-train
  parameterization.  Witnessed in round 3 by `SparsityRankEnvelope` and
  [`scripts/simulate_multi_k.py`](../scripts/simulate_multi_k.py).

- **Veridical status.**  A live "everything-is-working" audit page at
  [`reference/veridical_status.md`](reference/veridical_status.md);
  ground-truth state of Lean build, pymdp run, per-theorem registry,
  manuscript-variable provenance, and three-tier validation.

- **Witness (status / form / structure).**
  - As a **theorem status**: the analytical / topological content is
    parameterized by a `structure` hypothesis.  Eleven theorems carry
    the `witness` status.
  - As a **theorem form** (also "witness-form"): the proof body is a
    single anonymous-constructor / field-extraction line.  The
    canonical examples are
    [`couplingTax_quadratic_bound`](../lean/ActinfPolicyEntanglement/Heterogeneous.lean)
    (round 1) and the four round-3 graduations in
    `SpectralWitnesses.lean` + `ConnectionsWitnesses.lean`.
  - As a **`structure`**: the Lean `structure` packaging the
    hypothesis fields.  Ten such structures live in the boundary
    fragment (round-1: `BoundedQuadraticTax`,
    `SmallLambdaTolerance`; round-2:
    `FreeEnergyConvexityWitness`, `LocalConcavityAtZero`,
    `MarkovBlanketSeparationWitness`; round-3:
    `UpperSemicontinuousRankWitness`, `SparsityRankEnvelope`,
    `HierarchicalConcentrationWitness`,
    `SophisticatedInferenceEmbedding`; round-5:
    `PythagoreanWitness` in `Geometry.lean`, the round-5
    Pythagorean tie-in).

- **Witness-payload discharge.**  The operation of replacing a
  `witness`-status theorem with a `proved`-status theorem by supplying
  an instance of its witness `structure` (typically via Mathlib).
  Documented in
  [`MathlibRefinementRoadmap.md`](../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).

- **GNN (Generalized Notation Notation).**  Per Smékal & Friedman
  (2023, Zenodo `10.5281/zenodo.7803328`) and the upstream repo
  [`ActiveInferenceInstitute/GeneralizedNotationNotation`](https://github.com/ActiveInferenceInstitute/GeneralizedNotationNotation):
  a model-description language for active-inference generative
  models, expressed via the *Triple Play* of linguistic, visual,
  and executable views from a single GNN source.  In this project,
  GNN is introduced in
  [`manuscript/S08_gnn_generalized_notation_extension.md`](../manuscript/S08_gnn_generalized_notation_extension.md)
  as a shipped **fifth structural-and-numerical representation**
  alongside the four proof/evidence tracks (prose / equations /
  Python / Lean). It ships a parser, K=2 round-trip, Lean typed-contract
  emitter, and pipeline stage; it does not prove theorems or promote
  registry rows.

- **GNN (graph neural network) — disambiguation.**  Same acronym, an
  orthogonal meaning.  Used at §20.Q8 ("Q8 — Learning to couple
  (graph-neural-network connection)") to name the deep-learning
  architecture family that could *learn* the coupling potentials
  $J, K_c$ from environment interactions.  Disambiguated explicitly
  at §S8.3.  The two meanings do not collapse: Generalized Notation
  Notation is a model-description *language*; graph neural networks
  are a parametric inference *architecture*.

- **Fifth representation (structural-and-numerical).**  The
  framework's four proof/evidence tracks (prose / equations / Python /
  Lean) each enforce an invariant that fails the build when violated.
  GNN now ships as an additional structural-and-numerical
  representation with parser, round-trip, Lean-emitter, and pipeline
  gates. It is not a fifth proof track: it promotes no theorem row and
  leaves GNN-to-Lean proving as open work.

## See also

- [`reference/math_reference.md`](reference/math_reference.md) —
  *mathematical* glossary (formal objects, types, Python mirrors).
- [`manuscript/S06_notation_and_concordance.md`](../manuscript/S06_notation_and_concordance.md)
  — the canonical symbol-and-sign glossary embedded in the manuscript.
- [`FAQ.md`](FAQ.md) — answers to the 15 most common
  newcomer questions, many of which expand on glossary entries above.
- [`READING_ORDER.md`](READING_ORDER.md) — curated reading paths if
  you don't yet know which entry above is most relevant to your
  task.
