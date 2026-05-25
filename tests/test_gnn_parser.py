"""Tests for the project-owned GNN v1.1 parser (`src/gnn/parser.py`, `model.py`).

No mocks — every test parses real GNN source text or the shipped ``gnn/*.gnn.md``
files. Negative controls exercise every :class:`GNNParseError` path so the
parser's validation is proven non-vacuous.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from gnn.model import GnnConnection, GnnVariable
from gnn.parser import GNNParseError, parse_gnn, parse_gnn_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOY = PROJECT_ROOT / "gnn" / "bernoulli_toy.gnn.md"
K3 = PROJECT_ROOT / "gnn" / "k_stream_ensemble.gnn.md"

MINIMAL = """\
## GNNSection
M
## GNNVersionAndFlags
GNN v1.1
## ModelName
Minimal
## StateSpaceBlock
A[2,2,type=float]
## Connections
A-A
## InitialParameterization
A={
  (0.5, -0.5),
  (-0.5, 0.5)
}
## ActInf Ontology Annotation
A=CrossStreamCouplingPotential
## ModelParameters
num_streams: 2
"""


def test_parse_shipped_toy_structure() -> None:
    """The shipped K=2 toy parses with the expected streams and coupling."""
    m = parse_gnn_file(TOY)
    assert m.section == "ActInfPolicyEntanglement_K2_Ising"
    assert m.version.startswith("GNN v1")
    assert m.num_streams == 2
    assert m.has("J") and m.has("pi1") and m.has("pi2")
    np.testing.assert_allclose(m.variable("J").matrix(), [[0.5, -0.5], [-0.5, 0.5]])
    np.testing.assert_allclose(m.variable("E1").vector(), [0.5, 0.5])
    assert m.variable("lam").scalar() == 0.0


def test_parse_connections_directed_undirected_and_labels() -> None:
    """Edges parse with direction and optional v1.1 ``:label`` annotations."""
    m = parse_gnn_file(TOY)
    edges = {(c.source, c.target, c.directed, c.label) for c in m.connections}
    assert ("E1", "pi1", True, None) in edges
    assert ("pi1", "J", False, "cross_stream_coupling") in edges
    assert ("J", "q_joint", True, "coupling") in edges
    assert m.edges_for("J")  # J participates in edges


def test_ontology_and_model_parameters() -> None:
    """Ontology bindings and ModelParameters key:value pairs parse."""
    m = parse_gnn_file(TOY)
    assert m.ontology["J"] == "CrossStreamCouplingPotential"
    assert m.ontology["lam"] == "EntanglementDeformationParameter"
    assert m.model_parameters["num_streams"] == "2"


def test_k3_ensemble_parses_pairwise_couplings() -> None:
    """The K=3 chain ensemble parses three streams and two pairwise couplings."""
    m = parse_gnn_file(K3)
    assert m.num_streams == 3
    assert m.has("J12") and m.has("J23")
    np.testing.assert_allclose(m.variable("J12").matrix(), [[0.5, -0.5], [-0.5, 0.5]])


def test_minimal_string_parses() -> None:
    m = parse_gnn(MINIMAL)
    assert m.section == "M"
    np.testing.assert_allclose(m.variable("A").matrix(), [[0.5, -0.5], [-0.5, 0.5]])


# --- Negative controls: each GNNParseError path -------------------------------


def test_missing_required_section_raises() -> None:
    with pytest.raises(GNNParseError, match="missing required section"):
        parse_gnn("## GNNSection\nX\n## ModelName\nM")


def test_dimension_mismatch_raises() -> None:
    """A parameterization whose element count != declared dims is rejected."""
    bad = MINIMAL.replace("A={\n  (0.5, -0.5),\n  (-0.5, 0.5)\n}", "A={(1.0, 2.0)}")
    with pytest.raises(GNNParseError, match="GNN-E002|elements"):
        parse_gnn(bad)


def test_missing_type_declaration_raises() -> None:
    bad = MINIMAL.replace("A[2,2,type=float]", "A[2,2]")
    with pytest.raises(GNNParseError, match="missing required 'type='"):
        parse_gnn(bad)


def test_named_dimension_reference_raises() -> None:
    bad = MINIMAL.replace("A[2,2,type=float]", "A[num_obs,2,type=float]")
    with pytest.raises(GNNParseError, match="named-dimension"):
        parse_gnn(bad)


def test_malformed_declaration_raises() -> None:
    bad = MINIMAL.replace("A[2,2,type=float]", "A 2 2 float")
    with pytest.raises(GNNParseError, match="malformed StateSpaceBlock"):
        parse_gnn(bad)


def test_malformed_connection_raises() -> None:
    bad = MINIMAL.replace("A-A", "A ?? A")
    with pytest.raises(GNNParseError, match="malformed connection"):
        parse_gnn(bad)


def test_unbalanced_braces_raises() -> None:
    bad = MINIMAL.replace("A={\n  (0.5, -0.5),\n  (-0.5, 0.5)\n}", "A={(0.5, -0.5)")
    with pytest.raises(GNNParseError):
        parse_gnn(bad)


def test_no_integer_dims_raises() -> None:
    bad = MINIMAL.replace("A[2,2,type=float]", "A[type=float]")
    with pytest.raises(GNNParseError, match="no integer dimensions"):
        parse_gnn(bad)


# --- model.py accessors -------------------------------------------------------


def test_variable_lookup_missing_raises() -> None:
    m = parse_gnn(MINIMAL)
    with pytest.raises(KeyError):
        m.variable("does_not_exist")


def test_gnn_variable_scalar_and_value_errors() -> None:
    v = GnnVariable(name="x", dims=(2, 2), dtype="float", value=None)
    assert v.size == 4
    with pytest.raises(ValueError, match="no InitialParameterization"):
        v.matrix()
    with pytest.raises(ValueError, match="no InitialParameterization"):
        v.vector()
    nonscalar = GnnVariable(name="y", dims=(2,), dtype="float", value=np.array([1.0, 2.0]))
    with pytest.raises(ValueError, match="not a scalar"):
        nonscalar.scalar()


def test_gnn_connection_dataclass() -> None:
    c = GnnConnection(source="a", target="b", directed=True, label="x")
    assert c.source == "a" and c.target == "b" and c.directed and c.label == "x"
