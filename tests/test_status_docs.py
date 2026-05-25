"""Status-doc drift guards.

Visible onboarding docs are allowed to quote volatile counts, but the
counts must match generated artifacts instead of stale round notes.
"""

from __future__ import annotations

import csv
import os
import re
from pathlib import Path

import pytest

from manuscript.status import (
    ProjectStatus,
    _parse_pdfinfo,
    load_project_status,
    mathlibproofs_claim_issues,
    stale_reference_issues,
    stale_status_issues,
)
from manuscript.status_patterns import (
    live_status_line_issues,
    stale_doc_patterns,
    stale_literal_issues,
    status_doc_paths,
)
from orchestration import run_all

PROJECT = Path(__file__).resolve().parent.parent
AUDIT_MATRIX = PROJECT / "docs" / "_audit" / "pymdp_lean_manuscript_matrix_2026-05-21.csv"
AUDIT_MATRIX_COLUMNS = (
    "claim_area",
    "public_surface",
    "generating_source",
    "config_or_var_key",
    "artifact_or_sidecar",
    "verification_gate",
    "verdict",
    "remediation",
)
AUDIT_PATH_PREFIXES = ("output/", "docs/", "manuscript/", "scripts/", "tests/", "lean/")
AUDIT_PATH_SUFFIXES = (".csv", ".json", ".md", ".pdf", ".html", ".lean")
RETIRED_DISCUSSION_LABEL_RE = re.compile(r"\b[wW]ork[- ]?[pP]lan\b")
RETIRED_DISCUSSION_LABEL_SCAN_ROOTS = (
    PROJECT / "AGENTS.md",
    PROJECT / "README.md",
    PROJECT / "docs",
    PROJECT / "lean",
    PROJECT / "manuscript",
    PROJECT / "scripts",
    PROJECT / "src",
    PROJECT / "tests",
)
RETIRED_DISCUSSION_LABEL_ALLOWLIST = (PROJECT / "docs" / "_audit",)
RETIRED_DISCUSSION_LABEL_SUFFIXES = {".md", ".py", ".toml", ".yaml", ".yml", ".lean"}
PLACEHOLDER_MARKER_RE = re.compile(
    r"\b(?:TODO|TBD|FIXME|XXX)\b"
    r"|lorem ipsum"
    r"|coming soon"
    r"|fill in"
    r"|to be completed"
    r"|\bplaceholder(?:s)?\b"
    r"|\bstub(?:s|bed)?\b"
    r"|\bnot implemented\b",
    re.IGNORECASE,
)
PLACEHOLDER_SCAN_ROOTS = (
    PROJECT / "README.md",
    PROJECT / "AGENTS.md",
    PROJECT / "docs",
    PROJECT / "manuscript",
    PROJECT / "output" / "manuscript",
)
PLACEHOLDER_ALLOWLIST_ROOTS = (PROJECT / "docs" / "_audit",)
PLACEHOLDER_CONTEXT_ALLOWLIST = (
    "Token placeholders",
    "placeholder tokens",
    "placeholder citations",
    "unresolved placeholder",
    "raw math delimiters, placeholders",
    "instructional placeholder",
    "`[[...]]` placeholder",
    "`[[…]]` placeholder",
    "`[[VAR:key]]`",
    "`[[VAR:<key>]]`",
    "prior `kl q q s ≡ 0` placeholder",
    "`sorry` placeholder",
    "`sorry` placeholders",
    "hidden `sorry` placeholders",
    "reflexivity placeholders",
    "rather than `sorry` placeholders",
    "`floatLog` stubs",
    "pymdp call was stubbed out",
)
RUN_ALL_COUNT_RE = re.compile(
    r"(?:run_all|pipeline|canonical|orchestrator|full)\b[^\n]{0,90}\b(\d+)[- ]scripts?\b"
    r"|\b(\d+)[- ]scripts?\b[^\n]{0,90}\b(?:run_all|pipeline|canonical|orchestrator|full)\b",
    re.IGNORECASE,
)
RUN_ALL_COUNT_SCAN_ROOTS = (
    PROJECT / "README.md",
    PROJECT / "AGENTS.md",
    PROJECT / "docs",
    PROJECT / "scripts",
)
RUN_ALL_COUNT_ALLOWLIST_ROOTS = (
    PROJECT / "docs" / "_audit",
    PROJECT / "docs" / "CHANGELOG.md",
)
RUN_ALL_STAGE_DOCS = (
    PROJECT / "README.md",
    PROJECT / "docs" / "reference" / "four_track_coherence.md",
    PROJECT / "docs" / "reference" / "methods_orchestration.md",
)
GNN_STALE_CANDIDATE_RE = re.compile(
    r"candidate fifth representation"
    r"|not a fifth track yet"
    r"|does\s+not\s+currently\s+generate"
    r"|does\s+NOT\s+currently\s+generate"
    r"|tagged\s+`roadmap`",
    re.IGNORECASE,
)
GNN_CURRENT_SCAN_ROOTS = (
    PROJECT / "README.md",
    PROJECT / "docs",
    PROJECT / "manuscript",
)
GNN_STALE_ALLOWLIST_ROOTS = (
    PROJECT / "docs" / "_audit",
    PROJECT / "docs" / "CHANGELOG.md",
)
UNRESOLVED_PUBLICATION_DOI = "10.5281/zenodo.20301239"
UNRESOLVED_ZENODO_RECORD = "https://zenodo.org/records/20301239"
UNRESOLVED_SOURCE_REPOSITORY = "https://github.com/docxology/policy_entanglement"
CANONICAL_SOURCE_REPOSITORY = UNRESOLVED_SOURCE_REPOSITORY
WRONG_SOURCE_REPOSITORY = "https://github.com/ActiveInferenceInstitute/policy_entanglement"
PUBLICATION_METADATA_PATHS = (
    PROJECT / "README.md",
    PROJECT / "docs" / "README.md",
    PROJECT / "AGENTS.md",
    PROJECT / "CITATION.cff",
    PROJECT / "manuscript" / "config.yaml",
    PROJECT / "manuscript" / "refs" / "citations.yaml",
    PROJECT / "manuscript" / "1A_part1_introduction.md",
    PROJECT / "manuscript" / "6C_discussion_and_outlook.md",
)
PUBLICATION_REPOSITORY_PATHS = (
    *PUBLICATION_METADATA_PATHS,
    PROJECT / "CONTRIBUTING.md",
    PROJECT / "manuscript" / "0A_abstract.md",
)
PUBLICATION_BANNER_PATHS = (
    PROJECT / "README.md",
    PROJECT / "docs" / "README.md",
    PROJECT / "AGENTS.md",
)


def _audit_matrix_issues() -> list[str]:
    with AUDIT_MATRIX.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    issues: list[str] = []
    if not rows:
        return ["audit matrix is empty"]
    if tuple(rows[0].keys()) != AUDIT_MATRIX_COLUMNS:
        issues.append(f"audit matrix columns drifted: {tuple(rows[0].keys())!r}")
    for row in rows:
        for column in AUDIT_MATRIX_COLUMNS:
            if not row.get(column, "").strip():
                issues.append(f"{row.get('claim_area', '<unknown>')}: blank {column}")
        artifact_field = row.get("artifact_or_sidecar", "")
        if "output/reports/mathlib_proofs.json" in artifact_field:
            issues.append(f"{row.get('claim_area', '<unknown>')}: cites retired mathlib_proofs.json")
        for raw in artifact_field.split(";"):
            item = raw.strip().strip("`")
            if not item:
                continue
            if item.startswith(AUDIT_PATH_PREFIXES) or item.endswith(AUDIT_PATH_SUFFIXES):
                if not item.startswith(AUDIT_PATH_PREFIXES):
                    issues.append(f"{row.get('claim_area', '<unknown>')}: unrooted artifact path {item!r}")
                    continue
                if not (PROJECT / item).exists():
                    issues.append(f"{row.get('claim_area', '<unknown>')}: missing evidence path {item}")
    return issues


def _pymdp_package_api_wording_issues() -> list[str]:
    current_files = [
        PROJECT / "README.md",
        PROJECT / "AGENTS.md",
        PROJECT / "pyproject.toml",
        PROJECT / "docs" / "simulation" / "pomdp_simulation.md",
        PROJECT / "docs" / "reference" / "methods_audit.md",
        PROJECT / "src" / "simulation" / "README.md",
        PROJECT / "src" / "simulation" / "AGENTS.md",
        PROJECT / "manuscript" / "4B_empirical_suite.md",
        PROJECT / "manuscript" / "4C_pymdp_harness.md",
        PROJECT / "manuscript" / "6C_discussion_and_outlook.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in current_files if path.exists())
    issues: list[str] = []
    if "inferactively-pymdp==1.0.1" not in combined:
        issues.append("current docs no longer name the installed inferactively-pymdp==1.0.1 distribution")
    if "pymdp.agent.Agent" not in combined:
        issues.append("current docs no longer name the runtime pymdp.agent.Agent API")
    if "inferactively-pymdp 1.0.1" in combined:
        issues.append("use inferactively-pymdp==1.0.1 for package metadata")
    if re.search(r"(?<!inferactively-)\bpymdp==1\.0\.1\b", combined):
        issues.append("do not cite a nonexistent pymdp==1.0.1 distribution")
    return issues


def _retired_discussion_label_issues() -> list[str]:
    """Find current-facing references to the retired discussion label."""

    candidates: list[Path] = []
    for root in RETIRED_DISCUSSION_LABEL_SCAN_ROOTS:
        if root.is_file():
            candidates.append(root)
            continue
        if root.exists():
            candidates.extend(p for p in root.rglob("*") if p.is_file())

    issues: list[str] = []
    for path in candidates:
        if path.suffix not in RETIRED_DISCUSSION_LABEL_SUFFIXES:
            continue
        if any(path == allowed or allowed in path.parents for allowed in RETIRED_DISCUSSION_LABEL_ALLOWLIST):
            continue
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if RETIRED_DISCUSSION_LABEL_RE.search(line):
                issues.append(f"{path.relative_to(PROJECT)}:{line_no}: {line.strip()}")
    return issues


def _placeholder_marker_issues() -> list[str]:
    """Find live reader-facing draft markers while allowing syntax docs."""

    candidates: list[Path] = []
    for root in PLACEHOLDER_SCAN_ROOTS:
        if root.is_file():
            candidates.append(root)
            continue
        if root.exists():
            candidates.extend(p for p in root.rglob("*.md") if p.is_file())

    issues: list[str] = []
    for path in candidates:
        if any(path == allowed or allowed in path.parents for allowed in PLACEHOLDER_ALLOWLIST_ROOTS):
            continue
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not PLACEHOLDER_MARKER_RE.search(line):
                continue
            if any(allowed in line for allowed in PLACEHOLDER_CONTEXT_ALLOWLIST):
                continue
            issues.append(f"{path.relative_to(PROJECT)}:{line_no}: {line.strip()}")
    return issues


def _run_all_count_issues() -> list[str]:
    """Catch stale hand-written pipeline counts in current-facing docs."""

    expected = len(run_all.SCRIPTS)
    candidates: list[Path] = []
    for root in RUN_ALL_COUNT_SCAN_ROOTS:
        if root.is_file():
            candidates.append(root)
            continue
        if root.exists():
            candidates.extend(p for p in root.rglob("*") if p.is_file() and p.suffix in {".md", ".py"})

    issues: list[str] = []
    for path in candidates:
        if any(path == allowed or allowed in path.parents for allowed in RUN_ALL_COUNT_ALLOWLIST_ROOTS):
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in RUN_ALL_COUNT_RE.finditer(line):
                raw = next(group for group in match.groups() if group is not None)
                got = int(raw)
                if got != expected:
                    issues.append(
                        f"{path.relative_to(PROJECT)}:{line_no}: run_all script count {got} != live {expected}: "
                        f"{line.strip()}"
                    )
    return issues


def _run_all_stage_list_issues() -> list[str]:
    """Ensure high-traffic pipeline narratives name every live stage."""

    expected = {script for script, _description in run_all.SCRIPTS}
    issues: list[str] = []
    for path in RUN_ALL_STAGE_DOCS:
        if not path.exists():
            issues.append(f"{path.relative_to(PROJECT)}: missing run_all stage doc")
            continue
        text = path.read_text(encoding="utf-8")
        missing = sorted(script for script in expected if script not in text)
        if missing:
            issues.append(f"{path.relative_to(PROJECT)}: missing run_all stages {missing}")
    return issues


def _gnn_stale_candidate_issues() -> list[str]:
    """Catch stale roadmap-only GNN wording after S08 became shipped."""

    candidates: list[Path] = []
    for root in GNN_CURRENT_SCAN_ROOTS:
        if root.is_file():
            candidates.append(root)
            continue
        if root.exists():
            candidates.extend(p for p in root.rglob("*.md") if p.is_file())

    issues: list[str] = []
    for path in candidates:
        if any(path == allowed or allowed in path.parents for allowed in GNN_STALE_ALLOWLIST_ROOTS):
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "GNN" not in line and "Generalized Notation Notation" not in line:
                continue
            if GNN_STALE_CANDIDATE_RE.search(line):
                issues.append(f"{path.relative_to(PROJECT)}:{line_no}: {line.strip()}")
    return issues


def _repository_url_from_config() -> str:
    config_text = (PROJECT / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*repository_url:\s*"([^"]*)"\s*$', config_text)
    return match.group(1) if match else ""


def _publication_metadata_issues() -> list[str]:
    """Reject contradictory public DOI / source-repository states."""

    config_text = (PROJECT / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    doi_is_pending = bool(re.search(r"(?m)^\s*doi:\s*\"\"\s*$", config_text))
    repository_is_pending = bool(re.search(r"(?m)^\s*repository_url:\s*\"\"\s*$", config_text))
    issues: list[str] = []

    if doi_is_pending:
        for path in PUBLICATION_METADATA_PATHS:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(PROJECT)
            if UNRESOLVED_PUBLICATION_DOI in text:
                issues.append(f"{rel}: publishes unresolved DOI while config DOI is pending")
            if UNRESOLVED_ZENODO_RECORD in text:
                issues.append(f"{rel}: publishes unresolved Zenodo record while config DOI is pending")
        for path in PUBLICATION_BANNER_PATHS:
            if not path.exists():
                continue
            if "**Publication:**" in path.read_text(encoding="utf-8"):
                issues.append(f"{path.relative_to(PROJECT)}: uses public Publication banner while DOI is pending")
    else:
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in PUBLICATION_METADATA_PATHS if path.exists()
        )
        if "no Zenodo DOI has been minted yet" in combined or "public Zenodo DOI" in combined:
            issues.append("config DOI is present but current-facing docs still describe the DOI as pending")

    if repository_is_pending:
        for path in PUBLICATION_METADATA_PATHS:
            if not path.exists():
                continue
            if UNRESOLVED_SOURCE_REPOSITORY in path.read_text(encoding="utf-8"):
                issues.append(
                    f"{path.relative_to(PROJECT)}: publishes unresolved source repository while config repository is pending"
                )
    else:
        configured_url = _repository_url_from_config()
        if configured_url != CANONICAL_SOURCE_REPOSITORY:
            issues.append(
                f"manuscript/config.yaml: repository_url {configured_url!r} != canonical {CANONICAL_SOURCE_REPOSITORY!r}"
            )
        for path in PUBLICATION_REPOSITORY_PATHS:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(PROJECT)
            if WRONG_SOURCE_REPOSITORY in text:
                issues.append(f"{rel}: cites wrong source repository {WRONG_SOURCE_REPOSITORY!r}")
            if "no public repository URL" in text:
                issues.append(f"{rel}: claims no public repository URL while config repository is set")
        combined_banners = "\n".join(
            path.read_text(encoding="utf-8") for path in PUBLICATION_BANNER_PATHS if path.exists()
        )
        if "public source archive pending" in combined_banners:
            issues.append("current-facing banners still describe source archive as pending")

    return issues


def test_status_docs_do_not_contain_stale_live_counts() -> None:
    reference_issues = stale_reference_issues(PROJECT)
    assert not reference_issues, "\n".join(reference_issues)

    mathlib_issues = mathlibproofs_claim_issues(PROJECT)
    assert not mathlib_issues, "\n".join(mathlib_issues)

    pymdp_wording_issues = _pymdp_package_api_wording_issues()
    assert not pymdp_wording_issues, "\n".join(pymdp_wording_issues)

    retired_label_issues = _retired_discussion_label_issues()
    assert not retired_label_issues, "\n".join(retired_label_issues)

    placeholder_marker_issues = _placeholder_marker_issues()
    assert not placeholder_marker_issues, "\n".join(placeholder_marker_issues)

    run_all_count_issues = _run_all_count_issues()
    assert not run_all_count_issues, "\n".join(run_all_count_issues)

    run_all_stage_list_issues = _run_all_stage_list_issues()
    assert not run_all_stage_list_issues, "\n".join(run_all_stage_list_issues)

    gnn_stale_candidate_issues = _gnn_stale_candidate_issues()
    assert not gnn_stale_candidate_issues, "\n".join(gnn_stale_candidate_issues)

    publication_metadata_issues = _publication_metadata_issues()
    assert not publication_metadata_issues, "\n".join(publication_metadata_issues)

    test_path = PROJECT / "output" / "reports" / "test_results.json"
    pdf_path = PROJECT / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf"
    if not test_path.exists():
        # test_results.json is the essential artifact for status-count
        # validation; without it the live count cannot be checked. RedTeam
        # Tests H6 (2026-05-20): xfail instead of skip so its absence does
        # not masquerade as a pass.
        pytest.xfail("generated test_results.json not present — run scripts/regression_gate.py first")
    if not pdf_path.exists():
        # PDF artifact missing but test_results.json present: run the
        # reduced status check that compares against literal counts only,
        # not PDF-page / PDF-size live values. This passes when the
        # fixed-literal status counts in README/AGENTS docs are
        # consistent with the live test report, without requiring a full
        # LaTeX build (which is only exercised in `--with-pdf` runs).
        issues = stale_status_issues(PROJECT, require_live=False)
        assert not issues, "\n".join(issues)
        return
    status = load_project_status(PROJECT)
    issues = stale_status_issues(PROJECT, status)
    assert not issues, "\n".join(issues)

    audit_matrix_issues = _audit_matrix_issues()
    assert not audit_matrix_issues, "\n".join(audit_matrix_issues)


def test_stale_status_detects_table_shaped_rows(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "README.md").write_text(
        "\n".join(
            [
                "| Metric | Value |",
                "|---|---|",
                "| Tests collected | 853 |",
                "| Passing | 852 passed + 1 skipped |",
                "| Coverage on `src/` | 97.69 % |",
            ]
        ),
        encoding="utf-8",
    )
    status = ProjectStatus(
        tests_total=865,
        tests_passed=864,
        tests_skipped=1,
        tests_failed=0,
        coverage_percent=96.06,
        pdf_pages=139,
        pdf_size_bytes=6_921_624,
    )

    issues = stale_status_issues(tmp_path, status)

    assert any("tests collected table count 853 != live 865" in issue for issue in issues)
    assert any("pass/skip summary 852/1 != live 864/1" in issue for issue in issues)
    assert any("coverage 97.69% != live 96.06%" in issue for issue in issues)


def test_stale_status_detects_pdf_and_inline_pytest_counts(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "README.md").write_text(
        "pytest collected 800 items with 799 passed + 1 skipped.\n"
        "Combined PDF: 137 pages, 5.37 MB.\n"
        "Coverage on `src` is 90.00%.\n",
        encoding="utf-8",
    )
    status = ProjectStatus(
        tests_total=888,
        tests_passed=887,
        tests_skipped=1,
        tests_failed=0,
        coverage_percent=96.08,
        pdf_pages=143,
        pdf_size_bytes=8_680_000,
    )
    issues = stale_status_issues(tmp_path, status)
    assert any("pytest item count 800 != live 888" in issue for issue in issues)
    assert any("pass/skip summary 799/1 != live 887/1" in issue for issue in issues)
    assert any("PDF summary 137 pages, 5.37 MB" in issue for issue in issues)
    assert any("coverage 90.00% != live 96.08%" in issue for issue in issues)


def test_stale_reference_and_mathlib_claim_guards_on_temporary_tree(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "bad.md").write_text(f"Use Theorem {6}.{4} here.\n", encoding="utf-8")
    (tmp_path / "docs" / "token_drift.md").write_text(
        "Use [[CITATION:key]], output/dashboards/index.html, "
        "output/reports/mathlib_proofs.json, and schmidt_archetypes_old.csv.\n",
        encoding="utf-8",
    )
    stale_boundary_status = "boundary-via-" + "`rfl`"
    stale_proved_status = "Boundary-complete; " + "full proof on the boundary"
    (tmp_path / "docs" / "status_drift.md").write_text(
        f"The table says {stale_boundary_status} and {stale_proved_status}.\n",
        encoding="utf-8",
    )
    stale_mathlib_phrase = "future Mathlib" + " extension"
    (tmp_path / "docs" / "future_mathlib.md").write_text(
        f"A {stale_mathlib_phrase} will do this.\n",
        encoding="utf-8",
    )
    (tmp_path / "manuscript").mkdir()
    (tmp_path / "manuscript" / "paper.md").write_text(
        "MathlibProofs proves the current theorem result.\n",
        encoding="utf-8",
    )
    (tmp_path / "lean" / "MathlibProofs").mkdir(parents=True)
    (tmp_path / "lean" / "MathlibProofs" / "README.md").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("", encoding="utf-8")

    reference_issues = stale_reference_issues(tmp_path)
    assert reference_issues
    assert any("future" in issue.lower() or "mathlibproofs" in issue.lower() for issue in reference_issues)
    assert any("faithfulness" in issue for issue in reference_issues)
    status_issues = stale_status_issues(tmp_path, require_live=False)
    assert any("CITATION:" in issue for issue in status_issues)
    assert any("output/dashboards/" in issue for issue in status_issues)
    assert any("mathlib_proofs" in issue for issue in status_issues)
    assert any("schmidt_archetypes_" in issue for issue in status_issues)
    assert mathlibproofs_claim_issues(tmp_path)


def test_status_properties_and_require_live_modes(tmp_path: Path) -> None:
    status = ProjectStatus(
        tests_total=3,
        tests_passed=2,
        tests_skipped=1,
        tests_failed=0,
        coverage_percent=95.5,
        pdf_pages=12,
        pdf_size_bytes=2_500_000,
    )
    assert status.test_summary == "3 collected; 2 passed + 1 skipped"
    assert status.pdf_summary == "12 pages, 2.50 MB"

    readme = tmp_path / "README.md"
    readme.write_text("No live count here.\n", encoding="utf-8")
    assert stale_status_issues(tmp_path, require_live=False) == []

    with pytest.raises(FileNotFoundError):
        stale_status_issues(tmp_path, require_live=True)


def test_status_guard_allows_current_counts_and_detects_more_forms(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "guides"
    docs.mkdir(parents=True)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "README.md").write_text(
        "\n".join(
            [
                "| Metric | Value |",
                "|---|---|",
                "| Tests collected | 10 |",
                "| Passing | 9 passed + 1 skipped |",
                "| Coverage on `src/` | 96.92 % |",
                "pytest saw 8-collected and 7 pytest items.",
                "There were 6 tests collected.",
            ]
        ),
        encoding="utf-8",
    )
    status = ProjectStatus(
        tests_total=10,
        tests_passed=9,
        tests_skipped=1,
        tests_failed=0,
        coverage_percent=96.92,
        pdf_pages=140,
        pdf_size_bytes=9_230_000,
    )

    issues = stale_status_issues(tmp_path, status)

    assert not any("table count 10" in issue for issue in issues)
    assert any("pytest collected count 8 != live 10" in issue for issue in issues)
    assert any("pytest item count 7 != live 10" in issue for issue in issues)
    assert any("tests collected count 6 != live 10" in issue for issue in issues)


def test_pdfinfo_parser_failure_modes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    script = bin_dir / "pdfinfo"
    script.write_text("#!/usr/bin/env sh\necho 'Pages: 7'\necho 'File size: 1234 bytes'\n", encoding="utf-8")
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    assert _parse_pdfinfo(pdf) == (7, 1234)

    script.write_text("#!/usr/bin/env sh\necho 'boom' >&2\nexit 2\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="pdfinfo failed"):
        _parse_pdfinfo(pdf)

    script.write_text("#!/usr/bin/env sh\necho 'Pages: 7'\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="did not expose"):
        _parse_pdfinfo(pdf)

    script.unlink()
    (tmp_path / "_combined_manuscript.log").write_text(
        "Output written on _combined_manuscript.pdf (9 pages).\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PATH", str(bin_dir))
    assert _parse_pdfinfo(pdf) == (9, pdf.stat().st_size)


def test_status_patterns_helpers_on_temp_tree(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (tmp_path / "README.md").write_text("Still cites 844 tests.\n", encoding="utf-8")
    (docs / "note.md").write_text("844\n", encoding="utf-8")

    paths = status_doc_paths(tmp_path)
    assert (tmp_path / "README.md") in paths
    assert docs / "note.md" in paths

    live = ProjectStatus(
        tests_total=900,
        tests_passed=899,
        tests_skipped=1,
        tests_failed=0,
        coverage_percent=96.0,
        pdf_pages=140,
        pdf_size_bytes=7_000_000,
    )
    patterns = stale_doc_patterns(live)
    readme_text = (tmp_path / "README.md").read_text(encoding="utf-8")
    literal_issues = stale_literal_issues(readme_text, "README.md", patterns)
    assert any("844" in issue for issue in literal_issues)

    line_issues = live_status_line_issues(
        "tests/README.md",
        2,
        "pytest collected 800 items with 799 passed + 1 skipped.",
        live,
    )
    assert any("pytest item count 800 != live 900" in issue for issue in line_issues)
