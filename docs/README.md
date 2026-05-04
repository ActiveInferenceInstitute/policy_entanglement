# `docs/` — Modular technical documentation

A complete technical reference for the Policy Entanglement project,
organised into four topic subdirectories so a reader can find any
concept in two clicks.

## Subdirectories

| Subdir | Audience | Purpose |
|---|---|---|
| [`reference/`](reference/) | All | Cross-cutting references — architecture, math, Lean theorems, Python API, manuscript ↔ code map |
| [`guides/`](guides/) | Engineers | How-to: build, run, test, recipe-based quickstart |
| [`modules/`](modules/) | Researchers | Per-concept deep dives (decomposition, geometry, spectral, Bernoulli, heterogeneous) |
| [`simulation/`](simulation/) | Researchers / Engineers | pymdp 1.0.1 POMDP harness + visualization helpers |

## Reading order

For a first pass, read:
1. [`reference/architecture.md`](reference/architecture.md) — two-layer / two-track design.
2. [`guides/build_run.md`](guides/build_run.md) — how to compile, test, and render.
3. [`reference/math_reference.md`](reference/math_reference.md) — every formal object in one page.

Then deep dives:

* [`modules/decomposition_theorem.md`](modules/decomposition_theorem.md) — Theorem 4.1 (the load-bearing identity).
* [`modules/information_geometry.md`](modules/information_geometry.md) — e/m flatness, m-projection, Pythagorean structure, e-geodesic.
* [`modules/spectral_structure.md`](modules/spectral_structure.md) — Schmidt decomposition, archetypes, tensor-train ranks.
* [`modules/heterogeneous_ensembles.md`](modules/heterogeneous_ensembles.md) — Theorem 8.1 and the coupling tax.
* [`modules/bernoulli_toy.md`](modules/bernoulli_toy.md) — closed-form K = 2 worked example.
* [`reference/lean_reference.md`](reference/lean_reference.md) — every Lean theorem, its status (proved / boundary / sorry), and its Mathlib refinement plan.
* [`reference/python_api.md`](reference/python_api.md) — every Python function, signature, and contract.
* [`simulation/pomdp_simulation.md`](simulation/pomdp_simulation.md) — pymdp 1.0.1 POMDP harness (specs, builders, agents, inference, rollout, sweep).
* [`simulation/visualizations.md`](simulation/visualizations.md) — reusable plotting helpers.
* [`guides/testing.md`](guides/testing.md) — what we test, how, and why no mocks.

## File map

| File | Subdir | Purpose |
|---|---|---|
| [`reference/architecture.md`](reference/architecture.md) | reference | Two-layer / two-track architecture, file-layout map |
| [`reference/math_reference.md`](reference/math_reference.md) | reference | Glossary of formal objects (PMFs, marginals, KL, TC, free energies, geometry) |
| [`reference/lean_reference.md`](reference/lean_reference.md) | reference | Per-theorem status table + sorry inventory |
| [`reference/python_api.md`](reference/python_api.md) | reference | Per-function signatures, contracts, examples |
| [`reference/manuscript_map.md`](reference/manuscript_map.md) | reference | Section-by-section map: manuscript ↔ Lean ↔ Python ↔ tests ↔ docs |
| [`guides/build_run.md`](guides/build_run.md) | guides | Compile, test, render, generate figures |
| [`guides/quickstart_recipes.md`](guides/quickstart_recipes.md) | guides | Copy-paste recipes for every common task |
| [`guides/testing.md`](guides/testing.md) | guides | No-mocks policy, coverage targets, invariants checked |
| [`modules/decomposition_theorem.md`](modules/decomposition_theorem.md) | modules | Statement, proof scaffold, and numerical checks for Theorem 4.1 |
| [`modules/information_geometry.md`](modules/information_geometry.md) | modules | Dual-flat geometry of the entanglement manifold |
| [`modules/spectral_structure.md`](modules/spectral_structure.md) | modules | Schmidt rank, archetypes, tensor-train ranks |
| [`modules/heterogeneous_ensembles.md`](modules/heterogeneous_ensembles.md) | modules | Theorem 8.1 — O(λ²) coupling-tax envelope |
| [`modules/bernoulli_toy.md`](modules/bernoulli_toy.md) | modules | K=2 Ising worked example, closed-form MI |
| [`simulation/pomdp_simulation.md`](simulation/pomdp_simulation.md) | simulation | pymdp 1.0.1 harness architecture + API |
| [`simulation/visualizations.md`](simulation/visualizations.md) | simulation | Reusable plotting helpers |

## Conventions

* **Cross-references** use relative links (`../lean/...`, `../src/...`,
  `../manuscript/...`).  Inside `docs/<subdir>/foo.md` the project
  root is two levels up: `../../lean/`, `../../src/`, etc.
* **Math notation** matches the manuscript (`λ`, `q^k`, `D_KL`).
* **Theorem labels** match the manuscript section number, not internal
  Lean naming, where the two diverge.
