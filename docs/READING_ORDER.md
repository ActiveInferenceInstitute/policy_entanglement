# Reading order — curated paths by reader persona

Different readers need different entry points.  This page gives five
curated reading paths through the project, from a single-sentence
introduction to the deepest technical surface.

Each path lists 5–10 documents in the order they should be read.
Every link is relative to `docs/`; cross-cutting references (the
manuscript, the Lean source, the Python source, the figures) are
called out explicitly.

> **Newcomers.** If this is your first time looking at the project,
> read [`CONCEPTS.md`](CONCEPTS.md) before any persona path below.
> It is a deliberately zero-jargon three-minute capsule on what
> *policy entanglement* is, illustrated on the K=2 binary toy, and
> sets up the vocabulary every persona path assumes.  Then come back
> here and pick the persona below that matches you.

*Latest generated audit.*

---

## Persona 1: The active-inference researcher

You want to understand what the framework *predicts* and how it
relates to existing active-inference literature, without committing
to reading code or Lean.

1. [`../manuscript/0A_abstract.md`](../manuscript/0A_abstract.md) —
   the one-paragraph summary; what the framework claims.
2. [`../manuscript/1B_motivation.md`](../manuscript/1B_motivation.md)
   — why a tunable mean-field deformation is the right object.
3. [`../manuscript/2D_decomposition.md`](../manuscript/2D_decomposition.md)
   — the load-bearing decomposition identity, with corollaries.
4. [`modules/bernoulli_toy.md`](modules/bernoulli_toy.md) — the
   closed-form K = 2 worked example (the simplest case where every
   identity has a clean closed form).
5. [`../manuscript/2H_heterogeneous.md`](../manuscript/2H_heterogeneous.md)
   — heterogeneous ensembles and the `O(λ²)` coupling-tax witness,
   where the active-inference connection lands hardest.
6. [`../manuscript/5B_connections_aif.md`](../manuscript/5B_connections_aif.md)
   — the connection to classical AIF, hierarchical AIF
   (round-3 witness), and sophisticated inference (round-3 witness).
7. [`../manuscript/5D_connections_multi_agent.md`](../manuscript/5D_connections_multi_agent.md)
   — Markov-blanket separation (round-2 witness) and
   the multi-agent / CEREBRUM picture.
8. *(Optional structural bridge)* [`../manuscript/S08_gnn_generalized_notation_extension.md`](../manuscript/S08_gnn_generalized_notation_extension.md)
   — GNN as a shipped fifth structural-and-numerical representation
   (Smékal & Friedman 2023). Read this last; it adds parser /
   round-trip / Lean-emitter coverage without changing the four-track
   proof contract.

For a one-page "everything mathematically formal that appears in the
manuscript",
[`reference/math_reference.md`](reference/math_reference.md) is the
glossary.

---

## Persona 2: The Lean formalizer

You want to read every Lean file, understand the witness-structure
idiom, and see how to discharge a payload via Mathlib.

1. [`../lean/AGENTS.md`](../lean/AGENTS.md) — the Lean-side authoring
   rules + the hygiene budget.
2. [`reference/lean_reference.md`](reference/lean_reference.md) —
   per-theorem status table for every Lean declaration; the
   authoritative landing page on the Lean side.
3. [`modules/scalar_typeclass.md`](modules/scalar_typeclass.md) — the
   `CommScalar α` typeclass that lets algebraic identities be
   genuinely proved without Mathlib.
4. [`modules/heterogeneous_ensembles.md`](modules/heterogeneous_ensembles.md)
   — the coupling-tax witness + `BoundedQuadraticTax` /
   `SmallLambdaTolerance`,
   the original example of the witness-structure idiom.
5. [`modules/convexity.md`](modules/convexity.md) — round-2 witnesses
   (`FreeEnergyConvexityWitness`, `LocalConcavityAtZero`).
6. [`modules/spectral_witnesses.md`](modules/spectral_witnesses.md) —
   round-3 witnesses (`UpperSemicontinuousRankWitness`,
   `SparsityRankEnvelope`).
7. [`modules/connections_witnesses.md`](modules/connections_witnesses.md)
   — round-3 witnesses (`HierarchicalConcentrationWitness`,
   `SophisticatedInferenceEmbedding`).
8. [`modules/markov_blanket.md`](modules/markov_blanket.md) — round-2
   witness (`MarkovBlanketSeparationWitness`).
9. [`../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
   — the payload-discharge roadmap (what each witness payload needs
   from Mathlib to graduate `witness → proved`).

The Lean source itself lives under
[`../lean/ActinfPolicyEntanglement/`](../lean/ActinfPolicyEntanglement/);
all 17 submodules are small (60–250 lines).

---

## Persona 3: The Python / numerical engineer

You want to run the code, regenerate the figures, and add a new
analysis.

1. [`guides/build_run.md`](guides/build_run.md) — clone → `uv sync` →
   `lake build` → `pytest` → `run_all.py`.
2. [`guides/quickstart_recipes.md`](guides/quickstart_recipes.md) —
   copy-paste recipes for every common task.
3. [`reference/architecture.md`](reference/architecture.md) — the
   two-layer / executable-track architecture; what lives where.
4. [`reference/python_api.md`](reference/python_api.md) — index of
   the four subpackages of `src/`.
5. [`reference/python_api_lean.md`](reference/python_api_lean.md) —
   `src/lean/` (analytical mirrors of the Lean boundary fragment).
6. [`reference/python_api_simulation.md`](reference/python_api_simulation.md)
   — `src/simulation/` (pymdp harness, multi-K, long-horizon,
   revertibility).
7. [`simulation/pomdp_simulation.md`](simulation/pomdp_simulation.md)
   — the pymdp 1.0.1 harness layered design + quick example.
8. [`reference/python_api_visualizations.md`](reference/python_api_visualizations.md)
   — `src/visualizations/` figure helpers + PNG reproducibility
   metadata.
9. [`guides/testing.md`](guides/testing.md) — the no-mocks policy +
   what we test.

For a one-page audit of *what is currently working*, see
[`reference/veridical_status.md`](reference/veridical_status.md).

---

## Persona 4: The reviewer / auditor

You want to verify that the manuscript's claims are real — every
number traceable, every theorem checked, every figure reproducible.

1. [`reference/veridical_status.md`](reference/veridical_status.md)
   — the live audit page; Lean build state + pymdp run state +
   per-theorem status + variable provenance + three-tier validation
   summary.
2. [`reference/four_track_coherence.md`](reference/four_track_coherence.md)
   — the "show, not tell" contract.  How prose, equations, code, and
   Lean stay in lockstep via four CI gates.
3. [`reference/manuscript_map.md`](reference/manuscript_map.md) — the
   master cross-reference: for every section, the Lean module + the
   Python module + the test file + the docs page.
4. [`reference/_theorem_map.md`](reference/_theorem_map.md) —
   auto-generated per-theorem four-track wiring (21 rows).
5. [`reference/invariants_reference.md`](reference/invariants_reference.md)
   — per-invariant catalog (47 dashboard invariants, by family,
   each tied to its manuscript theorem and witness builder).
6. [`reference/statistics_reference.md`](reference/statistics_reference.md)
   — every grid, seed, agreement tolerance, free-energy bundle, and
   per-figure method.
7. [`reference/methods_orchestration.md`](reference/methods_orchestration.md)
   — dependency-ordered pipeline narrative: when variables are
   materialized, how figures carry provenance, and where drift is
   debugged.
8. [`guides/styleguide.md`](guides/styleguide.md) — the six hard
   manuscript ↔ code requirements.  Any violation is a CI failure.
9. [`CHANGELOG.md`](CHANGELOG.md) — what changed in each round.
10. The reproducer:
   ```bash
   uv run python scripts/run_all.py     # canonical pipeline; exits 0 if green
   ```

If you want to see a numerical witness for a specific manuscript
theorem, follow the per-theorem table in `_theorem_map.md` to the
test gate column.

---

## Persona 5: The newcomer (no prior context)

You don't know active inference, Lean, or this project.  You want a
gentle on-ramp.

1. [`README.md`](README.md) — top-level orientation (live counts +
   subdirectory map).
2. [`FAQ.md`](FAQ.md) — answers to the 15 most likely questions.
3. [`glossary.md`](glossary.md) — project jargon (boundary fragment,
   witness-form, four-track contract, …) in one place.
4. [`reference/architecture.md`](reference/architecture.md) — the
   project sits inside a research template; here is what is generic
   and what is project-specific.
5. [`../manuscript/0A_abstract.md`](../manuscript/0A_abstract.md) —
   what the framework claims.
6. [`../manuscript/1B_motivation.md`](../manuscript/1B_motivation.md)
   — why the framework matters.
7. [`modules/bernoulli_toy.md`](modules/bernoulli_toy.md) — the K=2
   worked example you can hold in your head.
8. [`modules/decomposition_theorem.md`](modules/decomposition_theorem.md)
   — the load-bearing identity, with intuition.
9. [`guides/build_run.md`](guides/build_run.md) — run the pipeline,
   see the green light, look at the figures.

If at any point you wonder *why* a number is what it is, follow the
per-theorem map in
[`reference/manuscript_map.md`](reference/manuscript_map.md) — every
claim in prose has a Lean theorem, a Python helper, a test, and a
figure.

---

## See also

* [`README.md`](README.md) — top-level docs index.
* [`AGENTS.md`](AGENTS.md) — live-report pointers and authoring rules.
* [`FAQ.md`](FAQ.md) — answers to common questions.
* [`glossary.md`](glossary.md) — project-jargon glossary.
* [`CHANGELOG.md`](CHANGELOG.md) — per-round revision history.
