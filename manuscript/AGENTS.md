# AGENTS.md — `manuscript/`

## Authoring rules

1. **One topic per file.**  Don't merge sections; the file boundary is
   the section boundary.  Break a section in two only if the manuscript
   itself does.
2. **Lexical order = render order.**  Files are concatenated in
   `os.listdir`-sorted order.  Numeric prefixes (`00_`, `01_`, …,
   `S01_`, …, `99_`) keep this stable.
3. **Cross-reference Lean.**  When stating a numbered theorem, link
   the file under
   [`../lean/ActinfPolicyEntanglement/`](../lean/ActinfPolicyEntanglement/)
   and name the Lean theorem (e.g. `entanglement_decomposition`).
4. **Cross-reference figures.**  Use relative paths to
   `../output/figures/<name>.png` so the rendered PDF picks them up
   from the same directory the pipeline collects.
5. **Avoid free-floating numbers.**  Numbers in prose should be
   either (a) defined symbols (e.g. `K`, `λ`), (b) rendered from
   `output/data/manuscript_variables.json`, or (c) sourced from a
   reproducible script.  Don't paste from notebooks.
6. **Math conventions.**
   * Natural log unless explicitly stated.
   * Joint distributions use `q(π¹, …, π^K)`; marginals use `q^k`.
   * Coupling parameter is `λ` (italic, lowercase).
   * KL divergence is `D_KL(p ‖ q)` (LaTeX `\KL{p}{q}` if you load
     [`preamble.md`](preamble.md)).
7. **References.**  Add new citations to
   [`99_bibliography.md`](99_bibliography.md); use `(Author Year)` in the
   prose, not numeric `[1]` markers.

## Adding a section

1. Pick a free numeric prefix (e.g. inserting `04a_` between `04_` and
   `05_`).  If the new content is a peer of the existing sections,
   bump the existing numbers — careful, this changes filenames.
2. Add the new file to the table in [`README.md`](README.md).
3. Run `./run.sh --project actinf_policy_entanglement_lean --pipeline`
   from the template root and inspect the PDF.

## Translating prose ⇄ Lean / Python

Whenever you state or refine a theorem in prose, the parallel changes
should be:

* Lean: edit
  [`../lean/ActinfPolicyEntanglement/<Module>.lean`](../lean/ActinfPolicyEntanglement/),
  ensure `lake build` stays green.
* Python: edit [`../src/<module>.py`](../src/), add or update tests in
  [`../tests/test_<module>.py`](../tests/), keep coverage ≥ 90%.
* Docs: update the relevant page under [`../docs/`](../docs/).

## Style sheet (terse)

* British or American spelling — pick one per file, don't mix.
* Equations with their own line use `$$ ... $$` (display); inline use
  `$...$`.
* Use `**bold**` for theorem statements and `*italic*` for new term
  introductions.
* Keep paragraphs ≤ 6 sentences.  Long tables go in appendices.
