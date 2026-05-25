"""Lean 4 boundary-fragment build gate (library implementation).

Business logic for :doc:`scripts/build_lean.py </scripts/build_lean>`.
Runs ``lake build`` inside ``lean/`` and asserts the boundary-fragment
hygiene budget:

* the build exits with status 0
* the source contains zero ``sorry`` statements (only doc comments may
  reference the word "sorry")
* the source contains zero ``axiom`` declarations
* no ``unsafe``/``partial``/``noncomputable`` declarations are present
* no boundary-fragment module imports Mathlib

Returns a non-zero exit code if any check fails so the parent pipeline
propagates the failure into CI.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

# Regex helpers used by the source-file scanners.
_SORRY_RE = re.compile(r"(?<!\w)sorry(?!\w)")
_AXIOM_RE = re.compile(r"^\s*axiom\s+\w")
_DISALLOWED_RE = re.compile(r"^\s*(unsafe|partial|noncomputable)\s+(def|theorem|abbrev)")
_MATHLIB_IMPORT_RE = re.compile(r"^\s*import\s+Mathlib(?:\.|\s|$)")
_LAKE_WARN_RE = re.compile(r"^(?P<file>[^\s:]+):(?P<line>\d+):(?P<col>\d+):\s*warning:\s*(?P<msg>.+)$")


def _lean_files(lean_dir: Path, *, exclude_subtree: Path) -> list[Path]:
    """Lean source files under ``lean_dir`` skipping the optional package tree."""
    return sorted(
        f for f in lean_dir.rglob("*.lean") if ".lake" not in f.parts and not f.is_relative_to(exclude_subtree)
    )


def scrape_lake_warnings(stderr_text: str) -> list[dict[str, str]]:
    """Extract structured warning rows from ``lake build`` stderr.

    Each row is a JSONL-friendly dict so downstream auditors can shift
    left on lint-quality regressions without re-parsing the raw output.
    """
    rows: list[dict[str, str]] = []
    for raw in stderr_text.splitlines():
        stripped = raw.strip()
        m = _LAKE_WARN_RE.match(stripped)
        if m:
            rows.append(
                {
                    "source": "lake-build",
                    "level": "warning",
                    "file": m.group("file"),
                    "line": m.group("line"),
                    "col": m.group("col"),
                    "message": m.group("msg"),
                }
            )
            continue
        if raw.lstrip().startswith("warning:"):
            rows.append(
                {
                    "source": "lake-build",
                    "level": "warning",
                    "file": "",
                    "line": "",
                    "col": "",
                    "message": stripped[len("warning:") :].strip(),
                }
            )
    return rows


def emit_infra_log(rows: list[dict[str, str]], *, log_path: Path) -> None:
    """Append structured warning rows to ``log_path`` (JSONL)."""
    if not rows:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with log_path.open("a", encoding="utf-8") as fh:
        for row in rows:
            row_with_ts = {**row, "timestamp": ts}
            fh.write(json.dumps(row_with_ts) + "\n")


def count_sorries(lean_dir: Path, *, exclude_subtree: Path) -> list[tuple[Path, int, str]]:
    """Find every ``sorry`` token outside doc comments."""
    hits: list[tuple[Path, int, str]] = []
    for f in _lean_files(lean_dir, exclude_subtree=exclude_subtree):
        in_doc = False
        for lineno, raw in enumerate(f.read_text().splitlines(), start=1):
            if "/-" in raw and not in_doc:
                in_doc = True
            if "-/" in raw and in_doc:
                in_doc = False
                continue
            if in_doc:
                continue
            if raw.lstrip().startswith("--"):
                continue
            if _SORRY_RE.search(raw):
                hits.append((f, lineno, raw.strip()))
    return hits


def count_axioms(lean_dir: Path, *, exclude_subtree: Path) -> list[tuple[Path, int, str]]:
    """Find every ``axiom`` declaration in the boundary fragment."""
    hits: list[tuple[Path, int, str]] = []
    for f in _lean_files(lean_dir, exclude_subtree=exclude_subtree):
        for lineno, raw in enumerate(f.read_text().splitlines(), start=1):
            if _AXIOM_RE.match(raw):
                hits.append((f, lineno, raw.strip()))
    return hits


def count_disallowed(lean_dir: Path, *, exclude_subtree: Path) -> list[tuple[Path, int, str]]:
    """Flag any ``unsafe``/``partial``/``noncomputable`` definitions."""
    hits: list[tuple[Path, int, str]] = []
    for f in _lean_files(lean_dir, exclude_subtree=exclude_subtree):
        for lineno, raw in enumerate(f.read_text().splitlines(), start=1):
            if _DISALLOWED_RE.match(raw):
                hits.append((f, lineno, raw.strip()))
    return hits


def count_mathlib_imports(
    *,
    import_roots: tuple[Path, ...],
    root_files: tuple[Path, ...],
) -> list[tuple[Path, int, str]]:
    """Flag Mathlib imports in the stock-Lean boundary package only.

    The optional ``lean/MathlibProofs`` sibling package is deliberately
    separate and not part of this boundary scan.
    """
    hits: list[tuple[Path, int, str]] = []
    files: list[Path] = []
    for root in import_roots:
        if root.exists():
            files.extend(sorted(root.rglob("*.lean")))
    files.extend(path for path in root_files if path.exists())
    for f in files:
        for lineno, raw in enumerate(f.read_text().splitlines(), start=1):
            if _MATHLIB_IMPORT_RE.match(raw):
                hits.append((f, lineno, raw.strip()))
    return hits


def _print_hits(label: str, hits: list[tuple[Path, int, str]], *, project_root: Path) -> None:
    """Print a uniform ``file:line  snippet`` listing to stderr."""
    print(f"!!! {len(hits)} {label}:", file=sys.stderr)
    for f, ln, snip in hits:
        print(f"    {f.relative_to(project_root)}:{ln}  {snip}", file=sys.stderr)


def main(
    *,
    project_root: Path,
    lean_dir: Path | None = None,
) -> int:
    """Run ``lake build`` + hygiene gates. Returns 0 on success."""
    lean_dir = lean_dir or (project_root / "lean")
    if not lean_dir.is_dir():
        print(f"!!! lean/ not found at {lean_dir}", file=sys.stderr)
        return 2

    mathlibproofs_dir = lean_dir / "MathlibProofs"
    boundary_import_roots = (
        lean_dir / "ActinfPolicyEntanglement",
        lean_dir / "FepSketches",
    )
    boundary_root_files = (
        lean_dir / "ActinfPolicyEntanglement.lean",
        lean_dir / "FepSketches.lean",
    )
    infra_log_path = project_root / "output" / "logs" / "infrastructure.jsonl"

    print(">>> lake build (lean/ boundary fragment)")
    proc = subprocess.run(
        ["lake", "build"],
        cwd=str(lean_dir),
        stderr=subprocess.PIPE,
        text=True,
    )
    rc = proc.returncode
    stderr_text = proc.stderr or ""
    if stderr_text.strip():
        sys.stderr.write(stderr_text)
    warning_rows = scrape_lake_warnings(stderr_text)
    emit_infra_log(warning_rows, log_path=infra_log_path)
    if warning_rows:
        print(
            f"··· lake build emitted {len(warning_rows)} warning(s); "
            f"logged to {infra_log_path.relative_to(project_root)}"
        )
    if rc != 0:
        print(f"!!! lake build failed (exit {rc})", file=sys.stderr)
        return rc

    sorries = count_sorries(lean_dir, exclude_subtree=mathlibproofs_dir)
    if sorries:
        _print_hits("sorry statement(s) found", sorries, project_root=project_root)
        return 1

    axioms = count_axioms(lean_dir, exclude_subtree=mathlibproofs_dir)
    if axioms:
        _print_hits("axiom declaration(s) found", axioms, project_root=project_root)
        return 1

    disallowed = count_disallowed(lean_dir, exclude_subtree=mathlibproofs_dir)
    if disallowed:
        _print_hits(
            "disallowed declaration(s) (unsafe/partial/noncomputable)",
            disallowed,
            project_root=project_root,
        )
        return 1

    mathlib_imports = count_mathlib_imports(
        import_roots=boundary_import_roots,
        root_files=boundary_root_files,
    )
    if mathlib_imports:
        _print_hits(
            "Mathlib import(s) found in boundary modules",
            mathlib_imports,
            project_root=project_root,
        )
        return 1

    n_files = sum(1 for _ in _lean_files(lean_dir, exclude_subtree=mathlibproofs_dir))
    print(
        f"OK  lake build succeeded · "
        f"{n_files} .lean files · 0 sorries · 0 axioms · "
        "0 unsafe/partial/noncomputable · 0 boundary Mathlib imports"
    )
    return 0


__all__ = [
    "count_axioms",
    "count_disallowed",
    "count_mathlib_imports",
    "count_sorries",
    "emit_infra_log",
    "main",
    "scrape_lake_warnings",
]
