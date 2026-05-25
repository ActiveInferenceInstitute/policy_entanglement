"""Coverage tests for `manuscript.lean_extract` — live extraction of
Lean source for `[[LEAN:label]]` tokens.

Split off from the original `test_manuscript_coverage.py`.
"""

from __future__ import annotations

from pathlib import Path

from manuscript.registry import load_registry
from manuscript.renderer import render_section

PROJECT = Path(__file__).resolve().parent.parent
REFS = PROJECT / "manuscript" / "refs"
MANUSCRIPT = PROJECT / "manuscript"
LEAN_DIR = PROJECT / "lean" / "ActinfPolicyEntanglement"


def test_lean_extract_loads_decomposition_module() -> None:
    """The on-disk Lean source must be parseable; the
    `entanglement_decomposition` theorem must be discoverable.
    """
    from manuscript.lean_extract import load_lean_snippets

    snippets = load_lean_snippets(LEAN_DIR)
    key = ("Decomposition", "entanglement_decomposition")
    assert key in snippets, sorted(s for s in snippets if s[0] == "Decomposition")
    s = snippets[key]
    assert s.keyword == "theorem"
    assert "entanglement_decomposition" in s.body
    assert s.module == "Decomposition"
    assert s.start_line > 0


def test_lean_extract_handles_inner_namespaces() -> None:
    """`Bipartite.isBipartiteMeanField_factors` lives inside the
    `Bipartite` inner namespace and must surface fully qualified.
    """
    from manuscript.lean_extract import load_lean_snippets

    snippets = load_lean_snippets(LEAN_DIR)
    key = ("Spectral", "Bipartite.isBipartiteMeanField_factors")
    assert key in snippets, sorted(k for k in snippets if k[0] == "Spectral")


def test_render_lean_snippet_includes_status() -> None:
    """The renderer wraps the snippet in a fenced Lean block and
    annotates the status keyword on the source-citation line.
    """
    from manuscript.lean_extract import load_lean_snippets, render_lean_snippet

    snippets = load_lean_snippets(LEAN_DIR)
    snip = snippets[("Decomposition", "entanglement_decomposition")]
    out = render_lean_snippet(snip, status="boundary")
    assert out.startswith("~~~lean")
    assert out.rstrip().endswith("~~~")
    assert "[status: **boundary**]" in out
    assert "Decomposition.lean:" in out


def test_render_section_resolves_lean_token() -> None:
    """`[[LEAN:thm_4_1]]` must expand to a fenced Lean block."""
    from manuscript.lean_extract import load_lean_snippets

    reg = load_registry(REFS)
    snippets = load_lean_snippets(LEAN_DIR)
    out = render_section(
        "[[LEAN:thm_4_1]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
        lean_snippets=snippets,
    )
    assert "~~~lean" in out.text
    assert "entanglement_decomposition" in out.text
    assert out.is_complete


def test_render_lean_snippet_allows_nested_backtick_fences() -> None:
    """Lean module docstrings may contain Markdown triple-backtick examples.
    The outer injected fence must not use the same delimiter.
    """
    from manuscript.lean_extract import load_lean_snippets, render_lean_snippet

    snippets = load_lean_snippets(LEAN_DIR)
    snip = snippets[("Decomposition", "freeEnergy_closedForm_witness")]
    assert "```" in snip.docstring
    out = render_lean_snippet(snip, status="boundary")
    assert out.startswith("~~~lean")
    assert out.count("~~~") == 2
    assert "```" in out


def test_render_section_lean_token_missing_when_no_cache() -> None:
    """Without a `lean_snippets` cache, the renderer marks the token
    as missing rather than crashing.
    """
    reg = load_registry(REFS)
    out = render_section(
        "[[LEAN:thm_4_1]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
        lean_snippets=None,
    )
    assert "[[MISSING:LEAN:thm_4_1" in out.text
    assert "thm_4_1" in out.missing_lean


def test_render_section_lean_token_missing_when_no_companion() -> None:
    """A theorem registered without `lean_module`/`lean_name` flags as
    missing-LEAN.  After round 3 every numbered manuscript theorem has
    a Lean companion, so this branch is exercised via a synthetic
    registry entry inserted in-memory: we patch the registry's theorem
    record to strip `lean_module` and verify the renderer marks the
    token as missing with the expected "no lean_module/lean_name"
    message.
    """
    import dataclasses

    reg = load_registry(REFS)
    # Grab a real theorem and clone it with its lean_module / lean_name
    # stripped so we exercise the "no companion" branch.
    original = reg.labels.theorems["thm_11_1"]
    stripped = dataclasses.replace(original, lean_module="", lean_name="")
    reg.labels.theorems["thm_11_1"] = stripped
    try:
        out = render_section(
            "[[LEAN:thm_11_1]]",
            registry=reg,
            variables={},
            manuscript_dir=MANUSCRIPT,
            lean_snippets={},
        )
        assert "no lean_module/lean_name in registry" in out.text
        assert "thm_11_1" in out.missing_lean
    finally:
        reg.labels.theorems["thm_11_1"] = original


def test_render_section_lean_token_unknown_label() -> None:
    """An unknown label raises a missing-LEAN marker."""
    reg = load_registry(REFS)
    out = render_section(
        "[[LEAN:nonexistent_label]]",
        registry=reg,
        variables={},
        manuscript_dir=MANUSCRIPT,
        lean_snippets={},
    )
    assert "[[MISSING:LEAN:nonexistent_label]]" in out.text
    assert "nonexistent_label" in out.missing_lean
