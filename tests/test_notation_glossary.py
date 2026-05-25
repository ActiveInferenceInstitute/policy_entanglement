"""Regression tests for the notation concordance appendix.

Asserts that every symbol-class actually used in the manuscript /
LaTeX preamble / Python source / Lean source is documented in
``manuscript/S06_notation_and_concordance.md`` exactly once.

Scope:

* Every LaTeX `\\newcommand{\\X}{...}` macro defined in
  `manuscript/preamble.md` is referenced by name in §S6.
* Every Python public identifier that the rest of the test suite
  cross-references (KL divergence, total correlation, entanglement
  posterior, etc.) is referenced in §2a's Python column.
* Every Lean type abbreviation (StreamIdx, PolicyFactor, JointDist,
  …) is referenced in §2a's Lean column.

These tests are intentionally string-based: they catch *omissions* in
the glossary (the most common drift), not formatting differences.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
GLOSSARY = PROJECT / "manuscript" / "S06_notation_and_concordance.md"
PREAMBLE = PROJECT / "manuscript" / "preamble.md"
LEAN_DIR = PROJECT / "lean" / "ActinfPolicyEntanglement"
LEAN_FILES = sorted(LEAN_DIR.glob("*.lean"))


@pytest.fixture(scope="module")
def glossary_text() -> str:
    return GLOSSARY.read_text()


# ---------------------------------------------------------------------------
# LaTeX preamble macros
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "macro",
    [
        r"\KL",
        r"\E",
        r"\Var",
        r"\policy",
        r"\policySpace",
        r"\Mfd",
        r"\MFsubmfd",
        r"\MI",
        r"\Hent",
        r"\efe",
        r"\fe",
        r"\coupJ",
        r"\coupK",
    ],
)
def test_every_preamble_macro_is_documented(glossary_text: str, macro: str) -> None:
    """Every `\\newcommand{\\X}{...}` in `preamble.md` must surface
    in the §2a glossary so a reader can look it up.
    """
    preamble = PREAMBLE.read_text()
    assert macro + "}" in preamble, f"sanity: preamble does not define {macro}"
    # Allow either bare macro form or backtick-fenced form.
    assert macro in glossary_text, f"glossary does not document preamble macro {macro!r}"


# ---------------------------------------------------------------------------
# Python identifiers that should appear in §2a's "Python" column
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "identifier",
    [
        "shannon_entropy",
        "kl_divergence",
        "total_correlation",
        "joint_marginal",
        "m_projection",
        "entangled_posterior",
        "coupled_policy_posterior",
        "schmidt_rank",
        "entanglement_entropy",
        "tensor_train_ranks",
        "InferenceMode",
        "coupling_phase_at",
        "optimal_lambda",
        "FreeEnergyBundle",
        "free_energy_bundle",
        "expected_free_energy_under_posterior",
        "coupling_energy",
        "PARAMETER_SWEEP_LAMBDAS",
        "PYMDP_SWEEP_LAMBDAS",
        "PYMDP_ROLLOUT_STEPS",
        "FIGURE_GLOBAL_SEED",
    ],
)
def test_every_python_identifier_is_documented(glossary_text: str, identifier: str) -> None:
    """Each public Python identifier the manuscript refers to must
    appear (verbatim, in code-fence form) in §2a's Python column.
    """
    assert identifier in glossary_text, f"glossary does not reference Python identifier {identifier!r}"


# ---------------------------------------------------------------------------
# Lean type abbreviations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "lean_name",
    [
        "StreamIdx",
        "PolicyFactor",
        "PolicySpace",
        "JointDist",
        "MFDist",
        "BinaryCoupling",
        "CouplingPotential",
        "HorizonProfile",
        "CommScalar",
    ],
)
def test_every_lean_abbrev_is_documented(glossary_text: str, lean_name: str) -> None:
    """Each Lean abbreviation that surfaces across more than one
    boundary submodule must appear in §2a's Lean column.
    """
    # Sanity: name must actually exist in the boundary fragment.
    found_in_lean = any(lean_name in p.read_text() for p in LEAN_FILES)
    assert found_in_lean, f"sanity: {lean_name!r} does not appear in any boundary Lean source"
    assert lean_name in glossary_text, f"glossary does not reference Lean abbreviation {lean_name!r}"


# ---------------------------------------------------------------------------
# Manuscript symbols (math notation)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "symbol",
    [
        r"$K \in \mathbb{N}$",
        r"$\lambda \in [0,\infty)$",
        r"$\gamma > 0$",
        r"$\gamma_k > 0$",
        r"$\Pi^k$",
        r"$T_k$",
        r"$L$",
        r"$\ell$",
        r"$d$",
        r"$P(\cdot)$",
        r"$Q(\cdot)$",
        r"$E_k(\pi^k)$",
        r"$G_k(\pi^k)$",
        r"$q_\lambda(\pi)$",
        r"$J(\pi)$",
        r"$K_c(\pi)$",
        r"$J_{\mathrm{soph}}$",
        r"$I(q)",  # opening of a row matching $I(q) = ...
    ],
)
def test_every_core_symbol_is_documented(glossary_text: str, symbol: str) -> None:
    """Each load-bearing math symbol used in the manuscript must
    appear (in the LHS of a glossary row) in §2a.
    """
    assert symbol in glossary_text, f"glossary does not document symbol {symbol!r}"


# ---------------------------------------------------------------------------
# Structural shape: glossary advertises every section that uses notation
# ---------------------------------------------------------------------------


def test_glossary_contains_every_top_section(glossary_text: str) -> None:
    """The glossary must cover the major thematic groups."""
    expected_section_headers = [
        "Sets, indices, and basic objects",
        "POMDP generative-model symbols",
        "Distributions",
        "Coupling potentials and parameters",
        "Information-theoretic quantities",
        "Free energies",
        "Manifolds, projections, and dual coordinates",
        "Spectral and tensor-network symbols",
        "Heterogeneous-ensemble quantities",
        "Relationship classes and claim-strength labels",
        "Hyperparameters",
        "LaTeX preamble macros",
        "Lean type abbreviations",
        "Phase / verdict labels",
        "Conventions",
    ]
    for hdr in expected_section_headers:
        assert hdr in glossary_text, f"glossary missing section: {hdr!r}"


def test_glossary_contains_sign_conventions_section(glossary_text: str) -> None:
    """S06 must include a "Sign conventions" section.

    Pins the round-1 addition (``manuscript/S06_notation_and_concordance.md``
    grew an explicit "Sign conventions" subsection so prose phrases like
    "modulo a sign convention" trace to a single anchor point in the
    glossary).
    """
    assert "Sign conventions" in glossary_text, "glossary missing the round-1 'Sign conventions' section"


@pytest.mark.parametrize(
    "label",
    [
        "`exact`",
        "`parametric`",
        "`analogical`",
        "`out-of-scope`",
        "`proved` / `witness` / `empirical` / `hypothesis` / `roadmap`",
    ],
)
def test_relationship_and_claim_labels_are_documented(glossary_text: str, label: str) -> None:
    """Part V's recovery rows use controlled labels; S06 must define them."""
    assert label in glossary_text, f"glossary does not define controlled label {label!r}"


def test_glossary_is_referenced_from_first_use_sections() -> None:
    """The glossary must be cross-referenced by the sections that
    *introduce* the most notation, so a reader following the prose
    finds the symbol catalog from page one.
    """
    for fname in (
        "0A_abstract.md",
        "2B_setup.md",
        "2C_lambda_deformation.md",
        "4C_pymdp_harness.md",
    ):
        path = PROJECT / "manuscript" / fname
        assert path.exists(), fname
        text = path.read_text()
        assert "[[SECREF:notation]]" in text, f"{fname} does not cross-reference the notation glossary"
