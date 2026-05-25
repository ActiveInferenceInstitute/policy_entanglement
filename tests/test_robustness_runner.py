"""Tests for :mod:`simulation.robustness_runner` serialisation and pipeline glue."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from simulation.agents import pymdp_available
from simulation.robustness import run_robustness_suite
from simulation.robustness_emit import (
    figure_metadata_dict,
    snapshot,
    write_ablation_csv,
    write_marginal_null_control_csv,
    write_robustness_csv,
)
from simulation.robustness_runner import run_robustness_pipeline


def test_snapshot_and_metadata_helpers() -> None:
    snap = snapshot()
    assert "K" in snap
    assert "robustness_interaction_families" in snap
    meta = figure_metadata_dict("plot_robustness_tc_envelopes", statistics={"rows": 1})
    assert meta["project.source_function"] == "plot_robustness_tc_envelopes"
    assert "project.hyperparameters" in meta


@pytest.mark.skipif(not pymdp_available(), reason="pymdp 1.0.1 not installed")
def test_write_robustness_csv_round_trip(tmp_path: Path) -> None:
    rows = run_robustness_suite([0.0, 1.0])
    path = write_robustness_csv(rows, tmp_path)
    assert path.exists()
    with path.open(newline="", encoding="utf-8") as fh:
        got = list(csv.DictReader(fh))
    assert len(got) == len(rows)
    assert got[0]["scenario_id"] == rows[0].scenario_id


@pytest.mark.skipif(not pymdp_available(), reason="pymdp 1.0.1 not installed")
def test_write_ablation_and_null_control_csv(tmp_path: Path) -> None:
    from simulation.robustness import run_coupling_ablation, run_marginal_null_control

    ablation_rows = run_coupling_ablation([0.0, 1.0])
    null_rows = run_marginal_null_control([0.0, 1.0])
    ablation_path = write_ablation_csv(ablation_rows, tmp_path)
    null_path = write_marginal_null_control_csv(null_rows, tmp_path)
    assert ablation_path.exists() and null_path.exists()
    with ablation_path.open(newline="", encoding="utf-8") as fh:
        assert len(list(csv.DictReader(fh))) == len(ablation_rows)
    with null_path.open(newline="", encoding="utf-8") as fh:
        assert len(list(csv.DictReader(fh))) == len(null_rows)


def test_run_robustness_pipeline_noop_without_pymdp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("simulation.robustness_runner.pymdp_available", lambda: False)
    assert (
        run_robustness_pipeline(
            fig_dir=tmp_path / "figures",
            sim_dir=tmp_path / "simulations",
            data_dir=tmp_path / "data",
        )
        == []
    )
