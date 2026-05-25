"""Visualization helpers for the pymdp-grounded free-energy bundle.

Each function takes a sequence of :class:`simulation.inference.FreeEnergyBundle`
records (one per λ) and emits a single PNG.  Pure I/O + matplotlib;
no numerical work — all computation lives in
``src/simulation/inference.py``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box, apply_lambda_axis
from .setup import PUBLICATION_STYLE, palette_color

ArrayF = NDArray[np.float64]


def _lams_array(bundles) -> ArrayF:
    return np.array([b.lam for b in bundles], dtype=np.float64)


def plot_vfe_decomposition(bundles, *, out_path: Path, metadata=None) -> Path:
    """Variational free energy decomposed across coupling λ.

    Top panel: per-stream VFE (one line per stream).
    Bottom panel: total VFE, the bundle's ``λ·⟨J⟩`` term (policy
    coupling observable), and the multi-information **positive** curve
    ``I(q_λ)`` as in Theorem 5.1 (Gibbs form adds ``+ I`` explicitly).
    The three lines are illustrative observables — the repository's pymdp
    bundle omits priors/log-partition bookkeeping from §5, so their sum is
    not claimed to coincide with global ``F[q_λ]`` without those terms.
    """
    out_path = Path(out_path)
    lams = _lams_array(bundles)
    n_streams = bundles[0].vfe_per_stream.shape[0]
    per_stream = np.stack([b.vfe_per_stream for b in bundles])  # (T, n_streams)
    vfe_total = np.array([b.vfe_total for b in bundles])
    coupling = np.array([b.coupling_term for b in bundles])
    tc = np.array([b.total_correlation for b in bundles])

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=PUBLICATION_STYLE.two_panel,
        sharex=True,
        constrained_layout=True,
    )
    for k in range(n_streams):
        ax1.plot(
            lams,
            per_stream[:, k],
            "-o",
            markersize=4,
            linewidth=2.0,
            label=f"stream {k}: $F[q_\\lambda^{k}]$",
        )
    ax1.set_ylabel("Per-stream VFE [nats]")
    ax1.set_title("pymdp variational free energy decomposition")
    ax1.legend(loc="best")

    ax2.plot(
        lams,
        vfe_total,
        "-o",
        markersize=4,
        linewidth=2.0,
        color="black",
        label=r"total $\sum_k F[q_\lambda^k]$",
    )
    ax2.plot(
        lams,
        coupling,
        "-s",
        markersize=3,
        linewidth=1.2,
        color=palette_color(5),
        label=r"$\lambda\,\langle J\rangle_{q_\lambda}$",
    )
    ax2.plot(lams, tc, "-^", markersize=3, linewidth=1.4, color=palette_color(6), label=r"$I(q_\lambda)$")
    apply_lambda_axis(ax2)
    ax2.set_ylabel("Free-energy term [nats]")
    ax2.legend(loc="best")
    add_stats_box(
        ax2,
        {"λ count": int(lams.size), "TC max": float(tc.max()), "coupling max": float(coupling.max())},
        loc="lower right",
    )
    return _save(fig, out_path, metadata=metadata)


def plot_efe_under_posterior(bundles, *, out_path: Path, metadata=None) -> Path:
    """Expected EFE ``⟨G_k⟩_{q^k_λ}`` per stream, plus the
    sum across streams.
    """
    out_path = Path(out_path)
    lams = _lams_array(bundles)
    efe = np.stack([b.efe_under_posterior for b in bundles])  # (T, K)
    n_streams = efe.shape[1]
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    for k in range(n_streams):
        ax.plot(lams, efe[:, k], "-o", markersize=4, linewidth=2.0, label=f"stream {k}")
    ax.plot(
        lams,
        efe.sum(axis=1),
        "--",
        color="black",
        linewidth=1.5,
        label=r"sum $\sum_k \langle G_k\rangle$",
    )
    apply_lambda_axis(ax)
    ax.set_ylabel(r"$\langle G_k\rangle_{q_\lambda^k}$ [nats]")
    ax.set_title("pymdp EFE under the coupled posterior")
    ax.legend(loc="best")
    add_stats_box(ax, {"streams": n_streams, "sum final": float(efe.sum(axis=1)[-1])}, loc="lower right")
    return _save(fig, out_path, metadata=metadata)


def plot_entropy_decomposition(bundles, *, out_path: Path, metadata=None) -> Path:
    """Joint vs sum-of-marginal entropy + their gap (= total correlation).

    Renders three lines: $H(q)$, $\\sum_k H(q^k)$, and the difference
    $I(q) = \\sum_k H(q^k) - H(q)$.  At λ=0 the first two curves
    coincide and TC = 0, providing a visual sanity check.
    """
    out_path = Path(out_path)
    lams = _lams_array(bundles)
    h_joint = np.array([b.joint_entropy for b in bundles])
    h_marg_sum = np.array([b.marginal_entropies.sum() for b in bundles])
    tc = np.array([b.total_correlation for b in bundles])

    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    ax.plot(
        lams,
        h_marg_sum,
        "-o",
        color=palette_color(5),
        markersize=4,
        linewidth=2.0,
        label=r"$\sum_k H(q_\lambda^k)$",
    )
    ax.plot(
        lams,
        h_joint,
        "-s",
        color=palette_color(1),
        markersize=4,
        linewidth=2.0,
        label=r"$H(q_\lambda)$",
    )
    ax.fill_between(
        lams,
        h_joint,
        h_marg_sum,
        alpha=0.2,
        color=palette_color(7),
        label=r"$I(q_\lambda) = \sum_k H(q^k) - H(q)$",
    )
    ax.plot(lams, tc, "--", color=palette_color(7), linewidth=1.4)
    apply_lambda_axis(ax)
    ax.set_ylabel("Entropy [nats]")
    ax.set_title("Joint vs marginal entropy: total correlation as the gap")
    ax.legend(loc="best")
    add_stats_box(ax, {"max gap": float(tc.max()), "zero gap": float(tc[0])}, loc="lower right")
    return _save(fig, out_path, metadata=metadata)


def plot_action_distribution_evolution(bundles, *, out_path: Path, metadata=None) -> Path:
    """Heatmap of the joint action distribution across λ.

    Rows = λ values, columns = joint policies (lex order over
    $\\prod_k \\Pi^k$).  Each row is a PMF over joint actions; the
    structure of the matrix shows how mass concentrates onto the
    aligned diagonal as λ grows.
    """
    out_path = Path(out_path)
    lams = _lams_array(bundles)
    flat = np.stack([b.action_distribution for b in bundles])  # (T, |Π|)
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    im = ax.imshow(
        flat,
        aspect="auto",
        origin="lower",
        cmap="magma",
        extent=(
            -0.5,
            float(flat.shape[1]) - 0.5,
            float(lams[0]),
            float(lams[-1]),
        ),
    )
    ax.set_xlabel(r"Joint policy index (lex over $\prod_k \Pi^k$)")
    ax.set_ylabel(r"Coupling $\lambda$")
    ax.set_title("pymdp coupled posterior: action distribution vs λ")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"$q_\lambda(\pi)$")
    return _save(fig, out_path, metadata=metadata)


def plot_free_energy_panel(bundles, *, out_path: Path, metadata=None) -> Path:
    """One four-panel figure that bundles every observable.

    Panel A shows total VFE, ``λ⟨J⟩``, and ``I(q_λ)``
    plus sign for multi-information matches §5; the pymdp CSV omits priors /
    ``log Z_E``, so plotted lines need not reconstruct global ``F[q_λ]`` alone.
    Panel B: per-stream VFE.
    Panel C: per-stream ⟨G_k⟩ under posterior.
    Panel D: joint vs marginal entropy.
    """
    out_path = Path(out_path)
    lams = _lams_array(bundles)
    n_streams = bundles[0].vfe_per_stream.shape[0]
    per_stream = np.stack([b.vfe_per_stream for b in bundles])
    vfe_total = np.array([b.vfe_total for b in bundles])
    coupling = np.array([b.coupling_term for b in bundles])
    tc = np.array([b.total_correlation for b in bundles])
    efe = np.stack([b.efe_under_posterior for b in bundles])
    h_joint = np.array([b.joint_entropy for b in bundles])
    h_marg = np.array([b.marginal_entropies.sum() for b in bundles])

    fig, axes = plt.subplots(2, 2, figsize=PUBLICATION_STYLE.dashboard_2x2, constrained_layout=True)
    ax_a, ax_b, ax_c, ax_d = axes.flatten()

    ax_a.plot(lams, vfe_total, "-o", color="black", markersize=3, label=r"total VFE")
    ax_a.plot(lams, coupling, "-s", color=palette_color(5), markersize=3, label=r"$\lambda\,\langle J\rangle$")
    ax_a.plot(lams, tc, "-^", color=palette_color(6), markersize=3, label=r"$I(q_\lambda)$")
    ax_a.set_title("A. Free-energy decomposition")
    apply_lambda_axis(ax_a, label=r"$\lambda$")
    ax_a.set_ylabel("nats")
    ax_a.legend()
    add_stats_box(ax_a, {"λ count": int(lams.size), "TC max": float(tc.max())}, loc="lower right")

    for k in range(n_streams):
        ax_b.plot(lams, per_stream[:, k], "-o", markersize=3, label=f"stream {k}")
    ax_b.set_title("B. Per-stream VFE")
    apply_lambda_axis(ax_b, label=r"$\lambda$")
    ax_b.set_ylabel("nats")
    ax_b.legend()

    for k in range(n_streams):
        ax_c.plot(lams, efe[:, k], "-o", markersize=3, label=f"stream {k}")
    ax_c.plot(lams, efe.sum(axis=1), "--", color="black", label=r"$\sum_k \langle G_k\rangle$")
    ax_c.set_title(r"C. Expected EFE under $q_\lambda$")
    apply_lambda_axis(ax_c, label=r"$\lambda$")
    ax_c.set_ylabel("nats")
    ax_c.legend()

    ax_d.plot(lams, h_marg, "-o", color=palette_color(5), markersize=3, label=r"$\sum_k H(q^k)$")
    ax_d.plot(lams, h_joint, "-s", color=palette_color(1), markersize=3, label=r"$H(q_\lambda)$")
    ax_d.fill_between(lams, h_joint, h_marg, alpha=0.2, color=palette_color(7), label=r"$I(q_\lambda)$")
    ax_d.set_title("D. Entropy / total correlation")
    apply_lambda_axis(ax_d, label=r"$\lambda$")
    ax_d.set_ylabel("nats")
    ax_d.legend()
    add_stats_box(ax_d, {"entropy gap max": float((h_marg - h_joint).max())}, loc="lower right")

    return _save(fig, out_path, metadata=metadata)


def plot_bundle_quantile_envelope(
    envelope,
    *,
    out_path: Path,
    field_label: str = r"Total correlation $I(q_\lambda)$ [nats]",
    metadata=None,
) -> Path:
    """Plot a :class:`simulation.statistics.QuantileEnvelope` as a
    median curve with quantile / min-max bands.

    The plot has a single axis; from bottom to top:

    * a translucent **min/max** band (lightest),
    * a translucent **quantile_lower / quantile_upper** band,
    * the **median** line with markers.

    Useful for showing how an observable varies across multiple
    seeds or perturbed runs of the same sweep grid.

    Args:
        envelope: A :class:`QuantileEnvelope` with aligned ``lams`` /
            ``median`` / ``lower`` / ``upper`` / ``minimum`` /
            ``maximum`` arrays.
        out_path: Destination PNG.
        field_label: Y-axis label; describe the aggregated observable.
        metadata: Optional ``figure_metadata`` payload for PNG
            tEXt chunks.
    """
    out_path = Path(out_path)
    lams = np.asarray(envelope.lams, dtype=np.float64)
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    ax.fill_between(
        lams,
        envelope.minimum,
        envelope.maximum,
        alpha=0.18,
        color=palette_color(5),
        label=f"min / max envelope (n={envelope.n_runs})",
    )
    ax.fill_between(
        lams,
        envelope.lower,
        envelope.upper,
        alpha=0.32,
        color=palette_color(5),
        label=(f"q{int(envelope.quantile_lower * 100):02d} / q{int(envelope.quantile_upper * 100):02d} band"),
    )
    ax.plot(
        lams,
        envelope.median,
        "-o",
        markersize=3,
        linewidth=1.8,
        color=palette_color(5),
        label="median",
    )
    apply_lambda_axis(ax)
    ax.set_ylabel(field_label)
    ax.set_title("Bundle observable across runs (quantile envelope)")
    ax.legend(loc="best")
    add_stats_box(ax, {"runs": int(envelope.n_runs), "median max": float(np.max(envelope.median))}, loc="upper left")
    return _save(fig, out_path, metadata=metadata)
