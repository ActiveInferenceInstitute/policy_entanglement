"""Tests for the project-local PDF validation helpers."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from manuscript.pdf_validation import (
    EXPECTED_PDF_MARGINS_IN,
    extract_pdf_text,
    parse_geometry_margins,
    scan_latex_log,
    scan_markdown_artifact,
    scan_pdf_text,
    scan_tex_artifact,
    validate_pdf_artifacts,
    validate_preamble_margins,
)


def test_pdf_text_scan_flags_raw_dollar_and_missing_token() -> None:
    issues = scan_pdf_text("Good text\nbad $ delimiter\n[[MISSING:LEAN:foo]]\n")
    messages = [issue.message for issue in issues]
    assert "raw dollar sign reached PDF text" in messages
    assert "missing manuscript token marker reached PDF" in messages


def test_markdown_scan_allows_token_examples_inside_code_spans() -> None:
    text = "Use `[[VAR:key]]` for examples.\n\nBut [[VAR:key]] outside code is bad."
    issues = scan_markdown_artifact(text)
    assert len(issues) == 1
    assert "unresolved registry token" in issues[0].message


def test_tex_scan_allows_texttt_token_examples() -> None:
    text = r"Use \texttt{[[VAR:key]]} as an example. Actual [[MISSING:VAR:key]] is bad."
    issues = scan_tex_artifact(text)
    assert len(issues) == 1
    assert "missing manuscript token" in issues[0].message


def test_latex_log_scan_flags_release_blockers() -> None:
    issues = scan_latex_log("Overfull \\hbox (12.0pt too wide)\n")
    assert len(issues) == 1
    assert issues[0].message == "LaTeX log issue"


def test_margin_parser_and_validator(tmp_path: Path) -> None:
    opts = ",".join(f"{k}={v}in" for k, v in EXPECTED_PDF_MARGINS_IN.items())
    preamble = tmp_path / "preamble.md"
    preamble.write_text(f"```latex\n\\usepackage[a4paper,{opts}]{{geometry}}\n```\n", encoding="utf-8")
    margins = parse_geometry_margins(preamble.read_text(encoding="utf-8"))
    assert margins["top"] == EXPECTED_PDF_MARGINS_IN["top"]
    assert validate_preamble_margins(preamble) == []


def test_pdf_issue_format_and_margin_failures(tmp_path: Path) -> None:
    missing = tmp_path / "missing_preamble.md"
    assert validate_preamble_margins(missing)[0].format().startswith(str(missing))

    preamble = tmp_path / "preamble.md"
    preamble.write_text(
        r"\usepackage[top=0.65in,bottom=oops,left=0.7in]{geometry}",
        encoding="utf-8",
    )
    margins = parse_geometry_margins(preamble.read_text(encoding="utf-8"))
    assert margins == {"top": 0.65, "left": 0.7}

    issues = validate_preamble_margins(preamble)
    messages = {issue.message for issue in issues}
    assert "missing geometry margin bottom" in messages
    assert "missing geometry margin right" in messages
    assert "geometry margin left=0.7in != expected 0.65in" in messages


def test_parse_geometry_margins_returns_empty_without_geometry() -> None:
    assert parse_geometry_margins("no geometry package here") == {}


def test_validate_pdf_artifacts_with_template_extractor(tmp_path: Path) -> None:
    project = tmp_path / "project"
    pdf_dir = project / "output" / "pdf"
    pdf_dir.mkdir(parents=True)
    pdf = pdf_dir / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n" + b"x" * 1200)
    (pdf_dir / "_combined_manuscript.md").write_text("Clean markdown.\n", encoding="utf-8")
    (pdf_dir / "_combined_manuscript.tex").write_text("Clean TeX.\n", encoding="utf-8")
    (pdf_dir / "_combined_manuscript.log").write_text("", encoding="utf-8")
    (pdf_dir / "_xelatex_stdout.log").write_text("", encoding="utf-8")

    manuscript = project / "manuscript"
    manuscript.mkdir()
    opts = ",".join(f"{k}={v}in" for k, v in EXPECTED_PDF_MARGINS_IN.items())
    (manuscript / "preamble.md").write_text(
        f"\\usepackage[a4paper,{opts}]{{geometry}}\n",
        encoding="utf-8",
    )

    template_root = tmp_path / "template"
    module_dir = template_root / "infrastructure" / "validation" / "content"
    module_dir.mkdir(parents=True)
    for init_dir in (
        template_root / "infrastructure",
        template_root / "infrastructure" / "validation",
        module_dir,
    ):
        (init_dir / "__init__.py").write_text("", encoding="utf-8")
    (module_dir / "pdf_validator.py").write_text(
        "def extract_text_from_pdf(path):\n    return 'Clean PDF text.\\n'\n",
        encoding="utf-8",
    )

    assert extract_pdf_text(pdf, template_root=template_root) == "Clean PDF text.\n"
    assert validate_pdf_artifacts(project_root=project, pdf_path=pdf, template_root=template_root) == []


def test_validate_pdf_artifacts_reports_missing_pdf(tmp_path: Path) -> None:
    issues = validate_pdf_artifacts(project_root=tmp_path, pdf_path=tmp_path / "missing.pdf")
    assert len(issues) == 1
    assert issues[0].message == "PDF missing"


def test_validate_pdf_artifacts_reports_small_pdf_missing_intermediates_and_stdout_log(tmp_path: Path) -> None:
    project = tmp_path / "project"
    pdf_dir = project / "output" / "pdf"
    pdf_dir.mkdir(parents=True)
    pdf = pdf_dir / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\nsmall")
    (pdf_dir / "_xelatex_stdout.log").write_text("Warning: something happened\n", encoding="utf-8")
    manuscript = project / "manuscript"
    manuscript.mkdir()
    (manuscript / "preamble.md").write_text("no geometry package here\n", encoding="utf-8")

    template_root = tmp_path / "template"
    module_dir = template_root / "infrastructure" / "validation" / "content"
    module_dir.mkdir(parents=True)
    (module_dir / "pdf_validator.py").write_text(
        "def extract_text_from_pdf(path):\n    return 'forward-looking pseudocode\\n'\n",
        encoding="utf-8",
    )

    issues = validate_pdf_artifacts(project_root=project, pdf_path=pdf, template_root=template_root)
    messages = [issue.message for issue in issues]
    assert "PDF too small" in messages
    assert "combined markdown missing" in messages
    assert "combined TeX missing" in messages
    assert "LaTeX log missing" in messages
    assert "LaTeX log issue" in messages
    assert "stale draft/Mathlib wording reached PDF" in messages
    assert any(message.startswith("missing geometry margin") for message in messages)


def test_pdf_text_extraction_cli_fallback_and_errors(tmp_path: Path, monkeypatch) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n" + b"x" * 1200)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    pdftotext = bin_dir / "pdftotext"
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")

    template_root = tmp_path / "template"
    module_dir = template_root / "infrastructure" / "validation" / "content"
    module_dir.mkdir(parents=True)
    (module_dir / "pdf_validator.py").write_text("raise RuntimeError('template broken')\n", encoding="utf-8")

    pdftotext.write_text("#!/usr/bin/env sh\necho 'fallback text'\n", encoding="utf-8")
    pdftotext.chmod(0o755)
    assert extract_pdf_text(pdf, template_root=template_root).strip() == "fallback text"

    pdftotext.write_text("#!/usr/bin/env sh\necho 'bad pdf' >&2\nexit 3\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="bad pdf"):
        extract_pdf_text(pdf)

    pdftotext.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="empty text"):
        extract_pdf_text(pdf)

    with pytest.raises(FileNotFoundError):
        extract_pdf_text(tmp_path / "missing.pdf")


def test_pdf_scanners_cover_stale_refs_placeholders_and_clean_missing_marker_examples() -> None:
    pdf_issues = scan_pdf_text(
        "The token marker [[MISSING:VAR:x]] is documented here.\n"
        "Actual unresolved ref ?? and ${BAD} plus " + "future Mathlib" + " extension.\n"
    )
    assert not any("missing manuscript token marker" in issue.message for issue in pdf_issues)
    assert any("unresolved reference/citation" in issue.message for issue in pdf_issues)
    assert any("unresolved placeholder" in issue.message for issue in pdf_issues)
    assert any("stale draft/Mathlib wording" in issue.message for issue in pdf_issues)

    md_issues = scan_markdown_artifact("~~~\n[[VAR:example]]\n~~~\nOutside [[MISSING:VAR:x]] and [??].\n")
    assert any("missing manuscript token marker" in issue.message for issue in md_issues)
    assert any("unresolved reference/citation" in issue.message for issue in md_issues)

    tex_issues = scan_tex_artifact(r"\texttt{[[VAR:ok]]} ${BAD} ?? NOT current source code")
    assert any("unresolved placeholder" in issue.message for issue in tex_issues)
    assert any("stale draft/Mathlib wording" in issue.message for issue in tex_issues)
