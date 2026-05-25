"""Additional pymdp-grounded visualizations driven by a list of
:class:`simulation.inference.FreeEnergyBundle` records and the
summary statistics in :mod:`simulation.statistics`.

Every helper accepts an optional ``metadata`` mapping that is
embedded as PNG tEXt via :func:`visualizations.metadata.figure_metadata`.
The figure scripts pass a hyperparameter snapshot + source-function
attribution so each rendered PNG records its own provenance.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from lean.free_energy import shannon_entropy as _shannon

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box, apply_lambda_axis
from .setup import PUBLICATION_STYLE, palette_color

ArrayF = NDArray[np.float64]


def plot_action_entropy_curve(
    bundles: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Per-λ Shannon entropy of the joint action distribution and mode
    probability as aligned stacked panels.

    * top: $H(q_\\lambda)$ in nats — decreases as the joint
      concentrates on its dominant archetype.
    * bottom: $\\max_\\pi q_\\lambda(\\pi)$ — the mode probability,
      asymptotically 1 as λ → ∞.
    """
    lams = np.array([b.lam for b in bundles], dtype=np.float64)
    action_entropy = np.array([_shannon(b.action_distribution) for b in bundles], dtype=np.float64)
    mode = np.array(
        [float(np.asarray(b.action_distribution).reshape(-1).max()) for b in bundles],
        dtype=np.float64,
    )
    log_num_joint_actions = float(np.log(np.asarray(bundles[0].action_distribution).reshape(-1).size))

    fig, (ax, ax_mode) = plt.subplots(
        2,
        1,
        figsize=PUBLICATION_STYLE.two_panel,
        sharex=True,
        constrained_layout=True,
    )
    ax.plot(
        lams,
        action_entropy,
        "-o",
        color=palette_color(5),
        markersize=4,
        linewidth=2.0,
        label=r"$H(q_\lambda)$",
    )
    ax.axhline(
        log_num_joint_actions,
        color=palette_color(5),
        linestyle=":",
        linewidth=1.0,
        label=r"$\log |\Pi|$ (uniform)",
    )
    ax.set_ylabel("Action entropy [nats]")
    ax.set_title("pymdp action distribution: entropy and mode probability")
    ax.legend(loc="best")

    ax_mode.plot(
        lams,
        mode,
        "-s",
        color=palette_color(6),
        markersize=4,
        linewidth=2.0,
        label=r"$\max_\pi q_\lambda(\pi)$",
    )
    apply_lambda_axis(ax_mode)
    ax_mode.set_ylabel("Mode probability")
    ax_mode.set_ylim(0.0, 1.05)
    ax_mode.legend(loc="best")
    add_stats_box(
        ax_mode,
        {
            "λ count": int(lams.size),
            "H min": float(action_entropy.min()),
            "mode final": float(mode[-1]),
        },
        loc="lower right",
    )
    return _save(fig, out_path, metadata=metadata)


def plot_kl_to_lambda_zero(
    bundles: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """KL divergence from the action distribution at coupling λ
    back to the mean-field baseline at λ = 0.

    A direct measure of how much the coupled posterior has *moved*
    from the mean-field anchor — complementary to the total
    correlation curve.
    """
    if not bundles:
        raise ValueError("need at least one bundle")
    q0 = np.asarray(bundles[0].action_distribution, dtype=np.float64).reshape(-1)
    q0_norm = q0 / max(float(q0.sum()), 1e-300)
    lams = np.array([b.lam for b in bundles], dtype=np.float64)
    kls: list[float] = []
    for b in bundles:
        qa = np.asarray(b.action_distribution, dtype=np.float64).reshape(-1)
        qa = qa / max(float(qa.sum()), 1e-300)
        mask = qa > 0.0
        kls.append(
            float((qa[mask] * (np.log(qa[mask]) - np.log(np.where(q0_norm[mask] > 0, q0_norm[mask], 1e-300)))).sum())
        )
    kl = np.array(kls, dtype=np.float64)

    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    ax.plot(
        lams,
        kl,
        "-o",
        color=palette_color(7),
        markersize=4,
        linewidth=2.0,
        label=r"$D_{\rm KL}(q_\lambda \,\|\, q_0)$",
    )
    ax.axhline(0.0, color="gray", linestyle=":", linewidth=0.7)
    apply_lambda_axis(ax)
    ax.set_ylabel("KL to mean-field baseline [nats]")
    ax.set_title("pymdp coupled posterior: KL divergence from λ = 0")
    ax.legend(loc="best")
    add_stats_box(ax, {"max KL": float(kl.max()), "λ count": int(lams.size)}, loc="upper left")
    return _save(fig, out_path, metadata=metadata)


def plot_marginal_entropy_per_stream(
    bundles: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Per-stream marginal entropy $H(q^k_\\lambda)$ vs λ.

    Reveals which streams collapse fastest under coupling.  The
    dashed line is the joint entropy $H(q_\\lambda)$ for context.
    """
    n_streams = bundles[0].marginal_entropies.shape[0]
    lams = np.array([b.lam for b in bundles], dtype=np.float64)
    h_stream_rows = np.stack([b.marginal_entropies for b in bundles], axis=0)  # (T, K)
    h_joint = np.array([b.joint_entropy for b in bundles], dtype=np.float64)

    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    for k in range(n_streams):
        ax.plot(
            lams,
            h_stream_rows[:, k],
            "-o",
            markersize=4,
            linewidth=2.0,
            label=f"$H(q_\\lambda^{k})$",
        )
    ax.plot(lams, h_joint, "--", color="black", linewidth=1.4, label=r"$H(q_\lambda)$ (joint)")
    apply_lambda_axis(ax)
    ax.set_ylabel("Entropy [nats]")
    ax.set_title("pymdp per-stream marginal entropy vs λ")
    ax.legend(loc="best")
    add_stats_box(
        ax,
        {"streams": n_streams, "joint H min": float(h_joint.min()), "joint H max": float(h_joint.max())},
        loc="lower right",
    )
    return _save(fig, out_path, metadata=metadata)


def plot_pymdp_summary_panel(
    bundles: Sequence[Any],
    *,
    out_path: Path,
    summary: Any | None = None,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Six-panel summary of the pymdp run.

    Panel (A): TC vs λ + half-saturation line.
    Panel (B): VFE total + coupling term + −I.
    Panel (C): action entropy + mode probability.
    Panel (D): KL to λ=0.
    Panel (E): per-stream marginal entropy.
    Panel (F): aligned-corner mass.
    """
    lams = np.array([b.lam for b in bundles], dtype=np.float64)
    tcs = np.array([b.total_correlation for b in bundles], dtype=np.float64)
    vfe = np.array([b.vfe_total for b in bundles], dtype=np.float64)
    coup = np.array([b.coupling_term for b in bundles], dtype=np.float64)
    mode = np.array(
        [float(np.asarray(b.action_distribution).reshape(-1).max()) for b in bundles],
        dtype=np.float64,
    )
    h_action = np.array(
        [_shannon(b.action_distribution) for b in bundles],
        dtype=np.float64,
    )
    n_streams = bundles[0].marginal_entropies.shape[0]
    h_stream_rows = np.stack([b.marginal_entropies for b in bundles], axis=0)
    aligned_mass: list[float] = []
    for b in bundles:
        flat = np.asarray(b.action_distribution).reshape(-1)
        if flat.size == 4:
            aligned_mass.append(float(flat[0] + flat[3]))
        else:
            aligned_mass.append(float("nan"))
    aligned_arr = np.array(aligned_mass, dtype=np.float64)

    q0 = np.asarray(bundles[0].action_distribution).reshape(-1)
    q0n = q0 / max(float(q0.sum()), 1e-300)
    kls = []
    for b in bundles:
        qa = np.asarray(b.action_distribution).reshape(-1)
        qa = qa / max(float(qa.sum()), 1e-300)
        mask = qa > 0.0
        kls.append(float((qa[mask] * (np.log(qa[mask]) - np.log(np.where(q0n[mask] > 0, q0n[mask], 1e-300)))).sum()))
    kl = np.array(kls, dtype=np.float64)

    fig, axes = plt.subplots(2, 3, figsize=PUBLICATION_STYLE.dashboard_2x3, constrained_layout=True)
    ax_a, ax_b, ax_c, ax_d, ax_e, ax_f = axes.flatten()

    ax_a.plot(lams, tcs, "-o", color=palette_color(7), markersize=4, label=r"$I(q_\lambda)$")
    if summary is not None and summary.lambda_at_half_saturation > 0:
        ax_a.axvline(
            summary.lambda_at_half_saturation,
            color=palette_color(7),
            linestyle=":",
            linewidth=0.9,
            label=rf"$\lambda_{{1/2}}\approx{summary.lambda_at_half_saturation:.2f}$",
        )
    ax_a.set_title("A. Total correlation")
    apply_lambda_axis(ax_a, label=r"$\lambda$")
    ax_a.set_ylabel("nats")
    ax_a.legend()
    add_stats_box(ax_a, {"grid": int(lams.size), "TC max": float(tcs.max())}, loc="lower right")

    ax_b.plot(lams, vfe, "-o", color="black", markersize=3, label="VFE total")
    ax_b.plot(lams, coup, "-s", color=palette_color(5), markersize=3, label=r"$\lambda\langle J\rangle$")
    ax_b.plot(lams, tcs, "-^", color=palette_color(6), markersize=3, label=r"$I(q_\lambda)$")
    ax_b.set_title("B. Free-energy decomposition")
    apply_lambda_axis(ax_b, label=r"$\lambda$")
    ax_b.set_ylabel("nats")
    ax_b.legend()

    ax_c.plot(lams, h_action, "-o", color=palette_color(5), markersize=3, label=r"$H(q_\lambda)$")
    ax_c.plot(lams, mode, "-s", color=palette_color(6), markersize=3, label="mode probability")
    ax_c.set_title("C. Action entropy + mode")
    apply_lambda_axis(ax_c, label=r"$\lambda$")
    ax_c.set_ylabel("entropy [nats] / probability")
    ax_c.set_ylim(0, max(float(h_action.max()), 1.05) * 1.08)
    ax_c.legend()
    add_stats_box(ax_c, {"H min": float(h_action.min()), "mode final": float(mode[-1])}, loc="upper right")

    ax_d.plot(lams, kl, "-o", color=palette_color(7), markersize=3, label=r"$D_{\rm KL}(q_\lambda \|\, q_0)$")
    ax_d.set_title("D. KL to mean-field baseline")
    apply_lambda_axis(ax_d, label=r"$\lambda$")
    ax_d.set_ylabel("nats")
    ax_d.legend()

    for k in range(n_streams):
        ax_e.plot(lams, h_stream_rows[:, k], "-o", markersize=3, label=f"$H(q^{k})$")
    ax_e.set_title("E. Per-stream marginal entropy")
    apply_lambda_axis(ax_e, label=r"$\lambda$")
    ax_e.set_ylabel("nats")
    ax_e.legend()

    ax_f.plot(lams, aligned_arr, "-o", color=palette_color(3), markersize=3, label=r"$q(0,0)+q(1,1)$")
    ax_f.axhline(0.5, color="gray", linestyle=":", linewidth=0.7, label="uniform baseline")
    ax_f.set_title("F. Aligned-corner mass")
    apply_lambda_axis(ax_f, label=r"$\lambda$")
    ax_f.set_ylabel("probability")
    ax_f.set_ylim(0, 1.05)
    ax_f.legend()
    finite_aligned = aligned_arr[np.isfinite(aligned_arr)]
    aligned_stats: dict[str, float | str] = {"aligned max": "n/a", "final": "n/a"}
    if finite_aligned.size:
        aligned_stats["aligned max"] = float(np.max(finite_aligned))
        if np.isfinite(aligned_arr[-1]):
            aligned_stats["final"] = float(aligned_arr[-1])
    add_stats_box(ax_f, aligned_stats, loc="lower right")

    return _save(fig, out_path, metadata=metadata)
