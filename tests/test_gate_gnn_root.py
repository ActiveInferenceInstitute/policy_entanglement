"""`scripts/gate.py` must never modify an operator-supplied GNN checkout.

`POLICY_ENTANGLEMENT_GNN_ROOT` can name a checkout that belongs to another
repository (an upstream clone or a mirror). The conformance arm may read it, but
provisioning — `git init`, fetch, detached checkout, remote re-pointing, or a
dependency install — must stay inside the gate-owned cache. These tests build
real temporary repositories and prove HEAD, refs, origin, local config, working
tree and the absence of a virtualenv are unchanged after the arm refuses.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from types import ModuleType

import pytest

from gnn.upstream import PinnedRelease

PROJECT = Path(__file__).resolve().parent.parent
GATE_PATH = PROJECT / "scripts" / "gate.py"
PINNED_TAG = "v5.1.0"


def _load_gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gate_under_test", GATE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GATE = _load_gate()


def _env() -> dict[str, str]:
    """Isolated git environment: no host config, deterministic identity."""
    env = dict(os.environ)
    env.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_AUTHOR_NAME": "Gate Test",
            "GIT_AUTHOR_EMAIL": "gate-test@example.invalid",
            "GIT_COMMITTER_NAME": "Gate Test",
            "GIT_COMMITTER_EMAIL": "gate-test@example.invalid",
            "GIT_AUTHOR_DATE": "2001-02-03T04:05:06+00:00",
            "GIT_COMMITTER_DATE": "2001-02-03T04:05:06+00:00",
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_CONFIG_COUNT": "0",
        }
    )
    return env


@pytest.fixture(autouse=True)
def _isolated_gate_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Real subprocesses use file-only transport and no operator Git configuration."""
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY"):
        monkeypatch.delenv(key, raising=False)
    for key, value in _env().items():
        if key.startswith("GIT_"):
            monkeypatch.setenv(key, value)
    monkeypatch.setenv("ACTINF_SKIP_BOOTSTRAP", "1")
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        env=_env(),
    )


def _commit(repo: Path, message: str) -> str:
    (repo / f"{message}.txt").write_text(message, encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "--quiet", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _repo(path: Path) -> tuple[Path, str]:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "--quiet", "--initial-branch=main")
    return path, _commit(path, "first")


def _pin(commit: str, repository: str = "https://github.com/example/upstream") -> PinnedRelease:
    return PinnedRelease(
        repository=repository,
        tag=PINNED_TAG,
        commit=commit,
        parser_module="gnn.parsers.markdown_parser",
        parser_class="MarkdownGNNParser",
    )


def _snapshot(repo: Path) -> dict[str, object]:
    """Capture refs/config and actual worktree bytes, including preexisting edits."""
    tracked = _git(repo, "ls-tree", "-r", "--name-only", "HEAD").stdout
    worktree = {}
    for path in repo.rglob("*"):
        if ".git" in path.relative_to(repo).parts:
            continue
        if path.is_symlink():
            worktree[path.relative_to(repo).as_posix()] = ("symlink", os.readlink(path))
        elif path.is_file():
            worktree[path.relative_to(repo).as_posix()] = ("file", path.read_bytes())
    return {
        "head": _git(repo, "rev-parse", "HEAD").stdout,
        "refs": _git(repo, "for-each-ref", "--format=%(refname) %(objectname)").stdout,
        "remotes": _git(repo, "remote", "--verbose").stdout,
        "local_config": _git(repo, "config", "--list", "--local").stdout,
        "status": _git(repo, "status", "--porcelain").stdout,
        "tracked": tracked,
        "worktree": worktree,
    }


def test_explicit_root_without_the_pin_is_refused_untouched(tmp_path: Path) -> None:
    repo, _ = _repo(tmp_path / "upstream")
    before = _snapshot(repo)
    gate_cache = tmp_path / "gate-cache"

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(GATE, "GNN_CACHE", gate_cache)
        patch.setenv(GATE.ENV_UPSTREAM_ROOT, str(repo))
        with pytest.raises(SystemExit) as refused:
            GATE._arm_gnn()

    message = str(refused.value)
    assert "does not contain the pinned commit" in message
    assert "does not fetch into an explicitly selected checkout" in message
    assert _snapshot(repo) == before
    assert not (repo / ".venv").exists()
    assert not gate_cache.exists(), "the arm must not provision anywhere while an explicit root is set"


def test_explicit_root_with_a_moved_tag_keeps_every_ref(tmp_path: Path) -> None:
    repo, pinned_commit = _repo(tmp_path / "upstream")
    _git(repo, "tag", PINNED_TAG, pinned_commit)
    moved_commit = _commit(repo, "second")
    _git(repo, "tag", "--force", PINNED_TAG, moved_commit)
    before = _snapshot(repo)

    with pytest.raises(SystemExit) as refused:
        GATE._validate_external_checkout(repo, _pin(pinned_commit))

    assert "no longer resolves to the pinned commit" in str(refused.value)
    assert _snapshot(repo) == before
    assert _git(repo, "rev-parse", f"refs/tags/{PINNED_TAG}^{{commit}}").stdout.strip() == moved_commit


def test_explicit_root_without_a_prepared_interpreter_is_refused(tmp_path: Path) -> None:
    repo, pinned_commit = _repo(tmp_path / "upstream")
    _git(repo, "tag", PINNED_TAG, pinned_commit)
    before = _snapshot(repo)

    with pytest.raises(SystemExit) as refused:
        GATE._validate_external_checkout(repo, _pin(pinned_commit))

    assert "no usable parser interpreter" in str(refused.value)
    assert _snapshot(repo) == before
    assert not (repo / ".venv").exists(), "the arm must not install into an explicit checkout"


def test_managed_cache_is_the_only_checkout_provisioned(tmp_path: Path) -> None:
    source, pinned_commit = _repo(tmp_path / "source")
    _git(source, "tag", PINNED_TAG, pinned_commit)
    before_source = _snapshot(source)
    pin = _pin(pinned_commit, repository=str(source))

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(GATE, "GNN_CACHE", tmp_path / "gate-cache")
        patch.delenv(GATE.ENV_UPSTREAM_ROOT, raising=False)
        cache_root = GATE._gnn_cache_root(pin)
        assert tmp_path / "gate-cache" in cache_root.parents
        GATE._ensure_checkout(cache_root, pin)

    assert _git(cache_root, "rev-parse", "HEAD").stdout.strip() == pinned_commit
    assert _git(cache_root, "remote", "get-url", "origin").stdout.strip() == str(source)
    assert _git(cache_root, "rev-parse", f"refs/tags/{PINNED_TAG}^{{commit}}").stdout.strip() == pinned_commit
    assert _snapshot(source) == before_source


def test_gate_module_keeps_the_cache_outside_the_working_tree() -> None:
    assert isinstance(GATE.GNN_CACHE, Path)
    assert PROJECT not in GATE.GNN_CACHE.parents
    assert GATE.ENV_UPSTREAM_ROOT == "POLICY_ENTANGLEMENT_GNN_ROOT"
    assert Path(GATE.__file__) == GATE_PATH


def _reader_repo(root: Path) -> tuple[Path, str]:
    """A committed rejection control, not a replacement GNN semantic validator."""
    repo, _ = _repo(root)
    package = repo / "src" / "gnn"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "importers.py").write_text(
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "member = json.loads(Path('member-input.json').read_text())\n"
        "print('PINNED_REJECTION ' + json.dumps(dict(file=__file__, cwd=os.getcwd(),\n"
        "    argv=sys.argv[1:], pythonpath=os.environ['PYTHONPATH'], member=member)))\n"
        "raise SystemExit(23)\n",
        encoding="utf-8",
    )
    commit = _commit(repo, "reader")
    assert _git(repo, "tag", PINNED_TAG, commit).returncode == 0
    return repo, commit


def _reader_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    member = tmp_path / "member"
    member.mkdir()
    (member / "member-input.json").write_text('{"member": "consumer"}', encoding="utf-8")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(GATE, "PROJECT_ROOT", member)
    monkeypatch.setenv("TMPDIR", str(scratch))
    return member, scratch


@pytest.mark.parametrize("state", ["dirty", "different-head", "managed-dirty"])
def test_reader_executes_selected_bytes_and_preserves_live_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str], state: str
) -> None:
    source, commit = _reader_repo(tmp_path / "source")
    pin = _pin(commit, repository=str(source))
    root = source
    if state == "managed-dirty":
        root = tmp_path / "managed-cache"
        GATE._ensure_checkout(root, pin)
    (root / "src/gnn/importers.py").write_text("print('LIVE_SOURCE_IMPORTED')\n", encoding="utf-8")
    if state == "different-head":
        _commit(root, "later")
    elif state == "managed-dirty":
        GATE._ensure_checkout(root, pin)
    before_source, before_root = _snapshot(source), _snapshot(root)
    member, scratch = _reader_context(tmp_path, monkeypatch)
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join((str(root / "src"), str(PROJECT / "src"))))

    assert GATE._run_pinned_reader(Path(sys.executable), root, pin) == 23
    output = capfd.readouterr().out
    trace = json.loads(next(line.removeprefix("PINNED_REJECTION ") for line in output.splitlines()
                            if line.startswith("PINNED_REJECTION ")))
    assert "LIVE_SOURCE_IMPORTED" not in output
    assert trace["member"] == {"member": "consumer"}
    assert Path(trace["cwd"]) == member
    assert trace["argv"] == [
        "check", "--repo", ".", "--require-pointer", "--workflow", ".github/workflows/ci.yml",
        "--job", "gnn-conformance", "--expected-commit", commit, "--expected-tag", PINNED_TAG,
    ]
    module_path = Path(trace["file"])
    assert module_path.is_relative_to(scratch)
    assert trace["pythonpath"] == str(module_path.parent.parent)
    assert not module_path.exists()
    assert list(scratch.iterdir()) == []
    assert _snapshot(source) == before_source
    assert _snapshot(root) == before_root


@pytest.mark.parametrize("missing_commit", [False, True])
def test_reader_refuses_missing_selected_source_without_live_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, missing_commit: bool
) -> None:
    repo, commit = _repo(tmp_path / "source")
    marker = tmp_path / "live-reader-executed"
    package = repo / "src/gnn"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "importers.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('live')\n", encoding="utf-8"
    )
    before = _snapshot(repo)
    _, scratch = _reader_context(tmp_path, monkeypatch)
    monkeypatch.setenv("PYTHONPATH", str(repo / "src"))
    with pytest.raises(SystemExit, match="cannot archive|has no regular"):
        GATE._run_pinned_reader(Path(sys.executable), repo, _pin("0" * 40 if missing_commit else commit))
    assert not marker.exists()
    assert list(scratch.iterdir()) == []
    assert _snapshot(repo) == before


@pytest.mark.parametrize("selection", ["empty", "whitespace", "missing", "file", "directory"])
def test_invalid_explicit_selection_never_creates_a_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, selection: str
) -> None:
    target = tmp_path / selection
    if selection == "file":
        target.write_text("operator data", encoding="utf-8")
    elif selection == "directory":
        target.mkdir()
    raw = {"empty": "", "whitespace": " \t "}.get(selection, str(target))
    cache = tmp_path / "cache"
    monkeypatch.setattr(GATE, "GNN_CACHE", cache)
    monkeypatch.setenv(GATE.ENV_UPSTREAM_ROOT, raw)
    with pytest.raises(SystemExit, match=GATE.ENV_UPSTREAM_ROOT):
        GATE._arm_gnn()
    assert not cache.exists()
    if selection == "file":
        assert target.read_text(encoding="utf-8") == "operator data"
    elif selection == "directory":
        assert list(target.iterdir()) == []
    else:
        assert not target.exists()


@pytest.mark.parametrize("selection", [" ./upstream ", "~/upstream"])
def test_explicit_root_normalization_reaches_selected_reader_without_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str], selection: str
) -> None:
    pytest.importorskip("defusedxml")
    pytest.importorskip("psutil")
    repo, commit = _reader_repo(tmp_path / "upstream")
    (repo / ".venv").symlink_to(sys.prefix, target_is_directory=True)
    pin_path = tmp_path / "pin.json"
    pin_path.write_text(json.dumps(asdict(_pin(commit))), encoding="utf-8")
    member, scratch = _reader_context(tmp_path, monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("PYTHONPATH", raising=False)
    monkeypatch.setenv(GATE.ENV_UPSTREAM_ROOT, selection)
    monkeypatch.setattr(GATE, "PIN_PATH", pin_path)
    monkeypatch.setattr(GATE, "GNN_CACHE", tmp_path / "cache")
    before = _snapshot(repo)
    assert GATE._arm_gnn() == 23
    output = capfd.readouterr().out
    assert f"validated operator checkout {repo.resolve()}" in output
    trace = json.loads(next(line.removeprefix("PINNED_REJECTION ") for line in output.splitlines()
                            if line.startswith("PINNED_REJECTION ")))
    assert Path(trace["cwd"]) == member
    assert Path(trace["file"]).is_relative_to(scratch)
    assert _snapshot(repo) == before
    assert not (tmp_path / "cache").exists()
    assert list(scratch.iterdir()) == []


@pytest.mark.parametrize(
    ("root_selection", "handoff"),
    [(None, False), ("", False), ("missing", False), ("", True), ("missing", True)],
)
def test_direct_conformance_invocation_distinguishes_unset_from_explicit(
    tmp_path: Path, root_selection: str | None, handoff: bool
) -> None:
    env = _env()
    env.pop(GATE.ENV_UPSTREAM_ROOT, None)
    env.pop(GATE.ENV_PINNED_RELEASE, None)
    env["PYTEST_ADDOPTS"] = ""
    if root_selection is not None:
        env[GATE.ENV_UPSTREAM_ROOT] = "" if root_selection == "" else str(tmp_path / "absent")
    if handoff:
        env[GATE.ENV_PINNED_RELEASE] = json.dumps(asdict(GATE._read_pin()))
    node = "test_upstream_parser_ran_from_the_pinned_commit" if handoff else "test_selected_release_is_the_canonical_pin"
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-cov", "-o", "addopts=",
            "--basetemp", str(tmp_path / "nested"),
            f"{PROJECT / 'tests/test_gnn_upstream_conformance.py'}::{node}",
        ],
        cwd=PROJECT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if root_selection is None:
        assert result.returncode == 0, result.stdout + result.stderr
        assert "1 skipped" in result.stdout
    else:
        assert result.returncode == 1, result.stdout + result.stderr
        assert "1 error" in result.stdout
        assert GATE.ENV_UPSTREAM_ROOT in result.stdout
