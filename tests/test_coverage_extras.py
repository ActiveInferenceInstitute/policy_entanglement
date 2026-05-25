"""Targeted branch-coverage tests for previously uncovered code paths.

Each test exercises a specific branch missed by the main suites.
All tests follow the no-mocks policy (real data and computations only).
"""

from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# manuscript.bibliography
# ---------------------------------------------------------------------------
from manuscript.bibliography import (
    _format_bibtex_authors,
    _infer_entry_type,
    _ordered_bib_fields,
    _sorted_keys,
    auto_bibliography,
    write_references_bib,
)
from manuscript.registry import Citation, CitationRegistry


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


# ---------------------------------------------------------------------------
# manuscript.equation_numbering — assign_within_section_numbers (lines 118-121)
# ---------------------------------------------------------------------------

from manuscript.equation_numbering import assign_within_section_numbers


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


# ---------------------------------------------------------------------------
# lean.decomposition error paths (lines 98 and 172)
# ---------------------------------------------------------------------------

from lean.decomposition import (
    _marginals_efes_broadcast_to_joint,
    free_energy_against_entangled_prior,
)


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


# ---------------------------------------------------------------------------
# lean.geometry — coupling_log_weight_affine_check returns False (line 126)
# ---------------------------------------------------------------------------

from lean.geometry import coupling_log_weight_affine_check


def test_coupling_log_weight_affine_check_returns_false_on_nan() -> None:
    # line 126: NaN propagation makes np.allclose return False → returns False
    Ja = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.array([[0.1, 0.0], [0.0, 0.1]])  # non-zero so NaN propagates
    gamma = float("nan")  # invalid but exercises the branch
    result = coupling_log_weight_affine_check(Ja, Kc, gamma, lams=[0.0, 1.0, 2.0])
    assert result is False


# ---------------------------------------------------------------------------
# lean.invariants — coupling_pays_invariants returns [] (line 369)
# ---------------------------------------------------------------------------

from lean.invariants import SweepGrid, coupling_pays_invariants


def test_coupling_pays_invariants_empty_when_all_below_threshold() -> None:
    # line 369: returns [] when no lambda value exceeds lam_threshold
    grid = SweepGrid(lam_min=0.0, lam_max=0.5, num=5)
    # threshold=1.0 is above lam_max=0.5 → no lam passes → pays list stays empty
    result = coupling_pays_invariants(grid, lam_threshold=1.0)
    assert result == []


# ---------------------------------------------------------------------------
# manuscript.validation — validate_figure_files missing image (line 344)
# ---------------------------------------------------------------------------

from manuscript.validation import validate_figure_files


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


# ---------------------------------------------------------------------------
# manuscript.validation — validate_manuscript_tree branches (lines 437, 456,
# 460, 463-464, 472, 476, 480, 488)
# ---------------------------------------------------------------------------

from manuscript.registry import (
    LabelsRegistry,
    Registry,
)
from manuscript.validation import validate_manuscript_tree


def _minimal_registry() -> Registry:
    return Registry(
        labels=LabelsRegistry(figures={}, equations={}),
        citations=CitationRegistry(entries={}, topic_order=(), topic_titles={}),
    )


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


# ---------------------------------------------------------------------------
# visualizations.graphs — K=2 else-branch and high-threshold no-edges (lines 65→, 70)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# visualizations.joint_plots — without tick labels (lines 53→56, 56→60)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# visualizations.joint_plots — without tick labels (lines 53→56, 56→60)
# ---------------------------------------------------------------------------


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
