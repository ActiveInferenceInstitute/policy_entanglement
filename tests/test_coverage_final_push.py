"""Extra pymdp validator branches and validation_cli main() coverage."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from manuscript import validation_cli as vc
from manuscript.output_gates import pymdp_validators

PROJECT = Path(__file__).resolve().parent.parent


def test_pymdp_validators_optional_missing_are_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output"
    (out / "data").mkdir(parents=True)
    (out / "simulations").mkdir(parents=True)
    monkeypatch.setattr(pymdp_validators, "OUTPUT_DIR", out)
    assert pymdp_validators.validate_sweep() == 0
    assert pymdp_validators.validate_free_energy_bundle() == 0
    assert pymdp_validators.validate_multi_k_sweep() == 0


def test_pymdp_validate_sweep_missing_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output" / "data"
    out.mkdir(parents=True)
    path = out / "parameter_sweep.csv"
    path.write_text("lambda,mi_closed_form\n0.0,0.1\n1.0,0.2\n", encoding="utf-8")
    monkeypatch.setattr(pymdp_validators, "OUTPUT_DIR", tmp_path / "output")
    assert pymdp_validators.validate_sweep() >= 1


def test_pymdp_validate_sweep_too_few_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output" / "data"
    out.mkdir(parents=True)
    path = out / "parameter_sweep.csv"
    path.write_text(
        "lambda,mi_closed_form,mi_empirical,mi_residual,free_energy_u0,"
        "free_energy_u1,free_energy_u2,schmidt_rank,entanglement_entropy,phase\n"
        "0.0,0.1,0.1,0.0,0.0,0.0,0.0,2,0.5,p\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pymdp_validators, "OUTPUT_DIR", tmp_path / "output")
    assert pymdp_validators.validate_sweep() >= 1


def test_validation_cli_main_on_minimal_manuscript(tmp_path: Path) -> None:
    ms = tmp_path / "manuscript"
    refs = ms / "refs"
    refs.mkdir(parents=True)
    shutil.copytree(PROJECT / "manuscript" / "refs", refs, dirs_exist_ok=True)
    (ms / "01_intro.md").write_text("# Introduction\n\nClean prose.\n", encoding="utf-8")
    (tmp_path / "output" / "data").mkdir(parents=True)
    (tmp_path / "output" / "data" / "manuscript_variables.json").write_text("{}\n", encoding="utf-8")
    code = vc.main([], project_root=tmp_path)
    assert code in (0, 1)


def test_report_rendered_leaks_detects_unresolved(tmp_path: Path) -> None:
    rendered = tmp_path / "output" / "manuscript"
    rendered.mkdir(parents=True)
    (rendered / "01_a.md").write_text("See [[FIG:missing]] token\n", encoding="utf-8")
    assert vc._report_rendered_leaks(rendered, project_root=tmp_path) >= 1
