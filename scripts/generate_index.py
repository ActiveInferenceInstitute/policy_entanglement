#!/usr/bin/env python3
"""Thin CLI wrapper for auto-generating ``manuscript/INDEX.md``.

Business logic lives in :mod:`manuscript.index_generator` (under ``src/``).
This script bootstraps the project's ``src/`` subpackages onto
:data:`sys.path` and dispatches to the library entry point.

Walks the manuscript/ directory, groups files by IMRAD Part (encoded in
the filename prefix ``<digit><letter>_``), and emits a TOC table pairing
each file with its registry title or the heading from the file itself
(for unregistered Part divider files).

Usage::

    uv run python scripts/generate_index.py
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent

sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from manuscript.index_generator import write_index  # noqa: E402


def main() -> int:
    out_path = write_index(manuscript_dir=PROJECT_ROOT / "manuscript")
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
