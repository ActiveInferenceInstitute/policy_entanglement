#!/usr/bin/env python3
"""Thin CLI wrapper for the project-local combined-PDF renderer.

Business logic lives in :mod:`orchestration.build_pdf` (under ``src/``).
This script bootstraps the project's ``src/`` subpackages onto
:data:`sys.path` and dispatches to the library entry point.

Usage::

    uv run python scripts/build_pdf.py
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent

sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from orchestration.build_pdf import main as _lib_main  # noqa: E402


def main() -> int:
    return _lib_main(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    sys.exit(main())
