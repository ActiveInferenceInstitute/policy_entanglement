"""Coverage for audit matrix and float interval bracket modules."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from lean.invariants import SweepGrid
from manuscript.audit_matrix import (
    AUDIT_MATRIX_COLUMNS,
    _resolve_test_gate,
    _theorem_row,
    build_audit_matrix_rows,
    render_audit_matrix_csv,
    write_audit_matrix,
)
from manuscript.registry import TheoremEntry
from manuscript.theorem_map import TEST_GATE
from manuscript.float_real_interval import decomposition_interval_bracket
from manuscript.variables import build_float_real_residual, write_float_real_residual


def test_audit_matrix_rows_cover_all_registry_theorems() -> None:
    project = Path(__file__).resolve().parent.parent
    rows = build_audit_matrix_rows(project)
    assert len(rows) >= 28
    assert tuple(rows[0].keys()) == AUDIT_MATRIX_COLUMNS
    labels = __import__("yaml").safe_load(
        (project / "manuscript" / "refs" / "labels.yaml").read_text(encoding="utf-8")
    )["theorems"]
    for label in labels:
        assert any(row["claim_area"].startswith(f"{label} (") for row in rows)
    roadmap = next(row for row in rows if row["claim_area"].startswith("roadmap_float_real_residual"))
    assert "interval-bracket" in roadmap["remediation"] or "Flocq" in roadmap["remediation"]
    witness = next(row for row in rows if row["claim_area"].startswith("thm_4_3"))
    assert witness["remediation"] != "none"


def test_resolve_test_gate_formats() -> None:
    assert _resolve_test_gate("roadmap_float_real_residual", {}) == "tests/test_meta_files_and_float_residual.py"
    assert (
        _resolve_test_gate("x", {"tests": "tests/test_custom.py"})
        == "tests/test_custom.py"
    )
    assert _resolve_test_gate("x", {"tests": "custom.py"}) == "tests/custom.py"
    assert _resolve_test_gate("x", {"tests": "custom"}) == "tests/test_custom.py"
    assert _resolve_test_gate("missing_label", {}) == "tests/test_veridical_status_doc.py"
    assert _resolve_test_gate("thm_4_1", {}) == "tests/test_decomposition.py"


def test_theorem_row_proved_remediation_none() -> None:
    entry = TheoremEntry(
        label="cor_4_2",
        kind="Corollary",
        number="5.2",
        name="Coupling-pays",
        section="decomposition",
        lean_module="Decomposition",
        lean_name="couplingVerdict_correct",
        status="proved",
    )
    row = _theorem_row("cor_4_2", entry, {"faithfulness": "substantive"})
    assert row["remediation"] == "none"
    assert row["verdict"] == "proved/substantive"


def test_theorem_row_without_faithfulness_uses_status_only() -> None:
    entry = TheoremEntry(
        label="cor_4_2",
        kind="Corollary",
        number="5.2",
        name="Coupling-pays",
        section="decomposition",
        status="proved",
    )
    row = _theorem_row("cor_4_2", entry, {})
    assert row["verdict"] == "proved"


def test_resolve_test_gate_test_gate_path_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(TEST_GATE, "full_path", "tests/already/full.py")
    assert _resolve_test_gate("full_path", {}) == "tests/already/full.py"
    monkeypatch.setitem(TEST_GATE, "bare_py", "custom_gate.py")
    assert _resolve_test_gate("bare_py", {}) == "tests/custom_gate.py"


def test_render_and_write_audit_matrix_csv(tmp_path: Path) -> None:
    project = Path(__file__).resolve().parent.parent
    csv_text = render_audit_matrix_csv(project)
    assert csv_text.startswith("claim_area,")
    out = write_audit_matrix(project, tmp_path / "matrix.csv")
    assert out.read_text(encoding="utf-8") == csv_text


def test_generate_audit_matrix_script_check() -> None:
    project = Path(__file__).resolve().parent.parent
    proc = subprocess.run(
        [sys.executable, str(project / "scripts" / "generate_audit_matrix.py"), "--check"],
        cwd=project,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_decomposition_interval_bracket_contains_float_residual() -> None:
    grid = SweepGrid(0.0, 4.0, 21)
    bracket = decomposition_interval_bracket(grid)
    assert bracket["decomposition_interval_contains_float"] is True
    assert float(bracket["decomposition_interval_upper"]) >= 0.0
    assert float(bracket["decomposition_interval_grid_points"]) == 21.0


def test_build_and_write_float_real_residual_on_project() -> None:
    project = Path(__file__).resolve().parent.parent
    payload = build_float_real_residual(project)
    assert payload["decomposition_interval_contains_float"] is True
    out = write_float_real_residual(project_root=project)
    assert out.exists()


def test_build_float_real_residual_rejects_non_scalar_invariant(monkeypatch: pytest.MonkeyPatch) -> None:
    from reporting.interactive_dashboard import Invariant

    def _bad_decomposition(_grid: SweepGrid) -> list[Invariant]:
        return [
            Invariant(
                name="decomposition_lhs_eq_rhs_max_residual",
                actual=["not-a-scalar"],
                expected=0.0,
                tol=1e-9,
                kind="equal",
                description="bad",
            )
        ]

    monkeypatch.setattr("manuscript.variables.decomposition_invariants", _bad_decomposition)
    with pytest.raises(TypeError, match="scalar"):
        build_float_real_residual()


def test_variables_main_prints_output_path(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = Path("/tmp/manuscript_variables_out.json")

    def _fake_write(**_kwargs: object) -> Path:
        return sentinel

    monkeypatch.setattr("manuscript.variables.write_manuscript_variables", _fake_write)
    from manuscript.variables import main

    main()
    assert capsys.readouterr().out.strip() == str(sentinel)
