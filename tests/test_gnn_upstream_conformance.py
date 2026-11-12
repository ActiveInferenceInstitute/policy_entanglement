"""Upstream-parser conformance test for the project-owned GNN parser.

The project-owned parser (`src/gnn/parser.py`) is cited-not-vendored: it never
imports upstream GNN code.  This test makes the "spec-conformant" claim
checkable by running the **real upstream parser**
(`gnn.parsers.markdown_parser.MarkdownGNNParser`) of the pinned GNN release
(`gnn/upstream.json`) against every shipped ``gnn/*.gnn.md`` spec and comparing
normalized digests.  Any divergence fails.

The upstream parser runs under the GNN checkout's own interpreter, with the
pinned commit's ``src/gnn`` extracted from Git onto ``PYTHONPATH`` — so the
bytes exercised are the pinned release's bytes, not the live working tree's
(the checkout may legitimately carry in-progress edits).  The checkout is
treated as read-only: this test only runs ``git archive`` / ``git show`` /
``git cat-file``.

When the checkout or its ``.venv`` is unavailable the test skips with an
explicit reason; setting ``POLICY_ENTANGLEMENT_GNN_ROOT`` selects a checkout
explicitly (and then an unavailable checkout is a failure, not a skip).
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from gnn.parser import parse_gnn, parse_gnn_file
from gnn.upstream import (
    DIGEST_DRIVER_SOURCE,
    ENV_UPSTREAM_ROOT,
    PARSER_RELATIVE_PATH,
    UpstreamPin,
    UpstreamPinError,
    checkout_available,
    default_gnn_root,
    digest_divergences,
    gnn_checkout_python,
    load_upstream_pin,
    normalize_upstream_digest,
    resolve_gnn_root,
    spec_digest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIN_PATH = PROJECT_ROOT / "gnn" / "upstream.json"
GNN_DIR = PROJECT_ROOT / "gnn"
SHIPPED_SPECS = sorted(GNN_DIR.glob("*.gnn.md"))

#: The canonical workstream pin.  Bumping it is a deliberate act: this test
#: pins the pin, so a silent re-pin cannot pass unnoticed.
CANONICAL_TAG = "v5.0.3"
CANONICAL_COMMIT = "8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1"


@dataclass(frozen=True)
class UpstreamRun:
    """One execution of the pinned upstream parser over the shipped specs."""

    pin: UpstreamPin
    root: Path
    payload: dict[str, Any]
    mutant: Path
    extract_dir: Path


@pytest.fixture(scope="module")
def upstream_run(tmp_path_factory: pytest.TempPathFactory) -> UpstreamRun:
    """Execute the pinned upstream parser on every shipped spec + a leniency mutant."""
    pin = load_upstream_pin(PIN_PATH)
    root = resolve_gnn_root(PROJECT_ROOT)
    explicit = ENV_UPSTREAM_ROOT in os.environ
    if not checkout_available(root):
        message = (
            f"upstream GNN checkout unavailable at {root} (needs {PARSER_RELATIVE_PATH} "
            f"and .venv/bin/python); set {ENV_UPSTREAM_ROOT} to select one"
        )
        if explicit:
            pytest.fail(message)
        pytest.skip(message)

    presence = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{pin.commit}^{{commit}}"],
        capture_output=True,
        text=True,
    )
    assert presence.returncode == 0, (
        f"pinned commit {pin.commit} is not present in {root}; fetch the pinned release before "
        "running the upstream conformance check"
    )

    extract_dir = tmp_path_factory.mktemp("gnn_upstream_pin")
    archive = subprocess.run(
        ["git", "-C", str(root), "archive", pin.commit, "src/gnn"],
        check=True,
        capture_output=True,
    )
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as stream:
        if sys.version_info >= (3, 12):
            stream.extractall(extract_dir, filter="data")
        else:  # pragma: no cover - the documented gate runs a modern interpreter
            stream.extractall(extract_dir)

    # Leniency mutant: the spaced section name is ignored by the upstream
    # parser (canonical inventory: `## ActInfOntologyAnnotation`), while the
    # project parser accepts both spellings.  Used as the non-vacuity control.
    mutant = extract_dir / "spaced_ontology.gnn.md"
    mutant.write_text(
        (GNN_DIR / "bernoulli_toy.gnn.md")
        .read_text(encoding="utf-8")
        .replace("## ActInfOntologyAnnotation", "## ActInf Ontology Annotation"),
        encoding="utf-8",
    )

    spec_paths = [str(path.resolve()) for path in SHIPPED_SPECS] + [str(mutant)]
    env = {**os.environ, "PYTHONPATH": str(extract_dir / "src")}
    command = [
        str(gnn_checkout_python(root)),
        "-c",
        DIGEST_DRIVER_SOURCE,
        "--module",
        pin.parser_module,
        "--class-name",
        pin.parser_class,
    ]
    for spec in spec_paths:
        command += ["--spec", spec]
    proc = subprocess.run(command, capture_output=True, text=True, env=env, cwd=extract_dir)
    assert proc.returncode == 0, f"upstream digest driver failed:\n{proc.stderr}"

    return UpstreamRun(
        pin=pin,
        root=root,
        payload=json.loads(proc.stdout),
        mutant=mutant,
        extract_dir=extract_dir,
    )


def test_pin_file_names_the_canonical_release() -> None:
    """The shipped pin is the canonical workstream pin (v5.0.3)."""
    pin = load_upstream_pin(PIN_PATH)
    assert pin.repository == "https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation"
    assert pin.tag == CANONICAL_TAG
    assert pin.commit == CANONICAL_COMMIT
    assert pin.parser_module == "gnn.parsers.markdown_parser"
    assert pin.parser_class == "MarkdownGNNParser"
    assert pin.schema == "gnn-importer-pin/v1"
    assert pin.recorded is not None


def test_pin_loader_rejects_malformed_pins(tmp_path: Path) -> None:
    """Every malformed pin shape is refused with a named error."""
    valid = PIN_PATH.read_text(encoding="utf-8")
    cases = {
        "missing_key.json": json.dumps(
            {
                "repository": "https://github.com/x/y",
                "tag": "v5.0.3",
                "commit": CANONICAL_COMMIT,
                "parser_module": "gnn.parsers.markdown_parser",
            }
        ),
        "extra_key.json": json.dumps(json.loads(valid) | {"extra": "nope"}),
        "bad_schema.json": json.dumps(json.loads(valid) | {"schema": "repo-specific-pin/v1"}),
        "bad_recorded.json": json.dumps(json.loads(valid) | {"recorded": "2026-13-01"}),
        "short_recorded.json": json.dumps(json.loads(valid) | {"recorded": "2026-11"}),
        "duplicate_key.json": valid.replace('"tag": "v5.0.3",', '"tag": "v5.0.3", "tag": "v5.0.3",'),
        "bad_repo.json": valid.replace("https://github.com/", "https://example.com/"),
        "bad_tag.json": valid.replace('"v5.0.3"', '"5.0.3"'),
        "bad_commit.json": valid.replace(CANONICAL_COMMIT, "not-a-commit"),
        "bad_module.json": valid.replace("gnn.parsers.markdown_parser", "markdown_parser"),
        "bad_class.json": valid.replace("MarkdownGNNParser", "Markdown GNN Parser"),
        "not_json.json": "{not json",
    }
    for name, text in cases.items():
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        with pytest.raises(UpstreamPinError):
            load_upstream_pin(path)


def test_pin_loader_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(UpstreamPinError, match="cannot read upstream pin"):
        load_upstream_pin(tmp_path / "absent.json")


def test_resolve_gnn_root_honours_explicit_selection(tmp_path: Path) -> None:
    """An explicit selection is final; an empty selection is refused."""
    chosen = tmp_path / "checkout"
    assert resolve_gnn_root(PROJECT_ROOT, {ENV_UPSTREAM_ROOT: str(chosen)}) == chosen.resolve()
    with pytest.raises(UpstreamPinError, match="must not be empty"):
        resolve_gnn_root(PROJECT_ROOT, {ENV_UPSTREAM_ROOT: "   "})
    assert resolve_gnn_root(PROJECT_ROOT, {}) == default_gnn_root(PROJECT_ROOT)
    assert gnn_checkout_python(chosen) == chosen / ".venv" / "bin" / "python"
    assert checkout_available(tmp_path / "absent") is False


def test_upstream_parser_ran_from_the_pinned_commit(upstream_run: UpstreamRun) -> None:
    """The executed parser bytes are the pinned commit's bytes, from the pinned tree."""
    parser_info = upstream_run.payload["parser"]
    assert parser_info["module"] == upstream_run.pin.parser_module
    assert parser_info["class"] == upstream_run.pin.parser_class
    assert parser_info["gnn_version"] == "5.0.3"
    assert Path(parser_info["file"]).is_relative_to(upstream_run.extract_dir)

    pinned_blob = subprocess.run(
        ["git", "-C", str(upstream_run.root), "show", f"{upstream_run.pin.commit}:{PARSER_RELATIVE_PATH}"],
        check=True,
        capture_output=True,
    ).stdout
    assert parser_info["sha256"] == hashlib.sha256(pinned_blob).hexdigest()


def test_upstream_parser_accepts_every_shipped_spec(upstream_run: UpstreamRun) -> None:
    """The upstream parser parses every shipped spec without errors or warnings."""
    for path in SHIPPED_SPECS:
        entry = upstream_run.payload["specs"][str(path.resolve())]
        assert entry["diagnostics"]["success"] is True, path.name
        assert entry["diagnostics"]["errors"] == [], path.name
        assert entry["diagnostics"]["warnings"] == [], path.name


@pytest.mark.parametrize("spec", SHIPPED_SPECS, ids=lambda path: path.name)
def test_project_parser_digest_matches_upstream(upstream_run: UpstreamRun, spec: Path) -> None:
    """The project-owned parser and the real upstream parser agree on every shipped spec."""
    project = spec_digest(parse_gnn_file(spec))
    upstream = normalize_upstream_digest(upstream_run.payload["specs"][str(spec.resolve())])
    assert digest_divergences(project, upstream) == []


def test_conformance_check_discriminates_on_the_leniency_mutant(upstream_run: UpstreamRun) -> None:
    """NON-VACUITY: the spaced ontology section diverges between the two parsers.

    The upstream parser silently ignores the spaced section name while the
    project parser accepts it (documented alias), so the comparison must report
    a divergence — proving the conformance check reads the parsed content
    rather than trivially agreeing.
    """
    project = spec_digest(parse_gnn_file(upstream_run.mutant))
    upstream = normalize_upstream_digest(upstream_run.payload["specs"][str(upstream_run.mutant)])
    assert project["ontology"], "project parser did not read the spaced ontology section"
    assert upstream["ontology"] == {}, "upstream parser unexpectedly read the spaced ontology section"
    issues = digest_divergences(project, upstream)
    assert issues and any("ontology" in issue for issue in issues)


def test_digest_comparison_rejects_malformed_digests() -> None:
    """A malformed digest field is refused instead of silently compared."""
    with pytest.raises(UpstreamPinError, match="must be a mapping"):
        digest_divergences({"variables": 3}, {})


def test_digest_comparison_flags_every_field_family() -> None:
    """The pure comparator reports drift in each digest field family."""
    base = spec_digest(parse_gnn_file(GNN_DIR / "bernoulli_toy.gnn.md"))
    other = spec_digest(parse_gnn_file(GNN_DIR / "k_stream_ensemble.gnn.md"))
    issues = digest_divergences(base, other)
    assert issues, "comparator found no divergence between two different models"
    for field in ("model_name", "variables", "connections", "ontology", "model_parameters", "parameters"):
        assert any(field in issue for issue in issues), field


def test_normalize_upstream_digest_rejects_incomplete_payloads() -> None:
    """Incomplete upstream payloads are refused instead of silently compared."""
    with pytest.raises(UpstreamPinError, match="missing fields"):
        normalize_upstream_digest({"model_name": "m"})
    with pytest.raises(UpstreamPinError, match="'variables'"):
        normalize_upstream_digest(
            {
                "model_name": "m",
                "version": "1.1",
                "time": "Static",
                "variables": 3,
                "connections": [],
                "ontology": [],
                "model_parameters": {},
                "parameters": {},
            }
        )
    with pytest.raises(UpstreamPinError, match="'connections'"):
        normalize_upstream_digest(
            {
                "model_name": "m",
                "version": "1.1",
                "time": "Static",
                "variables": [],
                "connections": 3,
                "ontology": [],
                "model_parameters": {},
                "parameters": {},
            }
        )
    with pytest.raises(UpstreamPinError, match="'ontology'"):
        normalize_upstream_digest(
            {
                "model_name": "m",
                "version": "1.1",
                "time": "Static",
                "variables": [],
                "connections": [],
                "ontology": 3,
                "model_parameters": {},
                "parameters": {},
            }
        )
    with pytest.raises(UpstreamPinError, match="'parameters'"):
        normalize_upstream_digest(
            {
                "model_name": "m",
                "version": "1.1",
                "time": "Static",
                "variables": [],
                "connections": [],
                "ontology": [],
                "model_parameters": {},
                "parameters": 3,
            }
        )
    with pytest.raises(UpstreamPinError, match="mappings"):
        normalize_upstream_digest(
            {
                "model_name": "m",
                "version": "1.1",
                "time": "Static",
                "variables": [3],
                "connections": [],
                "ontology": [],
                "model_parameters": {},
                "parameters": {},
            }
        )


def test_time_digest_classifies_like_upstream() -> None:
    """The ``## Time`` body is classified Static/Dynamic, as upstream classifies it."""
    source = (GNN_DIR / "bernoulli_toy.gnn.md").read_text(encoding="utf-8")
    assert spec_digest(parse_gnn_file(GNN_DIR / "bernoulli_toy.gnn.md"))["time"] == "Static"
    assert spec_digest(parse_gnn(source.replace("## Time\n\nStatic", "## Time\n\nDynamic")))["time"] == "Dynamic"
    # Upstream records the default "Static" for a body it cannot classify.
    assert spec_digest(parse_gnn(source.replace("## Time\n\nStatic", "## Time\n\nContinuous")))["time"] == "Static"


def test_normalize_upstream_digest_maps_enums_and_sequences() -> None:
    """Dtype aliases, version/time normalization, and comma-list parameters normalize."""
    normalized = normalize_upstream_digest(
        {
            "model_name": " Toy ",
            "version": "GNN v1.1",
            "time": "Time=t\nDynamic\nDiscrete",
            "variables": [{"name": "o1", "dims": [2, 1], "dtype": "DataType.INTEGER"}],
            "connections": [["a", "b", "DIRECTED", None]],
            "ontology": [{"variable": "a", "term": "T"}],
            "model_parameters": {"multi_k_stream_counts": [3, 4, 5], "num_streams": 2, "gamma": 1.0},
            "parameters": {"J": [[1.0, -1.0], [-1.0, 1.0]]},
        }
    )
    assert normalized["model_name"] == "Toy"
    assert normalized["version"] == "1.1"
    assert normalized["time"] == "Dynamic"
    assert normalized["variables"] == {"o1": {"dims": [2, 1], "dtype": "int"}}
    assert normalized["connections"] == [["a", "b", "DIRECTED", ""]]
    project_style = {
        "model_name": "Toy",
        "version": "1.1",
        "time": "Dynamic",
        "variables": {"o1": {"dims": [2, 1], "dtype": "int"}},
        "connections": [["a", "b", "directed", ""]],
        "ontology": {"a": "T"},
        "model_parameters": {"multi_k_stream_counts": "3, 4, 5", "num_streams": "2", "gamma": "1.0"},
        "parameters": {"J": [[1.0, -1.0], [-1.0, 1.0]]},
    }
    assert digest_divergences(project_style, normalized) == []
