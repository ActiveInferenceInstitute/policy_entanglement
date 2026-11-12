# GNN conformance

`gnn conformance (pinned)` is the display name of the `gnn-conformance` job in
[`workflows/ci.yml`](workflows/ci.yml). The job runs one gate arm,
`python scripts/gate.py gnn` (`make gnn` locally); that arm is the only
definition of the conformance check, so CI and a contributor run the same
command.

## The pin

The canonical pin file is [`../gnn/upstream.json`](../gnn/upstream.json), schema
`gnn-importer-pin/v1`. It records:

| Field | Value |
|---|---|
| `repository` | `https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation` |
| `tag` | `v5.1.0` |
| `commit` | `75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf` |
| `recorded` | `2026-11-12` |
| `parser_module` / `parser_class` | `gnn.parsers.markdown_parser` / `MarkdownGNNParser` |

### Adopted: the pin is read by the shared reader

The [GNN-FEP contract](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation/blob/main/docs/workflows/gnn-fep.md)
stages adoption by the pinned revision, and this pin names `v5.1.0`
(`75c834bd8519`), the release that ships `src/gnn/importers.py`. The member's
interim local reader is therefore deleted and the arm calls the shared reader
from the pinned release's own environment:

```bash
python -m gnn.importers check --repo . --require-pointer \
    --workflow .github/workflows/ci.yml --job gnn-conformance \
    --expected-commit 75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf --expected-tag v5.1.0
```

`python` is the pinned checkout's interpreter and `PYTHONPATH` is that
checkout's `src/`, so `gnn.importers` is the pinned release's module and the
specs are parsed by the pinned parser. The reader owns the pin's shape, the
pointer facts below (this file names `gnn/upstream.json`, `75c834bd8519`,
`ci.yml` and `gnn-conformance`), the fork check on `repository`, and the
`*.gnn.md` syntax check. Nothing is vendored and no newer reader is overlaid on
an older parser.

The arm reads the pin file once, only to select what to fetch, and hands the
release to the conformance test through `POLICY_ENTANGLEMENT_GNN_RELEASE`; the
test does not read the pin and keeps no copy of its shape.

**Cutover record.** `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1` (`v5.0.3`,
which predates the reader) → `75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf`
(`v5.1.0`). In the same change: `src/gnn/upstream.py::load_upstream_pin` and its
pin-shape tests were removed, `scripts/gate.py` passes the pin, pointer and spec
checks to the reader, and this pointer replaced its interim and blocked text.

## What the job parses

The arm provisions a per-pin cache directory outside the working tree
(`$XDG_CACHE_HOME/policy_entanglement/gnn-upstream/<tag>-<commit>/`, or
`$GATE_CACHE_DIR`), fails if the `v5.1.0` tag no longer resolves to the pinned
commit, and gives that checkout its own interpreter with the parser's runtime
dependencies (`numpy`, `defusedxml`, `psutil`).

`POLICY_ENTANGLEMENT_GNN_ROOT` is validated read-only instead: the named
checkout (often another repository's clone or mirror) must already contain the
pinned commit, any existing tag must still peel to it, and its `.venv` must
already import the parser's dependencies. The arm performs no `git init`,
fetch, checkout, `remote set-url`, or install there; a missing piece is an
explicit refusal, not a repair. `tests/test_gate_gnn_root.py` proves HEAD,
refs, origin, local config and the working tree are unchanged.

After the shared reader reports the pin, the pointer and the three specs, the
arm runs `python -m pytest -q tests/test_gnn_upstream_conformance.py`, which:

- extracts `src/gnn` from the pinned commit with `git archive` so the bytes
  under test are the pinned release's bytes, not the checkout's working tree;
- checks the executed parser's SHA-256 against the pinned blob;
- parses the three specs [`../gnn/bernoulli_toy.gnn.md`](../gnn/bernoulli_toy.gnn.md),
  [`../gnn/k_stream_ensemble.gnn.md`](../gnn/k_stream_ensemble.gnn.md) and
  [`../gnn/production_ensemble.gnn.md`](../gnn/production_ensemble.gnn.md) with
  the pinned `MarkdownGNNParser`, requiring no errors or warnings;
- compares normalized digests field by field with the project-owned parser in
  `src/gnn/parser.py`, with a dtype mutant (`type=bool`: project `bool`,
  upstream `binary`) proving the comparison is not vacuous. The earlier
  spaced-heading control is gone because `v5.1.0` now reads the spaced ontology
  heading that `v5.0.3` ignored.

It does not scan the rest of the repository for `*.gnn.md`.

## Workflow plumbing

The job syncs the default `uv` groups only (`uv sync --frozen`): the
conformance test needs `numpy` and the project's own `gnn` package, not the
pymdp/JAX `sim` group. The resolved pin is written to the job summary by the
arm itself (`gnn-version=… commit=…`).

The workflow installs `uv` with `astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2`
(v10.3.3, `version: "0.13.1"`, `python-version: "3.12"`). It does not use the
estate composite action `ActiveInferenceInstitute/.github/.github/actions/setup-python-uv`
in either job.
