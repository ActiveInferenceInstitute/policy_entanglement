"""Structural lock for the genuine ℝ analytic proofs in
``lean/MathlibProofs/MathlibProofs.lean``.

The MathlibProofs package is a SEPARATE lake project (it requires
Mathlib; ~8249 build jobs) and is therefore *not* built by the standard
`scripts/regression_gate.py` Lean step (which builds the 22-job
Mathlib-free boundary fragment). Without this lock a regression that
guts the genuine Theorem-5.1 analytic proof — a `sorry`, an `admit`, an
introduced `axiom`, a `native_decide`, or deleting the capstone — would
pass the normal gate silently. That is exactly the "fixing a
never-exercised gate" / silent-relabel failure class this project's
history is full of.

This is a FAST, deterministic, no-Mathlib-build GREP TRIPWIRE — and,
stated precisely (RedTeam 2026-05-19 C, no over-claim), it does **not**
by itself catch transitive `sorryAx`/`axiom`/`native_decide` laundering
(its captures historically stopped at `:= by`; it now also inspects
the full-identity proof body, but a grep is still not a kernel). The
genuine soundness gate is the `lake build` + **`#print axioms`
foundational-only** audit in `scripts/build_mathlib_proofs.py`, which
runs on the **automatic pytest path** via
`tests/test_mathlib_axiom_audit.py` *when the Lean toolchain is
available* (that test *honestly xfails — never silently passes —* when
it is not) and on the opt-in `--with-mathlib` / release path. That
audit fail-closes if any keystone depends on a non-foundational axiom
OR is renamed/missing. This fast lock is the between-build tripwire
(presence + grep hygiene + anti-degeneracy + proof-body
non-triviality); the axiom audit is the genuine enforcement. Neither
*proves* the theorems — `lake` does — but together they prevent the
genuine artifact from being silently hollowed out.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from lean.mathlib_proofs_gate import local_warning_issues

PROJECT = Path(__file__).resolve().parent.parent
MLP = PROJECT / "lean" / "MathlibProofs" / "MathlibProofs.lean"
BUILD_SCRIPT = PROJECT / "scripts" / "build_mathlib_proofs.py"

# Theorems whose genuine, axiom-clean proofs carry the manuscript's
# central formal-verification claim (Theorem 5.1 analytic content) and
# the previously-deferred product-marginalization core. Each must remain
# present with its named statement; deleting/renaming one is a
# manuscript-claim regression and must fail loudly here.
_REQUIRED_THEOREMS = (
    "streamMarginal_productDist",
    "logDiv_prod_separates",
    "streamMarginal_sum_eq_total",
    "klReal_nonneg",
    "klReal_split_via_intermediate",
    "klReal_minimises_generalK",
    "entanglement_decomposition_generalK",
    # The FULL S01 free-energy identity (2026-05-19). Its FIRST delivery
    # was a sorryAx-laundered fake caught + reverted; this pins the
    # genuine third state so it cannot be silently gutted again.
    "free_energy_decomposition_full",
)

# Tokens that would mean the "proof" is no longer a genuine proof.
_FORBIDDEN = ("sorry", "admit", "native_decide", "sorryAx")


def _src() -> str:
    assert MLP.exists(), f"{MLP} missing — the ℝ analytic proof layer is gone."
    return MLP.read_text(encoding="utf-8")


def _build_script_module():
    spec = importlib.util.spec_from_file_location("build_mathlib_proofs", BUILD_SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_mathlib_proofs_hygiene_no_sorry_axiom_native() -> None:
    """0 sorry/admit/native_decide/sorryAx in the ℝ proof file. A single
    one silently converts a machine-checked claim into an assumption —
    the exact pattern five prior review rounds existed to prevent."""
    src = _src()
    hits = {tok: src.count(tok) for tok in _FORBIDDEN if tok in src}
    assert not hits, (
        f"forbidden proof-gutting tokens in MathlibProofs.lean: {hits}. "
        "The genuine Theorem 5.1 analytic proof must stay axiom-clean; "
        "if a proof genuinely regressed, fix the proof — do NOT sorry it."
    )


def test_release_gate_rejects_local_mathlibproofs_warnings() -> None:
    """The release gate must fail on local MathlibProofs linter warnings,
    not merely on hard errors.
    """
    output = "warning: MathlibProofs.lean:674:0: automatically included section variable(s) unused\n"
    assert local_warning_issues(output) == [output.strip()]
    assert local_warning_issues("warning: Mathlib/Foo.lean:1:0: dependency warning") == []


def test_required_genuine_theorems_present() -> None:
    """The capstone + its load-bearing lemmas must remain declared. A
    rename/delete is a manuscript-claim regression (0A/2D/3A/veridical_
    status all cite these by name) and must be a deliberate, visible
    change here, not a silent one."""
    src = _src()
    missing = [name for name in _REQUIRED_THEOREMS if not re.search(rf"\btheorem\s+{re.escape(name)}\b", src)]
    assert not missing, (
        f"required genuine theorems absent from MathlibProofs.lean: "
        f"{missing}. These carry the manuscript's central formal-"
        "verification claim; update the manuscript + veridical_status.md "
        "deliberately if a name truly changed."
    )


def test_capstone_statement_is_the_general_entangled_form() -> None:
    """Anti-degeneracy lock. The capstone must remain the GENERAL
    entangled-`q` statement: `m` defined as the product of `q`'s stream
    marginals (NOT `m := q`), and `q` constrained only by positivity +
    normalization (never assumed to factorize). A future edit collapsing
    it to the degenerate product/`m=q` case (Gibbs-twice) re-introduces
    the F7 laundering and must fail here."""
    src = _src()
    m = re.search(
        r"theorem\s+entanglement_decomposition_generalK\b.*?:=\s*by",
        src,
        re.DOTALL,
    )
    assert m, "entanglement_decomposition_generalK signature not found."
    sig = m.group(0)
    # m is the product of q's stream marginals — the genuine m-projection.
    assert "streamMarginal q s (i s)" in sig and "∏ s" in sig, (
        "capstone `m` is no longer `∏ₛ streamMarginal q s (i s)` — the "
        "general-entangled m-projection. A degenerate `m := q` collapses "
        "the claim to Gibbs-twice (the F7 laundering). Reverted?"
    )
    # q is a free general joint: only positivity + normalization hypotheses.
    assert "∀ i, 0 < q i" in sig and "(∑ i, q i) = 1" in sig, (
        "capstone no longer takes a general `q` (only positivity + "
        "normalization expected); a factorization hypothesis on `q` "
        "would weaken Theorem 5.1's analytic claim."
    )


def test_full_identity_is_the_literal_s01_boxed_form() -> None:
    """Anti-degeneracy / anti-laundering lock for the FULL S01 identity.
    Its first delivery was a sorryAx fake; this pins the genuine third
    state's *statement shape* so a future edit cannot silently swap it
    for a weaker/adjacent identity (RedTeam-A MED-1 at the statement
    level). The conclusion must be the literal boxed
    `F = Σ streamFreeEnergyReal + γλ⟨K_c⟩ + logZE − λ⟨J⟩ + I(q)` over
    the genuine `entangledPosterior`, with `logZE` the definitional
    normalizer (not a free scalar) and `I(q)` the m-projection KL term."""
    src = _src()
    m = re.search(
        r"theorem\s+free_energy_decomposition_full\b.*?:=\s*by",
        src,
        re.DOTALL,
    )
    assert m, "free_energy_decomposition_full signature not found."
    sig = m.group(0)
    for needle, why in (
        ("entangledPosterior Ek Jpot lam", "q must be the genuine entangledPosterior (not an arbitrary/degenerate q)"),
        ("fullFreeEnergyReal q Ek Gk Jpot Kc gamma lam", "LHS must be the genuine manuscript VFE fullFreeEnergyReal"),
        ("streamFreeEnergyReal q Ek Gk gamma k", "RHS must carry the genuine per-stream free-energy sum"),
        ("gamma * lam * (∑ π, q π * Kc π)", "RHS must carry the genuine γλ⟨K_c⟩ coupling term"),
        ("logZE Ek Jpot lam", "RHS must carry the genuine definitional log-normalizer logZE"),
        ("lam * (∑ π, q π * Jpot π)", "RHS must carry the −λ⟨J⟩ term"),
        ("Real.log (q π / m π)", "RHS must carry the kernel-backed multi-information I(q)=∑q·log(q/m)"),
    ):
        assert needle in sig, (
            f"free_energy_decomposition_full no longer matches the literal "
            f"S01 boxed identity — missing/changed: {why!r}. A future edit "
            "must not swap the full identity for a weaker/adjacent statement."
        )
    # `logZE` must be defined as the genuine log-normalizer, not a scalar.
    assert re.search(r"def\s+logZE\b[^\n]*\n[^\n]*\n?\s*Real\.log\s*\(∑", src), (
        "logZE is no longer the definitional log-normalizer "
        "`Real.log (∑ π, entangledNumer …)` — an assumed scalar here is "
        "the exact laundering the first (reverted) fake attempted."
    )
    # Proof-BODY non-triviality (RedTeam 2026-05-19 C-F3): the prior
    # `:= by`-truncated capture never inspected the body, so a gutted /
    # degenerate / one-liner body would pass. Capture from `:= by` to the
    # next top-level declaration and require the genuine composition: the
    # body must apply the axiom-clean kernel and the expansion lemmas, and
    # be substantively long — a trivial body cannot prove the S01 identity.
    bm = re.search(
        r"theorem\s+free_energy_decomposition_full\b.*?:=\s*by"
        r"(?P<body>.*?)(?:\n(?:theorem|lemma|def|noncomputable def|end)\s)",
        src,
        re.DOTALL,
    )
    assert bm, "free_energy_decomposition_full proof body not found."
    body = bm.group("body")
    for lemma in (
        "entanglement_decomposition_generalK",
        "expected_logPrior_expand",
    ):
        assert lemma in body, (
            f"free_energy_decomposition_full body no longer applies "
            f"`{lemma}` — a body not composing the axiom-clean kernel + "
            "the expansion lemmas cannot genuinely prove the S01 identity "
            "(degenerate/laundered body the `:= by`-truncated check missed)."
        )
    assert len(body.strip()) > 400, (
        "free_energy_decomposition_full proof body is suspiciously short "
        f"({len(body.strip())} chars) — the genuine composition is long; "
        "a one-liner/stub body is the degeneration this lock now catches."
    )
