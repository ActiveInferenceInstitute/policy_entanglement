"""Integration tests for simulation pipeline modules (pymdp required)."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
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


@pytest.mark.parametrize("scalar_type", [float, np.float64])
def test_write_multi_k_csv_round_trip(tmp_path: Path, scalar_type) -> None:
    """Uniform independent ensembles retain even tiny positive probe lambdas."""
    lams = [scalar_type(1e-8), scalar_type(2e-8)]
    rows = [
        MultiKResult(
            K=2,
            lam=lam,
            total_correlation=0.0,
            joint_entropy=2.0 * math.log(2.0),
            marginal_entropies=(math.log(2.0), math.log(2.0)),
            coupling_term=0.0,
            aligned_mass=0.5,
            tt_ranks=(1,),
        )
        for lam in lams
    ]
    path = write_multi_k_csv(tmp_path, 2, rows)
    with path.open(newline="", encoding="utf-8") as stream:
        actual = list(csv.DictReader(stream))
    assert [float(row["lambda"]) for row in actual] == [float(lam) for lam in lams]
    assert all(float(row["lambda"]) > 0.0 for row in actual)
    for row in actual:
        assert float(row["marginal_entropy_sum"]) == pytest.approx(float(row["joint_entropy"]))
        assert float(row["aligned_mass"]) == 0.5
        assert row["tt_ranks"] == "1"


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


@pytest.mark.requires_pymdp
@pytest.mark.skipif(not pymdp_available(), reason="pymdp/JAX runtime unavailable (uv sync --group sim)")
@pytest.mark.parametrize("k", [2, 3, 4, 6])
@pytest.mark.parametrize("endpoints", [(3.0, 1.0), (2.0, 0.0)])
@pytest.mark.parametrize("sentinel_lambda", [2.0, 2.5])
def test_multi_k_pipeline_binds_zero_sentinel_and_max_lambda(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, k: int,
    endpoints: tuple[float, float], sentinel_lambda: float,
) -> None:
    from PIL import Image

    from simulation.hyperparameters_grids import FigureGrid
    from simulation.multi_k_experiments import run_multi_k_sweep

    grid = FigureGrid(*endpoints, 2)
    monkeypatch.setattr(H, "MULTI_K_VALUES", (k,))
    monkeypatch.setattr(H, "MULTI_K_SWEEP_LAMBDAS", grid)
    monkeypatch.setattr(H, "MULTI_K_SENTINEL_LAMBDA", sentinel_lambda)
    monkeypatch.setattr(H, "PYMDP_ENSEMBLE_COUPLING_LAMBDA", 1.0)
    monkeypatch.setattr(H, "PYMDP_ENSEMBLE_GAMMA", 1.0)
    assert run_multi_k_pipeline(tmp_path) == 0
    summary = json.loads((tmp_path / "output/data/multi_k_summary.json").read_text(encoding="utf-8"))
    expected = run_multi_k_sweep(
        k, [0.0, sentinel_lambda, max(endpoints)], coupling_lambda_gen=1.0, gamma=1.0,
    )
    zero, sentinel, endpoint = expected
    prefix = f"multi_k_K{k}_"
    assert summary[prefix + "lambda_min"] == min(endpoints)
    assert summary[prefix + "lambda_max"] == max(endpoints)
    assert summary[prefix + "aligned_mass_at_lambda_zero"] == pytest.approx(zero.aligned_mass)
    assert summary[prefix + "aligned_mass_at_lambda_max"] == pytest.approx(endpoint.aligned_mass)
    assert summary[prefix + "tc_at_lambda_max"] == pytest.approx(endpoint.total_correlation)
    assert summary[prefix + "tt_rank_max_at_lambda_max"] == max(endpoint.tt_ranks)
    assert summary[f"multi_information_K{k}_sentinel"] == pytest.approx(sentinel.total_correlation, abs=1e-10)
    with (tmp_path / f"output/simulations/pymdp_K{k}_sweep.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert [float(row["lambda"]) for row in rows] == list(grid.values())
    if min(endpoints) > 0:
        assert summary[prefix + "aligned_mass_at_lambda_zero"] < min(float(row["aligned_mass"]) for row in rows)
        assert abs(summary[f"multi_information_K{k}_sentinel"] - float(rows[-1]["total_correlation"])) > 1e-6
    with Image.open(tmp_path / "output/figures/multi_k_tt_rank_profile.png") as image:
        stats = json.loads(image.info["project.figure_statistics"])
        metadata = json.loads(image.info["project.hyperparameters"])
    line = stats["axes"][0]["lines"][0]
    assert line["label"] == f"K={k}, λ={max(endpoints):g}"
    assert line["y"]["min"] == min(endpoint.tt_ranks)
    assert line["y"]["max"] == max(endpoint.tt_ranks)
    assert metadata["sweep_lambda_max"] == max(endpoints)
    projected = H.figure_hyperparameter_summary()
    assert projected["multi_k_sweep_lambda_min"] == min(endpoints)
    assert projected["multi_k_sweep_lambda_max"] == max(endpoints)
