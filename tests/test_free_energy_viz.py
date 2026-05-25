"""Tests for visualizations.free_energy_plots.

All functions are tested headlessly via MPLBACKEND=Agg with synthetic
FreeEnergyBundle objects.  No pymdp installation required.
"""

from __future__ import annotations

import math
import os

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pytest

from simulation.inference import FreeEnergyBundle
from simulation.statistics import quantile_envelope_over_sweeps
from visualizations.free_energy_plots import (
    _lams_array,
    plot_action_distribution_evolution,
    plot_bundle_quantile_envelope,
    plot_efe_under_posterior,
    plot_entropy_decomposition,
    plot_free_energy_panel,
    plot_vfe_decomposition,
)

# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


def _make_bundle(lam: float, tc: float = 0.0, vfe: float = 0.0, coup: float = 0.0) -> FreeEnergyBundle:
    action_dist = np.array([0.25, 0.25, 0.25, 0.25])
    return FreeEnergyBundle(
        lam=lam,
        vfe_per_stream=np.array([vfe / 2.0, vfe / 2.0]),
        vfe_total=vfe,
        efe_per_stream=(np.array([0.1, -0.1]), np.array([-0.1, 0.1])),
        efe_under_posterior=np.array([0.05, -0.05]),
        joint_entropy=math.log(4) - tc,
        marginal_entropies=np.array([math.log(2), math.log(2)]),
        total_correlation=tc,
        coupling_term=coup,
        action_distribution=action_dist,
    )


@pytest.fixture
def bundles_5() -> list[FreeEnergyBundle]:
    return [_make_bundle(float(i), tc=i * 0.1, vfe=0.5 - i * 0.05, coup=i * 0.08) for i in range(5)]


# ---------------------------------------------------------------------------
# _lams_array
# ---------------------------------------------------------------------------


def test_lams_array_extracts_lam_field(bundles_5) -> None:
    lams = _lams_array(bundles_5)
    np.testing.assert_array_equal(lams, [0.0, 1.0, 2.0, 3.0, 4.0])


# ---------------------------------------------------------------------------
# plot_vfe_decomposition
# ---------------------------------------------------------------------------


def test_plot_vfe_decomposition_creates_file(tmp_path, bundles_5) -> None:
    out = tmp_path / "vfe.png"
    result = plot_vfe_decomposition(bundles_5, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_vfe_decomposition_accepts_metadata(tmp_path, bundles_5) -> None:
    out = tmp_path / "vfe_meta.png"
    result = plot_vfe_decomposition(bundles_5, out_path=out, metadata={"key": "val"})
    assert result.exists()


def test_plot_vfe_decomposition_minimal_two_bundles(tmp_path) -> None:
    out = tmp_path / "vfe2.png"
    bs = [_make_bundle(0.0), _make_bundle(1.0)]
    result = plot_vfe_decomposition(bs, out_path=out)
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_efe_under_posterior
# ---------------------------------------------------------------------------


def test_plot_efe_under_posterior_creates_file(tmp_path, bundles_5) -> None:
    out = tmp_path / "efe.png"
    result = plot_efe_under_posterior(bundles_5, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_efe_under_posterior_string_path(tmp_path, bundles_5) -> None:
    out = str(tmp_path / "efe_str.png")
    result = plot_efe_under_posterior(bundles_5, out_path=out)
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_entropy_decomposition
# ---------------------------------------------------------------------------


def test_plot_entropy_decomposition_creates_file(tmp_path, bundles_5) -> None:
    out = tmp_path / "entropy.png"
    result = plot_entropy_decomposition(bundles_5, out_path=out)
    assert result == out
    assert out.exists()


def test_plot_entropy_decomposition_zero_tc(tmp_path) -> None:
    bs = [_make_bundle(float(i), tc=0.0) for i in range(3)]
    out = tmp_path / "entropy_zero.png"
    result = plot_entropy_decomposition(bs, out_path=out)
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_action_distribution_evolution
# ---------------------------------------------------------------------------


def test_plot_action_distribution_evolution_creates_file(tmp_path, bundles_5) -> None:
    out = tmp_path / "action_dist.png"
    result = plot_action_distribution_evolution(bundles_5, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_action_distribution_evolution_concentrated_dist(tmp_path) -> None:
    def _make_concentrated(lam: float) -> FreeEnergyBundle:
        action_dist = np.array([0.49 + lam * 0.1, 0.01, 0.01, 0.49 + lam * 0.1])
        action_dist /= action_dist.sum()
        return FreeEnergyBundle(
            lam=lam,
            vfe_per_stream=np.array([0.0, 0.0]),
            vfe_total=0.0,
            efe_per_stream=(np.array([0.0, 0.0]), np.array([0.0, 0.0])),
            efe_under_posterior=np.array([0.0, 0.0]),
            joint_entropy=0.5,
            marginal_entropies=np.array([0.3, 0.3]),
            total_correlation=0.0,
            coupling_term=0.0,
            action_distribution=action_dist,
        )

    bs = [_make_concentrated(float(i) * 0.2) for i in range(4)]
    out = tmp_path / "conc.png"
    result = plot_action_distribution_evolution(bs, out_path=out)
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_free_energy_panel
# ---------------------------------------------------------------------------


def test_plot_free_energy_panel_creates_file(tmp_path, bundles_5) -> None:
    out = tmp_path / "panel.png"
    result = plot_free_energy_panel(bundles_5, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_free_energy_panel_with_metadata(tmp_path, bundles_5) -> None:
    out = tmp_path / "panel_meta.png"
    result = plot_free_energy_panel(bundles_5, out_path=out, metadata={"src": "test"})
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_bundle_quantile_envelope
# ---------------------------------------------------------------------------


@pytest.fixture
def envelope_fixture() -> object:
    lams = [0.0, 1.0, 2.0, 3.0]
    bundles_a = [_make_bundle(float(l), tc=l * 0.1) for l in lams]
    bundles_b = [_make_bundle(float(l), tc=l * 0.12) for l in lams]
    bundles_c = [_make_bundle(float(l), tc=l * 0.08) for l in lams]
    return quantile_envelope_over_sweeps([bundles_a, bundles_b, bundles_c])


def test_plot_bundle_quantile_envelope_creates_file(tmp_path, envelope_fixture) -> None:
    out = tmp_path / "envelope.png"
    result = plot_bundle_quantile_envelope(envelope_fixture, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_bundle_quantile_envelope_custom_label(tmp_path, envelope_fixture) -> None:
    out = tmp_path / "env_label.png"
    result = plot_bundle_quantile_envelope(
        envelope_fixture,
        out_path=out,
        field_label="Custom Y label",
    )
    assert result.exists()


def test_plot_bundle_quantile_envelope_with_metadata(tmp_path, envelope_fixture) -> None:
    out = tmp_path / "env_meta.png"
    result = plot_bundle_quantile_envelope(
        envelope_fixture,
        out_path=out,
        metadata={"project.source_script": "test.py"},
    )
    assert result.exists()
