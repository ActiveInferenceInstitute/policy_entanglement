#!/usr/bin/env python3
"""Thin CLI wrapper for the revertibility / m-projection witness sweep.

Computation and artifact emission live in
:mod:`simulation.revertibility_pipeline`; this script bootstraps ``src/``
onto :data:`sys.path` and forwards to :func:`simulation.revertibility_pipeline.main`.

Skipped (stdout note, exit 0) when the ``sim`` group is not installed.
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

from simulation.revertibility_pipeline import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(project_root=PROJECT_ROOT))
