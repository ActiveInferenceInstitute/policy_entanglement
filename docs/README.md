# `docs/` — Modular technical documentation

A complete technical reference for the Policy Entanglement project,
organized into four topic subdirectories so a reader can find any
concept in two clicks.

> **Citation metadata:** DOI [`10.5281/zenodo.20419431`](https://doi.org/10.5281/zenodo.20419431); source repository URL
> is set in [`manuscript/config.yaml`](../manuscript/config.yaml) and the abstract
> · cite via [`CITATION.cff`](../CITATION.cff)

> **Latest generated audit:** live counts come from generated reports,
> not this prose. Read `output/reports/release_readiness.json` for
> tests, coverage, PDF, figure, MathlibProofs, runtime, and artifact
> counts; `output/data/manuscript_variables.json` for Lean declaration
> and theorem-registry roll-ups; `output/reports/dashboard_invariants.txt`
> for dashboard invariants; and `output/MANIFEST.md` for pipeline timing.
> The boundary fragment remains stock-Lean, Mathlib-free, and hygiene
> clean by `scripts/build_lean.py`. Historical count movement is recorded
> in [`CHANGELOG.md`](CHANGELOG.md).

## Subdirectories

| Subdir | Audience | Purpose |
|---|---|---|
| [`reference/`](reference/) | All | Cross-cutting references — architecture, math, Lean theorems, Python API, manuscript ↔ code map |
| [`guides/`](guides/) | Engineers | How-to: build, run, test, recipe-based quickstart |
| [`modules/`](modules/) | Researchers | Per-concept deep dives (decomposition, geometry, spectral, Bernoulli, heterogeneous, **convexity**, **Markov blanket**, **spectral witnesses**, **connections witnesses**) |
| [`simulation/`](simulation/) | Researchers / Engineers | pymdp 1.0.1 POMDP harness + visualization helpers |

## Cross-cutting top-level pages

* [`CHANGELOG.md`](CHANGELOG.md) — per-round revision history (rounds 1, 2, 3).
* [`FAQ.md`](FAQ.md) — answers to the 15 most likely newcomer questions.
* [`READING_ORDER.md`](READING_ORDER.md) — curated reading paths by reader persona (active-inference researcher, Lean formalizer, Python engineer, reviewer, newcomer).
* [`glossary.md`](glossary.md) — project-jargon glossary (boundary fragment, witness-form, four-track contract, …); complements the mathematical glossary under [`reference/math_reference.md`](reference/math_reference.md) and the canonical symbol-and-sign glossary [`manuscript/S06_notation_and_concordance.md`](../manuscript/S06_notation_and_concordance.md).
* [`reference/methods_and_assumptions.md`](reference/methods_and_assumptions.md) — **normative** methods & assumptions ledger: the three verification tiers (ℝ machine-checked / Float-boundary / typed-contract / numerically-witnessed), the per-row strength table, Theorem 5.1's ℝ proof status, the Float↔ℝ residual, and empirical estimator definitions. Read this for claim-strength language.
* [`AGENTS.md`](AGENTS.md) — live-report pointers + authoring rules for agents.

## Reading order

For a first pass, read:
1. [`reference/architecture.md`](reference/architecture.md) — two-layer / executable-track design.
2. [`guides/styleguide.md`](guides/styleguide.md) — **the manuscript ↔ code contract**: configurable simulations, auto-injected variables, equation/figure auto-numbering, citation resolution, American English, and evidence-first prose.
3. [`reference/veridical_status.md`](reference/veridical_status.md) — live audit page: Lean + pymdp + variable-provenance state.
4. [`reference/methods_audit.md`](reference/methods_audit.md) — compact Lean + pymdp methods audit.
5. [`reference/reproducibility_checklist.md`](reference/reproducibility_checklist.md) — release/readiness gate for reviewers.
6. [`guides/build_run.md`](guides/build_run.md) — how to compile, test, and render.
7. [`reference/math_reference.md`](reference/math_reference.md) — every formal object in one page.

Then deep dives:

* [`modules/decomposition_theorem.md`](modules/decomposition_theorem.md) — the load-bearing decomposition identity.
* [`modules/information_geometry.md`](modules/information_geometry.md) — e/m flatness, m-projection, Pythagorean structure, e-geodesic.
* [`modules/spectral_structure.md`](modules/spectral_structure.md) — Schmidt decomposition, archetypes, tensor-train ranks.
* [`modules/heterogeneous_ensembles.md`](modules/heterogeneous_ensembles.md) — the coupling-tax witness and heterogeneous ensemble tax.
* [`modules/bernoulli_toy.md`](modules/bernoulli_toy.md) — closed-form K = 2 worked example.
* [`modules/convexity.md`](modules/convexity.md) — convexity witness (`thm_4_3`) and local concavity at λ = 0 (`prop_10_1`) discharged by `Convexity.lean`.
* [`modules/markov_blanket.md`](modules/markov_blanket.md) — Markov-blanket separation identity (`prop_11_3`) discharged by `MarkovBlanket.lean`.
* [`modules/spectral_witnesses.md`](modules/spectral_witnesses.md) — Schmidt-rank upper-semicontinuity (`prop_7_2`) + sparsity-rank tradeoff (`thm_7_3`) discharged by `SpectralWitnesses.lean`.
* [`modules/connections_witnesses.md`](modules/connections_witnesses.md) — hierarchical AIF as `λ → ∞` limit (`thm_11_1`) + sophisticated-inference embedding (`prop_11_2`) discharged by `ConnectionsWitnesses.lean`.
* [`reference/lean_reference.md`](reference/lean_reference.md) — every Lean theorem, its status (one of `proved` / `boundary` / `witness` / `forwarder`; `sketch` and `deferred` rows are empty as of round 3), and its Mathlib refinement plan (in [`MathlibRefinementRoadmap.md`](../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)).
* [`reference/methods_audit.md`](reference/methods_audit.md) — verified Lean and pymdp method contracts.
* [`reference/python_api.md`](reference/python_api.md) — every Python function, signature, and contract.
* [`simulation/pomdp_simulation.md`](simulation/pomdp_simulation.md) — pymdp 1.0.1 POMDP harness (specs, builders, agents, inference, rollout, sweep).
* [`simulation/visualizations.md`](simulation/visualizations.md) — reusable plotting helpers.
* [`guides/testing.md`](guides/testing.md) — what we test, how, and why no mocks.

## File map

| File | Subdir | Purpose |
|---|---|---|
| [`reference/architecture.md`](reference/architecture.md) | reference | Two-layer / executable-track architecture, file-layout map |
| [`reference/math_reference.md`](reference/math_reference.md) | reference | Glossary of formal objects (PMFs, marginals, KL, TC, free energies, geometry) |
| [`reference/statistics_reference.md`](reference/statistics_reference.md) | reference | Determinism contract, grid sizes, agreement tolerances, free-energy bundle, per-figure stats |
| [`reference/veridical_status.md`](reference/veridical_status.md) | reference | Live audit — Lean build state, pymdp run state, per-theorem status table, variable provenance chain, validation summary |
| [`reference/methods_audit.md`](reference/methods_audit.md) | reference | Lean + pymdp methods audit |
| [`reference/reproducibility_checklist.md`](reference/reproducibility_checklist.md) | reference | Release/readiness checklist: pipeline, PDF, variables, figure metadata, and review slices |
| [`reference/lean_reference.md`](reference/lean_reference.md) | reference | Per-theorem status table + sorry inventory (current: 17 modules, 126 declarations) |
| [`reference/invariants_reference.md`](reference/invariants_reference.md) | reference | Per-invariant catalog (47 invariants from `src/lean/invariants.py` + the round-3 `revertibility_kl_equals_multiinformation`) |
| [`reference/python_api.md`](reference/python_api.md) | reference | Per-function signatures, contracts, examples |
| [`reference/manuscript_map.md`](reference/manuscript_map.md) | reference | Section-by-section map: manuscript ↔ Lean ↔ Python ↔ tests ↔ docs |
| [`guides/styleguide.md`](guides/styleguide.md) | guides | **Manuscript ↔ code contract** — configurable simulations, injected variables, equation / figure auto-numbering, citation rules, American English |
| [`guides/build_run.md`](guides/build_run.md) | guides | Compile, test, render, generate figures |
| [`guides/quickstart_recipes.md`](guides/quickstart_recipes.md) | guides | Copy-paste recipes for every common task |
| [`guides/testing.md`](guides/testing.md) | guides | No-mocks policy, coverage targets, invariants checked |
| [`modules/decomposition_theorem.md`](modules/decomposition_theorem.md) | modules | Statement, proof scaffold, and numerical checks for the decomposition identity |
| [`modules/information_geometry.md`](modules/information_geometry.md) | modules | Dual-flat geometry of the entanglement manifold |
| [`modules/spectral_structure.md`](modules/spectral_structure.md) | modules | Schmidt rank, archetypes, tensor-train ranks |
| [`modules/heterogeneous_ensembles.md`](modules/heterogeneous_ensembles.md) | modules | Theorem 9.1 — O(λ²) coupling-tax envelope |
| [`modules/bernoulli_toy.md`](modules/bernoulli_toy.md) | modules | K=2 Ising worked example, closed-form MI |
| [`modules/convexity.md`](modules/convexity.md) | modules | **(round 2)** Convexity witness (`thm_4_3`) and local concavity at λ = 0 (`prop_10_1`) via `Convexity.lean` |
| [`modules/markov_blanket.md`](modules/markov_blanket.md) | modules | **(round 2)** Markov-blanket separation identity (`prop_11_3`) via `MarkovBlanket.lean` |
| [`modules/spectral_witnesses.md`](modules/spectral_witnesses.md) | modules | **(round 3)** Schmidt-rank upper-semicontinuity (`prop_7_2`) + sparsity-rank tradeoff (`thm_7_3`) via `SpectralWitnesses.lean` |
| [`modules/connections_witnesses.md`](modules/connections_witnesses.md) | modules | **(round 3)** Hierarchical AIF λ→∞ limit (`thm_11_1`) + sophisticated-inference embedding (`prop_11_2`) via `ConnectionsWitnesses.lean` |
| [`simulation/pomdp_simulation.md`](simulation/pomdp_simulation.md) | simulation | pymdp 1.0.1 harness architecture + API |
| [`simulation/visualizations.md`](simulation/visualizations.md) | simulation | Reusable plotting helpers |

## Lean Fragment Snapshot

| Metric | Value | Notes |
|---|---|---|
| Boundary submodules | Live in `output/data/manuscript_variables.json` | includes `Convexity`, `MarkovBlanket`, `SpectralWitnesses`, and `ConnectionsWitnesses` |
| Lake jobs | Live in `scripts/build_lean.py` output and `output/reports/release_readiness.json` | verified by the release gate |
| Public theorems / lemmas | Live in `output/data/manuscript_variables.json` | derived by `scripts/manuscript_variables.py` |
| Definitions (`def`) | Live in `output/data/manuscript_variables.json` | derived by `scripts/manuscript_variables.py` |
| Structures | Live in `output/data/manuscript_variables.json` | witness structures, including `PythagoreanWitness` |
| Total declarations | Live in `output/data/manuscript_variables.json` | derived, not hand-maintained |
| Strict `sorry` | Guarded zero budget | enforced by `scripts/build_lean.py` |
| `axiom` declarations | Guarded zero budget | enforced by `scripts/build_lean.py` |
| `unsafe` / `partial` / `noncomputable` | Guarded zero budget | enforced by `scripts/build_lean.py` |
| Boundary Mathlib imports | Guarded zero budget | stock Lean v4.29.0 boundary |

### Theorem-registry roll-up

Reading off `manuscript/refs/labels.yaml::theorems` via generated reports:

| Status | Count | Theorems |
|---|---|---|
| `witness` | Live | See `output/data/manuscript_variables.json` and `docs/reference/_theorem_map.md` |
| `proved` | Live | See `output/data/manuscript_variables.json` and `docs/reference/_theorem_map.md` |
| `boundary` | Live | See `output/data/manuscript_variables.json` and `docs/reference/_theorem_map.md` |
| `forwarder` | Live | See `output/data/manuscript_variables.json` and `docs/reference/_theorem_map.md` |
| retired statuses | Guarded empty | `sketch` and `deferred` are rejected for current rows |

All 20 theorem rows carry a live Lean companion (witness / proved /
boundary / forwarder), and the additional roadmap row resolves to the
`FloatRealResidualWitness` boundary scaffold.  Zero rows remain
`deferred` or `sketch`.

## Conventions

* **Cross-references** use relative links (`../lean/...`, `../src/...`,
  `../manuscript/...`).  Inside `docs/<subdir>/foo.md` the project
  root is two levels up: `../../lean/`, `../../src/`, etc.
* **Math notation** matches the manuscript (`λ`, `q^k`, `D_KL`).  Sign
  conventions for $F$, $G$, and $\log q$ are pinned in
  [`../manuscript/S06_notation_and_concordance.md`](../manuscript/S06_notation_and_concordance.md)
  under the registry label `notation.sign_conventions`.
* **Theorem labels** match the manuscript section number, not internal
  Lean naming, where the two diverge.
