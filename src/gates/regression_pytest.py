"""Pytest subprocess runner and coverage parsers for the regression gate."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python <3.11 fallback
    import tomli as tomllib

from gates.regression_baseline import fail as _fail
from gates.regression_baseline import info as _info

CRITICAL_COVERAGE_MODULES: dict[str, float] = {
    "src/manuscript/status.py": 95.0,
    "src/manuscript/pdf_validation.py": 95.0,
    "src/visualizations/metadata.py": 95.0,
    "src/simulation/parameter_sweep.py": 95.0,
    "src/visualizations/btai_plots.py": 90.0,
}

_PYTEST_KINDS = {
    "passed",
    "failed",
    "skipped",
    "error",
    "errors",
    "xfailed",
    "xpassed",
}


def coverage_fail_under(project_root: Path) -> float:
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return 95.0
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    report = data.get("tool", {}).get("coverage", {}).get("report", {})
    return float(report.get("fail_under", 95.0))


def parse_pytest_counts(output: str) -> dict[str, int]:
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


def coverage_percent_from_json(path: Path) -> float:
    if not path.exists():
        return 0.0
    data = json.loads(path.read_text(encoding="utf-8"))
    totals = data.get("totals", {}) if isinstance(data, dict) else {}
    return float(totals.get("percent_covered", 0.0))


def critical_module_coverage_issues(
    path: Path,
    thresholds: dict[str, float] | None = None,
) -> list[str]:
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


def clear_bytecode_cache(project_root: Path) -> int:
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


def write_fresh_test_results(
    *,
    project_root: Path,
    test_results_path: Path,
    pytest_log_path: Path,
    coverage_json_path: Path,
) -> dict[str, Any] | None:
    reports_dir = test_results_path.parent
    reports_dir.mkdir(parents=True, exist_ok=True)
    removed = clear_bytecode_cache(project_root)
    _info(f"cleared {removed} stale bytecode cache artifact(s) for a deterministic gate")
    fail_under = coverage_fail_under(project_root)
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

    counts = parse_pytest_counts(combined_output)
    failed_total = counts["failed"] + counts["errors"]
    total = (
        counts["passed"]
        + counts["failed"]
        + counts["skipped"]
        + counts["errors"]
        + counts["xfailed"]
        + counts["xpassed"]
    )
    coverage_percent = coverage_percent_from_json(coverage_json_path)
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


def count_invariants(invariants_path: Path) -> tuple[int, int] | None:
    if not invariants_path.exists():
        return None
    txt = invariants_path.read_text(encoding="utf-8")
    m = re.search(r"summary:\s+(\d+)\s*/\s*(\d+)\s+passed", txt)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def lean_budget_snapshot(*, project_root: Path, scripts_dir: Path) -> dict[str, int] | None:
    cmd = [sys.executable, str(scripts_dir / "build_lean.py")]
    proc = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    summary = proc.stdout + "\n" + proc.stderr
    m_lake = re.search(r"\((\d+)\s+jobs?\)", summary) or re.search(r"(\d+)\s+lake\s+jobs?", summary)
    m_sorry = re.search(r"(\d+)\s+sorr", summary)
    m_axiom = re.search(r"(\d+)\s+axiom", summary)
    m_unsafe = re.search(r"(\d+)\s+unsafe", summary)
    if not (m_sorry and m_axiom and m_unsafe):
        return None
    return {
        "lake_jobs": int(m_lake.group(1)) if m_lake else -1,
        "sorries": int(m_sorry.group(1)),
        "axioms": int(m_axiom.group(1)),
        "unsafe": int(m_unsafe.group(1)),
    }


__all__ = [
    "CRITICAL_COVERAGE_MODULES",
    "clear_bytecode_cache",
    "count_invariants",
    "coverage_fail_under",
    "coverage_percent_from_json",
    "critical_module_coverage_issues",
    "lean_budget_snapshot",
    "parse_pytest_counts",
    "write_fresh_test_results",
]
