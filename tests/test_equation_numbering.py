"""Tests for `manuscript.equation_numbering`.

Asserts the per-section auto-numbering pipeline:

* `precompute_equation_numbers` returns a stable label → "S.K" map
  using only the registry section number and source order.
* `retag_display_math` overwrites any existing `\\tag{...}` and
  injects a fresh `\\tag{S.K}` into every `$$..$$` block.
* The renderer's full pipeline produces auto-numbered tags in every
  rendered section file (no missing equation numbers).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from manuscript.equation_numbering import (
    file_to_section_number,
    precompute_equation_numbers,
    retag_display_math,
    section_equation_count,
)
from manuscript.meta_files import MANUSCRIPT_NON_BODY_MD
from manuscript.registry import load_registry

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT_DIR = PROJECT_ROOT / "manuscript"
RENDERED_DIR = PROJECT_ROOT / "output" / "manuscript"


@pytest.fixture(scope="module")
def registry():
    return load_registry(MANUSCRIPT_DIR / "refs")


def test_file_to_section_number_includes_main_files(registry) -> None:
    mapping = file_to_section_number(registry)
    assert mapping["1B_motivation.md"] == "1"
    assert mapping["2E_examples.md"] == "6"
    assert mapping["4B_empirical_suite.md"] == "13"


def test_precompute_equation_numbers_returns_stable_map(registry) -> None:
    mapping = precompute_equation_numbers(
        manuscript_dir=MANUSCRIPT_DIR,
        registry=registry,
    )
    assert isinstance(mapping, dict)
    # Every label points to "S.K".
    for label, value in mapping.items():
        assert isinstance(value, str)
        assert "." in value, f"{label} → {value!r} not in S.K form"


def test_precompute_includes_all_registered_eq_tokens(registry) -> None:
    """Every label that appears as a `[[EQ:label]]` token in any
    section file must show up in the precomputed map.
    """
    eq_token_re = re.compile(r"\[\[EQ:([A-Za-z0-9_]+)\]\]")
    expected: set[str] = set()
    for src in sorted(MANUSCRIPT_DIR.glob("*.md")):
        if src.name in MANUSCRIPT_NON_BODY_MD:
            continue
        for m in eq_token_re.finditer(src.read_text()):
            expected.add(m.group(1))
    mapping = precompute_equation_numbers(
        manuscript_dir=MANUSCRIPT_DIR,
        registry=registry,
    )
    missing = expected - set(mapping.keys())
    assert not missing, f"missing labels in mapping: {sorted(missing)}"


def test_retag_display_math_injects_new_tag() -> None:
    text = "Some prose.\n\n$$x = 1$$\n\nMore.\n\n$$y = 2$$\n"
    out = retag_display_math(text, section_number="5")
    assert "\\tag{5.1}" in out
    assert "\\tag{5.2}" in out


def test_retag_display_math_overwrites_existing_tag() -> None:
    text = "$$x = 1\n\\tag{99}$$"
    out = retag_display_math(text, section_number="5")
    # Old tag is gone, new tag is in place.
    assert "\\tag{99}" not in out
    assert "\\tag{5.1}" in out


def test_retag_display_math_noop_without_section_number() -> None:
    text = "$$x = 1$$"
    out = retag_display_math(text, section_number="")
    assert out == text


def test_section_equation_count_counts_eq_and_math() -> None:
    text = "Intro.\n\n$$a = 1$$\n\n[[EQ:foo]]\n\n$$b = 2$$\n"
    assert section_equation_count(text) == 3


@pytest.mark.parametrize(
    "section_file",
    [
        "2D_decomposition.md",
        "2E_examples.md",
        "2F_geometry.md",
        "2H_heterogeneous.md",
        "4B_empirical_suite.md",
    ],
)
def test_rendered_section_has_no_unnumbered_display_math(
    section_file: str,
) -> None:
    """After full render, every `$$..$$` block in these sections must
    carry a `\\tag{...}` (no missing numbers).
    """
    rendered = RENDERED_DIR / section_file
    if not rendered.exists():
        pytest.skip(f"render output missing: {rendered}")
    text = rendered.read_text()
    display_re = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
    for m in display_re.finditer(text):
        body = m.group(1)
        assert "\\tag{" in body, f"unnumbered display-math block in {section_file}:\n  body[:80] = {body[:80]!r}"


def test_rendered_section_tags_match_section_number() -> None:
    """Equations rendered in §6 must not carry appendix-section tags.

    Body-section equations get numeric tags (``S.K`` where S is a
    digit string). Appendix-section tags have single-letter prefixes
    (``A.``, ``B.``, …). A letter-prefixed tag inside a body section
    signals that ``precompute_equation_numbers`` assigned the canonical
    number from a later appendix occurrence instead of the first
    defining section — the first-occurrence-wins invariant was violated.
    Cross-references to equations from other *body* sections (e.g.
    ``\\tag{4.1}`` inside §6) are allowed because the equation was
    genuinely first defined there.
    """
    rendered = RENDERED_DIR / "2E_examples.md"
    if not rendered.exists():
        pytest.skip(f"render output missing: {rendered}")
    tags = re.findall(r"\\tag\{([^}]+)\}", rendered.read_text())
    assert tags  # at least one display equation in §6
    for tag in tags:
        assert not re.match(r"^[A-Z]\.", tag), (
            f"appendix-scoped equation tag {tag!r} leaked into §6 — "
            "check precompute_equation_numbers first-occurrence-wins invariant"
        )
