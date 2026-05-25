"""Analytical-core manuscript figures for the Policy Entanglement project.

Importable home for every `figure_*` function previously inlined in
``scripts/generate_figures.py``. Each function pulls the closed-form
result from :mod:`lean` (via :mod:`simulation.builders` for the K-stream
coupling tensor) and styled-plot glue from sibling
:mod:`visualizations` helpers, then writes a single PNG with
reproducibility metadata.

The figures honour the module-level :data:`OUTPUT_DIR` constant; tests
monkeypatch this attribute to redirect into ``tmp_path``. The thin
:mod:`scripts.generate_figures` orchestrator re-exports both the figure
functions and :data:`OUTPUT_DIR` for backwards-compatible test entry
points.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import numpy as np

from lean.bernoulli_toy import (
    coupling_phase_at,
    empirical_mutual_information,
    ising_free_energy_curve,
    ising_joint_posterior,
    ising_mutual_information,
    optimal_lambda,
)
from lean.coupling import (
    coupling_log_weight,
    entangled_posterior,
)
from lean.heterogeneous import (
    InferenceMode,
    coupling_tax,
)
from lean.spectral import (
    entanglement_entropy,
    schmidt_decomposition,
    schmidt_rank,
    tensor_train_ranks,
)
from simulation import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).
from simulation.builders import ising_coupling_tensor

from ._io import _save_with_metadata as _save
from .annotations import (
    FREE_ENERGY_LABEL,
    MI_LABEL,
    add_provenance_footer,
    add_stats_box,
    apply_lambda_axis,
    mark_critical_lambdas,
    pin_theorem,
)
from .geodesic import (
    plot_kl_geodesic_in_simplex,
    plot_lambda_star_locus,
)
from .graphs import plot_coupling_graph
from .heatmaps import (
    plot_lambda_utility_heatmap,
    plot_schmidt_entropy_surface,
)
from .joint_plots import plot_joint_heatmap_with_marginals
from .log_weight import plot_log_weight_flow
from .metadata import figure_metadata
from .setup import (
    PUBLICATION_STYLE,
    deterministic_setup,
    ensure_outdir,
    palette_color,
)
from .spectral_plots import (
    plot_archetype_dendrogram,
    plot_tensor_train_rank_surface,
)

_SRC_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = _SRC_DIR.parent

deterministic_setup(seed=int(H.FIGURE_GLOBAL_SEED))

#: Default figure output directory. Tests monkeypatch this attribute to redirect
#: emission into ``tmp_path``; production runs persist into the project tree.
OUTPUT_DIR = ensure_outdir(PROJECT_ROOT / "output" / "figures")

#: Provenance label injected into every PNG's metadata block. Kept literal so
#: downstream artifact audits can trace a figure to its conceptual origin even
#: after the thin-orchestrator move.
_PROVENANCE_SCRIPT = "scripts/generate_figures.py"


def _md(source_function: str, **extra: object) -> dict:
    """Reproducibility metadata for analytical figures."""
    return figure_metadata(
        source_script=_PROVENANCE_SCRIPT,
        source_function=source_function,
        hyperparameters={
            "figure_global_seed": int(H.FIGURE_GLOBAL_SEED),
            "param_sweep_grid_points": int(H.PARAMETER_SWEEP_LAMBDAS.num),
            "param_sweep_lambda_max": float(H.PARAMETER_SWEEP_LAMBDAS.stop),
            "phase_lambda_c1": float(H.PHASE_LAMBDA_C1),
            "phase_lambda_c2": float(H.PHASE_LAMBDA_C2),
            "coupling_tax_probe_lambda": float(H.COUPLING_TAX_PROBE_LAMBDA),
        },
        extra=dict(extra) if extra else None,
        project_root=PROJECT_ROOT,
    )


# ---------------------------------------------------------------------------
# Legacy figures (kept for backwards compat with validate_outputs.py)
# ---------------------------------------------------------------------------


def figure_ising_mi_curve() -> Path:
    lams = H.PARAMETER_SWEEP_LAMBDAS.values()
    closed = np.array([ising_mutual_information(lam) for lam in lams])
    empirical = np.array([empirical_mutual_information(lam) for lam in lams])
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    ax.plot(lams, closed, label=r"closed form: $\log 2 - H_b(\sigma(\lambda))$", linewidth=2)
    ax.plot(lams[::10], empirical[::10], "o", label="empirical", markersize=4)
    ax.axhline(np.log(2.0), color="gray", linestyle=":", label=r"$\log 2$ (saturation)")
    ax.set_ylabel(MI_LABEL)
    ax.set_title(r"K=2 Ising: closed-form vs empirical mutual information")
    ax.legend(loc="lower right")
    apply_lambda_axis(ax)
    pin_theorem(ax, "Prop 8.1 (witness)", loc="upper left")
    add_stats_box(
        ax,
        {
            "grid": len(lams),
            "max residual": float(np.max(np.abs(closed - empirical))),
            "saturation": float(np.log(2.0)),
        },
        loc="lower right",
    )
    add_provenance_footer(
        fig,
        script=_PROVENANCE_SCRIPT,
        function="figure_ising_mi_curve",
        hyperparameters={"grid": len(lams)},
    )
    out = OUTPUT_DIR / "ising_mi_curve.png"
    return _save(fig, out, metadata=_md("figure_ising_mi_curve"))


def figure_free_energy_curve() -> Path:
    lams = H.PARAMETER_SWEEP_LAMBDAS.values()
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    utility_levels = [0.0, 0.5, 1.0, 2.0]
    extrema: list[float] = []
    for utility in utility_levels:
        Fs = np.array(  # noqa: N806 — F = free energy (manuscript symbol).
            [ising_free_energy_curve(lam, utility) for lam in lams]
        )
        extrema.append(float(Fs.min()))
        ax.plot(lams, Fs, label=rf"utility $u = {utility}$", linewidth=2.0)
    ax.set_ylabel(FREE_ENERGY_LABEL)
    ax.set_title(r"K=2 Ising: free-energy curve (utility sweep)")
    ax.legend(loc="upper right", title="surplus")
    apply_lambda_axis(ax)
    pin_theorem(ax, "Thm 5.6 (witness)", loc="lower left")
    add_stats_box(
        ax,
        {
            "grid": len(lams),
            "utility levels": len(utility_levels),
            "min F": min(extrema),
        },
        loc="lower right",
    )
    add_provenance_footer(
        fig,
        script=_PROVENANCE_SCRIPT,
        function="figure_free_energy_curve",
        hyperparameters={"grid": len(lams), "utilities": "{0, 0.5, 1, 2}"},
    )
    out = OUTPUT_DIR / "free_energy_curve.png"
    return _save(fig, out, metadata=_md("figure_free_energy_curve"))


def figure_coupling_tax_quadratic() -> Path:
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    # Manuscript symbols (G, J, Kc) — uppercase is intentional.
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]  # noqa: N806
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])  # noqa: N806
    Kc = np.array([[0.2, -0.1], [-0.1, 0.2]])  # noqa: N806
    modes = [InferenceMode.VFE, InferenceMode.EFE]
    lams = H.COUPLING_TAX_LAMBDAS.values()
    taxes = np.array([coupling_tax(mf, G, J, Kc, gamma=1.0, lam=lam, modes=modes) for lam in lams])
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    ax.plot(lams, taxes, "o-", label="numerical tax", markersize=3)
    # Estimate the O(λ²) curvature constant C at the canonical probe λ
    # from hyperparameters — not at an arbitrary grid index.
    probe = float(H.COUPLING_TAX_PROBE_LAMBDA)
    tax_at_probe = coupling_tax(mf, G, J, Kc, gamma=1.0, lam=probe, modes=modes)
    if tax_at_probe > 0.0 and probe > 0.0:
        C = tax_at_probe / (probe**2)  # noqa: N806 — C = curvature constant (Thm 9.1).
        ax.plot(lams, C * lams**2, "--", label=rf"$O(\lambda^2)$ envelope, $C \approx {C:.3g}$")
    ax.set_ylabel(r"Coupling tax $\mathrm{KL}(q_{\mathrm{full}}\,\|\,q_{\mathrm{pinned}})$  [nats]")
    ax.set_title(r"Heterogeneous K=2: $O(\lambda^2)$ coupling tax")
    ax.legend(loc="upper left")
    apply_lambda_axis(ax)
    pin_theorem(ax, "Thm 9.1", loc="lower right")
    add_stats_box(
        ax,
        {"grid": len(lams), "probe λ": probe, "max tax": float(taxes.max())},
        loc="upper right",
    )
    add_provenance_footer(
        fig,
        script=_PROVENANCE_SCRIPT,
        function="figure_coupling_tax_quadratic",
        hyperparameters={"probe": probe},
    )
    out = OUTPUT_DIR / "coupling_tax_quadratic.png"
    return _save(fig, out, metadata=_md("figure_coupling_tax_quadratic"))


def figure_phase_diagram() -> Path:
    lams = H.PHASE_DIAGRAM_LAMBDAS.values()
    phase_to_int = {"disordered": 0, "mixed": 1, "frozen": 2}
    phases = np.array(
        [
            phase_to_int[
                coupling_phase_at(
                    lam,
                    lam_c1=float(H.PHASE_LAMBDA_C1),
                    lam_c2=float(H.PHASE_LAMBDA_C2),
                )
            ]
            for lam in lams
        ]
    )
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.wide, constrained_layout=True)
    ax.fill_between(lams, 0, 1, where=phases == 0, alpha=0.45, label="disordered (mean-field)", color=palette_color(2))
    ax.fill_between(lams, 0, 1, where=phases == 1, alpha=0.45, label="mixed (skilled)", color=palette_color(1))
    ax.fill_between(lams, 0, 1, where=phases == 2, alpha=0.45, label="frozen (archetypal)", color=palette_color(6))
    ax.set_yticks([])
    ax.set_title(
        rf"Coupling phase diagram "
        rf"($\lambda_c^{{(1)}}={H.PHASE_LAMBDA_C1:g},\;"
        rf"\lambda_c^{{(2)}}={H.PHASE_LAMBDA_C2:g}$)"
    )
    ax.legend(loc="upper right", ncol=3)
    apply_lambda_axis(ax)
    mark_critical_lambdas(
        ax, [H.PHASE_LAMBDA_C1, H.PHASE_LAMBDA_C2], labels=(r"$\lambda_c^{(1)}$", r"$\lambda_c^{(2)}$")
    )
    add_provenance_footer(fig, script=_PROVENANCE_SCRIPT, function="figure_phase_diagram")
    out = OUTPUT_DIR / "phase_diagram.png"
    return _save(fig, out, metadata=_md("figure_phase_diagram"))


def figure_optimal_lambda() -> Path:
    deltas = H.OPTIMAL_LAMBDA_DELTAS.values()
    lams = np.array([optimal_lambda(d) for d in deltas])
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    ax.plot(deltas, lams, linewidth=2, color=palette_color(5))
    ax.axhline(0.0, color="gray", linestyle=":", linewidth=0.7)
    ax.axvline(0.0, color="gray", linestyle=":", linewidth=0.7)
    ax.set_xlabel(r"Utility surplus $\Delta_{\mathrm{util}}/\Delta_{\max}$")
    ax.set_ylabel(r"Optimal coupling $\lambda^\star(\Delta)$")
    ax.set_title(
        r"Closed-form optimal coupling, K=2 Ising toy "
        r"($\lambda^\star = 2\,\mathrm{arctanh}\,\Delta$)"
    )
    ax.grid(alpha=0.3)
    pin_theorem(ax, "Thm 5.5 + 5.6", loc="upper left")
    add_stats_box(
        ax,
        {"grid": len(deltas), "λ min": float(lams.min()), "λ max": float(lams.max())},
        loc="lower right",
    )
    add_provenance_footer(fig, script=_PROVENANCE_SCRIPT, function="figure_optimal_lambda")
    out = OUTPUT_DIR / "optimal_lambda.png"
    return _save(fig, out, metadata=_md("figure_optimal_lambda"))


def figure_schmidt_rank_vs_lambda() -> Path:
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    # Manuscript symbols (G, J, Kc) — uppercase is intentional.
    G = [np.zeros(2), np.zeros(2)]  # noqa: N806
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])  # noqa: N806
    Kc = np.zeros((2, 2))  # noqa: N806
    lams = H.SCHMIDT_RANK_LAMBDAS.values()
    ranks_list: list[int] = []
    for lam in lams:
        q = entangled_posterior(mf, G, J, Kc, gamma=0.0, lam=lam)
        ranks_list.append(int(schmidt_rank(q, atol=float(H.SPECTRAL_RANK_ATOL))))
    ranks = np.array(ranks_list, dtype=np.int64)
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    ax.step(lams, ranks, where="post", linewidth=2.2, color=palette_color(3))
    ax.set_yticks([0, 1, 2])
    ax.set_ylabel("Schmidt rank")
    ax.set_title(
        r"K=2 Ising: Schmidt rank vs $\lambda$ "
        r"(rank $1\to 2$ at first non-zero coupling)"
    )
    apply_lambda_axis(ax)
    pin_theorem(ax, "Prop 8.1", loc="lower right")
    add_stats_box(
        ax,
        {"grid": len(lams), "rank min": int(ranks.min()), "rank max": int(ranks.max())},
        loc="upper left",
    )
    add_provenance_footer(
        fig,
        script=_PROVENANCE_SCRIPT,
        function="figure_schmidt_rank_vs_lambda",
        hyperparameters={"atol": float(H.SPECTRAL_RANK_ATOL)},
    )
    out = OUTPUT_DIR / "schmidt_rank.png"
    return _save(fig, out, metadata=_md("figure_schmidt_rank_vs_lambda"))


# ---------------------------------------------------------------------------
# Lifted figures (visualizations subpackage backing functions)
# ---------------------------------------------------------------------------


def figure_phase_landscape() -> Path:
    """Phase landscape over (λ, utility): heatmap of free energy."""
    lams = H.PHASE_LANDSCAPE_LAMBDAS.values()
    utilities = H.PHASE_LANDSCAPE_UTILITIES.values()
    score = np.zeros((utilities.size, lams.size), dtype=np.float64)
    for i, u in enumerate(utilities):
        for j, lam in enumerate(lams):
            score[i, j] = ising_free_energy_curve(float(lam), float(u))
    return plot_lambda_utility_heatmap(
        lams=lams,
        utilities=utilities,
        score=score,
        title="K=2 Ising: free energy F(λ, utility)",
        cbar_label="F  [nats]",
        out_path=OUTPUT_DIR / "phase_landscape.png",
        cmap="viridis",
        metadata=_md("figure_phase_landscape"),
    )


def figure_schmidt_entropy_surface() -> Path:
    """Schmidt entropy heatmap over (λ, utility)."""
    lams = H.PHASE_LANDSCAPE_LAMBDAS.values()
    utilities = H.PHASE_LANDSCAPE_UTILITIES.values()
    entropies = np.zeros((utilities.size, lams.size), dtype=np.float64)
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    # Manuscript symbols (J, Kc, G) — uppercase is intentional.
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])  # noqa: N806
    Kc = np.zeros((2, 2))  # noqa: N806
    for i, u in enumerate(utilities):
        # Utility shifts the per-stream G_k.
        G = [np.array([0.0, float(u)]), np.array([0.0, float(u)])]  # noqa: N806
        for j, lam in enumerate(lams):
            q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=float(lam))
            entropies[i, j] = entanglement_entropy(q)
    return plot_schmidt_entropy_surface(
        lams=lams,
        utilities=utilities,
        entropies=entropies,
        out_path=OUTPUT_DIR / "schmidt_entropy_surface.png",
        metadata=_md("figure_schmidt_entropy_surface"),
    )


def figure_joint_heatmap_with_marginals() -> Path:
    """Joint Ising posterior with marginals + residual."""
    lam = float(H.JOINT_HEATMAP_LAMBDA)
    q = ising_joint_posterior(lam)
    return plot_joint_heatmap_with_marginals(
        q=q,
        title=f"K=2 Ising joint posterior at λ={lam:g} (with m-projection residual)",
        out_path=OUTPUT_DIR / "joint_heatmap_lambda2.png",
        xticklabels=["π¹=0", "π¹=1"],
        yticklabels=["π²=0", "π²=1"],
        metadata=_md("figure_joint_heatmap_with_marginals"),
    )


def figure_archetype_dendrogram() -> Path:
    """Schmidt archetypes for the K=2 Ising joint."""
    q = ising_joint_posterior(float(H.ARCHETYPE_DENDROGRAM_LAMBDA))
    archetypes = schmidt_decomposition(q)
    weights = [a.weight for a in archetypes]
    R = len(archetypes)  # noqa: N806 — R = Schmidt rank (manuscript symbol).
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
        metadata=_md("figure_archetype_dendrogram"),
    )


def figure_tensor_train_ranks() -> Path:
    """TT rank profiles across K=2..5 streams under uniform coupling."""
    k_values = list(int(k) for k in H.TT_RANK_STREAM_COUNTS)
    profiles: list[list[int]] = []
    for n_streams in k_values:
        shape = tuple(2 for _ in range(n_streams))
        # Manuscript symbols (J, G, Kc) — uppercase is intentional.
        J = ising_coupling_tensor(shape, scale=1.0)  # noqa: N806
        mf = [np.array([0.5, 0.5]) for _ in range(n_streams)]
        G = [np.zeros(2) for _ in range(n_streams)]  # noqa: N806
        Kc = np.zeros(shape)  # noqa: N806
        q = entangled_posterior(
            mf,
            G,
            J,
            Kc,
            gamma=0.0,
            lam=float(H.TT_RANK_PROFILE_LAMBDA),
        )
        profiles.append(tensor_train_ranks(q, atol=float(H.SPECTRAL_RANK_ATOL)))
    return plot_tensor_train_rank_surface(
        k_values=k_values,
        rank_profiles=profiles,
        out_path=OUTPUT_DIR / "tensor_train_rank_surface.png",
        metadata=_md("figure_tensor_train_ranks"),
    )


def figure_log_weight_flow() -> Path:
    """e-geodesic: each policy's log-weight is affine in λ."""
    # Manuscript symbols (J, Kc, W) — uppercase is intentional.
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])  # noqa: N806
    Kc = np.array([[0.2, -0.1], [-0.1, 0.2]])  # noqa: N806
    lams = H.LOG_WEIGHT_FLOW_LAMBDAS.values()
    log_w = np.zeros((lams.size, 4), dtype=np.float64)
    for i, lam in enumerate(lams):
        W = coupling_log_weight(J, Kc, gamma=1.0, lam=float(lam))  # noqa: N806
        log_w[i, :] = W.reshape(-1)
    return plot_log_weight_flow(
        lams=lams,
        log_weights=log_w,
        out_path=OUTPUT_DIR / "log_weight_flow.png",
        pi_labels=["(0,0)", "(0,1)", "(1,0)", "(1,1)"],
        metadata=_md("figure_log_weight_flow"),
    )


def figure_kl_geodesic_in_simplex() -> Path:
    """KL geodesic of the K=2 Ising joint traced across $\\lambda \\in [0, 4]$
    in the 2-D summary plane (alignment fraction × off-diagonal disparity).
    """
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    # Manuscript symbols (G, J, Kc) — uppercase is intentional.
    G = [np.zeros(2), np.zeros(2)]  # noqa: N806
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])  # noqa: N806
    Kc = np.zeros((2, 2))  # noqa: N806
    lams = H.KL_GEODESIC_LAMBDAS.values()
    joints = [entangled_posterior(mf, G, J, Kc, gamma=0.0, lam=float(lam)) for lam in lams]
    return plot_kl_geodesic_in_simplex(
        lams=lams,
        joints=joints,
        out_path=OUTPUT_DIR / "kl_geodesic_simplex.png",
        metadata=_md("figure_kl_geodesic_in_simplex"),
    )


def figure_lambda_star_locus() -> Path:
    """Optimal coupling $\\lambda^\\star$ across (utility, gamma)."""
    utilities = H.LAMBDA_STAR_UTILITIES.values()
    gammas = H.LAMBDA_STAR_GAMMAS.values()
    lam_star = np.zeros((utilities.size, gammas.size), dtype=np.float64)
    for i, u in enumerate(utilities):
        for j, g in enumerate(gammas):
            # The K=2 Ising lam* is independent of gamma in the closed form
            # (see Appendix C); here we modulate the *effective* surplus by
            # gamma to expose the (utility, gamma) interaction.
            delta_eff = float(np.tanh(g * u))
            lam_star[i, j] = float(optimal_lambda(delta_eff))
    return plot_lambda_star_locus(
        utilities=utilities,
        gammas=gammas,
        lambda_star=lam_star,
        out_path=OUTPUT_DIR / "lambda_star_locus.png",
        metadata=_md("figure_lambda_star_locus"),
    )


def figure_coupling_graph() -> Path | None:
    """Coupling-potential graph for the configured Ising-like ensemble."""
    shape = tuple(2 for _ in range(int(H.COUPLING_GRAPH_STREAM_COUNT)))
    J = ising_coupling_tensor(shape, scale=1.0)  # noqa: N806 — manuscript symbol.
    return plot_coupling_graph(
        coupling_j=J,
        out_path=OUTPUT_DIR / "coupling_graph.png",
        threshold=0.0,
        metadata=_md("figure_coupling_graph"),
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def emit_all_figures() -> list[Path]:
    """Generate every analytical figure and return the emitted paths."""
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
    return figures


def main() -> None:
    """CLI entry point: emit every analytical figure and print its path."""
    for path in emit_all_figures():
        print(path)


__all__ = [
    "OUTPUT_DIR",
    "PROJECT_ROOT",
    "emit_all_figures",
    "figure_archetype_dendrogram",
    "figure_coupling_graph",
    "figure_coupling_tax_quadratic",
    "figure_free_energy_curve",
    "figure_ising_mi_curve",
    "figure_joint_heatmap_with_marginals",
    "figure_kl_geodesic_in_simplex",
    "figure_lambda_star_locus",
    "figure_log_weight_flow",
    "figure_optimal_lambda",
    "figure_phase_diagram",
    "figure_phase_landscape",
    "figure_schmidt_entropy_surface",
    "figure_schmidt_rank_vs_lambda",
    "figure_tensor_train_ranks",
    "main",
]


if __name__ == "__main__":
    main()
