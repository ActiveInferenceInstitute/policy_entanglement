"""Cover residual paths in src/manuscript/* (renderer helpers, validation
edge cases, bibliography fallbacks).

Brings the manuscript subpackage over the 90 % coverage floor.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from registry import (
    Citation,
    CitationRegistry,
    Equation,
    Figure,
    LabelsRegistry,
    Registry,
    Section,  # noqa: F401
    TheoremEntry,  # noqa: F401
    load_citations,
    load_labels,
    load_registry,
)
from renderer import _format_var, render_section
from bibliography import _sorted_keys, auto_bibliography
from validation import (
    HEADING_RE,
    HYPERLINK_RE,
    SECTION_FILES_RE,
    section_paths,
    validate_figure_files,
    validate_hyperlinks,
    validate_manuscript_tree,
    validate_undefined_tokens,
    validate_variables_against_ranges,
)
from tokens import iter_tokens


PROJECT = Path(__file__).resolve().parent.parent
REFS = PROJECT / "manuscript" / "refs"
MANUSCRIPT = PROJECT / "manuscript"


# ---------------------------------------------------------------------------
# Renderer formatter helpers
# ---------------------------------------------------------------------------


def test_format_var_integer_float_collapses_to_int() -> None:
    assert _format_var(2.0, None) == "2"


def test_format_var_float_default_six_sigfig() -> None:
    out = _format_var(1.234567890123, None)
    assert out == "1.23457"


def test_format_var_explicit_format() -> None:
    assert _format_var(1.5, ".3f") == "1.500"


def test_format_var_list_renders_as_brackets() -> None:
    assert _format_var([1, 2, 3], None) == "[1, 2, 3]"


def test_format_var_string_passes_through() -> None:
    assert _format_var("hello", None) == "hello"


def test_format_var_int_no_format() -> None:
    assert _format_var(42, None) == "42"


# ---------------------------------------------------------------------------
# Renderer figure / equation / citelist substitutions
# ---------------------------------------------------------------------------


def _tiny_registry() -> Registry:
    fig = Figure(
        label="x",
        path="output/figures/whatever.png",
        caption="Sample caption.",
        short="x", sections=("§1",),
        source="scripts/x.py", number=1,
    )
    eq = Equation(
        label="e", latex="x = y", name="Sample equation",
        sections=("§1",), number=1,
    )
    cite = Citation(
        key="x-2024", authors="X, Y.", year=2024,
        title="Title", venue="Venue", topic="topicA",
    )
    return Registry(
        labels=LabelsRegistry(figures={"x": fig}, equations={"e": eq}),
        citations=CitationRegistry(
            entries={"x-2024": cite},
            topic_order=("topicA",),
            topic_titles={"topicA": "Topic A"},
        ),
    )


def test_render_section_resolves_figref() -> None:
    reg = _tiny_registry()
    out = render_section(
        "See [[FIGREF:x]].",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "Fig. 1" in out.text


def test_render_section_resolves_eq_block() -> None:
    reg = _tiny_registry()
    out = render_section(
        "Eqn: [[EQ:e]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "$$" in out.text and "x = y" in out.text


def test_render_section_resolves_eqref() -> None:
    reg = _tiny_registry()
    out = render_section(
        "see [[EQREF:e]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "Eq. (1)" in out.text


def test_render_section_resolves_citelist() -> None:
    reg = _tiny_registry()
    out = render_section(
        "[[CITELIST:topicA]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "Topic A" in out.text
    assert "X, Y." in out.text


def test_render_section_marks_missing_eq_and_eqref() -> None:
    reg = _tiny_registry()
    out = render_section(
        "[[EQ:nope]] [[EQREF:nope]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "MISSING:EQ:nope" in out.text
    assert "MISSING:EQREF:nope" in out.text
    assert sorted(set(out.missing_equations)) == ["nope"]


def test_render_section_marks_missing_figref() -> None:
    reg = _tiny_registry()
    out = render_section(
        "[[FIGREF:nope]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "MISSING:FIGREF:nope" in out.text
    assert out.missing_figures == ["nope"]


# ---------------------------------------------------------------------------
# Bibliography
# ---------------------------------------------------------------------------


def test_auto_bibliography_unknown_topic_returns_empty() -> None:
    reg = load_citations(REFS / "citations.yaml")
    assert auto_bibliography(reg, topic="this_topic_does_not_exist") == ""


def test_auto_bibliography_handles_uncategorised_entries() -> None:
    reg = CitationRegistry(
        entries={
            "extra-2099": Citation(
                key="extra-2099", authors="Z, W.", year=2099,
                title="t", venue="v", topic="orphan",
            ),
            "x-2024": Citation(
                key="x-2024", authors="X, Y.", year=2024,
                title="t", venue="v", topic="known",
            ),
        },
        topic_order=("known",),
        topic_titles={"known": "Known"},
    )
    body = auto_bibliography(reg, topic="all")
    assert "Known" in body
    # Orphan topic should appear under its title-cased label as fallback.
    assert "Orphan" in body


def test_sorted_keys_returns_alphabetical() -> None:
    reg = CitationRegistry(
        entries={
            "b-2024": Citation(key="b-2024", authors="B", year=2024,
                                title="t", venue="v", topic="t"),
            "a-2024": Citation(key="a-2024", authors="A", year=2024,
                                title="t", venue="v", topic="t"),
        },
        topic_order=("t",),
        topic_titles={"t": "T"},
    )
    assert _sorted_keys(reg, "t") == ["a-2024", "b-2024"]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_section_paths_includes_99_bibliography() -> None:
    paths = section_paths(MANUSCRIPT)
    names = [p.name for p in paths]
    assert "99_bibliography.md" in names


def test_section_files_re_matches_only_numbered_sections() -> None:
    assert SECTION_FILES_RE.match("00_abstract.md")
    assert SECTION_FILES_RE.match("17_closing.md")
    assert SECTION_FILES_RE.match("S03_appendix.md")
    assert SECTION_FILES_RE.match("preamble.md")
    assert not SECTION_FILES_RE.match("README.md")


def test_heading_re_rejects_non_heading() -> None:
    assert HEADING_RE.match("# Title")
    assert not HEADING_RE.match("paragraph text")


def test_hyperlink_re_finds_targets() -> None:
    text = "see [a](b.md) and [c](https://x)"
    matches = list(HYPERLINK_RE.finditer(text))
    assert len(matches) == 2


def test_validate_hyperlinks_skips_mailto() -> None:
    # mailto links are external; should not be flagged as broken.
    broken = validate_hyperlinks("[Contact](mailto:x@y)", base=MANUSCRIPT)
    assert broken == []


def test_validate_figure_files_skips_external() -> None:
    out = validate_figure_files(
        "![alt](https://example.com/x.png)", manuscript_dir=MANUSCRIPT,
    )
    assert out == []


def test_validate_undefined_tokens_handles_citelist() -> None:
    reg = _tiny_registry()
    bad = validate_undefined_tokens(
        "[[CITELIST:topicA]] [[CITELIST:nope]]",
        reg, variables={},
    )
    kinds = [k for k, _ in bad]
    assert "CITELIST" in kinds


def test_validate_undefined_tokens_eq_unknown() -> None:
    reg = _tiny_registry()
    bad = validate_undefined_tokens(
        "[[EQ:unknown]] [[EQREF:unknown]]",
        reg, variables={},
    )
    kinds = sorted({k for k, _ in bad})
    assert kinds == ["EQ", "EQREF"]


def test_validate_variables_handles_missing_or_non_numeric() -> None:
    bad = validate_variables_against_ranges(
        {"a": "not_a_number"}, {"a": (0.0, 1.0), "b": (0.0, 1.0)},
    )
    assert "a" in bad and "non-numeric" in bad["a"]
    assert "b" in bad and "missing" in bad["b"]


def test_validate_manuscript_tree_handles_pandoc_raw_block(tmp_path: Path) -> None:
    """Sections that lead with a Pandoc raw-LaTeX block must still be
    accepted as having a leading heading further down."""
    section = tmp_path / "S99_test.md"
    section.write_text(
        "```{=latex}\n\\appendix\n```\n\n# Real Heading\n\nbody.\n"
    )
    reg = _tiny_registry()
    report = validate_manuscript_tree(
        manuscript_dir=tmp_path, registry=reg, variables={},
    )
    assert "S99_test.md" not in report.missing_headings


def test_validate_manuscript_tree_detects_missing_heading(tmp_path: Path) -> None:
    section = tmp_path / "00_no_heading.md"
    section.write_text("Just some prose, no heading.\n")
    reg = _tiny_registry()
    report = validate_manuscript_tree(
        manuscript_dir=tmp_path, registry=reg, variables={},
    )
    assert "00_no_heading.md" in report.missing_headings


def test_validate_manuscript_tree_runs_variable_ranges() -> None:
    reg = _tiny_registry()
    report = validate_manuscript_tree(
        manuscript_dir=MANUSCRIPT, registry=reg, variables={"x": 0.5},
        variable_ranges={"x": (0.0, 1.0)},
    )
    # Ranges argument was honoured (no violation).
    assert "x" not in report.out_of_range_variables


# ---------------------------------------------------------------------------
# iter_tokens edge cases
# ---------------------------------------------------------------------------


def test_iter_tokens_empty_text() -> None:
    assert list(iter_tokens("")) == []


def test_iter_tokens_no_tokens() -> None:
    assert list(iter_tokens("just prose")) == []


def test_render_result_is_complete_property() -> None:
    from renderer import RenderResult
    assert RenderResult(text="").is_complete
    r = RenderResult(text="", missing_figures=["x"])
    assert not r.is_complete


def test_validation_report_is_clean_property() -> None:
    from validation import ManuscriptValidationReport
    r = ManuscriptValidationReport(section_files=[])
    assert r.is_clean
    r.missing_headings.append("x.md")
    assert not r.is_clean


# ---------------------------------------------------------------------------
# registry.py edge cases
# ---------------------------------------------------------------------------


def test_seq_handles_none_str_and_iterable() -> None:
    from registry import _seq
    assert _seq(None) == tuple()
    assert _seq("only_one") == ("only_one",)
    assert _seq(["a", "b"]) == ("a", "b")


def test_load_citations_skips_non_dict_payload(tmp_path: Path) -> None:
    """An ill-formed entry (e.g. a list) is skipped silently rather than
    crashing the whole load."""
    from registry import load_citations
    yaml_path = tmp_path / "citations.yaml"
    yaml_path.write_text(
        "topic_order: ['a']\n"
        "topic_titles: {a: A}\n"
        "ok-2024:\n"
        "  authors: 'X'\n"
        "  year: 2024\n"
        "  title: 't'\n"
        "  venue: 'v'\n"
        "  topic: a\n"
        "broken: [not-a-dict, payload]\n"
    )
    reg = load_citations(yaml_path)
    assert "ok-2024" in reg.entries
    assert "broken" not in reg.entries


def test_citation_render_bibliography_with_doi() -> None:
    from registry import Citation
    c = Citation(
        key="x", authors="A", year=2020, title="t", venue="v",
        doi="10.1234/abc",
    )
    line = c.render_bibliography()
    assert "doi:10.1234/abc" in line


# ---------------------------------------------------------------------------
# bibliography.py: empty topic + topic_order fallback
# ---------------------------------------------------------------------------


def test_auto_bibliography_skips_empty_topic_in_topic_order() -> None:
    """When `topic_order` lists a topic with no matching entries, the
    auto-bib should silently skip it (covers the `if not keys: continue`
    branch)."""
    reg = CitationRegistry(
        entries={
            "x-2024": Citation(
                key="x-2024", authors="X", year=2024, title="t",
                venue="v", topic="real",
            ),
        },
        topic_order=("empty_topic", "real"),
        topic_titles={"empty_topic": "Empty", "real": "Real"},
    )
    body = auto_bibliography(reg, topic="all")
    assert "Empty" not in body  # skipped
    assert "Real" in body


# ---------------------------------------------------------------------------
# renderer.py: render_all without a variables JSON
# ---------------------------------------------------------------------------


def test_render_all_works_with_missing_variables_path(tmp_path: Path) -> None:
    """`render_all` should still write the rendered sections even when
    `variables_path` does not exist (no `[[VAR:...]]` tokens are
    resolvable, but pure text + figure / citation tokens still work)."""
    from registry import load_registry
    from renderer import render_all
    reg = load_registry(REFS)
    out = tmp_path / "rendered"
    # Only render a single tiny section so the test is fast.
    src = tmp_path / "manuscript_src"
    src.mkdir()
    (src / "00_only.md").write_text(
        "# Hello\n\nThis section has no VAR tokens but cites [@heins-2022].\n"
    )
    results = render_all(
        manuscript_dir=src,
        output_dir=out,
        registry=reg,
        variables_path=tmp_path / "missing.json",
    )
    assert "00_only.md" in results
    assert results["00_only.md"].is_complete


# ---------------------------------------------------------------------------
# validation.py: hyperlink anchor + docstring-style stripping
# ---------------------------------------------------------------------------


def test_validate_hyperlinks_resolves_anchor_only_links_against_existing_file(tmp_path: Path) -> None:
    """A link of the form `target.md#section` should still verify the
    file exists (anchor is stripped before resolution)."""
    md = tmp_path / "x.md"
    target = tmp_path / "target.md"
    target.write_text("# heading\n")
    md.write_text("[a](target.md#heading)")
    broken = validate_hyperlinks(md.read_text(), base=tmp_path)
    assert broken == []


def test_validate_figure_files_strips_anchor() -> None:
    """Image link with an anchor portion should still resolve."""
    text = "![alt](does/not/exist.png#anchor)"
    bad = validate_figure_files(text, manuscript_dir=PROJECT)
    # Anchor gets stripped, then the path is validated relative to project.
    assert "does/not/exist.png" in bad


# ---------------------------------------------------------------------------
# Section cross-reference validator
# ---------------------------------------------------------------------------


def test_section_ref_re_captures_top_level_and_subsection() -> None:
    from validation import SECTION_REF_RE
    matches = list(SECTION_REF_RE.finditer("see §3 and §3.2 and §11.12"))
    assert len(matches) == 3
    assert matches[0].group(1) == "3" and matches[0].group(2) is None
    assert matches[1].group(1) == "3" and matches[1].group(2) == "2"
    assert matches[2].group(1) == "11" and matches[2].group(2) == "12"


def test_collect_top_level_sections_from_real_manuscript() -> None:
    from validation import collect_top_level_sections
    out = collect_top_level_sections(MANUSCRIPT)
    # Sections 0..17 plus 99 should all be there (99 is bibliography).
    assert {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17}.issubset(out)


def test_collect_section_subheadings_finds_real_subsections() -> None:
    from validation import collect_section_subheadings
    out = collect_section_subheadings(MANUSCRIPT)
    # §11 has 12 subsections (11.1 through 11.12).
    assert 11 in out
    assert {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}.issubset(out[11])
    # §6 has 4 subsections (6.1, 6.2, 6.3, 6.4).
    assert 6 in out
    assert {1, 2, 3, 4}.issubset(out[6])


def test_validate_section_references_accepts_known_subsection() -> None:
    from validation import validate_section_references
    bad = validate_section_references(
        "Refer to §3.2 and §11.12.",
        top_level={3, 11},
        subsections={3: {1, 2}, 11: {1, 12}},
    )
    assert bad == []


def test_validate_section_references_flags_unknown_subsection() -> None:
    from validation import validate_section_references
    bad = validate_section_references(
        "See §3.99 (does not exist).",
        top_level={3},
        subsections={3: {1, 2}},
    )
    assert len(bad) == 1
    assert "§3.99" in bad[0]


def test_validate_section_references_flags_missing_top_level() -> None:
    from validation import validate_section_references
    bad = validate_section_references(
        "See §42.",
        top_level={1, 2},
        subsections={},
    )
    assert len(bad) == 1
    assert "§42" in bad[0]


def test_validate_section_references_accepts_99_bibliography() -> None:
    from validation import validate_section_references
    bad = validate_section_references(
        "see the bibliography in §99.",
        top_level={1},
        subsections={},
    )
    assert bad == []  # 99 is the bibliography file, always valid


def test_validate_manuscript_tree_clean_for_real_repository_with_section_refs() -> None:
    from registry import load_registry
    from validation import validate_manuscript_tree
    reg = load_registry(REFS)
    report = validate_manuscript_tree(
        manuscript_dir=MANUSCRIPT, registry=reg, variables={},
    )
    assert not report.bad_section_refs, report.bad_section_refs


def test_validation_report_is_clean_with_bad_section_refs() -> None:
    from validation import ManuscriptValidationReport
    r = ManuscriptValidationReport(section_files=[])
    r.bad_section_refs["x.md"] = ["§99.99"]
    assert not r.is_clean


# ---------------------------------------------------------------------------
# New SEC / SECREF / THM / THMREF tokens
# ---------------------------------------------------------------------------


def test_sec_token_regex_matches() -> None:
    from tokens import SEC_RE, SECREF_RE
    assert SEC_RE.match("[[SEC:motivation]]") is not None
    assert SEC_RE.match("[[SEC:lambda_deformation.precision]]") is not None
    assert SECREF_RE.match("[[SECREF:phase]]") is not None
    assert SECREF_RE.match("[[SECREF:setup.mf_baseline]]") is not None


def test_thm_token_regex_matches() -> None:
    from tokens import THM_RE, THMREF_RE
    assert THM_RE.match("[[THM:thm_4_1]]") is not None
    assert THMREF_RE.match("[[THMREF:cor_4_3]]") is not None


def test_iter_tokens_recognises_sec_and_thm() -> None:
    text = (
        "open [[SEC:motivation]], cross-ref [[SECREF:phase]], "
        "block [[THM:thm_4_1]], inline [[THMREF:cor_4_3]]."
    )
    kinds = sorted({k for k, *_ in iter_tokens(text)})
    assert "SEC" in kinds
    assert "SECREF" in kinds
    assert "THM" in kinds
    assert "THMREF" in kinds


def test_render_resolves_secref_to_section_number() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "Cross-ref to [[SECREF:motivation]] and [[SECREF:phase.diagram]].",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "§1" in out.text
    assert "§9.1" in out.text
    assert out.is_complete


def test_render_resolves_sec_to_full_label() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "Heading: [[SEC:examples]].",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "§5 Examples and Worked Cases" in out.text


def test_render_resolves_thm_to_bold_block() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "[[THM:thm_4_1]]\n\nThe statement follows...",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "**Theorem 4.1 (Entanglement Decomposition).**" in out.text


def test_render_resolves_thmref_to_inline() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "Recall [[THMREF:thm_8_1]] and [[THMREF:cor_4_2]].",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "Theorem 8.1" in out.text
    assert "Corollary 4.2" in out.text


def test_render_marks_missing_sec_and_thm_tokens() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "[[SEC:nope]] [[SECREF:nope]] [[THM:nope]] [[THMREF:nope]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
    )
    assert "nope" in out.text
    assert sorted(set(out.missing_sections)) == ["nope"]
    assert sorted(set(out.missing_theorems)) == ["nope"]


def test_render_result_is_complete_includes_sec_and_thm() -> None:
    from renderer import RenderResult
    r = RenderResult(text="", missing_sections=["x"])
    assert not r.is_complete
    r2 = RenderResult(text="", missing_theorems=["y"])
    assert not r2.is_complete


def test_load_registry_includes_sections_and_theorems() -> None:
    reg = load_registry(REFS)
    assert reg.labels.sections
    assert "decomposition" in reg.labels.sections
    assert reg.labels.sections["decomposition"].number == "4"
    assert reg.labels.theorems
    assert "thm_4_1" in reg.labels.theorems
    t = reg.labels.theorems["thm_4_1"]
    assert t.kind == "Theorem"
    assert t.number == "4.1"


def test_section_with_parent_relationship() -> None:
    reg = load_registry(REFS)
    sub = reg.labels.sections["setup.pomdp"]
    assert sub.parent == "setup"
    assert sub.number == "2.1"


def test_theorem_render_block_with_and_without_name() -> None:
    from registry import TheoremEntry
    t1 = TheoremEntry(
        label="x", kind="Theorem", number="9.9", name="Named", section="x",
    )
    assert t1.render_block() == "**Theorem 9.9 (Named).**"
    assert t1.render_inline() == "Theorem 9.9"
    t2 = TheoremEntry(
        label="y", kind="Lemma", number="3.3", name="", section="y",
    )
    assert t2.render_block() == "**Lemma 3.3.**"


# ---------------------------------------------------------------------------
# Hardcoded-ref detector
# ---------------------------------------------------------------------------


def test_find_hardcoded_refs_flags_bare_section_in_prose() -> None:
    from validation import find_hardcoded_refs
    text = "We discuss this in §11.2 in more detail."
    out = find_hardcoded_refs(text)
    assert "§11.2" in out


def test_find_hardcoded_refs_flags_bare_theorem_in_prose() -> None:
    from validation import find_hardcoded_refs
    text = "Recall Theorem 4.1 from earlier."
    out = find_hardcoded_refs(text)
    assert any("Theorem 4.1" in s for s in out)


def test_find_hardcoded_refs_skips_heading() -> None:
    from validation import find_hardcoded_refs
    text = "## §4.2 The Proof\n\nbody.\n"
    out = find_hardcoded_refs(text)
    assert "§4.2" not in out


def test_find_hardcoded_refs_skips_inline_code() -> None:
    from validation import find_hardcoded_refs
    text = "The literal `§3.2` is code, not a reference."
    out = find_hardcoded_refs(text)
    assert "§3.2" not in out


def test_find_hardcoded_refs_skips_theorem_label_paragraph() -> None:
    from validation import find_hardcoded_refs
    text = "**Theorem 4.1 (X).** Body of the statement uses Theorem 4.1 internally."
    out = find_hardcoded_refs(text)
    assert "Theorem 4.1" not in out


def test_validate_manuscript_tree_no_hardcoded_refs() -> None:
    """Real manuscript: zero hardcoded refs after the migration."""
    from registry import load_registry
    from validation import validate_manuscript_tree
    reg = load_registry(REFS)
    report = validate_manuscript_tree(
        manuscript_dir=MANUSCRIPT, registry=reg, variables={},
    )
    assert not report.hardcoded_refs, report.hardcoded_refs


def test_validation_report_is_clean_with_hardcoded_refs() -> None:
    from validation import ManuscriptValidationReport
    r = ManuscriptValidationReport(section_files=[])
    r.hardcoded_refs["x.md"] = ["§99"]
    assert not r.is_clean


# ---------------------------------------------------------------------------
# Final coverage closures (audit-driven additions)
# ---------------------------------------------------------------------------


def test_validate_hyperlinks_skips_data_uri() -> None:
    """data: URI links must be silently skipped (not flagged as broken)."""
    from validation import validate_hyperlinks
    text = "Embedded [icon](data:image/png;base64,AAAA) in prose."
    assert validate_hyperlinks(text, base=MANUSCRIPT) == []


def test_validate_hyperlinks_skips_token_marker() -> None:
    """Links whose target starts with `[[` are token markers, not real URLs."""
    from validation import validate_hyperlinks
    text = "Reference [token]([[FIG:placeholder]]) — should be ignored."
    assert validate_hyperlinks(text, base=MANUSCRIPT) == []


def test_validate_hyperlinks_skips_generated_output_paths() -> None:
    """Links pointing into `output/` are generated artefacts; their
    existence at validation time is not required."""
    from validation import validate_hyperlinks, _is_generated_output_path
    assert _is_generated_output_path("../output/figures/whatever.png")
    assert _is_generated_output_path("output/data/foo.csv")
    assert not _is_generated_output_path("../src/lean/joint_dist.py")
    text = "[gen](../output/data/never_existed.csv) and [src](../src/lean/joint_dist.py)"
    out = validate_hyperlinks(text, base=MANUSCRIPT)
    # Only src path is checked; it exists.
    assert out == []


def test_validate_figure_files_reports_missing_png(tmp_path: Path) -> None:
    """When the PNG referenced by `![](path)` does not exist, it must
    appear in the broken-image list."""
    from validation import validate_figure_files
    md = "![alt text](does/not/exist.png)"
    bad = validate_figure_files(md, manuscript_dir=tmp_path)
    assert "does/not/exist.png" in bad


def test_collect_top_level_sections_handles_malformed_filename(tmp_path: Path) -> None:
    """`collect_top_level_sections` should silently skip files whose
    two-character prefix is not numeric."""
    from validation import collect_top_level_sections
    (tmp_path / "ZZ_invalid.md").write_text("# X")
    (tmp_path / "01_real.md").write_text("# Real")
    out = collect_top_level_sections(tmp_path)
    assert out == {1}


def test_load_labels_skips_non_dict_section_payload(tmp_path: Path) -> None:
    """Defensive guard: malformed `sections:` entries (not dicts) are
    silently skipped during load."""
    from registry import load_labels
    yaml_path = tmp_path / "labels.yaml"
    yaml_path.write_text(
        "figures: {}\n"
        "equations: {}\n"
        "sections:\n"
        "  good: {number: '1', title: 'OK'}\n"
        "  broken: ['this', 'is', 'a', 'list']\n"
        "theorems: {}\n"
    )
    lr = load_labels(yaml_path)
    assert "good" in lr.sections
    assert "broken" not in lr.sections


def test_load_labels_skips_non_dict_theorem_payload(tmp_path: Path) -> None:
    from registry import load_labels
    yaml_path = tmp_path / "labels.yaml"
    yaml_path.write_text(
        "figures: {}\n"
        "equations: {}\n"
        "sections: {}\n"
        "theorems:\n"
        "  ok: {kind: 'Theorem', number: '1.1', section: 'x'}\n"
        "  bad: 'just a string'\n"
    )
    lr = load_labels(yaml_path)
    assert "ok" in lr.theorems
    assert "bad" not in lr.theorems


def test_plot_rollout_marginals_rejects_empty_marginals_list(tmp_path: Path) -> None:
    """K < 1 triggers ValueError guard at trajectory_plots line 30."""
    import numpy as np
    from trajectory_plots import plot_rollout_marginals
    with pytest.raises(ValueError, match="non-empty"):
        plot_rollout_marginals(
            marginals_per_stream=[], titles=[],
            total_correlations=np.zeros(0), out_path=tmp_path / "x.png",
        )


# ---------------------------------------------------------------------------
# Lean-source auto-extraction for [[LEAN:label]] tokens
# ---------------------------------------------------------------------------


LEAN_DIR = PROJECT / "lean" / "ActinfPolicyEntanglement"


def test_lean_extract_loads_decomposition_module() -> None:
    """The on-disk Lean source must be parseable; the
    `entanglement_decomposition` theorem must be discoverable."""
    from lean_extract import load_lean_snippets
    snippets = load_lean_snippets(LEAN_DIR)
    key = ("Decomposition", "entanglement_decomposition")
    assert key in snippets, sorted(s for s in snippets if s[0] == "Decomposition")
    s = snippets[key]
    assert s.keyword == "theorem"
    assert "entanglement_decomposition" in s.body
    assert s.module == "Decomposition"
    assert s.start_line > 0


def test_lean_extract_handles_inner_namespaces() -> None:
    """`Bipartite.schmidtRank_one_iff_meanField` lives inside the
    `Bipartite` inner namespace and must surface fully qualified."""
    from lean_extract import load_lean_snippets
    snippets = load_lean_snippets(LEAN_DIR)
    key = ("Spectral", "Bipartite.schmidtRank_one_iff_meanField")
    assert key in snippets, sorted(k for k in snippets if k[0] == "Spectral")


def test_render_lean_snippet_includes_status() -> None:
    """The renderer wraps the snippet in a fenced ```lean block and
    annotates the status keyword on the source-citation line."""
    from lean_extract import load_lean_snippets, render_lean_snippet
    snippets = load_lean_snippets(LEAN_DIR)
    snip = snippets[("Decomposition", "entanglement_decomposition")]
    out = render_lean_snippet(snip, status="boundary")
    assert out.startswith("```lean")
    assert out.rstrip().endswith("```")
    assert "[status: **boundary**]" in out
    assert "Decomposition.lean:" in out


def test_render_section_resolves_lean_token() -> None:
    """`[[LEAN:thm_4_1]]` must expand to a fenced Lean block."""
    from lean_extract import load_lean_snippets
    reg = load_registry(REFS)
    snippets = load_lean_snippets(LEAN_DIR)
    out = render_section(
        "[[LEAN:thm_4_1]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
        lean_snippets=snippets,
    )
    assert "```lean" in out.text
    assert "entanglement_decomposition" in out.text
    assert out.is_complete


def test_render_section_lean_token_missing_when_no_cache() -> None:
    """Without a `lean_snippets` cache, the renderer marks the token
    as missing rather than crashing."""
    reg = load_registry(REFS)
    out = render_section(
        "[[LEAN:thm_4_1]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
        lean_snippets=None,
    )
    assert "[[MISSING:LEAN:thm_4_1" in out.text
    assert "thm_4_1" in out.missing_lean


def test_render_section_lean_token_missing_when_no_companion() -> None:
    """A theorem registered without `lean_module`/`lean_name` (e.g.
    `thm_4_2`, `prop_10_1`, `thm_11_1`, …) flags as missing-LEAN."""
    from registry import LabelsRegistry, TheoremEntry
    reg = load_registry(REFS)
    out = render_section(
        "[[LEAN:thm_4_2]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
        lean_snippets={},
    )
    assert "no lean_module/lean_name in registry" in out.text
    assert "thm_4_2" in out.missing_lean


def test_render_section_lean_token_unknown_label() -> None:
    """An unknown label raises a missing-LEAN marker."""
    reg = load_registry(REFS)
    out = render_section(
        "[[LEAN:nonexistent_label]]",
        registry=reg, variables={}, manuscript_dir=MANUSCRIPT,
        lean_snippets={},
    )
    assert "[[MISSING:LEAN:nonexistent_label]]" in out.text
    assert "nonexistent_label" in out.missing_lean
