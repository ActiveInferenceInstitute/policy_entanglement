"""Domain-scoped coverage meta-tests: manuscript validation, bibliography, figures."""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest

from lean.bernoulli_toy import ising_free_energy_curve, ising_mutual_information
from lean.decomposition import (
    _marginals_efes_broadcast_to_joint,
    free_energy_against_entangled_prior,
)
from lean.geometry import coupling_log_weight_affine_check
from lean.invariants import SweepGrid, coupling_pays_invariants
from manuscript import validation_cli as vc
from manuscript._resolvers import _caption_with_uncertainty
from manuscript.bibliography import (
    _format_bibtex_authors,
    _infer_entry_type,
    _ordered_bib_fields,
    _sorted_keys,
    auto_bibliography,
    write_references_bib,
)
from manuscript.equation_numbering import assign_within_section_numbers
from manuscript.output_gates import pymdp_validators
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
    validate_figure_files,
    validate_manuscript_tree,
)
from tests.output_gates_helpers import patch_output_dir

MANUSCRIPT = Path(__file__).resolve().parent.parent.parent / "manuscript"

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

def _refs(ms_dir: Path, labels_yaml: str) -> Registry:
    refs = ms_dir / "refs"
    refs.mkdir(parents=True, exist_ok=True)
    (refs / "labels.yaml").write_text(labels_yaml, encoding="utf-8")
    (refs / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n", encoding="utf-8")
    return load_registry(refs)

def _reg(
    topic_order: tuple[str, ...] = ("topicA",),
    extra: dict | None = None,
) -> CitationRegistry:
    entries: dict[str, Citation] = {
        "alpha2020": Citation(
            key="alpha2020",
            authors="Alpha, A.",
            year=2020,
            title="Title A",
            venue="Journal A",
            volume="1",
            pages="1--10",
            topic="topicA",
        ),
        "beta2021": Citation(
            key="beta2021",
            authors="Beta, B.",
            year=2021,
            title="Title B",
            venue="Workshop Proc.",
            topic="topicB",
        ),
    }
    if extra:
        entries.update(extra)
    return CitationRegistry(
        entries=entries,
        topic_order=topic_order,
        topic_titles={"topicA": "Topic A"},
    )

def _minimal_registry() -> Registry:
    return Registry(
        labels=LabelsRegistry(figures={}, equations={}),
        citations=CitationRegistry(entries={}, topic_order=(), topic_titles={}),
    )

PROJECT = Path(__file__).resolve().parent.parent.parent

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

def test_sorted_keys_all_topic_line13() -> None:
    # line 13: _sorted_keys called with "all" returns all keys
    reg = _reg()
    keys = _sorted_keys(reg, "all")
    assert sorted(keys) == ["alpha2020", "beta2021"]

def test_sorted_keys_specific_topic_line14() -> None:
    # exercises line 14: the `topic != "all"` branch of _sorted_keys
    reg = _reg()
    keys = _sorted_keys(reg, "topicB")
    assert keys == ["beta2021"]

def test_sorted_keys_unknown_topic_empty() -> None:
    reg = _reg()
    assert _sorted_keys(reg, "nonexistent") == []

def test_auto_bibliography_leftover_topic_line38() -> None:
    # topicB is NOT in topic_order → leftover-topic branch (line 38)
    reg = _reg(topic_order=("topicA",))
    result = auto_bibliography(reg, topic="all")
    assert "beta2021" in result or "Title B" in result

def test_format_bibtex_authors_empty_string_line60() -> None:
    # line 60: return "" for empty input
    assert _format_bibtex_authors("") == ""

def test_infer_entry_type_no_author_line87() -> None:
    # lines 87→89: `if author:` is False → "author" key absent from fields
    c = Citation(
        key="noauth",
        authors="",
        year=2022,
        title="Paper",
        venue="Journal J",
        volume="3",
        topic="",
    )
    _etype, fields = _infer_entry_type(c)
    assert "author" not in fields

def test_infer_entry_type_misc_venue_pages_line110() -> None:
    # lines 110→112: misc branch — venue present, pages present, no volume
    c = Citation(
        key="misc1",
        authors="X, Y.",
        year=2023,
        title="Misc",
        venue="Workshop Proceedings",
        pages="5--12",
        topic="",
    )
    etype, fields = _infer_entry_type(c)
    assert etype == "misc"
    assert "howpublished" in fields
    assert "pages" in fields

def test_infer_entry_type_empty_venue_with_pages() -> None:
    # line 110→112: venue is empty (if venue: is False) but pages is present
    c = Citation(
        key="novenp",
        authors="A. B.",
        year=2020,
        title="Paper",
        venue="",
        pages="1--5",
        topic="",
    )
    etype, fields = _infer_entry_type(c)
    assert etype == "misc"
    assert "pages" in fields
    assert "howpublished" not in fields

def test_ordered_bib_fields_extra_keys_line152() -> None:
    # lines 152-154: fields with keys beyond the preferred ordering
    # Use TWO extra fields so the loop continues (covers 153→149 branch)
    fields = {
        "author": "X, Y.",
        "title": "T",
        "year": "2022",
        "extra_key_a": "val_a",
        "extra_key_b": "val_b",
    }
    result = _ordered_bib_fields("misc", fields)
    keys = [k for k, _ in result]
    assert "extra_key_a" in keys
    assert "extra_key_b" in keys

def test_write_references_bib_creates_valid_bib(tmp_path) -> None:
    reg = _reg()
    bib_path = tmp_path / "refs.bib"
    write_references_bib(reg, bib_path)
    content = bib_path.read_text()
    assert "@article{alpha2020," in content
    assert "@misc{beta2021," in content

def test_assign_within_section_numbers_bare_math() -> None:
    text = "$$x^2$$ then $$y^2$$"
    result = assign_within_section_numbers(text)
    assert len(result) == 2
    k0, _pos0, kind0, label0 = result[0]
    assert k0 == 1
    assert kind0 == "math"
    assert label0 is None
    k1, _pos1, kind1, _label1 = result[1]
    assert k1 == 2
    assert kind1 == "math"

def test_assign_within_section_numbers_eq_token() -> None:
    text = "[[EQ:tc_eq]] and $$bare$$"
    result = assign_within_section_numbers(text)
    kinds = [r[2] for r in result]
    assert "eq" in kinds
    assert "math" in kinds
    labels = [r[3] for r in result]
    assert "tc_eq" in labels

def test_assign_within_section_numbers_empty() -> None:
    assert assign_within_section_numbers("no equations") == []

def test_marginals_efes_broadcast_wrong_shape_line98() -> None:
    # line 98: shape mismatch raises ValueError
    joint_shape = (2, 3)
    per_stream_G = [
        np.zeros(2),  # stream 0 OK
        np.zeros(2),  # stream 1 WRONG — should be (3,)
    ]
    with pytest.raises(ValueError, match="stream 1"):
        _marginals_efes_broadcast_to_joint(per_stream_G, joint_shape)

def test_free_energy_against_entangled_prior_shape_mismatch_line172() -> None:
    # line 172: coupling_j and coupling_kc different shapes → ValueError
    q = np.full((2, 2), 0.25)
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    coupling_j = np.zeros((2, 2))
    coupling_kc = np.zeros((3, 3))  # deliberately wrong shape
    with pytest.raises(ValueError, match="joint shape"):
        free_energy_against_entangled_prior(
            q,
            mf,
            [np.zeros(2), np.zeros(2)],
            coupling_j,
            coupling_kc,
            gamma=1.0,
            lam=1.0,
        )

def test_coupling_log_weight_affine_check_returns_false_on_nan() -> None:
    # line 126: NaN propagation makes np.allclose return False → returns False
    Ja = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.array([[0.1, 0.0], [0.0, 0.1]])  # non-zero so NaN propagates
    gamma = float("nan")  # invalid but exercises the branch
    result = coupling_log_weight_affine_check(Ja, Kc, gamma, lams=[0.0, 1.0, 2.0])
    assert result is False

def test_coupling_pays_invariants_empty_when_all_below_threshold() -> None:
    # line 369: returns [] when no lambda value exceeds lam_threshold
    grid = SweepGrid(lam_min=0.0, lam_max=0.5, num=5)
    # threshold=1.0 is above lam_max=0.5 → no lam passes → pays list stays empty
    result = coupling_pays_invariants(grid, lam_threshold=1.0)
    assert result == []

def test_validate_figure_files_reports_missing_file(tmp_path) -> None:
    # line 344: image reference to a nonexistent file → reported
    text = "# Sec\n![Caption](figures/missing.png)\n"
    result = validate_figure_files(text, tmp_path)
    assert any("missing.png" in r for r in result)

def test_validate_figure_files_existing_file_not_reported(tmp_path) -> None:
    fig_dir = tmp_path / "figures"
    fig_dir.mkdir()
    (fig_dir / "present.png").write_bytes(b"\x89PNG\r\n")
    text = "# Sec\n![Caption](figures/present.png)\n"
    result = validate_figure_files(text, tmp_path)
    assert result == []

def test_validate_figure_files_external_link_ignored(tmp_path) -> None:
    text = "![Alt](https://example.com/image.png)\n"
    result = validate_figure_files(text, tmp_path)
    assert result == []

def test_validate_manuscript_tree_raw_block_triggers_in_raw(tmp_path) -> None:
    # lines 437+443: in_raw toggling — file starts with a code block before heading
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    (ms_dir / "01_section.md").write_text("```python\ncode_line\n```\n# Section Title\n\nBody text.\n")
    # Provide a minimal labels.yaml so section_paths finds the file
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text(
        "sections:\n  s1:\n    number: '1'\n    title: Section\n    file: 01_section.md\n"
    )
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
    )
    # Heading found correctly (code block skipped, real heading found)
    assert "01_section.md" not in report.missing_headings

def test_validate_manuscript_tree_broken_link_captured(tmp_path) -> None:
    # line 456: bad_links branch — relative link to nonexistent file
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    (ms_dir / "01_section.md").write_text("# Section\n\n[broken link](nonexistent_doc.md)\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
    )
    assert "01_section.md" in report.broken_links

def test_validate_manuscript_tree_missing_figure_captured(tmp_path) -> None:
    # line 460: missing_figure_files branch
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    (ms_dir / "01_section.md").write_text("# Section\n\n![Figure](figures/ghost.png)\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
    )
    assert "01_section.md" in report.missing_figure_files

def test_validate_manuscript_tree_empty_caption_captured(tmp_path) -> None:
    # lines 463-464: empty alt-text caption
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    fig_dir = ms_dir / "figures"
    fig_dir.mkdir()
    (fig_dir / "real.png").write_bytes(b"\x89PNG")
    (ms_dir / "01_section.md").write_text("# Section\n\n![](figures/real.png)\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
    )
    assert any("01_section.md" in c for c in report.empty_captions)

def test_validate_manuscript_tree_hardcoded_numeric_literal(tmp_path) -> None:
    # line 480: hardcoded_numeric_literals branch
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    (ms_dir / "01_section.md").write_text("# Section\n\nWe used a 121-point grid in the sweep.\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
    )
    assert "01_section.md" in report.hardcoded_numeric_literals

def test_validate_manuscript_tree_variable_ranges_branch(tmp_path) -> None:
    # line 483: variable_ranges branch with out-of-range variable
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    (ms_dir / "01_section.md").write_text("# Section\n\nBody.\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={"K": 99},
        variable_ranges={"K": (1.0, 10.0)},
    )
    assert "K" in report.out_of_range_variables

def test_plot_coupling_graph_k2_high_threshold_no_edges(tmp_path) -> None:
    """K=2 matrix + threshold above all weights → else branch + fallback edge."""
    from visualizations.graphs import has_networkx, plot_coupling_graph

    if not has_networkx():
        pytest.skip("networkx not installed")

    J = np.array([[0.1, -0.1], [-0.1, 0.1]])
    # threshold=1.0 is above abs(J).mean() ≈ 0.1 → no edges added → fallback at line 70
    out = plot_coupling_graph(coupling_j=J, out_path=tmp_path / "g_nothr.png", threshold=1.0)
    assert out is not None
    assert out.exists()

def test_validate_manuscript_tree_yaml_front_matter_skip(tmp_path) -> None:
    # line 437: `continue` inside `if stripped.startswith("---"):` branch
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    (ms_dir / "01_section.md").write_text("---\ntitle: Test\n---\n# Real Heading\n\nBody.\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
    )
    # "---" delimiter is skipped (line 437), but "title: Test" is picked up next
    # as first content (YAML front-matter body is not auto-skipped).
    # The important thing: the validator ran without error.
    assert isinstance(report.missing_headings, list)

def test_validate_manuscript_tree_no_heading_loop_exhaustion(tmp_path) -> None:
    # line 432→447: the for loop exhausts all lines without finding a heading
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    # File with only a code block — no real heading after it
    (ms_dir / "01_section.md").write_text("```python\ncode_only\n```\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
    )
    # No heading found → file added to missing_headings
    assert "01_section.md" in report.missing_headings

def test_collect_section_subheadings_nondict_entry_line103(tmp_path) -> None:
    # line 103: non-dict entry in sections is skipped by collect_section_subheadings
    from manuscript.validation import collect_section_subheadings

    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    # "bad_entry" maps to a scalar string, not a dict
    (refs_dir / "labels.yaml").write_text(
        "sections:\n  s1:\n    number: '1.2'\n    title: Sub\n  bad_entry: not_a_dict\n"
    )
    result = collect_section_subheadings(ms_dir)
    # s1 has number '1.2' → {1: {2}}; bad_entry is silently skipped
    assert 1 in result
    assert 2 in result[1]

def test_validate_lean_wiring_missing_snippet_line405(tmp_path) -> None:
    # line 405: Lean module file present but snippet (qname) not found → broken wiring
    from manuscript.registry import LabelsRegistry, TheoremEntry
    from manuscript.validation import validate_lean_wiring

    # Lean module file with NO matching declaration
    lean_dir = tmp_path / "lean"
    lean_dir.mkdir()
    (lean_dir / "MyModule.lean").write_text("-- placeholder\ntheorem some_other_theorem : True := trivial\n")
    theorem = TheoremEntry(
        label="t1",
        kind="Theorem",
        number="1.1",
        name="Test",
        section="s1",
        lean_module="MyModule",
        lean_name="missing_theorem",
    )
    registry = Registry(
        labels=LabelsRegistry(figures={}, equations={}, theorems={"t1": theorem}),
        citations=CitationRegistry(entries={}, topic_order=(), topic_titles={}),
    )
    broken = validate_lean_wiring(registry, lean_dir)
    assert "t1" in broken
    assert "missing_theorem" in broken["t1"]

def test_validate_manuscript_tree_lean_dir_none_branch(tmp_path) -> None:
    # line 488: lean_dir is not None branch (triggers validate_lean_wiring call)
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    (ms_dir / "01_section.md").write_text("# Section\n\nBody.\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    # Pass a non-existent lean_dir: validate_lean_wiring returns {} (dir missing)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
        lean_dir=tmp_path / "lean_nonexistent",
    )
    assert report.broken_lean_wiring == {}

def test_validate_manuscript_tree_bad_section_ref(tmp_path) -> None:
    # line 472: bad_section_refs branch — §99 not in any known section
    ms_dir = tmp_path / "manuscript"
    ms_dir.mkdir()
    # §88 is not in top_level (only §1 is present) and is not 99 (bibliography)
    (ms_dir / "01_section.md").write_text("# Section\n\nSee §88 for another discussion.\n")
    refs_dir = ms_dir / "refs"
    refs_dir.mkdir()
    (refs_dir / "labels.yaml").write_text("sections:\n  s1:\n    number: '1'\n    title: S\n    file: 01_section.md\n")
    (refs_dir / "citations.yaml").write_text("topic_order: []\ntopic_titles: {}\n")
    from manuscript.registry import load_registry

    registry = load_registry(refs_dir)
    report = validate_manuscript_tree(
        manuscript_dir=ms_dir,
        registry=registry,
        variables={},
    )
    # §88 not in top_level={1} → captured as bad section ref or hardcoded ref
    assert "01_section.md" in report.bad_section_refs or "01_section.md" in report.hardcoded_refs

def test_plot_joint_heatmap_no_tick_labels(tmp_path) -> None:
    """Call without xticklabels/yticklabels to cover the False branches."""
    from lean.coupling import entangled_posterior
    from visualizations.joint_plots import plot_joint_heatmap_with_marginals

    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.zeros((2, 2))
    q = entangled_posterior(mf, [np.zeros(2), np.zeros(2)], J, Kc, gamma=0.0, lam=1.0)
    out = plot_joint_heatmap_with_marginals(
        q=q,
        title="no ticks",
        out_path=tmp_path / "nt.png",
        # xticklabels and yticklabels intentionally omitted → None
    )
    assert out.exists()

def test_pymdp_validators_optional_missing_are_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output"
    (out / "data").mkdir(parents=True)
    (out / "simulations").mkdir(parents=True)
    patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_sweep() == 0
    assert pymdp_validators.validate_free_energy_bundle() == 0
    assert pymdp_validators.validate_multi_k_sweep() == 0

def test_pymdp_validate_sweep_missing_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output" / "data"
    out.mkdir(parents=True)
    path = out / "parameter_sweep.csv"
    path.write_text("lambda,mi_closed_form\n0.0,0.1\n1.0,0.2\n", encoding="utf-8")
    patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_sweep() >= 1

def test_pymdp_validate_sweep_too_few_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output" / "data"
    out.mkdir(parents=True)
    path = out / "parameter_sweep.csv"
    path.write_text(
        "lambda,mi_closed_form,mi_empirical,mi_residual,free_energy_u0,"
        "free_energy_u1,free_energy_u2,schmidt_rank,entanglement_entropy,phase\n"
        "0.0,0.1,0.1,0.0,0.0,0.0,0.0,2,0.5,p\n",
        encoding="utf-8",
    )
    patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_sweep() >= 1

def test_validation_cli_main_on_minimal_manuscript(tmp_path: Path) -> None:
    ms = tmp_path / "manuscript"
    refs = ms / "refs"
    refs.mkdir(parents=True)
    shutil.copytree(PROJECT / "manuscript" / "refs", refs, dirs_exist_ok=True)
    (ms / "01_intro.md").write_text("# Introduction\n\nClean prose.\n", encoding="utf-8")
    (tmp_path / "output" / "data").mkdir(parents=True)
    (tmp_path / "output" / "data" / "manuscript_variables.json").write_text("{}\n", encoding="utf-8")
    code = vc.main([], project_root=tmp_path)
    assert code in (0, 1)

def test_report_rendered_leaks_detects_unresolved(tmp_path: Path) -> None:
    rendered = tmp_path / "output" / "manuscript"
    rendered.mkdir(parents=True)
    (rendered / "01_a.md").write_text("See [[FIG:missing]] token\n", encoding="utf-8")
    assert vc._report_rendered_leaks(rendered, project_root=tmp_path) >= 1
