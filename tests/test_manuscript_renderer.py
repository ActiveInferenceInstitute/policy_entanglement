"""Coverage tests for `manuscript.renderer`, `manuscript.bibliography`,
and the `iter_tokens` edge cases.

Split off from the original `test_manuscript_coverage.py` per the
project's modularity styleguide — one focused test module per
manuscript-pipeline subsystem.
"""

from __future__ import annotations

from pathlib import Path

from manuscript.bibliography import _sorted_keys, auto_bibliography
from manuscript.registry import (
    Citation,
    CitationRegistry,
    Equation,
    Figure,
    LabelsRegistry,
    Registry,
    Section,
    load_citations,
)
from manuscript.renderer import _format_var, render_section
from manuscript.tokens import iter_tokens

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
        short="x",
        sections=("§1",),
        source="scripts/x.py",
        number=1,
    )
    eq = Equation(
        label="e",
        latex="x = y",
        name="Sample equation",
        sections=("§1",),
        number=1,
    )
    cite = Citation(
        key="x-2024",
        authors="X, Y.",
        year=2024,
        title="Title",
        venue="Venue",
        topic="topicA",
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
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    # Renders as a clickable LaTeX hyperref (raw_tex via Pandoc).
    assert "\\hyperref[fig:x]" in out.text
    assert "Fig.~1" in out.text


def test_render_section_resolves_eq_block() -> None:
    reg = _tiny_registry()
    out = render_section(
        "Eqn: [[EQ:e]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    # Registered equation emitted as Pandoc display-math with crossref attr.
    assert "$$" in out.text
    assert "{#eq:e}" in out.text
    assert "x = y" in out.text


def test_render_section_resolves_eqref() -> None:
    reg = _tiny_registry()
    out = render_section(
        "see [[EQREF:e]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "\\hyperref[eq:e]" in out.text
    assert "Eq.~(1)" in out.text


def test_render_section_advances_subsection_cursor_for_existing_anchor() -> None:
    reg = Registry(
        labels=LabelsRegistry(
            figures={},
            equations={},
            sections={
                "top": Section(label="top", number="1", title="Top", parent="", file="x.md"),
                "top.a": Section(label="top.a", number="1.1", title="A", file="", parent="top"),
                "top.b": Section(label="top.b", number="1.2", title="B", file="", parent="top"),
            },
        ),
        citations=CitationRegistry(entries={}, topic_order=(), topic_titles={}),
    )
    out = render_section(
        "# Top\n\n## A {#sec:top.a}\n\n## B\n",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
        file_name="x.md",
    )
    assert "## A {#sec:top.a}" in out.text
    assert "## B {#sec:top.b}" in out.text
    assert out.text.count("#sec:top.a") == 1


def test_render_section_resolves_citelist() -> None:
    reg = _tiny_registry()
    out = render_section(
        "[[CITELIST:topicA]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "Topic A" in out.text
    assert "X, Y." in out.text


def test_render_section_emits_citep_for_known_key() -> None:
    reg = _tiny_registry()
    out = render_section(
        "see [@x-2024] for details.",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "\\citep{x-2024}" in out.text
    assert not out.missing_citations


def test_render_section_records_missing_citation() -> None:
    reg = _tiny_registry()
    out = render_section(
        "[@nope-2099]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "MISSING:CITE:nope-2099" in out.text
    assert out.missing_citations == ["nope-2099"]


def test_render_section_marks_missing_eq_and_eqref() -> None:
    reg = _tiny_registry()
    out = render_section(
        "[[EQ:nope]] [[EQREF:nope]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
    )
    assert "MISSING:EQ:nope" in out.text
    assert "MISSING:EQREF:nope" in out.text
    assert sorted(set(out.missing_equations)) == ["nope"]


def test_render_section_marks_missing_figref() -> None:
    reg = _tiny_registry()
    out = render_section(
        "[[FIGREF:nope]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
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
                key="extra-2099",
                authors="Z, W.",
                year=2099,
                title="t",
                venue="v",
                topic="orphan",
            ),
            "x-2024": Citation(
                key="x-2024",
                authors="X, Y.",
                year=2024,
                title="t",
                venue="v",
                topic="known",
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
            "b-2024": Citation(key="b-2024", authors="B", year=2024, title="t", venue="v", topic="t"),
            "a-2024": Citation(key="a-2024", authors="A", year=2024, title="t", venue="v", topic="t"),
        },
        topic_order=("t",),
        topic_titles={"t": "T"},
    )
    assert _sorted_keys(reg, "t") == ["a-2024", "b-2024"]


def test_auto_bibliography_skips_empty_topic_in_topic_order() -> None:
    """When `topic_order` lists a topic with no matching entries, the
    auto-bib should silently skip it (covers the `if not keys: continue`
    branch).
    """
    reg = CitationRegistry(
        entries={
            "x-2024": Citation(
                key="x-2024",
                authors="X",
                year=2024,
                title="t",
                venue="v",
                topic="real",
            ),
        },
        topic_order=("empty_topic", "real"),
        topic_titles={"empty_topic": "Empty", "real": "Real"},
    )
    body = auto_bibliography(reg, topic="all")
    assert "Empty" not in body  # skipped
    assert "Real" in body


# ---------------------------------------------------------------------------
# iter_tokens edge cases + result objects
# ---------------------------------------------------------------------------


def test_iter_tokens_empty_text() -> None:
    assert list(iter_tokens("")) == []


def test_iter_tokens_no_tokens() -> None:
    assert list(iter_tokens("just prose")) == []


def test_render_result_is_complete_property() -> None:
    from manuscript.renderer import RenderResult

    assert RenderResult(text="").is_complete
    r = RenderResult(text="", missing_figures=["x"])
    assert not r.is_complete


# ---------------------------------------------------------------------------
# render_all without a variables JSON
# ---------------------------------------------------------------------------


def test_render_all_works_with_missing_variables_path(tmp_path: Path) -> None:
    """`render_all` should still write the rendered sections even when
    `variables_path` does not exist (no `[[VAR:...]]` tokens are
    resolvable, but pure text + figure / citation tokens still work).
    """
    from manuscript.registry import load_registry
    from manuscript.renderer import render_all

    reg = load_registry(REFS)
    out = tmp_path / "rendered"
    src = tmp_path / "manuscript_src"
    src.mkdir()
    (src / "00_only.md").write_text("# Hello\n\nThis section has no VAR tokens but cites [@heins-2022].\n")
    results = render_all(
        manuscript_dir=src,
        output_dir=out,
        registry=reg,
        variables_path=tmp_path / "missing.json",
    )
    assert "00_only.md" in results
    assert results["00_only.md"].is_complete
