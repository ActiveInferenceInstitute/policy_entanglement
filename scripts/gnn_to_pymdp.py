#!/usr/bin/env python3
r"""GNN -> pymdp config generator (the S08 ``scripts/gnn_to_pymdp.py`` deliverable).

Thin orchestrator: consumes a GNN source file and emits the structural
configuration a pymdp-style harness needs, sourced entirely from the ``.gnn``
declarations.

Two modes:

* default (policy-level, :func:`gnn.bridge.to_pymdp_config`): stream count,
  per-stream policy cardinality, per-stream habit priors, the joint coupling
  tensor, and the scalar parameters — the K=2 toy / K-stream ensemble config.
* ``--harness`` (production harness, :func:`gnn.harness.harness_config`):
  the full per-stream ``A``/``B``/``C``/``D`` factors, the joint coupling,
  ``gamma``, and control cardinalities for the production ensemble
  (``gnn/production_ensemble.gnn.md`` by default).

Usage::

    uv run python scripts/gnn_to_pymdp.py [gnn/bernoulli_toy.gnn.md]
    uv run python scripts/gnn_to_pymdp.py --harness [gnn/production_ensemble.gnn.md]

Prints the config as JSON to stdout (the executable-view configuration), so a
downstream practitioner can specify a new policy-entanglement experiment as a
``.gnn`` file and recover the harness configuration without writing Python.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from gnn.bridge import to_pymdp_config  # noqa: E402
from gnn.harness import harness_config  # noqa: E402
from gnn.parser import parse_gnn_file  # noqa: E402

DEFAULT_GNN = PROJECT_ROOT / "gnn" / "bernoulli_toy.gnn.md"
DEFAULT_HARNESS_GNN = PROJECT_ROOT / "gnn" / "production_ensemble.gnn.md"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    harness = "--harness" in args
    paths = [arg for arg in args if arg != "--harness"]
    default = DEFAULT_HARNESS_GNN if harness else DEFAULT_GNN
    gnn_path = Path(paths[0]) if paths else default
    model = parse_gnn_file(gnn_path)
    config = harness_config(model) if harness else to_pymdp_config(model)
    print(json.dumps(config, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
