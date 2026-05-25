"""Tests for the manuscript registry, tokens, and renderer."""

from __future__ import annotations

import json
from pathlib import Path

from manuscript.bibliography import auto_bibliography, write_references_bib
from manuscript.meta_files import MANUSCRIPT_NON_BODY_MD
from manuscript.registry import (
    Citation,
    CitationRegistry,
    LabelsRegistry,
    Registry,
    load_citations,
    load_labels,
    load_registry,
)
from manuscript.renderer import render_all, render_section
from manuscript.tokens import (
    CITATION_RE,
    EQ_RE,
    EQREF_RE,
    FIG_RE,
    FIGREF_RE,
    VAR_RE,
    iter_tokens,
)
from manuscript.validation import (
    ManuscriptValidationReport,
    validate_figure_files,
    validate_hyperlinks,
    validate_manuscript_tree,
    validate_undefined_tokens,
    validate_variables_against_ranges,
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
        key="x",
        authors="Smith, J., Jones, K.",
        year=2020,
        title="t",
        venue="v",
    )
    assert c.render_inline() == "(Smith 2020)"


def test_citation_render_bibliography_includes_url_and_note() -> None:
    c = Citation(
        key="x",
        authors="Doe, A.",
        year=2021,
        title="T",
        venue="V",
        url="https://example.com",
        note="A note.",
    )
    line = c.render_bibliography()
    assert line.startswith("- ")
    assert "https://example.com" in line
    assert "*A note.*" in line


def test_citation_render_bibliography_preserves_title_question_mark() -> None:
    c = Citation(
        key="x",
        authors="Doe, A.",
        year=2021,
        title="A title?",
        venue="V",
    )

    assert "A title?. " not in c.render_bibliography()
    assert "A title? " in c.render_bibliography()


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def test_render_section_resolves_var() -> None:
    reg = load_registry(REFS)
    text = "MI at λ=1 is [[VAR:ising_mi_at_lam_1:.3f]] nats."
    result = render_section(
        text,
        registry=reg,
        variables={"ising_mi_at_lam_1": 0.123456},
        manuscript_dir=MANUSCRIPT,
    )
    assert "0.123" in result.text
    assert result.is_complete


def test_render_section_resolves_fig() -> None:
    reg = load_registry(REFS)
    result = render_section(
        "[[FIG:phase_landscape]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    # Pandoc-crossref-attributed image directive: `![caption](path){#fig:LABEL}`.
    assert "![" in result.text
    assert "phase_landscape" in result.text
    assert "(../output/figures/phase_landscape.png)" in result.text
    assert "{#fig:phase_landscape}" in result.text
    assert "Uncertainty semantics:" in result.text


def test_render_section_resolves_multi_citation() -> None:
    """`[@a; @b]` renders as `\\citep{a,b}` — single natbib command,
    comma-separated keys.
    """
    reg = load_registry(REFS)
    result = render_section(
        "see [@heins-2022; @friston-2017] for context.",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "\\citep{heins-2022,friston-2017}" in result.text


def test_render_section_resolves_citation() -> None:
    reg = load_registry(REFS)
    result = render_section(
        "Per [@heins-2022], pymdp grounds AIF.",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "\\citep{heins-2022}" in result.text


def test_render_section_marks_missing_tokens() -> None:
    reg = load_registry(REFS)
    text = "[[FIG:does_not_exist]] [[VAR:ghost]] [@nobody]"
    result = render_section(
        text,
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
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
            capture_output=True,
            text=True,
            cwd=PROJECT,
            timeout=120,
        )
        # Surfacing the failure helps quick debugging.
        assert result.returncode == 0, f"manuscript_variables.py failed: {result.stderr}"
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


def test_write_references_bib_emits_article_for_journals(tmp_path: Path) -> None:
    reg = load_citations(REFS / "citations.yaml")
    out = tmp_path / "references.bib"
    write_references_bib(reg, out)
    text = out.read_text()
    assert "@article{friston-2017," in text
    assert "journal = {Neural Computation}" in text
    assert "author = {Friston, K. and FitzGerald, T. and Rigoli, F. and Schwartenbeck, P. and Pezzulo, G.}" in text


def test_write_references_bib_misc_for_http_venue(tmp_path: Path) -> None:
    reg = load_citations(REFS / "citations.yaml")
    out = tmp_path / "references.bib"
    write_references_bib(reg, out)
    text = out.read_text()
    assert "@misc{bradbury-2018," in text
    assert "http://github.com/jax-ml/jax" in text


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
        {"x": 5.0},
        {"x": (0.0, 1.0)},
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


# ---------------------------------------------------------------------------
# Round-1 invariants: citation/topic registry coherence.
#
# Round 1 added 20 new bibliography entries and 2 new topics
# (control_rl, markov_blanket). These tests pin the contract that:
#   * every entry's `topic` field is registered in `topic_order` (else
#     `auto_bibliography(topic="all")` silently drops that entry),
#   * citekeys are unique (a duplicate key would silently overwrite
#     because YAML/dict semantics keep the last one),
#   * every body-used `[@key]` resolves against the registry.
# ---------------------------------------------------------------------------


def test_every_citation_topic_appears_in_topic_order() -> None:
    """Every `topic` referenced by a citation entry must be registered
    in `topic_order` (otherwise `auto_bibliography(topic="all")` skips
    the entry — a silent failure mode for new bibliography sections).
    """
    reg = load_citations(REFS / "citations.yaml")
    registered = set(reg.topic_order)
    stray = sorted({c.topic for c in reg.entries.values() if c.topic and c.topic not in registered})
    assert not stray, (
        f"citations.yaml has topics not in topic_order: {stray}. "
        "Add them to `topic_order` (and `topic_titles`) so "
        "auto-bibliography includes them."
    )


def test_citations_yaml_has_unique_citekeys() -> None:
    """Every top-level citekey in `citations.yaml` must be unique.

    A duplicate key in the raw YAML would silently survive (PyYAML
    keeps the last definition under dict semantics), so this test
    reads the file as text and counts colon-prefixed top-level keys.
    """
    import re as _re

    text = (REFS / "citations.yaml").read_text()
    # Top-level entry keys are at column 0 (no leading whitespace),
    # end in ':' and are followed by a newline (the YAML payload sits
    # on the next indented lines).
    keys = _re.findall(r"(?m)^([A-Za-z][A-Za-z0-9_-]+):\s*$", text)
    # Drop the registry-level non-entry keys.
    keys = [k for k in keys if k not in {"topic_order", "topic_titles"}]
    duplicates = sorted({k for k in keys if keys.count(k) > 1})
    assert not duplicates, f"duplicate citekeys in citations.yaml: {duplicates}"


def test_every_body_used_citation_resolves() -> None:
    """Every `[@key]` (or `[@a; @b]`) that appears in a manuscript body
    file must resolve to a real entry in `citations.yaml`.

    Iterates the manuscript tree, scrubs code fences, extracts every
    citation key via `CITATION_RE`, and asserts each is in the registry.
    """
    import re as _re

    reg = load_citations(REFS / "citations.yaml")
    known = set(reg.entries.keys())
    # Exclude docs-of-syntax files that show placeholder citations.
    skip_files = set(MANUSCRIPT_NON_BODY_MD)
    code_fence_re = _re.compile(r"(```|~~~).*?\1", _re.DOTALL)
    inline_code_re = _re.compile(r"`[^`\n]*`")
    failures: list[tuple[str, str]] = []
    for fp in MANUSCRIPT.rglob("*.md"):
        if "refs/" in str(fp) or fp.name in skip_files:
            continue
        text = code_fence_re.sub("", fp.read_text())
        text = inline_code_re.sub("", text)
        for m in CITATION_RE.finditer(text):
            for key in _re.findall(r"@([A-Za-z0-9_-]+)", m.group("inner")):
                if key not in known:
                    failures.append((fp.name, key))
    assert not failures, "Unresolved citation keys in manuscript bodies:\n  " + "\n  ".join(
        f"{fname}: [@{k}]" for fname, k in failures
    )
