#!/usr/bin/env python3
"""Auto-generate the per-theorem four-track wiring table.

Thin orchestrator: business logic lives in
:mod:`manuscript.theorem_map`. This script binds the project root and
writes ``docs/reference/_theorem_map.md``.

Drift gate: ``tests/test_theorem_map_generated.py`` asserts that
re-running this generator produces no change to the on-disk file.
Any new theorem in ``labels.yaml`` or any rename of its Lean / Python /
test companion will fail CI until this table is regenerated.
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from manuscript import theorem_map as _tm  # noqa: E402

# Re-exports for tests (``tests/test_theorem_map_generated.py`` loads
# this script as a module and asserts on these names).
PYTHON_COMPANION = _tm.PYTHON_COMPANION
TEST_GATE = _tm.TEST_GATE
MATHLIB_READINESS = _tm.MATHLIB_READINESS


def render() -> str:
    """Render the auto-generated theorem-map markdown using the project root."""
    return _tm.render(PROJECT_ROOT / "manuscript" / "refs")


def main() -> int:
    out_path = _tm.write(PROJECT_ROOT)
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
