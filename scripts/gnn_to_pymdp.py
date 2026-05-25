#!/usr/bin/env python3
r"""GNN -> pymdp config generator (the S08 ``scripts/gnn_to_pymdp.py`` deliverable).

Thin orchestrator: consumes a GNN source file and emits the structural
configuration a pymdp-style harness needs (stream count, per-stream policy
cardinality, per-stream habit priors, the joint coupling tensor, scalar
parameters), sourced entirely from the ``.gnn`` declarations via
:func:`gnn.bridge.to_pymdp_config`.

Usage::

    uv run python scripts/gnn_to_pymdp.py [gnn/bernoulli_toy.gnn.md]

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
from gnn.parser import parse_gnn_file  # noqa: E402

DEFAULT_GNN = PROJECT_ROOT / "gnn" / "bernoulli_toy.gnn.md"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    gnn_path = Path(args[0]) if args else DEFAULT_GNN
    config = to_pymdp_config(parse_gnn_file(gnn_path))
    print(json.dumps(config, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
