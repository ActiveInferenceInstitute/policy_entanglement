"""Revertibility witness sweep pipeline (computation + artifact emission)."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from simulation import hyperparameters as H  # noqa: N812
from simulation.agents import pymdp_available
from simulation.revertibility import RevertibilityRecord, revertibility_summary, revertibility_test
from visualizations.metadata import figure_metadata
from visualizations.multi_k_plots import plot_revertibility_witness
from visualizations.setup import deterministic_setup, ensure_outdir

FIG_DIR = Path("output/figures")
SIM_DIR = Path("output/simulations")
DATA_DIR = Path("output/data")


def revertibility_figure_metadata(
    project_root: Path,
    source_function: str,
    **extra: object,
) -> dict[str, str]:
    """Build figure-metadata snapshot for revertibility witness PNGs."""
    snapshot = {
        "lambdas": list(float(x) for x in H.REVERTIBILITY_LAMBDAS),
        "tolerance": float(H.REVERTIBILITY_TOLERANCE),
        "kl_identity_tolerance": float(H.REVERTIBILITY_KL_IDENTITY_TOLERANCE),
        "K": int(H.PYMDP_ENSEMBLE_K),
        "gamma": float(H.PYMDP_ENSEMBLE_GAMMA),
        "coupling_lambda_gen": float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
    }
    return figure_metadata(
        source_script="scripts/simulate_revertibility.py",
        source_function=source_function,
        hyperparameters=snapshot,
        extra=dict(extra) if extra else None,
        project_root=project_root,
    )


def write_revertibility_csv(path: Path, records: Sequence[RevertibilityRecord]) -> None:
    """Write ``pymdp_revertibility.csv`` rows from witness records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "lambda",
                "multi_information",
                "kl_q_to_mproj",
                "kl_identity_residual",
                "marginal_max_abs_diff",
                "marginals_match",
                "kl_identity_holds",
                "revertible",
            ]
        )
        for r in records:
            writer.writerow(
                [
                    f"{r.lam:.6f}",
                    f"{r.multi_information:.10g}",
                    f"{r.kl_q_to_mproj:.10g}",
                    f"{r.kl_identity_residual:.10g}",
                    f"{r.marginal_max_abs_diff:.10g}",
                    int(r.marginals_match),
                    int(r.kl_identity_holds),
                    int(r.revertible),
                ]
            )


def write_revertibility_summary(path: Path, records: Sequence[RevertibilityRecord]) -> dict[str, float]:
    """Write ``revertibility_summary.json`` and return the summary dict."""
    summary = revertibility_summary(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def run_revertibility_pipeline(
    *,
    project_root: Path,
    fig_dir: Path | None = None,
    sim_dir: Path | None = None,
    data_dir: Path | None = None,
) -> Mapping[str, Path]:
    """Run the revertibility witness sweep and emit CSV, PNG, and JSON artifacts."""
    fig_dir = fig_dir or project_root / FIG_DIR
    sim_dir = sim_dir or project_root / SIM_DIR
    data_dir = data_dir or project_root / DATA_DIR
    ensure_outdir(fig_dir)
    ensure_outdir(sim_dir)
    ensure_outdir(data_dir)
    deterministic_setup(seed=int(H.FIGURE_GLOBAL_SEED))

    print(
        f"[revertibility] testing {len(H.REVERTIBILITY_LAMBDAS)} λ values "
        f"(K={int(H.PYMDP_ENSEMBLE_K)}, γ={float(H.PYMDP_ENSEMBLE_GAMMA):.2f})",
        flush=True,
    )
    records = revertibility_test(
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        lambda_values=H.REVERTIBILITY_LAMBDAS,
        tolerance=float(H.REVERTIBILITY_TOLERANCE),
        kl_identity_tolerance=float(H.REVERTIBILITY_KL_IDENTITY_TOLERANCE),
    )
    for r in records:
        flag = "OK" if r.revertible else "FAIL"
        print(
            f"[revertibility] λ={r.lam:.3f}: I={r.multi_information:.6g}, "
            f"KL={r.kl_q_to_mproj:.6g}, |Δ|max={r.marginal_max_abs_diff:.2e}, "
            f"residual={r.kl_identity_residual:.2e}  {flag}",
            flush=True,
        )

    csv_path = sim_dir / "pymdp_revertibility.csv"
    write_revertibility_csv(csv_path, records)
    fig_path = plot_revertibility_witness(
        records,
        out_path=fig_dir / "revertibility_witness.png",
        metadata=revertibility_figure_metadata(project_root, "plot_revertibility_witness"),
    )
    summary_path = data_dir / "revertibility_summary.json"
    write_revertibility_summary(summary_path, records)
    return {"csv": csv_path, "figure": fig_path, "summary": summary_path}


def main(project_root: Path | None = None) -> int:
    """CLI entry: skip gracefully when pymdp is unavailable."""
    if not pymdp_available():  # pragma: no cover
        print("pymdp not installed; skipping simulate_revertibility.py")
        print("Install via: uv sync --group sim")
        return 0
    root = project_root or Path.cwd()
    paths = run_revertibility_pipeline(project_root=root)
    for p in paths.values():
        print(str(p))
    return 0


__all__ = [
    "DATA_DIR",
    "FIG_DIR",
    "SIM_DIR",
    "main",
    "revertibility_figure_metadata",
    "run_revertibility_pipeline",
    "write_revertibility_csv",
    "write_revertibility_summary",
]
