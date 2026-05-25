"""Live project-status facts for README / AGENTS / docs validation.

The project intentionally keeps volatile status numbers out of prose
where possible.  When a visible onboarding document does quote them
(pytest collection count, pass/skip split, PDF pages / size), this
module derives the expected values from generated artifacts and gives
validators one place to detect stale literals.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from manuscript.status_patterns import (
    live_status_line_issues,
    stale_doc_patterns,
    stale_literal_issues,
    status_doc_paths,
)


@dataclass(frozen=True)
class ProjectStatus:
    """Live status summary derived from generated artifacts."""

    tests_total: int
    tests_passed: int
    tests_skipped: int
    tests_failed: int
    coverage_percent: float
    pdf_pages: int
    pdf_size_bytes: int

    @property
    def pdf_size_mb(self) -> float:
        """Decimal MB, matching the rendered PDF byte count."""
        return self.pdf_size_bytes / 1_000_000.0

    @property
    def test_summary(self) -> str:
        """Human-readable pytest summary used in docs."""
        return f"{self.tests_total} collected; {self.tests_passed} passed + {self.tests_skipped} skipped"

    @property
    def pdf_summary(self) -> str:
        """Human-readable PDF summary used in docs."""
        return f"{self.pdf_pages} pages, {self.pdf_size_mb:.2f} MB"


def _parse_latex_pdf_log(pdf_path: Path) -> tuple[int, int]:
    """Return ``(pages, bytes)`` from the adjacent LaTeX log fallback."""
    candidates = (
        pdf_path.with_suffix(".log"),
        pdf_path.parent / "_combined_manuscript.log",
    )
    for log_path in candidates:
        if not log_path.exists():
            continue
        text = log_path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"Output written on .+ \((\d+) pages?\)", text)
        if match:
            return int(match.group(1)), pdf_path.stat().st_size
    raise RuntimeError(f"could not find a LaTeX page-count fallback for {pdf_path}")


def _parse_pdfinfo(pdf_path: Path) -> tuple[int, int]:
    """Return ``(pages, bytes)`` from ``pdfinfo`` or the LaTeX log fallback."""
    try:
        proc = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            check=False,
            text=True,
            timeout=5.0,
        )
    except FileNotFoundError:
        return _parse_latex_pdf_log(pdf_path)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"could not run pdfinfo for {pdf_path}: {exc}") from exc
    if proc.returncode != 0:
        raise RuntimeError(f"pdfinfo failed for {pdf_path}: {proc.stderr.strip()}")
    pages = None
    size_bytes = None
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":", 1)[1].strip())
        if line.startswith("File size:"):
            match = re.search(r"(\d+)\s+bytes", line)
            if match:
                size_bytes = int(match.group(1))
    if pages is None or size_bytes is None:
        raise RuntimeError(f"pdfinfo did not expose pages and size for {pdf_path}")
    return pages, size_bytes


def load_project_status(project_root: Path) -> ProjectStatus:
    """Load live status from regression output and the rendered PDF."""
    root = Path(project_root)
    test_path = root / "output" / "reports" / "test_results.json"
    pdf_path = root / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf"
    data = json.loads(test_path.read_text(encoding="utf-8"))
    project = data["project"]
    summary = data.get("summary", {})
    coverage = project.get("coverage_percent", summary.get("project_coverage"))
    if coverage is None:
        cov_path = root / "output" / "reports" / "coverage.json"
        if cov_path.exists():
            cov_data = json.loads(cov_path.read_text(encoding="utf-8"))
            coverage = float(cov_data.get("totals", {}).get("percent_covered", 0.0))
        else:
            raise KeyError("coverage_percent missing from test_results.json and coverage.json")
    pages, size_bytes = _parse_pdfinfo(pdf_path)
    return ProjectStatus(
        tests_total=int(project["total"]),
        tests_passed=int(project["passed"]),
        tests_skipped=int(project["skipped"]),
        tests_failed=int(project["failed"]),
        coverage_percent=float(coverage),
        pdf_pages=int(pages),
        pdf_size_bytes=int(size_bytes),
    )


def _status_doc_paths(root: Path) -> list[Path]:
    return status_doc_paths(root)


def stale_status_issues(
    project_root: Path,
    status: ProjectStatus | None = None,
    *,
    require_live: bool = True,
) -> list[str]:
    """Return stale-count issues in high-traffic status documents.

    ``scripts/run_all.py`` validates the manuscript before the regression
    gate writes ``output/reports/test_results.json``.  In that clean-output
    state, callers can pass ``require_live=False``: fixed stale literals are
    still rejected, while live table comparisons are deferred until the
    generated status artifacts exist.
    """
    root = Path(project_root)
    live: ProjectStatus | None = status
    if live is None:
        try:
            live = load_project_status(root)
        except (FileNotFoundError, RuntimeError, json.JSONDecodeError, KeyError):
            if require_live:
                raise
    patterns = stale_doc_patterns(live)
    issues: list[str] = []
    for path in status_doc_paths(root):
        if not path.exists():
            continue
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8")
        issues.extend(stale_literal_issues(text, rel, patterns))
        if live is None:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            issues.extend(live_status_line_issues(rel, line_no, line, live))
    return issues


_CURRENT_REFERENCE_SCAN_ROOTS: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "docs",
    "lean",
    "manuscript",
    "scripts",
    "src",
    "tests",
)

_CURRENT_REFERENCE_SUFFIXES = {".lean", ".md", ".py", ".yaml", ".yml"}

_REFERENCE_DRIFT_EXCLUDES: frozenset[str] = frozenset(
    {
        # These files intentionally preserve historical round narratives
        # or token-system examples, so old display numbers can be quoted
        # only when they are explicitly contextualized as history.
        "docs/CHANGELOG.md",
        "docs/reference/methods_audit.md",
        "docs/reference/veridical_status.md",
        "manuscript/refs/README.md",
    }
)

_REFERENCE_DRIFT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\*Last reviewed:\s*2026-05-1[234][^*]*\*", re.IGNORECASE),
        "replace dated current-facing review stamps with live readiness/audit pointers",
    ),
    (
        re.compile(r"\bfuture\s+Mathlib\s+extension\b|\bfuture proof slice would add\b", re.IGNORECASE),
        "describe MathlibProofs as a separate additive layer or roadmap, not as current future-pseudocode prose",
    ),
    (
        re.compile(
            r"boundary-via-"
            r"`rfl`|Boundary-complete;\s+full proof on the boundary|"
            r"stock-Lean boundary without analytic "
            r"witness assumptions",
            re.IGNORECASE,
        ),
        "describe theorem-status strength through per-row faithfulness, not broad status labels",
    ),
    (re.compile(r"\b(?:Theorem|Thm)\s+6\.4\b"), "use Theorem 7.4 for the e-geodesic/log-weight affine result"),
    (re.compile(r"\b(?:Theorem|Thm)\s+8\.1\b"), "use Theorem 9.1 for the heterogeneous coupling-tax result"),
    (re.compile(r"\b(?:Corollary|Cor)\s+8\.2\b"), "use Corollary 9.2 for the reflexive-stream tolerance result"),
    (re.compile(r"\bProp(?:osition)?\s+6\.3\b"), "use Proposition 7.3 for total correlation as KL"),
    (re.compile(r"\bProp(?:osition)?\s+8\.3\b"), "use Proposition 7.3 for total correlation as KL"),
    (re.compile(r"\bProp(?:osition)?\s+9\.1\b"), "use Proposition 8.1 for Schmidt rank-one mean-field factorization"),
    (
        re.compile(
            r"\((?:(?:Theorem|Thm|Proposition|Prop|Corollary|Cor)\s+)?"
            r"(?:4\.1|6\.4|8\.1)"
            r"[^)]*(?:,|;| and )[^)]*?(?:4\.1|5\.1|6\.4|7\.1|7\.2|7\.3|8\.1|8\.2|8\.3|9\.1|9\.2)[^)]*\)",
            re.IGNORECASE,
        ),
        "replace retired grouped theorem-number lists with tokenized refs",
    ),
    (
        re.compile(
            r"\bm-projection[^\n]{0,120}\bProp(?:osition)?\s+8\.2\b"
            r"|\bProp(?:osition)?\s+8\.2\b[^\n]{0,120}\bm-projection"
        ),
        "use Proposition 7.2 for the m-projection KL-minimization result",
    ),
)


def _current_reference_paths(root: Path) -> list[Path]:
    """Return current-facing source/prose files checked for stale display numbers."""
    paths: dict[Path, None] = {}
    for rel in _CURRENT_REFERENCE_SCAN_ROOTS:
        path = root / rel
        if not path.exists():
            continue
        candidates = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
        for candidate in candidates:
            if candidate.suffix not in _CURRENT_REFERENCE_SUFFIXES:
                continue
            try:
                rel_name = candidate.relative_to(root).as_posix()
            except ValueError:
                continue
            if rel_name in _REFERENCE_DRIFT_EXCLUDES:
                continue
            if "/.lake/" in rel_name or "/build/" in rel_name or rel_name.startswith("output/"):
                continue
            paths[candidate] = None
    return list(paths)


def _stale_reference_issues(project_root: Path) -> list[str]:
    """Return current-facing theorem-number drift issues.

    This is intentionally narrower than a generic prose linter.  It catches
    retired display-number phrases that have already caused drift after the
    manuscript was renumbered, while allowing legitimate current references
    such as spectral Proposition 8.2.
    """
    root = Path(project_root)
    issues: list[str] = []
    for path in _current_reference_paths(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern, replacement in _REFERENCE_DRIFT_PATTERNS:
                if pattern.search(line):
                    issues.append(f"{rel}:{line_no}: stale theorem reference {pattern.pattern!r}; {replacement}")
    return issues


def stale_reference_issues(project_root: Path) -> list[str]:
    """Return current-facing theorem-number drift issues.

    Public wrapper used by ``scripts/validate_manuscript.py``; the private
    name is retained for older tests and callers.
    """

    return _stale_reference_issues(project_root)


_MATHLIBPROOFS_POSITIVE_CLAIMS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bMathlibProofs\s+(?:proves|discharges|establishes|contains)\b", re.IGNORECASE),
    re.compile(r"\bproved\s+(?:inside|in|by)\s+`?MathlibProofs`?\b", re.IGNORECASE),
    re.compile(r"\b`?MathlibProofs`?.{0,100}\bcurrent theorem result\b", re.IGNORECASE),
    re.compile(r"\bgreen\s+`?lake build`?.{0,100}\b`?MathlibProofs`?\b", re.IGNORECASE),
)

_MATHLIBPROOFS_CAUTION_MARKERS: tuple[str, ...] = (
    "no ",
    "not ",
    "does not",
    "must not",
    "cannot",
    "without",
    "until",
    "before",
    "once",
    "future",
    "should",
    "would",
    "can ",
    "could",
    "optional",
    "scaffold",
    "scope note",
)


def mathlibproofs_claim_issues(project_root: Path) -> list[str]:
    """Reject overbroad current-facing MathlibProofs proof claims.

    ``lean/MathlibProofs`` may be cited for the compiled headline
    real-valued decomposition.  Prose still must not imply that every
    witness-form payload is proved or that the stock-Lean Float boundary is
    itself Mathlib-backed.
    """

    root = Path(project_root)
    paths = [
        *(root / "manuscript").glob("*.md"),
        root / "README.md",
        root / "AGENTS.md",
        root / "lean" / "MathlibProofs" / "README.md",
        root / "docs" / "reference" / "methods_orchestration.md",
        root / "docs" / "reference" / "_theorem_map.md",
    ]
    issues: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        rel = path.relative_to(root).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "MathlibProofs" not in line:
                continue
            lowered = line.lower()
            cautious = any(marker in lowered for marker in _MATHLIBPROOFS_CAUTION_MARKERS)
            if cautious:
                continue
            for pattern in _MATHLIBPROOFS_POSITIVE_CLAIMS:
                if pattern.search(line):
                    issues.append(
                        f"{rel}:{line_no}: MathlibProofs is cited as a current proof/result; "
                        "scope the claim to the compiled headline real-valued decomposition "
                        "or to a specific row with green Mathlib source"
                    )
    return issues
