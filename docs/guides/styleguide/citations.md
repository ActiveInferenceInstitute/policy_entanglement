# §5 — Citations: end-to-end resolution

Back to the styleguide hub: [`../styleguide.md`](../styleguide.md).

## The registry

Every citation lives in
[`manuscript/refs/citations.yaml`](../../../manuscript/refs/citations.yaml)
keyed by a slug.  Do not hard-code current citation counts in docs:
the live registry totals and topic roll-ups are generated from
`citations.yaml` by
[`scripts/manuscript_variables.py`](../../../scripts/manuscript_variables.py)
into
[`output/data/manuscript_variables.json`](../../../output/data/manuscript_variables.json)
and checked by
[`scripts/validate_manuscript.py`](../../../scripts/validate_manuscript.py).
The active bibliography topics are declared in the same YAML under
`topic_order:` and `topic_titles:`.

### Slug convention (round-1+2)

Slugs follow `lastname-year` lowercased (Pandoc-style).  When two
entries collide, append `-a`, `-b`, …  (e.g. `friston-2024-a`,
`friston-2024-b`).  The slug-vs-year boundary is locked: the
**slug** is the stable identifier in `[@key]`; the **year** is
duplicated into the body of the YAML entry so renaming a slug never
silently changes the rendered date.  Both fields are validated by
`scripts/validate_manuscript.py`.

```yaml
heins-2022:
  authors: "C. Heins, B. Millidge, D. Demekas, …"
  year: 2022
  title: "pymdp: A Python library for active inference …"
  venue: "Journal of Open Source Software"
  doi: "10.21105/joss.04098"
  url: "https://joss.theoj.org/papers/10.21105/joss.04098"
  topic: "active_inference"
```

## Inline + multi-citation tokens

* `[@heins-2022]` → `(Heins 2022)` inline.
* `[@heins-2022; @harris-2020]` → `(Heins 2022; Harris 2020)` —
  Pandoc-style multi-citation with semicolons inside one bracket.
* The validator iterates every `@key` inside *every* multi-citation
  body and reports each missing key individually.

## Topic-grouped bibliographies

`[[CITELIST:topic]]` emits a Markdown bullet list of every citation
whose `topic:` matches `topic`.  The active topics are declared in
the same YAML under `topic_order:` and `topic_titles:` so the
bibliography section ([`99_bibliography.md`](../../../manuscript/99_bibliography.md))
can render them in a stable order.  See
[`src/manuscript/bibliography.py`](../../../src/manuscript/bibliography.py).

The round-1+2 topic extensions add `control_rl` ("Control / RL as
probabilistic inference") and `markov_blanket` ("Markov blankets and
particular physics") to support citations attached to the new
`Convexity.lean` / `MarkovBlanket.lean` discussions and the
control-as-inference connection sections.  Both topics participate in
`topic_order` / `topic_titles` so `99_bibliography.md` picks them up
without any code change.

## Validator checks

[`scripts/validate_manuscript.py`](../../../scripts/validate_manuscript.py)
fails if:

* any `[@key]` in any section file lacks an entry in
  `citations.yaml`;
* any `[[CITELIST:topic]]` references an unknown topic;
* any citation is malformed (missing `authors` / `year` / `title` /
  `venue`).

## Adding a new citation

1. Append the entry to `citations.yaml` under the right `topic:`.
2. Reference it inline with `[@my-key]`.
3. (Optional) re-render and rebuild
   `99_bibliography.md` if you added a new topic.
4. `uv run python scripts/validate_manuscript.py` to confirm.
