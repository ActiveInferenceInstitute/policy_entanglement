"""Tests for the pymdp-grounded free-energy visualization helpers.

Each plot is exercised on a real ``free_energy_curve`` output and
asserts:

* the PNG header on disk (smoke check),
* the in-memory ``Figure`` object's structure (axis labels, line
  count, legend text) — ensures visual regressions are caught
  before they reach the manuscript.

No mocks; pymdp must be installed or the suite skips entirely.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from simulation.agents import pymdp_available

if not pymdp_available():
    pytestmark = pytest.mark.skip(reason="pymdp 1.0.1 not installed")

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt

from simulation.builders import make_ising_ensemble
from simulation.inference import free_energy_curve
from simulation.statistics import quantile_envelope_over_sweeps
from visualizations.free_energy_plots import (
    plot_action_distribution_evolution,
    plot_bundle_quantile_envelope,
    plot_efe_under_posterior,
    plot_entropy_decomposition,
    plot_free_energy_panel,
    plot_vfe_decomposition,
)

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _assert_png(p: Path) -> None:
    assert p.exists()
    assert p.stat().st_size > 0
    with p.open("rb") as fh:
        assert fh.read(8) == PNG_HEADER


@pytest.fixture
def captured_figures(monkeypatch: pytest.MonkeyPatch) -> list[plt.Figure]:
    """Stop the plot helpers from closing their figures so we can inspect.

    The free_energy_plots helpers call ``plt.close(fig)`` after saving.
    We replace ``plt.close`` (and the matching ``Figure.clear`` /
    ``Figure.close`` paths) with a capturing no-op for the test's
    lifetime; the test then reads structure off the captured Figure.
    """
    captured: list[plt.Figure] = []

    def _capture(arg=None) -> None:
        if isinstance(arg, plt.Figure):
            captured.append(arg)
        elif arg is None:
            captured.append(plt.gcf())

    plt.close("all")
    monkeypatch.setattr(plt, "close", _capture)
    return captured


@pytest.fixture(scope="module")
def bundles():
    spec = make_ising_ensemble(num_streams=2, gamma=1.0, coupling_amplitude=1.0)
    lams = np.linspace(0.0, 3.0, 9)
    return free_energy_curve(spec, [0, 0], lams)


def test_plot_vfe_decomposition_emits_png(bundles, tmp_path: Path) -> None:
    p = plot_vfe_decomposition(bundles, out_path=tmp_path / "vfe.png")
    _assert_png(p)


def test_plot_vfe_decomposition_axes_are_labelled(bundles, tmp_path: Path, captured_figures: list[plt.Figure]) -> None:
    plot_vfe_decomposition(bundles, out_path=tmp_path / "vfe.png")
    assert captured_figures, "plot helper did not produce a figure"
    fig = captured_figures[-1]
    axes = fig.get_axes()
    # Two stacked panels: per-stream VFE and total / coupling / TC.
    assert len(axes) == 2
    ax1, ax2 = axes
    assert "VFE" in ax1.get_ylabel() or "free" in ax1.get_ylabel().lower()
    assert ax2.get_xlabel() != ""
    # Bottom panel must contain three labeled lines (total, λ·⟨J⟩, I).
    bottom_lines = ax2.get_lines()
    assert len(bottom_lines) >= 3
    legend = ax2.get_legend()
    assert legend is not None
    legend_text = " ".join(t.get_text() for t in legend.get_texts())
    assert "lambda" in legend_text.lower() or r"\lambda" in legend_text


def test_plot_efe_under_posterior_emits_png(bundles, tmp_path: Path) -> None:
    p = plot_efe_under_posterior(bundles, out_path=tmp_path / "efe.png")
    _assert_png(p)


def test_plot_efe_under_posterior_has_efe_axis(bundles, tmp_path: Path, captured_figures: list[plt.Figure]) -> None:
    plot_efe_under_posterior(bundles, out_path=tmp_path / "efe.png")
    assert captured_figures
    fig = captured_figures[-1]
    axes = fig.get_axes()
    assert axes, "expected at least one axis"
    # Y-axis labels should reference EFE / g_k / 'nats' (the EFE energy unit).
    ylabels = [ax.get_ylabel().lower() for ax in axes]
    assert any("efe" in y or "expected" in y or "free energy" in y or "g_k" in y or "nats" in y for y in ylabels), (
        ylabels
    )


def test_plot_entropy_decomposition_emits_png(bundles, tmp_path: Path) -> None:
    p = plot_entropy_decomposition(bundles, out_path=tmp_path / "ent.png")
    _assert_png(p)


def test_plot_entropy_decomposition_has_entropy_axis(
    bundles, tmp_path: Path, captured_figures: list[plt.Figure]
) -> None:
    plot_entropy_decomposition(bundles, out_path=tmp_path / "ent.png")
    assert captured_figures
    fig = captured_figures[-1]
    axes = fig.get_axes()
    assert axes, "expected at least one axis"
    # Entropy decomposition must label a y-axis as entropy or H.
    labels = [ax.get_ylabel().lower() for ax in axes]
    assert any("entropy" in y or "h(" in y or "h " in y or y.startswith("h") for y in labels), labels


def test_plot_action_distribution_evolution_emits_png(bundles, tmp_path: Path) -> None:
    p = plot_action_distribution_evolution(bundles, out_path=tmp_path / "act.png")
    _assert_png(p)


def test_plot_action_distribution_has_policy_axis(bundles, tmp_path: Path, captured_figures: list[plt.Figure]) -> None:
    """The action-distribution evolution heatmap shows joint policy index
    on x and λ on y (one row per λ in the bundle), so we assert the
    policy-index axis is correctly labeled.
    """
    plot_action_distribution_evolution(bundles, out_path=tmp_path / "act.png")
    assert captured_figures
    fig = captured_figures[-1]
    axes = fig.get_axes()
    assert axes
    # At least one axis must reference policy / Π / lex / index.
    xlabels = [ax.get_xlabel() for ax in axes]
    ylabels = [ax.get_ylabel() for ax in axes]
    all_labels = " ".join(xlabels + ylabels).lower()
    assert any(token in all_labels for token in ("policy", "lex", "index", r"\pi", "π")), (xlabels, ylabels)


def test_plot_free_energy_panel_emits_png(bundles, tmp_path: Path) -> None:
    p = plot_free_energy_panel(bundles, out_path=tmp_path / "panel.png")
    _assert_png(p)


def test_plot_free_energy_panel_is_multi_axis(bundles, tmp_path: Path, captured_figures: list[plt.Figure]) -> None:
    """The summary panel must compose multiple axes (it is a dashboard)."""
    plot_free_energy_panel(bundles, out_path=tmp_path / "panel.png")
    assert captured_figures
    fig = captured_figures[-1]
    axes = fig.get_axes()
    assert len(axes) >= 3, f"summary panel should have ≥3 sub-axes, got {len(axes)}"


def test_plot_bundle_quantile_envelope_emits_png(bundles, tmp_path: Path) -> None:
    """Smoke test: identical sweeps produce a degenerate envelope but
    the PNG should still render successfully."""
    env = quantile_envelope_over_sweeps([bundles, bundles])
    p = plot_bundle_quantile_envelope(env, out_path=tmp_path / "env.png")
    _assert_png(p)


def test_plot_bundle_quantile_envelope_has_three_layers(
    bundles, tmp_path: Path, captured_figures: list[plt.Figure]
) -> None:
    """The envelope plot must compose:

    * two `fill_between` collections (min/max + quantile band),
    * one median line.

    Verifies the visual contract used in the manuscript dashboards.
    """
    from dataclasses import replace

    perturbed = [replace(b, total_correlation=b.total_correlation * 1.5) for b in bundles]
    env = quantile_envelope_over_sweeps([bundles, perturbed], field="total_correlation")
    plot_bundle_quantile_envelope(env, out_path=tmp_path / "env.png")
    assert captured_figures
    fig = captured_figures[-1]
    axes = fig.get_axes()
    assert len(axes) == 1
    ax = axes[0]
    # PolyCollections from fill_between (band fills).
    assert len(ax.collections) >= 2, ax.collections
    # Median line.
    assert len(ax.get_lines()) >= 1, ax.get_lines()
    # Legend mentions "median".
    legend = ax.get_legend()
    assert legend is not None
    legend_text = " ".join(t.get_text() for t in legend.get_texts())
    assert "median" in legend_text.lower(), legend_text


def test_plots_round_trip_from_disk(bundles, tmp_path: Path) -> None:
    """Each PNG, when re-read as bytes, has the file-format header
    AND a positive image-data section. Catches truncated writes that
    smoke-test header checks would miss.
    """
    paths = [
        plot_vfe_decomposition(bundles, out_path=tmp_path / "vfe.png"),
        plot_efe_under_posterior(bundles, out_path=tmp_path / "efe.png"),
        plot_entropy_decomposition(bundles, out_path=tmp_path / "ent.png"),
        plot_action_distribution_evolution(bundles, out_path=tmp_path / "act.png"),
        plot_free_energy_panel(bundles, out_path=tmp_path / "panel.png"),
    ]
    for p in paths:
        data = p.read_bytes()
        assert data.startswith(PNG_HEADER)
        # PNG IEND chunk marks file termination; a truncated PNG omits it.
        assert b"IEND" in data, f"PNG {p.name} appears truncated (no IEND chunk)"
        # Healthy figures are at least a few KB.
        assert len(data) > 2000, f"PNG {p.name} suspiciously small ({len(data)} bytes)"
