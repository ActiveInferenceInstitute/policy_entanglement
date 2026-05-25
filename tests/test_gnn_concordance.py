"""GNN concordance parity test — the fifth track of the symbol concordance.

Asserts every standing framework symbol of the K=2 toy has a GNN representation
(a declared variable bound to an Active Inference Ontology term). The negative
control removes one binding and confirms the parity check FAILS, so the test is
proven non-vacuous (``feedback-shape-tests-dont-bind-truth``).
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from gnn.model import GnnModel
from gnn.parser import parse_gnn_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOY = PROJECT_ROOT / "gnn" / "bernoulli_toy.gnn.md"

# Standing framework symbols (manuscript concordance) -> GNN variable name.
# Each must be a declared GNN variable carrying an Ontology annotation.
SYMBOL_TO_GNN: dict[str, str] = {
    "pi^1 (stream-1 policy)": "pi1",
    "pi^2 (stream-2 policy)": "pi2",
    "E^1 (stream-1 habit)": "E1",
    "E^2 (stream-2 habit)": "E2",
    "J (cross-stream coupling)": "J",
    "lambda (deformation)": "lam",
    "gamma (sophistication)": "gamma",
    "q (entangled joint posterior)": "q_joint",
}


def _parity_gaps(model: GnnModel) -> list[str]:
    """Return the symbols lacking a declared+annotated GNN representation."""
    gaps: list[str] = []
    for symbol, var in SYMBOL_TO_GNN.items():
        if not model.has(var):
            gaps.append(f"{symbol}: variable {var!r} not declared")
        elif var not in model.ontology:
            gaps.append(f"{symbol}: variable {var!r} has no Ontology annotation")
    return gaps


def test_every_standing_symbol_has_a_gnn_representation() -> None:
    """Concordance parity: all standing K=2 symbols are GNN-represented."""
    model = parse_gnn_file(TOY)
    gaps = _parity_gaps(model)
    assert not gaps, f"GNN concordance gaps: {gaps}"


def test_concordance_parity_is_non_vacuous() -> None:
    """NEGATIVE CONTROL: dropping a GNN ontology binding fails the parity check."""
    model = parse_gnn_file(TOY)
    broken_ontology = {k: v for k, v in model.ontology.items() if k != "J"}
    broken = replace(model, ontology=broken_ontology)
    gaps = _parity_gaps(broken)
    assert gaps, "parity check passed with J's ontology removed — it is vacuous"
    assert any("J" in g for g in gaps)


def test_ontology_terms_are_distinct_and_meaningful() -> None:
    """The cross-stream coupling and deformation carry distinct ontology terms."""
    model = parse_gnn_file(TOY)
    assert model.ontology["J"] == "CrossStreamCouplingPotential"
    assert model.ontology["lam"] == "EntanglementDeformationParameter"
    assert model.ontology["pi1"] != model.ontology["pi2"]


@pytest.mark.parametrize("var", list(SYMBOL_TO_GNN.values()))
def test_each_mapped_variable_is_declared(var: str) -> None:
    model = parse_gnn_file(TOY)
    assert model.has(var)
