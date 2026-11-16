"""Regression tests for the release pipeline manifest writer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image

from manuscript.readiness_audit import manifest_stage_timings
from orchestration import run_all

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


def _readiness_fixture(root: Path) -> Path:
    """Run the complete producer against controlled reports and a real PDF."""
    refs = root / "manuscript" / "refs"
    refs.mkdir(parents=True)
    (refs / "labels.yaml").write_text("theorems: {}\nfigures: {}\n", encoding="utf-8")
    reports = root / "output" / "reports"
    reports.mkdir(parents=True)
    (reports / "test_results.json").write_text(
        json.dumps({"project": {
            "total": 3, "passed": 2, "skipped": 1, "failed": 0, "coverage_percent": 97.5,
        }}),
        encoding="utf-8",
    )
    pdf = root / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf"
    pdf.parent.mkdir()
    with Image.new("RGB", (16, 16), "white") as image:
        image.save(pdf, format="PDF")
    scripts = root / "scripts"
    scripts.mkdir()
    (scripts / "readiness_report.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {str(PROJECT / 'src')!r})\n"
        "from manuscript.readiness import write_release_readiness\n"
        "write_release_readiness(Path.cwd())\n",
        encoding="utf-8",
    )
    return scripts


@pytest.mark.parametrize("preexisting", [False, True])
def test_final_manifest_binds_final_readiness_and_current_timings(tmp_path: Path, preexisting: bool) -> None:
    scripts = _readiness_fixture(tmp_path)
    if preexisting:
        run_all._write_manifest(
            project_root=tmp_path,
            run_summary={
                "stages": [run_all.StageSummary(script="previous.py", duration_s=999.0, returncode=0)],
                "total_wall_s": 999.0,
            },
        )
    assert run_all.main(["--serial", "--only", "readiness_report"], project_root=tmp_path, scripts_dir=scripts) == 0
    readiness = tmp_path / "output" / "reports" / "release_readiness.json"
    content = readiness.read_bytes()
    payload = json.loads(content)
    timings = manifest_stage_timings(project_root=tmp_path)
    assert payload["runtime_budget"] == timings
    assert [stage["script"] for stage in timings["stages"]] == ["readiness_report.py"]
    assert payload["tests"]["total"] == 3
    assert payload["tests"]["passed"] == 2
    assert payload["coverage"]["percent"] == 97.5
    manifest = (tmp_path / "output" / "MANIFEST.md").read_text(encoding="utf-8")
    for name in ("release_readiness.json", "release_readiness.md", "release_note.md", "release_index.md"):
        artifact = tmp_path / "output" / "reports" / name
        artifact_bytes = artifact.read_bytes()
        row = next(line for line in manifest.splitlines() if f"`output/reports/{name}`" in line)
        assert f"| {len(artifact_bytes)} |" in row
        assert hashlib.sha256(artifact_bytes).hexdigest() in row
    for name in ("release_readiness.md", "release_note.md"):
        rendered = (tmp_path / "output" / "reports" / name).read_text()
        assert "readiness_report.py" in rendered.split("## Runtime Budget", 1)[1]
        assert "previous.py" not in rendered


@pytest.mark.parametrize("preexisting", [False, True])
def test_no_manifest_keeps_manifest_bytes_untouched(tmp_path: Path, preexisting: bool) -> None:
    scripts = _readiness_fixture(tmp_path)
    manifest = tmp_path / "output" / "MANIFEST.md"
    original = b"operator-owned historical inventory\n"
    if preexisting:
        manifest.parent.mkdir(exist_ok=True)
        manifest.write_bytes(original)
    assert run_all.main(
        ["--serial", "--only", "readiness_report", "--no-manifest"],
        project_root=tmp_path,
        scripts_dir=scripts,
    ) == 0
    if preexisting:
        assert manifest.read_bytes() == original
    else:
        assert not manifest.exists()
    payload = json.loads((tmp_path / "output/reports/release_readiness.json").read_text())
    assert payload["tests"]["passed"] == 2


def test_final_readiness_missing_input_fails_pipeline(tmp_path: Path) -> None:
    scripts = _readiness_fixture(tmp_path)
    with (scripts / "readiness_report.py").open("a", encoding="utf-8") as stream:
        stream.write("(Path.cwd() / 'output/reports/test_results.json').unlink()\n")
    assert run_all.main(
        ["--serial", "--only", "readiness_report"], project_root=tmp_path, scripts_dir=scripts,
    ) == 1
