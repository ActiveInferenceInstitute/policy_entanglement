"""End-to-end pipeline runner (library implementation).

Business logic for :doc:`scripts/run_all.py </scripts/run_all>`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from manuscript.readiness import refresh_release_readiness_runtime_budget
from orchestration.executor import ExecutionOutcome, execute_pipeline
from orchestration.manifest import StageSummary, write_manifest
from orchestration.stages import (
    MATHLIB_PROOF_SCRIPTS,
    PARALLEL_STAGE_STEMS,
    PDF_SCRIPTS,
    SCRIPTS,
    StageFlags,
)

# Backward-compatible re-exports for tests and scripts.
from orchestration.executor import StageResult, run_parallel_batch, run_serial, spawn

_SHA256_MAX_BYTES = 8 * 1024 * 1024
_MANIFEST_EXCLUDED_FILENAMES = frozenset({"MANIFEST.md", ".DS_Store"})
_write_manifest = write_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run every project script end-to-end.")
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="NAME",
        help="Skip a script by name (basename, no .py); may be repeated.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="NAME",
        help="Run only the named scripts (no .py); may be repeated.",
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        default=False,
        help="Disable parallel execution of the empirical producer batch.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=6,
        help="Max worker threads for the parallel empirical producer batch (default 6).",
    )
    parser.add_argument(
        "--no-manifest",
        action="store_true",
        default=False,
        help="Skip writing output/MANIFEST.md at end.",
    )
    parser.add_argument(
        "--with-pdf",
        action="store_true",
        default=False,
        help="Run project-local PDF build/validation gates before regression_gate.py.",
    )
    parser.add_argument(
        "--with-mathlib",
        action="store_true",
        default=False,
        help="Run the optional additive lean/MathlibProofs package build after build_lean.py.",
    )
    return parser


def _write_final_manifest(
    *,
    project_root: Path,
    outcome: ExecutionOutcome,
) -> None:
    try:
        manifest_path = write_manifest(
            project_root=project_root,
            run_summary={
                "stages": outcome.stage_summaries,
                "total_wall_s": outcome.total_wall_s,
            },
        )
        print(
            f"\n>>> wrote {manifest_path.relative_to(project_root)} "
            f"({len(outcome.stage_summaries)} stages, {outcome.total_wall_s:.1f}s total)"
        )
    except OSError as exc:
        print(f"!!! could not write MANIFEST.md: {exc}", file=sys.stderr)


def _refresh_readiness_if_needed(outcome: ExecutionOutcome, project_root: Path) -> None:
    if outcome.failures or not outcome.stage_summaries:
        return
    readiness_ran = any(row.get("script") == "readiness_report.py" for row in outcome.stage_summaries)
    if not readiness_ran:
        return
    try:
        refresh_release_readiness_runtime_budget(project_root)
    except OSError as exc:
        print(
            f"!!! could not refresh release_readiness.json runtime budget: {exc}",
            file=sys.stderr,
        )


def main(
    argv: list[str] | None = None,
    *,
    project_root: Path,
    scripts_dir: Path,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    flags = StageFlags(
        skip=frozenset(args.skip),
        only=frozenset(args.only),
        with_pdf=bool(args.with_pdf),
        with_mathlib=bool(args.with_mathlib),
    )
    outcome = execute_pipeline(
        flags=flags,
        scripts=SCRIPTS,
        parallel_stems=PARALLEL_STAGE_STEMS,
        project_root=project_root,
        scripts_dir=scripts_dir,
        parallel=not args.serial,
        max_workers=max(1, int(args.max_workers)),
        write_pre_regression_manifest=not args.no_manifest,
    )
    if not args.no_manifest and outcome.stage_summaries:
        _write_final_manifest(project_root=project_root, outcome=outcome)
    _refresh_readiness_if_needed(outcome, project_root)
    print()
    if outcome.failures:
        print(
            f"FAILED: {len(outcome.failures)} script(s): {', '.join(outcome.failures)}",
            file=sys.stderr,
        )
        return 1
    print(f"All scripts succeeded; outputs validated. Total: {outcome.total_wall_s:.1f}s")
    return 0


__all__ = [
    "MATHLIB_PROOF_SCRIPTS",
    "PARALLEL_STAGE_STEMS",
    "PDF_SCRIPTS",
    "SCRIPTS",
    "StageResult",
    "StageSummary",
    "_MANIFEST_EXCLUDED_FILENAMES",
    "_SHA256_MAX_BYTES",
    "_run_parallel_batch",
    "_run_serial",
    "_spawn",
    "_write_manifest",
    "build_parser",
    "main",
]

# Legacy private aliases expected by tests.
_run_parallel_batch = run_parallel_batch
_run_serial = run_serial
_spawn = spawn
