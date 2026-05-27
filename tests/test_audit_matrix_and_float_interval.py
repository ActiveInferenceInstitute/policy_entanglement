"""Coverage for audit matrix and float interval bracket modules."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from lean.invariants import decomposition_sweep_points
from manuscript.audit_matrix import (
    AUDIT_MATRIX_COLUMNS,
    _resolve_test_gate,
    _theorem_row,
    build_audit_matrix_rows,
    render_audit_matrix_csv,
    write_audit_matrix,
)
from manuscript.float_real_interval import decomposition_interval_bracket
from manuscript.registry import TheoremEntry, load_labels
from manuscript.theorem_map import TEST_GATE
from manuscript.variables import (
    build_float_real_residual,
    decomposition_certificate_grid,
    write_float_real_residual,
)


def test_audit_matrix_rows_cover_all_registry_theorems() -> None:
    project = Path(__file__).resolve().parent.parent
    rows = build_audit_matrix_rows(project)
    assert len(rows) >= 28
    assert tuple(rows[0].keys()) == AUDIT_MATRIX_COLUMNS
    labels = load_labels(project / "manuscript" / "refs" / "labels.yaml")
    for label in labels.theorems:
        assert any(row["claim_area"].startswith(f"{label} (") for row in rows)
    roadmap = next(row for row in rows if row["claim_area"].startswith("roadmap_float_real_residual"))
    assert "interval-bracket" in roadmap["remediation"] or "Flocq" in roadmap["remediation"]
    witness = next(row for row in rows if row["claim_area"].startswith("thm_4_3"))
    assert witness["remediation"] != "none"


def test_audit_matrix_no_silent_veridical_fallback() -> None:
    project = Path(__file__).resolve().parent.parent
    labels = load_labels(project / "manuscript" / "refs" / "labels.yaml")
    missing: list[str] = []
    for label, entry in labels.theorems.items():
        if entry.tests.strip():
            continue
        if label not in TEST_GATE:
            missing.append(label)
    assert missing == [], f"theorem labels missing TEST_GATE and explicit tests: {missing}"


def test_resolve_test_gate_formats() -> None:
    empty = TheoremEntry(label="x", kind="Theorem", number="1", name="n", section="s")
    assert _resolve_test_gate("roadmap_float_real_residual", empty) == "tests/test_meta_files_and_float_residual.py"
    assert (
        _resolve_test_gate("x", TheoremEntry("x", "Theorem", "1", "n", "s", tests="tests/test_custom.py"))
        == "tests/test_custom.py"
    )
    assert _resolve_test_gate("x", TheoremEntry("x", "Theorem", "1", "n", "s", tests="custom.py")) == "tests/custom.py"
    assert (
        _resolve_test_gate("x", TheoremEntry("x", "Theorem", "1", "n", "s", tests="custom")) == "tests/test_custom.py"
    )
    assert _resolve_test_gate("missing_label", empty) == "tests/test_veridical_status_doc.py"
    assert _resolve_test_gate("thm_4_1", empty) == "tests/test_decomposition.py"


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
        faithfulness="substantive",
    )
    row = _theorem_row("cor_4_2", entry)
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
    row = _theorem_row("cor_4_2", entry)
    assert row["verdict"] == "proved"


def test_resolve_test_gate_test_gate_path_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    empty = TheoremEntry(label="x", kind="Theorem", number="1", name="n", section="s")
    monkeypatch.setitem(TEST_GATE, "full_path", "tests/already/full.py")
    assert _resolve_test_gate("full_path", empty) == "tests/already/full.py"
    monkeypatch.setitem(TEST_GATE, "bare_py", "custom_gate.py")
    assert _resolve_test_gate("bare_py", empty) == "tests/custom_gate.py"


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


def test_load_audit_track_rows_rejects_invalid_track(tmp_path: Path) -> None:
    from manuscript.audit_matrix import _load_audit_track_rows

    tracks_dir = tmp_path / "manuscript" / "refs"
    tracks_dir.mkdir(parents=True)
    (tracks_dir / "audit_tracks.yaml").write_text("tracks:\n  - claim_area: only-one-column\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        _load_audit_track_rows(tmp_path)


def test_decomposition_interval_bracket_two_source_check() -> None:
    grid = decomposition_certificate_grid()
    points = decomposition_sweep_points(grid)
    max_residual = max(point.residual for point in points)
    bracket = decomposition_interval_bracket(points, invariant_max_residual=max_residual)
    assert bracket["decomposition_invariant_within_interval"] is True
    assert float(bracket["decomposition_interval_upper"]) >= max_residual
    assert float(bracket["decomposition_interval_grid_points"]) == float(len(points))


def test_decomposition_interval_bracket_rejects_empty_points() -> None:
    with pytest.raises(ValueError, match="at least one sweep point"):
        decomposition_interval_bracket([], invariant_max_residual=0.0)


def test_decomposition_interval_bracket_rejects_inflated_invariant() -> None:
    grid = decomposition_certificate_grid()
    points = decomposition_sweep_points(grid)
    max_residual = max(point.residual for point in points)
    bracket = decomposition_interval_bracket(points, invariant_max_residual=max_residual * 10.0 + 1.0)
    assert bracket["decomposition_invariant_within_interval"] is False


def test_decomposition_interval_worst_lambda_at_interval_peak() -> None:
    from decimal import Decimal, localcontext

    from lean.invariants import DecompositionSweepPoint

    def _upper(residual: float, lhs: float, rhs_total: float) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = 50
            base = Decimal(str(residual))
            scale = max(abs(Decimal(str(lhs))), abs(Decimal(str(rhs_total))), Decimal("1"))
            margin = scale * Decimal(2) ** -50 + Decimal(2) ** -52
            return base + margin

    points = [
        DecompositionSweepPoint(lam=0.0, residual=1.0, lhs=0.0, rhs_total=0.0),
        DecompositionSweepPoint(lam=1.0, residual=0.5, lhs=100.0, rhs_total=100.0),
    ]
    peak_lam = max(points, key=lambda p: _upper(p.residual, p.lhs, p.rhs_total)).lam
    bracket = decomposition_interval_bracket(points, invariant_max_residual=1.0)
    assert bracket["decomposition_interval_worst_lambda"] == peak_lam


def test_build_and_write_float_real_residual_on_project() -> None:
    project = Path(__file__).resolve().parent.parent
    payload = build_float_real_residual()
    assert payload["decomposition_invariant_within_interval"] is True
    assert payload["decomposition_lhs_eq_rhs_max_residual"] <= float(payload["decomposition_interval_upper"]) + 1e-18
    out = write_float_real_residual(project_root=project)
    assert out.exists()


def test_build_float_real_residual_rejects_non_scalar_invariant(monkeypatch: pytest.MonkeyPatch) -> None:
    from reporting.interactive_dashboard import Invariant

    def _bad_decomposition(_points: object) -> list[Invariant]:
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

    monkeypatch.setattr("manuscript.variables.decomposition_invariants_from_points", _bad_decomposition)
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
