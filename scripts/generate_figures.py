#!/usr/bin/env python3
"""Generate every figure for the Policy Entanglement manuscript.

Thin orchestrator — imports computations from :mod:`lean` (analytical
core) and helpers from :mod:`visualizations`; only handles I/O,
plotting glue, and output-path collection.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
for _sub in ("", "lean", "simulation", "visualizations"):
    p = SRC_DIR / _sub if _sub else SRC_DIR
    sys.path.insert(0, str(p))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from bernoulli_toy import (  # noqa: E402
    coupling_phase_at,
    empirical_mutual_information,
    ising_free_energy_curve,
    ising_joint_posterior,
    ising_mutual_information,
    optimal_lambda,
)
from coupling import (  # noqa: E402
    coupling_log_weight,
    entangled_posterior,
)
from heterogeneous import (  # noqa: E402
    InferenceMode,
    coupling_tax,
)
from spectral import (  # noqa: E402
    entanglement_entropy,
    schmidt_decomposition,
    schmidt_rank,
    tensor_train_ranks,
)

# Visualization helpers (viz subpackage).
from heatmaps import plot_lambda_utility_heatmap, plot_schmidt_entropy_surface  # noqa: E402
from joint_plots import plot_joint_heatmap_with_marginals  # noqa: E402
from log_weight import plot_log_weight_flow  # noqa: E402
from setup import deterministic_setup, ensure_outdir  # noqa: E402
from spectral_plots import (  # noqa: E402
    plot_archetype_dendrogram,
    plot_tensor_train_rank_surface,
)

deterministic_setup(seed=42)

OUTPUT_DIR = ensure_outdir(PROJECT_ROOT / "output" / "figures")


# ---------------------------------------------------------------------------
# Legacy figures (kept for backwards compat with validate_outputs.py)
# ---------------------------------------------------------------------------


def figure_ising_mi_curve() -> Path:
    lams = np.linspace(0.0, 6.0, 121)
    closed = np.array([ising_mutual_information(l) for l in lams])
    empirical = np.array([empirical_mutual_information(l) for l in lams])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(lams, closed, label="closed form: log 2 − H_b(σ(λ))", linewidth=2)
    ax.plot(lams[::10], empirical[::10], "o", label="empirical", markersize=4)
    ax.axhline(np.log(2.0), color="gray", linestyle=":", label="log 2 (saturation)")
    ax.set_xlabel("Coupling λ")
    ax.set_ylabel("Mutual information I(λ)  [nats]")
    ax.set_title("K=2 Ising: closed-form vs empirical mutual information")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    out = OUTPUT_DIR / "ising_mi_curve.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def figure_free_energy_curve() -> Path:
    lams = np.linspace(0.0, 6.0, 121)
    fig, ax = plt.subplots(figsize=(6, 4))
    for utility in [0.0, 0.5, 1.0, 2.0]:
        Fs = np.array([ising_free_energy_curve(l, utility) for l in lams])
        ax.plot(lams, Fs, label=f"utility = {utility}", linewidth=1.5)
    ax.set_xlabel("Coupling λ")
    ax.set_ylabel("F[q_λ]  [nats]")
    ax.set_title("K=2 Ising: free-energy curve (utility sweep)")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    out = OUTPUT_DIR / "free_energy_curve.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def figure_coupling_tax_quadratic() -> Path:
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.array([[0.2, -0.1], [-0.1, 0.2]])
    modes = [InferenceMode.VFE, InferenceMode.EFE]
    lams = np.linspace(0.0, 1.5, 31)
    taxes = np.array(
        [coupling_tax(mf, G, J, Kc, gamma=1.0, lam=l, modes=modes) for l in lams]
    )
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(lams, taxes, "o-", label="numerical tax", markersize=3)
    if taxes[1] > 0.0:
        C = taxes[1] / (lams[1] ** 2)
        ax.plot(lams, C * lams ** 2, "--", label=f"O(λ²) envelope, C ≈ {C:.3g}")
    ax.set_xlabel("Coupling λ")
    ax.set_ylabel("Coupling tax  KL(q_full ‖ q_pinned)  [nats]")
    ax.set_title("Heterogeneous K=2: O(λ²) coupling tax (Theorem 8.1)")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    out = OUTPUT_DIR / "coupling_tax_quadratic.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def figure_phase_diagram() -> Path:
    lams = np.linspace(0.0, 4.0, 401)
    phase_to_int = {"disordered": 0, "mixed": 1, "frozen": 2}
    phases = np.array(
        [phase_to_int[coupling_phase_at(l, lam_c1=0.5, lam_c2=2.5)] for l in lams]
    )
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.fill_between(lams, 0, 1, where=phases == 0, alpha=0.4, label="disordered")
    ax.fill_between(lams, 0, 1, where=phases == 1, alpha=0.4, label="mixed (skilled)")
    ax.fill_between(lams, 0, 1, where=phases == 2, alpha=0.4, label="frozen")
    ax.set_xlabel("Coupling λ")
    ax.set_yticks([])
    ax.set_title("Coupling phase diagram (illustrative thresholds 0.5, 2.5)")
    ax.legend(loc="upper right")
    out = OUTPUT_DIR / "phase_diagram.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def figure_optimal_lambda() -> Path:
    deltas = np.linspace(-0.95, 0.95, 191)
    lams = np.array([optimal_lambda(d) for d in deltas])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(deltas, lams, linewidth=2)
    ax.axhline(0.0, color="gray", linestyle=":", linewidth=0.7)
    ax.axvline(0.0, color="gray", linestyle=":", linewidth=0.7)
    ax.set_xlabel("Utility surplus Δ / Δmax")
    ax.set_ylabel("Optimal coupling λ*(Δ)")
    ax.set_title("Closed-form optimal coupling, K=2 Ising toy")
    ax.grid(alpha=0.3)
    out = OUTPUT_DIR / "optimal_lambda.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def figure_schmidt_rank_vs_lambda() -> Path:
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.zeros(2), np.zeros(2)]
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.zeros((2, 2))
    lams = np.linspace(0.0, 4.0, 81)
    ranks = []
    for lam in lams:
        q = entangled_posterior(mf, G, J, Kc, gamma=0.0, lam=lam)
        ranks.append(schmidt_rank(q, atol=1e-9))
    ranks = np.array(ranks)
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.step(lams, ranks, where="post", linewidth=2)
    ax.set_yticks([0, 1, 2])
    ax.set_xlabel("Coupling λ")
    ax.set_ylabel("Schmidt rank")
    ax.set_title("K=2 Ising: Schmidt rank vs λ (Prop 7.1)")
    ax.grid(alpha=0.3)
    out = OUTPUT_DIR / "schmidt_rank.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# New figures (visualizations subpackage)
# ---------------------------------------------------------------------------


def figure_phase_landscape() -> Path:
    """Phase landscape over (λ, utility): heatmap of free energy."""
    lams = np.linspace(0.0, 4.0, 41)
    utilities = np.linspace(0.0, 2.0, 21)
    score = np.zeros((utilities.size, lams.size), dtype=np.float64)
    for i, u in enumerate(utilities):
        for j, l in enumerate(lams):
            score[i, j] = ising_free_energy_curve(float(l), float(u))
    return plot_lambda_utility_heatmap(
        lams=lams,
        utilities=utilities,
        score=score,
        title="K=2 Ising: free energy F(λ, utility)",
        cbar_label="F  [nats]",
        out_path=OUTPUT_DIR / "phase_landscape.png",
        cmap="viridis",
    )


def figure_schmidt_entropy_surface() -> Path:
    """Schmidt entropy heatmap over (λ, utility)."""
    lams = np.linspace(0.0, 4.0, 41)
    utilities = np.linspace(0.0, 2.0, 21)
    entropies = np.zeros((utilities.size, lams.size), dtype=np.float64)
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.zeros((2, 2))
    for i, u in enumerate(utilities):
        # Utility shifts the per-stream G_k.
        G = [np.array([0.0, float(u)]), np.array([0.0, float(u)])]
        for j, l in enumerate(lams):
            q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=float(l))
            entropies[i, j] = entanglement_entropy(q)
    return plot_schmidt_entropy_surface(
        lams=lams,
        utilities=utilities,
        entropies=entropies,
        out_path=OUTPUT_DIR / "schmidt_entropy_surface.png",
    )


def figure_joint_heatmap_with_marginals() -> Path:
    """Joint Ising posterior at λ=2 with marginals + residual."""
    q = ising_joint_posterior(2.0)
    return plot_joint_heatmap_with_marginals(
        q=q,
        title="K=2 Ising joint posterior at λ=2 (with m-projection residual)",
        out_path=OUTPUT_DIR / "joint_heatmap_lambda2.png",
        xticklabels=["π¹=0", "π¹=1"],
        yticklabels=["π²=0", "π²=1"],
    )


def figure_archetype_dendrogram() -> Path:
    """Schmidt archetypes for the K=2 Ising joint at λ=3."""
    q = ising_joint_posterior(3.0)
    archetypes = schmidt_decomposition(q)
    weights = [a.weight for a in archetypes]
    R = len(archetypes)
    overlap = np.zeros((R, R), dtype=np.float64)
    for i in range(R):
        for j in range(R):
            ui, vi = archetypes[i].u, archetypes[i].v
            uj, vj = archetypes[j].u, archetypes[j].v
            overlap[i, j] = float(abs(np.dot(ui, uj)) * abs(np.dot(vi, vj)))
    return plot_archetype_dendrogram(
        weights=weights,
        overlap_matrix=overlap,
        out_path=OUTPUT_DIR / "archetype_dendrogram.png",
    )


def figure_tensor_train_ranks() -> Path:
    """TT rank profiles across K=2..5 streams under uniform coupling."""
    K_values = [2, 3, 4, 5]
    profiles: list[list[int]] = []
    for K in K_values:
        shape = tuple(2 for _ in range(K))
        from builders import ising_coupling_tensor  # local import keeps top tidy
        J = ising_coupling_tensor(shape, scale=1.0)
        mf = [np.array([0.5, 0.5]) for _ in range(K)]
        G = [np.zeros(2) for _ in range(K)]
        Kc = np.zeros(shape)
        q = entangled_posterior(mf, G, J, Kc, gamma=0.0, lam=2.0)
        profiles.append(tensor_train_ranks(q, atol=1e-9))
    return plot_tensor_train_rank_surface(
        K_values=K_values,
        rank_profiles=profiles,
        out_path=OUTPUT_DIR / "tensor_train_rank_surface.png",
    )


def figure_log_weight_flow() -> Path:
    """e-geodesic: each policy's log-weight is affine in λ."""
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.array([[0.2, -0.1], [-0.1, 0.2]])
    lams = np.linspace(0.0, 3.0, 31)
    log_w = np.zeros((lams.size, 4), dtype=np.float64)
    for i, lam in enumerate(lams):
        W = coupling_log_weight(J, Kc, gamma=1.0, lam=float(lam))
        log_w[i, :] = W.reshape(-1)
    return plot_log_weight_flow(
        lams=lams,
        log_weights=log_w,
        out_path=OUTPUT_DIR / "log_weight_flow.png",
        pi_labels=["(0,0)", "(0,1)", "(1,0)", "(1,1)"],
    )


def figure_kl_geodesic_in_simplex() -> Path:
    """KL geodesic of the K=2 Ising joint traced across $\\lambda \\in [0, 4]$
    in the 2-D summary plane (alignment fraction × off-diagonal disparity).
    """
    from geodesic import plot_kl_geodesic_in_simplex

    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.zeros(2), np.zeros(2)]
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.zeros((2, 2))
    lams = np.linspace(0.0, 4.0, 21)
    joints = [
        entangled_posterior(mf, G, J, Kc, gamma=0.0, lam=float(l))
        for l in lams
    ]
    return plot_kl_geodesic_in_simplex(
        lams=lams, joints=joints,
        out_path=OUTPUT_DIR / "kl_geodesic_simplex.png",
    )


def figure_lambda_star_locus() -> Path:
    """Optimal coupling $\\lambda^\\star$ across (utility, gamma)."""
    from geodesic import plot_lambda_star_locus
    from bernoulli_toy import optimal_lambda

    utilities = np.linspace(0.0, 0.95, 20)
    gammas = np.linspace(0.5, 2.0, 16)
    lam_star = np.zeros((utilities.size, gammas.size), dtype=np.float64)
    for i, u in enumerate(utilities):
        for j, g in enumerate(gammas):
            # The K=2 Ising lam* is independent of gamma in the closed form
            # (see Appendix C); here we modulate the *effective* surplus by
            # gamma to expose the (utility, gamma) interaction.
            delta_eff = float(np.tanh(g * u))
            lam_star[i, j] = float(optimal_lambda(delta_eff))
    return plot_lambda_star_locus(
        utilities=utilities, gammas=gammas, lambda_star=lam_star,
        out_path=OUTPUT_DIR / "lambda_star_locus.png",
    )


def figure_coupling_graph() -> Path | None:
    """Coupling-potential graph for a K=4 Ising-like ensemble."""
    from graphs import plot_coupling_graph
    from builders import ising_coupling_tensor
    J = ising_coupling_tensor((2, 2, 2, 2), scale=1.0)
    return plot_coupling_graph(
        coupling_J=J,
        out_path=OUTPUT_DIR / "coupling_graph.png",
        threshold=0.0,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    figures: list[Path] = [
        figure_ising_mi_curve(),
        figure_free_energy_curve(),
        figure_coupling_tax_quadratic(),
        figure_phase_diagram(),
        figure_optimal_lambda(),
        figure_schmidt_rank_vs_lambda(),
        figure_phase_landscape(),
        figure_schmidt_entropy_surface(),
        figure_joint_heatmap_with_marginals(),
        figure_archetype_dendrogram(),
        figure_tensor_train_ranks(),
        figure_log_weight_flow(),
        figure_kl_geodesic_in_simplex(),
        figure_lambda_star_locus(),
    ]
    cg = figure_coupling_graph()
    if cg is not None:
        figures.append(cg)
    for path in figures:
        print(path)


if __name__ == "__main__":
    main()
