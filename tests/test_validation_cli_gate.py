"""Integration tests for :mod:`manuscript.validation_cli`."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from manuscript.validation_cli import build_parser, main

PROJECT = Path(__file__).resolve().parent.parent


def test_build_parser_defaults_point_at_project_tree() -> None:
    parser = build_parser(project_root=PROJECT)
    args = parser.parse_args([])
    assert args.manuscript_dir == PROJECT / "manuscript"
    assert args.variables == PROJECT / "output" / "data" / "manuscript_variables.json"


def test_validation_cli_main_passes_on_real_repository() -> None:
    variables = PROJECT / "output" / "data" / "manuscript_variables.json"
    if not variables.exists():
        pytest.skip("manuscript_variables.json missing — run analysis pipeline first")
    code = main([], project_root=PROJECT)
    assert code == 0


def test_validate_manuscript_script_delegates_to_library() -> None:
    variables = PROJECT / "output" / "data" / "manuscript_variables.json"
    if not variables.exists():
        pytest.skip("manuscript_variables.json missing — run analysis pipeline first")
    proc = subprocess.run(
        [sys.executable, str(PROJECT / "scripts" / "validate_manuscript.py")],
        cwd=str(PROJECT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
