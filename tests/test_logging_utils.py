"""Tests for `simulation.logging_utils` — the structured pymdp run logger.

JSONL emission, schema, runtime measurement, status propagation,
fresh / append modes, env-var disable.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from simulation.logging_utils import RunLogger, default_logger


def _records(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def test_emit_writes_single_jsonl_record(tmp_path: Path) -> None:
    log = RunLogger(path=tmp_path / "runs.jsonl")
    log.emit({"event": "ping", "value": 42})
    rec = _records(log.path)
    assert len(rec) == 1
    assert rec[0]["event"] == "ping"
    assert rec[0]["value"] == 42
    assert "timestamp" in rec[0]


def test_emit_appends_across_calls(tmp_path: Path) -> None:
    log = RunLogger(path=tmp_path / "runs.jsonl")
    log.emit({"event": "first"})
    log.emit({"event": "second"})
    rec = _records(log.path)
    assert [r["event"] for r in rec] == ["first", "second"]


def test_fresh_truncates(tmp_path: Path) -> None:
    log = RunLogger(path=tmp_path / "runs.jsonl")
    log.emit({"event": "x"})
    log.fresh()
    log.emit({"event": "y"})
    rec = _records(log.path)
    assert [r["event"] for r in rec] == ["y"]


def test_disabled_logger_writes_nothing(tmp_path: Path) -> None:
    p = tmp_path / "runs.jsonl"
    log = RunLogger(path=p, enabled=False)
    log.emit({"event": "ignored"})
    assert not p.exists()


def test_timed_records_runtime_and_ok_status(tmp_path: Path) -> None:
    log = RunLogger(path=tmp_path / "runs.jsonl")
    with log.timed(section="probe", grid_points=21) as ctx:
        time.sleep(0.005)
        ctx.update(extra="payload")
    rec = _records(log.path)[0]
    assert rec["section"] == "probe"
    assert rec["grid_points"] == 21
    assert rec["extra"] == "payload"
    assert rec["status"] == "ok"
    assert rec["runtime_ms"] >= 5.0


def test_timed_propagates_error_status(tmp_path: Path) -> None:
    log = RunLogger(path=tmp_path / "runs.jsonl")
    with pytest.raises(RuntimeError), log.timed(section="probe") as ctx:
        ctx.set_status("error")
        raise RuntimeError("boom")
    rec = _records(log.path)[0]
    assert rec["status"] == "error"


def test_timed_handles_numpy_payload(tmp_path: Path) -> None:
    """Default JSON serialiser must round-trip numpy types."""
    import numpy as np

    log = RunLogger(path=tmp_path / "runs.jsonl")
    with log.timed(section="np") as ctx:
        ctx.update(arr=np.array([1.0, 2.0, 3.0]), x=np.float64(1.5))
    rec = _records(log.path)[0]
    assert rec["arr"] == [1.0, 2.0, 3.0]
    assert rec["x"] == 1.5


def test_default_logger_respects_env_var(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYMDP_RUN_LOG_DISABLED", "1")
    log = default_logger(tmp_path)
    assert log.enabled is False
    log.emit({"event": "should-not-write"})
    assert not (tmp_path / "output" / "logs" / "pymdp_runs.jsonl").exists()


def test_default_logger_creates_parent_directory(tmp_path: Path) -> None:
    log = default_logger(tmp_path)
    log.emit({"event": "ping"})
    assert (tmp_path / "output" / "logs" / "pymdp_runs.jsonl").exists()


def test_timed_record_close_is_idempotent(tmp_path: Path) -> None:
    """Closing a TimedRecord twice must not emit a second JSON record."""
    log = RunLogger(path=tmp_path / "runs.jsonl")
    with log.timed(event="test") as rec:
        rec.update(step=1)
    # Force a second close — must be a no-op (guard branch on line 112).
    rec.close()
    lines = (tmp_path / "runs.jsonl").read_text().splitlines()
    assert len(lines) == 1


def test_json_default_raises_for_unsupported_type(tmp_path: Path) -> None:
    """_json_default must raise TypeError for objects it cannot serialise."""
    import json

    from simulation.logging_utils import _json_default

    with pytest.raises(TypeError, match="unsupported type"):
        json.dumps({"v": object()}, default=_json_default)


def test_json_default_serialises_numpy_scalar(tmp_path: Path) -> None:
    """_json_default serialises np.integer and np.floating scalars via .item()."""
    import json

    import numpy as np

    from simulation.logging_utils import _json_default

    result = json.dumps({"v": np.int64(42)}, default=_json_default)
    assert json.loads(result)["v"] == 42


def test_json_default_serialises_path(tmp_path: Path) -> None:
    """_json_default serialises pathlib.Path objects as strings."""
    import json

    from simulation.logging_utils import _json_default

    p = tmp_path / "some_file.txt"
    result = json.dumps({"path": p}, default=_json_default)
    assert json.loads(result)["path"] == str(p)


def test_fresh_is_noop_when_disabled(tmp_path: Path) -> None:
    """RunLogger.fresh() on a disabled logger must not create any file."""
    path = tmp_path / "noop.jsonl"
    log = RunLogger(path=path, enabled=False)
    log.fresh()  # must not create the file (disabled branch)
    assert not path.exists()
