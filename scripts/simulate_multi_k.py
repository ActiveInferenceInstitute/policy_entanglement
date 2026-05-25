#!/usr/bin/env python3
"""Thin CLI wrapper for multi-K ensemble experiments."""

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

from simulation.multi_k_pipeline import (  # noqa: E402,F401
    figure_metadata_snapshot,
    run_multi_k_pipeline,
    write_multi_k_csv,
)

FIG_DIR = PROJECT_ROOT / "output" / "figures"
SIM_DIR = PROJECT_ROOT / "output" / "simulations"
DATA_DIR = PROJECT_ROOT / "output" / "data"


def main() -> int:
    return run_multi_k_pipeline(PROJECT_ROOT)


if __name__ == "__main__":
    sys.exit(main())
