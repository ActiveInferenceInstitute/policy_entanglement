"""pymdp POMDP-pipeline orchestration entry point.

CLI parsing, ``simulation.hyperparameters`` override application, and the
end-to-end run of every pymdp figure live here. Splitting the pipeline
from the figure functions (in :mod:`visualizations.pymdp_figures`) keeps
the thin :mod:`scripts.simulate_pymdp` orchestrator at <80 lines and
lets the override layer be unit-tested directly without spinning up the
matplotlib stack.

Workflow on :func:`main` invocation:

1. Parse argv (or :data:`sys.argv[1:]`) into a validated namespace.
2. Skip cleanly (exit 0) when pymdp is not importable — keeps the
   figure pipeline robust on lean CI runners.
3. Patch the requested ``simulation.hyperparameters`` constants for the
   lifetime of the process (no source edits — the run is bit-exact
   equivalent to pre-CLI behaviour when no flags are passed).
4. Re-seed the deterministic plotting stack and emit a structured
   ``main_start`` event via :data:`visualizations.pymdp_figures.LOGGER`.
5. Invoke every figure function and print the emitted artifact paths
   (one per line) for downstream manifest collection.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

from simulation import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the CLI override layer. Defaults reproduce :mod:`H` exactly."""
    p = argparse.ArgumentParser(
        prog="simulate_pymdp",
        description=(
            "Run the pymdp 1.0.1 POMDP simulation harness end-to-end. "
            "Defaults reproduce the manuscript figures bit-exactly; overrides "
            "patch simulation.hyperparameters for the lifetime of the process."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--ensemble-K", type=int, default=int(H.PYMDP_ENSEMBLE_K))
    p.add_argument("--gamma", type=float, default=float(H.PYMDP_ENSEMBLE_GAMMA))
    p.add_argument("--coupling-lambda", type=float, default=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA))
    p.add_argument("--sweep-lambda-min", type=float, default=float(H.PYMDP_SWEEP_LAMBDAS.start))
    p.add_argument("--sweep-lambda-max", type=float, default=float(H.PYMDP_SWEEP_LAMBDAS.stop))
    p.add_argument("--sweep-num", type=int, default=int(H.PYMDP_SWEEP_LAMBDAS.num))
    p.add_argument("--rollout-steps", type=int, default=int(H.PYMDP_ROLLOUT_STEPS))
    p.add_argument("--rollout-lambda", type=float, default=float(H.PYMDP_ROLLOUT_LAMBDA))
    p.add_argument("--rollout-seed", type=int, default=int(H.PYMDP_ROLLOUT_SEED))
    p.add_argument("--observations", type=int, nargs="+", default=list(H.PYMDP_SWEEP_OBSERVATIONS))
    p.add_argument("--figure-seed", type=int, default=int(H.FIGURE_GLOBAL_SEED))
    args = p.parse_args(argv)
    if args.ensemble_K < 2:
        p.error("--ensemble-K must be >= 2 (Ising harness assumes >= 2 streams)")
    if args.sweep_num < 2:
        p.error("--sweep-num must be >= 2")
    if args.sweep_lambda_max <= args.sweep_lambda_min:
        p.error("--sweep-lambda-max must be > --sweep-lambda-min")
    if args.rollout_steps < 1:
        p.error("--rollout-steps must be >= 1")
    if len(args.observations) != args.ensemble_K:
        p.error(f"--observations length {len(args.observations)} must equal --ensemble-K ({args.ensemble_K})")
    return args


def apply_overrides(args: argparse.Namespace) -> None:
    """Patch ``simulation.hyperparameters`` constants from CLI args.

    The constants are frozen at import time; we mutate the module attributes
    so every downstream ``H.PYMDP_*`` read picks up the override. The
    manuscript-variables JSON mirror reflects the new values automatically
    because it reads the same module.
    """
    H.PYMDP_ENSEMBLE_K = int(args.ensemble_K)
    H.PYMDP_ENSEMBLE_GAMMA = float(args.gamma)
    H.PYMDP_ENSEMBLE_COUPLING_LAMBDA = float(args.coupling_lambda)
    H.PYMDP_ROLLOUT_STEPS = int(args.rollout_steps)
    H.PYMDP_ROLLOUT_LAMBDA = float(args.rollout_lambda)
    H.PYMDP_ROLLOUT_SEED = int(args.rollout_seed)
    H.PYMDP_SWEEP_OBSERVATIONS = tuple(int(o) for o in args.observations)
    H.FIGURE_GLOBAL_SEED = int(args.figure_seed)
    # FigureGrid is a frozen dataclass; rebuild it.
    H.PYMDP_SWEEP_LAMBDAS = H.FigureGrid(
        float(args.sweep_lambda_min),
        float(args.sweep_lambda_max),
        int(args.sweep_num),
        label=H.PYMDP_SWEEP_LAMBDAS.label,
    )


def main(argv: list[str] | None = None) -> None:
    """CLI entry point — parses argv, applies overrides, runs every figure.

    Figure functions, ``LOGGER``, and the heavy matplotlib/pymdp stack are
    imported lazily so ``--help`` and validation failures surface before the
    expensive import chain runs.
    """
    args = parse_args(argv)

    from simulation.agents import pymdp_available

    if not pymdp_available():  # pragma: no cover
        print("pymdp not installed; skipping simulate_pymdp.py")
        print("Install via: uv sync --group sim")
        sys.exit(0)

    apply_overrides(args)

    from visualizations import pymdp_figures as figures_module
    from visualizations.setup import deterministic_setup

    deterministic_setup(seed=int(H.FIGURE_GLOBAL_SEED))
    logger = figures_module.LOGGER
    logger.fresh()
    logger.emit(
        {
            "script": "simulate_pymdp.py",
            "event": "main_start",
            "figure_global_seed": int(H.FIGURE_GLOBAL_SEED),
            "pymdp_ensemble_K": int(H.PYMDP_ENSEMBLE_K),
            "pymdp_ensemble_gamma": float(H.PYMDP_ENSEMBLE_GAMMA),
        }
    )

    csv_path, curve_path = figures_module.figure_pymdp_lambda_sweep()
    rollout_path = figures_module.figure_pymdp_rollout()
    fe_paths = figures_module.figure_pymdp_free_energies()
    emitted: tuple[Path, ...] = (csv_path, curve_path, rollout_path, *fe_paths)
    for p in emitted:
        print(p)
    logger.emit(
        {
            "script": "simulate_pymdp.py",
            "event": "main_end",
            "artifacts_emitted": [str(p) for p in emitted],
        }
    )


__all__ = ["apply_overrides", "main", "parse_args"]


if __name__ == "__main__":
    main()
