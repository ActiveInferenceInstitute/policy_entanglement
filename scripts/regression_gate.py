#!/usr/bin/env python3
"""Thin CLI wrapper for the pipeline regression gate.

Business logic lives in :mod:`gates.regression_gate` (under ``src/``).
This script bootstraps the project's ``src/`` subpackages onto :data:`sys.path`,
parses command-line arguments, and dispatches to the library entry point.

The committed baseline JSON (``scripts/regression_baseline.json``) lives
alongside this script so the gate's contract is co-located with the CLI.

The module-level re-exports below preserve the tests' importlib contract
(``tests/test_regression_gate.py`` loads this file via
:func:`importlib.util.spec_from_file_location` and calls
``_parse_pytest_counts`` / ``_critical_module_coverage_issues`` directly).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
BASELINE_PATH = THIS_DIR / "regression_baseline.json"
TEST_RESULTS_PATH = PROJECT_ROOT / "output" / "reports" / "test_results.json"
PYTEST_LOG_PATH = PROJECT_ROOT / "output" / "reports" / "pytest_regression_gate.log"
COVERAGE_JSON_PATH = PROJECT_ROOT / "output" / "reports" / "coverage.json"
INVARIANTS_PATH = PROJECT_ROOT / "output" / "reports" / "dashboard_invariants.txt"

sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from gates.regression_gate import (  # noqa: E402,F401
    CRITICAL_COVERAGE_MODULES,
    _clear_bytecode_cache,
    _count_invariants,
    _coverage_percent_from_json,
    _critical_module_coverage_issues,
    _fail,
    _info,
    _lean_budget_snapshot,
    _load_baseline,
    _load_test_results,
    _ok,
    _parse_pytest_counts,
    _write_fresh_test_results,
)
from gates.regression_gate import (  # noqa: E402
    gate as _gate,
)


def gate(*, update_baseline: bool = False) -> int:
    """Run the regression gate against this project. See :func:`gates.regression_gate.gate`."""
    return _gate(
        project_root=PROJECT_ROOT,
        scripts_dir=THIS_DIR,
        baseline_path=BASELINE_PATH,
        update_baseline=update_baseline,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline regression gate (round-5 P0-3).")
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        default=False,
        help=(
            "If the gate passes, refresh `scripts/regression_baseline.json` "
            "with the current run's metrics.  Use at release time."
        ),
    )
    args = parser.parse_args(argv)
    return gate(update_baseline=args.update_baseline)


if __name__ == "__main__":
    sys.exit(main())
