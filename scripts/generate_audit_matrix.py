#!/usr/bin/env python3
"""Generate the pymdp / Lean / manuscript claim audit matrix CSV.

Thin orchestrator: business logic lives in :mod:`manuscript.audit_matrix`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from manuscript.audit_matrix import (  # noqa: E402
    render_audit_matrix_csv,
    write_audit_matrix,
)

DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "_audit" / "pymdp_lean_manuscript_matrix_2026-05-21.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the CSV to docs/_audit/ (default when neither --check nor --write is given).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the on-disk CSV differs from the generator output.",
    )
    args = parser.parse_args()

    rendered = render_audit_matrix_csv(PROJECT_ROOT)
    if args.check:
        if not DEFAULT_OUTPUT.exists():
            print(f"missing audit matrix: {DEFAULT_OUTPUT}", file=sys.stderr)
            return 1
        on_disk = DEFAULT_OUTPUT.read_text(encoding="utf-8")
        if on_disk != rendered:
            print(f"audit matrix drift: regenerate with {Path(__file__).name} --write", file=sys.stderr)
            return 1
        print(f"audit matrix OK: {DEFAULT_OUTPUT}")
        return 0

    out_path = write_audit_matrix(PROJECT_ROOT, DEFAULT_OUTPUT)
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
