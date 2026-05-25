"""Tests for the visualizations subpackage.

Every helper writes a PNG to a `tmp_path`-rooted directory; we assert
that the file exists, is non-empty, and starts with the canonical PNG
header.  Headless matplotlib is configured at import time.
"""

from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")

from pathlib import Path

import numpy as np
import pytest

from lean.coupling import entangled_posterior
from lean.spectral import schmidt_decomposition
from visualizations.annotations import add_stats_box
from visualizations.graphs import has_networkx, has_seaborn, plot_coupling_graph
from visualizations.heatmaps import plot_lambda_utility_heatmap, plot_schmidt_entropy_surface
from visualizations.joint_plots import plot_joint_heatmap_with_marginals
from visualizations.log_weight import plot_log_weight_flow
from visualizations.setup import PUBLICATION_STYLE, deterministic_setup, ensure_outdir
from visualizations.spectral_plots import plot_archetype_dendrogram, plot_tensor_train_rank_surface
from visualizations.trajectory_plots import plot_rollout_marginals

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _assert_png(path: Path) -> None:
    assert path.exists(), f"missing: {path}"
    assert path.stat().st_size > 0, f"empty: {path}"
    with path.open("rb") as fh:
        assert fh.read(8) == PNG_HEADER


# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------


def test_deterministic_setup_runs_without_error() -> None:
    deterministic_setup(seed=123)


def test_publication_style_exposes_stable_sizes() -> None:
    assert PUBLICATION_STYLE.single[0] >= 7.0
    assert PUBLICATION_STYLE.title_size >= 14.0
    assert PUBLICATION_STYLE.tick_size >= 12.0
    assert PUBLICATION_STYLE.legend_size >= 10.0
    assert PUBLICATION_STYLE.strip(2)[0] > PUBLICATION_STYLE.single[0]


def test_add_stats_box_accepts_all_documented_input_shapes() -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3)
    add_stats_box(axes[0], {"grid": 3, "residual": 1e-12})
    add_stats_box(axes[1], [("grid", 3), ("residual", 1e-12)])
    add_stats_box(axes[2], ["grid: 3", "residual: 1e-12"])

    texts = [axis.texts[0].get_text() for axis in axes]
    plt.close(fig)

    assert texts[0].splitlines() == ["grid: 3", "residual: 1.00e-12"]
    assert texts[1].splitlines() == ["grid: 3", "residual: 1.00e-12"]
    assert texts[2].splitlines() == ["grid: 3", "residual: 1e-12"]


def test_ensure_outdir_creates_directory(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "output"
    out = ensure_outdir(target)
    assert out.is_dir()
    assert out == target


def test_ensure_outdir_idempotent(tmp_path: Path) -> None:
    target = tmp_path / "twice"
    target.mkdir()
    out = ensure_outdir(target)
    assert out.is_dir()


# ---------------------------------------------------------------------------
# Heatmaps
# ---------------------------------------------------------------------------


def test_plot_lambda_utility_heatmap_writes_png(tmp_path: Path) -> None:
    lams = np.linspace(0.0, 1.0, 5)
    utilities = np.linspace(0.0, 1.0, 4)
    score = np.random.default_rng(0).standard_normal((4, 5))
    out = plot_lambda_utility_heatmap(
        lams=lams,
        utilities=utilities,
        score=score,
        title="t",
        cbar_label="cb",
        out_path=tmp_path / "heat.png",
    )
    _assert_png(out)


def test_plot_schmidt_entropy_surface_writes_png(tmp_path: Path) -> None:
    lams = np.linspace(0.0, 1.0, 5)
    utilities = np.linspace(0.0, 1.0, 4)
    entropies = np.random.default_rng(1).standard_normal((4, 5))
    out = plot_schmidt_entropy_surface(
        lams=lams,
        utilities=utilities,
        entropies=entropies,
        out_path=tmp_path / "schmidt.png",
    )
    _assert_png(out)


# ---------------------------------------------------------------------------
# Joint heatmap with marginals
# ---------------------------------------------------------------------------


def _ising_q(lam: float = 1.0) -> np.ndarray:
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.zeros(2), np.zeros(2)]
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.zeros((2, 2))
    return entangled_posterior(mf, G, J, Kc, gamma=0.0, lam=lam)


def test_plot_joint_heatmap_with_marginals(tmp_path: Path) -> None:
    q = _ising_q(1.5)
    out = plot_joint_heatmap_with_marginals(
        q=q,
        title="K=2 Ising",
        out_path=tmp_path / "joint.png",
        xticklabels=["a", "b"],
        yticklabels=["x", "y"],
    )
    _assert_png(out)


def test_plot_joint_heatmap_with_marginals_rejects_K3() -> None:
    bad = np.zeros((2, 2, 2))
    with pytest.raises(ValueError, match="K=2"):
        plot_joint_heatmap_with_marginals(q=bad, title="t", out_path="/dev/null")


# ---------------------------------------------------------------------------
# Spectral plots
# ---------------------------------------------------------------------------


def test_plot_archetype_dendrogram(tmp_path: Path) -> None:
    q = _ising_q(2.0)
    archs = schmidt_decomposition(q)
    weights = [a.weight for a in archs]
    R = len(archs)
    overlap = np.eye(R)
    out = plot_archetype_dendrogram(
        weights=weights,
        overlap_matrix=overlap,
        out_path=tmp_path / "arch.png",
    )
    _assert_png(out)


def test_plot_tensor_train_rank_surface(tmp_path: Path) -> None:
    out = plot_tensor_train_rank_surface(
        k_values=[2, 3, 4],
        rank_profiles=[[1], [2, 1], [3, 2, 1]],
        out_path=tmp_path / "tt.png",
    )
    _assert_png(out)


# ---------------------------------------------------------------------------
# Trajectory + log-weight plots
# ---------------------------------------------------------------------------


def test_plot_rollout_marginals(tmp_path: Path) -> None:
    rng = np.random.default_rng(0)
    margs = [
        rng.dirichlet(np.ones(2), size=5),
        rng.dirichlet(np.ones(2), size=5),
    ]
    tcs = np.array([0.0, 0.1, 0.2, 0.3, 0.25])
    out = plot_rollout_marginals(
        marginals_per_stream=margs,
        titles=["s0", "s1"],
        total_correlations=tcs,
        out_path=tmp_path / "roll.png",
    )
    _assert_png(out)


def test_plot_rollout_marginals_K1(tmp_path: Path) -> None:
    margs = [np.full((4, 2), 0.5)]
    tcs = np.array([0.0, 0.0, 0.0, 0.0])
    out = plot_rollout_marginals(
        marginals_per_stream=margs,
        titles=["lone"],
        total_correlations=tcs,
        out_path=tmp_path / "roll1.png",
    )
    _assert_png(out)


def test_plot_log_weight_flow(tmp_path: Path) -> None:
    lams = np.linspace(0.0, 2.0, 10)
    log_w = lams[:, None] * np.array([0.5, -0.5, 0.0, 1.0])
    out = plot_log_weight_flow(
        lams=lams,
        log_weights=log_w,
        out_path=tmp_path / "lw.png",
        pi_labels=["(0,0)", "(0,1)", "(1,0)", "(1,1)"],
    )
    _assert_png(out)


def test_plot_log_weight_flow_default_labels(tmp_path: Path) -> None:
    lams = np.linspace(0.0, 1.0, 5)
    log_w = np.zeros((5, 2))
    out = plot_log_weight_flow(lams=lams, log_weights=log_w, out_path=tmp_path / "lw0.png")
    _assert_png(out)


def test_plot_log_weight_flow_rejects_empty_lambda_grid(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        plot_log_weight_flow(
            lams=[],
            log_weights=np.zeros((0, 2)),
            out_path=tmp_path / "lw_empty.png",
        )


def test_plot_log_weight_flow_single_lambda_point(tmp_path: Path) -> None:
    out = plot_log_weight_flow(
        lams=[1.0],
        log_weights=np.array([[0.2, -0.1]]),
        out_path=tmp_path / "lw_single.png",
    )
    _assert_png(out)


# ---------------------------------------------------------------------------
# Optional networkx graph
# ---------------------------------------------------------------------------


def test_plot_coupling_graph_runs_when_networkx_present(tmp_path: Path) -> None:
    if not has_networkx():
        pytest.skip("networkx not installed")
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    out = plot_coupling_graph(coupling_j=J, out_path=tmp_path / "cg.png", threshold=0.0)
    assert out is not None
    _assert_png(out)


def test_plot_coupling_graph_K3(tmp_path: Path) -> None:
    if not has_networkx():
        pytest.skip("networkx not installed")
    rng = np.random.default_rng(0)
    J = rng.standard_normal((2, 2, 2))
    out = plot_coupling_graph(coupling_j=J, out_path=tmp_path / "cg3.png", threshold=0.0)
    assert out is not None
    _assert_png(out)


def test_plot_coupling_graph_rejects_K1() -> None:
    if not has_networkx():
        pytest.skip("networkx not installed")
    with pytest.raises(ValueError, match="K ≥ 2"):
        plot_coupling_graph(coupling_j=np.zeros(2), out_path="/dev/null")


def test_has_seaborn_returns_bool() -> None:
    assert isinstance(has_seaborn(), bool)


# ---------------------------------------------------------------------------
# KL geodesic + lambda* locus (geodesic submodule)
# ---------------------------------------------------------------------------


def test_plot_kl_geodesic_in_simplex(tmp_path: Path) -> None:
    from visualizations.geodesic import plot_kl_geodesic_in_simplex

    lams = np.linspace(0.0, 4.0, 9)
    joints = [_ising_q(float(l)) for l in lams]
    out = plot_kl_geodesic_in_simplex(
        lams=lams,
        joints=joints,
        out_path=tmp_path / "kl.png",
    )
    _assert_png(out)


def test_plot_kl_geodesic_rejects_length_mismatch(tmp_path: Path) -> None:
    from visualizations.geodesic import plot_kl_geodesic_in_simplex

    with pytest.raises(ValueError, match="len"):
        plot_kl_geodesic_in_simplex(
            lams=[0.0, 1.0],
            joints=[_ising_q(0.0)],
            out_path=tmp_path / "x.png",
        )


def test_plot_lambda_star_locus(tmp_path: Path) -> None:
    from visualizations.geodesic import plot_lambda_star_locus

    utilities = np.linspace(0.0, 0.9, 5)
    gammas = np.linspace(0.5, 2.0, 4)
    grid = np.tanh(np.outer(utilities, gammas))
    out = plot_lambda_star_locus(
        utilities=utilities,
        gammas=gammas,
        lambda_star=grid,
        out_path=tmp_path / "lstar.png",
    )
    _assert_png(out)
