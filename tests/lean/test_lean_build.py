"""Pipeline gate: the Lean 4 boundary fragment must build cleanly with
zero `sorry`s, zero `axiom`s, and zero `unsafe`/`partial`/`noncomputable`
declarations. Any regression here fails CI immediately.

Skipped automatically if the `lake` binary is not on PATH (so a
Python-only dev environment does not block local testing).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BUILD_LEAN = PROJECT_ROOT / "scripts" / "build_lean.py"


@pytest.mark.skipif(
    shutil.which("lake") is None,
    reason="`lake` (Lean 4 build tool) not on PATH",
)
def test_lake_build_zero_sorry_zero_axiom() -> None:
    """`scripts/build_lean.py` runs `lake build` and asserts a
    sorry/axiom/unsafe budget of zero. Exit 0 = all gates passed."""
    result = subprocess.run(
        [sys.executable, str(BUILD_LEAN)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"build_lean.py failed (exit {result.returncode})\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )
    assert "0 sorries" in result.stdout
    assert "0 axioms" in result.stdout
