#!/usr/bin/env python3
"""Thin CLI wrapper for the Lean 4 boundary-fragment build gate.

Business logic lives in :mod:`lean.build_gate` (under ``src/``). This
script bootstraps the project's ``src/`` subpackages onto :data:`sys.path`
and dispatches to the library entry point.

The gate runs ``lake build`` inside ``lean/`` and asserts the
boundary-fragment hygiene budget (zero ``sorry``/``axiom``/
``unsafe``/``partial``/``noncomputable`` declarations and zero Mathlib
imports from boundary modules). A non-zero exit propagates the failure
into :doc:`scripts/run_all.py </scripts/run_all>` and CI.

Usage::

    uv run python scripts/build_lean.py
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent

sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from lean.build_gate import main as _lib_main  # noqa: E402


def main() -> int:
    return _lib_main(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    sys.exit(main())
