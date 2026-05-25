"""Safe branch-coverage tests (no global import pollution)."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from lean import mathlib_proofs_gate as mpg
from orchestration import build_pdf as bp


def _install_fake_lake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, script: str) -> None:
    bindir = tmp_path / "bin"
    bindir.mkdir()
    lake = bindir / "lake"
    lake.write_text(script, encoding="utf-8")
    lake.chmod(lake.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}")


def test_pandoc_to_tex_assembles_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    combined_md = pdf_dir / f"{bp.COMBINED_STEM}.md"
    combined_md.write_text("# Title\n", encoding="utf-8")
    combined_tex = pdf_dir / f"{bp.COMBINED_STEM}.tex"
    preamble_tex = pdf_dir / "_preamble.tex"
    preamble_tex.write_text("\\usepackage{x}\n\\begin{document}\n", encoding="utf-8")
    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "config.yaml").write_text("paper:\n  title: Demo\n", encoding="utf-8")

    def _fake_run(cmd, *, cwd, stdout_path=None):
        combined_tex.write_text(
            "\\documentclass{article}\n\\begin{document}\n\\end{document}\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(bp, "_run", _fake_run)
    bp._pandoc_to_tex(
        combined_md=combined_md,
        combined_tex=combined_tex,
        pdf_dir=pdf_dir,
        preamble_tex=preamble_tex,
        source_manuscript=ms,
        project_root=tmp_path,
    )
    assert "\\usepackage{x}" in combined_tex.read_text(encoding="utf-8")


def test_mathlib_proofs_gate_rejects_warnings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mathlib_dir = tmp_path / "lean" / "MathlibProofs"
    mathlib_dir.mkdir(parents=True)
    (mathlib_dir / "lakefile.lean").write_text("-- scaffold\n", encoding="utf-8")
    (mathlib_dir / "MathlibProofs.lean").write_text("def proofSliceVersion : Nat := 3\n", encoding="utf-8")
    _install_fake_lake(
        tmp_path,
        monkeypatch,
        script='#!/bin/sh\necho "warning: MathlibProofs.lean:1:1: oops"\nexit 0\n',
    )
    assert mpg.run_mathlib_proofs_gate(tmp_path) == 1


def test_mathlib_proofs_gate_rejects_failed_build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mathlib_dir = tmp_path / "lean" / "MathlibProofs"
    mathlib_dir.mkdir(parents=True)
    (mathlib_dir / "lakefile.lean").write_text("-- scaffold\n", encoding="utf-8")
    (mathlib_dir / "MathlibProofs.lean").write_text("def proofSliceVersion : Nat := 3\n", encoding="utf-8")
    _install_fake_lake(tmp_path, monkeypatch, script="#!/bin/sh\nexit 1\n")
    assert mpg.run_mathlib_proofs_gate(tmp_path) == 1


def test_mathlib_proofs_gate_rejects_local_hygiene(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mathlib_dir = tmp_path / "lean" / "MathlibProofs"
    mathlib_dir.mkdir(parents=True)
    (mathlib_dir / "lakefile.lean").write_text("-- scaffold\n", encoding="utf-8")
    (mathlib_dir / "MathlibProofs.lean").write_text("def proofSliceVersion : Nat := 3\n", encoding="utf-8")
    (mathlib_dir / "Bad.lean").write_text("theorem bad : True := by sorry\n", encoding="utf-8")
    _install_fake_lake(tmp_path, monkeypatch, script="#!/bin/sh\nexit 0\n")
    assert mpg.run_mathlib_proofs_gate(tmp_path) == 1
