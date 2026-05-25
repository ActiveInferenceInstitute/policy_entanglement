"""Project-wide token-resolution invariants.

Every ``[[SECREF:label]]``, ``[[THMREF:label]]``, ``[[LEAN:label]]``,
``[[VAR:key]]``, ``[[FIG:label]]``, ``[[FIGREF:label]]``,
``[[EQREF:label]]`` token in any manuscript body file must resolve to
a known entry in the canonical sources:

* ``labels.yaml::sections`` for ``SECREF``
* ``labels.yaml::theorems`` for ``THMREF`` / ``LEAN``
  (and ``LEAN`` must have non-null ``lean_module`` + ``lean_name``)
* ``labels.yaml::figures`` for ``FIG`` / ``FIGREF``
* ``labels.yaml::equations`` for ``EQREF``
* ``output/data/manuscript_variables.json`` for ``VAR`` (only enforced
  when the JSON is already present)

Documentation files whose purpose is to *describe* the token syntax
(README, AGENTS, INDEX, the pymdp-validation worked-example) use
placeholder tokens like ``[[VAR:<key>]]``; these are excluded so the
test stays specific to manuscript body content.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parent.parent
MS = PROJECT / "manuscript"
LABELS = yaml.safe_load((MS / "refs" / "labels.yaml").read_text())

KNOWN_SECTIONS = set(LABELS.get("sections", {}).keys())
KNOWN_THEOREMS = set(LABELS.get("theorems", {}).keys())
KNOWN_FIGURES = set(LABELS.get("figures", {}).keys())
KNOWN_EQUATIONS = set(LABELS.get("equations", {}).keys())
LEAN_WIRED = {k for k, v in LABELS.get("theorems", {}).items() if v.get("lean_module") and v.get("lean_name")}

_VAR_PATH = PROJECT / "output" / "data" / "manuscript_variables.json"


def _known_vars() -> set[str]:
    """Resolve the populated VAR namespace at *test execution* time.

    ``manuscript_variables.json`` is produced by the session-scoped
    autouse bootstrap fixture in ``conftest.py``, which runs *after*
    collection. Reading it at module import (collection) time froze an
    empty-or-stale snapshot: a clean ``output/`` yielded an empty set
    (enforcement silently disabled), while a stale partial JSON left by
    an interrupted earlier run yielded an incomplete set that failed
    real prose ``[[VAR:...]]`` keys. Evaluating lazily keeps this in
    lock-step with the bootstrap contract and the self-bootstrap helper
    in ``test_manuscript_registry.py``.
    """
    if not _VAR_PATH.exists():
        return set()
    try:
        return set(json.loads(_VAR_PATH.read_text()).keys())
    except (OSError, ValueError):
        return set()


TOKEN_RE = re.compile(
    r"\[\[(SECREF|THMREF|LEAN|VAR|FIG|FIGREF|EQ|EQREF|EQLABEL):"
    r"(?P<name>[^\]]+)\]\]"
)
CODE_FENCE_RE = re.compile(r"(```|~~~).*?\1", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

# Files whose body is *about the syntax* — placeholder tokens are OK.
SYNTAX_DOC_FILES = {
    "manuscript/AGENTS.md",
    "manuscript/README.md",
    "manuscript/INDEX.md",
    "manuscript/4E_pymdp_validation.md",
    "manuscript/S05_lean_code_skeleton.md",
    "manuscript/refs/AGENTS.md",
    "manuscript/refs/README.md",
}


def _strip_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", CODE_FENCE_RE.sub("", text))


def _is_placeholder(raw: str) -> bool:
    return "<" in raw or ">" in raw or raw in {"label", "key", "...", "name", "key:fmt"}


def _manuscript_bodies() -> list[Path]:
    return sorted(p for p in MS.rglob("*.md") if "refs/" not in str(p))


def _parse_var_key(name: str) -> str:
    """``[[VAR:foo:.4f]]`` — strip the format spec, return ``"foo"``."""
    return name.split(":", 1)[0]


@pytest.mark.parametrize("kind", ["SECREF", "THMREF", "LEAN", "FIG", "FIGREF", "EQREF", "VAR"])
def test_all_tokens_resolve(kind: str) -> None:
    """Every token of ``kind`` in every manuscript body file points at
    something that exists in the canonical source.
    """
    known_vars = _known_vars()
    failures: list[tuple[str, str, str]] = []
    for fp in _manuscript_bodies():
        rel = str(fp.relative_to(PROJECT))
        if rel in SYNTAX_DOC_FILES:
            continue
        text = _strip_code(fp.read_text())
        for m in TOKEN_RE.finditer(text):
            tkind, raw = m.group(1), m.group("name").strip()
            if tkind != kind:
                continue
            if _is_placeholder(raw):
                continue
            if kind == "VAR":
                key = _parse_var_key(raw)
                if known_vars and key not in known_vars:
                    failures.append((rel, kind, key))
            elif kind == "SECREF":
                if raw not in KNOWN_SECTIONS:
                    failures.append((rel, kind, raw))
            elif kind == "THMREF":
                if raw not in KNOWN_THEOREMS:
                    failures.append((rel, kind, raw))
            elif kind == "LEAN":
                if raw not in KNOWN_THEOREMS:
                    failures.append((rel, kind, raw))
                elif raw not in LEAN_WIRED:
                    failures.append((rel, "LEAN(unwired)", raw))
            elif kind in {"FIG", "FIGREF"}:
                if raw not in KNOWN_FIGURES:
                    failures.append((rel, kind, raw))
            elif kind == "EQREF":
                if raw not in KNOWN_EQUATIONS:
                    failures.append((rel, kind, raw))
    if failures:
        lines = [f"Unresolved {kind} tokens:"]
        for fp, k, raw in failures:
            lines.append(f"  {fp}: [[{k}:{raw}]]")
        pytest.fail("\n".join(lines))


def test_every_registered_figure_has_artifact_on_disk() -> None:
    """``labels.yaml::figures[*].path`` must point at a real file.

    The pymdp-grounded figures (``pymdp_*``) are generated by the
    separate ``scripts/simulate_pymdp.py`` pipeline stage and are
    excluded here so that the analytical figure suite alone can
    serve as a CI gate without running the full pymdp harness.  A
    companion test in ``tests/test_simulation_pymdp.py`` enforces
    pymdp-figure presence once the harness has run.
    """
    missing: list[tuple[str, str]] = []
    for label, entry in LABELS.get("figures", {}).items():
        if label.startswith("pymdp_"):
            continue
        path = PROJECT / entry["path"]
        if not path.exists():
            missing.append((label, entry["path"]))
    if missing:
        lines = ["Figure artifacts referenced in labels.yaml but missing on disk:"]
        for lab, p in missing:
            lines.append(f"  {lab}: {p}")
        pytest.fail("\n".join(lines))


def test_lean_theorems_with_wiring_point_at_real_declarations() -> None:
    """For each theorem with ``lean_module`` + ``lean_name``, the
    declared name must appear in the corresponding ``.lean`` file.
    """
    lean_dir = PROJECT / "lean" / "ActinfPolicyEntanglement"
    if not lean_dir.exists():
        pytest.skip("Lean source tree not present")
    missing: list[tuple[str, str]] = []
    for label, entry in LABELS.get("theorems", {}).items():
        mod, name = entry.get("lean_module"), entry.get("lean_name")
        if not (mod and name):
            continue
        # Lean module may be nested (e.g. "Spectral.Bipartite")
        path_segments = mod.split(".")
        file_path = lean_dir.joinpath(*path_segments[:-1]) / f"{path_segments[-1]}.lean"
        if not file_path.exists():
            file_path = lean_dir / f"{mod.replace('.', '/')}.lean"
        if not file_path.exists():
            missing.append((label, f"file missing for module {mod}"))
            continue
        # Strip leading qualifier for nested declarations like
        # "Bipartite.isBipartiteMeanField_factors".
        last_name = name.strip('"').split(".")[-1]
        text = file_path.read_text()
        if last_name not in text:
            missing.append((label, f"{mod}.{name} not found in {file_path.name}"))
    if missing:
        lines = ["Lean declarations referenced in labels.yaml but not found:"]
        for lab, why in missing:
            lines.append(f"  {lab}: {why}")
        pytest.fail("\n".join(lines))
