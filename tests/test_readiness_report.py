"""Tests for the release-readiness report script helpers."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from manuscript import readiness as readiness_mod

PROJECT = Path(__file__).resolve().parent.parent


def _seed_labels_yaml(project_root: Path) -> None:
    refs = project_root / "manuscript" / "refs"
    refs.mkdir(parents=True, exist_ok=True)
    shutil.copy(PROJECT / "manuscript" / "refs" / "labels.yaml", refs / "labels.yaml")


def test_status_counts_groups_git_short_codes() -> None:
    counts = readiness_mod._status_counts([" M README.md", "A  file.txt", " D old.txt", "?? new.txt"])
    assert counts["modified"] == 1
    assert counts["added"] == 1
    assert counts["deleted"] == 1
    assert counts["untracked"] == 1


def test_optional_json_returns_empty_dict_for_missing_file(tmp_path: Path) -> None:
    assert readiness_mod._optional_json(tmp_path / "missing.json") == {}


def test_manifest_stage_timings_and_mathlib_status_parse_live_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "MANIFEST.md"
    manifest.write_text(
        "\n".join(
            [
                "| Stage | Wall time (s) | Status |",
                "|---|---:|---|",
                "| `build_lean.py` | 1.25 | OK |",
                "| `build_mathlib_proofs.py` | 2.50 | OK |",
                "**Total wall-clock**: 3.75s",
            ]
        ),
        encoding="utf-8",
    )
    budget = readiness_mod._manifest_stage_timings(manifest, project_root=PROJECT)
    assert budget["manifest_present"] is True
    assert budget["total_wall_s"] == 3.75
    assert budget["stage_count"] == 2
    assert budget["failed_stages"] == []
    assert budget["slowest_stages"][0]["script"] == "build_mathlib_proofs.py"

    mathlib = readiness_mod._mathlib_proofs_status(PROJECT, budget)
    assert mathlib["present"] is True
    assert mathlib["proofSliceVersion"] == 3
    assert mathlib["theorem_count"] >= 4
    assert mathlib["build_checked"] is True
    assert mathlib["build_status"] == "passed"
    assert mathlib["hygiene_clean"] is True


def test_reconcile_runtime_budget_clears_stale_failures_when_gates_green() -> None:
    budget = {"failed_stages": ["readiness_report.py"], "stage_count": 1}
    test_results = {"total_failed": 0}

    class _Status:
        tests_failed = 0

    reconciled = readiness_mod._reconcile_runtime_budget(budget, status=_Status(), test_results=test_results)
    assert reconciled["failed_stages"] == []


def test_release_note_writer_uses_live_snapshot(tmp_path: Path) -> None:
    _seed_labels_yaml(tmp_path)

    class _Status:
        tests_total = 3
        tests_passed = 2
        tests_skipped = 1
        tests_failed = 0
        test_summary = "3 collected; 2 passed + 1 skipped"
        coverage_percent = 97.5
        pdf_pages = 12
        pdf_size_bytes = 1_230_000
        pdf_size_mb = 1.23
        pdf_summary = "12 pages, 1.23 MB"

    out = readiness_mod._write_release_note(
        tmp_path,
        status=_Status(),
        figures=[tmp_path / "a.png", tmp_path / "b.png"],
        generated_manuscript=[tmp_path / "m.md"],
        manifest_present=True,
        out_dir=tmp_path,
    )
    assert out.parent == tmp_path
    text = out.read_text(encoding="utf-8")
    assert "Reviewer Release Note" in text
    assert "3 collected; 2 passed + 1 skipped" in text
    assert "`proved`" in text
    assert "`roadmap`" in text

    json_path = readiness_mod._write_readiness_json(
        tmp_path,
        status=_Status(),
        figures=[tmp_path / "a.png", tmp_path / "b.png"],
        generated_manuscript=[tmp_path / "m.md"],
        manifest_present=True,
        out_dir=tmp_path,
    )
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["tests"]["total"] == 3
    assert payload["tests"]["failed"] == 0
    assert payload["artifacts"]["png_figures"] == 2
    assert payload["artifacts"]["rendered_manuscript_markdown"] == 1
    assert "theorems" in payload
    assert payload["mathlib_proofs"]["claim_status"].startswith("separate Mathlib package")
    assert "runtime_budget" in payload
    assert "figure_audit" in payload
    assert "pdf_audit" in payload

    index = readiness_mod._write_release_index(
        tmp_path,
        release_note=out,
        readiness_json=json_path,
        readiness_md=tmp_path / "release_readiness.md",
        manifest=tmp_path / "MANIFEST.md",
    )
    assert "Reviewer Release Index" in index.read_text(encoding="utf-8")
