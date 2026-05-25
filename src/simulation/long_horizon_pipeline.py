"""Long-horizon coupled rollout pipeline."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from simulation import hyperparameters as H  # noqa: N812 - H = hyperparameters (manuscript convention).
from simulation.agents import pymdp_available
from simulation.long_horizon import long_horizon_rollout, long_horizon_summary
from visualizations.metadata import figure_metadata
from visualizations.multi_k_plots import plot_long_horizon_marginals, plot_long_horizon_steady_state
from visualizations.setup import deterministic_setup, ensure_outdir


def figure_metadata_snapshot(project_root: Path, source_function: str, **extra) -> dict[str, str]:
    snapshot = {
        "horizon": int(H.LONG_HORIZON_STEPS),
        "lam": float(H.LONG_HORIZON_LAMBDA),
        "seed": int(H.LONG_HORIZON_SEED),
        "K": int(H.PYMDP_ENSEMBLE_K),
        "gamma": float(H.PYMDP_ENSEMBLE_GAMMA),
        "coupling_lambda_gen": float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        "tail_window": int(H.LONG_HORIZON_TAIL_WINDOW),
        "steady_state_tol": float(H.LONG_HORIZON_STEADY_STATE_TOL),
    }
    return figure_metadata(
        source_script="scripts/simulate_long_horizon.py",
        source_function=source_function,
        hyperparameters=snapshot,
        extra=dict(extra) if extra else None,
        project_root=project_root,
    )


def run_long_horizon_pipeline(project_root: Path) -> int:
    if not pymdp_available():  # pragma: no cover
        print("pymdp not installed; skipping simulate_long_horizon.py")
        print("Install via: uv sync --group sim")
        return 0

    fig_dir = project_root / "output" / "figures"
    sim_dir = project_root / "output" / "simulations"
    data_dir = project_root / "output" / "data"
    ensure_outdir(fig_dir)
    ensure_outdir(sim_dir)
    ensure_outdir(data_dir)
    deterministic_setup(seed=int(H.FIGURE_GLOBAL_SEED))

    start_t = time.perf_counter()
    last_progress: list[int] = [0]
    horizon = int(H.LONG_HORIZON_STEPS)

    def _progress(step: int, total: int) -> None:
        if step - last_progress[0] >= 10 or step == total:
            last_progress[0] = step
            elapsed = time.perf_counter() - start_t
            print(
                f"[long-horizon] step {step}/{total} ({100.0 * step / max(total, 1):.1f}%, {elapsed:.1f}s elapsed)",
                flush=True,
            )

    print(
        f"[long-horizon] starting T={horizon} rollout "
        f"(K={int(H.PYMDP_ENSEMBLE_K)}, λ={float(H.LONG_HORIZON_LAMBDA):.2f}, "
        f"seed={int(H.LONG_HORIZON_SEED)})",
        flush=True,
    )
    result = long_horizon_rollout(
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        horizon=horizon,
        lam=float(H.LONG_HORIZON_LAMBDA),
        seed=int(H.LONG_HORIZON_SEED),
        tail_window=int(H.LONG_HORIZON_TAIL_WINDOW),
        steady_state_tol=float(H.LONG_HORIZON_STEADY_STATE_TOL),
        progress_callback=_progress,
    )
    elapsed = time.perf_counter() - start_t
    print(
        f"[long-horizon] finished {horizon} steps in {elapsed:.2f}s (habit_accumulation={result.habit_accumulation})",
        flush=True,
    )

    csv_path = sim_dir / "pymdp_long_horizon.csv"
    n_streams = len(result.marginal_trajectories)
    with csv_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        header = ["t", "total_correlation"]
        for k in range(n_streams):
            marg = result.marginal_trajectories[k]
            for u in range(marg.shape[1]):
                header.append(f"q{k}_u{u}")
        writer.writerow(header)
        for t in range(result.T):
            row = [t, f"{result.total_correlations[t]:.10g}"]
            for k in range(n_streams):
                marg = result.marginal_trajectories[k]
                for u in range(marg.shape[1]):
                    row.append(f"{marg[t, u]:.10g}")
            writer.writerow(row)

    def md(fn: str, **extra) -> dict[str, str]:
        return figure_metadata_snapshot(project_root, fn, **extra)

    marg_png = plot_long_horizon_marginals(
        result,
        out_path=fig_dir / "long_horizon_marginals.png",
        metadata=md("plot_long_horizon_marginals"),
    )
    ss_png = plot_long_horizon_steady_state(
        result,
        out_path=fig_dir / "long_horizon_steady_state.png",
        metadata=md("plot_long_horizon_steady_state"),
    )

    summary = long_horizon_summary(result)
    summary_path = data_dir / "long_horizon_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    for path in (csv_path, marg_png, ss_png, summary_path):
        print(str(path))
    return 0
