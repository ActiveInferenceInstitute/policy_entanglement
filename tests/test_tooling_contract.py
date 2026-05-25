"""Tooling-contract guards for the documented local release gates."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tokenize
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def _pyproject_text() -> str:
    return (PROJECT / "pyproject.toml").read_text(encoding="utf-8")


def _dependency_group_block(name: str) -> str:
    text = _pyproject_text()
    match = re.search(rf"^{name}\s*=\s*\[(.*?)^\]", text, flags=re.MULTILINE | re.DOTALL)
    assert match is not None, f"missing dependency group {name}"
    return match.group(1)


def test_default_uv_sync_installs_lint_gate_dependencies() -> None:
    text = _pyproject_text()
    assert 'default-groups = ["dev", "viz", "lint"]' in text

    lint_block = _dependency_group_block("lint")
    for package in ("ruff", "mypy", "types-pyyaml"):
        assert package in lint_block.lower()


def test_documented_release_gate_uses_default_lint_environment() -> None:
    root_docs = "\n".join(
        [
            (PROJECT / "README.md").read_text(encoding="utf-8"),
            (PROJECT / "AGENTS.md").read_text(encoding="utf-8"),
            (PROJECT / "docs" / "reference" / "reproducibility_checklist.md").read_text(encoding="utf-8"),
        ]
    )
    assert "uv run mypy src/ scripts/" in root_docs
    assert "scripts/run_all.py --with-pdf --with-mathlib" in root_docs
    assert 'default-groups = ["dev", "viz", "lint"]' in _pyproject_text()


def test_dashboard_reporting_imports_are_project_local() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT / "src")
    code = "\n".join(
        [
            "from lean.invariants import SweepGrid, ising_invariants",
            "from reporting.interactive_dashboard import InteractiveDashboard, Invariant, Panel",
            "grid = SweepGrid(0.0, 1.0, 3)",
            "assert ising_invariants(grid)",
            "dash = InteractiveDashboard(title='standalone')",
            "dash.add_panel(Panel(panel_id='p', title='P', traces=[]))",
            "dash.add_invariant(Invariant('ok', actual=1.0, expected=1.0))",
            "assert dash.evaluate_invariants()[0]['passed']",
        ]
    )

    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"


def test_pdf_renderer_is_project_local() -> None:
    build_pdf = (PROJECT / "scripts" / "build_pdf.py").read_text(encoding="utf-8")
    assert "infrastructure.rendering" not in build_pdf
    assert "parent template" not in build_pdf.lower()


def test_tests_do_not_use_mocking_frameworks() -> None:
    forbidden = {"MagicMock", "Mock", "unittest.mock", "mocker.patch", "pytest_mock"}
    offenders: list[str] = []

    for path in sorted((PROJECT / "tests").rglob("test_*.py")):
        tokens: list[str] = []
        with path.open(encoding="utf-8") as fh:
            for tok in tokenize.generate_tokens(fh.readline):
                if tok.type in {tokenize.COMMENT, tokenize.STRING, tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE}:
                    continue
                tokens.append(tok.string)
        source_tokens = " ".join(tokens)
        compact_tokens = source_tokens.replace(" ", "")
        for needle in forbidden:
            haystack = compact_tokens if "." in needle else source_tokens
            if needle in haystack:
                offenders.append(f"{path.relative_to(PROJECT)}: forbidden mock token {needle!r}")

    assert not offenders, "\n".join(offenders)
