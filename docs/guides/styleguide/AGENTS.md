# AGENTS.md - `docs/guides/styleguide/`

This directory defines the manuscript and documentation style contract.
When editing it, keep the fragments specific, enforceable, and aligned
with the validators.

Authoring rules:

1. Put cross-cutting overview material in
   [`../styleguide.md`](../styleguide.md); put detailed rules in the
   topical fragment that owns them.
2. Use American English except inside exact citation titles, schema
   fields, and stable code identifiers.
3. Do not add hand-maintained live counts. Point to
   `output/data/manuscript_variables.json`,
   `output/reports/test_results.json`, or
   `output/reports/release_readiness.json` instead.
4. If a rule is intended to be blocking, make sure there is a validator
   or test that enforces it, or name the missing guardrail explicitly.
5. Keep examples tokenized with `[[VAR:...]]`, `[[SECREF:...]]`,
   `[[THMREF:...]]`, `[[FIGREF:...]]`, and `[[EQREF:...]]` where they
   represent manuscript-facing prose.
