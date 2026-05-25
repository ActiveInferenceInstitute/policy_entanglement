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

import importlib
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
        pytest.skip("pymdp 1.0.1 not installed")
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
