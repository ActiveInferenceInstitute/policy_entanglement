#!/usr/bin/env python3
"""Validate the rendered combined PDF and its TeX intermediates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
TEMPLATE_ROOT = PROJECT_ROOT.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from manuscript.pdf_validation import validate_pdf_artifacts  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pdf",
        type=Path,
        default=PROJECT_ROOT / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf",
    )
    args = parser.parse_args(argv)

    print("[pdf validation]")
    issues = validate_pdf_artifacts(
        project_root=PROJECT_ROOT,
        pdf_path=args.pdf,
        template_root=TEMPLATE_ROOT,
    )
    if issues:
        for issue in issues:
            print(f"  ✗ {issue.format()}", file=sys.stderr)
        print(f"FAILED: {len(issues)} PDF validation issue(s)", file=sys.stderr)
        return 1
    print(f"  ✓ {args.pdf.relative_to(PROJECT_ROOT)}")
    print("All PDF validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
