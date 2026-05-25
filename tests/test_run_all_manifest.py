"""Regression tests for the release pipeline manifest writer."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUN_ALL = PROJECT / "scripts" / "run_all.py"


def _run_all_module():
    spec = importlib.util.spec_from_file_location("run_all", RUN_ALL)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_manifest_excludes_ds_store_but_keeps_real_artifacts(tmp_path: Path) -> None:
    """Release manifests should not inventory ignored OS metadata."""
    output = tmp_path / "output"
    data_dir = output / "data"
    data_dir.mkdir(parents=True)
    legitimate = data_dir / "payload.json"
    legitimate.write_text('{"ok": true}\n', encoding="utf-8")
    (output / ".DS_Store").write_bytes(b"finder metadata")

    mod = _run_all_module()
    manifest = mod._write_manifest(
        project_root=tmp_path,
        run_summary={
            "stages": [{"script": "example.py", "duration_s": 1.25, "returncode": 0}],
            "total_wall_s": 1.25,
        },
    )

    text = manifest.read_text(encoding="utf-8")
    expected_digest = hashlib.sha256(legitimate.read_bytes()).hexdigest()
    assert "`output/data/payload.json`" in text
    assert expected_digest in text
    assert "output/.DS_Store" not in text
