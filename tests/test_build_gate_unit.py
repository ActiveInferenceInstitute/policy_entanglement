"""Unit tests for :mod:`lean.build_gate` scanners (no ``lake`` required)."""

from __future__ import annotations

import json
from pathlib import Path

from lean.build_gate import (
    count_axioms,
    count_disallowed,
    count_mathlib_imports,
    count_sorries,
    emit_infra_log,
    scrape_lake_warnings,
)

PROJECT = Path(__file__).resolve().parent.parent


def test_scrape_lake_warnings_structured_and_fallback() -> None:
    stderr = "foo.lean:12:3: warning: unused variable\nwarning: build completed with warnings\nnoise line\n"
    rows = scrape_lake_warnings(stderr)
    assert len(rows) == 2
    assert rows[0]["file"] == "foo.lean"
    assert rows[0]["line"] == "12"
    assert rows[1]["message"] == "build completed with warnings"


def test_emit_infra_log_writes_jsonl(tmp_path: Path) -> None:
    log_path = tmp_path / "infra.jsonl"
    emit_infra_log([{"source": "lake-build", "level": "warning", "message": "x"}], log_path=log_path)
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["message"] == "x"
    assert "timestamp" in payload


def test_count_sorries_skips_comments_and_docstrings(tmp_path: Path) -> None:
    lean_dir = tmp_path / "lean"
    pkg = lean_dir / "ActinfPolicyEntanglement"
    pkg.mkdir(parents=True)
    (pkg / "Bad.lean").write_text(
        "-- sorry in comment only\n/- doc sorry token -/\ntheorem t : True := by sorry\n",
        encoding="utf-8",
    )
    exclude = lean_dir / "MathlibProofs"
    hits = count_sorries(lean_dir, exclude_subtree=exclude)
    assert len(hits) == 1
    assert "sorry" in hits[0][2]


def test_count_axioms_and_disallowed(tmp_path: Path) -> None:
    lean_dir = tmp_path / "lean"
    pkg = lean_dir / "ActinfPolicyEntanglement"
    pkg.mkdir(parents=True)
    (pkg / "Bad.lean").write_text(
        "axiom cheat : True\nunsafe def bad : Nat := 0\n",
        encoding="utf-8",
    )
    exclude = lean_dir / "MathlibProofs"
    assert len(count_axioms(lean_dir, exclude_subtree=exclude)) == 1
    assert len(count_disallowed(lean_dir, exclude_subtree=exclude)) == 1


def test_count_mathlib_imports_flags_boundary_package(tmp_path: Path) -> None:
    lean_dir = tmp_path / "lean"
    root = lean_dir / "ActinfPolicyEntanglement"
    root.mkdir(parents=True)
    bad = root / "Import.lean"
    bad.write_text("import Mathlib.Data.Nat.Basic\n", encoding="utf-8")
    hits = count_mathlib_imports(
        import_roots=(root,),
        root_files=(lean_dir / "Missing.lean",),
    )
    assert len(hits) == 1
    assert "Mathlib" in hits[0][2]


def test_build_gate_scanners_clean_on_real_boundary_fragment() -> None:
    lean_dir = PROJECT / "lean"
    exclude = lean_dir / "MathlibProofs"
    assert count_sorries(lean_dir, exclude_subtree=exclude) == []
    assert count_axioms(lean_dir, exclude_subtree=exclude) == []
    assert count_disallowed(lean_dir, exclude_subtree=exclude) == []
