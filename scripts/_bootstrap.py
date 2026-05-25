"""Shared sys.path bootstrap for project scripts."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_project_paths(*, project_root: Path | None = None) -> Path:
    """Insert ``src/`` subpackage roots on ``sys.path`` once."""

    root = project_root or Path(__file__).resolve().parent.parent
    src = root / "src"
    # The empty-string entry adds ``src/`` itself; that's enough for the
    # newer packages (``gates``, ``orchestration``) that use namespaced
    # imports. The other subpackages retain bare-import-friendly entries
    # for legacy callers that import like ``from coupling import ...``.
    for sub in ("", "lean", "simulation", "visualizations", "manuscript", "reporting", "dashboard_types"):
        path = src / sub if sub else src
        entry = str(path)
        if entry in sys.path:
            sys.path.remove(entry)
        sys.path.insert(0, entry)
    return root


__all__ = ["ensure_project_paths"]
