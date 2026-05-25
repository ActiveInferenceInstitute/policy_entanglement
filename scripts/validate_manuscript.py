#!/usr/bin/env python3
"""Thin CLI wrapper for the manuscript-completeness validator.

Business logic lives in :mod:`manuscript.validation_cli` (under ``src/``).
This script bootstraps the project's ``src/`` subpackages onto
:data:`sys.path` and dispatches to the library entry point.

Runs the full :func:`manuscript.validation.validate_manuscript_tree`
suite plus rendered-token-leak, project-status, stale-reference, and
MathlibProofs-claim gates. Exits non-zero on any failure (suitable as
a CI gate).

Usage::

    uv run python scripts/validate_manuscript.py
    uv run python scripts/validate_manuscript.py --manuscript-dir path/to/manuscript
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent

sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from manuscript.validation_cli import main as _lib_main  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    return _lib_main(argv, project_root=PROJECT_ROOT)


if __name__ == "__main__":
    sys.exit(main())
