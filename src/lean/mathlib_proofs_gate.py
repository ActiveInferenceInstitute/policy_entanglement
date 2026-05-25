"""MathlibProofs build and axiom-audit gate."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from lean._lake_lock import mathlib_proofs_lock

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

KEYSTONE_THEOREMS = (
    "streamMarginal_productDist",
    "logDiv_prod_separates",
    "klReal_nonneg",
    "klReal_split_via_intermediate",
    "klReal_minimises_generalK",
    "entanglement_decomposition_generalK",
    "free_energy_decomposition_full",
    "streamMarginal_pos",
    "multiInformation_nonneg_at_joint",
)

FORBIDDEN_LOCAL_TOKENS = ("sorry", "admit ", "axiom ", "unsafe ", "partial ")


def declared_keystones(mathlib_src: Path) -> list[str]:
    if not mathlib_src.exists():
        return []
    src = mathlib_src.read_text(encoding="utf-8")
    return [name for name in KEYSTONE_THEOREMS if re.search(rf"\btheorem\s+{re.escape(name)}\b", src)]


def axiom_audit(
    mathlib_dir: Path,
    mathlib_src: Path,
    *,
    project_root: Path | None = None,
) -> list[str]:
    names = declared_keystones(mathlib_src)
    if not names:
        return ["no keystone theorems declared in MathlibProofs.lean — the genuine ℝ proof is missing"]
    missing = [n for n in KEYSTONE_THEOREMS if n not in names]
    if missing:
        return [
            f"expected keystone(s) absent from MathlibProofs.lean: {missing}. "
            "A rename/delete silently removes them from the #print-axioms "
            "audit — update KEYSTONE_THEOREMS deliberately if intended."
        ]
    body = "import MathlibProofs\nopen MathlibProofs\n" + "".join(f"#print axioms {n}\n" for n in names)
    violations: list[str] = []
    lock_root = project_root or mathlib_dir.parent.parent
    with mathlib_proofs_lock(lock_root), tempfile.TemporaryDirectory() as td:
        chk = Path(td) / "AxiomAudit.lean"
        chk.write_text(body, encoding="utf-8")
        proc = subprocess.run(
            ["lake", "env", "lean", str(chk)],
            cwd=str(mathlib_dir),
            check=False,
            capture_output=True,
            text=True,
        )
    out = proc.stdout + proc.stderr
    if proc.returncode != 0:
        return [f"axiom audit failed to run (exit {proc.returncode}): {out.strip()[:400]}"]
    for name in names:
        m = re.search(rf"'MathlibProofs\.{re.escape(name)}'\s+depends on axioms:\s*\[([^\]]*)\]", out)
        if not m:
            violations.append(f"{name}: could not parse #print axioms output (fail-closed)")
            continue
        found = {a.strip() for a in m.group(1).split(",") if a.strip()}
        extra = found - ALLOWED_AXIOMS
        if extra:
            violations.append(
                f"{name}: depends on NON-foundational axioms {sorted(extra)} "
                f"(allowed: {sorted(ALLOWED_AXIOMS)}) — this is an assumed, not proved, theorem"
            )
    return violations


def local_hygiene_issues(mathlib_dir: Path, project_root: Path) -> list[str]:
    issues: list[str] = []
    for path in mathlib_dir.glob("*.lean"):
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_LOCAL_TOKENS:
            if token in text:
                rel = path.relative_to(project_root)
                issues.append(f"{rel}: forbidden local token {token!r}")
    return issues


def local_warning_issues(output: str) -> list[str]:
    return [line for line in output.splitlines() if re.search(r"warning: MathlibProofs\.lean:", line)]


def _hydrate_mathlib_cache(mathlib_dir: Path) -> None:
    """Best-effort download of Mathlib oleans before the proof build.

    A cold `lake build` for this scaffold otherwise compiles all of Mathlib
    from source. The cache step is not a substitute for the build or axiom
    audit; it only provisions dependencies so the fail-closed gate can run in
    the normal project-test path.
    """
    print(">>> lake exe cache get (hydrate Mathlib build cache)")
    proc = subprocess.run(
        ["lake", "exe", "cache", "get"],
        cwd=str(mathlib_dir),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        print("OK  Mathlib cache hydrated.")
        return

    combined = (proc.stdout or "") + (proc.stderr or "")
    print(
        "!!! Mathlib cache hydration failed; falling back to lake build "
        f"(exit {proc.returncode}).",
        file=sys.stderr,
    )
    if combined.strip():
        print(combined.strip()[-1200:], file=sys.stderr)


def run_mathlib_proofs_gate(project_root: Path) -> int:
    mathlib_dir = project_root / "lean" / "MathlibProofs"
    mathlib_src = mathlib_dir / "MathlibProofs.lean"
    lakefile = mathlib_dir / "lakefile.lean"
    if not lakefile.exists():
        print("MathlibProofs has no Lake scaffold yet; nothing to build.")
        return 0

    with mathlib_proofs_lock(project_root):
        _hydrate_mathlib_cache(mathlib_dir)
        print(">>> lake build (lean/MathlibProofs optional additive scaffold)")
        proc = subprocess.run(
            ["lake", "build"],
            cwd=str(mathlib_dir),
            check=False,
            capture_output=True,
            text=True,
        )
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    if proc.returncode != 0:
        print(f"!!! MathlibProofs build failed with exit code {proc.returncode}", file=sys.stderr)
        return proc.returncode

    warning_issues = local_warning_issues(proc.stdout + proc.stderr)
    if warning_issues:
        for issue in warning_issues:
            print(f"!!! LOCAL MATHLIBPROOFS WARNING: {issue}", file=sys.stderr)
        return 1

    issues = local_hygiene_issues(mathlib_dir, project_root)
    if issues:
        for issue in issues:
            print(f"!!! {issue}", file=sys.stderr)
        return 1

    print(">>> #print axioms audit (keystone theorems must be foundational-only)")
    violations = axiom_audit(mathlib_dir, mathlib_src, project_root=project_root)
    if violations:
        for v in violations:
            print(f"!!! AXIOM AUDIT: {v}", file=sys.stderr)
        print(
            "!!! The genuine-ℝ-proof claim is NOT verified: a keystone "
            "theorem is assumed, not proved. This is the exact laundering "
            "this gate exists to catch.",
            file=sys.stderr,
        )
        return 1

    audited = declared_keystones(mathlib_src)
    print(
        "OK  MathlibProofs builds, clean local hygiene, and "
        f"{len(audited)} keystone theorem(s) #print-axioms foundational-only "
        f"({', '.join(audited)})"
    )
    return 0
