"""Integration tests for simulation pipeline modules (pymdp required)."""

from __future__ import annotations

from pathlib import Path

import pytest

from simulation import hyperparameters as H
from simulation.agents import pymdp_available
from simulation.long_horizon_pipeline import figure_metadata_snapshot as lh_meta
from simulation.long_horizon_pipeline import run_long_horizon_pipeline
from simulation.multi_k_experiments import MultiKResult
from simulation.multi_k_pipeline import (
    figure_metadata_snapshot as mk_meta,
)
from simulation.multi_k_pipeline import (
    run_multi_k_pipeline,
    write_multi_k_csv,
)
from simulation.robustness_runner import run_robustness_pipeline

PROJECT = Path(__file__).resolve().parent.parent


@pytest.mark.skipif(not pymdp_available(), reason="pymdp not installed")
def test_long_horizon_pipeline_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(H, "LONG_HORIZON_STEPS", 8, raising=False)
    monkeypatch.setattr(H, "LONG_HORIZON_TAIL_WINDOW", 3, raising=False)
    assert run_long_horizon_pipeline(tmp_path) == 0
    assert (tmp_path / "output" / "simulations" / "pymdp_long_horizon.csv").exists()
    meta = lh_meta(tmp_path, "plot_long_horizon_marginals", rows=1)
    assert meta["project.source_function"] == "plot_long_horizon_marginals"


@pytest.mark.skipif(not pymdp_available(), reason="pymdp not installed")
def test_multi_k_pipeline_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(H, "MULTI_K_VALUES", (2,), raising=False)
    assert run_multi_k_pipeline(tmp_path) == 0
    assert (tmp_path / "output" / "data" / "multi_k_summary.json").exists()
    meta = mk_meta(tmp_path, "plot_multi_k_total_correlation")
    assert "K_values" in meta["project.hyperparameters"]


def test_write_multi_k_csv_round_trip(tmp_path: Path) -> None:
    rows = [
        MultiKResult(
            K=2,
            lam=0.5,
            total_correlation=0.1,
            joint_entropy=1.0,
            marginal_entropies=(0.4, 0.4),
            coupling_term=0.2,
            aligned_mass=0.3,
            tt_ranks=(1, 2),
        )
    ]
    path = write_multi_k_csv(tmp_path, 2, rows)
    text = path.read_text(encoding="utf-8")
    assert "total_correlation" in text
    assert "0.5" in text


@pytest.mark.skipif(not pymdp_available(), reason="pymdp not installed")
def test_robustness_pipeline_full(tmp_path: Path) -> None:
    paths = run_robustness_pipeline(
        fig_dir=tmp_path / "figures",
        sim_dir=tmp_path / "simulations",
        data_dir=tmp_path / "data",
        project_root=tmp_path,
    )
    assert paths
    assert (tmp_path / "data" / "robustness_summary.json").exists()
