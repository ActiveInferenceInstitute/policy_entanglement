"""Pytest configuration: add `src/` to `sys.path` so test modules can
import the four subpackages by their canonical namespaces:

    from lean.coupling import ...
    from simulation.specs import ...
    from manuscript.registry import ...
    from visualizations.heatmaps import ...

The bare-module import shim (e.g. `from coupling import ...`) is no
longer supported — every test and script uses the fully-qualified
subpackage path.

The repository root is also added to `sys.path` so modules under
`src/lean/` can import the project-agnostic infrastructure helpers
(``infrastructure.reporting.Invariant``, ``InteractiveDashboard``,
``Panel``, ``Control``) used by the simulation dashboard and the
plaintext invariants report.

In addition, this module installs a session-scoped autouse fixture
that bootstraps the project's analysis artifacts before tests run.
The fixture is needed because the parent template's full pipeline
executes ``Clean Output Directories`` (stage 0) before
``Project Tests`` (stage 3) — but several tests assert against
``output/figures/*.png`` and ``output/data/manuscript_variables.json``
that are normally produced by ``Project Analysis`` (stage 4).

The fixture:

* Detects missing artifacts by inspecting ``manuscript/refs/labels.yaml``
  (figure paths excluding ``pymdp_*``) and the prose ``[[VAR:...]]``
  keys vs. ``output/data/manuscript_variables.json``.
* Runs only the scripts whose outputs are missing (idempotent;
  amortized once per session).
* Chooses the Python interpreter that can satisfy ``pymdp_available()``
  — the project's own ``.venv/bin/python`` is preferred when ``pymdp``
  is missing from the active interpreter (which is the case under the
  template's root ``uv run pytest`` invocation).
"""
from __future__ import annotations

import json
import os
import re
import subprocess  # nosec B404 - controlled subprocess for analysis-script bootstrap.
import sys
from pathlib import Path

from manuscript.meta_files import MANUSCRIPT_NON_BODY_MD

_HERE = Path(__file__).resolve().parent
_SRC = _HERE / "src"
_REPO = _HERE.parent.parent  # projects/<name>/conftest.py → repo root
for _p in (_SRC, _REPO):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)


# ---------------------------------------------------------------------------
# Session-scoped autouse fixture: bootstrap analysis artifacts.
#
# Design contract:
#
#   * Idempotent: a single early `_all_artefacts_present()` check exits in
#     well under 50 ms when the working tree already has every artifact.
#   * Session-scoped: cost (≤ ~45 s for a full bootstrap including pymdp
#     scripts) is paid once per pytest invocation.
#   * Interpreter-aware: when the active ``sys.executable`` cannot import
#     ``pymdp`` but ``projects/<name>/.venv/bin/python`` can, the project
#     venv is used to drive the pymdp-dependent simulate_* scripts. This
#     keeps the parent template's pipeline green even though the root
#     ``uv run pytest`` interpreter doesn't carry the optional ``sim``
#     dependency group.
# ---------------------------------------------------------------------------


import pytest  # noqa: E402  (placed after sys.path setup so namespaces resolve)
import yaml  # noqa: E402

_PROJECT = _HERE
_OUTPUT = _PROJECT / "output"
_FIG_DIR = _OUTPUT / "figures"
_DATA_DIR = _OUTPUT / "data"
_VAR_JSON = _DATA_DIR / "manuscript_variables.json"
_LABELS_YAML = _PROJECT / "manuscript" / "refs" / "labels.yaml"
_SCRIPTS = _PROJECT / "scripts"
_PROJECT_VENV_PY = _PROJECT / ".venv" / "bin" / "python"

# Token regex used by the prose-VAR audit; mirrors `tests/test_veridicality.py`.
_VAR_RE = re.compile(r"\[\[VAR:([A-Za-z0-9_]+)(?::[^\]]+)?\]\]")


def _missing_figure_labels() -> list[str]:
    """Return labels (excluding ``pymdp_*``) whose figure file is missing.

    Mirrors ``tests/test_token_resolution.py::test_every_registered_figure_has_artifact_on_disk``
    so the fixture only schedules a re-run when that test would currently fail.
    """
    if not _LABELS_YAML.exists():
        return []
    labels = yaml.safe_load(_LABELS_YAML.read_text()) or {}
    figures = labels.get("figures", {}) or {}
    missing: list[str] = []
    for label, entry in figures.items():
        if label.startswith("pymdp_"):
            continue
        rel = entry.get("path") if isinstance(entry, dict) else None
        if not rel:
            continue
        if not (_PROJECT / rel).exists():
            missing.append(label)
    return missing


def _prose_var_keys() -> set[str]:
    """Keys appearing in ``manuscript/*.md`` body files via ``[[VAR:key]]``."""
    keys: set[str] = set()
    manuscript_dir = _PROJECT / "manuscript"
    if not manuscript_dir.is_dir():
        return keys
    for src in sorted(manuscript_dir.glob("*.md")):
        if src.name in MANUSCRIPT_NON_BODY_MD:
            continue
        for m in _VAR_RE.finditer(src.read_text()):
            keys.add(m.group(1))
    return keys


def _existing_var_keys() -> set[str]:
    """Keys present in the current ``manuscript_variables.json``."""
    if not _VAR_JSON.exists():
        return set()
    try:
        return set(json.loads(_VAR_JSON.read_text()).keys())
    except (OSError, ValueError):
        return set()


def _pymdp_importable(python: Path) -> bool:
    """Return True if ``python`` can ``import pymdp`` (best-effort)."""
    try:
        completed = subprocess.run(  # nosec B603 - controlled probe.
            [str(python), "-c", "import pymdp"],
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


def _resolve_python_for(*, needs_pymdp: bool) -> str:
    """Return an interpreter path that can satisfy the script's needs.

    When ``needs_pymdp`` is True and ``sys.executable`` lacks pymdp, fall
    back to the project's own ``.venv/bin/python`` (which is provisioned
    with ``uv sync --group sim``). When neither has pymdp, return the
    active interpreter so the script reaches its own ``pymdp_available()``
    guard and exits 0 cleanly with a stdout note.
    """
    active = sys.executable
    if not needs_pymdp:
        return active
    if _pymdp_importable(Path(active)):
        return active
    if _PROJECT_VENV_PY.exists() and _pymdp_importable(_PROJECT_VENV_PY):
        return str(_PROJECT_VENV_PY)
    return active


def _run_script(script_name: str, *, needs_pymdp: bool = False, timeout: int = 600) -> int:
    """Execute ``scripts/<script_name>`` with a suitable interpreter.

    The subprocess is launched from ``_PROJECT`` so the scripts' relative
    output paths resolve correctly. ``MPLBACKEND=Agg`` is set to keep
    matplotlib headless. Non-zero exit codes are reported via stdout but
    are not raised — the downstream tests will fail with a clearer
    artifact-missing message if a script genuinely broke, and the
    fixture's job is to do its best and stay out of the way.
    """
    python = _resolve_python_for(needs_pymdp=needs_pymdp)
    script = _SCRIPTS / script_name
    env = dict(os.environ)
    env.setdefault("MPLBACKEND", "Agg")
    try:
        completed = subprocess.run(  # nosec B603 - controlled invocation of repo scripts.
            [python, str(script)],
            cwd=str(_PROJECT),
            env=env,
            check=False,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(
            f"[conftest:bootstrap] {script_name} could not start: {exc}",
            file=sys.stderr,
        )
        return 1
    if completed.returncode != 0:
        print(
            f"[conftest:bootstrap] {script_name} exited {completed.returncode}\n"
            f"--- stdout ---\n{completed.stdout}\n"
            f"--- stderr ---\n{completed.stderr}\n",
            file=sys.stderr,
        )
    return int(completed.returncode)


def _all_artefacts_present() -> bool:
    """Cheap idempotency check: skip bootstrap when everything is ready.

    "Ready" means: no figures (excluding ``pymdp_*``) are missing, and
    every prose ``[[VAR:key]]`` resolves in the current variables JSON.
    """
    if _missing_figure_labels():
        return False
    prose = _prose_var_keys()
    existing = _existing_var_keys()
    missing_vars = prose - existing
    return not missing_vars


def _strict_mode_enabled() -> bool:
    """Honor either ACTINF_STRICT_BOOTSTRAP=1 or any CI runner env signal.

    Strict mode (RedTeam Tests C1+C2, 2026-05-20): when set, the bootstrap
    *does not regenerate* anything; instead it fails fast with an
    actionable message if any required artefact is missing.  This closes
    the convergent-automation attack surface where a CI run silently
    regenerates the artefacts under test, masking a registry-vs-prose
    drift that the test was supposed to catch.

    Recognised env vars:
      - ``ACTINF_STRICT_BOOTSTRAP=1`` — explicit opt-in.
      - ``CI=true`` / ``CI=1`` — generic CI-runner signal (GitHub
        Actions, GitLab, CircleCI, etc.).  Override with
        ``ACTINF_STRICT_BOOTSTRAP=0`` to disable in a CI env that
        legitimately needs the regen path.
    """
    explicit = os.environ.get("ACTINF_STRICT_BOOTSTRAP")
    if explicit is not None:
        return explicit not in ("", "0", "false", "False", "no", "off")
    ci = os.environ.get("CI", "").lower()
    return ci in ("1", "true", "yes", "on")


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_project_artefacts() -> None:  # noqa: PT004 (no return value).
    """Ensure analysis artifacts referenced by tests exist on disk.

    Idempotent and session-scoped: the full bootstrap costs ~45 s the
    first time and ~30 ms thereafter. The fixture is autouse so the
    test author never has to remember to request it.

    **Strict mode (RedTeam Tests C1+C2, 2026-05-20).**  Under
    ``ACTINF_STRICT_BOOTSTRAP=1`` or ``CI=true``, the regeneration path
    is DISABLED; missing artefacts cause an immediate ``pytest.exit``
    with a clear "regenerate locally first" message.  This prevents the
    test suite from silently regenerating the very state it claims to
    check (the
    `[[template-repo-convergent-automation]]` /
    `[[feedback-fix-every-copy-of-a-gate]]` attack surface).
    """
    # Allow operators to disable the bootstrap explicitly (e.g. when
    # debugging the scripts themselves and the artifacts should *not*
    # be regenerated on every pytest run).
    if os.environ.get("ACTINF_SKIP_BOOTSTRAP"):
        return

    if _all_artefacts_present():
        return

    if _strict_mode_enabled():
        pytest.exit(
            "actinf bootstrap is in STRICT mode "
            "(ACTINF_STRICT_BOOTSTRAP=1 or CI=true) but project artefacts "
            "are missing or stale. Run `uv run python scripts/run_all.py` "
            "locally to regenerate the artefacts before re-invoking pytest, "
            "OR unset ACTINF_STRICT_BOOTSTRAP / CI to allow auto-regeneration "
            "(NOT recommended in CI — auto-regen masks the registry-vs-prose "
            "drift the tests exist to catch).",
            returncode=1,
        )

    _FIG_DIR.mkdir(parents=True, exist_ok=True)
    _DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Closed-form / analytical figures (no pymdp dep). Cheap (~3 s).
    if _missing_figure_labels():
        _run_script("generate_figures.py", needs_pymdp=False, timeout=300)

    # 2) The pymdp-dependent simulation scripts. Each emits a few
    #    figures and/or a JSON sidecar; manuscript_variables.py later
    #    reads those sidecars to populate the aggregate VAR namespace.
    #
    #    Per RedTeam Tests C2 (2026-05-20), the exit-code accumulator
    #    below lifts the previously-swallowed `_run_script` returncode
    #    into an explicit pytest.fail when any generator failed.  This
    #    closes the `2>/dev/null || true` antipattern noted by the
    #    global CLAUDE.md Operational Rules.
    failed_scripts: list[tuple[str, int]] = []
    for script, timeout in (
        ("simulate_multi_k.py", 300),
        ("simulate_long_horizon.py", 600),
        ("simulate_revertibility.py", 300),
        ("simulate_pymdp.py", 600),
        ("simulate_robustness.py", 900),
        ("simulate_btai.py", 600),
        ("simulate_adversarial.py", 600),
    ):
        rc = _run_script(script, needs_pymdp=True, timeout=timeout)
        if rc != 0:
            failed_scripts.append((script, rc))

    # 3) The GNN fifth-track sidecar feeds gnn_* manuscript variables.
    rc = _run_script("simulate_gnn.py", needs_pymdp=False, timeout=300)
    if rc != 0:
        failed_scripts.append(("simulate_gnn.py", rc))

    # 4) Aggregate every fact source into the manuscript variables JSON.
    rc = _run_script("manuscript_variables.py", needs_pymdp=True, timeout=120)
    if rc != 0:
        failed_scripts.append(("manuscript_variables.py", rc))

    # Surface generator failures explicitly under strict mode; in
    # permissive mode (local dev without `CI=true`), log them but let
    # downstream tests surface the specific missing VARs they need.
    if failed_scripts and _strict_mode_enabled():
        msg = "actinf bootstrap: the following generator scripts failed under STRICT mode:\n" + "\n".join(
            f"  - {script} (exit {rc})" for script, rc in failed_scripts
        ) + "\n\nRe-run locally with `uv run python scripts/run_all.py` and resolve before CI."
        pytest.fail(msg, pytrace=False)
