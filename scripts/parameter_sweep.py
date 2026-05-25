#!/usr/bin/env python3
"""Sweep coupling λ over a configurable grid and emit a CSV.

Thin orchestrator: argument parsing only — sweep computation and
CSV writing live in :mod:`simulation.parameter_sweep`.

The defaults reproduce the canonical manuscript sweep, so existing
pipeline runs are unaffected. Override the λ grid, utility surplus
levels, phase thresholds, or Schmidt truncation tolerance with CLI
flags; see ``--help``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np  # noqa: E402

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from simulation import hyperparameters as H  # noqa: E402,N812 — H = hyperparameters (manuscript convention).
from simulation.parameter_sweep import run as _run_sweep  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "output" / "data"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Build the CLI. Defaults reproduce the canonical manuscript sweep."""
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--lam-min",
        type=float,
        default=float(H.PARAMETER_SWEEP_LAMBDAS.start),
        help="lower bound on the λ-sweep grid (default from hyperparameters)",
    )
    p.add_argument(
        "--lam-max",
        type=float,
        default=float(H.PARAMETER_SWEEP_LAMBDAS.stop),
        help="upper bound on the λ-sweep grid (default from hyperparameters)",
    )
    p.add_argument(
        "--num",
        type=int,
        default=int(H.PARAMETER_SWEEP_LAMBDAS.num),
        help="number of grid points (default from hyperparameters)",
    )
    p.add_argument(
        "--utilities",
        type=float,
        nargs="+",
        default=[0.0, 1.0, 2.0],
        help="utility surplus values to evaluate the FE curve at",
    )
    p.add_argument(
        "--lam-c1",
        type=float,
        default=float(H.PHASE_LAMBDA_C1),
        help="lower phase threshold (default from hyperparameters)",
    )
    p.add_argument(
        "--lam-c2",
        type=float,
        default=float(H.PHASE_LAMBDA_C2),
        help="upper phase threshold (default from hyperparameters)",
    )
    p.add_argument(
        "--schmidt-atol",
        type=float,
        default=1e-9,
        help="absolute tolerance for Schmidt-rank truncation (default 1e-9)",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR / "parameter_sweep.csv",
        help="output CSV path (default: output/data/parameter_sweep.csv)",
    )
    args = p.parse_args(argv)
    if args.num < 2:
        p.error("--num must be ≥ 2")
    if args.lam_max <= args.lam_min:
        p.error("--lam-max must be strictly greater than --lam-min")
    if args.lam_c2 < args.lam_c1:
        p.error("--lam-c2 must be ≥ --lam-c1")
    if len(args.utilities) < 1:
        p.error("--utilities must list at least one value")
    return args


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    lams = np.linspace(args.lam_min, args.lam_max, args.num)
    out = _run_sweep(
        lams=lams,
        utilities=args.utilities,
        lam_c1=args.lam_c1,
        lam_c2=args.lam_c2,
        schmidt_atol=args.schmidt_atol,
        output_path=args.output,
    )
    print(out)


if __name__ == "__main__":
    main()
