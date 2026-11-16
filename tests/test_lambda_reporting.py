"""Numerical reporting regressions using real Gibbs PMFs and temporary artifacts.

No stored scientific outputs or pymdp runtime are needed for these cases.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from lean.coupling import entangled_posterior
from lean.decomposition import entanglement_decomposition_rhs, free_energy_against_entangled_prior
from lean.free_energy import shannon_entropy, total_correlation
from lean.joint_dist import joint_marginals
from lean.spectral import tensor_train_ranks
from manuscript.output_gates import pymdp_validators
from simulation import hyperparameters as H
from simulation.hyperparameters_grids import FigureGrid
from simulation.inference import FreeEnergyBundle
from simulation.multi_k_experiments import MultiKResult
from simulation.multi_k_pipeline import write_multi_k_csv
from simulation.statistics import kl_to_lambda_zero_curve, pymdp_summary_statistics
from tests.output_gates_helpers import patch_output_dir
from visualizations.free_energy_plots import plot_action_distribution_evolution
from visualizations.pymdp_extras import plot_kl_to_lambda_zero, plot_pymdp_summary_panel


def _bundle(lam: float, interaction: np.ndarray) -> FreeEnergyBundle:
    k = interaction.ndim
    priors = [np.full(2, 0.5) for _ in range(k)]
    costs = [np.zeros(2) for _ in range(k)]
    q = entangled_posterior(priors, costs, interaction, np.zeros_like(interaction), gamma=1.0, lam=lam)
    marginals = joint_marginals(q)
    vfe = np.array([np.sum(m * np.log(m / 0.5)) for m in marginals])
    return FreeEnergyBundle(
        lam=lam,
        vfe_per_stream=vfe,
        vfe_total=float(vfe.sum()),
        efe_per_stream=tuple(costs),
        efe_under_posterior=np.zeros(k),
        joint_entropy=shannon_entropy(q),
        marginal_entropies=np.array([shannon_entropy(m) for m in marginals]),
        total_correlation=total_correlation(q),
        coupling_term=float(lam * np.sum(q * interaction)),
        action_distribution=q.reshape(-1),
    )


def _corner_interaction(k: int, strength: float = 1.0) -> np.ndarray:
    interaction = np.zeros((2,) * k)
    interaction[(0,) * k] = interaction[(1,) * k] = strength
    return interaction


def _free_energy_row(bundle: FreeEnergyBundle, interaction: np.ndarray) -> dict[str, str]:
    q = bundle.action_distribution.reshape(interaction.shape)
    priors = [np.full(2, 0.5) for _ in range(interaction.ndim)]
    costs = list(bundle.efe_per_stream)
    kc = np.zeros_like(interaction)
    lhs = free_energy_against_entangled_prior(q, priors, costs, interaction, kc, gamma=1.0, lam=bundle.lam)
    terms = entanglement_decomposition_rhs(q, priors, costs, interaction, kc, gamma=1.0, lam=bundle.lam)
    rhs = (terms.sum_marginal_free_energies + terms.coupling_cost_term
           + terms.coupling_prior_term + terms.total_correlation_gain)
    return {
        "lambda": repr(float(bundle.lam)),
        "vfe_total": repr(float(bundle.vfe_total)),
        "joint_entropy": repr(float(bundle.joint_entropy)),
        "marginal_entropy_sum": repr(float(bundle.marginal_entropies.sum())),
        "total_correlation": repr(float(bundle.total_correlation)),
        "coupling_term": repr(float(bundle.coupling_term)),
        "decomposition_lhs": repr(float(lhs)),
        "decomposition_rhs": repr(float(rhs)),
        "decomposition_residual": repr(float(abs(lhs - rhs))),
    }


def _multi_k_row(bundle: FreeEnergyBundle, k: int) -> MultiKResult:
    q = bundle.action_distribution.reshape((2,) * k)
    return MultiKResult(
        K=k, lam=bundle.lam, total_correlation=bundle.total_correlation,
        marginal_entropies=tuple(float(h) for h in bundle.marginal_entropies),
        joint_entropy=bundle.joint_entropy, coupling_term=bundle.coupling_term,
        tt_ranks=tuple(int(rank) for rank in tensor_train_ranks(q, atol=float(H.SPECTRAL_RANK_ATOL))),
        aligned_mass=float(q[(0,) * k] + q[(1,) * k]),
    )


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _png_statistics(path: Path) -> dict:
    with Image.open(path) as image:
        assert image.format == "PNG"
        statistics = json.loads(image.info["project.figure_statistics"])
        image.verify()
    return statistics


@pytest.mark.parametrize("k", [2, 3, 4, 6])
@pytest.mark.parametrize("endpoints", [(2.0, 1.0), (2.0, 0.0), (2e-8, 1e-8)])
def test_csv_gates_accept_requested_order_and_only_check_exact_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, k: int, endpoints: tuple[float, float]
) -> None:
    grid = FigureGrid(*endpoints, 2)
    monkeypatch.setattr(H, "PYMDP_SWEEP_LAMBDAS", grid)
    monkeypatch.setattr(H, "MULTI_K_SWEEP_LAMBDAS", grid)
    monkeypatch.setattr(H, "MULTI_K_VALUES", (k,))
    out = patch_output_dir(monkeypatch, tmp_path)
    sim = out / "simulations"
    sim.mkdir(parents=True)
    interaction = _corner_interaction(k, 1e8 if max(endpoints) < 1e-6 else 1.0)
    bundles = [_bundle(float(lam), interaction) for lam in grid.values()]
    free_path = sim / "pymdp_free_energy_bundle.csv"
    _write_rows(free_path, [_free_energy_row(bundle, interaction) for bundle in bundles])
    multi_path = write_multi_k_csv(sim, k, [_multi_k_row(bundle, k) for bundle in bundles])
    assert pymdp_validators.validate_free_energy_bundle() == 0
    assert pymdp_validators.validate_multi_k_sweep() == 0
    for path in (free_path, multi_path):
        with path.open(newline="", encoding="utf-8") as stream:
            actual = [float(row["lambda"]) for row in csv.DictReader(stream)]
        assert actual == list(grid.values())
    if min(endpoints) > 0:
        assert all(bundle.total_correlation > 0.0 for bundle in bundles)


@pytest.mark.parametrize("column", ["total_correlation", "coupling_term", "marginal_entropy_sum"])
def test_actual_zero_row_corruption_still_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, column: str
) -> None:
    grid = FigureGrid(1.0, 0.0, 2)
    monkeypatch.setattr(H, "PYMDP_SWEEP_LAMBDAS", grid)
    monkeypatch.setattr(H, "MULTI_K_SWEEP_LAMBDAS", grid)
    monkeypatch.setattr(H, "MULTI_K_VALUES", (3,))
    out = patch_output_dir(monkeypatch, tmp_path)
    sim = out / "simulations"
    sim.mkdir(parents=True)
    interaction = _corner_interaction(3)
    bundles = [_bundle(float(lam), interaction) for lam in grid.values()]
    free_rows = [_free_energy_row(bundle, interaction) for bundle in bundles]
    free_path = sim / "pymdp_free_energy_bundle.csv"
    multi_path = write_multi_k_csv(sim, 3, [_multi_k_row(bundle, 3) for bundle in bundles])
    with multi_path.open(newline="", encoding="utf-8") as stream:
        multi_rows = list(csv.DictReader(stream))
    _write_rows(free_path, free_rows)
    assert pymdp_validators.validate_free_energy_bundle() == 0
    assert pymdp_validators.validate_multi_k_sweep() == 0
    for rows in (free_rows, multi_rows):
        zero = next(row for row in rows if float(row["lambda"]) == 0.0)
        zero[column] = repr(float(zero[column]) + 0.5)
        if column == "total_correlation":
            # Keep the H-gap identity intact: the zero-TC contract must still reject it.
            zero["joint_entropy"] = repr(float(zero["joint_entropy"]) - 0.5)
    _write_rows(free_path, free_rows)
    _write_rows(multi_path, multi_rows)
    assert pymdp_validators.validate_free_energy_bundle() > 0
    assert pymdp_validators.validate_multi_k_sweep() > 0


@pytest.mark.parametrize("k", [2, 3, 4, 6])
def test_pngs_report_positive_only_kl_and_all_binary_corner_masses(tmp_path: Path, k: int) -> None:
    interaction = _corner_interaction(k)
    reference = _bundle(0.0, interaction)
    bundles = [_bundle(float(lam), interaction) for lam in (np.log(9.0), np.log(3.0))]
    expected_kl = kl_to_lambda_zero_curve(bundles, zero_reference=reference)
    summary = pymdp_summary_statistics(bundles, zero_reference=reference)
    kl_png = plot_kl_to_lambda_zero(bundles, zero_reference=reference, out_path=tmp_path / "kl.png")
    panel_png = plot_pymdp_summary_panel(
        bundles, zero_reference=reference, summary=summary, out_path=tmp_path / "panel.png"
    )
    standalone = _png_statistics(kl_png)["axes"][0]["lines"][0]["y"]
    panels = _png_statistics(panel_png)["axes"]
    dashboard = panels[3]["lines"][0]["y"]
    for curve in (standalone, dashboard):
        assert curve["finite_count"] == 2
        assert curve["min"] == pytest.approx(float(expected_kl.min()))
        assert curve["max"] == pytest.approx(float(expected_kl.max()))
        assert curve["min"] > 0.0
    aligned = panels[5]["lines"][0]["y"]
    expected_aligned = [float(bundle.action_distribution[0] + bundle.action_distribution[-1]) for bundle in bundles]
    assert aligned["finite_count"] == 2
    assert aligned["min"] == pytest.approx(min(expected_aligned))
    assert aligned["max"] == pytest.approx(max(expected_aligned))
    uniform = panels[5]["lines"][1]["y"]
    assert uniform["min"] == pytest.approx(2.0 / 2**k)
    assert uniform["max"] == pytest.approx(2.0 / 2**k)


@pytest.mark.parametrize("k", [3, 4, 6])
def test_higher_order_dependence_is_not_replaced_by_pair_information(tmp_path: Path, k: int) -> None:
    parity = (-1.0) ** np.indices((2,) * k).sum(axis=0)
    interaction = np.log(1.0 + 0.6 * parity)
    reference = _bundle(0.0, interaction)
    bundle = _bundle(1.0, interaction)
    joint = bundle.action_distribution.reshape((2,) * k)
    pair = joint.sum(axis=tuple(range(2, k)))
    np.testing.assert_allclose(pair, 0.25, atol=1e-12)
    assert bundle.total_correlation > 0.0
    path = plot_pymdp_summary_panel(
        [reference, bundle], zero_reference=reference, out_path=tmp_path / "parity.png"
    )
    tc = _png_statistics(path)["axes"][0]["lines"][0]["y"]
    assert tc["max"] == pytest.approx(bundle.total_correlation)


@pytest.mark.parametrize("grid", [[3.0, 1.0], [1.0, 3.0, 0.0, 2.0]])
def test_action_heatmap_uses_requested_row_coordinates(tmp_path: Path, grid: list[float]) -> None:
    bundles = [_bundle(lam, _corner_interaction(2)) for lam in grid]
    path = plot_action_distribution_evolution(bundles, out_path=tmp_path / "actions.png")
    axis = _png_statistics(path)["axes"][0]
    assert axis["ylim"] == pytest.approx([-0.5, len(grid) - 0.5])
    assert axis["images"][0]["array"]["shape"] == [len(grid), 4]
    assert axis["images"][0]["array"]["finite_count"] == len(grid) * 4
