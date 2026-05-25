#!/usr/bin/env python3
"""Thin CLI wrapper for MathlibProofs build + axiom audit."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from lean.mathlib_proofs_gate import (  # noqa: E402,F401
    ALLOWED_AXIOMS,
    FORBIDDEN_LOCAL_TOKENS,
    KEYSTONE_THEOREMS,
    run_mathlib_proofs_gate,
)
from lean.mathlib_proofs_gate import (  # noqa: E402
    axiom_audit as _axiom_audit_impl,
)
from lean.mathlib_proofs_gate import (  # noqa: E402
    declared_keystones as _declared_keystones_impl,
)
from lean.mathlib_proofs_gate import (  # noqa: E402
    local_hygiene_issues as _local_hygiene_issues_impl,
)

MATHLIB_PROOFS_DIR = PROJECT_ROOT / "lean" / "MathlibProofs"
MATHLIB_PROOFS_SRC = MATHLIB_PROOFS_DIR / "MathlibProofs.lean"


def _declared_keystones() -> list[str]:
    return _declared_keystones_impl(MATHLIB_PROOFS_SRC)


def _axiom_audit() -> list[str]:
    return _axiom_audit_impl(MATHLIB_PROOFS_DIR, MATHLIB_PROOFS_SRC)


def _local_hygiene_issues() -> list[str]:
    return _local_hygiene_issues_impl(MATHLIB_PROOFS_DIR, PROJECT_ROOT)


def main() -> int:
    return run_mathlib_proofs_gate(PROJECT_ROOT)


if __name__ == "__main__":
    sys.exit(main())
