"""Tests for the manuscript registry, tokens, and renderer."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from registry import (
    Citation,
    CitationRegistry,
    Equation,
    Figure,
    LabelsRegistry,
    Registry,
    load_citations,
    load_labels,
    load_registry,
)
from tokens import (
    CITATION_RE,
    EQ_RE,
    EQREF_RE,
    FIG_RE,
    FIGREF_RE,
    VAR_RE,
    iter_tokens,
)
from renderer import RenderResult, render_section, render_all
from bibliography import auto_bibliography
from validation import (
    ManuscriptValidationReport,
    validate_undefined_tokens,
    validate_hyperlinks,
    validate_figure_files,
    validate_variables_against_ranges,
    validate_manuscript_tree,
)


PROJECT = Path(__file__).resolve().parent.parent
REFS = PROJECT / "manuscript" / "refs"
MANUSCRIPT = PROJECT / "manuscript"


# ---------------------------------------------------------------------------
# Token regexes
# ---------------------------------------------------------------------------


def test_fig_token_matches() -> None:
    assert FIG_RE.match("[[FIG:phase_landscape]]") is not None
    assert FIG_RE.match("[[FIG:abc123]]") is not None
    assert FIG_RE.match("[[FIG:bad-token]]") is None  # hyphen not allowed


def test_figref_token_matches() -> None:
    assert FIGREF_RE.match("[[FIGREF:phase_landscape]]") is not None


def test_eq_token_matches() -> None:
    assert EQ_RE.match("[[EQ:tc_decomp]]") is not None
    assert EQREF_RE.match("[[EQREF:tc_decomp]]") is not None


def test_var_token_with_format() -> None:
    m = VAR_RE.match("[[VAR:ising_mi_at_lam_1:.4f]]")
    assert m is not None
    assert m.group("key") == "ising_mi_at_lam_1"
    assert m.group("fmt") == ".4f"


def test_var_token_without_format() -> None:
    m = VAR_RE.match("[[VAR:ising_mi_at_lam_1]]")
    assert m is not None
    assert m.group("fmt") is None


def test_citation_token_matches() -> None:
    """Single-citation form `[@key]` matches and exposes the key in the
    `inner` group as `@key`."""
    m = CITATION_RE.match("[@heins-2022]")
    assert m is not None
    assert m.group("inner") == "@heins-2022"


def test_citation_token_matches_multi_citation() -> None:
    """Pandoc-style multi-citation `[@a; @b; @c]` matches as a single
    token; the inner group carries every key."""
    m = CITATION_RE.match("[@friston-2017; @pezzulo-2018]")
    assert m is not None
    assert "@friston-2017" in m.group("inner")
    assert "@pezzulo-2018" in m.group("inner")


def test_iter_tokens_finds_all() -> None:
    text = (
        "First [[FIG:phase_landscape]], then [[VAR:foo:.2f]], "
        "ref [[FIGREF:bar]] eq [[EQ:tc_decomp]] cite [@heins-2022]."
    )
    kinds = [k for k, *_ in iter_tokens(text)]
    assert "FIG" in kinds
    assert "VAR" in kinds
    assert "FIGREF" in kinds
    assert "EQ" in kinds
    assert "CITE" in kinds


# ---------------------------------------------------------------------------
# Registry parsing
# ---------------------------------------------------------------------------


def test_load_labels_returns_figures_and_equations() -> None:
    lr = load_labels(REFS / "labels.yaml")
    assert isinstance(lr, LabelsRegistry)
    assert "phase_landscape" in lr.figures
    assert "tc_decomp" in lr.equations
    fig = lr.figures["phase_landscape"]
    assert fig.path.endswith(".png")
    assert fig.number >= 1


def test_load_citations_includes_pymdp() -> None:
    cr = load_citations(REFS / "citations.yaml")
    assert isinstance(cr, CitationRegistry)
    assert "heins-2022" in cr.entries
    pymdp = cr.entries["heins-2022"]
    assert pymdp.year == 2022
    assert "pymdp" in pymdp.title.lower()
    assert "active_inference" in {c.topic for c in cr.entries.values()}


def test_load_registry_round_trip() -> None:
    reg = load_registry(REFS)
    assert isinstance(reg, Registry)
    assert reg.labels.figures
    assert reg.citations.entries


def test_citation_render_inline() -> None:
    c = Citation(
        key="x", authors="Smith, J., Jones, K.", year=2020,
        title="t", venue="v",
    )
    assert c.render_inline() == "(Smith 2020)"


def test_citation_render_bibliography_includes_url_and_note() -> None:
    c = Citation(
        key="x", authors="Doe, A.", year=2021, title="T",
        venue="V", url="https://example.com", note="A note.",
    )
    line = c.render_bibliography()
    assert line.startswith("- ")
    assert "https://example.com" in line
    assert "*A note.*" in line


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def test_render_section_resolves_var() -> None:
    reg = load_registry(REFS)
    text = "MI at λ=1 is [[VAR:ising_mi_at_lam_1:.3f]] nats."
    result = render_section(
        text, registry=reg,
        variables={"ising_mi_at_lam_1": 0.123456},
        manuscript_dir=MANUSCRIPT,
    )
    assert "0.123" in result.text
    assert result.is_complete


def test_render_section_resolves_fig() -> None:
    reg = load_registry(REFS)
    result = render_section(
        "[[FIG:phase_landscape]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    # Markdown image directive `![alt](path)` — alt text is the caption,
    # downstream pandoc-crossref auto-prefixes "Figure N:".
    assert "![" in result.text
    assert "phase_landscape" in result.text
    assert "(../output/figures/phase_landscape.png)" in result.text


def test_render_section_resolves_multi_citation() -> None:
    """`[@a; @b]` renders as `(Author1 year1; Author2 year2)` — single
    outer parens, semicolon-separated inner list."""
    reg = load_registry(REFS)
    result = render_section(
        "see [@heins-2022; @friston-2017] for context.",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "(Heins 2022; Friston 2017)" in result.text


def test_render_section_resolves_citation() -> None:
    reg = load_registry(REFS)
    result = render_section(
        "Per [@heins-2022], pymdp grounds AIF.",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "(Heins 2022)" in result.text


def test_render_section_marks_missing_tokens() -> None:
    reg = load_registry(REFS)
    text = "[[FIG:does_not_exist]] [[VAR:ghost]] [@nobody]"
    result = render_section(
        text, registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert not result.is_complete
    assert result.missing_figures == ["does_not_exist"]
    assert result.missing_variables == ["ghost"]
    assert result.missing_citations == ["nobody"]


def _ensure_manuscript_variables_json() -> Path:
    """Self-bootstrap: ensure `output/data/manuscript_variables.json`
    exists by running `scripts/manuscript_variables.py` if needed.

    This makes the test robust to a freshly-cleaned `output/` (e.g. when
    the parent template's pipeline runs Stage 0 — `Clean Output Directories`
    — before Stage 3 runs the project test suite).
    """
    import subprocess
    import sys as _sys

    json_path = PROJECT / "output" / "data" / "manuscript_variables.json"
    if not json_path.exists():
        result = subprocess.run(
            [_sys.executable, str(PROJECT / "scripts" / "manuscript_variables.py")],
            capture_output=True, text=True, cwd=PROJECT, timeout=120,
        )
        # Surfacing the failure helps quick debugging.
        assert result.returncode == 0, (
            f"manuscript_variables.py failed: {result.stderr}"
        )
        assert json_path.exists(), "expected output/data/manuscript_variables.json"
    return json_path


def test_render_all_writes_every_section(tmp_path: Path) -> None:
    reg = load_registry(REFS)
    variables_path = _ensure_manuscript_variables_json()
    out = tmp_path / "rendered"
    lean_dir = PROJECT / "lean" / "ActinfPolicyEntanglement"
    results = render_all(
        manuscript_dir=MANUSCRIPT,
        output_dir=out,
        registry=reg,
        variables_path=variables_path,
        lean_dir=lean_dir,
    )
    assert results
    for name, r in results.items():
        assert (out / name).exists(), f"missing {name}"
        assert r.is_complete, f"{name}: {r.missing_figures} {r.missing_variables} {r.missing_citations}"


# ---------------------------------------------------------------------------
# Bibliography auto-generation
# ---------------------------------------------------------------------------


def test_auto_bibliography_groups_by_topic() -> None:
    reg = load_citations(REFS / "citations.yaml")
    body = auto_bibliography(reg, topic="all")
    assert "Active inference and the free-energy principle" in body
    assert "Heins, C." in body
    # Software dependencies (companion code) topic should appear too.
    assert "Software dependencies" in body


def test_auto_bibliography_single_topic() -> None:
    reg = load_citations(REFS / "citations.yaml")
    body = auto_bibliography(reg, topic="active_inference")
    assert "Heins, C." in body
    assert "Tononi" not in body  # different topic


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def test_validate_undefined_tokens_returns_unknowns() -> None:
    reg = load_registry(REFS)
    text = "[[FIG:nope]] [[VAR:nope]] [@nope-1999]"
    bad = validate_undefined_tokens(text, reg, variables={})
    kinds = sorted({k for k, _ in bad})
    assert kinds == ["CITE", "FIG", "VAR"]


def test_validate_hyperlinks_skips_external_and_anchors(tmp_path: Path) -> None:
    md = tmp_path / "x.md"
    md.write_text("[a](https://x) [b](#anchor) [c](missing.md)")
    broken = validate_hyperlinks(md.read_text(), base=tmp_path)
    assert broken == ["missing.md"]


def test_validate_figure_files_requires_existing(tmp_path: Path) -> None:
    md = tmp_path / "x.md"
    md.write_text("![alt](missing.png)")
    bad = validate_figure_files(md.read_text(), manuscript_dir=tmp_path)
    assert bad == ["missing.png"]


def test_validate_variables_against_ranges_finds_violation() -> None:
    bad = validate_variables_against_ranges(
        {"x": 5.0}, {"x": (0.0, 1.0)},
    )
    assert "x" in bad
    assert "out of range" in bad["x"]


def test_validate_variables_against_ranges_missing_key() -> None:
    bad = validate_variables_against_ranges({}, {"y": (0.0, 1.0)})
    assert "y" in bad


def test_validate_manuscript_tree_clean_repository() -> None:
    """The actual project's manuscript should pass clean."""
    reg = load_registry(REFS)
    variables_path = _ensure_manuscript_variables_json()
    variables = json.loads(variables_path.read_text())
    report = validate_manuscript_tree(
        manuscript_dir=MANUSCRIPT,
        registry=reg,
        variables=variables,
    )
    assert isinstance(report, ManuscriptValidationReport)
    assert not report.undefined_tokens, report.undefined_tokens
    assert not report.broken_links, report.broken_links
    assert not report.missing_figure_files, report.missing_figure_files
    assert not report.missing_headings, report.missing_headings
    assert not report.empty_captions, report.empty_captions
