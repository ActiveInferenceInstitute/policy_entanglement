#!/usr/bin/env python3
"""Report-only four-track concordance coherence check (thin orchestrator).

Mechanical guardrail recommended by the 2026-05-18 deep review
(Meadows leverage point #6: turn manual-concordance seam-decay into a
detectable signal). Scope is deliberately *mechanical and non-blocking*:

  1. Every ``status: proved|witness|boundary|forwarder`` row in
     ``manuscript/refs/labels.yaml`` has its ``lean_name`` present in the
     project Lean source (``lean/`` excluding vendored ``.lake/``).
  2. Every Python identifier asserted in S06's Python column that looks
     like a bare ``snake_case``/``CamelCase`` callable (and is *not*
     inside a ``(no ...)`` disclaimer cell) resolves to a ``def``/``class``
     in ``src/``.

It does NOT judge whether a proof is "substantive" (that is a
research-taxonomy decision documented in ``docs/reference/veridical_status.md``,
not a regex). It always exits 0 — wire it into blocking CI only after it
has demonstrated a low false-positive rate.

Usage:  uv run python scripts/check_concordance.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S06 = ROOT / "manuscript" / "S06_notation_and_concordance.md"
LABELS = ROOT / "manuscript" / "refs" / "labels.yaml"
SRC = ROOT / "src"
LEAN = ROOT / "lean"

# Only flag an S06 Python cell as asserting a callable when it is written
# in *call form* — ``name(`` inside a backtick span. Bare backtick tokens
# (``lam``, ``gamma``, ``coupling_j``, module names) are parameter/attribute
# symbols, NOT asserted function bindings, and must not cry wolf.
_CALL = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)\(")
# Python builtins / well-known library callables legitimately used in S06
# expressions (``sum(per_stream_efe(...))`` etc.) — not project bindings.
_BUILTINS = {
    "sum",
    "len",
    "min",
    "max",
    "abs",
    "int",
    "float",
    "list",
    "dict",
    "set",
    "tuple",
    "range",
    "enumerate",
    "zip",
    "sorted",
}
_DISCLAIMER = re.compile(r"\(no [^)]*\)|symbol only|not implemented|inline", re.I)
_LEAN_NAME = re.compile(r"lean_name:\s*\"?([A-Za-z_][A-Za-z0-9_.]*)\"?")


def _src_python_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in SRC.rglob("*.py") if "__pycache__" not in p.parts)


def _lean_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in LEAN.rglob("*.lean") if ".lake" not in p.parts)


def concordance_issues(
    *,
    labels_path: Path = LABELS,
    s06_path: Path = S06,
    py_blob: str | None = None,
    lean_blob: str | None = None,
) -> list[str]:
    """Return the list of mechanical four-track concordance violations.

    Pure resolver extracted from ``main()`` so it can be asserted as a
    *blocking* pytest invariant (``tests/test_concordance_enforced.py``)
    while the CLI stays report-only/exit-0. Paths/blobs are injectable so
    the enforcement test can ship a self-proving negative control (a
    deliberately-broken registry must be flagged) — per the 2026-05-18
    deep review's rule that a check only ever observed passing enforces
    nothing. Scope is unchanged: mechanical identifier/``lean_name``
    resolution only; proof *substance* stays a human-reviewed
    ``veridical_status.md`` decision, never a regex here.
    """
    if py_blob is None:
        py_blob = _src_python_text()
    if lean_blob is None:
        lean_blob = _lean_text()
    unresolved: list[str] = []

    # (1) registry lean_name resolution
    for raw in labels_path.read_text(encoding="utf-8").splitlines():
        m = _LEAN_NAME.search(raw)
        if not m:
            continue
        name = m.group(1).split(".")[-1]
        if not re.search(rf"\b(theorem|lemma|def)\s+{re.escape(name)}\b", lean_blob):
            unresolved.append(f"[labels.yaml] lean_name '{m.group(1)}' not found in lean/")

    # (2) S06 Python-column identifiers
    in_table = False
    for line in s06_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and "Python" in line and "Lean" in line:
            in_table = True
            continue
        if not (in_table and line.startswith("|")):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        py_cell = cells[3]
        if _DISCLAIMER.search(py_cell):
            continue
        for ident in _CALL.findall(py_cell):
            if ident in _BUILTINS:
                continue
            if not re.search(rf"\b(def|class)\s+{re.escape(ident)}\b", py_blob):
                unresolved.append(f"[S06 Python] asserted callable '{ident}(...)' not defined in src/")

    return unresolved


def main() -> int:
    unresolved = concordance_issues()

    print("=== concordance coherence check (report-only, non-blocking) ===")
    if unresolved:
        print(f"UNRESOLVED ({len(unresolved)}):")
        for u in sorted(set(unresolved)):
            print(f"  - {u}")
    else:
        print("OK: all probed registry lean_names and S06 Python identifiers resolve.")
    print("(exit 0 by design — promote to a blocking gate only after a clean run history)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
