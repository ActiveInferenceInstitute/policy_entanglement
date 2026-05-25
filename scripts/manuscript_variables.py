#!/usr/bin/env python3
"""Thin CLI wrapper for the manuscript-variables generator.

Business logic lives in :mod:`manuscript.variables` (under ``src/``). This
script keeps the historical CLI stable while remaining a thin orchestrator
that bootstraps the project's ``src/`` subpackages onto :data:`sys.path`,
calls into ``src/``, and prints the emitted output path.
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from manuscript.variables import (  # noqa: E402,F401
    _format_lambda_key,
    _format_lambda_list,
    build_manuscript_variables,
    main,
    write_manuscript_variables,
)

__all__ = [
    "PROJECT_ROOT",
    "_format_lambda_key",
    "_format_lambda_list",
    "build_manuscript_variables",
    "main",
    "write_manuscript_variables",
]


if __name__ == "__main__":
    main()
