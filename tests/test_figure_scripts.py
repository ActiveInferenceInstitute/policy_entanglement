"""Smoke tests for the figure-generation pipeline.

Exercise every `figure_*` function defined in
:mod:`visualizations.analytical_figures` and
:mod:`visualizations.pymdp_figures`, verifying that the emitted PNG is a
real PNG. Tests import the thin :mod:`scripts.generate_figures` and
:mod:`scripts.simulate_pymdp` orchestrators (which re-export each figure
callable) so historical entry points remain wired, but redirect
``OUTPUT_DIR`` / ``FIG_DIR`` / ``SIM_DIR`` on the **src-side** modules —
those are the attributes the figure functions actually read at call time.

These are *integration* tests — they run the actual figure
generation, write to a `tmp_path`, and check on-disk output.  No
mocks.  pymdp-dependent figures skip cleanly when the ``sim`` group
is missing.
"""

from __future__ import annotations

import csv
import importlib
import json
import os
import sys
from pathlib import Path

import pytest

from simulation.agents import pymdp_available  # noqa: E402

os.environ.setdefault("MPLBACKEND", "Agg")

PROJECT = Path(__file__).resolve().parent.parent
SCRIPTS = PROJECT / "scripts"
sys.path.insert(0, str(SCRIPTS))

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _assert_png(path: Path) -> None:
    assert path.exists(), f"missing: {path}"
    assert path.stat().st_size > 0
    with path.open("rb") as fh:
        assert fh.read(8) == PNG_HEADER, f"not a PNG: {path}"


@pytest.fixture(scope="module")
def gen_module(monkeypatch_module_scope=None):
    """Import the thin ``scripts/generate_figures.py`` orchestrator once per module."""
    return importlib.import_module("generate_figures")


@pytest.fixture(autouse=True)
def _redirect_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Each figure_* function writes to its module's OUTPUT_DIR. The
    business logic lives in ``visualizations.analytical_figures``; redirect
    that attribute (and the script-side mirror) to ``tmp_path`` so tests
    don't litter ``output/figures/``.
    """
    analytical = importlib.import_module("visualizations.analytical_figures")
    monkeypatch.setattr(analytical, "OUTPUT_DIR", tmp_path, raising=False)
    monkeypatch.setattr("generate_figures.OUTPUT_DIR", tmp_path, raising=False)
    yield


@pytest.mark.parametrize(
    "fn_name",
    [
        "figure_ising_mi_curve",
        "figure_free_energy_curve",
        "figure_coupling_tax_quadratic",
        "figure_phase_diagram",
        "figure_optimal_lambda",
        "figure_schmidt_rank_vs_lambda",
        "figure_phase_landscape",
        "figure_schmidt_entropy_surface",
        "figure_joint_heatmap_with_marginals",
        "figure_archetype_dendrogram",
        "figure_tensor_train_ranks",
        "figure_log_weight_flow",
        "figure_kl_geodesic_in_simplex",
        "figure_lambda_star_locus",
    ],
)
def test_figure_function_emits_png(gen_module, fn_name: str) -> None:
    fn = getattr(gen_module, fn_name)
    out = fn()
    _assert_png(out)


def test_figure_coupling_graph_when_networkx_present(gen_module) -> None:
    from visualizations.graphs import has_networkx  # noqa: WPS433

    if not has_networkx():
        pytest.skip("networkx not installed")
    out = gen_module.figure_coupling_graph()
    assert out is not None
    _assert_png(out)


# ---------------------------------------------------------------------------
# pymdp-script smoke tests (skip when sim group missing)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def sim_module():
    if not pymdp_available():
        pytest.skip("pymdp/JAX runtime unavailable (uv sync --group sim)")
    return importlib.import_module("simulate_pymdp")


@pytest.fixture
def _redirect_pymdp_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Redirect the pymdp figure outputs to ``tmp_path``.

    ``visualizations.pymdp_figures`` is the source of truth (the figure
    functions read ``FIG_DIR`` / ``SIM_DIR`` from their defining module);
    the script-side mirrors are patched as well so test code that asserts
    against the script namespace remains accurate.
    """
    pymdp_module = importlib.import_module("visualizations.pymdp_figures")
    monkeypatch.setattr(pymdp_module, "FIG_DIR", tmp_path, raising=False)
    monkeypatch.setattr(pymdp_module, "SIM_DIR", tmp_path, raising=False)
    monkeypatch.setattr("simulate_pymdp.FIG_DIR", tmp_path, raising=False)
    monkeypatch.setattr("simulate_pymdp.SIM_DIR", tmp_path, raising=False)
    logger = pymdp_module.default_logger(tmp_path)
    monkeypatch.setattr(pymdp_module, "LOGGER", logger)
    monkeypatch.setattr("simulate_pymdp.LOGGER", logger)


def test_pymdp_lambda_sweep_writes_csv_and_pngs(sim_module, _redirect_pymdp_outputs) -> None:
    csv_path, curve_path = sim_module.figure_pymdp_lambda_sweep()
    assert csv_path.suffix == ".csv"
    assert csv_path.exists()
    _assert_png(curve_path)


def test_pymdp_rollout_writes_png(sim_module, _redirect_pymdp_outputs) -> None:
    out = sim_module.figure_pymdp_rollout()
    _assert_png(out)


def test_pymdp_free_energies_writes_csv_json_and_pngs(sim_module, _redirect_pymdp_outputs) -> None:
    out = sim_module.figure_pymdp_free_energies()
    assert len(out) == 11
    csv_path, summary_path, *png_paths = out
    assert csv_path.suffix == ".csv"
    assert csv_path.exists() and csv_path.stat().st_size > 0
    assert summary_path.suffix == ".json"
    assert summary_path.exists() and summary_path.stat().st_size > 0
    for p in png_paths:
        _assert_png(p)


@pytest.mark.requires_pymdp
@pytest.mark.parametrize("k", [2, 3, 4, 6])
@pytest.mark.parametrize("endpoints", [(3.0, 1.0), (2e-8, 1e-8)])
def test_pymdp_pipeline_custom_grids_keep_zero_reference_and_k_dimensional_information(
    sim_module, _redirect_pymdp_outputs, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    k: int, endpoints: tuple[float, float],
) -> None:
    from PIL import Image

    from manuscript.variables_sidecars import pymdp_facts
    from simulation import hyperparameters as H
    from simulation.builders import make_ising_ensemble
    from simulation.hyperparameters_grids import FigureGrid
    from simulation.inference import free_energy_bundle, free_energy_curve
    from simulation.statistics import kl_to_lambda_zero_curve, pymdp_summary_statistics, summary_to_var_dict
    from simulation.sweep import lambda_sweep

    grid = FigureGrid(*endpoints, 2)
    strength = 1e8 if max(endpoints) < 1e-6 else 1.0
    monkeypatch.setattr(H, "PYMDP_ENSEMBLE_K", k)
    monkeypatch.setattr(H, "PYMDP_ENSEMBLE_GAMMA", 1.0)
    monkeypatch.setattr(H, "PYMDP_ENSEMBLE_COUPLING_LAMBDA", strength)
    monkeypatch.setattr(H, "PYMDP_SWEEP_OBSERVATIONS", (0,) * k)
    monkeypatch.setattr(H, "PYMDP_SWEEP_LAMBDAS", grid)
    monkeypatch.setattr(H, "PYMDP_ROLLOUT_STEPS", 2)
    sweep_csv, tc_png = sim_module.figure_pymdp_lambda_sweep()
    free_csv, summary_path, *_ = sim_module.figure_pymdp_free_energies()
    _assert_png(sim_module.figure_pymdp_rollout())
    for path in (sweep_csv, free_csv):
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        assert [float(row["lambda"]) for row in rows] == list(grid.values())
        assert all(float(row["lambda"]) > 0.0 for row in rows)

    spec = make_ising_ensemble(num_streams=k, coupling_amplitude=strength, gamma=1.0)
    reference = free_energy_bundle(spec, [0] * k, lam=0.0)
    bundles = free_energy_curve(spec, [0] * k, grid.values())
    expected = summary_to_var_dict(pymdp_summary_statistics(bundles, zero_reference=reference))
    actual = json.loads(summary_path.read_text(encoding="utf-8"))
    facts = pymdp_facts()
    for key, value in expected.items():
        assert actual[key] == pytest.approx(value, abs=1e-8)
        assert facts[key] == pytest.approx(value, abs=1e-8)
    assert facts["pymdp_coupling_term_at_lambda_zero"] == pytest.approx(0.0, abs=1e-12)
    assert facts["pymdp_joint_entropy_at_lambda_zero"] == pytest.approx(reference.joint_entropy)
    assert facts["pymdp_marginal_entropy_sum_at_lambda_zero"] == pytest.approx(reference.marginal_entropies.sum())
    expected_kl = kl_to_lambda_zero_curve(bundles, zero_reference=reference)
    assert float(expected_kl.min()) > 0.0
    with Image.open(tmp_path / "pymdp_kl_to_lambda_zero.png") as image:
        curve = json.loads(image.info["project.figure_statistics"])["axes"][0]["lines"][0]["y"]
        assert curve["min"] == pytest.approx(float(expected_kl.min()), abs=1e-8)
    with Image.open(tc_png) as image:
        stats = json.loads(image.info["project.figure_statistics"])
        assert f"K={k}" in stats["axes"][0]["title"]
        assert stats["axes"][0]["lines"][0]["y"]["max"] == pytest.approx(
            max(bundle.total_correlation for bundle in bundles), abs=1e-8
        )
        assert json.loads(image.info["project.hyperparameters"])["sweep_lambda_max"] == max(endpoints)
    snapshots = list(tmp_path.glob("pymdp_joint_lambda_*.png"))
    assert len(snapshots) == 2
    by_lambda = {row.lam: row.joint for row in lambda_sweep(spec, [0] * k, grid.values())}
    for path in snapshots:
        with Image.open(path) as image:
            lam = float(image.info["project.panel"].removeprefix("joint_lambda_"))
            assert json.loads(image.info["project.source_joint_shape"]) == [2] * k
            assert json.loads(image.info["project.joint_projection_streams"]) == [0, 1]
            statistics = json.loads(image.info["project.figure_statistics"])
        axis = next(axis for axis in statistics["axes"] if axis["xlabel"] == "Stream 1 policy index")
        q = by_lambda[lam]
        pair = q if k == 2 else q.sum(axis=tuple(range(2, k)))
        rendered = axis["images"][0]["array"]
        assert rendered["shape"] == [2, 2]
        assert rendered["min"] == pytest.approx(float(pair.min()), abs=1e-8)
        assert rendered["max"] == pytest.approx(float(pair.max()), abs=1e-8)
        if k > 2:
            titles = [axis["title"] for axis in statistics["axes"]]
            titles.extend(text["text"] for text in statistics["figure_texts"])
            assert any("marginal" in title for title in titles)
    if max(endpoints) < 1e-6:
        assert not (tmp_path / "pymdp_joint_lambda_0.00.png").exists()
