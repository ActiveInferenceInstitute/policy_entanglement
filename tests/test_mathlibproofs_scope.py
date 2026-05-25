"""Guards for MathlibProofs claim-scope discipline."""

from __future__ import annotations

from pathlib import Path

from manuscript.status import mathlibproofs_claim_issues

PROJECT = Path(__file__).resolve().parent.parent


def test_mathlibproofs_prose_does_not_overpromote_boundary_claims() -> None:
    issues = mathlibproofs_claim_issues(PROJECT)
    assert not issues, "\n".join(issues)


def test_mathlibproofs_optional_slice_files_and_kernels_are_present() -> None:
    root = PROJECT / "lean" / "MathlibProofs"
    assert (root / "lakefile.lean").is_file()
    assert (root / "lean-toolchain").is_file()
    source = root / "MathlibProofs.lean"
    assert source.is_file()
    text = source.read_text(encoding="utf-8")
    assert "import Mathlib" in text
    assert "def proofSliceVersion : Nat := 3" in text
    assert "theorem vecMulVec_rank_le_one" in text
    assert "theorem rank_le_one_of_pointwise_factorization" in text
    assert "theorem klReal_nonneg" in text
    assert "theorem klReal_minimises_of_pythagorean" in text
    # `noncomputable` is intentionally NOT forbidden: the genuine S01
    # free-energy / log-normalizer / posterior definitions are real-valued
    # and use `Real.exp`/`Real.log`, which are noncomputable in Lean 4 +
    # Mathlib — the keyword is mandatory there and has zero bearing on
    # proof validity. Axiom-cleanliness is enforced independently and
    # is the real integrity gate: `#print axioms` foundational-only via
    # `test_mathlib_axiom_audit.py` + `build_mathlib_proofs.py` (which
    # carries the same corrected forbidden-token set). `sorry`/`axiom `/
    # `unsafe `/`partial ` remain forbidden — those genuinely signal a
    # non-clean proof.
    for forbidden in ("sorry", "axiom ", "unsafe ", "partial "):
        assert forbidden not in text
