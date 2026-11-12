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
import os
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

from gnn.upstream import UpstreamPin

PROJECT = Path(__file__).resolve().parent.parent
GATE_PATH = PROJECT / "scripts" / "gate.py"
PINNED_TAG = "v5.0.3"


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
        }
    )
    return env


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


def _pin(commit: str, repository: str = "https://github.com/example/upstream") -> UpstreamPin:
    return UpstreamPin(
        repository=repository,
        tag=PINNED_TAG,
        commit=commit,
        parser_module="gnn.parsers.markdown_parser",
        parser_class="MarkdownGNNParser",
    )


def _snapshot(repo: Path) -> dict[str, str]:
    """Everything a mutation would show up in: HEAD, refs, origin, config, tree."""
    tracked = _git(repo, "ls-tree", "-r", "--name-only", "HEAD").stdout
    worktree = sorted(
        path.relative_to(repo).as_posix()
        for path in repo.rglob("*")
        if ".git" not in path.relative_to(repo).parts and path.is_file()
    )
    return {
        "head": _git(repo, "rev-parse", "HEAD").stdout,
        "refs": _git(repo, "for-each-ref", "--format=%(refname) %(objectname)").stdout,
        "remotes": _git(repo, "remote", "--verbose").stdout,
        "local_config": _git(repo, "config", "--list", "--local").stdout,
        "status": _git(repo, "status", "--porcelain").stdout,
        "tracked": tracked,
        "worktree": "\n".join(worktree),
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
