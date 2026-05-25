"""Tests for visualizations.pymdp_extras.

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
from simulation.statistics import pymdp_summary_statistics
from visualizations.pymdp_extras import (
    _save,
    _shannon,
    plot_action_entropy_curve,
    plot_kl_to_lambda_zero,
    plot_marginal_entropy_per_stream,
    plot_pymdp_summary_panel,
)

# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


def _make_bundle(
    lam: float,
    tc: float = 0.0,
    vfe: float = 0.0,
    coup: float = 0.0,
) -> FreeEnergyBundle:
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
def bundles_6() -> list[FreeEnergyBundle]:
    return [_make_bundle(float(i), tc=i * 0.1, vfe=0.5 - i * 0.04, coup=i * 0.07) for i in range(6)]


# ---------------------------------------------------------------------------
# _shannon (private, but exposed for coverage)
# ---------------------------------------------------------------------------


def test_shannon_uniform_binary() -> None:
    assert _shannon(np.array([0.5, 0.5])) == pytest.approx(math.log(2), abs=1e-12)


def test_shannon_delta() -> None:
    assert _shannon(np.array([1.0, 0.0])) == pytest.approx(0.0, abs=1e-12)


def test_shannon_multidim() -> None:
    p = np.array([[0.25, 0.25], [0.25, 0.25]])
    assert _shannon(p) == pytest.approx(math.log(4), abs=1e-12)


# ---------------------------------------------------------------------------
# _save (private, but exposed for coverage)
# ---------------------------------------------------------------------------


def test_save_creates_file_and_returns_path(tmp_path) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    out = tmp_path / "test_save.png"
    result = _save(fig, out, metadata=None)
    assert result == out
    assert out.exists()


def test_save_with_metadata(tmp_path) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    out = tmp_path / "test_meta.png"
    result = _save(fig, out, metadata={"key": "val"})
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_action_entropy_curve
# ---------------------------------------------------------------------------


def test_plot_action_entropy_curve_creates_file(tmp_path, bundles_6) -> None:
    out = tmp_path / "action_entropy.png"
    result = plot_action_entropy_curve(bundles_6, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_action_entropy_curve_minimal_two_bundles(tmp_path) -> None:
    bs = [_make_bundle(0.0), _make_bundle(1.0)]
    out = tmp_path / "ae2.png"
    result = plot_action_entropy_curve(bs, out_path=out)
    assert result.exists()


def test_plot_action_entropy_curve_with_metadata(tmp_path, bundles_6) -> None:
    out = tmp_path / "ae_meta.png"
    result = plot_action_entropy_curve(bundles_6, out_path=out, metadata={"src": "test"})
    assert result.exists()


def test_plot_action_entropy_curve_concentrated_dist(tmp_path) -> None:
    def _b(lam: float) -> FreeEnergyBundle:
        d = np.array([0.0, 0.0, 0.0, 1.0]) if lam > 1 else np.array([0.25, 0.25, 0.25, 0.25])
        return FreeEnergyBundle(
            lam=lam,
            vfe_per_stream=np.array([0.0, 0.0]),
            vfe_total=0.0,
            efe_per_stream=(np.array([0.0, 0.0]), np.array([0.0, 0.0])),
            efe_under_posterior=np.array([0.0, 0.0]),
            joint_entropy=0.0,
            marginal_entropies=np.array([0.0, 0.0]),
            total_correlation=0.0,
            coupling_term=0.0,
            action_distribution=d,
        )

    bs = [_b(0.0), _b(2.0), _b(4.0)]
    out = tmp_path / "ae_conc.png"
    result = plot_action_entropy_curve(bs, out_path=out)
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_kl_to_lambda_zero
# ---------------------------------------------------------------------------


def test_plot_kl_to_lambda_zero_creates_file(tmp_path, bundles_6) -> None:
    out = tmp_path / "kl.png"
    result = plot_kl_to_lambda_zero(bundles_6, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_kl_to_lambda_zero_raises_on_empty(tmp_path) -> None:
    with pytest.raises(ValueError, match="at least one bundle"):
        plot_kl_to_lambda_zero([], out_path=tmp_path / "kl_empty.png")


def test_plot_kl_to_lambda_zero_identical_dists(tmp_path) -> None:
    bs = [_make_bundle(float(i)) for i in range(3)]
    out = tmp_path / "kl_ident.png"
    result = plot_kl_to_lambda_zero(bs, out_path=out)
    assert result.exists()


def test_plot_kl_to_lambda_zero_with_metadata(tmp_path, bundles_6) -> None:
    out = tmp_path / "kl_meta.png"
    result = plot_kl_to_lambda_zero(bundles_6, out_path=out, metadata={"src": "test"})
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_marginal_entropy_per_stream
# ---------------------------------------------------------------------------


def test_plot_marginal_entropy_per_stream_creates_file(tmp_path, bundles_6) -> None:
    out = tmp_path / "marg_entropy.png"
    result = plot_marginal_entropy_per_stream(bundles_6, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_marginal_entropy_per_stream_string_path(tmp_path, bundles_6) -> None:
    out = str(tmp_path / "marg_str.png")
    result = plot_marginal_entropy_per_stream(bundles_6, out_path=out)
    assert result.exists()


def test_plot_marginal_entropy_per_stream_with_metadata(tmp_path, bundles_6) -> None:
    out = tmp_path / "marg_meta.png"
    result = plot_marginal_entropy_per_stream(bundles_6, out_path=out, metadata={"src": "test"})
    assert result.exists()


# ---------------------------------------------------------------------------
# plot_pymdp_summary_panel
# ---------------------------------------------------------------------------


def test_plot_pymdp_summary_panel_creates_file(tmp_path, bundles_6) -> None:
    out = tmp_path / "summary.png"
    result = plot_pymdp_summary_panel(bundles_6, out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_pymdp_summary_panel_with_summary(tmp_path, bundles_6) -> None:
    summary = pymdp_summary_statistics(bundles_6)
    out = tmp_path / "summary_w_stats.png"
    result = plot_pymdp_summary_panel(bundles_6, out_path=out, summary=summary)
    assert result.exists()


def test_plot_pymdp_summary_panel_summary_none(tmp_path, bundles_6) -> None:
    out = tmp_path / "summary_none.png"
    result = plot_pymdp_summary_panel(bundles_6, out_path=out, summary=None)
    assert result.exists()


def test_plot_pymdp_summary_panel_with_metadata(tmp_path, bundles_6) -> None:
    out = tmp_path / "summary_meta.png"
    result = plot_pymdp_summary_panel(
        bundles_6,
        out_path=out,
        metadata={"project.source_script": "test.py"},
    )
    assert result.exists()


def test_plot_pymdp_summary_panel_nonk2_dist(tmp_path) -> None:
    def _b8(lam: float) -> FreeEnergyBundle:
        return FreeEnergyBundle(
            lam=lam,
            vfe_per_stream=np.array([0.0, 0.0, 0.0]),
            vfe_total=0.0,
            efe_per_stream=(np.zeros(2), np.zeros(2), np.zeros(2)),
            efe_under_posterior=np.zeros(3),
            joint_entropy=math.log(8),
            marginal_entropies=np.array([math.log(2), math.log(2), math.log(2)]),
            total_correlation=0.0,
            coupling_term=0.0,
            action_distribution=np.ones(8) / 8.0,
        )

    bs = [_b8(float(i)) for i in range(4)]
    out = tmp_path / "summary_k3.png"
    result = plot_pymdp_summary_panel(bs, out_path=out)
    assert result.exists()
