"""Dashboard facade — re-exports types, CLI, payload, and panel assembly."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, cast

from dashboard_types import panels as _panels
from dashboard_types.cli import parse_dashboard_args
from dashboard_types.paths import (
    DASHBOARD_PROJECT_ROOT,
    DATA_DIR,
    OUTPUT,
    REP_DIR,
    WEB_DIR,
)
from dashboard_types.payload import build_dashboard_payload as _build_dashboard_payload
from dashboard_types.types import Control, Invariant, Panel


def build_dashboard_payload(args: argparse.Namespace) -> dict[str, Any]:
    return _build_dashboard_payload(args)


def build_dashboard(args: argparse.Namespace, payload: dict[str, Any]) -> Any:
    return _panels.build_dashboard(args, payload)


def write_dashboard(args: argparse.Namespace) -> dict[str, Path]:
    """Compute, build, and persist all dashboard artifacts."""
    payload = build_dashboard_payload(args)
    d = build_dashboard(args, payload)
    return cast(
        dict[str, Path],
        d.write(
            html_path=args.html_out,
            json_path=args.json_out,
            invariants_path=args.invariants_out,
            txt_path=args.summary_out,
        ),
    )


def main(argv: list[str] | None = None) -> None:
    """CLI entry point: parse args, build, persist, exit non-zero on invariant fail."""
    args = parse_dashboard_args(argv)
    payload = build_dashboard_payload(args)
    d = build_dashboard(args, payload)
    out = d.write(
        html_path=args.html_out,
        json_path=args.json_out,
        invariants_path=args.invariants_out,
        txt_path=args.summary_out,
    )
    for k in ("html", "json", "invariants", "summary"):
        if k in out:
            print(out[k])

    failed = [i for i in d.evaluate_invariants() if not i["passed"]]
    if failed:
        names = ", ".join(i["name"] for i in failed)
        print(f"FAILED INVARIANTS: {names}", file=sys.stderr)
        sys.exit(1)


__all__ = [
    "Control",
    "DASHBOARD_PROJECT_ROOT",
    "DATA_DIR",
    "Invariant",
    "OUTPUT",
    "Panel",
    "REP_DIR",
    "WEB_DIR",
    "build_dashboard",
    "build_dashboard_payload",
    "main",
    "parse_dashboard_args",
    "write_dashboard",
]
