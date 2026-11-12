"""Upstream-parser conformance test for the project-owned GNN parser.

The project-owned parser (`src/gnn/parser.py`) is cited-not-vendored: it never
imports upstream GNN code.  This test makes the "spec-conformant" claim
checkable by running the **real upstream parser**
(`gnn.parsers.markdown_parser.MarkdownGNNParser`) of the pinned GNN release
against every shipped ``gnn/*.gnn.md`` spec and comparing normalized digests.
Any divergence fails.

The pinned release is not read here: the `gnn` gate arm reads `gnn/upstream.json`
once, the GNN-FEP shared reader (`python -m gnn.importers`) validates the pin,
the `.github/GNN.md` pointer and the specs from the pinned tree, and the arm
publishes the selected release through `POLICY_ENTANGLEMENT_GNN_RELEASE`.
Reading the pin shape is that reader's job, so this test has no copy of it.

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
    ENV_PINNED_RELEASE,
    ENV_UPSTREAM_ROOT,
    PARSER_RELATIVE_PATH,
    PinnedRelease,
    UpstreamConformanceError,
    checkout_available,
    default_gnn_root,
    digest_divergences,
    gnn_checkout_python,
    normalize_upstream_digest,
    pinned_release,
    resolve_gnn_root,
    spec_digest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GNN_DIR = PROJECT_ROOT / "gnn"
SHIPPED_SPECS = sorted(GNN_DIR.glob("*.gnn.md"))

#: The canonical workstream pin.  Bumping it is a deliberate act: this test
#: pins the release the arm selected, so a silent re-pin cannot pass unnoticed.
CANONICAL_TAG = "v5.1.0"
CANONICAL_COMMIT = "75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf"
CANONICAL_GNN_VERSION = "5.1.0"


@dataclass(frozen=True)
class UpstreamRun:
    """One execution of the pinned upstream parser over the shipped specs."""

    release: PinnedRelease
    root: Path
    payload: dict[str, Any]
    mutant: Path
    extract_dir: Path


@pytest.fixture(scope="module")
def selected_release() -> PinnedRelease:
    """The release the ``gnn`` arm selected, or a skip outside the arm."""
    if ENV_PINNED_RELEASE not in os.environ:
        pytest.skip(
            f"{ENV_PINNED_RELEASE} is unset: this test runs inside the `gnn` arm "
            "(`python scripts/gate.py gnn`), which reads the pin"
        )
    return pinned_release()


@pytest.fixture(scope="module")
def upstream_run(tmp_path_factory: pytest.TempPathFactory, selected_release: PinnedRelease) -> UpstreamRun:
    """Execute the pinned upstream parser on every shipped spec + a leniency mutant."""
    pin = selected_release
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

    # Non-vacuity control: the two parsers classify one dtype differently —
    # the project parser reads `bool`, the pinned upstream parser reads its
    # `binary` — so the comparison must report a dtype divergence rather than
    # trivially agreeing.  (The earlier control, the spaced ontology heading,
    # no longer discriminates: v5.1.0 reads it, where v5.0.3 ignored it.)
    mutant = extract_dir / "bool_dtype.gnn.md"
    mutant.write_text(
        (GNN_DIR / "bernoulli_toy.gnn.md")
        .read_text(encoding="utf-8")
        .replace("pi1[2,1,type=float]", "pi1[2,1,type=bool]"),
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
        release=pin,
        root=root,
        payload=json.loads(proc.stdout),
        mutant=mutant,
        extract_dir=extract_dir,
    )


def test_selected_release_is_the_canonical_pin(selected_release: PinnedRelease) -> None:
    """The release the arm read is the canonical workstream pin (v5.1.0).

    The pin's schema, revision shape, repository and recorded date are the
    shared reader's findings (`pin-*`, reported by the arm before this test
    runs), so this test pins only what the arm selected: a silent re-pin
    cannot pass unnoticed.
    """
    assert selected_release.repository == "https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation"
    assert selected_release.tag == CANONICAL_TAG
    assert selected_release.commit == CANONICAL_COMMIT
    assert selected_release.parser_module == "gnn.parsers.markdown_parser"
    assert selected_release.parser_class == "MarkdownGNNParser"


def test_pinned_release_record_is_required_and_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    """The arm's hand-off is refused when absent or incomplete, never guessed."""
    monkeypatch.delenv(ENV_PINNED_RELEASE, raising=False)
    with pytest.raises(UpstreamConformanceError, match="is unset"):
        pinned_release()
    monkeypatch.setenv(ENV_PINNED_RELEASE, json.dumps({"commit": CANONICAL_COMMIT}))
    with pytest.raises(UpstreamConformanceError, match="parser_module"):
        pinned_release()
    monkeypatch.setenv(
        ENV_PINNED_RELEASE,
        json.dumps(
            {
                "repository": "https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation",
                "tag": CANONICAL_TAG,
                "commit": CANONICAL_COMMIT,
                "parser_module": "gnn.parsers.markdown_parser",
                "parser_class": "MarkdownGNNParser",
            }
        ),
    )
    assert pinned_release().commit == CANONICAL_COMMIT


def test_resolve_gnn_root_honours_explicit_selection(tmp_path: Path) -> None:
    """An explicit selection is final; an empty selection is refused."""
    chosen = tmp_path / "checkout"
    assert resolve_gnn_root(PROJECT_ROOT, {ENV_UPSTREAM_ROOT: str(chosen)}) == chosen.resolve()
    with pytest.raises(UpstreamConformanceError, match="must not be empty"):
        resolve_gnn_root(PROJECT_ROOT, {ENV_UPSTREAM_ROOT: "   "})
    assert resolve_gnn_root(PROJECT_ROOT, {}) == default_gnn_root(PROJECT_ROOT)
    assert gnn_checkout_python(chosen) == chosen / ".venv" / "bin" / "python"
    assert checkout_available(tmp_path / "absent") is False


def test_upstream_parser_ran_from_the_pinned_commit(upstream_run: UpstreamRun) -> None:
    """The executed parser bytes are the pinned commit's bytes, from the pinned tree."""
    parser_info = upstream_run.payload["parser"]
    assert parser_info["module"] == upstream_run.release.parser_module
    assert parser_info["class"] == upstream_run.release.parser_class
    assert parser_info["gnn_version"] == CANONICAL_GNN_VERSION
    assert Path(parser_info["file"]).is_relative_to(upstream_run.extract_dir)

    pinned_blob = subprocess.run(
        ["git", "-C", str(upstream_run.root), "show", f"{upstream_run.release.commit}:{PARSER_RELATIVE_PATH}"],
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


def test_conformance_check_discriminates_on_the_dtype_mutant(upstream_run: UpstreamRun) -> None:
    """NON-VACUITY: a dtype the two parsers classify differently must diverge.

    The project parser reads `type=bool` as `bool`; the pinned upstream parser
    reads its `binary`.  Both parse the mutant successfully, so a comparison
    that reported no divergence here would be comparing nothing — the check
    must report the dtype difference.
    """
    project = spec_digest(parse_gnn_file(upstream_run.mutant))
    upstream = normalize_upstream_digest(upstream_run.payload["specs"][str(upstream_run.mutant)])
    assert project["variables"]["pi1"]["dtype"] == "bool"
    assert upstream["variables"]["pi1"]["dtype"] == "binary"
    issues = digest_divergences(project, upstream)
    assert issues and all("dtype" in issue for issue in issues)


def test_digest_comparison_rejects_malformed_digests() -> None:
    """A malformed digest field is refused instead of silently compared."""
    with pytest.raises(UpstreamConformanceError, match="must be a mapping"):
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
    with pytest.raises(UpstreamConformanceError, match="missing fields"):
        normalize_upstream_digest({"model_name": "m"})
    with pytest.raises(UpstreamConformanceError, match="'variables'"):
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
    with pytest.raises(UpstreamConformanceError, match="'connections'"):
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
    with pytest.raises(UpstreamConformanceError, match="'ontology'"):
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
    with pytest.raises(UpstreamConformanceError, match="'parameters'"):
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
    with pytest.raises(UpstreamConformanceError, match="mappings"):
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
