"""Drift-detection test for the auto-generated per-theorem four-track table.

Re-runs ``scripts/generate_theorem_map.py::render`` and asserts that
the result matches ``docs/reference/_theorem_map.md`` byte-for-byte.

Any change to:

  * ``manuscript/refs/labels.yaml::theorems`` (new theorem, renamed
    Lean companion, status update),
  * ``scripts/generate_theorem_map.py::PYTHON_COMPANION``,
  * ``scripts/generate_theorem_map.py::TEST_GATE``,

requires regenerating the table:

    uv run python scripts/generate_theorem_map.py

— and committing the updated ``_theorem_map.md``.

This is the four-track-coherence drift gate: it locks the manuscript's
per-theorem cross-reference to the registry and to the
generator-side Python / test mapping, so the rendered table cannot
fall out of sync with reality.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
GENERATOR = PROJECT / "scripts" / "generate_theorem_map.py"
GENERATED = PROJECT / "docs" / "reference" / "_theorem_map.md"


@pytest.fixture(scope="module")
def generator_module():
    """Load the generator script as a module without invoking ``main``."""
    spec = importlib.util.spec_from_file_location("generate_theorem_map", GENERATOR)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generated_file_exists() -> None:
    assert GENERATED.is_file(), (
        f"missing auto-generated file at {GENERATED}; run `uv run python scripts/generate_theorem_map.py` to create it"
    )


def test_generated_table_is_byte_identical(generator_module) -> None:
    """Re-render and confirm zero drift against the committed file."""
    rendered = generator_module.render()
    on_disk = GENERATED.read_text()
    assert rendered == on_disk, (
        "drift detected between scripts/generate_theorem_map.py output "
        "and docs/reference/_theorem_map.md.\n"
        "Regenerate with: `uv run python scripts/generate_theorem_map.py`"
    )


def test_python_companion_paths_resolve(generator_module) -> None:
    """Every entry in PYTHON_COMPANION points at a real source file."""
    src = PROJECT / "src"
    missing = []
    for label, (_qualified, source) in generator_module.PYTHON_COMPANION.items():
        if not (src / source).is_file():
            missing.append(f"{label}: {source}")
    assert not missing, "PYTHON_COMPANION entries point at missing source files: " + ", ".join(missing)


def test_test_gate_files_resolve(generator_module) -> None:
    """Every entry in TEST_GATE points at a real test file."""
    tests_dir = PROJECT / "tests"
    missing = []
    for label, name in generator_module.TEST_GATE.items():
        if not (tests_dir / f"{name}.py").is_file():
            missing.append(f"{label}: tests/{name}.py")
    assert not missing, "TEST_GATE entries point at missing test files: " + ", ".join(missing)


def test_every_current_theorem_has_python_and_test_columns(generator_module) -> None:
    """HONEST four-track contract (RedTeam 2026-05-19 R2 — this test
    previously *encoded the over-claim it should prevent*: it mandated a
    `PYTHON_COMPANION` for EVERY row, which forced thematically-adjacent
    mis-wirings for witness-tier rows whose Lean body is a typed
    hypothesis-reexport with NO genuine content-bound Python witness).

    Honest rule now: (1) every Lean-companion row must have a
    ``TEST_GATE`` entry; (2) a ``PYTHON_COMPANION`` entry is required
    UNLESS the row's registry ``faithfulness`` is ``typed-witness`` — for
    those the absence is correct and the table renders the explicit
    "typed contract; no content-bound Python witness" marker. A missing
    companion on any OTHER tier (substantive / statement-restricted /
    definitional / forwarder) is still a genuine four-track gap and fails.
    """
    import sys

    import yaml  # noqa: WPS433

    src = str(PROJECT / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    for sub in ("manuscript",):
        p = str(PROJECT / "src" / sub)
        if p not in sys.path:
            sys.path.insert(0, p)
    from manuscript.registry import load_registry  # noqa: E402

    registry = load_registry(PROJECT / "manuscript" / "refs")
    raw = yaml.safe_load((PROJECT / "manuscript" / "refs" / "labels.yaml").read_text(encoding="utf-8"))["theorems"]
    missing: list[str] = []
    for label, theorem in registry.labels.theorems.items():
        if not theorem.has_lean_companion:
            continue
        if label not in generator_module.TEST_GATE:
            missing.append(f"{label} (no TEST_GATE entry)")
        faithfulness = str((raw.get(label) or {}).get("faithfulness", ""))
        if label not in generator_module.PYTHON_COMPANION and faithfulness != "typed-witness":
            missing.append(
                f"{label} (no PYTHON_COMPANION entry; faithfulness={faithfulness!r} "
                "is not 'typed-witness' so a content-bound Python witness IS required)"
            )
    assert not missing, "current theorems with Lean companions but missing four-track wiring: " + ", ".join(missing)


def test_every_current_theorem_has_mathlib_readiness_metadata(generator_module) -> None:
    """Every theorem row must carry a MathlibProofs integration decision.

    The table is deliberately generated from a hand-authored map: if a
    new theorem appears without a readiness, payload, and first-action
    entry, this test fails before the docs can imply an unreviewed
    Mathlib path.
    """
    import sys

    src = str(PROJECT / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from manuscript.registry import load_registry  # noqa: E402

    labels = set(load_registry(PROJECT / "manuscript" / "refs").labels.theorems)
    readiness = generator_module.MATHLIB_READINESS
    assert set(readiness) == labels
    empty = [label for label, row in readiness.items() if len(row) != 3 or not all(str(cell).strip() for cell in row)]
    assert not empty, "empty Mathlib readiness rows: " + ", ".join(empty)
