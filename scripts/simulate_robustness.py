#!/usr/bin/env python3
"""Run robustness, ablation, and long-horizon replicate sidecars.

Thin orchestrator: numerical logic lives in :mod:`simulation.robustness`,
plotting in :mod:`visualizations.robustness_plots`, and the
serialisation + figure-emission glue in
:mod:`simulation.robustness_runner`. Every configured value comes from
:mod:`simulation.hyperparameters`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from simulation.agents import pymdp_available  # noqa: E402
from simulation.robustness_runner import run_robustness_pipeline  # noqa: E402

FIG_DIR = PROJECT_ROOT / "output" / "figures"
SIM_DIR = PROJECT_ROOT / "output" / "simulations"
DATA_DIR = PROJECT_ROOT / "output" / "data"


def main() -> int:
    if not pymdp_available():  # pragma: no cover
        print("pymdp not installed; skipping simulate_robustness.py")
        print("Install via: uv sync --group sim")
        return 0
    artifacts = run_robustness_pipeline(
        fig_dir=FIG_DIR,
        sim_dir=SIM_DIR,
        data_dir=DATA_DIR,
        project_root=PROJECT_ROOT,
    )
    for path in artifacts:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
