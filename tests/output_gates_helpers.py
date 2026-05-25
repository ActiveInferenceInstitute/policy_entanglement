"""Shared pytest helpers for output-gates tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from manuscript.output_gates import (
    artifact_validators,
    constants,
    pymdp_long_horizon_validators,
    pymdp_revertibility_validators,
    pymdp_robustness_validators,
    pymdp_sweep_validators,
    pymdp_validators,
)

_OUTPUT_DIR_MODULES = (
    constants,
    artifact_validators,
    pymdp_validators,
    pymdp_sweep_validators,
    pymdp_long_horizon_validators,
    pymdp_revertibility_validators,
    pymdp_robustness_validators,
)


def patch_output_dir(monkeypatch: pytest.MonkeyPatch, root: Path) -> Path:
    """Point all output-gate validators at a temp ``output/`` tree."""
    out = root if root.name == "output" else root / "output"
    for module in _OUTPUT_DIR_MODULES:
        monkeypatch.setattr(module, "OUTPUT_DIR", out)
    return out
