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
| `tag` | `v5.0.3` |
| `commit` | `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1` |
| `recorded` | `2026-11-12` |
| `parser_module` / `parser_class` | `gnn.parsers.markdown_parser` / `MarkdownGNNParser` |

The GNN-FEP contract requires the upstream `gnn.importers` reader instead of
the local `src/gnn/upstream.py::load_upstream_pin` copy. The arm now invokes
the contract checker with `--require-pointer --workflow .github/workflows/ci.yml
--job gnn-conformance`, against source extracted from the pinned commit.
It never substitutes the checkout's newer working tree.

**Migration blocked:** the pinned release does not contain `gnn/importers.py`.
The checker therefore fails at module import. The local bootstrap pin reader
and its tests remain until a reviewed upstream release/pin decision makes the
shared reader available; this is not a completed single-reader migration.
No pin or schema is changed here.

## What the job parses

The arm provisions a per-pin cache directory outside the working tree
(`$XDG_CACHE_HOME/policy_entanglement/gnn-upstream/<tag>-<commit>/`, or
`$GATE_CACHE_DIR`), fails if the `v5.0.3` tag no longer resolves to the pinned
commit, and gives that checkout its own interpreter with the parser's runtime
dependencies (`numpy`, `defusedxml`, `psutil`).

`POLICY_ENTANGLEMENT_GNN_ROOT` is validated read-only instead: the named
checkout (often another repository's clone or mirror) must already contain the
pinned commit, any existing tag must still peel to it, and its `.venv` must
already import the parser's dependencies. The arm performs no `git init`,
fetch, checkout, `remote set-url`, or install there; a missing piece is an
explicit refusal, not a repair. `tests/test_gate_gnn_root.py` proves HEAD,
refs, origin, local config and the working tree are unchanged.

The arm runs the shared contract checker first, then retains the independent
digest-conformance check even if the contract checker fails:
`python -m pytest -q tests/test_gnn_upstream_conformance.py`, which:

- extracts `src/gnn` from the pinned commit with `git archive` so the bytes
  under test are the pinned release's bytes, not the checkout's working tree;
- checks the executed parser's SHA-256 against the pinned blob;
- parses the three specs [`../gnn/bernoulli_toy.gnn.md`](../gnn/bernoulli_toy.gnn.md),
  [`../gnn/k_stream_ensemble.gnn.md`](../gnn/k_stream_ensemble.gnn.md) and
  [`../gnn/production_ensemble.gnn.md`](../gnn/production_ensemble.gnn.md) with
  the pinned `MarkdownGNNParser`, requiring no errors or warnings;
- compares normalized digests field by field with the project-owned parser in
  `src/gnn/parser.py`, with a spaced-heading mutant proving the comparison is
  not vacuous.

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
