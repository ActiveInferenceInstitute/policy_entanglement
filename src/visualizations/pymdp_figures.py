"""Figure builders for the pymdp-backed simulation pipeline.

Importable equivalents of the historical ``scripts/simulate_pymdp.py``
``figure_pymdp_*`` functions. Each builder:

* Runs the real ``pymdp`` simulation (no mocks).
* Writes the long-form CSV / JSON artifacts manuscript variables and
  downstream regression tests rely on.
* Emits every PNG via :func:`visualizations._io._save_with_metadata` so
  the reproducibility tEXt chunks travel with the figures.
* Returns the emitted paths so :mod:`simulation.pymdp_pipeline` (or the
  thin ``scripts/simulate_pymdp.py`` wrapper, which re-exports the module
  attributes) can print them for manifest collection.

The module-level :data:`FIG_DIR`, :data:`SIM_DIR`, :data:`LOGGER`, and
:data:`SOURCE_SCRIPT` constants are the default sinks used by the no-arg
``figure_pymdp_*`` callables. Tests that monkeypatch these names on the
thin script (or directly on this module) flow into the next figure call
because the no-arg wrappers re-read the module globals at every
invocation. The metadata helper :func:`build_metadata` keeps PNG
provenance stamps source-of-truth and parameterised by the caller's
``source_script`` so the script-side wrapper can keep
``project.source_script == "scripts/simulate_pymdp.py"``.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from simulation import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).
from simulation.builders import make_ising_ensemble
from simulation.inference import (
    decomposition_witness_curve,
    free_energy_curve,
)
from simulation.logging_utils import RunLogger, default_logger
from simulation.rollout import simulate_coupled_rollout
from simulation.statistics import (
    pymdp_summary_statistics,
    summary_to_var_dict,
)
from simulation.sweep import lambda_sweep
from visualizations._io import _save_with_metadata as _save
from visualizations.annotations import add_stats_box, apply_lambda_axis
from visualizations.free_energy_plots import (
    plot_action_distribution_evolution,
    plot_efe_under_posterior,
    plot_entropy_decomposition,
    plot_free_energy_panel,
    plot_vfe_decomposition,
)
from visualizations.joint_plots import plot_joint_heatmap_with_marginals
from visualizations.metadata import figure_metadata
from visualizations.pymdp_extras import (
    plot_action_entropy_curve,
    plot_kl_to_lambda_zero,
    plot_marginal_entropy_per_stream,
    plot_pymdp_summary_panel,
)
from visualizations.setup import PUBLICATION_STYLE, ensure_outdir, palette_color
from visualizations.trajectory_plots import plot_rollout_marginals

#: Type alias for the per-figure metadata factory: ``(source_function, **extra) → dict``.
MetadataFactory = Callable[..., dict[str, Any]]

#: Resolved at import time to ``projects/actinf_policy_entanglement_lean/``.
#: ``__file__`` lives at ``<project>/src/visualizations/pymdp_figures.py`` →
#: ``parents[2]`` is the project root regardless of how ``sys.path`` is
#: assembled (script bootstrap or direct ``-m`` execution).
PROJECT_ROOT = Path(__file__).resolve().parents[2]

#: Default source-script tag stamped into every emitted PNG. The thin
#: ``scripts/simulate_pymdp.py`` wrapper re-exports the same string, so
#: existing reproducibility tooling keeps seeing the canonical script path.
SOURCE_SCRIPT = "scripts/simulate_pymdp.py"

#: Default sink for every figure PNG emitted by this module.
FIG_DIR: Path = ensure_outdir(PROJECT_ROOT / "output" / "figures")

#: Default sink for every long-form simulation artefact (CSV, JSON).
SIM_DIR: Path = ensure_outdir(PROJECT_ROOT / "output" / "simulations")

#: Shared structured logger used for ``[run_logger]`` events around every
#: figure. Reused across calls inside a single process.
LOGGER: RunLogger = default_logger(PROJECT_ROOT)


def hyperparam_snapshot() -> dict[str, object]:
    """Hyperparameter snapshot used by every emitted figure's metadata."""
    return {
        "K": int(H.PYMDP_ENSEMBLE_K),
        "gamma": float(H.PYMDP_ENSEMBLE_GAMMA),
        "coupling_lambda_gen": float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        "sweep_grid_points": int(H.PYMDP_SWEEP_LAMBDAS.num),
        "sweep_lambda_max": float(H.PYMDP_SWEEP_LAMBDAS.stop),
        "rollout_steps": int(H.PYMDP_ROLLOUT_STEPS),
        "rollout_seed": int(H.PYMDP_ROLLOUT_SEED),
        "rollout_lambda": float(H.PYMDP_ROLLOUT_LAMBDA),
        "observations": list(H.PYMDP_SWEEP_OBSERVATIONS),
        "figure_global_seed": int(H.FIGURE_GLOBAL_SEED),
    }


def build_metadata(
    source_function: str,
    *,
    source_script: str = SOURCE_SCRIPT,
    project_root: Path = PROJECT_ROOT,
    extra: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Build PNG metadata for a given pymdp figure function.

    Args:
        source_function: Name of the calling ``figure_pymdp_*`` function.
        source_script: Path string stamped into ``project.source_script``;
            defaults to the canonical script path so PNGs continue to
            attribute provenance to ``scripts/simulate_pymdp.py`` even when
            generated through the src-side entry point.
        project_root: Project root used to resolve git revision.
        extra: Optional dict merged into the metadata payload (e.g. panel
            name for multi-panel figures).
    """
    return figure_metadata(
        source_script=source_script,
        source_function=source_function,
        hyperparameters=hyperparam_snapshot(),
        extra=dict(extra) if extra else None,
        project_root=project_root,
    )


def _md(source_function: str, **extra: object) -> dict[str, str]:
    """Module-level metadata factory used by the no-arg figure wrappers."""
    return build_metadata(source_function, extra=extra or None)


def _figure_pymdp_lambda_sweep_impl(
    *,
    fig_dir: Path,
    sim_dir: Path,
    logger: RunLogger,
    metadata_factory: MetadataFactory,
) -> tuple[Path, Path]:
    """λ-sweep implementation; see :func:`figure_pymdp_lambda_sweep`."""
    spec = make_ising_ensemble(
        coupling_amplitude=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    obs = list(H.PYMDP_SWEEP_OBSERVATIONS)
    lams = H.PYMDP_SWEEP_LAMBDAS.values()
    with logger.timed(
        script="simulate_pymdp.py",
        section="figure_pymdp_lambda_sweep",
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        observations=list(obs),
        grid_points=int(lams.size),
        lambda_min=float(lams[0]),
        lambda_max=float(lams[-1]),
    ) as ctx:
        sweep = lambda_sweep(spec, obs, lams)
        ctx.update(
            policy_shape=list(spec.policy_shape()),
            tc_min=float(min(r.total_correlation for r in sweep)),
            tc_max=float(max(r.total_correlation for r in sweep)),
            all_pmf=bool(all(r.is_pmf for r in sweep)),
        )

    csv_path = sim_dir / "pymdp_lambda_sweep.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["lambda", "total_correlation", "is_pmf"])
        for r in sweep:
            writer.writerow([f"{r.lam:.4f}", f"{r.total_correlation:.10g}", int(r.is_pmf)])

    sentinels = [0, len(sweep) // 2, len(sweep) - 1]
    md = metadata_factory("figure_pymdp_lambda_sweep")
    for s in sentinels:
        r = sweep[s]
        out = fig_dir / f"pymdp_joint_lambda_{r.lam:.2f}.png"
        plot_joint_heatmap_with_marginals(
            q=r.joint,
            title=f"pymdp coupled K=2 Ising joint, λ={r.lam:.2f}",
            out_path=out,
            xticklabels=["u=0", "u=1"],
            yticklabels=["u=0", "u=1"],
            metadata=metadata_factory("figure_pymdp_lambda_sweep", panel=f"joint_lambda_{r.lam:.2f}"),
        )

    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    tcs = [r.total_correlation for r in sweep]
    ax.plot(
        [r.lam for r in sweep],
        tcs,
        "o-",
        linewidth=2.0,
        markersize=5,
        color=palette_color(7),
    )
    apply_lambda_axis(ax)
    ax.set_ylabel("Total correlation I(q_λ)  [nats]")
    ax.set_title("pymdp coupled K=2 Ising: total correlation vs λ")
    add_stats_box(
        ax,
        {
            "grid": len(sweep),
            "TC max": float(max(tcs)),
            "all PMF": all(r.is_pmf for r in sweep),
        },
        loc="lower right",
    )
    curve_path = fig_dir / "pymdp_total_correlation_curve.png"
    return csv_path, _save(fig, curve_path, metadata=md)


def _figure_pymdp_rollout_impl(
    *,
    fig_dir: Path,
    logger: RunLogger,
    metadata_factory: MetadataFactory,
) -> Path:
    """Rollout implementation; see :func:`figure_pymdp_rollout`."""
    spec = make_ising_ensemble(
        coupling_amplitude=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    with logger.timed(
        script="simulate_pymdp.py",
        section="figure_pymdp_rollout",
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        horizon=int(H.PYMDP_ROLLOUT_STEPS),
        lam=float(H.PYMDP_ROLLOUT_LAMBDA),
        seed=int(H.PYMDP_ROLLOUT_SEED),
    ) as ctx:
        rollout = simulate_coupled_rollout(
            spec,
            horizon=int(H.PYMDP_ROLLOUT_STEPS),
            lam=float(H.PYMDP_ROLLOUT_LAMBDA),
            seed=int(H.PYMDP_ROLLOUT_SEED),
        )
        tcs = rollout.total_correlations()
        ctx.update(
            steps_emitted=len(rollout.steps),
            tc_initial=float(tcs[0]),
            tc_final=float(tcs[-1]),
            sampled_actions=[list(s.sampled_actions) for s in rollout.steps],
        )

    marginals_per_stream = [
        np.stack([s.mean_field_marginals[k] for s in rollout.steps], axis=0) for k in range(spec.num_streams())
    ]

    return plot_rollout_marginals(
        marginals_per_stream=marginals_per_stream,
        titles=[f"stream {k}: q_t^k" for k in range(spec.num_streams())],
        total_correlations=rollout.total_correlations(),
        out_path=fig_dir / "pymdp_coupled_rollout.png",
        metadata=metadata_factory("figure_pymdp_rollout"),
    )


def _figure_pymdp_free_energies_impl(
    *,
    fig_dir: Path,
    sim_dir: Path,
    logger: RunLogger,
    metadata_factory: MetadataFactory,
) -> tuple[Path, ...]:
    """Free-energy implementation; see :func:`figure_pymdp_free_energies`."""
    spec = make_ising_ensemble(
        coupling_amplitude=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    obs = list(H.PYMDP_SWEEP_OBSERVATIONS)
    lams = H.PYMDP_SWEEP_LAMBDAS.values()
    with logger.timed(
        script="simulate_pymdp.py",
        section="figure_pymdp_free_energies",
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        observations=list(obs),
        grid_points=int(lams.size),
        lambda_min=float(lams[0]),
        lambda_max=float(lams[-1]),
    ) as ctx:
        bundles = free_energy_curve(spec, obs, lams)
        decomposition_witnesses = decomposition_witness_curve(spec, obs, lams)
        summary = pymdp_summary_statistics(bundles)
        residual_max = max(w.residual for w in decomposition_witnesses)
        ctx.update(
            tc_min=float(min(b.total_correlation for b in bundles)),
            tc_max=float(max(b.total_correlation for b in bundles)),
            vfe_total_min=float(min(b.vfe_total for b in bundles)),
            vfe_total_max=float(max(b.vfe_total for b in bundles)),
            decomposition_residual_max=float(residual_max),
            coupling_term_at_lambda_zero=float(bundles[0].coupling_term),
            joint_entropy_at_lambda_zero=float(bundles[0].joint_entropy),
            marginal_entropy_sum_at_lambda_zero=float(bundles[0].marginal_entropies.sum()),
            tc_at_half_saturation=float(summary.tc_at_half_saturation),
            lambda_at_half_saturation=float(summary.lambda_at_half_saturation),
        )

    csv_path = sim_dir / "pymdp_free_energy_bundle.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        K = bundles[0].vfe_per_stream.shape[0]  # noqa: N806 — K = number of streams (manuscript symbol).
        header = [
            "lambda",
            "vfe_total",
            "joint_entropy",
            "marginal_entropy_sum",
            "total_correlation",
            "coupling_term",
            "decomposition_lhs",
            "decomposition_rhs",
            "decomposition_residual",
        ]
        for k in range(K):
            header += [f"vfe_stream_{k}", f"efe_under_posterior_stream_{k}", f"marginal_entropy_{k}"]
        writer.writerow(header)
        for b, w in zip(bundles, decomposition_witnesses, strict=True):
            row = [
                f"{b.lam:.6f}",
                f"{b.vfe_total:.10g}",
                f"{b.joint_entropy:.10g}",
                f"{b.marginal_entropies.sum():.10g}",
                f"{b.total_correlation:.10g}",
                f"{b.coupling_term:.10g}",
                f"{w.lhs:.10g}",
                f"{w.rhs:.10g}",
                f"{w.residual:.10g}",
            ]
            for k in range(K):
                row += [
                    f"{b.vfe_per_stream[k]:.10g}",
                    f"{b.efe_under_posterior[k]:.10g}",
                    f"{b.marginal_entropies[k]:.10g}",
                ]
            writer.writerow(row)

    summary_path = sim_dir / "pymdp_summary.json"
    summary_record = summary_to_var_dict(summary)
    summary_record.update(
        {
            "pymdp_decomposition_residual_max": float(residual_max),
            "pymdp_decomposition_residual_mean": float(np.mean([w.residual for w in decomposition_witnesses])),
        }
    )
    summary_path.write_text(
        json.dumps(summary_record, indent=2, sort_keys=True) + "\n",
    )

    base = "figure_pymdp_free_energies"
    vfe_png = plot_vfe_decomposition(
        bundles,
        out_path=fig_dir / "pymdp_vfe_decomposition.png",
        metadata=metadata_factory(base, panel="vfe_decomposition"),
    )
    efe_png = plot_efe_under_posterior(
        bundles,
        out_path=fig_dir / "pymdp_efe_under_posterior.png",
        metadata=metadata_factory(base, panel="efe_under_posterior"),
    )
    ent_png = plot_entropy_decomposition(
        bundles,
        out_path=fig_dir / "pymdp_entropy_decomposition.png",
        metadata=metadata_factory(base, panel="entropy_decomposition"),
    )
    act_png = plot_action_distribution_evolution(
        bundles,
        out_path=fig_dir / "pymdp_action_distribution.png",
        metadata=metadata_factory(base, panel="action_distribution"),
    )
    panel_png = plot_free_energy_panel(
        bundles,
        out_path=fig_dir / "pymdp_free_energy_panel.png",
        metadata=metadata_factory(base, panel="four_panel"),
    )

    extras_md = metadata_factory("figure_pymdp_free_energies_extras")
    # aH = action-entropy figure, Hk = per-stream entropy figure (manuscript symbols).
    aH_png = plot_action_entropy_curve(  # noqa: N806
        bundles,
        out_path=fig_dir / "pymdp_action_entropy.png",
        metadata=extras_md,
    )
    kl_png = plot_kl_to_lambda_zero(
        bundles,
        out_path=fig_dir / "pymdp_kl_to_lambda_zero.png",
        metadata=extras_md,
    )
    Hk_png = plot_marginal_entropy_per_stream(  # noqa: N806
        bundles,
        out_path=fig_dir / "pymdp_marginal_entropy_per_stream.png",
        metadata=extras_md,
    )
    summary_png = plot_pymdp_summary_panel(
        bundles,
        out_path=fig_dir / "pymdp_summary_panel.png",
        summary=summary,
        metadata=extras_md,
    )

    return (
        csv_path,
        summary_path,
        vfe_png,
        efe_png,
        ent_png,
        act_png,
        panel_png,
        aH_png,
        kl_png,
        Hk_png,
        summary_png,
    )


def figure_pymdp_lambda_sweep() -> tuple[Path, Path]:
    """λ-sweep: total-correlation curve + sentinel-λ joint snapshots.

    Reads :data:`FIG_DIR`, :data:`SIM_DIR`, :data:`LOGGER`, and :func:`_md`
    from this module's namespace at every call so tests (or callers) that
    monkeypatch those names see the override on the next invocation.
    """
    return _figure_pymdp_lambda_sweep_impl(
        fig_dir=FIG_DIR,
        sim_dir=SIM_DIR,
        logger=LOGGER,
        metadata_factory=_md,
    )


def figure_pymdp_rollout() -> Path:
    """Deterministic coupled rollout: per-stream marginals + TC curve.

    Reads :data:`FIG_DIR`, :data:`LOGGER`, and :func:`_md` from this
    module's namespace at every call.
    """
    return _figure_pymdp_rollout_impl(
        fig_dir=FIG_DIR,
        logger=LOGGER,
        metadata_factory=_md,
    )


def figure_pymdp_free_energies() -> tuple[Path, ...]:
    """Compute the full free-energy bundle and emit nine PNGs + one CSV + one JSON.

    Reads :data:`FIG_DIR`, :data:`SIM_DIR`, :data:`LOGGER`, and :func:`_md`
    from this module's namespace at every call.
    """
    return _figure_pymdp_free_energies_impl(
        fig_dir=FIG_DIR,
        sim_dir=SIM_DIR,
        logger=LOGGER,
        metadata_factory=_md,
    )


__all__ = [
    "FIG_DIR",
    "LOGGER",
    "MetadataFactory",
    "PROJECT_ROOT",
    "SIM_DIR",
    "SOURCE_SCRIPT",
    "_md",
    "build_metadata",
    "figure_pymdp_free_energies",
    "figure_pymdp_lambda_sweep",
    "figure_pymdp_rollout",
    "hyperparam_snapshot",
]
