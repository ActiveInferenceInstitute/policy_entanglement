# `.github/workflows/`

[`ci.yml`](ci.yml) runs on pushes and pull requests to `main`, with
`concurrency` cancelling a superseded run on the same ref. Every step is a
[`scripts/gate.py`](../../scripts/gate.py) arm, so the workflow and the local
`make` targets run one definition of each command; [`../GNN.md`](../GNN.md)
documents the conformance job and its pin, and
[`../../docs/guides/gate.md`](../../docs/guides/gate.md) is the arm-by-arm
run guide.

| Job | Steps (gate arms) |
|---|---|
| `ci` — "Pipeline gates, lint, and Lean budget" | `uv sync --frozen --group sim`, then `python scripts/gate.py lint`, `format`, `types`, `pipeline`. `pipeline` is `scripts/run_all.py` (Lean boundary build + hygiene budget, artifact generation, manuscript validation, regression gate). Timeout 180 minutes. |
| `gnn-conformance` — "gnn conformance (pinned)" | `uv sync --frozen` (default groups only), then `python scripts/gate.py gnn`, which fetches the commit pinned in [`../../gnn/upstream.json`](../../gnn/upstream.json), refuses a moved tag, and runs `tests/test_gnn_upstream_conformance.py`. Timeout 30 minutes. |

The pipeline arm's regression gate runs pytest with `-m "not slow"`; the
`slow`-marked release probes (the Lean toolchain build test and the
MathlibProofs axiom audit) are opt-in through `python scripts/gate.py slow`
(`make slow`), and the release path adds them through
`python scripts/gate.py pipeline-release`.

`uv` is installed with `astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2`
(v10.3.3). The workflow does not use the estate composite action
`ActiveInferenceInstitute/.github/.github/actions/setup-python-uv`.
