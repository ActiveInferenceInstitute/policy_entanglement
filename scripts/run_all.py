#!/usr/bin/env python3
"""Thin CLI wrapper for the end-to-end pipeline runner.

Business logic lives in :mod:`orchestration.run_all` (under ``src/``). This
script bootstraps the project's ``src/`` subpackages onto :data:`sys.path`
and dispatches to the library entry point with this project's paths.

Usage::

    uv run python scripts/run_all.py
    uv run python scripts/run_all.py --skip parameter_sweep
    uv run python scripts/run_all.py --serial
    uv run python scripts/run_all.py --with-pdf
    uv run python scripts/run_all.py --with-mathlib
    uv run python scripts/run_all.py --with-pdf --with-mathlib

The module-level re-exports below preserve the tests' contract
(``tests/test_run_all_manifest.py`` loads this file via importlib and calls
``_write_manifest`` directly; ``tests/test_status_docs.py`` and
``tests/test_manuscript_variables_pipeline.py`` access ``SCRIPTS`` /
``PDF_SCRIPTS`` / ``MATHLIB_PROOF_SCRIPTS`` as module attributes).
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent

sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from orchestration.run_all import (  # noqa: E402,F401
    _MANIFEST_EXCLUDED_FILENAMES,
    _SHA256_MAX_BYTES,
    MATHLIB_PROOF_SCRIPTS,
    PARALLEL_STAGE_STEMS,
    PDF_SCRIPTS,
    SCRIPTS,
    StageResult,
    StageSummary,
    _write_manifest,
    build_parser,
)
from orchestration.run_all import (  # noqa: E402
    _run_parallel_batch as _lib_run_parallel_batch,
)
from orchestration.run_all import (  # noqa: E402
    _run_serial as _lib_run_serial,
)
from orchestration.run_all import (  # noqa: E402
    _spawn as _lib_spawn,
)
from orchestration.run_all import (  # noqa: E402
    main as _lib_main,
)


def _spawn(script: str, *, capture: bool) -> StageResult:
    """Project-bound thin wrapper preserving the legacy call shape."""
    return _lib_spawn(script, capture=capture, scripts_dir=THIS_DIR, project_root=PROJECT_ROOT)


def _run_serial(script: str) -> int:
    """Project-bound thin wrapper preserving the legacy call shape."""
    return _lib_run_serial(script, scripts_dir=THIS_DIR, project_root=PROJECT_ROOT)


def _run_parallel_batch(scripts: list[str], *, max_workers: int) -> list[StageResult]:
    """Project-bound thin wrapper preserving the legacy call shape."""
    return _lib_run_parallel_batch(
        scripts,
        max_workers=max_workers,
        scripts_dir=THIS_DIR,
        project_root=PROJECT_ROOT,
    )


def main(argv: list[str] | None = None) -> int:
    return _lib_main(argv, project_root=PROJECT_ROOT, scripts_dir=THIS_DIR)


if __name__ == "__main__":
    sys.exit(main())
