"""Tests for `scripts/generate_index.py` — the auto-generated TOC.

The output `manuscript/INDEX.md` must contain every section registered
in `manuscript/refs/labels.yaml::sections` and must be byte-stable
under repeated runs.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from manuscript.index_generator import build_index_text, write_index

PROJECT = Path(__file__).resolve().parent.parent
INDEX = PROJECT / "manuscript" / "INDEX.md"


@pytest.fixture(scope="module")
def fresh_index() -> str:
    """Run the generator and return the produced text."""
    result = subprocess.run(
        [sys.executable, str(PROJECT / "scripts" / "generate_index.py")],
        capture_output=True,
        text=True,
        cwd=PROJECT,
    )
    assert result.returncode == 0, result.stderr
    return INDEX.read_text()


def test_index_lists_every_top_level_section(fresh_index: str) -> None:
    """Every top-level section file (`0N_*.md` and `S0N_*.md`) must
    appear in the auto-generated index."""
    expected = sorted(
        p.name
        for p in (PROJECT / "manuscript").glob("*.md")
        if p.name.split("_", 1)[0].rstrip("a").isalnum()
        and (p.name[0].isdigit() or p.name.startswith("S0"))
        and p.name not in {"99_bibliography.md"}  # has its own row
    )
    for name in expected:
        if name.startswith(("00_", "preamble")):
            continue
        assert name in fresh_index, f"INDEX.md missing entry for {name}"


def test_index_includes_bibliography(fresh_index: str) -> None:
    assert "99_bibliography.md" in fresh_index


def test_index_byte_stable_under_repeat() -> None:
    """Re-running `generate_index.py` must produce the same bytes."""
    one = subprocess.run(
        [sys.executable, str(PROJECT / "scripts" / "generate_index.py")],
        capture_output=True,
        text=True,
        cwd=PROJECT,
    )
    text_a = INDEX.read_text()
    two = subprocess.run(
        [sys.executable, str(PROJECT / "scripts" / "generate_index.py")],
        capture_output=True,
        text=True,
        cwd=PROJECT,
    )
    text_b = INDEX.read_text()
    assert text_a == text_b
    assert one.returncode == 0
    assert two.returncode == 0


def test_index_contains_auto_generated_marker(fresh_index: str) -> None:
    assert "auto-generated" in fresh_index.lower()


def test_index_links_to_registry(fresh_index: str) -> None:
    assert "refs/labels.yaml" in fresh_index
    assert "refs/citations.yaml" in fresh_index


def test_index_generator_library_build_index_text() -> None:
    text = build_index_text(manuscript_dir=PROJECT / "manuscript")
    assert "auto-generated" in text.lower()
    assert "refs/labels.yaml" in text


def test_index_generator_library_write_index(tmp_path: Path) -> None:
    ms = tmp_path / "manuscript"
    refs = ms / "refs"
    refs.mkdir(parents=True)
    (refs / "labels.yaml").write_text(
        "figures: {}\nequations: {}\nsections:\n  intro:\n    file: 01_intro.md\n    title: Intro\n",
        encoding="utf-8",
    )
    (refs / "citations.yaml").write_text("entries: []\n", encoding="utf-8")
    (ms / "01_intro.md").write_text("# Intro\n", encoding="utf-8")
    path = write_index(manuscript_dir=ms)
    assert path == ms / "INDEX.md"
    assert "Intro" in path.read_text(encoding="utf-8")
