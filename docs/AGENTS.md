# AGENTS.md — `docs/`

## Purpose

`docs/` holds the project's technical reference.  It is *not* the
manuscript (that lives in [`../manuscript/`](../manuscript/)) and *not*
per-directory READMEs (those live at the directory roots).  Rather,
`docs/` is the place for cross-cutting explanation: how the project
fits together, what theorems mean, how to refine Lean proofs.

## Authoring rules

1. **Topic-per-file.**  One file = one cohesive topic.  Don't
   merge.
2. **Cross-link liberally.**  Connect each docs page to the relevant
   manuscript section, Lean module, and Python module.
3. **Stay current.**  When you change `lean/` or `src/` semantics,
   update the matching docs page in the same commit.
4. **Examples are runnable.**  Every code block under "Quick example"
   must execute as-is from the project root.
5. **Don't duplicate the manuscript.**  When in doubt, link to the
   manuscript section rather than copying the prose.

## When to add a new page

Add a new file under `docs/` when:

* A new module / theorem family is introduced that doesn't fit any
  existing page.
* You want to explain a recurring engineering decision (e.g. the
  Mathlib-free pivot, the binder-token rename).
* A future agent will want a single landing-page for a workflow
  (build, test, refine).

## When *not* to add a new page

* Small clarifications belong in the relevant directory's `README.md`,
  not a new docs page.
* Per-test or per-function notes belong in the docstring, not docs.
* User-facing how-tos belong in the project root [`../README.md`](../README.md).

## Required maintenance

When closing a Phase-7 sorry:
1. Update the row in [`reference/lean_reference.md`](reference/lean_reference.md).
2. If the proof relies on a new Mathlib lemma, mention it in
   [`guides/build_run.md`](guides/build_run.md) under "Mathlib dependencies".
3. Update [`guides/testing.md`](guides/testing.md) if the corresponding Python
   sanity test changes.
