"""PDF-render validation helpers for the project-local release gate.

This module owns the project-specific checks that make the rendered PDF auditable: unresolved
tokens, raw math delimiters, LaTeX log failures, stale draft language, and
the compact-margin contract.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PdfValidationIssue:
    """One PDF/readiness validation issue."""

    source: str
    line: int
    message: str
    excerpt: str

    def format(self) -> str:
        loc = self.source if self.line <= 0 else f"{self.source}:{self.line}"
        return f"{loc}: {self.message}: {self.excerpt}"


EXPECTED_PDF_MARGINS_IN: dict[str, float] = {
    "top": 0.65,
    "bottom": 0.72,
    "left": 0.65,
    "right": 0.65,
}

_FENCED_CODE_RE = re.compile(r"(```|~~~)[^\n]*\n.*?\1", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_LATEX_TEXTTT_RE = re.compile(r"\\texttt\{[^{}]*\}")
_TOKEN_RE = re.compile(r"\[\[(?:VAR|SEC|SECREF|THM|THMREF|FIG|FIGREF|EQ|EQREF|LEAN|CITE|CITELIST):[^\]]+\]\]")
_MISSING_TOKEN_RE = re.compile(r"\[\[MISSING:[^\]]+\]\]")
_UNRESOLVED_PLACEHOLDER_RE = re.compile(r"\$\{[A-Za-z0-9_]+\}")
_PDF_RAW_DOLLAR_RE = re.compile(r"\$")
_UNRESOLVED_REF_RE = re.compile(r"\?\?|\[\?\]")

_STALE_DRAFT_PHRASES: tuple[re.Pattern[str], ...] = (
    re.compile(r"future\s+Mathlib\s+extension", re.IGNORECASE),
    re.compile(r"forward-looking pseudocode", re.IGNORECASE),
    re.compile(r"NOT current source code", re.IGNORECASE),
    re.compile(r"deferred theorem(?:s)?", re.IGNORECASE),
)

_LATEX_LOG_FATAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"! LaTeX Error:", re.IGNORECASE),
    re.compile(r"Undefined control sequence", re.IGNORECASE),
    re.compile(r"Missing \$ inserted", re.IGNORECASE),
    re.compile(r"Emergency stop", re.IGNORECASE),
    re.compile(r"Fatal error", re.IGNORECASE),
    re.compile(r"Citation .+ undefined", re.IGNORECASE),
    re.compile(r"Reference .+ undefined", re.IGNORECASE),
    re.compile(r"There were undefined (?:references|citations)", re.IGNORECASE),
    re.compile(r"Missing character:", re.IGNORECASE),
    re.compile(r"Overfull \\hbox", re.IGNORECASE),
    re.compile(r"Underfull \\hbox", re.IGNORECASE),
    re.compile(r"Warning:", re.IGNORECASE),
)


def _strip_markdown_code(text: str) -> str:
    """Remove fenced and inline code spans before source-token scans."""

    return _INLINE_CODE_RE.sub("", _FENCED_CODE_RE.sub("", text))


def _line_issue(source: str, line_no: int, message: str, line: str) -> PdfValidationIssue:
    return PdfValidationIssue(
        source=source,
        line=line_no,
        message=message,
        excerpt=line.strip()[:220],
    )


def _scan_lines(
    *,
    source: str,
    text: str,
    checks: Iterable[tuple[re.Pattern[str], str]],
) -> list[PdfValidationIssue]:
    issues: list[PdfValidationIssue] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for pattern, message in checks:
            if pattern.search(line):
                issues.append(_line_issue(source, line_no, message, line))
    return issues


def scan_pdf_text(text: str, *, source: str = "pdf text") -> list[PdfValidationIssue]:
    """Scan extracted PDF text for high-confidence render failures.

    Token-system examples are intentionally allowed in prose, so this
    PDF-text scan only rejects missing markers, unresolved reference glyphs,
    raw math delimiters, placeholders, and stale draft phrases.
    """

    issues: list[PdfValidationIssue] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _MISSING_TOKEN_RE.search(line) and not re.search(r"\b(?:marker|token|substitutes|fails fast)\b", line):
            issues.append(_line_issue(source, line_no, "missing manuscript token marker reached PDF", line))
    checks = [
        (_UNRESOLVED_REF_RE, "unresolved reference/citation reached PDF"),
        (_UNRESOLVED_PLACEHOLDER_RE, "unresolved placeholder reached PDF"),
        (_PDF_RAW_DOLLAR_RE, "raw dollar sign reached PDF text"),
        *[(pattern, "stale draft/Mathlib wording reached PDF") for pattern in _STALE_DRAFT_PHRASES],
    ]
    issues.extend(_scan_lines(source=source, text=text, checks=checks))
    return issues


def scan_markdown_artifact(text: str, *, source: str = "combined markdown") -> list[PdfValidationIssue]:
    """Scan rendered combined Markdown outside code spans."""

    stripped = _strip_markdown_code(text)
    checks = [
        (_MISSING_TOKEN_RE, "missing manuscript token marker reached rendered markdown"),
        (_TOKEN_RE, "unresolved registry token outside code spans"),
        (_UNRESOLVED_PLACEHOLDER_RE, "unresolved placeholder reached rendered markdown"),
        (_UNRESOLVED_REF_RE, "unresolved reference/citation reached rendered markdown"),
        *[(pattern, "stale draft/Mathlib wording reached rendered markdown") for pattern in _STALE_DRAFT_PHRASES],
    ]
    return _scan_lines(source=source, text=stripped, checks=checks)


def scan_tex_artifact(text: str, *, source: str = "combined tex") -> list[PdfValidationIssue]:
    """Scan generated TeX while allowing intentional ``\\texttt{[[...]]}`` examples."""

    stripped = _LATEX_TEXTTT_RE.sub("", text)
    checks = [
        (_MISSING_TOKEN_RE, "missing manuscript token marker reached TeX"),
        (_UNRESOLVED_PLACEHOLDER_RE, "unresolved placeholder reached TeX"),
        (_UNRESOLVED_REF_RE, "unresolved reference/citation reached TeX"),
        *[(pattern, "stale draft/Mathlib wording reached TeX") for pattern in _STALE_DRAFT_PHRASES],
    ]
    return _scan_lines(source=source, text=stripped, checks=checks)


def scan_latex_log(text: str, *, source: str = "latex log") -> list[PdfValidationIssue]:
    """Scan the LaTeX log for any warning/error class we treat as release-blocking."""

    return _scan_lines(
        source=source,
        text=text,
        checks=[(pattern, "LaTeX log issue") for pattern in _LATEX_LOG_FATAL_PATTERNS],
    )


def extract_pdf_text(pdf_path: Path, *, template_root: Path | None = None) -> str:
    """Extract text from a PDF with an optional legacy extractor and CLI fallback."""

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    if template_root is not None and template_root.exists():
        module_path = template_root / "infrastructure" / "validation" / "content" / "pdf_validator.py"
        try:
            if not module_path.exists():
                raise FileNotFoundError(module_path)
            spec = importlib.util.spec_from_file_location(
                "_actinf_template_pdf_validator",
                module_path,
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"could not load {module_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return str(module.extract_text_from_pdf(pdf_path))
        except Exception:
            # Fall through to the command-line extractor.  The caller receives
            # a failure only if every extraction path fails.
            pass

    proc = subprocess.run(
        ["pdftotext", str(pdf_path), "-"],
        capture_output=True,
        check=False,
        text=True,
        timeout=60.0,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "pdftotext failed")
    if not proc.stdout.strip():
        raise RuntimeError("pdftotext returned empty text")
    return proc.stdout


def parse_geometry_margins(preamble_text: str) -> dict[str, float]:
    """Parse inch margins from the LaTeX ``geometry`` package line."""

    match = re.search(r"\\usepackage\[(?P<opts>[^\]]+)\]\{geometry\}", preamble_text)
    if not match:
        return {}
    margins: dict[str, float] = {}
    for part in match.group("opts").split(","):
        key, sep, value = part.strip().partition("=")
        if sep != "=" or not value.endswith("in"):
            continue
        try:
            margins[key] = float(value[:-2])
        except ValueError:
            continue
    return margins


def validate_preamble_margins(preamble_path: Path) -> list[PdfValidationIssue]:
    """Validate the compact PDF margin contract."""

    if not preamble_path.exists():
        return [PdfValidationIssue(str(preamble_path), 0, "preamble missing", str(preamble_path))]
    margins = parse_geometry_margins(preamble_path.read_text(encoding="utf-8"))
    issues: list[PdfValidationIssue] = []
    for key, expected in EXPECTED_PDF_MARGINS_IN.items():
        got = margins.get(key)
        if got is None:
            issues.append(PdfValidationIssue(str(preamble_path), 0, f"missing geometry margin {key}", ""))
        elif abs(got - expected) > 1e-9:
            issues.append(
                PdfValidationIssue(
                    str(preamble_path),
                    0,
                    f"geometry margin {key}={got:g}in != expected {expected:g}in",
                    "",
                )
            )
    return issues


def validate_pdf_artifacts(
    *,
    project_root: Path,
    pdf_path: Path | None = None,
    template_root: Path | None = None,
) -> list[PdfValidationIssue]:
    """Validate the current rendered PDF and its intermediate artifacts."""

    root = Path(project_root)
    pdf = pdf_path or root / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf"
    issues: list[PdfValidationIssue] = []
    if not pdf.exists():
        return [PdfValidationIssue(str(pdf), 0, "PDF missing", str(pdf))]
    if pdf.stat().st_size < 1_000:
        issues.append(PdfValidationIssue(str(pdf), 0, "PDF too small", f"{pdf.stat().st_size} bytes"))

    try:
        issues.extend(scan_pdf_text(extract_pdf_text(pdf, template_root=template_root), source=str(pdf)))
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        issues.append(PdfValidationIssue(str(pdf), 0, "could not extract PDF text", str(exc)))

    md_path = root / "output" / "pdf" / "_combined_manuscript.md"
    tex_path = root / "output" / "pdf" / "_combined_manuscript.tex"
    log_path = root / "output" / "pdf" / "_combined_manuscript.log"
    stdout_log_path = root / "output" / "pdf" / "_xelatex_stdout.log"
    if md_path.exists():
        issues.extend(scan_markdown_artifact(md_path.read_text(encoding="utf-8"), source=str(md_path)))
    else:
        issues.append(PdfValidationIssue(str(md_path), 0, "combined markdown missing", ""))
    if tex_path.exists():
        issues.extend(scan_tex_artifact(tex_path.read_text(encoding="utf-8"), source=str(tex_path)))
    else:
        issues.append(PdfValidationIssue(str(tex_path), 0, "combined TeX missing", ""))
    if log_path.exists():
        issues.extend(scan_latex_log(log_path.read_text(encoding="utf-8", errors="ignore"), source=str(log_path)))
    else:
        issues.append(PdfValidationIssue(str(log_path), 0, "LaTeX log missing", ""))
    if stdout_log_path.exists():
        issues.extend(
            scan_latex_log(stdout_log_path.read_text(encoding="utf-8", errors="ignore"), source=str(stdout_log_path))
        )

    issues.extend(validate_preamble_margins(root / "manuscript" / "preamble.md"))
    return issues
