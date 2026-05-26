"""Regression gate baseline I/O and comparison helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, cast


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def fail(msg: str) -> None:
    print(f"  ✗ {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(f"  · {msg}")


def load_baseline(baseline_path: Path) -> dict[str, Any]:
    if not baseline_path.exists():
        raise SystemExit(f"baseline missing: {baseline_path}")
    return cast(dict[str, Any], json.loads(baseline_path.read_text(encoding="utf-8")))


def load_test_results(test_results_path: Path) -> dict[str, Any] | None:
    if not test_results_path.exists():
        return None
    return cast(dict[str, Any], json.loads(test_results_path.read_text(encoding="utf-8")))


def refresh_baseline(
    baseline: dict[str, Any],
    *,
    baseline_path: Path,
    project_root: Path,
    cur_total: int,
    cur_cov: float,
    cur_inv_passed: int,
    lean: dict[str, int] | None,
    drift_cov: float,
) -> None:
    baseline["test_count_min"] = max(int(baseline["test_count_min"]), cur_total)
    baseline["coverage_percent_min"] = max(
        float(baseline["coverage_percent_min"]),
        round(cur_cov - drift_cov / 2, 2),
    )
    baseline["invariant_count_min"] = max(int(baseline["invariant_count_min"]), cur_inv_passed)
    if lean is not None:
        baseline["lean_lake_jobs_min"] = max(int(baseline["lean_lake_jobs_min"]), lean["lake_jobs"])
    baseline_path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    ok(f"baseline refreshed at {baseline_path.relative_to(project_root)}")


__all__ = [
    "fail",
    "info",
    "load_baseline",
    "load_test_results",
    "ok",
    "refresh_baseline",
]
