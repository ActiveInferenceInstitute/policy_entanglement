# Bibliography {-}

This bibliography is *auto-generated* from
[`manuscript/refs/citations.yaml`](refs/citations.yaml) by
`scripts/inject_manuscript_variables.py` — every Pandoc-style citation
in the body (a citekey enclosed in square brackets prefixed with `@`)
resolves to one entry below, and every entry below is grouped by
topic in the order specified by the `topic_order:` list of the YAML
source.

When you add a body citation:

1. Add an entry to [`refs/citations.yaml`](refs/citations.yaml) with
   the citekey, full author / year / title / venue, and a `topic:`.
2. Reference it from any body section as a Pandoc-style key — a
   lower-case `lastname-yyyy` slug enclosed in square brackets and
   prefixed with the at-sign; use a semicolon to separate
   multi-references inside a single bracket.
3. Re-run `uv run python scripts/inject_manuscript_variables.py` and
   confirm `output/manuscript/99_bibliography.md` contains
   the expanded entry.

[[CITELIST:all]]
