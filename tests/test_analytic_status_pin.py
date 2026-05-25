"""Analytic-status string pin on `thm_4_1` per IterativeDepth Lens 3.

The registry row at `manuscript/refs/labels.yaml::theorems.thm_4_1`
encodes the ℝ-machine-checked discharge of Theorem 4.1 (the
manuscript's central result, the full S01 boxed free-energy identity)
in a free-text `analytic_status:` field.  No derived `[[VAR:...]]`
token currently exposes that field to the reader-visible claim
counts, so a future copy-edit could silently break the prose-side
claim that the ℝ kernel is machine-checked.

This test pins the structural signal-carrying tokens of that field —
the name of the keystone theorem, the audit gate, the foundational-
axiom claim, and the single open residual — so any edit that
weakens the disclosure is caught by CI.  Per
`[[feedback-fix-every-copy-of-a-gate]]` and
`[[feedback-shape-tests-dont-bind-truth]]`, the pin checks substantive
tokens, not just string equality.

Negative control: corrupting any pinned token (verified once-locally,
recorded in this docstring) makes the test fail loudly.
"""

from __future__ import annotations

from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
LABELS_YAML = PROJECT / "manuscript" / "refs" / "labels.yaml"


def _load_thm_4_1() -> dict:
    with LABELS_YAML.open() as fh:
        labels = yaml.safe_load(fh)
    theorems = labels.get("theorems") or {}
    row = theorems.get("thm_4_1")
    assert row is not None, "thm_4_1 row missing from labels.yaml"
    return row


def test_thm_4_1_status_and_faithfulness_pinned() -> None:
    """The Float-layer status + faithfulness fields are pinned."""
    row = _load_thm_4_1()
    assert str(row.get("status")) == "boundary", (
        f"thm_4_1.status drifted from 'boundary' to {row.get('status')!r}.  "
        "The Float-layer registry status MUST remain 'boundary' — the "
        "ℝ-discharge is encoded in the separate 'mathlib_analytic_proof' / "
        "'analytic_status' channels (Pass-11 design)."
    )
    assert str(row.get("faithfulness")) == "typed-witness", (
        f"thm_4_1.faithfulness drifted from 'typed-witness' to {row.get('faithfulness')!r}."
    )


def test_thm_4_1_mathlib_proof_reference_pinned() -> None:
    """The `mathlib_analytic_proof` field MUST name a real
    `MathlibProofs.*` keystone the build can verify."""
    row = _load_thm_4_1()
    proof = str(row.get("mathlib_analytic_proof", ""))
    assert "MathlibProofs." in proof, (
        f"thm_4_1.mathlib_analytic_proof must name a MathlibProofs.* declaration; got {proof!r}."
    )
    assert "entanglement_decomposition_generalK" in proof or "free_energy_decomposition_full" in proof, (
        f"thm_4_1.mathlib_analytic_proof must reference either the "
        f"general-K kernel (`entanglement_decomposition_generalK`) or the "
        f"full capstone (`free_energy_decomposition_full`); got {proof!r}."
    )


def test_thm_4_1_analytic_status_signal_tokens_pinned() -> None:
    """The free-text `analytic_status:` field MUST carry the substantive
    signal-carrying tokens.  Each missing token below is the
    `[[feedback-shape-tests-dont-bind-truth]]` failure mode — disclosure
    weakening without registry edit detection.
    """
    row = _load_thm_4_1()
    status = str(row.get("analytic_status", ""))

    required_tokens = {
        "free_energy_decomposition_full": "the ℝ-machine-checked capstone theorem name",
        "build_mathlib_proofs.py": "the enforced reproducible-build script",
        "axiom-clean": "the foundational-only axiom claim",
        "negative control": "the non-vacuity negative-control discipline",
        "Float<->R": "the single open residual (Float↔ℝ bridge)",
        "methods_and_assumptions.md": "the open-residual scope document",
    }

    missing = [f"  - {token}  ({why})" for token, why in required_tokens.items() if token not in status]
    assert not missing, (
        "thm_4_1.analytic_status has lost one or more substantive "
        "signal-carrying tokens.  The disclosure must move at every "
        "site, not just here.  Missing:\n" + "\n".join(missing) + "\n\nCurrent value:\n" + status
    )
