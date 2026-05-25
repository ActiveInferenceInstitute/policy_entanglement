#!/usr/bin/env python3
"""Write a reviewer-facing release-readiness summary from live artifacts.

Thin orchestrator: business logic lives in :mod:`manuscript.readiness`.
This script binds ``PROJECT_ROOT`` and re-exports the test-facing
helpers (``tests/test_readiness_report.py`` loads this module via
``importlib`` and asserts on the underscore-prefixed names below; keep
that surface stable).
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from manuscript import readiness as _r  # noqa: E402

# ---------------------------------------------------------------------------
# Pure helper re-exports (no project_root dependency).
# ---------------------------------------------------------------------------
FORBIDDEN_MATHLIB_LOCAL_TOKENS = _r.FORBIDDEN_MATHLIB_LOCAL_TOKENS
MANIFEST_STAGE_RE = _r.MANIFEST_STAGE_RE
MANIFEST_TOTAL_RE = _r.MANIFEST_TOTAL_RE
_status_counts = _r._status_counts
_as_float = _r._as_float
_runtime_stage_dicts = _r._runtime_stage_dicts
_runtime_failed_stage_names = _r._runtime_failed_stage_names
_format_stage_list = _r._format_stage_list
_optional_json = _r._optional_json


# ---------------------------------------------------------------------------
# Project-root-bound wrappers. The test suite calls these with the
# signatures shown below; the wrappers forward to the src module with
# ``PROJECT_ROOT`` bound.
# ---------------------------------------------------------------------------


def _git_status_lines() -> list[str]:
    return _r._git_status_lines(PROJECT_ROOT)


def _theorem_status_counts() -> dict[str, int]:
    return _r._theorem_status_counts(PROJECT_ROOT)


def _manifest_stage_timings(manifest_path: Path | None = None) -> dict[str, object]:
    return _r._manifest_stage_timings(manifest_path, project_root=PROJECT_ROOT)


def _mathlib_proofs_status(runtime_budget: dict[str, object] | None = None) -> dict[str, object]:
    return _r._mathlib_proofs_status(PROJECT_ROOT, runtime_budget)


def _registered_figure_paths() -> set[str]:
    return _r._registered_figure_paths(PROJECT_ROOT)


def _figure_audit(figures: list[Path]) -> dict[str, object]:
    return _r._figure_audit(PROJECT_ROOT, figures)


def _pdf_artifact_audit(status) -> dict[str, object]:
    return _r._pdf_artifact_audit(PROJECT_ROOT, status)


def _write_release_note(
    *,
    status,
    figures: list[Path],
    generated_manuscript: list[Path],
    manifest_present: bool,
    out_dir: Path | None = None,
) -> Path:
    return _r._write_release_note(
        PROJECT_ROOT,
        status=status,
        figures=figures,
        generated_manuscript=generated_manuscript,
        manifest_present=manifest_present,
        out_dir=out_dir,
    )


def _write_readiness_json(
    *,
    status,
    figures: list[Path],
    generated_manuscript: list[Path],
    manifest_present: bool,
    out_dir: Path | None = None,
) -> Path:
    return _r._write_readiness_json(
        PROJECT_ROOT,
        status=status,
        figures=figures,
        generated_manuscript=generated_manuscript,
        manifest_present=manifest_present,
        out_dir=out_dir,
    )


def _write_release_index(
    *,
    release_note: Path,
    readiness_json: Path,
    readiness_md: Path,
    manifest: Path,
    out_dir: Path | None = None,
) -> Path:
    return _r._write_release_index(
        PROJECT_ROOT,
        release_note=release_note,
        readiness_json=readiness_json,
        readiness_md=readiness_md,
        manifest=manifest,
        out_dir=out_dir,
    )


def main() -> int:
    try:
        out = _r.write_release_readiness(PROJECT_ROOT)
    except (FileNotFoundError, RuntimeError, KeyError) as exc:
        raise SystemExit(
            "release readiness requires a built PDF and live test artifacts; "
            "run `uv run python scripts/build_pdf.py && uv run python scripts/validate_pdf.py` "
            f"after the test/report gates. Details: {exc}"
        ) from exc
    print(out.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
