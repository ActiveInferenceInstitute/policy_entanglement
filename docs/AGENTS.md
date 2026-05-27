# AGENTS.md — `docs/`

**Publication:** DOI https://doi.org/10.5281/zenodo.20418904 · source https://github.com/ActiveInferenceInstitute/policy_entanglement · claim matrix [`_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv`](_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv) · cross-track source [`../manuscript/refs/audit_tracks.yaml`](../manuscript/refs/audit_tracks.yaml) · generator [`../scripts/generate_audit_matrix.py`](../scripts/generate_audit_matrix.py) (`--write` / `--check`)

## Purpose

`docs/` holds the project's technical reference.  It is *not* the
manuscript (that lives in [`../manuscript/`](../manuscript/)) and *not*
per-directory READMEs (those live at the directory roots).  Rather,
`docs/` is the place for cross-cutting explanation: how the project
fits together, what theorems mean, how to refine Lean proofs.

## Current ground truth

Do not maintain live status numbers in this file. Any agent picking up
work in `docs/` must reconcile edits against the generated reports:

| Question | Authoritative source |
|---|---|
| Lean build, hygiene, declaration counts, theorem-registry roll-ups | `scripts/build_lean.py`, `output/data/manuscript_variables.json`, and `docs/reference/_theorem_map.md` |
| Test collection, pass/skip split, and coverage | `output/reports/test_results.json` |
| Figures, rendered manuscript artifacts, PDF summary, MathlibProofs status, and runtime budget | `output/reports/release_readiness.json` and `output/MANIFEST.md` |
| Round-by-round history and retired display numbers | `docs/CHANGELOG.md` and explicitly historical audit tables |

Historical count movement may remain in `CHANGELOG.md` or in a table
explicitly labeled as revision history. Current-facing docs should use
live-report pointers, theorem labels such as `thm_4_1`, and descriptive
names such as "the decomposition theorem" rather than hand-written
display numbers.

**Sign conventions:** §S6 carries a new "Sign conventions" subsection
registered as `notation.sign_conventions`.  Cite it from any new
docs page that introduces a free-energy or log-weight sign.

**Round-1 + round-2 citation additions (treat as canonical for new docs):**

`levine-2018`, `oseledets-2011`, `ay-jost-le-schwachhofer-2017`,
`schollwock-2011`, `fountas-2020`, `hafner-2023`, `sajid-2021`,
`toussaint-2009`, `botvinick-toussaint-2012`, `lanillos-2021`,
`degenne-2025`, `li-turner-2016`, `fu-smith-panagiotelis-2025`,
`devries-2025`, `nuijten-lukashchuk-2025`, `champion-2024-reframing`,
`friston-rgm-2025`, `albarracin-2024`, `waade-2025` (renamed from
`tomljenovic`), `ruiz-serra-2025`, `aguilera-2021`, `friston-2024-federated`,
`smithe-2024-structured`, `brownian-lean-2025`.  The 2026-05-21
scholarship pass added verified structured-VI / agency anchors:
`dacosta-2024-agency`, `saul-jordan-1995`, and
`wainwright-jordan-2008`.

**Round-2 invariant pin tests:** 10 round-2 tests pin round-1 / round-2
invariants (declaration counts, witness theorem identities, citation
registry size, run-all script count, sign-conventions subsection
presence).  **Round-3** added **35 further tests** (now part of
the full test suite pinning the new round-3 invariants: multi-K experiment
results, long-horizon steady-state convergence, revertibility KL
identity, the four new witness theorems, the two new submodule
existence checks, and the 47 dashboard invariants.

## Authoring rules

1. **Topic-per-file.**  One file = one cohesive topic.  Don't
   merge.
2. **Cross-link liberally.**  Connect each docs page to the relevant
   manuscript section, Lean module, and Python module.
3. **Stay current.**  When you change `lean/` or `src/` semantics,
   update the matching docs page in the same commit. When status
   changes, update the producer or generated-report wiring rather than
   adding hand-maintained counts to this file.
4. **Examples are runnable.**  Every code block under "Quick example"
   must execute as-is from the project root.
5. **Don't duplicate the manuscript.**  When in doubt, link to the
   manuscript section rather than copying the prose.
6. **Honor the styleguide contract.**  Before authoring or reviewing
   manuscript prose, figure captions, equations, or citations, read
   [`guides/styleguide.md`](guides/styleguide.md).  Hardcoded numbers
   in `manuscript/*.md`, raw `\tag{...}` in display math, missing
   `[[FIG:label]]` registrations, or unresolved `[@citekey]` are CI
   failures by design.
7. **Use American English.**  Documentation prose follows
   [`guides/styleguide/prose.md`](guides/styleguide/prose.md): American
   spelling, evidence-first claims, exact citation titles preserved,
   and historical code identifiers left stable.
8. **Prefer live-derived values.**  When a doc needs to cite the Lean
   declaration count, the run-all script count, or the bibliography
   size, link to the variable in
   `output/data/manuscript_variables.json` rather than hard-coding the
   number — `scripts/run_all.py` re-derives these every run.

## When to add a new page

Add a new file under `docs/` when:

* A new module / theorem family is introduced that doesn't fit any
  existing page (the round-2 `Convexity` and `MarkovBlanket` modules
  are the canonical example — each got its own page).
* You want to explain a recurring engineering decision (e.g. the
  Mathlib-free pivot, the binder-token rename, the
  `lean_inductive_count` → `lean_structure_count` rename).
* A future agent will want a single landing-page for a workflow
  (build, test, refine).

## When *not* to add a new page

* Small clarifications belong in the relevant directory's `README.md`,
  not a new docs page.
* Per-test or per-function notes belong in the docstring, not docs.
* User-facing how-tos belong in the project root [`../README.md`](../README.md).

## Required maintenance

When closing a Mathlib-refinement witness payload (i.e. moving a
`witness` row to `proved`):

1. Update the row in [`reference/lean_reference.md`](reference/lean_reference.md).
2. Flip the `status:` in `manuscript/refs/labels.yaml::theorems`
   (this is what auto-injects into the §12 status table).
3. If the proof relies on a new Mathlib lemma, mention it in
   [`guides/build_run.md`](guides/build_run.md) under "Mathlib dependencies".
4. Update [`guides/testing.md`](guides/testing.md) if the corresponding Python
   sanity test changes.
5. Re-run `scripts/run_all.py` and verify that
   `lean_total_declarations`, `lean_structure_count`, and the lake-job
   count in `output/data/manuscript_variables.json` move in the
   direction you expect.

When the witness rows move toward `proved` through a separate
MathlibProofs discharge (see
[`../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)),
update the generated theorem-map producer, README honesty prose, and
live-report wiring. Do not add new status counts to this file.
