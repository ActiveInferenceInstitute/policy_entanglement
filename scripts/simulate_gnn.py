#!/usr/bin/env python3
r"""Run the GNN fifth-track round-trip (executable Triple-Play view).

Thin orchestrator: the round-trip logic lives in :mod:`gnn.runner`; this script
binds output directories and forwards. The ``DATA_DIR`` / ``FIG_DIR`` /
``GNN_DIR`` module-level attributes are patchable for deterministic test runs.

Reconstructs the K=2 Bernoulli/Ising mutual-information curve from
``gnn/bernoulli_toy.gnn.md`` via the framework's general machinery
(``gnn.bridge``), compares it to the closed form, and emits:

* ``output/data/gnn_bernoulli_roundtrip.json`` — deterministic sidecar with the
  per-lambda residuals, the max residual, and an embedded zero-coupling
  negative-control residual (non-vacuity evidence).
* ``output/figures/gnn_bernoulli_roundtrip.png`` — MI overlay + residual.
* ``gnn/generated/BernoulliToyGnn.lean`` — the emitted Lean typed contract.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from gnn import runner as _runner  # noqa: E402

DATA_DIR = PROJECT_ROOT / "output" / "data"
FIG_DIR = PROJECT_ROOT / "output" / "figures"
GNN_DIR = PROJECT_ROOT / "gnn"


def main() -> int:
    return _runner.run(data_dir=DATA_DIR, fig_dir=FIG_DIR, gnn_dir=GNN_DIR)


if __name__ == "__main__":
    sys.exit(main())
