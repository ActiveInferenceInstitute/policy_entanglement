"""Tests for :mod:`simulation.parameter_sweep` (importable sweep writer).

Referenced from ``manuscript/S08_gnn_generalized_notation_extension.md`` as the
validation gate for ``output/data/parameter_sweep.csv``.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from simulation import hyperparameters as H
from simulation.parameter_sweep import run


def test_parameter_sweep_run_writes_expected_grid(tmp_path: Path) -> None:
    out = tmp_path / "parameter_sweep.csv"
    lams = np.linspace(0.0, 1.0, 5)
    written = run(
        lams=lams,
        utilities=[0.0, 1.0, 2.0],
        lam_c1=float(H.PHASE_LAMBDA_C1),
        lam_c2=float(H.PHASE_LAMBDA_C2),
        schmidt_atol=float(H.SPECTRAL_RANK_ATOL),
        output_path=out,
    )
    assert written == out
    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 5
    assert {"lambda", "mi_closed_form", "mi_empirical", "phase"} <= set(rows[0])
    assert "free_energy_u0" in rows[0]
    assert "free_energy_u1" in rows[0]
    assert "free_energy_u2" in rows[0]
    for row in rows:
        mi_c = float(row["mi_closed_form"])
        mi_e = float(row["mi_empirical"])
        assert abs(mi_c - mi_e) <= float(H.PARAMETER_SWEEP_AGREEMENT_TOLERANCE) + 1e-12


def test_parameter_sweep_run_includes_entanglement_entropy_column(tmp_path: Path) -> None:
    out = tmp_path / "parameter_sweep.csv"
    run(
        lams=[0.0, 2.0],
        utilities=[0.5],
        lam_c1=float(H.PHASE_LAMBDA_C1),
        lam_c2=float(H.PHASE_LAMBDA_C2),
        schmidt_atol=float(H.SPECTRAL_RANK_ATOL),
        output_path=out,
    )
    with out.open(newline="", encoding="utf-8") as fh:
        row = next(csv.DictReader(fh))
    assert float(row["entanglement_entropy"]) >= 0.0
    assert row["phase"] in {"disordered", "mixed", "frozen"}
