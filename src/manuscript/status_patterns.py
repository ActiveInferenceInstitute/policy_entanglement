"""Stale status-document patterns and live metric comparators."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol


class LiveStatus(Protocol):
    @property
    def tests_total(self) -> int: ...

    @property
    def tests_passed(self) -> int: ...

    @property
    def tests_skipped(self) -> int: ...

    @property
    def tests_failed(self) -> int: ...

    @property
    def coverage_percent(self) -> float: ...

    @property
    def pdf_pages(self) -> int: ...

    @property
    def pdf_size_mb(self) -> float: ...

    @property
    def pdf_summary(self) -> str: ...


STATUS_DOCS: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "docs/README.md",
    "docs/AGENTS.md",
    "docs/guides/README.md",
    "docs/guides/build_run.md",
    "docs/guides/quickstart_recipes.md",
    "docs/guides/testing.md",
    "docs/reference/README.md",
    "docs/reference/statistics_reference.md",
    "docs/reference/veridical_status.md",
    "lean/AGENTS.md",
    "lean/ActinfPolicyEntanglement/AGENTS.md",
    "lean/FepSketches/AGENTS.md",
    "scripts/AGENTS.md",
    "scripts/README.md",
    "tests/AGENTS.md",
    "tests/README.md",
    "tests/lean/README.md",
)


def status_doc_paths(root: Path) -> list[Path]:
    """High-traffic status docs plus every docs markdown page."""

    explicit = [root / rel for rel in STATUS_DOCS]
    docs: list[Path] = []
    if (root / "docs").exists():
        docs = [
            path
            for path in sorted((root / "docs").rglob("*.md"))
            if "docs/_audit/" not in path.relative_to(root).as_posix()
        ]
    unique: dict[Path, None] = {}
    for path in [*explicit, *docs]:
        unique[path] = None
    return list(unique)


def stale_doc_patterns(live: LiveStatus | None) -> dict[str, str]:
    """Regex → remediation message for stale status literals."""

    return {
        r"\b844\b": (
            f"use live pytest collection count {live.tests_total}"
            if live
            else "replace with a live pytest-status pointer"
        ),
        r"\b843 passed\b": (
            f"use live pass count {live.tests_passed} passed" if live else "replace with a live pytest-status pointer"
        ),
        r"\b137 pages\b": f"use live PDF page count {live.pdf_pages} pages"
        if live
        else "replace with a live PDF-status pointer",
        r"\b5\.37 MB\b": f"use live PDF size {live.pdf_size_mb:.2f} MB"
        if live
        else "replace with a live PDF-status pointer",
        r"\b40\s+(?:PNGs?|figures)\b": "replace stale figure counts with release_readiness.json pointers",
        r"\b1026\s+tests\s+pass\b": "replace stale test counts with release_readiness.json pointers",
        r"\b8\s+skipped\b": "replace stale skip counts with release_readiness.json pointers",
        r"\b168[-\s]+page\b|\b168\s+pages\b": "replace stale PDF counts with release_readiness.json pointers",
        r"\b37\s+rendered\s+markdown\s+files\b": "replace stale rendered-manuscript counts with release_readiness.json pointers",
        r"scripts/execute_pipeline\.py": "use scripts/run_all.py or make readiness",
        r"output/actinf_policy_entanglement_lean(?:/|_combined\.pdf)": "use output/pdf/actinf_policy_entanglement_lean_combined.pdf",
        r"output/reports/(?:validation_report|pipeline_report)\.md": "use release_readiness.md/json and test_results.json",
        r"output/reports/mathlib_proofs\.json": (
            "use output/reports/release_readiness.json, output/MANIFEST.md, "
            "and scripts/build_mathlib_proofs.py for MathlibProofs evidence"
        ),
        r"\bv0_1\b|\bv0\.1\b": "use the current MathlibProofs version label or live readiness pointer",
        r"\b98\.48\s*%": (
            f"use live coverage {live.coverage_percent:.2f} %"
            if live
            else "replace with a live coverage-status pointer"
        ),
        r"\b98\.20\s*%": (
            f"use live coverage {live.coverage_percent:.2f} %"
            if live
            else "replace with a live coverage-status pointer"
        ),
        r"\b19/19 green exit\b": "use the live `lake build` job summary",
        r"full of `sorry` placeholders": "describe witness-form obligations, not strict `sorry`s",
        r"\b1653 statements\b": "avoid stale source-statement counts",
        r"src/pomdp_simulation\.py": "use the current `src/simulation/` module path",
        r"tests/test_pomdp_simulation\.py": "use the current `tests/test_simulation_pymdp.py` path",
        r"\[\[CITATION:": "use Pandoc citation keys such as [@key] or registry-backed [[CITELIST:topic]]",
        r"output/dashboards/": "use output/web/dashboard.html and output/data/dashboard_payload.json",
        r"schmidt_archetypes_": "use the current output/data/ising_archetypes.csv sidecar",
        r"current as of round 3": "point current-facing docs at live readiness artifacts, not historical round labels",
        r"Phase 0 complete": "replace retired phase labels with live boundary-state wording",
    }


def stale_literal_issues(text: str, rel: str, patterns: dict[str, str]) -> list[str]:
    issues: list[str] = []
    for pattern, replacement in patterns.items():
        if re.search(pattern, text):
            issues.append(f"{rel}: stale status literal {pattern!r}; {replacement}")
    return issues


def live_status_line_issues(rel: str, line_no: int, line: str, live: LiveStatus) -> list[str]:
    issues: list[str] = []
    lowered = line.lower()
    table_match = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
    if table_match:
        metric = table_match.group(1).strip().lower()
        value = table_match.group(2).strip()
        if metric == "tests collected":
            count_match = re.search(r"\b(\d+)\b", value)
            if count_match:
                got = int(count_match.group(1))
                if got != live.tests_total:
                    issues.append(f"{rel}:{line_no}: tests collected table count {got} != live {live.tests_total}")
        if metric == "passing":
            pass_skip = re.search(r"\b(\d+)\s+passed\s*\+\s*(\d+)\s+skipped\b", value)
            if pass_skip:
                got_passed = int(pass_skip.group(1))
                got_skipped = int(pass_skip.group(2))
                if live.tests_failed == 0 and (got_passed != live.tests_passed or got_skipped != live.tests_skipped):
                    issues.append(
                        f"{rel}:{line_no}: pass/skip summary "
                        f"{got_passed}/{got_skipped} != live "
                        f"{live.tests_passed}/{live.tests_skipped}"
                    )
        if "coverage" in metric and "src" in metric:
            cov_match = re.match(r"\s*([0-9]+(?:\.[0-9]+)?)\s*%", value)
            if cov_match:
                got_cov = float(cov_match.group(1))
                if abs(got_cov - live.coverage_percent) > 0.01:
                    issues.append(f"{rel}:{line_no}: coverage {got_cov:.2f}% != live {live.coverage_percent:.2f}%")

    if "pytest" in lowered or "test" in lowered or "python" in lowered:
        for match in re.finditer(r"\b(\d+)[-\s]+collected\b", line):
            got = int(match.group(1))
            if got != live.tests_total:
                issues.append(f"{rel}:{line_no}: pytest collected count {got} != live {live.tests_total}")
        for match in re.finditer(r"\b(\d+)\s+pytest items\b", line):
            got = int(match.group(1))
            if got != live.tests_total:
                issues.append(f"{rel}:{line_no}: pytest item count {got} != live {live.tests_total}")
        for match in re.finditer(r"\b(\d+)\s+items\b", line):
            got = int(match.group(1))
            if got != live.tests_total and "pytest" in line.lower():
                issues.append(f"{rel}:{line_no}: pytest item count {got} != live {live.tests_total}")
        if "tests collected" in lowered:
            for match in re.finditer(r"\b(\d+)\s+tests collected\b", lowered):
                got = int(match.group(1))
                if got != live.tests_total:
                    issues.append(f"{rel}:{line_no}: tests collected count {got} != live {live.tests_total}")
        pass_skip = re.search(r"\b(\d+)\s+passed\s*\+\s*(\d+)\s+skipped\b", line)
        if pass_skip:
            got_passed = int(pass_skip.group(1))
            got_skipped = int(pass_skip.group(2))
            if live.tests_failed == 0 and (got_passed != live.tests_passed or got_skipped != live.tests_skipped):
                issues.append(
                    f"{rel}:{line_no}: pass/skip summary "
                    f"{got_passed}/{got_skipped} != live "
                    f"{live.tests_passed}/{live.tests_skipped}"
                )
    pdf_match = re.search(r"\b(\d+)\s+pages,\s*([0-9]+(?:\.[0-9]+)?)\s+MB\b", line)
    if pdf_match:
        got_pages = int(pdf_match.group(1))
        got_mb = float(pdf_match.group(2))
        if got_pages != live.pdf_pages or abs(got_mb - live.pdf_size_mb) > 0.01:
            issues.append(f"{rel}:{line_no}: PDF summary {got_pages} pages, {got_mb:.2f} MB != live {live.pdf_summary}")
    if (
        ("coverage on `src`" in lowered or ("coverage" in lowered and "`src`" in lowered))
        and "floor" not in lowered
        and "≥" not in line
        and ">=" not in line
    ):
        cov_match = re.search(r"\b([0-9]+(?:\.[0-9]+)?)\s*%", line)
        if cov_match:
            got_cov = float(cov_match.group(1))
            if abs(got_cov - live.coverage_percent) > 0.01:
                issues.append(f"{rel}:{line_no}: coverage {got_cov:.2f}% != live {live.coverage_percent:.2f}%")
    return issues
