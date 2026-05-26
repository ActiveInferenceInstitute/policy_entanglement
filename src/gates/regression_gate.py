"""Pipeline regression gate (library implementation)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from gates.regression_baseline import (
    fail as _fail,
)
from gates.regression_baseline import (
    info as _info,
)
from gates.regression_baseline import (
    load_baseline as _load_baseline,
)
from gates.regression_baseline import (
    load_test_results as _load_test_results,
)
from gates.regression_baseline import (
    ok as _ok,
)
from gates.regression_baseline import (
    refresh_baseline,
)
from gates.regression_pytest import (
    CRITICAL_COVERAGE_MODULES,
    subprocess,  # noqa: F401 — test monkeypatch target
)
from gates.regression_pytest import (
    clear_bytecode_cache as _clear_bytecode_cache,
)
from gates.regression_pytest import (
    count_invariants as _count_invariants,
)
from gates.regression_pytest import (
    coverage_fail_under as _coverage_fail_under,
)
from gates.regression_pytest import (
    coverage_percent_from_json as _coverage_percent_from_json,
)
from gates.regression_pytest import (
    critical_module_coverage_issues as _critical_module_coverage_issues,
)
from gates.regression_pytest import (
    lean_budget_snapshot as _lean_budget_snapshot,
)
from gates.regression_pytest import (
    parse_pytest_counts as _parse_pytest_counts,
)
from gates.regression_pytest import (
    write_fresh_test_results as _write_fresh_test_results,
)


def gate(
    *,
    project_root: Path,
    scripts_dir: Path,
    baseline_path: Path | None = None,
    update_baseline: bool = False,
) -> int:
    """Run the regression gate; return process exit code."""
    baseline_path = baseline_path or scripts_dir / "regression_baseline.json"
    test_results_path = project_root / "output" / "reports" / "test_results.json"
    pytest_log_path = project_root / "output" / "reports" / "pytest_regression_gate.log"
    coverage_json_path = project_root / "output" / "reports" / "coverage.json"
    invariants_path = project_root / "output" / "reports" / "dashboard_invariants.txt"

    print("[regression-gate]")
    baseline = _load_baseline(baseline_path)
    tol = baseline.get("tolerance", {})
    drift_test = int(tol.get("test_count_drop_max", 2))
    drift_cov = float(tol.get("coverage_drop_pct_max", 1.0))

    if os.environ.get("REGRESSION_GATE_USE_EXISTING_TEST_REPORT") == "1":
        _info("using existing test_results.json by explicit environment override")
        test_results = _load_test_results(test_results_path)
    else:
        test_results = _write_fresh_test_results(
            project_root=project_root,
            test_results_path=test_results_path,
            pytest_log_path=pytest_log_path,
            coverage_json_path=coverage_json_path,
        )
    fail = 0
    cur_total = cur_failed = 0
    cur_cov = 0.0
    if test_results is None:
        _info(f"missing {test_results_path.relative_to(project_root)}; skipping test/coverage gate")
    else:
        if int(test_results.get("pytest_returncode", 0)) != 0:
            fail += 1
        summary = test_results.get("summary", {}) or {}
        project = test_results.get("project", {}) or {}
        cur_total = int(
            summary.get("total_tests")
            or project.get("total", 0)
            or (int(project.get("passed", 0)) + int(project.get("failed", 0)))
        )
        cur_failed = int(summary.get("total_failed", project.get("failed", 0)))
        cur_cov = float(summary.get("project_coverage", project.get("coverage_percent", 0.0)))

        baseline_test_floor = int(baseline.get("test_count_min", 0)) - drift_test
        if cur_total < baseline_test_floor:
            _fail(
                f"test count regressed: {cur_total} < "
                f"baseline_min({baseline['test_count_min']}) - drift({drift_test}) "
                f"= {baseline_test_floor}"
            )
            fail += 1
        else:
            _ok(f"test count {cur_total} ≥ baseline floor {baseline_test_floor}")

        if cur_failed > int(baseline.get("test_failed_max", 0)):
            _fail(f"test failures: {cur_failed} > max {baseline['test_failed_max']}")
            fail += 1
        else:
            _ok(f"test failures {cur_failed} ≤ max {baseline['test_failed_max']}")

        cov_floor = float(baseline.get("coverage_percent_min", 0.0)) - drift_cov
        if cur_cov + 1e-9 < cov_floor:
            _fail(
                f"coverage regressed: {cur_cov:.2f}% < "
                f"baseline_min({baseline['coverage_percent_min']:.2f}%) - drift({drift_cov:.2f}%) "
                f"= {cov_floor:.2f}%"
            )
            fail += 1
        else:
            _ok(f"coverage {cur_cov:.2f}% ≥ floor {cov_floor:.2f}%")

        critical_coverage_issues = _critical_module_coverage_issues(coverage_json_path)
        if critical_coverage_issues:
            for issue in critical_coverage_issues:
                _fail(f"critical module coverage: {issue}")
            fail += len(critical_coverage_issues)
        else:
            module_list = ", ".join(CRITICAL_COVERAGE_MODULES)
            _ok(f"critical module coverage floors met: {module_list}")

    inv_pair = _count_invariants(invariants_path)
    cur_inv_passed = cur_inv_total = 0
    if inv_pair is None:
        _fail(
            f"invariant report missing or unparseable: {invariants_path.relative_to(project_root)}; "
            "run `uv run python scripts/build_dashboard.py` before regression_gate.py"
        )
        fail += 1
    else:
        cur_inv_passed, cur_inv_total = inv_pair
        inv_floor = int(baseline.get("invariant_count_min", 0))
        if cur_inv_passed < inv_floor:
            _fail(f"invariants regressed: {cur_inv_passed} passed < floor {inv_floor}")
            fail += 1
        else:
            _ok(f"invariants {cur_inv_passed}/{cur_inv_total} ≥ floor {inv_floor}")

    lean = _lean_budget_snapshot(project_root=project_root, scripts_dir=scripts_dir)
    if lean is None:
        _info("could not snapshot Lean budget (build_lean.py output unparseable); skipping Lean gate")
    else:
        lake_floor = int(baseline.get("lean_lake_jobs_min", 21))
        if lean["lake_jobs"] < 0:
            _fail(
                "lake jobs count unparseable from build_lean.py output (summary format changed?) — refusing to assume the floor"
            )
            fail += 1
        elif lean["lake_jobs"] < lake_floor:
            _fail(f"lake jobs regressed: {lean['lake_jobs']} < floor {lake_floor}")
            fail += 1
        else:
            _ok(f"lake jobs {lean['lake_jobs']} ≥ floor {lake_floor}")
        for name, key in (("sorries", "lean_sorry_max"), ("axioms", "lean_axiom_max"), ("unsafe", "lean_unsafe_max")):
            ceil = int(baseline.get(key, 0))
            if lean[name] > ceil:
                _fail(f"Lean {name} regressed: {lean[name]} > max {ceil}")
                fail += 1
            else:
                _ok(f"Lean {name} = {lean[name]} ≤ max {ceil}")

    if update_baseline and fail == 0 and test_results is not None and inv_pair is not None:
        refresh_baseline(
            baseline,
            baseline_path=baseline_path,
            project_root=project_root,
            cur_total=cur_total,
            cur_cov=cur_cov,
            cur_inv_passed=cur_inv_passed,
            lean=lean,
            drift_cov=drift_cov,
        )

    print()
    if fail == 0:
        print("Regression gate passed.")
        return 0
    print(f"REGRESSION GATE FAILED: {fail} issue(s)", file=sys.stderr)
    return 1


__all__ = [
    "CRITICAL_COVERAGE_MODULES",
    "_clear_bytecode_cache",
    "_count_invariants",
    "_coverage_fail_under",
    "_coverage_percent_from_json",
    "_critical_module_coverage_issues",
    "_fail",
    "_info",
    "_lean_budget_snapshot",
    "_load_baseline",
    "_load_test_results",
    "_ok",
    "_parse_pytest_counts",
    "_write_fresh_test_results",
    "gate",
    "subprocess",
]
