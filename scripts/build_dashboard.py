#!/usr/bin/env python3
"""Thin CLI wrapper for the interactive simulation dashboard.

Computation, invariant assembly, and HTML/JSON emission live in
:mod:`dashboard_types.dashboard` (under ``src/``). This script bootstraps the
project's ``src/`` subpackages onto :data:`sys.path` and forwards argv into the
src-side :func:`main`.

Usage::

    uv run --active python scripts/build_dashboard.py
    uv run --active python scripts/build_dashboard.py --lam-min 0 --lam-max 8 --num 401
    uv run --active python scripts/build_dashboard.py --utilities 0 0.5 1 2 4
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

from dashboard_types.dashboard import (  # noqa: E402,F401
    DATA_DIR,
    OUTPUT,
    REP_DIR,
    WEB_DIR,
    build_dashboard,
    build_dashboard_payload,
    main,
    parse_dashboard_args,
    write_dashboard,
)

# Backwards-compatible private aliases (preserved for any callers that imported
# the historical private names directly from this script).
_build_dashboard = build_dashboard
_compute_payload = build_dashboard_payload
_parse_args = parse_dashboard_args

__all__ = [
    "DATA_DIR",
    "OUTPUT",
    "PROJECT_ROOT",
    "REP_DIR",
    "WEB_DIR",
    "_build_dashboard",
    "_compute_payload",
    "_parse_args",
    "build_dashboard",
    "build_dashboard_payload",
    "main",
    "parse_dashboard_args",
    "write_dashboard",
]


if __name__ == "__main__":
    main()
