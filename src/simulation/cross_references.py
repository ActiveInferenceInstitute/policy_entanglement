"""Prose ↔ equation ↔ Lean cross-reference registry for the simulation harness.

Every public numerical witness in :mod:`simulation` carries a precise
mapping to:

* the manuscript section / theorem / equation it witnesses,
* the Lean declaration that types the analytic content, and
* the dashboard invariant (or test gate) that enforces it.

Hand-maintaining this mapping in scattered docstrings or per-figure
captions leads to drift the moment a section is renumbered or a Lean
declaration renamed.  This module centralizes the mapping so:

* ``scripts/validate_manuscript.py`` can cross-check that every
  registered cross-reference resolves to an existing label /
  equation / Lean declaration;
* figure-generation scripts can decorate each PNG's tEXt metadata
  with the registered ``theorem_witnessed``, ``equation_witnessed``,
  ``lean_declaration``, and ``manuscript_section`` fields;
* downstream users running ``python -m simulation.cross_references``
  get a one-stop dump of the mapping.

The mapping is keyed by Python ``module.function`` qualifier so each
entry is grep-discoverable from the source it documents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class CrossReference:
    """Cross-reference card for a single simulation function.

    All fields use the project's source-format tokens (``[[THMREF:..]]``,
    ``[[EQREF:..]]``, ``[[SECREF:..]]``) so the same string can be
    embedded verbatim in manuscript prose, in a figure caption, or in
    a PNG tEXt metadata field without translation.

    Attributes:
        function: Fully-qualified ``simulation.module.function`` name.
        theorem: ``THMREF`` token (e.g. ``"thm_4_1"``); ``None`` if the
            function does not witness a specific theorem.
        equation: ``EQREF`` token (e.g. ``"tc_decomp"``); ``None`` if not
            applicable.
        section: ``SECREF`` token (e.g. ``"decomposition"``).
        lean_declaration: Fully-qualified Lean name (e.g.
            ``"Decomposition.entanglement_decomposition"``); ``None``
            for purely-empirical functions with no Lean companion.
        mathlib_proof: ``MathlibProofs`` namespace target (e.g.
            ``"free_energy_decomposition_full"``); ``None`` when no
            ℝ-level discharge exists yet.
        dashboard_invariant: Name of the dashboard invariant that
            enforces this witness on every build, or ``None``.
        description: One-line human-readable description, ≤ 80 chars.
    """

    function: str
    theorem: str | None
    equation: str | None
    section: str
    lean_declaration: str | None
    mathlib_proof: str | None
    dashboard_invariant: str | None
    description: str


# ---------------------------------------------------------------------------
# Registry — every public numerical witness lives here.
#
# Adding a new function:
#   1. Add a ``CrossReference`` entry below, keyed by ``module.function``.
#   2. Ensure the ``theorem`` / ``equation`` / ``section`` tokens exist
#      in ``manuscript/refs/labels.yaml``.
#   3. Ensure ``lean_declaration`` and ``mathlib_proof`` resolve to
#      actual Lean declarations (test_lean_statement_faithfulness.py
#      pins these on every CI run).
# ---------------------------------------------------------------------------

CROSS_REFERENCES: Final[tuple[CrossReference, ...]] = (
    CrossReference(
        function="simulation.inference.coupled_policy_posterior",
        theorem="thm_4_1",
        equation="tc_decomp",
        section="decomposition",
        lean_declaration="Decomposition.entanglement_decomposition",
        mathlib_proof="free_energy_decomposition_full",
        dashboard_invariant="decomposition_lhs_eq_rhs_max_residual",
        description="λ-coupled joint policy posterior; numerical anchor of Theorem 5.1",
    ),
    CrossReference(
        function="simulation.inference.free_energy_bundle",
        theorem="thm_4_1",
        equation="tc_decomp",
        section="pymdp_free_energy",
        lean_declaration="FreeEnergy.totalCorrelation",
        mathlib_proof="free_energy_decomposition_full",
        dashboard_invariant="pymdp_decomposition_residual_max",
        description="Free-energy bundle: VFE/EFE/TC/coupling/entropy at one λ",
    ),
    CrossReference(
        function="simulation.sweep.total_correlation_curve",
        theorem="prop_6_3",
        equation="total_correlation",
        section="pymdp_free_energy",
        lean_declaration="FreeEnergy.totalCorrelation_eq_kl_to_mprojection",
        mathlib_proof="multiInformation_nonneg_at_joint",
        dashboard_invariant="pymdp_total_correlation_lam_4",
        description="I(q_λ) saturation curve; multi-information identity",
    ),
    CrossReference(
        function="simulation.revertibility.m_projection_witness",
        theorem="prop_6_3",
        equation="total_correlation",
        section="empirical",
        lean_declaration="Geometry.mProjection_kl_eq_self_when_meanfield",
        mathlib_proof="entanglement_decomposition_generalK",
        dashboard_invariant="revertibility_kl_equals_multiinformation",
        description="m-projection KL identity witness; D_KL(q‖m̂q)=I(q)",
    ),
    CrossReference(
        function="simulation.rollout.simulate_coupled_rollout",
        theorem="thm_11_1",
        equation=None,
        section="heterogeneous",
        lean_declaration="ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness",
        mathlib_proof=None,
        dashboard_invariant=None,
        description="Coupled deterministic rollout under fixed seed",
    ),
    CrossReference(
        function="simulation.long_horizon.long_horizon_rollout",
        theorem="thm_11_1",
        equation=None,
        section="heterogeneous.habit",
        lean_declaration="ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness",
        mathlib_proof=None,
        dashboard_invariant="long_horizon_steady_state_kl_max",
        description="T=100 long-horizon rollout with habit-accumulation diagnostics",
    ),
    CrossReference(
        function="simulation.multi_k_experiments.run_multi_k_sweep",
        theorem="thm_7_3",
        equation=None,
        section="spectral.multistream_tt",
        lean_declaration="SpectralWitnesses.sparsityRank_tradeoff_witness",
        mathlib_proof=None,
        dashboard_invariant=None,
        description="K∈{3,4,5} ensemble sweep; multi-stream sparsity-rank tradeoff",
    ),
    CrossReference(
        function="simulation.btai_baseline.run_btai_scenario",
        theorem=None,
        equation=None,
        section="discussion",
        lean_declaration=None,
        mathlib_proof=None,
        dashboard_invariant=None,
        description="Branching-Time AIF MCTS baseline; shipped §13 empirical harness",
    ),
    CrossReference(
        function="simulation.adversarial.measure_drift",
        theorem=None,
        equation="closed_form_F",
        section="open_questions",
        lean_declaration=None,
        mathlib_proof=None,
        dashboard_invariant=None,
        description="Bounded-norm adversarial drift on q_λ; §20 Q11 protocol",
    ),
    CrossReference(
        function="simulation.robustness.robustness_scenarios",
        theorem="thm_4_1",
        equation="tc_decomp",
        section="pymdp_validation",
        lean_declaration="Decomposition.entanglement_decomposition",
        mathlib_proof="free_energy_decomposition_full",
        dashboard_invariant="robustness_decomposition_residual_max",
        description="One-axis robustness scenario builder; decomposition residual invariant",
    ),
)


def cross_reference_for(function_name: str) -> CrossReference | None:
    """Return the cross-reference entry for a function, or ``None`` if absent."""
    for entry in CROSS_REFERENCES:
        if entry.function == function_name:
            return entry
    return None


def as_metadata_dict(entry: CrossReference) -> dict[str, str]:
    """Render a cross-reference as a ``str → str`` dict for PNG tEXt metadata.

    The keys are prefixed with ``"project.cross_reference."`` so they
    coexist with other project metadata under
    :data:`visualizations.metadata.FIGURE_METADATA_SCHEMA_VERSION`
    without collision.
    """
    prefix = "project.cross_reference."
    out: dict[str, str] = {f"{prefix}function": entry.function}
    if entry.theorem:
        out[f"{prefix}theorem"] = f"[[THMREF:{entry.theorem}]]"
    if entry.equation:
        out[f"{prefix}equation"] = f"[[EQREF:{entry.equation}]]"
    out[f"{prefix}section"] = f"[[SECREF:{entry.section}]]"
    if entry.lean_declaration:
        out[f"{prefix}lean_declaration"] = entry.lean_declaration
    if entry.mathlib_proof:
        out[f"{prefix}mathlib_proof"] = f"MathlibProofs.{entry.mathlib_proof}"
    if entry.dashboard_invariant:
        out[f"{prefix}dashboard_invariant"] = entry.dashboard_invariant
    out[f"{prefix}description"] = entry.description
    return out


def to_markdown_table() -> str:
    """Render the registry as a markdown table for the manuscript / docs."""
    header = "| Function | Theorem | Equation | Section | Lean | Mathlib Proof | Dashboard Invariant |"
    rule = "|---|---|---|---|---|---|---|"
    rows = [header, rule]
    for entry in CROSS_REFERENCES:
        rows.append(
            "| "
            + " | ".join(
                [
                    entry.function,
                    entry.theorem or "—",
                    entry.equation or "—",
                    entry.section,
                    entry.lean_declaration or "—",
                    entry.mathlib_proof or "—",
                    entry.dashboard_invariant or "—",
                ]
            )
            + " |"
        )
    return "\n".join(rows)


if __name__ == "__main__":  # pragma: no cover
    print(to_markdown_table())
