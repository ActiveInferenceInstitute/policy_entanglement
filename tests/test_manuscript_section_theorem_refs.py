"""Coverage tests for section / theorem cross-reference handling and
the hardcoded-reference detector.

Split off from the original `test_manuscript_coverage.py`.
"""

from __future__ import annotations

from pathlib import Path

from manuscript.registry import load_registry
from manuscript.renderer import render_section
from manuscript.tokens import iter_tokens

PROJECT = Path(__file__).resolve().parent.parent
REFS = PROJECT / "manuscript" / "refs"
MANUSCRIPT = PROJECT / "manuscript"


# ---------------------------------------------------------------------------
# Section reference regexes
# ---------------------------------------------------------------------------


def test_section_ref_re_captures_top_level_and_subsection() -> None:
    from manuscript.validation import SECTION_REF_RE

    matches = list(SECTION_REF_RE.finditer("see §4 and §4.2 and §17.12"))
    assert len(matches) == 3
    assert matches[0].group(1) == "4" and matches[0].group(2) is None
    assert matches[1].group(1) == "4" and matches[1].group(2) == "2"
    assert matches[2].group(1) == "17" and matches[2].group(2) == "12"


def test_collect_top_level_sections_from_real_manuscript() -> None:
    from manuscript.validation import collect_top_level_sections

    out = collect_top_level_sections(MANUSCRIPT)
    # Tier-2 IMRAD layout: §1 motivation .. §21 discussion-and-outlook.
    assert {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21}.issubset(out)


def test_collect_section_subheadings_finds_real_subsections() -> None:
    from manuscript.validation import collect_section_subheadings

    out = collect_section_subheadings(MANUSCRIPT)
    # §17 (Connections — classical AIF) carries 4 subsections in the registry.
    assert 17 in out
    assert {1, 2, 3, 4}.issubset(out[17])
    # §18 (Connections — control / RL) carries 4 subsections.
    assert 18 in out
    assert {1, 2, 3, 4}.issubset(out[18])
    # §19 (Connections — multi-agent / geometry) carries 4 subsections (incl. CEREBRUM at 19.4).
    assert 19 in out
    assert {1, 2, 3, 4}.issubset(out[19])
    # §7 (geometry) carries 4 subsections.
    assert 7 in out
    assert {1, 2, 3, 4}.issubset(out[7])


# ---------------------------------------------------------------------------
# validate_section_references
# ---------------------------------------------------------------------------


def test_validate_section_references_accepts_known_subsection() -> None:
    from manuscript.validation import validate_section_references

    bad = validate_section_references(
        "Refer to §4.2 and §17.12.",
        top_level={4, 17},
        subsections={4: {1, 2}, 17: {1, 12}},
    )
    assert bad == []


def test_validate_section_references_flags_unknown_subsection() -> None:
    from manuscript.validation import validate_section_references

    bad = validate_section_references(
        "See §4.99 (does not exist).",
        top_level={4},
        subsections={4: {1, 2}},
    )
    assert len(bad) == 1
    assert "§4.99" in bad[0]


def test_validate_section_references_flags_missing_top_level() -> None:
    from manuscript.validation import validate_section_references

    bad = validate_section_references(
        "See §42.",
        top_level={1, 2},
        subsections={},
    )
    assert len(bad) == 1
    assert "§42" in bad[0]


def test_validate_section_references_accepts_99_bibliography() -> None:
    from manuscript.validation import validate_section_references

    bad = validate_section_references(
        "see the bibliography in §99.",
        top_level={1},
        subsections={},
    )
    assert bad == []  # 99 is the bibliography file, always valid


def test_validate_manuscript_tree_clean_for_real_repository_with_section_refs() -> None:
    from manuscript.validation import validate_manuscript_tree

    reg = load_registry(REFS)
    report = validate_manuscript_tree(
        manuscript_dir=MANUSCRIPT,
        registry=reg,
        variables={},
    )
    assert not report.bad_section_refs, report.bad_section_refs


def test_validation_report_is_clean_with_bad_section_refs() -> None:
    from manuscript.validation import ManuscriptValidationReport

    r = ManuscriptValidationReport(section_files=[])
    r.bad_section_refs["x.md"] = ["§99.99"]
    assert not r.is_clean


# ---------------------------------------------------------------------------
# SEC / SECREF / THM / THMREF tokens
# ---------------------------------------------------------------------------


def test_sec_token_regex_matches() -> None:
    from manuscript.tokens import SEC_RE, SECREF_RE

    assert SEC_RE.match("[[SEC:motivation]]") is not None
    assert SEC_RE.match("[[SEC:lambda_deformation.precision]]") is not None
    assert SECREF_RE.match("[[SECREF:phase]]") is not None
    assert SECREF_RE.match("[[SECREF:setup.mf_baseline]]") is not None


def test_thm_token_regex_matches() -> None:
    from manuscript.tokens import THM_RE, THMREF_RE

    assert THM_RE.match("[[THM:thm_4_1]]") is not None
    assert THMREF_RE.match("[[THMREF:cor_4_3]]") is not None


def test_iter_tokens_recognises_sec_and_thm() -> None:
    text = "open [[SEC:motivation]], cross-ref [[SECREF:phase]], block [[THM:thm_4_1]], inline [[THMREF:cor_4_3]]."
    kinds = sorted({k for k, *_ in iter_tokens(text)})
    assert "SEC" in kinds
    assert "SECREF" in kinds
    assert "THM" in kinds
    assert "THMREF" in kinds


def test_render_resolves_secref_to_section_number() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "Cross-ref to [[SECREF:motivation]] and [[SECREF:phase.diagram]].",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    # New rendering emits raw LaTeX hyperrefs.
    assert "\\hyperref[sec:motivation]" in out.text
    assert "§1" in out.text
    assert "\\hyperref[sec:phase.diagram]" in out.text
    assert "§10.1" in out.text
    assert out.is_complete


def test_render_resolves_sec_to_full_label() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "Heading: [[SEC:examples]].",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "\\hyperref[sec:examples]" in out.text
    assert "§6 Examples and Worked Cases" in out.text


def test_render_resolves_thm_to_bold_block() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "[[THM:thm_4_1]]\n\nThe statement follows...",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "\\phantomsection\\label{thm:thm_4_1}" in out.text
    assert "**Theorem 5.1 (Entanglement Decomposition).**" in out.text


def test_render_resolves_thmref_to_inline() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "Recall [[THMREF:thm_8_1]] and [[THMREF:cor_4_2]].",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "\\hyperref[thm:thm_8_1]" in out.text
    assert "Theorem 9.1" in out.text
    assert "\\hyperref[thm:cor_4_2]" in out.text
    assert "Corollary 5.2" in out.text


def test_render_marks_missing_sec_and_thm_tokens() -> None:
    reg = load_registry(REFS)
    out = render_section(
        "[[SEC:nope]] [[SECREF:nope]] [[THM:nope]] [[THMREF:nope]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "nope" in out.text
    assert sorted(set(out.missing_sections)) == ["nope"]
    assert sorted(set(out.missing_theorems)) == ["nope"]


def test_render_result_is_complete_includes_sec_and_thm() -> None:
    from manuscript.renderer import RenderResult

    r = RenderResult(text="", missing_sections=["x"])
    assert not r.is_complete
    r2 = RenderResult(text="", missing_theorems=["y"])
    assert not r2.is_complete


def test_load_registry_includes_sections_and_theorems() -> None:
    reg = load_registry(REFS)
    assert reg.labels.sections
    assert "decomposition" in reg.labels.sections
    # Tier-2 IMRAD: decomposition is now §5 (was §4 before).
    assert reg.labels.sections["decomposition"].number == "5"
    assert reg.labels.theorems
    assert "thm_4_1" in reg.labels.theorems
    t = reg.labels.theorems["thm_4_1"]
    assert t.kind == "Theorem"
    # Tier-2 IMRAD: thm_4_1 (entanglement decomposition) renumbered 4.1 → 5.1.
    # The label `thm_4_1` is an abstract identifier; only the displayed
    # `number` follows the new section ordering.
    assert t.number == "5.1"


def test_section_with_parent_relationship() -> None:
    reg = load_registry(REFS)
    sub = reg.labels.sections["setup.pomdp"]
    assert sub.parent == "setup"
    # Setup is §3 in the IMRAD layout, so its first subsection is §3.1.
    assert sub.number == "3.1"


def test_theorem_render_block_with_and_without_name() -> None:
    from manuscript.registry import TheoremEntry

    t1 = TheoremEntry(
        label="x",
        kind="Theorem",
        number="9.9",
        name="Named",
        section="x",
    )
    assert t1.render_block() == "**Theorem 9.9 (Named).**"
    assert t1.render_inline() == "Theorem 9.9"
    t2 = TheoremEntry(
        label="y",
        kind="Lemma",
        number="3.3",
        name="",
        section="y",
    )
    assert t2.render_block() == "**Lemma 3.3.**"


# ---------------------------------------------------------------------------
# Hardcoded-ref detector
# ---------------------------------------------------------------------------


def test_find_hardcoded_refs_flags_bare_section_in_prose() -> None:
    from manuscript.validation import find_hardcoded_refs

    text = "We discuss this in §17.2 in more detail."
    out = find_hardcoded_refs(text)
    assert "§17.2" in out


def test_find_hardcoded_refs_flags_bare_theorem_in_prose() -> None:
    from manuscript.validation import find_hardcoded_refs

    text = "Recall Theorem 5.1 from earlier."
    out = find_hardcoded_refs(text)
    assert any("Theorem 5.1" in s for s in out)


def test_find_hardcoded_refs_skips_heading() -> None:
    from manuscript.validation import find_hardcoded_refs

    text = "## §5.2 The Proof\n\nbody.\n"
    out = find_hardcoded_refs(text)
    assert "§5.2" not in out


def test_find_hardcoded_refs_skips_inline_code() -> None:
    from manuscript.validation import find_hardcoded_refs

    text = "The literal `§4.2` is code, not a reference."
    out = find_hardcoded_refs(text)
    assert "§4.2" not in out


def test_find_hardcoded_refs_skips_theorem_label_paragraph() -> None:
    from manuscript.validation import find_hardcoded_refs

    text = "**Theorem 5.1 (X).** Body of the statement uses Theorem 5.1 internally."
    out = find_hardcoded_refs(text)
    assert "Theorem 5.1" not in out


def test_find_hardcoded_refs_flags_word_form_section_in_prose() -> None:
    """Spelled-out "Section 7" / "section 7" must be caught, not only `§7`."""
    from manuscript.validation import find_hardcoded_refs

    assert "Section 7" in find_hardcoded_refs("see Section 7 for details")
    assert "section 1" in find_hardcoded_refs("the determinism contract in section 1")


def test_find_hardcoded_refs_flags_figure_equation_table_appendix_in_prose() -> None:
    """Body prose must route figure/equation/table/appendix references
    through registry tokens; bare display references are flagged.
    """
    from manuscript.validation import find_hardcoded_refs

    assert any("Figure 3" in s for s in find_hardcoded_refs("as shown in Figure 3 above"))
    assert any("Fig. 3" in s for s in find_hardcoded_refs("see Fig. 3"))
    assert any("Equation 4" in s for s in find_hardcoded_refs("see Equation 4"))
    assert any("Eq. (4" in s for s in find_hardcoded_refs("see Eq. (4)"))
    assert any("Table 2" in s for s in find_hardcoded_refs("see Table 2"))
    assert any("Appendix B" in s for s in find_hardcoded_refs("see Appendix B"))


def test_find_hardcoded_refs_allows_unnumbered_section_prose() -> None:
    """The bare word "section" without a number is ordinary prose, not a
    cross-reference, and must not be flagged (no false positives).
    """
    from manuscript.validation import find_hardcoded_refs

    for ok in ("in this section we", "a cross-section of", "the subsection below"):
        assert find_hardcoded_refs(ok) == [], ok


def test_validate_manuscript_tree_no_hardcoded_refs() -> None:
    """Real manuscript: zero hardcoded refs after the migration."""
    from manuscript.validation import validate_manuscript_tree

    reg = load_registry(REFS)
    report = validate_manuscript_tree(
        manuscript_dir=MANUSCRIPT,
        registry=reg,
        variables={},
    )
    assert not report.hardcoded_refs, report.hardcoded_refs


def test_validation_report_is_clean_with_hardcoded_refs() -> None:
    from manuscript.validation import ManuscriptValidationReport

    r = ManuscriptValidationReport(section_files=[])
    r.hardcoded_refs["x.md"] = ["§99"]
    assert not r.is_clean


def test_validation_report_is_not_clean_with_tokens_in_code_fences() -> None:
    from manuscript.validation import ManuscriptValidationReport

    r = ManuscriptValidationReport(section_files=[])
    r.tokens_in_code_fences["x.md"] = ["[[EQ:e]]"]
    assert not r.is_clean
