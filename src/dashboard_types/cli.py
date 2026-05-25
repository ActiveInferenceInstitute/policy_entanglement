"""Dashboard CLI argument parsing."""

from __future__ import annotations

import argparse
from pathlib import Path

from dashboard_types.paths import DATA_DIR, REP_DIR, WEB_DIR


def parse_dashboard_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the dashboard CLI argument set.

    Defaults reproduce the canonical manuscript sweep so existing pipeline runs
    are unaffected.
    """
    p = argparse.ArgumentParser(
        description=("Build the interactive simulation dashboard for actinf_policy_entanglement_lean."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--lam-min", type=float, default=0.0)
    p.add_argument("--lam-max", type=float, default=6.0)
    p.add_argument("--num", type=int, default=121)
    p.add_argument(
        "--utilities",
        type=float,
        nargs="+",
        default=[0.0, 1.0, 2.0],
        help="utility surplus levels for the FE curve panel",
    )
    p.add_argument("--lam-c1", type=float, default=0.5)
    p.add_argument("--lam-c2", type=float, default=2.5)
    p.add_argument("--schmidt-atol", type=float, default=1e-9)
    p.add_argument(
        "--probe-lambdas",
        type=float,
        nargs="+",
        default=[0.0, 1.0, 2.0, 4.0],
        help="λ values offered as joint-heatmap snapshots",
    )
    p.add_argument("--html-out", type=Path, default=WEB_DIR / "dashboard.html")
    p.add_argument("--json-out", type=Path, default=DATA_DIR / "dashboard_payload.json")
    p.add_argument("--invariants-out", type=Path, default=REP_DIR / "dashboard_invariants.txt")
    p.add_argument("--summary-out", type=Path, default=REP_DIR / "dashboard_summary.txt")
    args = p.parse_args(argv)
    if args.num < 2:
        p.error("--num must be ≥ 2")
    if args.lam_max <= args.lam_min:
        p.error("--lam-max must be > --lam-min")
    return args


__all__ = ["parse_dashboard_args"]
