#!/usr/bin/env python3
"""Thin CLI wrapper for long-horizon coupled rollout."""

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

from simulation.long_horizon_pipeline import run_long_horizon_pipeline  # noqa: E402


def main() -> int:
    return run_long_horizon_pipeline(PROJECT_ROOT)


if __name__ == "__main__":
    sys.exit(main())
