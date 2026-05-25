"""Validation / error-path tests for the GNN bridge (negative controls).

These exercise the bridge and parser guards on genuinely malformed inputs, and
prove the *pipeline stage itself* (``gnn.runner.run``) returns non-zero on a
wrong-coupling GNN source — a non-vacuity check one level above the unit test.
No mocks; real parsing and arithmetic.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from gnn.bridge import build_joint_coupling, per_stream_priors
from gnn.parser import parse_gnn, parse_gnn_file
from gnn.runner import SIDECAR_NAME, run

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GNN_DIR = PROJECT_ROOT / "gnn"
TOY = GNN_DIR / "bernoulli_toy.gnn.md"

_STREAMLESS = """\
## GNNSection
S
## GNNVersionAndFlags
GNN v1.1
## ModelName
Streamless
## StateSpaceBlock
J[2,2,type=float]
## Connections
J-J
## InitialParameterization
J={(0.5,-0.5),(-0.5,0.5)}
"""

_NO_COUPLING = """\
## GNNSection
NC
## GNNVersionAndFlags
GNN v1.1
## ModelName
NoCoupling
## StateSpaceBlock
pi1[2,1,type=float]
pi2[2,1,type=float]
E1[2,1,type=float]
E2[2,1,type=float]
## Connections
E1>pi1
## InitialParameterization
E1={(0.5,0.5)}
E2={(0.5,0.5)}
"""


def test_per_stream_priors_streamless_raises() -> None:
    with pytest.raises(ValueError, match="no policy streams"):
        per_stream_priors(parse_gnn(_STREAMLESS))


def test_build_joint_coupling_no_coupling_variable_raises() -> None:
    with pytest.raises(ValueError, match="no coupling variable"):
        build_joint_coupling(parse_gnn(_NO_COUPLING))


def test_build_joint_coupling_k2_shape_mismatch_raises() -> None:
    """A K=2 model whose J is not (2,2) is rejected."""
    model = parse_gnn_file(TOY)
    wrong = replace(model.variable("J"), dims=(2, 2), value=np.zeros((2, 2)))
    # Force a 3x3 J via a fresh variable of the wrong declared cardinality.
    from gnn.model import GnnVariable

    big = GnnVariable(name="J", dims=(3, 3), dtype="float", value=np.zeros((3, 3)))
    broken = replace(model, variables={**model.variables, "J": big})
    with pytest.raises(ValueError, match="coupling J shape"):
        build_joint_coupling(broken)
    assert wrong.dims == (2, 2)  # sanity on the helper


def test_pairwise_coupling_out_of_range_raises() -> None:
    """A K=2 model carrying a J13 edge (stream 3 absent) is rejected."""
    from gnn.model import GnnVariable

    model = parse_gnn(_NO_COUPLING)  # has pi1, pi2 only
    j13 = GnnVariable(name="J13", dims=(2, 2), dtype="float", value=np.zeros((2, 2)))
    broken = replace(model, variables={**model.variables, "J13": j13})
    with pytest.raises(ValueError, match="indexes streams outside"):
        build_joint_coupling(broken)


def test_parser_garbage_parameterization_raises() -> None:
    from gnn.parser import GNNParseError

    bad = _STREAMLESS.replace("J={(0.5,-0.5),(-0.5,0.5)}", "J={(alpha, beta), (gamma, delta)}")
    with pytest.raises(GNNParseError, match="cannot parse InitialParameterization"):
        parse_gnn(bad)


def test_parser_accepts_default_hint_and_ontology_alias() -> None:
    """A ``default=`` hint is preserved-ignored; ``ActInfOntologyAnnotation``
    (no spaces) is accepted as an alias."""
    src = """\
## GNNSection
A
## GNNVersionAndFlags
GNN v1.1
## ModelName
Aliased
## StateSpaceBlock
D[2,1,type=float,default=uniform]
## Connections
D>D
## InitialParameterization
D={(0.5,0.5)}
## ActInfOntologyAnnotation
D=Prior
## ModelParameters
junk_line_without_separator
num: 1
"""
    m = parse_gnn(src)
    assert m.ontology["D"] == "Prior"
    assert m.model_parameters["num"] == "1"
    assert "junk_line_without_separator" not in m.model_parameters


def test_gnn_var_range_gate_is_non_vacuous() -> None:
    """The GNN VAR range gate passes the real values and FAILS wrong ones.

    Proves (ISA ISC-40) that the gate added to ``REQUIRED_VARIABLES`` /
    ``EXPECTED_RANGES`` discriminates: a wrong round-trip residual is rejected,
    and a *vacuous* negative-control residual (≈0, meaning the control no longer
    diverges) is also rejected by its lower bound.
    """
    from manuscript.output_gates.constants import REQUIRED_VARIABLES
    from manuscript.validation import validate_variables_against_ranges

    gnn_ranges = {k: v for k, v in REQUIRED_VARIABLES.items() if k.startswith("gnn_")}
    assert gnn_ranges, "no gnn_ range gates registered"

    good = {
        "gnn_roundtrip_max_residual": 7.77e-16,
        "gnn_negative_control_max_residual": 0.6758,
        "gnn_round_trip_lambda_points": 121.0,
        "gnn_num_streams": 2.0,
    }
    assert validate_variables_against_ranges(good, gnn_ranges) == {}

    # Wrong round-trip residual (round-trip silently broke) -> rejected.
    bad_resid = {**good, "gnn_roundtrip_max_residual": 0.5}
    assert "gnn_roundtrip_max_residual" in validate_variables_against_ranges(bad_resid, gnn_ranges)

    # Vacuous negative control (zero-coupling no longer diverges) -> rejected.
    vacuous = {**good, "gnn_negative_control_max_residual": 0.0}
    assert "gnn_negative_control_max_residual" in validate_variables_against_ranges(vacuous, gnn_ranges)


def test_pipeline_stage_returns_nonzero_on_wrong_coupling(tmp_path: Path) -> None:
    """NON-VACUITY at the pipeline level: a wrong-J GNN source makes the stage fail."""
    bad_gnn_dir = tmp_path / "gnn"
    bad_gnn_dir.mkdir()
    text = TOY.read_text()
    # Halve the coupling magnitude -> wrong curve -> round-trip must fail.
    text = text.replace(
        "J={\n  (0.5, -0.5),\n  (-0.5, 0.5)\n}",
        "J={\n  (0.1, -0.1),\n  (-0.1, 0.1)\n}",
    )
    (bad_gnn_dir / "bernoulli_toy.gnn.md").write_text(text)
    rc = run(
        data_dir=tmp_path / "data",
        fig_dir=tmp_path / "fig",
        gnn_dir=bad_gnn_dir,
        lean_out=tmp_path / "x.lean",
    )
    assert rc == 1
    import json

    payload = json.loads((tmp_path / "data" / SIDECAR_NAME).read_text())
    assert payload["round_trip_passes"] is False
