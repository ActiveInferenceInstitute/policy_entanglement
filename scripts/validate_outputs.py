#!/usr/bin/env python3
"""Thin CLI wrapper for output artifact validation gates."""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)
from manuscript.output_gates import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
