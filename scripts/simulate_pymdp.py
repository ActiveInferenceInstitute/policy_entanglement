#!/usr/bin/env python3
"""Thin CLI wrapper for the pymdp POMDP simulation harness.

CLI argument parsing, hyperparameter overrides, and pipeline orchestration
live in :mod:`simulation.pymdp_pipeline` (under ``src/``); figure-emitting
functions live in :mod:`visualizations.pymdp_figures`. This script
bootstraps the project's ``src/`` subpackages onto :data:`sys.path` and
forwards argv to the src-side :func:`main`.

The figure functions and the module-level ``FIG_DIR`` / ``SIM_DIR`` / ``LOGGER``
constants are re-exported into this module's namespace so historical test
entry points that do ``importlib.import_module("simulate_pymdp")`` and
monkeypatch those names continue to work without modification.

When no CLI flags are supplied the run is bit-exact equivalent to the
pre-refactor behaviour, so manuscript-variable injection and tests are
unaffected. When pymdp is not importable the pipeline prints
``pymdp not installed; skipping simulate_pymdp.py`` on stdout and exits
0 — keeping the figure pipeline and CI runners robust on lean
environments that do not ship the optional ``sim`` group.

Usage::

    uv run --active python scripts/simulate_pymdp.py
    uv run --active python scripts/simulate_pymdp.py --ensemble-K 3 --observations 1 0 1
    uv run --active python scripts/simulate_pymdp.py --rollout-steps 32 --rollout-lambda 1.5
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

from simulation.pymdp_pipeline import (  # noqa: E402,F401
    apply_overrides,
    main,
    parse_args,
)

# Backwards-compatible private alias preserved for any caller that imported the
# historical private name directly from this script.
_parse_args = parse_args
_apply_overrides = apply_overrides

# Re-export the figure surface so test monkeypatches against the script-module
# attributes (``FIG_DIR``, ``SIM_DIR``, ``LOGGER``, the ``figure_pymdp_*`` callables)
# continue to find the same objects as the importable ``visualizations.pymdp_figures``
# module.
from visualizations.pymdp_figures import (  # noqa: E402,F401
    FIG_DIR,
    LOGGER,
    SIM_DIR,
    figure_pymdp_free_energies,
    figure_pymdp_lambda_sweep,
    figure_pymdp_rollout,
)

__all__ = [
    "FIG_DIR",
    "LOGGER",
    "PROJECT_ROOT",
    "SIM_DIR",
    "_apply_overrides",
    "_parse_args",
    "apply_overrides",
    "figure_pymdp_free_energies",
    "figure_pymdp_lambda_sweep",
    "figure_pymdp_rollout",
    "main",
    "parse_args",
]


if __name__ == "__main__":
    main()
