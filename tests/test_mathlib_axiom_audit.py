"""Automatic-path enforcement of the ℝ-proof axiom audit.

RedTeam 2026-05-19 (C-F1) correctly found that the prior "enforced, no
longer maintainer-attested" claim was itself an over-claim: the
`#print axioms` audit in `scripts/build_mathlib_proofs.py` only ran on
the opt-in `--with-mathlib` path, and this project is local-only with
no CI — so on every path that *actually runs automatically* (pytest)
the genuine soundness check (which is the ONLY thing that catches a
transitive `sorryAx`/`native_decide`/introduced-`axiom` fake with no
literal token — the exact laundering caught and reverted this session)
was not invoked. The fast `test_mathlib_proofs_integrity.py` grep lock
cannot see that class (its regex stops at `:= by`).

This test puts the genuine audit on the automatic path: it invokes
`build_mathlib_proofs._axiom_audit()` directly. It is HONEST about its
own preconditions — if the `lake`/Lean toolchain is unavailable it
**xfails with a precise reason** (NOT a silent pass): an environment
that cannot run the audit must not look like one where the audit passed.

**Fail-closed fix (2026-05-24, advisor + Forge cross-vendor convergent
finding).** The prior version `pytest.skip`-ped whenever the build
returned nonzero — which made the fail-loud assertion below unreachable,
so on a Lean-enabled checkout a genuinely broken / unsound build (or an
axiom violation) showed up as a green *skip* rather than a *failure* —
the project's documented "never-exercised gate" class. The classifier
below now fail-closes: with the toolchain PRESENT, a nonzero exit is a
SOUNDNESS failure (FAIL), not an environment skip. Only an explicitly
detected build-provisioning gap (Mathlib deps not fetched), *and* an
explicit `ACTINF_ALLOW_AXIOM_XFAIL=1` opt-out, may downgrade to xfail.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT / "scripts" / "build_mathlib_proofs.py"
LAKEFILE = PROJECT / "lean" / "MathlibProofs" / "lakefile.lean"

# Output markers that indicate an unprovisioned build ENVIRONMENT (deps not
# fetched / no cached build / network) as opposed to a SOUNDNESS failure.
_PROVISIONING_MARKERS = (
    "could not resolve",
    "failed to fetch",
    "lake update",
    "no such file or directory",
    "manifest is out of date",
    "network is unreachable",
    "git fetch",
)


def classify_axiom_probe(returncode: int, combined_output: str, *, allow_xfail: bool) -> str:
    """Classify a `build_mathlib_proofs.py` probe result (lake already present).

    Returns one of: ``"pass"`` (returncode 0), ``"fail"`` (nonzero — treated as a
    soundness failure, the fail-closed default), or ``"xfail-unprovisioned"``
    (nonzero AND the output shows a build-environment provisioning gap AND the
    caller explicitly allowed the xfail bypass).

    Fail-closed: a nonzero exit defaults to ``"fail"``. Only a *detected*
    provisioning gap together with an explicit opt-out downgrades to xfail — so
    a broken/unsound build (sorryAx, non-foundational axiom, broken keystone)
    can never be silently skipped.
    """
    if returncode == 0:
        return "pass"
    unprovisioned = any(m in combined_output.lower() for m in _PROVISIONING_MARKERS)
    if unprovisioned and allow_xfail:
        return "xfail-unprovisioned"
    return "fail"


def test_keystones_are_foundational_only_on_the_automatic_path() -> None:
    if shutil.which("lake") is None:
        # RedTeam Tests M5 (2026-05-20): under strict-mode CI, the
        # axiom audit MUST run.  If `lake` is absent in a CI invocation
        # this is a CI-config defect (the matrix must include a
        # Lean-toolchain job), not an honest xfail.
        strict = os.environ.get("ACTINF_STRICT_BOOTSTRAP")
        ci = os.environ.get("CI", "").lower()
        if (strict and strict not in ("", "0", "false", "False", "no", "off")) or (
            ci in ("1", "true", "yes", "on") and os.environ.get("ACTINF_ALLOW_AXIOM_XFAIL") not in ("1", "true")
        ):
            pytest.fail(
                "lake/Lean toolchain absent in a STRICT/CI invocation — "
                "the #print axioms audit MUST run here. Either install "
                "the Lean toolchain in the CI matrix OR set "
                "ACTINF_ALLOW_AXIOM_XFAIL=1 explicitly to accept the "
                "honest-xfail bypass (NOT recommended; the audit is the "
                "project's only soundness gate against transitive "
                "sorryAx laundering)."
            )
        pytest.xfail(
            "lake/Lean toolchain absent — the #print axioms audit cannot "
            "run here; this is an HONEST xfail, not a pass. The genuine "
            "soundness gate is `scripts/build_mathlib_proofs.py` in a "
            "Lean-enabled (maintainer/release/CI-with-Lean) environment."
        )
    if not LAKEFILE.exists():
        pytest.xfail("MathlibProofs lake scaffold absent — audit not applicable here.")

    probe = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(PROJECT),
        capture_output=True,
        text=True,
        timeout=1800,
    )
    combined = (probe.stdout or "") + "\n" + (probe.stderr or "")
    allow_xfail = os.environ.get("ACTINF_ALLOW_AXIOM_XFAIL") in ("1", "true")
    verdict = classify_axiom_probe(probe.returncode, combined, allow_xfail=allow_xfail)

    if verdict == "xfail-unprovisioned":
        pytest.xfail(
            "lake present but the MathlibProofs build environment is unprovisioned "
            "(deps/cache absent) and ACTINF_ALLOW_AXIOM_XFAIL=1 is set — honest "
            f"xfail, not a pass.\n{combined[-1500:]}"
        )

    # verdict == "fail": fail-closed — a nonzero exit with the toolchain present
    # is a SOUNDNESS failure (transitive sorryAx / non-foundational axiom /
    # broken keystone), NOT an environment skip. This is the path the prior
    # `pytest.skip` made unreachable.
    assert verdict == "pass", (
        "scripts/build_mathlib_proofs.py returned nonzero with the Lean toolchain "
        "PRESENT — fail-closed: this is the transitive-sorryAx / non-foundational-"
        "axiom / broken-keystone class the fast grep locks cannot see. A nonzero "
        "exit here is a SOUNDNESS failure, not an environment skip. Fix the proof; "
        "never relabel to silence. (If the build environment is genuinely "
        "unprovisioned, set ACTINF_ALLOW_AXIOM_XFAIL=1 for an honest xfail.)\n"
        f"--- stdout ---\n{(probe.stdout or '')[-2000:]}\n--- stderr ---\n{(probe.stderr or '')[-2000:]}"
    )
    assert "foundational-only" in probe.stdout, (
        "build_mathlib_proofs.py exited 0 but did not report the "
        "#print-axioms foundational-only confirmation — the audit step "
        f"may not have run. stdout tail:\n{probe.stdout[-1500:]}"
    )


def test_classify_axiom_probe_is_fail_closed() -> None:
    """Non-vacuity control for the fail-closed classifier (no Lean build needed).

    Proves the bug is closed: a nonzero exit is `fail` by default, and only a
    detected provisioning gap WITH the explicit opt-out downgrades to xfail. A
    soundness-failure output (sorryAx / non-foundational axiom) is ALWAYS `fail`,
    even with the opt-out set.
    """
    # Clean build → pass.
    assert classify_axiom_probe(0, "9 keystone theorem(s) ... foundational-only", allow_xfail=False) == "pass"
    # Nonzero with a soundness-failure signature → fail (the bug's target case),
    # and fail even when the xfail opt-out is set (soundness is never skippable).
    sorry_out = "free_energy_decomposition_full depends on axioms: [propext, sorryAx, Classical.choice]"
    assert classify_axiom_probe(1, sorry_out, allow_xfail=False) == "fail"
    assert classify_axiom_probe(1, sorry_out, allow_xfail=True) == "fail"
    # Nonzero, generic failure, no opt-out → fail (fail-closed default).
    assert classify_axiom_probe(1, "build error: rewrite failed", allow_xfail=False) == "fail"
    # Nonzero + provisioning gap + explicit opt-out → honest xfail.
    assert classify_axiom_probe(1, "error: could not resolve dependencies", allow_xfail=True) == "xfail-unprovisioned"
    # Same provisioning gap WITHOUT opt-out → still fail-closed.
    assert classify_axiom_probe(1, "error: could not resolve dependencies", allow_xfail=False) == "fail"
