# `manuscript/refs/` — registry directory

Single source of truth for every figure, equation, and citation
referenced from the manuscript body.  The auto-injection pipeline at
[`scripts/inject_manuscript_variables.py`](../../scripts/inject_manuscript_variables.py)
reads these YAMLs together with
[`output/data/manuscript_variables.json`](../../output/data/manuscript_variables.json)
and resolves every `[[FIG:...]]`, `[[FIGREF:...]]`, `[[EQ:...]]`,
`[[EQREF:...]]`, `[[VAR:...]]`, `[[CITELIST:topic]]`, and `[@key]`
token in the source.  Output lands at
[`output/manuscript_rendered/`](../../output/manuscript_rendered/).

## Files

* [`labels.yaml`](labels.yaml) — figure, equation, **section** and
  **theorem** registry.
  * `figures:` — `path`, `caption`, `short`, `sections`, `source`.
    Numbers derived from YAML insertion order.
  * `equations:` — `latex`, `name`, `sections`.  Numbers derived
    from YAML insertion order.
  * `sections:` — `number`, `title`, optional `file`, optional
    `parent` (for subsections).  The `parent` field links a `§N.M`
    subsection to its top-level `§N`.
  * `theorems:` — `kind` ("Theorem", "Proposition", "Corollary",
    "Lemma", "Definition"), `number` (e.g. "4.1"), optional `name`,
    `section` (the section in which the theorem is stated).
* [`citations.yaml`](citations.yaml) — citation registry.  Each entry
  is keyed by a Pandoc-style `lastname-yyyy[-letter]` slug and carries
  `authors`, `year`, `title`, `venue`, optionally `volume`, `pages`,
  `doi`, `url`, `note`, plus a required `topic` for grouping.

## Adding a figure

1. Add it under `figures:` in [`labels.yaml`](labels.yaml).  Pick a
   short snake_case `label`.
2. Reference it from the body as `[[FIG:label]]` (full block) or
   `[[FIGREF:label]]` (inline cross-reference).
3. Make sure the PNG actually lives at the registered `path` after
   running `uv run python scripts/generate_figures.py` (or
   `simulate_pymdp.py`).

## Adding a section reference

* All section numbers are encoded by *labels*, never typed inline.
* In body prose write `[[SECREF:phase.diagram]]` to render `§9.1`,
  or `[[SEC:phase.diagram]]` to render the full `§9.1 Phase diagram`
  (used in headings of the rendered output).
* The `validate_manuscript.py` validator forbids hard-coded `§N` /
  `§N.M` strings in body prose — the only acceptable sites are
  Markdown headings, fenced code, inline code, and the bold theorem
  block label.

## Adding a theorem reference

* Every numbered theorem / proposition / corollary / lemma is registered
  under `theorems:` in [`labels.yaml`](labels.yaml).
* In body prose write `[[THMREF:thm_4_1]]` to render the inline label
  `Theorem 4.1`, or `[[THM:thm_4_1]]` to render the *full bold block*
  `**Theorem 4.1 (Entanglement Decomposition).**` that opens the
  statement.
* As with sections, hard-coded `Theorem N.M` / `Prop N.M` / `Cor N.M`
  references in body prose are forbidden by the validator.

## Adding an equation

1. Add it under `equations:` in [`labels.yaml`](labels.yaml).
2. Reference as `[[EQ:label]]` (display block) or `[[EQREF:label]]`
   (inline).

## Adding a citation

1. Add it to [`citations.yaml`](citations.yaml) using the
   `lastname-yyyy` key convention.
2. Reference it from the body as `[@key]` (or `[@k1; @k2]` for a
   multi-citation).
3. The bibliography section is auto-rendered from the
   `[[CITELIST:all]]` directive in
   [`../99_bibliography.md`](../99_bibliography.md).

## Validation

The contract that every token in the manuscript has a corresponding
registry entry is enforced by
[`scripts/validate_manuscript.py`](../../scripts/validate_manuscript.py),
which runs as the final gate of `scripts/run_all.py`.
