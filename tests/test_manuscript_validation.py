"""Coverage tests for `manuscript.validation` and `manuscript.registry`
edge cases (hyperlinks, figure files, variable ranges, malformed YAML,
manuscript-tree validator, missing headings).

Split off from the original `test_manuscript_coverage.py`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from manuscript.registry import (
    Citation,
    CitationRegistry,
    Equation,
    Figure,
    LabelsRegistry,
    Registry,
    load_registry,
)
from manuscript.validation import (
    HEADING_RE,
    HYPERLINK_RE,
    SECTION_FILES_RE,
    find_hardcoded_numeric_literals,
    find_hardcoded_rendered_source_literals,
    find_registry_tokens_in_code_fences,
    find_rendered_token_leaks,
    section_paths,
    validate_figure_files,
    validate_hyperlinks,
    validate_lean_wiring,
    validate_manuscript_tree,
    validate_registry_source_fields,
    validate_rendered_token_leaks,
    validate_undefined_tokens,
    validate_variables_against_ranges,
    variable_provenance_summary,
)

PROJECT = Path(__file__).resolve().parent.parent
REFS = PROJECT / "manuscript" / "refs"
MANUSCRIPT = PROJECT / "manuscript"
FIGURE_UNCERTAINTY_CLASSES = {
    "deterministic_grid",
    "canonical_seed",
    "replicate_envelope",
    "confidence_interval",
    "analytical_schematic",
}


def _tiny_registry() -> Registry:
    fig = Figure(
        label="x",
        path="output/figures/whatever.png",
        caption="Sample.",
        short="x",
        sections=("§1",),
        source="scripts/x.py",
        number=1,
    )
    eq = Equation(
        label="e",
        latex="x = y",
        name="Sample",
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


# ---------------------------------------------------------------------------
# Section-path collection + regexes
# ---------------------------------------------------------------------------


def test_section_paths_includes_99_bibliography() -> None:
    paths = section_paths(MANUSCRIPT)
    names = [p.name for p in paths]
    assert "99_bibliography.md" in names


def test_section_files_re_matches_only_numbered_sections() -> None:
    assert SECTION_FILES_RE.match("0A_abstract.md")
    assert SECTION_FILES_RE.match("2D_decomposition.md")
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


# ---------------------------------------------------------------------------
# Hyperlinks + figure-file existence
# ---------------------------------------------------------------------------


def test_validate_hyperlinks_skips_mailto() -> None:
    broken = validate_hyperlinks("[Contact](mailto:x@y)", base=MANUSCRIPT)
    assert broken == []


def test_validate_hyperlinks_skips_data_uri() -> None:
    text = "Embedded [icon](data:image/png;base64,AAAA) in prose."
    assert validate_hyperlinks(text, base=MANUSCRIPT) == []


def test_validate_hyperlinks_skips_token_marker() -> None:
    text = "Reference [token]([[FIG:placeholder]]) — should be ignored."
    assert validate_hyperlinks(text, base=MANUSCRIPT) == []


def test_validate_hyperlinks_skips_generated_output_paths() -> None:
    from manuscript.validation import _is_generated_output_path

    assert _is_generated_output_path("../output/figures/whatever.png")
    assert _is_generated_output_path("output/data/foo.csv")
    assert not _is_generated_output_path("../src/lean/joint_dist.py")
    text = "[gen](../output/data/never_existed.csv) and [src](../src/lean/joint_dist.py)"
    assert validate_hyperlinks(text, base=MANUSCRIPT) == []


def test_validate_hyperlinks_resolves_anchor_only_links_against_existing_file(
    tmp_path: Path,
) -> None:
    """A link of the form `target.md#section` should still verify the
    file exists (anchor is stripped before resolution).
    """
    md = tmp_path / "x.md"
    target = tmp_path / "target.md"
    target.write_text("# heading\n")
    md.write_text("[a](target.md#heading)")
    broken = validate_hyperlinks(md.read_text(), base=tmp_path)
    assert broken == []


def test_validate_figure_files_skips_external() -> None:
    out = validate_figure_files(
        "![alt](https://example.com/x.png)",
        manuscript_dir=MANUSCRIPT,
    )
    assert out == []


def test_validate_figure_files_strips_anchor() -> None:
    text = "![alt](does/not/exist.png#anchor)"
    bad = validate_figure_files(text, manuscript_dir=PROJECT)
    assert "does/not/exist.png" in bad


def test_validate_figure_files_reports_missing_png(tmp_path: Path) -> None:
    md = "![alt text](does/not/exist.png)"
    bad = validate_figure_files(md, manuscript_dir=tmp_path)
    assert "does/not/exist.png" in bad


# ---------------------------------------------------------------------------
# Token + variable range validators
# ---------------------------------------------------------------------------


def test_validate_undefined_tokens_handles_citelist() -> None:
    reg = _tiny_registry()
    bad = validate_undefined_tokens(
        "[[CITELIST:topicA]] [[CITELIST:nope]]",
        reg,
        variables={},
    )
    kinds = [k for k, _ in bad]
    assert "CITELIST" in kinds


def test_validate_undefined_tokens_eq_unknown() -> None:
    reg = _tiny_registry()
    bad = validate_undefined_tokens(
        "[[EQ:unknown]] [[EQREF:unknown]]",
        reg,
        variables={},
    )
    kinds = sorted({k for k, _ in bad})
    assert kinds == ["EQ", "EQREF"]


def test_validate_undefined_tokens_keeps_defined_fig_and_var() -> None:
    """Grouped conditions must not flag valid FIG/VAR when another kind is undefined."""
    reg = _tiny_registry()
    bad = validate_undefined_tokens(
        "[[FIG:x]] [[FIGREF:x]] [[VAR:live_metric]] [[EQ:unknown]]",
        reg,
        variables={"live_metric": 0.42},
    )
    assert bad == [("EQ", "unknown")]


def test_validate_undefined_tokens_flags_sentinel_var() -> None:
    reg = _tiny_registry()
    bad = validate_undefined_tokens(
        "[[VAR:live_metric]]",
        reg,
        variables={"live_metric": "not-run"},
    )
    assert bad == [("VAR", "live_metric")]


def test_validate_variables_handles_missing_or_non_numeric() -> None:
    bad = validate_variables_against_ranges(
        {"a": "not_a_number"},
        {"a": (0.0, 1.0), "b": (0.0, 1.0)},
    )
    assert "a" in bad and "non-numeric" in bad["a"]
    assert "b" in bad and "missing" in bad["b"]


def test_strict_source_literal_detector_scans_headings() -> None:
    text = "# Proof of Theorem 5.1\n\nBody with [[THMREF:thm_4_1]]."
    assert "Theorem 5.1" in find_hardcoded_rendered_source_literals(text)


def test_strict_source_literal_detector_ignores_tokens_and_code() -> None:
    text = "caption [[THMREF:thm_4_1]] and `Theorem 5.1` plus ```text\nFigure 7\n```"
    assert find_hardcoded_rendered_source_literals(text) == []


def test_validate_registry_source_fields_flags_paper_facing_values() -> None:
    reg = _tiny_registry()
    bad_fig = Figure(
        label="bad",
        path="output/figures/bad.png",
        caption="See Figure 7 and Theorem 5.1.",
        short="T=100 rollout",
        sections=("§1",),
        source="scripts/x.py",
        number=2,
    )
    registry = Registry(
        labels=LabelsRegistry(
            figures={**reg.labels.figures, "bad": bad_fig},
            equations=reg.labels.equations,
        ),
        citations=reg.citations,
    )
    hits = validate_registry_source_fields(registry)
    assert "labels.yaml::figures.bad.caption" in hits
    assert "labels.yaml::figures.bad.short" in hits


def test_rendered_token_leak_detector_allows_code_examples() -> None:
    text = (
        "Every value flows through `[[VAR:<key>]]` examples.\n\n"
        "```markdown\n[[SECREF:example]]\n[[MISSING:LEAN:example]]\n```\n"
    )
    assert find_rendered_token_leaks(text) == []


def test_rendered_token_leak_detector_flags_paper_facing_tokens() -> None:
    text = "Rendered prose still says [[VAR:pymdp_sweep_grid_points]] and [[MISSING:LEAN:x]]."
    assert find_rendered_token_leaks(text) == ["[[VAR:pymdp_sweep_grid_points]]", "[[MISSING:LEAN:x]]"]


def test_validate_rendered_token_leaks_scans_rendered_markdown(tmp_path: Path) -> None:
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    good.write_text("Token syntax example: `[[FIG:label]]`.\n", encoding="utf-8")
    bad.write_text("Paper-facing unresolved token [[THMREF:thm_4_1]].\n", encoding="utf-8")

    assert validate_rendered_token_leaks(tmp_path) == {"bad.md": ["[[THMREF:thm_4_1]]"]}


def test_variable_provenance_summary_classes_known_sources() -> None:
    summary = variable_provenance_summary(
        {
            "param_sweep_grid_points": 121,
            "lean_total_declarations": 124,
            "theorem_registry_count": 20,
            "ising_mi_at_lam_1": 0.1,
            "robustness_scenario_count": 14,
            "surprise_key": 1,
        },
        hyperparameter_keys=frozenset({"param_sweep_grid_points"}),
    )

    assert summary["hyperparameter-derived"] == 1
    assert summary["source-scan-derived"] == 1
    assert summary["registry-derived"] == 1
    assert summary["analytic-computation"] == 1
    assert summary["sidecar-derived"] == 1
    assert summary["uncategorized"] == 1


def test_figure_registry_declares_caption_uncertainty_contract() -> None:
    data = yaml.safe_load((REFS / "labels.yaml").read_text(encoding="utf-8"))
    failures: list[str] = []
    for label, payload in (data.get("figures") or {}).items():
        uncertainty = str(payload.get("uncertainty", "") or "")
        if uncertainty not in FIGURE_UNCERTAINTY_CLASSES:
            failures.append(f"{label}: invalid uncertainty class {uncertainty!r}")
        if not str(payload.get("source", "") or "").strip():
            failures.append(f"{label}: missing source")
        caption = str(payload.get("caption", "") or "")
        if re.search(r"\bseed\s*=\s*\d+\b", caption, flags=re.IGNORECASE):
            failures.append(f"{label}: hard-coded seed literal in caption")
        if re.search(r"\bT\s*=\s*\d+\b", caption):
            failures.append(f"{label}: hard-coded horizon literal in caption")
    assert not failures, "\n".join(failures)


# ---------------------------------------------------------------------------
# Manuscript-tree validator
# ---------------------------------------------------------------------------


def test_validate_manuscript_tree_handles_pandoc_raw_block(tmp_path: Path) -> None:
    """Sections that lead with a Pandoc raw-LaTeX block must still be
    accepted as having a leading heading further down.
    """
    section = tmp_path / "S99_test.md"
    section.write_text("```{=latex}\n\\appendix\n```\n\n# Real Heading\n\nbody.\n")
    reg = _tiny_registry()
    report = validate_manuscript_tree(
        manuscript_dir=tmp_path,
        registry=reg,
        variables={},
    )
    assert "S99_test.md" not in report.missing_headings


def test_validate_manuscript_tree_detects_missing_heading(tmp_path: Path) -> None:
    section = tmp_path / "00_no_heading.md"
    section.write_text("Just some prose, no heading.\n")
    reg = _tiny_registry()
    report = validate_manuscript_tree(
        manuscript_dir=tmp_path,
        registry=reg,
        variables={},
    )
    assert "00_no_heading.md" in report.missing_headings


def test_validate_manuscript_tree_runs_variable_ranges() -> None:
    reg = _tiny_registry()
    report = validate_manuscript_tree(
        manuscript_dir=MANUSCRIPT,
        registry=reg,
        variables={"x": 0.5},
        variable_ranges={"x": (0.0, 1.0)},
    )
    assert "x" not in report.out_of_range_variables


def test_validation_report_is_clean_property() -> None:
    from manuscript.validation import ManuscriptValidationReport

    r = ManuscriptValidationReport(section_files=[])
    assert r.is_clean
    r.missing_headings.append("x.md")
    assert not r.is_clean


def test_collect_top_level_sections_reads_registry(tmp_path: Path) -> None:
    """`collect_top_level_sections` reads section numbers from the
    registry under ``manuscript/refs/labels.yaml`` (Tier-2 contract:
    section numbers are owned by the registry, not the filename).
    """
    from manuscript.validation import collect_top_level_sections

    refs = tmp_path / "refs"
    refs.mkdir()
    (refs / "labels.yaml").write_text(
        "sections:\n"
        '  intro:    {number: "1", title: "Intro",    file: "1B_intro.md"}\n'
        '  intro.x:  {number: "1.1", title: "Sub",    parent: intro}\n'
        '  body:     {number: "2", title: "Body",     file: "2B_body.md"}\n'
        '  bad:      {number: "",  title: "Bad",      file: "X.md"}\n'
    )
    out = collect_top_level_sections(tmp_path)
    assert out == {1, 2}


# ---------------------------------------------------------------------------
# Registry edge cases (malformed YAML payloads)
# ---------------------------------------------------------------------------


def test_seq_handles_none_str_and_iterable() -> None:
    from manuscript.registry import _seq

    assert _seq(None) == tuple()
    assert _seq("only_one") == ("only_one",)
    assert _seq(["a", "b"]) == ("a", "b")


def test_load_citations_skips_non_dict_payload(tmp_path: Path) -> None:
    """An ill-formed entry (e.g. a list) is skipped silently rather than
    crashing the whole load.
    """
    from manuscript.registry import load_citations

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
    from manuscript.registry import Citation

    c = Citation(
        key="x",
        authors="A",
        year=2020,
        title="t",
        venue="v",
        doi="10.1234/abc",
    )
    line = c.render_bibliography()
    assert "doi:10.1234/abc" in line


def test_load_labels_skips_non_dict_section_payload(tmp_path: Path) -> None:
    from manuscript.registry import load_labels

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
    from manuscript.registry import load_labels

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


# ---------------------------------------------------------------------------
# Adjacent: visualization helper validation
# ---------------------------------------------------------------------------


def test_plot_rollout_marginals_rejects_empty_marginals_list(tmp_path: Path) -> None:
    """K < 1 triggers ValueError guard at trajectory_plots line 30."""
    import numpy as np

    from visualizations.trajectory_plots import plot_rollout_marginals

    with pytest.raises(ValueError, match="non-empty"):
        plot_rollout_marginals(
            marginals_per_stream=[],
            titles=[],
            total_correlations=np.zeros(0),
            out_path=tmp_path / "x.png",
        )


# ---------------------------------------------------------------------------
# Four-track wiring: theorem registry ↔ Lean source ↔ auto-injection
# ---------------------------------------------------------------------------


def test_validate_lean_wiring_returns_empty_when_lean_dir_missing(tmp_path: Path) -> None:
    """No Lean directory → wiring check is a no-op (skip)."""
    registry = load_registry(REFS)
    broken = validate_lean_wiring(registry, lean_dir=None)
    assert broken == {}


def test_validate_lean_wiring_returns_empty_when_lean_dir_does_not_exist(tmp_path: Path) -> None:
    registry = load_registry(REFS)
    broken = validate_lean_wiring(registry, lean_dir=tmp_path / "does-not-exist")
    assert broken == {}


def test_validate_lean_wiring_resolves_every_registered_companion() -> None:
    """The live boundary fragment satisfies every registered Lean companion.

    This is the four-track coherence gate: every theorem in
    `manuscript/refs/labels.yaml` whose `lean_module`/`lean_name` are
    populated must point at a real Lean declaration in
    `lean/ActinfPolicyEntanglement/`.
    """
    registry = load_registry(REFS)
    lean_dir = PROJECT / "lean" / "ActinfPolicyEntanglement"
    broken = validate_lean_wiring(registry, lean_dir=lean_dir)
    assert broken == {}, "broken Lean wiring (registered theorem → Lean source mismatch):\n  " + "\n  ".join(
        f"{label}: {explanation}" for label, explanation in broken.items()
    )


def test_validate_lean_wiring_detects_missing_module(tmp_path: Path) -> None:
    """Build a synthetic registry pointing at a non-existent module
    and verify the gate flags it.
    """
    from manuscript.registry import TheoremEntry

    fake_thm = TheoremEntry(
        label="thm_fake",
        kind="Theorem",
        number="9.9",
        name="Fake",
        section="setup",
        lean_module="NonexistentModule",
        lean_name="nonexistent",
        status="proved",
    )
    labels = LabelsRegistry(
        equations={},
        figures={},
        sections={},
        theorems={"thm_fake": fake_thm},
    )
    citations = CitationRegistry(entries={}, topic_order=(), topic_titles={})
    registry = Registry(labels=labels, citations=citations)
    # Use a real but irrelevant lean dir.
    lean_dir = PROJECT / "lean" / "ActinfPolicyEntanglement"
    broken = validate_lean_wiring(registry, lean_dir=lean_dir)
    assert "thm_fake" in broken
    assert "NonexistentModule" in broken["thm_fake"]


# ---------------------------------------------------------------------------
# Extended hardcoded-numeric detectors (empirical results, horizons, K)
# ---------------------------------------------------------------------------


def test_find_hardcoded_numeric_literals_flags_empirical_result() -> None:
    """``I(λ=2) = 0.4421`` outside [[VAR:...]] should fail the gate."""
    text = "We observe I(λ=2) = 0.4421 nats at the half-saturation point."
    hits = find_hardcoded_numeric_literals(text)
    assert any("0.4421" in h for h in hits), hits


def test_find_hardcoded_numeric_literals_skips_var_token() -> None:
    """Same text with [[VAR:...]] → no flag (token wins)."""
    text = "We observe I(λ=2) = [[VAR:ising_mi_at_lam_2:.4f]] nats."
    hits = find_hardcoded_numeric_literals(text)
    # The bare numerals "2" and the var key are inside protected regions.
    assert not any("0.4421" in h for h in hits), hits


def test_find_hardcoded_numeric_literals_flags_rollout_horizon() -> None:
    text = "Each rollout of 10 steps produces..."
    hits = find_hardcoded_numeric_literals(text)
    assert any("10 steps" in h for h in hits), hits


def test_find_hardcoded_numeric_literals_flags_K_ensemble() -> None:
    text = "We use K = 4 streams across the experiment."
    hits = find_hardcoded_numeric_literals(text)
    assert any("4 streams" in h.lower() for h in hits), hits


def test_find_hardcoded_numeric_literals_does_not_flag_short_decimals() -> None:
    """``\\lambda \\in [0, 3]`` should NOT be flagged as a result."""
    text = r"For $\lambda \in [0, 3]$ the curve traces a sigmoid."
    hits = find_hardcoded_numeric_literals(text)
    assert hits == []


def test_find_hardcoded_numeric_literals_flags_grid_point_count() -> None:
    """``121-point grid`` must be flagged so prose pulls the integer
    from the hyperparameter snapshot via ``[[VAR:...]]`` rather than
    hand-typing the count.
    """
    text = "We sweep the 121-point grid in λ across the parameter range."
    hits = find_hardcoded_numeric_literals(text)
    assert any("121-point" in h for h in hits), hits


def test_find_hardcoded_numeric_literals_flags_seed_literal() -> None:
    """``seed = 42`` must be flagged.

    Seeds belong in :mod:`simulation.hyperparameters` and flow into
    the manuscript via ``[[VAR:figure_global_seed]]``; a hard-coded
    integer in prose would drift the moment the seed bank changes.
    """
    text = "All figures use seed = 42 for reproducibility."
    hits = find_hardcoded_numeric_literals(text)
    assert any("seed" in h.lower() for h in hits), hits


def test_find_registry_tokens_in_code_fences_flags_cross_reference_tokens() -> None:
    text = "```lean\n-- bad: [[EQ:tc_decomp]] inside code\n```\n"
    hits = find_registry_tokens_in_code_fences(text)
    assert hits == ["[[EQ:tc_decomp]]"]


def test_find_registry_tokens_in_tilde_code_fences_flags_cross_reference_tokens() -> None:
    text = "~~~lean\n-- bad: [[LEAN:thm_4_1]] inside code\n~~~\n"
    hits = find_registry_tokens_in_code_fences(text)
    assert hits == ["[[LEAN:thm_4_1]]"]


def test_find_registry_tokens_in_code_fences_allows_var_tokens() -> None:
    text = '```json\n{"K": [[VAR:pymdp_ensemble_K]]}\n```\n'
    assert find_registry_tokens_in_code_fences(text) == []


# ---------------------------------------------------------------------------
# Sentinel-list export gate: every H.*_SENTINEL_* constant must be
# serialized into manuscript_variables.json so prose enumerations
# trace back to a single source of truth.
# ---------------------------------------------------------------------------


def test_every_sentinel_tuple_has_a_json_export(tmp_path: Path) -> None:
    """For every public ``*_SENTINEL_*`` (or matching ``*_VERIFICATION_*``)
    constant in :mod:`simulation.hyperparameters`, ``manuscript_variables.py``
    must export at least one JSON key derived from it.

    Catches drift where a new sentinel tuple is added to hyperparameters
    but not threaded through the auto-injection pipeline.
    """
    import json
    import sys

    src = str(PROJECT / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from simulation import hyperparameters as H  # noqa: E402

    sentinel_attrs = [
        name
        for name in dir(H)
        if (
            name.endswith("_SENTINEL_LAMBDAS")
            or name.endswith("_SENTINEL_DELTAS")
            or name.endswith("_VERIFICATION_LAMBDAS")
            or name == "TT_RANK_STREAM_COUNTS"
        )
        and not name.startswith("_")
    ]
    assert sentinel_attrs, "expected at least one sentinel attribute in H"

    json_path = PROJECT / "output" / "data" / "manuscript_variables.json"
    if not json_path.exists():
        pytest.skip("manuscript_variables.json not yet produced")
    keys = set(json.loads(json_path.read_text()).keys())

    # Convention: sentinel JSON keys are the lower-cased attribute name
    # (e.g. `ising_mi_sentinel_lambdas` for `ISING_MI_SENTINEL_LAMBDAS`).
    missing: list[str] = []
    for attr in sentinel_attrs:
        expected_key = attr.lower()
        if expected_key not in keys:
            missing.append(f"{attr} (expected JSON key '{expected_key}')")
    assert not missing, (
        "sentinel constants in hyperparameters.py without a "
        "manuscript_variables.json key — extend "
        "scripts/manuscript_variables.py::_sentinel_list_facts: " + ", ".join(missing)
    )
