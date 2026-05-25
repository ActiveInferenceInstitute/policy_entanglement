"""Pipeline regression gate (library implementation).

Business logic for :doc:`scripts/regression_gate.py </scripts/regression_gate>`.
Compares the current pipeline-run artifacts against a committed baseline and
fails (returns non-zero exit code) when any "silent degradation" is detected:

* Total test count has dropped by more than ``test_count_drop_max``.
* A test failed (``test_failed_max`` is exceeded).
* Code coverage has dropped by more than ``coverage_drop_pct_max`` percentage
  points.
* A critical module fell below its per-module coverage floor.
* Dashboard invariant report is missing/unparseable, or its count has dropped
  below ``invariant_count_min``.
* Lean budget gate has regressed (any ``sorry`` / ``axiom`` / ``unsafe``
  declaration introduced, or the recorded lake-job floor was lowered).

The module exposes a parameterised :func:`gate` plus the small helpers
(:func:`_parse_pytest_counts`, :func:`_critical_module_coverage_issues`, …)
that the test suite loads directly. The thin script wrapper
``scripts/regression_gate.py`` handles argparse + path defaults and re-exports
every symbol below for the importlib-based unit tests.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python <3.11 fallback
    import tomli as tomllib

CRITICAL_COVERAGE_MODULES: dict[str, float] = {
    "src/manuscript/status.py": 95.0,
    "src/manuscript/pdf_validation.py": 95.0,
    "src/visualizations/metadata.py": 95.0,
    "src/simulation/parameter_sweep.py": 95.0,
    "src/visualizations/btai_plots.py": 90.0,
}


def _coverage_fail_under(project_root: Path) -> float:
    """Read ``tool.coverage.report.fail_under`` from the project pyproject."""
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return 95.0
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    report = data.get("tool", {}).get("coverage", {}).get("report", {})
    return float(report.get("fail_under", 95.0))


_PYTEST_KINDS = {
    "passed",
    "failed",
    "skipped",
    "error",
    "errors",
    "xfailed",
    "xpassed",
}


def _ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def _fail(msg: str) -> None:
    print(f"  ✗ {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(f"  · {msg}")


def _load_baseline(baseline_path: Path) -> dict[str, Any]:
    if not baseline_path.exists():
        raise SystemExit(f"baseline missing: {baseline_path}")
    return cast(dict[str, Any], json.loads(baseline_path.read_text(encoding="utf-8")))


def _load_test_results(test_results_path: Path) -> dict[str, Any] | None:
    if not test_results_path.exists():
        return None
    return cast(dict[str, Any], json.loads(test_results_path.read_text(encoding="utf-8")))


def _parse_pytest_counts(output: str) -> dict[str, int]:
    """Extract pass/fail/skip counts from pytest's terminal summary."""
    counts = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "xfailed": 0,
        "xpassed": 0,
    }
    summary_line = ""
    for line in reversed(output.splitlines()):
        plain = re.sub(r"\x1b\[[0-9;]*m", "", line)
        if " in " not in plain:
            continue
        if any(f" {kind}" in plain for kind in _PYTEST_KINDS):
            summary_line = plain
            break
    for match in re.finditer(
        r"(\d+)\s+(passed|failed|skipped|errors?|xfailed|xpassed)",
        summary_line,
    ):
        count = int(match.group(1))
        kind = match.group(2)
        if kind == "error":
            kind = "errors"
        counts[kind] += count
    return counts


def _coverage_percent_from_json(path: Path) -> float:
    if not path.exists():
        return 0.0
    data = json.loads(path.read_text(encoding="utf-8"))
    totals = data.get("totals", {}) if isinstance(data, dict) else {}
    return float(totals.get("percent_covered", 0.0))


def _critical_module_coverage_issues(
    path: Path,
    thresholds: dict[str, float] | None = None,
) -> list[str]:
    """Return critical module coverage regressions from coverage.py JSON."""

    if not path.exists():
        return [f"coverage JSON missing: {path}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    files = data.get("files", {}) if isinstance(data, dict) else {}
    if not isinstance(files, dict):
        return ["coverage JSON has no files object"]
    issues: list[str] = []
    for module, floor in (thresholds or CRITICAL_COVERAGE_MODULES).items():
        payload = files.get(module)
        if not isinstance(payload, dict):
            issues.append(f"{module}: missing from coverage JSON")
            continue
        summary = payload.get("summary", {})
        if not isinstance(summary, dict) or "percent_covered" not in summary:
            issues.append(f"{module}: missing coverage summary")
            continue
        percent = float(summary.get("percent_covered", 0.0))
        if percent + 1e-9 < floor:
            issues.append(f"{module}: coverage {percent:.2f}% < floor {floor:.2f}%")
    return issues


def _clear_bytecode_cache(project_root: Path) -> int:
    """Remove every ``__pycache__`` dir and stray ``*.pyc`` under the project.

    A regression gate MUST be deterministic. Python only recompiles a
    ``.pyc`` when it judges the source newer; an edited-but-not-recompiled
    test/module (e.g. an mtime-preserving copy, a same-second edit) makes
    pytest import *stale* compiled code, so the same tree yields a red run
    and then a green run with no source change. That non-determinism is
    indistinguishable from a real regression and silently destroys trust
    in every "gate passed/failed" verdict. Clearing bytecode before the
    snapshot hardens the gate against the bytecode-staleness class. NOTE
    (RedTeam 2026-05-18): this is hardening of ONE class, not a proof of
    full determinism — the session-scoped conftest bootstrap remains a
    known order/clean-state surface, and the originally-observed flap's
    mechanism was never reproduced. The negative control (a real failure
    still fails) holds; 'deterministic by construction' would overclaim.

    ``.venv``/``.lake``/vendored trees are skipped (not ours; large).
    Returns the number of cache artifacts removed (for the log).
    """
    skip_parts = {".venv", ".lake", "node_modules", ".git"}
    removed = 0
    for cache_dir in project_root.rglob("__pycache__"):
        if skip_parts & set(cache_dir.parts):
            continue
        shutil.rmtree(cache_dir, ignore_errors=True)
        removed += 1
    for pyc in project_root.rglob("*.pyc"):
        if skip_parts & set(pyc.parts):
            continue
        try:
            pyc.unlink()
            removed += 1
        except OSError:
            pass
    return removed


def _write_fresh_test_results(
    *,
    project_root: Path,
    test_results_path: Path,
    pytest_log_path: Path,
    coverage_json_path: Path,
) -> dict[str, Any] | None:
    """Run the real pytest suite with coverage and write a fresh report.

    Bytecode is cleared immediately before this subprocess (see
    :func:`_clear_bytecode_cache`); we intentionally omit
    ``--import-mode=importlib`` because it duplicates script modules under
    alternate names and depresses measured ``src/`` coverage by ~6pp while
    adding no staleness protection beyond the cache purge.
    """
    reports_dir = test_results_path.parent
    reports_dir.mkdir(parents=True, exist_ok=True)
    removed = _clear_bytecode_cache(project_root)
    _info(f"cleared {removed} stale bytecode cache artifact(s) for a deterministic gate")
    fail_under = _coverage_fail_under(project_root)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--cov=src",
        f"--cov-report=json:{coverage_json_path}",
        "--cov-report=term",
        f"--cov-fail-under={fail_under:g}",
        "-q",
    ]
    env = {
        **os.environ,
        "PY_COLORS": "0",
        "MPLBACKEND": "Agg",
        # Belt-and-suspenders: never write bytecode during the gate run,
        # so a freshly-cleared tree cannot reacquire a stale .pyc mid-suite.
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    _info("running fresh pytest + coverage snapshot for regression gate")
    proc = subprocess.run(
        cmd,
        cwd=str(project_root),
        env=env,
        capture_output=True,
        text=True,
    )
    combined_output = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    pytest_log_path.write_text(combined_output, encoding="utf-8")

    counts = _parse_pytest_counts(combined_output)
    failed_total = counts["failed"] + counts["errors"]
    total = (
        counts["passed"]
        + counts["failed"]
        + counts["skipped"]
        + counts["errors"]
        + counts["xfailed"]
        + counts["xpassed"]
    )
    coverage_percent = _coverage_percent_from_json(coverage_json_path)
    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/regression_gate.py",
        "pytest_command": cmd,
        "pytest_returncode": proc.returncode,
        "pytest_log": str(pytest_log_path.relative_to(project_root)),
        "summary": {
            "total_tests": total,
            "total_failed": failed_total,
            "project_coverage": coverage_percent,
        },
        "project": {
            "passed": counts["passed"],
            "failed": failed_total,
            "skipped": counts["skipped"],
            "xfailed": counts["xfailed"],
            "xpassed": counts["xpassed"],
            "total": total,
            "coverage_percent": coverage_percent,
        },
    }
    test_results_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _info(f"pytest log written to {pytest_log_path.relative_to(project_root)}")
    _info(f"test report written to {test_results_path.relative_to(project_root)}")
    if proc.returncode != 0:
        _fail(f"pytest exited with code {proc.returncode}; see {pytest_log_path.relative_to(project_root)}")
    return report


def _count_invariants(invariants_path: Path) -> tuple[int, int] | None:
    """Return ``(passed, total)`` invariants from ``dashboard_invariants.txt``."""
    if not invariants_path.exists():
        return None
    txt = invariants_path.read_text(encoding="utf-8")
    # The summary line follows the pattern:
    #   "summary:      47/47 passed, 0 failed"
    m = re.search(r"summary:\s+(\d+)\s*/\s*(\d+)\s+passed", txt)
    if not m:
        return None
    passed = int(m.group(1))
    total = int(m.group(2))
    return passed, total


def _lean_budget_snapshot(*, project_root: Path, scripts_dir: Path) -> dict[str, int] | None:
    """Run ``build_lean.py`` and parse its budget summary line.

    Returns a dict ``{lake_jobs, sorries, axioms, unsafe}`` on success.
    """
    cmd = [sys.executable, str(scripts_dir / "build_lean.py")]
    proc = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    # Match: "OK  lake build succeeded · 20 .lean files · 0 sorries · 0 axioms · 0 unsafe..."
    summary = proc.stdout + "\n" + proc.stderr
    m_lake = re.search(r"\((\d+)\s+jobs?\)", summary) or re.search(r"(\d+)\s+lake\s+jobs?", summary)
    m_sorry = re.search(r"(\d+)\s+sorr", summary)
    m_axiom = re.search(r"(\d+)\s+axiom", summary)
    m_unsafe = re.search(r"(\d+)\s+unsafe", summary)
    if not (m_sorry and m_axiom and m_unsafe):
        return None
    return {
        # -1 is an explicit "could not parse" sentinel. Never default to
        # the passing floor value (21): a build-summary format change that
        # breaks the jobs regex must surface as a loud gate failure, not a
        # silent pass that masks a regressed Lean build.
        "lake_jobs": int(m_lake.group(1)) if m_lake else -1,
        "sorries": int(m_sorry.group(1)),
        "axioms": int(m_axiom.group(1)),
        "unsafe": int(m_unsafe.group(1)),
    }


def gate(
    *,
    project_root: Path,
    scripts_dir: Path,
    baseline_path: Path | None = None,
    update_baseline: bool = False,
) -> int:
    """Run the regression gate; return process exit code.

    Args:
        project_root: Project root (the ``actinf_policy_entanglement_lean``
            directory containing ``output/``, ``src/``, ``tests/``).
        scripts_dir: Project ``scripts/`` directory (used to locate
            ``build_lean.py`` and the baseline JSON).
        baseline_path: Override location of the committed baseline JSON.
            Defaults to ``scripts_dir / "regression_baseline.json"``.
        update_baseline: When True (and the gate passes), refresh the
            baseline file with the current run's metrics.

    Returns:
        ``0`` on a passing gate, ``1`` on any detected regression.
    """
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

    # ---- Test results --------------------------------------------------------
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
        # Schema: see `output/reports/test_results.json` (top-level
        # ``summary`` aggregate + per-suite ``project`` block).
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

    # ---- Dashboard invariants ------------------------------------------------
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

    # ---- Lean budget --------------------------------------------------------
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

    # ---- Maybe refresh baseline ---------------------------------------------
    if update_baseline and fail == 0 and test_results is not None and inv_pair is not None:
        baseline["test_count_min"] = max(int(baseline["test_count_min"]), cur_total)
        baseline["coverage_percent_min"] = max(
            float(baseline["coverage_percent_min"]),
            round(cur_cov - drift_cov / 2, 2),  # leave half the drift budget headroom
        )
        baseline["invariant_count_min"] = max(
            int(baseline["invariant_count_min"]),
            cur_inv_passed,
        )
        if lean is not None:
            baseline["lean_lake_jobs_min"] = max(
                int(baseline["lean_lake_jobs_min"]),
                lean["lake_jobs"],
            )
        baseline_path.write_text(
            json.dumps(baseline, indent=2) + "\n",
            encoding="utf-8",
        )
        _ok(f"baseline refreshed at {baseline_path.relative_to(project_root)}")

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
]
