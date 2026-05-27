"""Tests for ``MANUSCRIPT_NON_BODY_MD`` wiring and float residual export."""

from __future__ import annotations

from pathlib import Path

from manuscript import equation_numbering, renderer
from manuscript.meta_files import MANUSCRIPT_NON_BODY_MD
from manuscript.output_gates import csv_helpers
from manuscript.variables import build_float_real_residual, write_float_real_residual
from simulation import hyperparameters as H


def test_meta_files_constant_used_by_precompute_and_renderer() -> None:
    expected = frozenset({"README.md", "AGENTS.md", "INDEX.md", "SYNTAX.md", "preamble.md"})
    assert expected == MANUSCRIPT_NON_BODY_MD
    assert "SYNTAX.md" in MANUSCRIPT_NON_BODY_MD
    assert renderer.__doc__ is not None
    assert equation_numbering.__doc__ is not None


def test_parameter_sweep_required_columns_matches_default_utilities() -> None:
    cols = csv_helpers.parameter_sweep_required_columns()
    for u in H.PARAMETER_SWEEP_DEFAULT_UTILITIES:
        assert f"free_energy_u{u:g}" in cols
    assert "lambda" in cols
    assert "mi_closed_form" in cols


def test_float_real_residual_artifact_finite_and_consistent(tmp_path: Path) -> None:
    payload = build_float_real_residual()
    for key, value in payload.items():
        if key.endswith("_within_interval"):
            assert isinstance(value, bool)
            assert value is True
            continue
        if key.endswith("_reference"):
            assert isinstance(value, str)
            continue
        assert isinstance(value, float)
        assert value == value  # finite
    assert payload["decomposition_lhs_eq_rhs_max_residual"] >= 0.0
    assert payload["capstone_conjunct_tolerance"] == 1e-9
    assert payload["decomposition_lhs_eq_rhs_max_residual"] <= float(payload["decomposition_interval_upper"]) + 1e-18
    assert payload["decomposition_invariant_within_interval"] is True
    assert (
        abs(payload["montecarlo_mi_sample_mean"] - payload["montecarlo_mi_closed_form"])
        <= payload["montecarlo_mi_concentration_radius"] + 1e-12
    )
    out = write_float_real_residual(tmp_path / "output" / "reports" / "float_real_residual.json")
    assert out.exists()
