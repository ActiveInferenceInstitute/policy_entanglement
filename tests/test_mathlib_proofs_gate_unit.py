"""Unit tests for :mod:`lean.mathlib_proofs_gate`."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from lean import mathlib_proofs_gate as mpg

PROJECT = Path(__file__).resolve().parent.parent


def test_declared_keystones_reads_live_source() -> None:
    src = PROJECT / "lean" / "MathlibProofs" / "MathlibProofs.lean"
    names = mpg.declared_keystones(src)
    assert "entanglement_decomposition_generalK" in names


def test_declared_keystones_missing_file(tmp_path: Path) -> None:
    assert mpg.declared_keystones(tmp_path / "missing.lean") == []


def test_local_hygiene_and_warning_helpers(tmp_path: Path) -> None:
    lean_dir = tmp_path / "lean" / "MathlibProofs"
    lean_dir.mkdir(parents=True)
    (lean_dir / "Bad.lean").write_text("theorem t : True := by sorry\n", encoding="utf-8")
    issues = mpg.local_hygiene_issues(lean_dir, tmp_path)
    assert any("sorry" in issue for issue in issues)
    warnings = mpg.local_warning_issues("warning: MathlibProofs.lean:12:3: unused\n")
    assert len(warnings) == 1


def test_run_mathlib_proofs_gate_without_lakefile(tmp_path: Path) -> None:
    mathlib_dir = tmp_path / "lean" / "MathlibProofs"
    mathlib_dir.mkdir(parents=True)
    (mathlib_dir / "MathlibProofs.lean").write_text("-- stub\n", encoding="utf-8")
    assert mpg.run_mathlib_proofs_gate(tmp_path) == 0


def test_axiom_audit_reports_missing_keystones(tmp_path: Path) -> None:
    lean_dir = tmp_path / "MathlibProofs"
    lean_dir.mkdir()
    src = lean_dir / "MathlibProofs.lean"
    src.write_text("theorem streamMarginal_productDist : True := trivial\n", encoding="utf-8")
    issues = mpg.axiom_audit(lean_dir, src, project_root=tmp_path)
    assert any("expected keystone" in issue for issue in issues)


def test_axiom_audit_empty_source(tmp_path: Path) -> None:
    lean_dir = tmp_path / "MathlibProofs"
    lean_dir.mkdir()
    src = lean_dir / "MathlibProofs.lean"
    src.write_text("-- empty\n", encoding="utf-8")
    assert mpg.axiom_audit(lean_dir, src, project_root=tmp_path) == [
        "no keystone theorems declared in MathlibProofs.lean — the genuine ℝ proof is missing"
    ]


def test_lake_lock_serializes(tmp_path: Path) -> None:
    from lean._lake_lock import mathlib_proofs_lock, mathlib_proofs_lock_path

    path = mathlib_proofs_lock_path(tmp_path)
    with mathlib_proofs_lock(tmp_path):
        assert path.exists()


def test_axiom_audit_non_foundational_axiom(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lean_dir = tmp_path / "MathlibProofs"
    lean_dir.mkdir(parents=True)
    src = lean_dir / "MathlibProofs.lean"
    src.write_text(
        "\n".join(f"theorem {name} : True := trivial" for name in mpg.KEYSTONE_THEOREMS) + "\n", encoding="utf-8"
    )

    def _bad_axioms(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout="'MathlibProofs.streamMarginal_productDist' depends on axioms: [propext, sorryAx]\n",
            stderr="",
        )

    monkeypatch.setattr(mpg.subprocess, "run", _bad_axioms)
    issues = mpg.axiom_audit(lean_dir, src, project_root=tmp_path)
    assert any("NON-foundational" in issue for issue in issues)


def test_axiom_audit_unparseable_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lean_dir = tmp_path / "MathlibProofs"
    lean_dir.mkdir(parents=True)
    src = lean_dir / "MathlibProofs.lean"
    body = "\n".join(f"theorem {name} : True := trivial" for name in mpg.KEYSTONE_THEOREMS)
    src.write_text(body + "\n", encoding="utf-8")

    def _empty(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, 0, stdout="no axioms here\n", stderr="")

    monkeypatch.setattr(mpg.subprocess, "run", _empty)
    issues = mpg.axiom_audit(lean_dir, src, project_root=tmp_path)
    assert any("could not parse" in issue for issue in issues)


def test_run_mathlib_proofs_gate_prints_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mathlib_dir = tmp_path / "lean" / "MathlibProofs"
    mathlib_dir.mkdir(parents=True)
    (mathlib_dir / "lakefile.lean").write_text("-- lake\n", encoding="utf-8")
    body = "\n".join(f"theorem {name} : True := trivial" for name in mpg.KEYSTONE_THEOREMS)
    (mathlib_dir / "MathlibProofs.lean").write_text(body + "\n", encoding="utf-8")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    lake = bin_dir / "lake"
    lake.write_text(
        '#!/bin/sh\nif [ "$1" = "build" ]; then echo OK; exit 0; fi\nif [ "$1" = "env" ]; then exit 0; fi\nexit 1\n',
        encoding="utf-8",
    )
    lake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setattr(mpg, "axiom_audit", lambda *args, **kwargs: [])

    assert mpg.run_mathlib_proofs_gate(tmp_path) == 0
    out = capsys.readouterr().out
    assert "keystone" in out
