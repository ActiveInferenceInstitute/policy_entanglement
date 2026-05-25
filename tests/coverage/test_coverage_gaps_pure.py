"""Targeted no-mock tests for residual pure-Python coverage gaps.

Every test exercises a specific source line/branch that the main suites
miss, using only real data, real temp files, and real computations
(no MagicMock / unittest.mock / mocker.patch / monkeypatch).

Scope is deliberately limited to *pure-Python* gaps that are reachable
without pymdp, a live Lean toolchain, or external CLIs -- the
pymdp/Lean/CLI surface is the documented CLAUDE.md rotating-project
exception and is intentionally CI-only.

Source lines targeted (from --cov-report=term-missing):

* manuscript/bibliography.py   38, 100-101
* manuscript/validation.py     107-108, 137-138, 142, 536, 608, 643, 654
* manuscript/_resolvers.py     61, 64, 332-333
* manuscript/renderer.py       316, 341, 446, 450, 497
* manuscript/pdf_validation.py 213-214, 259-260
* lean/invariants.py           369
* lean/bernoulli_toy.py        158-159
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np

from lean.bernoulli_toy import ising_free_energy_curve, ising_mutual_information
from lean.invariants import SweepGrid, coupling_pays_invariants
from manuscript._resolvers import _caption_with_uncertainty
from manuscript.bibliography import _infer_entry_type, auto_bibliography
from manuscript.pdf_validation import parse_geometry_margins, validate_preamble_margins
from manuscript.registry import (
    Citation,
    CitationRegistry,
    Figure,
    LabelsRegistry,
    Registry,
    Section,
    TheoremEntry,
    load_registry,
)
from manuscript.renderer import render_section
from manuscript.validation import (
    collect_section_subheadings,
    collect_top_level_sections,
    validate_manuscript_tree,
)

MANUSCRIPT = Path(__file__).resolve().parent.parent.parent / "manuscript"


# ---------------------------------------------------------------------------
# lean/bernoulli_toy.py  -- line 158-159: lam < 0 stable-logistic branch
# ---------------------------------------------------------------------------


def test_ising_free_energy_curve_negative_lambda_branch() -> None:
    """A negative lambda takes the e/(1+e) numerically-stable branch.

    For lambda < 0 alignment is negative, so with positive utility the
    free energy strictly increases relative to the lambda = 0 baseline.
    """
    f_neg = ising_free_energy_curve(-1.5, utility=2.0)
    f_zero = ising_free_energy_curve(0.0, utility=2.0)
    assert f_zero == 0.0
    assert f_neg > 0.0
    expected = -2.0 * np.tanh(-1.5 / 2.0) - ising_mutual_information(-1.5)
    assert abs(f_neg - expected) < 1e-12


def test_ising_free_energy_curve_negative_equals_positive_mirror() -> None:
    """tanh is odd and MI is even, so F(-l) + F(+l) = -2*I(l)."""
    lam = 2.3
    f_pos = ising_free_energy_curve(lam, utility=1.0)
    f_neg = ising_free_energy_curve(-lam, utility=1.0)
    assert abs((f_pos + f_neg) - (-2.0 * ising_mutual_information(lam))) < 1e-12


# ---------------------------------------------------------------------------
# lean/invariants.py  -- line 369: ``if not pays: return []``
# ---------------------------------------------------------------------------


def test_coupling_pays_invariants_empty_when_grid_below_threshold() -> None:
    """Every grid point <= lam_threshold skips the body, so the
    accumulator stays empty and the early ``return []`` fires."""
    grid = SweepGrid(-1.0, 0.05, 5)
    assert all(v <= 0.1 for v in grid.values())
    assert coupling_pays_invariants(grid) == []


def test_coupling_pays_invariants_nonempty_above_threshold() -> None:
    """Sanity counterpart: a grid above the threshold yields invariants."""
    grid = SweepGrid(0.5, 6.0, 8)
    invs = coupling_pays_invariants(grid, lam_threshold=0.1)
    assert invs


# ---------------------------------------------------------------------------
# manuscript/_resolvers.py  -- _caption_with_uncertainty lines 61 & 64
# ---------------------------------------------------------------------------


def _fig(caption: str, uncertainty: str = "") -> Figure:
    return Figure(
        label="f",
        path="output/figures/x.png",
        caption=caption,
        short="f",
        sections=("§1",),
        source="scripts/x.py",
        number=1,
        uncertainty=uncertainty,
    )


def test_caption_with_uncertainty_already_present_short_circuits() -> None:
    """Line 61: caption already states uncertainty semantics -> returned
    verbatim (no second appendage)."""
    cap = "A plot.  Uncertainty semantics: deterministic grid."
    out = _caption_with_uncertainty(_fig(cap, uncertainty="deterministic_grid"))
    assert out == cap.strip()
    assert out.lower().count("uncertainty semantics:") == 1


def test_caption_with_uncertainty_blank_uncertainty_returns_caption() -> None:
    """Line 64: empty ``uncertainty`` field -> caption returned unchanged."""
    out = _caption_with_uncertainty(_fig("Just a caption.", uncertainty=""))
    assert out == "Just a caption."
    assert "uncertainty semantics" not in out.lower()


def test_caption_with_uncertainty_unknown_key_humanizes_underscores() -> None:
    """Fallback path: an unmapped uncertainty key is rendered with
    underscores turned into spaces."""
    out = _caption_with_uncertainty(_fig("Cap.", uncertainty="custom_mode_x"))
    assert "Uncertainty semantics: custom mode x." in out


# ---------------------------------------------------------------------------
# manuscript/_resolvers.py  -- _resolve_lean lines 332-333 (snippet absent)
# via the public render_section orchestrator.
# ---------------------------------------------------------------------------


def test_resolve_lean_snippet_absent_from_cache_marks_missing() -> None:
    """A theorem with a Lean companion whose (module, name) is NOT in the
    supplied snippet cache -> [[MISSING:LEAN:...]] + recorded miss."""
    theorem = TheoremEntry(
        label="t1",
        kind="Theorem",
        number="1.1",
        name="Test",
        section="s1",
        lean_module="Decomposition",
        lean_name="entanglement_decomposition",
        status="proved",
    )
    registry = Registry(
        labels=LabelsRegistry(figures={}, equations={}, theorems={"t1": theorem}),
        citations=CitationRegistry(entries={}, topic_order=(), topic_titles={}),
    )
    out = render_section(
        "Companion: [[LEAN:t1]]",
        registry=registry,
        variables={},
        manuscript_dir=MANUSCRIPT,
        lean_snippets={},
    )
    assert "[[MISSING:LEAN:t1 (Decomposition.entanglement_decomposition not found in source)]]" in out.text
    assert out.missing_lean == ["t1"]


# ---------------------------------------------------------------------------
# manuscript/bibliography.py  -- line 38 (leftover topic, empty keys) and
# lines 100-101 (venue starts with http -> misc/howpublished).
# ---------------------------------------------------------------------------


def test_auto_bibliography_leftover_topic_with_no_entries_skipped() -> None:
    """Line 38: a topic that exists only in ``topic_titles`` (not on any
    entry and not in ``topic_order``) contributes zero keys and is
    ``continue``-skipped while building the 'all' bibliography."""
    entries = {
        "a2020": Citation(
            key="a2020",
            authors="Alpha, A.",
            year=2020,
            title="Title A",
            venue="Journal A",
            volume="1",
            pages="1--10",
            topic="present_topic",
        ),
    }
    reg = CitationRegistry(
        entries=entries,
        topic_order=(),
        topic_titles={"present_topic": "Present", "ghost_topic": "Ghost"},
    )
    md = auto_bibliography(reg, "all")
    assert "## Present" in md
    assert "Ghost" not in md


def test_infer_entry_type_http_venue_becomes_misc_howpublished() -> None:
    """Lines 100-101: a venue beginning with ``http`` is treated as a
    ``misc`` entry whose ``howpublished`` field holds the URL-venue."""
    c = Citation(
        key="web2023",
        authors="Web, W.",
        year=2023,
        title="An online note",
        venue="https://example.org/post",
    )
    entry_type, fields = _infer_entry_type(c)
    assert entry_type == "misc"
    assert fields["howpublished"] == "https://example.org/post"
    assert fields["title"] == "An online note"


# ---------------------------------------------------------------------------
# manuscript/pdf_validation.py
#   lines 213-214: geometry margin value ends in 'in' but is not a float
#   lines 259-260: validate_preamble_margins missing-file issue
# ---------------------------------------------------------------------------


def test_parse_geometry_margins_non_float_value_is_skipped() -> None:
    """A geometry option that ends in ``in`` but whose numeric prefix is
    not parseable hits the ``except ValueError: continue`` (213-214)."""
    preamble = r"\usepackage[top=0.9in,left=notanumberin,right=0.9in,bottom=xyzin]{geometry}"
    margins = parse_geometry_margins(preamble)
    assert margins == {"top": 0.9, "right": 0.9}


def test_parse_geometry_margins_non_in_unit_is_skipped() -> None:
    """A non-``in`` unit takes the earlier ``continue`` (not the
    ValueError path) -- keeps the two branches independently exercised."""
    margins = parse_geometry_margins(r"\usepackage[top=2cm,left=0.9in]{geometry}")
    assert margins == {"left": 0.9}


def test_validate_preamble_margins_missing_file_reports_issue() -> None:
    """Missing preamble path -> a single 'preamble missing' issue."""
    issues = validate_preamble_margins(Path("/no/such/preamble.md"))
    assert len(issues) == 1
    assert "preamble missing" in issues[0].message


# ---------------------------------------------------------------------------
# manuscript/validation.py
#   107-108 / 137-138 : YAML refs file unreadable -> except returns early
#   142               : collect_top_level_sections section loop body
#   536               : theorem WITHOUT lean companion is `continue`d
#   608               : strict heading hardcoded-source-literal recorded
#   643               : registry token inside a code fence recorded
#   654               : strict registry source-field hits merged
# ---------------------------------------------------------------------------


def test_collect_section_subheadings_unreadable_refs_returns_empty(tmp_path: Path) -> None:
    """Lines 107-108: ``refs/labels.yaml`` exists but is a directory, so
    ``read_text`` raises OSError -> ``except (OSError, ImportError)``."""
    ms = tmp_path / "manuscript"
    (ms / "refs").mkdir(parents=True)
    (ms / "refs" / "labels.yaml").mkdir()
    assert collect_section_subheadings(ms) == {}


def test_collect_top_level_sections_unreadable_refs_returns_empty(tmp_path: Path) -> None:
    """Lines 137-138: same OSError path for the top-level collector."""
    ms = tmp_path / "manuscript"
    (ms / "refs").mkdir(parents=True)
    (ms / "refs" / "labels.yaml").mkdir()
    assert collect_top_level_sections(ms) == set()


def test_collect_top_level_sections_parses_section_numbers(tmp_path: Path) -> None:
    """Line 142+: the section loop body runs and returns the top-level
    numbers (entries with a parent are excluded)."""
    ms = tmp_path / "manuscript"
    (ms / "refs").mkdir(parents=True)
    (ms / "refs" / "labels.yaml").write_text(
        "sections:\n"
        "  s1:\n    number: '1'\n    title: Intro\n    file: 01_intro.md\n"
        "  s2:\n    number: '2'\n    title: Methods\n    file: 02_methods.md\n"
        "  s2a:\n    number: '2.1'\n    title: Sub\n    parent: s2\n"
        "  bad:\n    number: 'not-a-number'\n    title: Bad\n",
        encoding="utf-8",
    )
    assert collect_top_level_sections(ms) == {1, 2}


def test_collect_section_subheadings_parses_subsections(tmp_path: Path) -> None:
    """Counterpart that exercises the subsection regex match branch."""
    ms = tmp_path / "manuscript"
    (ms / "refs").mkdir(parents=True)
    (ms / "refs" / "labels.yaml").write_text(
        "sections:\n"
        "  s2a:\n    number: '2.1'\n    title: Sub one\n"
        "  s2b:\n    number: '2.3'\n    title: Sub three\n"
        "  top:\n    number: '2'\n    title: Top\n",
        encoding="utf-8",
    )
    assert collect_section_subheadings(ms) == {2: {1, 3}}


def _refs(ms_dir: Path, labels_yaml: str) -> Registry:
    refs = ms_dir / "refs"
    refs.mkdir(parents=True, exist_ok=True)
    (refs / "labels.yaml").write_text(labels_yaml, encoding="utf-8")
    (refs / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n", encoding="utf-8")
    return load_registry(refs)


def test_validate_manuscript_tree_theorem_without_companion_is_skipped(tmp_path: Path) -> None:
    """Line 536: a real ``lean_dir`` is supplied and a theorem WITHOUT a
    Lean companion is skipped by ``if not theorem.has_lean_companion``."""
    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "01_section.md").write_text("# Section\n\nClean body prose.\n", encoding="utf-8")
    lean_dir = tmp_path / "lean"
    lean_dir.mkdir()
    (lean_dir / "Mod.lean").write_text("theorem foo : True := trivial\n", encoding="utf-8")
    registry = _refs(
        ms,
        "sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n"
        "theorems:\n  t1:\n    kind: Theorem\n    number: '1.1'\n    name: NoCompanion\n    section: s1\n",
    )
    assert registry.labels.theorems["t1"].has_lean_companion is False
    report = validate_manuscript_tree(
        manuscript_dir=ms,
        registry=registry,
        variables={},
        lean_dir=lean_dir,
    )
    assert report.broken_lean_wiring == {}


def test_validate_manuscript_tree_hardcoded_heading_literal_recorded(tmp_path: Path) -> None:
    """Line 608: a section heading that hand-writes ``Theorem 5.1`` is
    flagged into ``hardcoded_rendered_source_fields``."""
    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "01_section.md").write_text("# Section\n\n## Proof of Theorem 5.1\n\nBody.\n", encoding="utf-8")
    registry = _refs(ms, "sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    report = validate_manuscript_tree(manuscript_dir=ms, registry=registry, variables={})
    assert "01_section.md" in report.hardcoded_rendered_source_fields
    assert any("Theorem 5.1" in h for h in report.hardcoded_rendered_source_fields["01_section.md"])


def test_validate_manuscript_tree_token_in_code_fence_recorded(tmp_path: Path) -> None:
    """Line 643: a forbidden cross-reference token inside a fenced code
    block is captured into ``tokens_in_code_fences``."""
    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "01_section.md").write_text(
        "# Section\n\n```\nsome code with [[EQ:euler]] inside\n```\n",
        encoding="utf-8",
    )
    registry = _refs(ms, "sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    report = validate_manuscript_tree(manuscript_dir=ms, registry=registry, variables={})
    assert "01_section.md" in report.tokens_in_code_fences
    assert "[[EQ:euler]]" in report.tokens_in_code_fences["01_section.md"]


def test_validate_manuscript_tree_strict_registry_source_field_recorded(tmp_path: Path) -> None:
    """Line 654: a registry figure caption that hand-writes a display
    label is merged into ``hardcoded_rendered_source_fields``."""
    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "01_section.md").write_text("# Section\n\nClean prose.\n", encoding="utf-8")
    fig = Figure(
        label="bad",
        path="output/figures/x.png",
        caption="See Figure 3 for the layout.",
        short="bad",
        sections=("§1",),
        source="scripts/x.py",
        number=1,
    )
    registry = Registry(
        labels=LabelsRegistry(
            figures={"bad": fig},
            equations={},
            sections={"s1": Section(label="s1", number="1", title="S", file="01_section.md", parent="")},
        ),
        citations=CitationRegistry(entries={}, topic_order=(), topic_titles={}),
    )
    report = validate_manuscript_tree(manuscript_dir=ms, registry=registry, variables={})
    key = "labels.yaml::figures.bad.caption"
    assert key in report.hardcoded_rendered_source_fields
    assert any("Figure 3" in h for h in report.hardcoded_rendered_source_fields[key])


# ---------------------------------------------------------------------------
# manuscript/renderer.py
#   316  : existing ## anchor whose sec: id is in sub_labels advances cursor
#   341  : existing extra heading attributes preserved alongside #sec:
#   446 / 450 / 497 : _section_to_file parent-chain + theorem-anchor inject
# ---------------------------------------------------------------------------


def test_render_section_existing_anchor_advances_cursor_line316() -> None:
    """Line 316: the first ``##`` already carries ``{#sec:top.b}`` whose
    label is found in ``sub_labels[sub_idx:]`` so the cursor jumps past
    it; the next bare ``##`` then maps to the following subsection."""
    reg = Registry(
        labels=LabelsRegistry(
            figures={},
            equations={},
            sections={
                "top": Section(label="top", number="1", title="Top", parent="", file="x.md"),
                "top.a": Section(label="top.a", number="1.1", title="A", file="", parent="top"),
                "top.b": Section(label="top.b", number="1.2", title="B", file="", parent="top"),
                "top.c": Section(label="top.c", number="1.3", title="C", file="", parent="top"),
            },
        ),
        citations=CitationRegistry(entries={}, topic_order=(), topic_titles={}),
    )
    out = render_section(
        "# Top\n\n## B {#sec:top.b}\n\n## Next\n",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
        file_name="x.md",
    )
    assert "## B {#sec:top.b}" in out.text
    assert "## Next {#sec:top.c}" in out.text


def test_render_section_preserves_extra_heading_attrs_line341() -> None:
    """Line 341: a bare ``##`` heading that already carries a non-id
    attribute block has that block preserved after the injected
    ``#sec:`` anchor."""
    reg = Registry(
        labels=LabelsRegistry(
            figures={},
            equations={},
            sections={
                "top": Section(label="top", number="1", title="Top", parent="", file="x.md"),
                "top.a": Section(label="top.a", number="1.1", title="A", file="", parent="top"),
            },
        ),
        citations=CitationRegistry(entries={}, topic_order=(), topic_titles={}),
    )
    out = render_section(
        "# Top\n\n## A {.callout}\n",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
        file_name="x.md",
    )
    assert "## A {#sec:top.a .callout}" in out.text


def test_render_all_parent_chain_and_theorem_anchor_injection(tmp_path: Path) -> None:
    """Drives ``render_all`` so the parent-chain resolution in
    ``_section_to_file`` (446/450) and the no-statement theorem-anchor
    injection (``_ensure_theorem_anchors`` 493/497) both execute.

    A corollary referenced only inline (no ``**[[THMREF]]**`` statement)
    lives in a *subsection* whose file is resolved transitively through
    its parent -- exercising the ``parent.file`` walk-up and the anchor
    injection after the level-1 heading.
    """
    from manuscript.renderer import render_all

    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "01_intro.md").write_text("# Introduction\n\nWe rely on [[THMREF:cor_x]] later.\n", encoding="utf-8")
    refs = ms / "refs"
    refs.mkdir()
    refs_yaml = (
        "sections:\n"
        "  intro:\n    number: '1'\n    title: Introduction\n    file: 01_intro.md\n"
        "  intro.sub:\n    number: '1.1'\n    title: Sub\n    parent: intro\n"
        "theorems:\n"
        "  cor_x:\n    kind: Corollary\n    number: '1.2'\n    name: Inline only\n    section: intro.sub\n"
    )
    (refs / "labels.yaml").write_text(refs_yaml, encoding="utf-8")
    (refs / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n", encoding="utf-8")
    registry = load_registry(refs)

    out_dir = tmp_path / "out"
    (tmp_path / "vars.json").write_text("{}", encoding="utf-8")
    results = render_all(
        manuscript_dir=ms,
        output_dir=out_dir,
        registry=registry,
        variables_path=tmp_path / "vars.json",
    )
    rendered = (out_dir / "01_intro.md").read_text(encoding="utf-8")
    assert "\\label{thm:cor_x}" in rendered
    assert "01_intro.md" in results
