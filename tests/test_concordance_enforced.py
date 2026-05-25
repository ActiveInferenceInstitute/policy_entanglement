"""Recommendation #8 (2026-05-18 deep review): four-track concordance
drift is a **build error**, not a recurring manual-review finding.

`scripts/check_concordance.py` stays report-only / exit-0 (a guard that
cry-wolf-blocks gets disabled). These tests are the *teeth*: they assert
the mechanical resolver finds zero unresolved bindings, and — critically
— include a self-proving negative control. The deep review's own rule:
"a check only ever observed passing enforces nothing"; so we demonstrate
the resolver actually fails on injected drift.

Scope is intentionally mechanical (identifier / `lean_name` resolution).
Proof *substance* / statement-faithfulness remains a human-reviewed
`docs/reference/veridical_status.md` decision, never adjudicated here.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
_SCRIPT = PROJECT / "scripts" / "check_concordance.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_concordance", _SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_no_unresolved_four_track_concordance_bindings() -> None:
    """Every registry `lean_name` resolves in `lean/` and every S06
    call-form Python identifier resolves in `src/`. A failure here means
    the concordance (the four-track single source of truth) points at a
    symbol that no longer exists — fix the binding or the source."""
    checker = _load_checker()
    issues = checker.concordance_issues()
    assert not issues, "four-track concordance drift detected:\n" + "\n".join(f"  - {i}" for i in issues)


def test_resolver_detects_injected_registry_drift(tmp_path: Path) -> None:
    """Negative control: a deliberately-broken registry `lean_name` MUST
    be flagged. Without this, a perpetually-green enforcement test is no
    evidence the gate enforces anything (deep-review rule)."""
    checker = _load_checker()
    bad_labels = tmp_path / "labels.yaml"
    bad_labels.write_text(
        'thmref:\n  injected_bogus:\n    lean_name: "this_lean_symbol_does_not_exist_anywhere_xyzzy"\n',
        encoding="utf-8",
    )
    empty_s06 = tmp_path / "S06_empty.md"
    empty_s06.write_text("(no concordance table here)\n", encoding="utf-8")
    issues = checker.concordance_issues(
        labels_path=bad_labels,
        s06_path=empty_s06,
        py_blob="",
        lean_blob="-- deliberately empty lean source --",
    )
    assert any("xyzzy" in i for i in issues), f"resolver failed to detect injected registry drift; issues={issues}"


def test_resolver_detects_injected_s06_python_drift(tmp_path: Path) -> None:
    """Negative control for branch (2): an S06 Python cell asserting a
    call-form identifier absent from `src/` MUST be flagged."""
    checker = _load_checker()
    empty_labels = tmp_path / "labels.yaml"
    empty_labels.write_text("# no lean_name rows\n", encoding="utf-8")
    bad_s06 = tmp_path / "S06.md"
    bad_s06.write_text(
        "| Symbol | Meaning | Notation | Python | Lean |\n"
        "|---|---|---|---|---|\n"
        "| $x$ | demo | `x` | `nonexistent_callable_qqq(z)` | `X` |\n",
        encoding="utf-8",
    )
    issues = checker.concordance_issues(
        labels_path=empty_labels,
        s06_path=bad_s06,
        py_blob="# no defs here",
        lean_blob="",
    )
    assert any("nonexistent_callable_qqq" in i for i in issues), (
        f"resolver failed to detect injected S06 Python drift; issues={issues}"
    )
