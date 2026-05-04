#!/usr/bin/env python3
"""Run the pymdp 1.0.1 POMDP simulation harness end-to-end.

Builds the K-stream Ising ensemble, runs:

  1. A λ-sweep at fixed observations (total-correlation curve + joint
     heatmaps at three sentinel λ values).
  2. A deterministic coupled rollout of T steps (mean-field marginals
     time-series + total-correlation curve).

Emits CSV and PNG artefacts under ``output/simulations/`` and
``output/figures/``.  Prints every output path to stdout for the
pipeline manifest.

Skipped (with a stdout note, exit 0) when the ``sim`` group is not
installed — keeps the figure pipeline robust on lean CI runners.
"""
from __future__ import annotations

import csv
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

import numpy as np  # noqa: E402

from agents import pymdp_available  # noqa: E402

if not pymdp_available():  # pragma: no cover
    print("pymdp not installed; skipping simulate_pymdp.py")
    print("Install via: uv sync --group sim")
    sys.exit(0)

from builders import make_ising_ensemble  # noqa: E402
from inference import coupled_policy_posterior  # noqa: E402
from joint_plots import plot_joint_heatmap_with_marginals  # noqa: E402
from rollout import simulate_coupled_rollout  # noqa: E402
from setup import deterministic_setup, ensure_outdir  # noqa: E402
from sweep import lambda_sweep  # noqa: E402
from trajectory_plots import plot_rollout_marginals  # noqa: E402

deterministic_setup(seed=42)

FIG_DIR = ensure_outdir(PROJECT_ROOT / "output" / "figures")
SIM_DIR = ensure_outdir(PROJECT_ROOT / "output" / "simulations")


def figure_pymdp_lambda_sweep() -> tuple[Path, Path]:
    """λ-sweep: total-correlation curve + sentinel-λ joint snapshots."""
    spec = make_ising_ensemble(coupling_lambda=1.0, K=2, gamma=1.0)
    obs = [0, 0]
    lams = np.linspace(0.0, 4.0, 21)
    sweep = lambda_sweep(spec, obs, lams)

    # CSV artefact for reproducibility.
    csv_path = SIM_DIR / "pymdp_lambda_sweep.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["lambda", "total_correlation", "is_pmf"])
        for r in sweep:
            writer.writerow([f"{r.lam:.4f}", f"{r.total_correlation:.10g}", int(r.is_pmf)])

    # Sentinel-λ heatmaps.  Pick lo/mid/hi from sweep.
    sentinels = [0, len(sweep) // 2, len(sweep) - 1]
    snapshot_paths: list[Path] = []
    for s in sentinels:
        r = sweep[s]
        out = FIG_DIR / f"pymdp_joint_lambda_{r.lam:.2f}.png"
        plot_joint_heatmap_with_marginals(
            q=r.joint,
            title=f"pymdp coupled K=2 Ising joint, λ={r.lam:.2f}",
            out_path=out,
            xticklabels=["u=0", "u=1"],
            yticklabels=["u=0", "u=1"],
        )
        snapshot_paths.append(out)

    # Total-correlation curve as a standalone PNG.
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(
        [r.lam for r in sweep],
        [r.total_correlation for r in sweep],
        "o-", linewidth=1.5, markersize=4, color="purple",
    )
    ax.set_xlabel("Coupling λ")
    ax.set_ylabel("Total correlation I(q_λ)  [nats]")
    ax.set_title("pymdp coupled K=2 Ising: total correlation vs λ")
    ax.grid(alpha=0.3)
    curve_path = FIG_DIR / "pymdp_total_correlation_curve.png"
    fig.tight_layout()
    fig.savefig(curve_path, bbox_inches="tight")
    plt.close(fig)

    return csv_path, curve_path


def figure_pymdp_rollout() -> Path:
    """Deterministic coupled rollout: per-stream marginals + total-corr curve."""
    spec = make_ising_ensemble(coupling_lambda=1.0, K=2, gamma=1.0)
    rollout = simulate_coupled_rollout(spec, T=10, lam=2.0, seed=0)

    # Stack per-stream marginals: each is (T, num_controls).
    marginals_per_stream = [
        np.stack([s.mean_field_marginals[k] for s in rollout.steps], axis=0)
        for k in range(spec.K())
    ]

    return plot_rollout_marginals(
        marginals_per_stream=marginals_per_stream,
        titles=[f"stream {k}: q_t^k" for k in range(spec.K())],
        total_correlations=rollout.total_correlations(),
        out_path=FIG_DIR / "pymdp_coupled_rollout.png",
    )


def main() -> None:
    csv_path, curve_path = figure_pymdp_lambda_sweep()
    rollout_path = figure_pymdp_rollout()
    for p in (csv_path, curve_path, rollout_path):
        print(p)


if __name__ == "__main__":
    main()
