"""Structured run logger for the pymdp simulation harness.

Emits one JSONL record per (script, λ, observation) call to the
coupled-policy posterior, capturing:

* timestamp (UTC, ISO-8601),
* script and section (caller-provided),
* hyperparameters used (K, γ, λ, seed),
* shape signatures of pymdp's per-stream outputs,
* scalar observables (TC, joint entropy, vfe_total, coupling term),
* runtime in milliseconds.

The output file lives at ``output/logs/pymdp_runs.jsonl`` (project-
relative) so it can be inspected with ``jq``, diffed across runs,
and re-processed by downstream tools.

The logger is append-only unless a caller explicitly starts with
``RunLogger.fresh()``. The canonical `simulate_pymdp.py` pipeline entry
does this so `output/logs/pymdp_runs.jsonl` describes the current run
with the current schema.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass
class RunLogger:
    """Append-only JSONL logger for pymdp runs.

    Use `with logger.timed(event=...) as ctx: ctx.update(...)` to wrap
    a measured block; the logger fills in `runtime_ms` automatically.
    """

    path: Path
    enabled: bool = True

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_project_root(
        cls,
        project_root: Path,
        *,
        relative_path: str = "output/logs/pymdp_runs.jsonl",
        enabled: bool = True,
    ) -> RunLogger:
        return cls(path=project_root / relative_path, enabled=enabled)

    def fresh(self) -> None:
        """Truncate the log file (start-of-pipeline convenience)."""
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("")

    def emit(self, record: Mapping[str, Any]) -> None:
        """Append a single JSON record to the log."""
        if not self.enabled:
            return
        full = {"timestamp": _now_iso(), **dict(record)}
        with self.path.open("a") as fh:
            fh.write(json.dumps(full, separators=(",", ":"), default=_json_default) + "\n")

    @contextmanager
    def timed(self, **base: Any) -> Iterator[TimedRecord]:
        """Open a record builder; close it on exit and emit with runtime."""
        rec = TimedRecord(parent=self, base=dict(base), start=time.perf_counter())
        try:
            yield rec
        finally:
            rec.close()


@dataclass
class TimedRecord:
    """In-progress record builder yielded by :meth:`RunLogger.timed`.

    Call :meth:`update` to merge fields and :meth:`set_status` to
    annotate success / failure; the context manager closes and emits
    the record on `__exit__`.
    """

    parent: RunLogger
    base: dict[str, Any]
    start: float
    extras: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"
    closed: bool = False

    def update(self, **fields: Any) -> None:
        self.extras.update(fields)

    def set_status(self, status: str) -> None:
        self.status = status

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        runtime_ms = (time.perf_counter() - self.start) * 1000.0
        record: dict[str, Any] = {**self.base, **self.extras}
        record["runtime_ms"] = round(runtime_ms, 3)
        record["status"] = self.status
        self.parent.emit(record)


def _json_default(o: Any) -> Any:
    """JSON fallback serialiser for numpy types + Path.

    Note (RedTeam Methods L5, 2026-05-20): numpy is a hard project
    dependency, so the prior ``try/except ImportError`` block was
    impossible-error handling.  Removed for clarity.
    """
    import numpy as np  # numpy is a hard dependency of every other module

    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"unsupported type: {type(o).__name__}")


# ---------------------------------------------------------------------------
# Convenience: a default project-root logger configurable via env var.
# ---------------------------------------------------------------------------


def default_logger(project_root: Path) -> RunLogger:
    """Project-root logger that respects ``PYMDP_RUN_LOG_DISABLED=1``."""
    enabled = os.environ.get("PYMDP_RUN_LOG_DISABLED", "0") != "1"
    return RunLogger.from_project_root(project_root, enabled=enabled)
