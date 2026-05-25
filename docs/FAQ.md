# FAQ — Policy Entanglement project

Answers to the questions a newcomer is most likely to ask after
glancing at the repository.  Each answer points to the authoritative
docs page or source file for further reading.

*Latest generated audit.*

---

## 1.  What is this project?

A Lean-4-formalized + Python-grounded study of **policy entanglement**
in active inference: a one-parameter (λ) deformation of mean-field
posteriors that interpolates between independent per-stream control
(λ = 0, mean-field) and tightly-coupled archetypal regimes (λ → ∞).

The **load-bearing identity** is the entanglement decomposition theorem
— see
[`modules/decomposition_theorem.md`](modules/decomposition_theorem.md):

$$
F[q_\lambda] \;=\; \sum_k F[q^k_\lambda] \;+\; \gamma\,\lambda\,\mathbb{E}_{q_\lambda}[K_c] \;+\; \log Z_E(\lambda) \;-\; \lambda\,\mathbb{E}_{q_\lambda}[J] \;+\; I(q_\lambda).
$$

The variational free energy decomposes cleanly into a marginal piece,
a coupling cost, a coupling-prior partition surplus, and a
multi-information penalty.

When the docs say the framework relates to existing active-inference
variants, read the relationship class literally.  Mean-field discrete
AIF is the exact `λ = 0` anchor.  Factor-graph / RxInfer-style
message passing is a parametric implementation route; the inserted
policy-coupling factor has exact semantics only inside the specified
graph.  Hierarchical / deep temporal AIF,
sophisticated inference, branching-time AIF, RGM, and policy-space
Markov blankets are structural analogies unless their extra temporal,
recursive, or state-space machinery is explicitly supplied.

For full orientation, start at
[`README.md`](README.md) and follow the reading order at
[`READING_ORDER.md`](READING_ORDER.md).

---

## 2.  Where is the manuscript?

In [`../manuscript/`](../manuscript/) — modular Markdown. The
rendered PDF lives under [`../output/pdf/`](../output/pdf/) after
running the template render pipeline. Live render counts, figure
counts, page counts, and file sizes come from
[`../output/reports/release_readiness.json`](../output/reports/release_readiness.json)
and [`../output/MANIFEST.md`](../output/MANIFEST.md), not from
hand-maintained FAQ prose.

The single source of truth for figures, equations, theorems, and
section labels is
[`manuscript/refs/labels.yaml`](../manuscript/refs/labels.yaml); for
citations,
[`manuscript/refs/citations.yaml`](../manuscript/refs/citations.yaml).

---

## 3.  How do I build and run everything?

The canonical one-command answer is:

```bash
uv run python scripts/run_all.py
```

This runs the canonical `scripts/run_all.py` pipeline in order (Lean budget → analytical
figures → variables JSON → archetypes / sweeps → pymdp → round-3
sims → robustness expansion → dashboard → registry indices → manuscript injection →
validation gates → regression gate).

For piecewise execution, see
[`guides/build_run.md`](guides/build_run.md).  For copy-paste
recipes, see
[`guides/quickstart_recipes.md`](guides/quickstart_recipes.md).

---

## 4.  Why are there 0 Mathlib imports?

By choice.  The Lean 4 boundary fragment ships with **0 strict
`sorry`, 0 axioms, 0 unsafe/partial/noncomputable, 0 Mathlib
imports**, on stock Lean v4.29.0.

This is achieved by stating analytic content (KL chain rule,
real-analytic continuity, matrix SVD, tensor-train rank envelopes,
measure tightness) as **witness-consuming theorems**: each theorem
takes a `structure`-packaged hypothesis (e.g. `BoundedQuadraticTax`,
`UpperSemicontinuousRankWitness`) and certifies it without
`import Mathlib`.  See
[`reference/lean_reference.md`](reference/lean_reference.md) for the
per-theorem table.

The Mathlib refinement that discharges the witness *payloads* is
documented in
[`../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).
The separate [`../lean/MathlibProofs/`](../lean/MathlibProofs/) package
now machine-checks the **headline Theorem 5.1** — the full S01 boxed
free-energy identity — in $\mathbb{R}$, via
`MathlibProofs.free_energy_decomposition_full` (updated 2026-05-19,
post-Pass-11).  Axiom-clean under foundational-only `#print axioms`,
two independent negative controls, enforced via
`scripts/build_mathlib_proofs.py` and the automatic pytest gate
`tests/test_mathlib_axiom_audit.py`.  The Float boundary fragment is
the typed numerical shadow with a per-row faithfulness ledger
(`docs/reference/veridical_status.md`).  Single open residual: a
*verified* error-bounded Float$\leftrightarrow\mathbb{R}$ bridge,
scoped in `docs/reference/methods_and_assumptions.md`.

---

## 5.  What does "witness form" mean?

A *witness-form* theorem certifies an existence claim by extracting
fields from a caller-supplied `structure`.  Example: Theorem 9.1
(coupling-tax `O(λ²)` envelope) is stated as

```lean
theorem couplingTax_quadratic_bound … (witness : BoundedQuadraticTax …) :
    ∀ λ, tax λ ≤ witness.C * λ^2 * ‖K_c‖^2 :=
  fun λ => witness.bound λ
```

The analytic *content* (Bregman Taylor expansion) lives in
`witness.bound`, supplied by the caller — typically a separate MathlibProofs
refinement library, today a Python numerical witness verified at
floating tolerance.  The boundary fragment certifies that *if* the
witness exists, *then* the manuscript theorem follows.

See
[`reference/four_track_coherence.md`](reference/four_track_coherence.md)
for the full contract.

---

## 6.  What is "no-mocks policy"?

Every Python test in this project uses **real numerical examples**:
no `MagicMock`, no `mocker.patch`, no `unittest.mock`.  Tests of
HTTP fixtures use `pytest-httpserver`; tests of PDF generation use
`reportlab`; tests of file I/O use real temporary files via
`tmp_path`.

The reasons:

1. Numerical claims need numerical verification.  Mocks give the
   answer you wanted, not the answer the math gives.
2. The Lean side ships only the *boundary* of each theorem; the
   Python test suite is the *sanity rail* that catches arithmetic
   drift while Mathlib proofs land.
3. Reproducibility under fixed seeds is easier to debug than
   behavior-behind-a-mock.

See [`guides/testing.md`](guides/testing.md) for the catalog of
tested properties.

---

## 7.  What changed in round 3?

Round 3 closed every remaining `deferred` theorem.  See
[`CHANGELOG.md`](CHANGELOG.md) for the full per-round history.

In one paragraph: round 3 added two new Lean submodules
(`SpectralWitnesses.lean`, `ConnectionsWitnesses.lean`) — each
shipping two witness-form theorems plus their `structure`s — and
three empirical experiments (`simulate_multi_k.py`,
`simulate_long_horizon.py`, `simulate_revertibility.py`). For the
per-round count deltas, use [`CHANGELOG.md`](CHANGELOG.md); for current
pipeline, test, figure, and theorem-registry state, use
[`../output/reports/release_readiness.json`](../output/reports/release_readiness.json),
[`../output/reports/test_results.json`](../output/reports/test_results.json),
and [`reference/_theorem_map.md`](reference/_theorem_map.md).

---

## 8.  Where is the Python ↔ Lean ↔ manuscript ↔ test mapping?

The authoritative per-section table is
[`reference/manuscript_map.md`](reference/manuscript_map.md).  The
auto-generated per-theorem table is
[`reference/_theorem_map.md`](reference/_theorem_map.md) (do **not**
hand-edit; rerun
[`../scripts/generate_theorem_map.py`](../scripts/generate_theorem_map.py)).

The CI gate `validate_lean_wiring` (inside
[`../scripts/validate_manuscript.py`](../scripts/validate_manuscript.py))
enforces that every registry theorem with a populated `lean_module`
field resolves to a real Lean declaration on disk.

---

## 9.  Where is the manuscript ↔ code style contract?

[`guides/styleguide.md`](guides/styleguide.md) — six hard
requirements:

1. **Real, configurable simulations.**  Every grid / seed / horizon
   reads from
   [`../src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py).
2. **Auto-injected variables.**  Every numeric in prose comes from
   `output/data/manuscript_variables.json` via `[[VAR:key]]`.
3. **Auto-numbered equations.**  Display math gets `S.K` tags from the
   registry.
4. **Method-anchored figures.**  Every figure caption names its
   generation method (function path + grid hyperparameter).
5. **Resolved citations.**  Every `[@key]` resolves through
   `citations.yaml`.

Each rule has its own detail page under
[`guides/styleguide/`](guides/styleguide/).

---

## 10.  How do I add a new theorem, figure, or citation?

* **New theorem.**  Five-step recipe in
  [`reference/four_track_coherence.md`](reference/four_track_coherence.md)
  ("Adding a new theorem (or witness)") — add Python helper + test,
  state the theorem in Lean (witness form if Mathlib-dependent),
  register in `labels.yaml::theorems`, reference in prose, validate.
* **New figure.**  Recipe in
  [`guides/styleguide/figures.md`](guides/styleguide/figures.md) —
  add `figure_*` function to
  [`../scripts/generate_figures.py`](../scripts/generate_figures.py),
  register in `labels.yaml::figures`, reference with `[[FIG:label]]`.
* **New citation.**  Recipe in
  [`guides/styleguide/citations.md`](guides/styleguide/citations.md)
  — append the entry to
  [`../manuscript/refs/citations.yaml`](../manuscript/refs/citations.yaml)
  under its `topic`, cite inline with `[@my-key]`.

---

## 11.  Why is the dependency surface so small?

Three reasons:

1. **Reproducibility.**  Every claim that lives in prose has a
   numerical witness in `src/` + a tested invariant in `tests/`.
   Reducing the dependency surface reduces the number of moving
   parts that can drift.
2. **Lean hygiene.**  The boundary fragment depends on stock Lean
   v4.29.0 + nothing else.  Mathlib is a deliberate non-dependency.
3. **Pipeline runtime.**  The full `run_all.py` walks the live `SCRIPTS` table
   in tens of seconds on a stock laptop because each stage is a thin
   Python orchestrator over numpy.

The only optional deps are the `sim` group (pymdp + JAX, for the
POMDP harness) and the `viz` group (seaborn / networkx / plotly, for
extras like the coupling-potential graph).  See
[`guides/build_run.md`](guides/build_run.md).

---

## 12.  What hardware do I need?

A stock laptop is enough.  The full pipeline is CPU-only by default
(JAX falls back to CPU automatically; we use FPI inference, not VI,
so there is no SGD loop).  Approximate end-to-end runtime on
Apple-silicon: 20–40 s for `scripts/run_all.py`; about a minute for
the local PDF render on top of that.

No GPU.  No cluster.  Determinism is enforced through seeds set inside
each script (`PYMDP_ROLLOUT_SEED = 0`, `FIGURE_GLOBAL_SEED = 42`,
etc.).

---

## 13.  Where do I file an issue?

This project lives inside the `template` monorepo at
[`docxology/template`](https://github.com/docxology/template).  The
infrastructure (the `Layer 1` directories — `infrastructure/`,
`scripts/00_*` through `scripts/07_*`, `tests/infra_tests/`) is
shared with other projects under `projects/`.  Project-specific
issues belong under `projects/actinf_policy_entanglement_lean/`;
template-wide issues belong at the repository root.

---

## 14.  What is the relation to `fep_lean`?

This project's Lean boundary fragment is **re-exported** to the
`fep_lean` catalog layout via
[`../lean/FepSketches/PolicyEntanglementBoundary.lean`](../lean/FepSketches/PolicyEntanglementBoundary.lean).
The re-export is a thin `export` shim — it adds zero theorems and
zero structures, but lets downstream `fep_lean` consumers
`import FepSketches.PolicyEntanglementBoundary` and get the entire
boundary fragment by transitive re-export.  It is part of the current
22-job Lake build; the generated `lean_lake_jobs_total` variable is the
source of truth when the package graph changes.

---

## 15.  Where do I go from here?

* [`README.md`](README.md) — top-level orientation.
* [`READING_ORDER.md`](READING_ORDER.md) — curated paths by persona.
* [`CHANGELOG.md`](CHANGELOG.md) — round-by-round history.
* [`glossary.md`](glossary.md) — project-jargon glossary (boundary
  fragment, witness-form, four-track contract, …).
* [`reference/architecture.md`](reference/architecture.md) — two-layer
  / two-track design.
* [`reference/manuscript_map.md`](reference/manuscript_map.md) — the
  master cross-reference.
* [`reference/invariants_reference.md`](reference/invariants_reference.md)
  — the 47 dashboard invariants by family and witness builder.
* [`reference/veridical_status.md`](reference/veridical_status.md) —
  the live audit page that the CI gates produce.

---

## 16.  What is S08 / GNN?

Supplement §S8 introduces **Generalized Notation Notation (GNN)** —
per Smékal & Friedman (2023, Zenodo `10.5281/zenodo.7803328`) and the
upstream repo [`ActiveInferenceInstitute/GeneralizedNotationNotation`](https://github.com/ActiveInferenceInstitute/GeneralizedNotationNotation)
— as a shipped fifth **structural-and-numerical** representation of
the framework alongside the four proof/evidence tracks (prose /
equations / Python / Lean).

The shipped bridge includes a project-owned parser, a K=2 Bernoulli
round-trip from a real `.gnn` source, a Lean typed-contract emitter,
and a `simulate_gnn.py` pipeline stage. It does **not** prove theorems,
replace the four-track proof contract, or promote any theorem row; its
open work is a first-class upstream coupling primitive, full-bundle
pymdp regeneration, and GNN-to-Lean proving. See
[`reference/four_track_coherence.md`](reference/four_track_coherence.md)
for the structural boundary.

**Acronym disambiguation.**  §20.Q8 uses the same acronym "GNN" to
refer to *graph neural networks* (the deep-learning architecture
family that could *learn* the coupling potentials end-to-end).  The
two meanings are orthogonal: Generalized Notation Notation is a
*model-description language*; graph neural networks are a
*parametric inference architecture*.  Disambiguated explicitly at
§S8.3.

For the must-NOT-include over-claims about GNN (e.g. "GNN is
verified because it parses" — false; parsing is not proving), see
the assessment ledger at
[`_audit/FOUR_SKILL_ASSESSMENT_2026-05-19.md`](_audit/FOUR_SKILL_ASSESSMENT_2026-05-19.md).
