"""Pytest configuration shim.

Adds each subpackage of `src/` to `sys.path` so test modules can use
both bare module names (legacy: ``from joint_dist import ...``) and
fully-qualified subpackage paths (``from simulation.specs import ...``).
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT = Path(__file__).resolve().parent
_SRC_DIRS = [
    _PROJECT / "src",
    _PROJECT / "src" / "lean",
    _PROJECT / "src" / "simulation",
    _PROJECT / "src" / "visualizations",
    _PROJECT / "src" / "manuscript",
]
for _d in _SRC_DIRS:
    s = str(_d)
    if s not in sys.path:
        sys.path.insert(0, s)
