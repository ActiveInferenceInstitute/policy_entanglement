# Prose, Language, and Evidence Style

Back to the styleguide hub: [`../styleguide.md`](../styleguide.md).

## American English

All reader-facing prose uses American English: `behavior`, `artifact`,
`modeling`, `formalization`, `factorization`, `marginalization`,
`normalization`, `color`, and `center`.  The only exceptions are:

* historical code identifiers, such as `mProjection_minimises_kl` and
  `entangled_prior_unnormalised`;
* exact citation titles and direct quotations from sources;
* external file names, schema fields, or Lean declarations that already
  exist in upstream systems and cannot be renamed locally.

The test
[`tests/test_american_english.py`](../../../tests/test_american_english.py)
scans prose-like files outside `output/` and fails on common British
spellings outside inline code spans and fenced code blocks.

## Evidence-first Writing

Methods, results, and discussion sections should show the evidence
chain.  When a paragraph makes a claim about an empirical result,
formal theorem, or reproducibility guarantee, it should name at least
one of the following:

* the source script or module that produced the result;
* the emitted CSV, JSON, PNG, or PDF artifact;
* the test that gates the claim;
* the registry token (`[[VAR:...]]`, `[[FIG:...]]`, `[[THMREF:...]]`,
  `[[LEAN:...]]`) that injects the live value or reference;
* the primary citation that anchors an external literature claim.

Interpretive prose is welcome, but it should follow the artifact rather
than substitute for it.  The evidence ledgers in
[`manuscript/4B_empirical_suite.md`](../../../manuscript/4B_empirical_suite.md)
and
[`manuscript/6C_discussion_and_outlook.md`](../../../manuscript/6C_discussion_and_outlook.md)
are the current templates.
