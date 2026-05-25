"""Coverage-focused tests for manuscript.status."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from manuscript.status import (
    ProjectStatus,
    _parse_latex_pdf_log,
    _parse_pdfinfo,
    load_project_status,
    stale_status_issues,
)


def _write_pdfinfo_shim(bin_dir: Path, body: str, *, mode: int = 0o755) -> Path:
    script = bin_dir / "pdfinfo"
    script.write_text(body, encoding="utf-8")
    script.chmod(mode)
    return script


def test_parse_latex_pdf_log_raises_after_existing_nonmatching_log(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\nstatus\n")
    pdf.with_suffix(".log").write_text("This log has no page-count footer.\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="could not find a LaTeX page-count fallback"):
        _parse_latex_pdf_log(pdf)


def test_parse_pdfinfo_wraps_permission_error_from_nonexecutable_shim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\nstatus\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_pdfinfo_shim(bin_dir, "#!/bin/sh\nexit 0\n", mode=0o644)
    monkeypatch.setenv("PATH", str(bin_dir))

    with pytest.raises(RuntimeError, match="could not run pdfinfo"):
        _parse_pdfinfo(pdf)


def test_parse_pdfinfo_rejects_nonmatching_file_size_line(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\nstatus\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_pdfinfo_shim(
        bin_dir,
        "#!/bin/sh\necho 'Pages: 7'\necho 'File size: unknown'\n",
    )
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")

    with pytest.raises(RuntimeError, match="did not expose pages and size"):
        _parse_pdfinfo(pdf)


def test_load_project_status_reads_json_and_pdfinfo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reports = tmp_path / "output" / "reports"
    pdf_dir = tmp_path / "output" / "pdf"
    reports.mkdir(parents=True)
    pdf_dir.mkdir(parents=True)
    (reports / "test_results.json").write_text(
        ('{"project": {"total": 932, "passed": 930, "skipped": 2, "failed": 0, "coverage_percent": 96.37}}'),
        encoding="utf-8",
    )
    pdf = pdf_dir / "actinf_policy_entanglement_lean_combined.pdf"
    pdf.write_bytes(b"%PDF-1.4\nstatus\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_pdfinfo_shim(
        bin_dir,
        "#!/bin/sh\necho 'Pages: 144'\necho 'File size: 8765432 bytes'\n",
    )
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")

    status = load_project_status(tmp_path)

    assert status == ProjectStatus(
        tests_total=932,
        tests_passed=930,
        tests_skipped=2,
        tests_failed=0,
        coverage_percent=96.37,
        pdf_pages=144,
        pdf_size_bytes=8_765_432,
    )


def test_stale_status_issues_accepts_matching_live_counts_in_all_supported_forms(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (docs / "status.md").write_text(
        "\n".join(
            [
                "| Metric | Value |",
                "|---|---|",
                "| Tests collected | 932 |",
                "| Passing | 930 passed + 2 skipped |",
                "| Coverage on `src/` | 96.37 % |",
                "pytest saw 932-collected and 932 pytest items.",
                "pytest kept 932 items and 932 tests collected with 930 passed + 2 skipped.",
                "Combined PDF: 144 pages, 8.77 MB.",
                "Coverage on `src` is 96.37%.",
            ]
        ),
        encoding="utf-8",
    )
    (tests_dir / "README.md").write_text("", encoding="utf-8")
    status = ProjectStatus(
        tests_total=932,
        tests_passed=930,
        tests_skipped=2,
        tests_failed=0,
        coverage_percent=96.37,
        pdf_pages=144,
        pdf_size_bytes=8_765_432,
    )

    assert stale_status_issues(tmp_path, status) == []


def test_stale_status_issues_ignores_unparseable_metric_rows_without_reporting_drift(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (docs / "status.md").write_text(
        "\n".join(
            [
                "| Metric | Value |",
                "|---|---|",
                "| Tests collected | pending refresh |",
                "| Passing | see live regression output |",
                "| Coverage on `src/` | current report |",
                "Coverage on `src` remains aligned with the generated report.",
            ]
        ),
        encoding="utf-8",
    )
    (tests_dir / "README.md").write_text("", encoding="utf-8")
    status = ProjectStatus(
        tests_total=932,
        tests_passed=930,
        tests_skipped=2,
        tests_failed=0,
        coverage_percent=96.37,
        pdf_pages=144,
        pdf_size_bytes=8_765_432,
    )

    assert stale_status_issues(tmp_path, status) == []
