"""Multi-K ensemble sweep pipeline (K>2 streams)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from simulation import hyperparameters as H  # noqa: N812 - H = hyperparameters (manuscript convention).
from simulation.agents import pymdp_available
from simulation.multi_k_experiments import multi_k_summary, run_multi_k_sweep
from visualizations.metadata import figure_metadata
from visualizations.multi_k_plots import (
    plot_multi_k_aligned_mass,
    plot_multi_k_total_correlation,
    plot_multi_k_tt_rank_profile,
)
from visualizations.setup import deterministic_setup, ensure_outdir


def figure_metadata_snapshot(project_root: Path, source_function: str, **extra) -> dict[str, str]:
    snapshot = {
        "K_values": list(int(k) for k in H.MULTI_K_VALUES),
        "gamma": float(H.PYMDP_ENSEMBLE_GAMMA),
        "coupling_lambda_gen": float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        "sweep_grid_points": int(H.MULTI_K_SWEEP_LAMBDAS.num),
        "sweep_lambda_max": float(H.MULTI_K_SWEEP_LAMBDAS.stop),
        "figure_global_seed": int(H.FIGURE_GLOBAL_SEED),
    }
    return figure_metadata(
        source_script="scripts/simulate_multi_k.py",
        source_function=source_function,
        hyperparameters=snapshot,
        extra=dict(extra) if extra else None,
        project_root=project_root,
    )


def write_multi_k_csv(sim_dir: Path, k: int, results) -> Path:
    csv_path = sim_dir / f"pymdp_K{k}_sweep.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "lambda",
                "total_correlation",
                "joint_entropy",
                "marginal_entropy_sum",
                "coupling_term",
                "aligned_mass",
                "tt_ranks",
            ]
        )
        for row in results:
            writer.writerow(
                [
                    f"{row.lam:.6f}",
                    f"{row.total_correlation:.10g}",
                    f"{row.joint_entropy:.10g}",
                    f"{sum(row.marginal_entropies):.10g}",
                    f"{row.coupling_term:.10g}",
                    f"{row.aligned_mass:.10g}",
                    "|".join(str(int(x)) for x in row.tt_ranks),
                ]
            )
    return csv_path


def run_multi_k_pipeline(project_root: Path) -> int:
    if not pymdp_available():  # pragma: no cover
        print("pymdp not installed; skipping simulate_multi_k.py")
        print("Install via: uv sync --group sim")
        return 0

    fig_dir = project_root / "output" / "figures"
    sim_dir = project_root / "output" / "simulations"
    data_dir = project_root / "output" / "data"
    ensure_outdir(fig_dir)
    ensure_outdir(sim_dir)
    ensure_outdir(data_dir)
    deterministic_setup(seed=int(H.FIGURE_GLOBAL_SEED))

    lams = list(H.MULTI_K_SWEEP_LAMBDAS.values())
    results_by_k: dict[int, list] = {}
    summaries: dict[str, object] = {}

    for k in H.MULTI_K_VALUES:
        k_int = int(k)
        print(f"[multi-K] K={k_int}: sweeping {len(lams)} λ values...", flush=True)
        results = run_multi_k_sweep(
            k_int,
            lams,
            coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
            gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        )
        results_by_k[k_int] = results
        csv_path = write_multi_k_csv(sim_dir, k_int, results)
        print(f"[multi-K] K={k_int}: wrote {csv_path}", flush=True)
        sub = multi_k_summary(results)
        for sub_k, sub_v in sub.items():
            summaries[f"multi_k_K{k_int}_{sub_k}"] = float(sub_v)
        summaries[f"multi_information_K{k_int}_lambda_{int(H.MULTI_K_SENTINEL_LAMBDA)}"] = float(
            next(
                (r.total_correlation for r in results if abs(r.lam - float(H.MULTI_K_SENTINEL_LAMBDA)) < 1e-9),
                results[-1].total_correlation,
            )
        )

    def md(fn: str, **extra) -> dict[str, str]:
        return figure_metadata_snapshot(project_root, fn, **extra)

    tc_png = plot_multi_k_total_correlation(
        results_by_k,
        out_path=fig_dir / "multi_k_total_correlation.png",
        metadata=md("plot_multi_k_total_correlation"),
    )
    aligned_png = plot_multi_k_aligned_mass(
        results_by_k,
        out_path=fig_dir / "multi_k_aligned_mass.png",
        metadata=md("plot_multi_k_aligned_mass"),
    )
    tt_png = plot_multi_k_tt_rank_profile(
        results_by_k,
        out_path=fig_dir / "multi_k_tt_rank_profile.png",
        lam_index=-1,
        metadata=md("plot_multi_k_tt_rank_profile"),
    )

    summary_path = data_dir / "multi_k_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2, sort_keys=True) + "\n")

    for path in (
        summary_path,
        tc_png,
        aligned_png,
        tt_png,
        *(sim_dir / f"pymdp_K{int(k)}_sweep.csv" for k in H.MULTI_K_VALUES),
    ):
        print(str(path))
    return 0
