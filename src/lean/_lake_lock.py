"""Process-wide lock for MathlibProofs ``lake`` subprocesses.

Concurrent ``lake build`` / ``lake env lean`` invocations against the same
``.lake`` tree race and flake under full pytest. A session-scoped file lock
serializes MathlibProofs gate work without blocking unrelated tests.
"""

from __future__ import annotations

import contextlib
import fcntl
from collections.abc import Iterator
from pathlib import Path


def mathlib_proofs_lock_path(project_root: Path) -> Path:
    cache = project_root / "output" / ".cache"
    cache.mkdir(parents=True, exist_ok=True)
    return cache / "mathlib_proofs.lake.lock"


@contextlib.contextmanager
def mathlib_proofs_lock(project_root: Path) -> Iterator[None]:
    lock_path = mathlib_proofs_lock_path(project_root)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            if lock_path.exists() and lock_path.stat().st_size == 0:
                with contextlib.suppress(OSError):
                    lock_path.unlink()
