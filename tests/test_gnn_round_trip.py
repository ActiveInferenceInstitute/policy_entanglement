"""Round-trip tests for the GNN fifth track (`src/gnn/bridge.py`, `runner.py`).

The load-bearing integrity test: the GNN-sourced mutual-information curve
(reconstructed from the parsed coupling via the framework's general
``entangled_posterior`` + ``total_correlation``) must match the *independent*
closed form ``ising_mutual_information`` to ``BERNOULLI_VERIFICATION_TOLERANCE``.

Non-vacuity is proven by a zero-coupling negative control that genuinely FAILS,
and the subtle sign-invariance of mutual information is pinned as a test so a
future contributor cannot mistake J -> -J for a valid negative control.

No mocks — real numpy arithmetic, real parsing of the shipped ``gnn/`` files.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np

from gnn.bridge import (
    build_joint_coupling,
    per_stream_priors,
    reconstruct_mi_curve,
    to_pymdp_config,
)
from gnn.parser import parse_gnn_file
from gnn.runner import compute_roundtrip
from lean.bernoulli_toy import ising_mutual_information  # independent comparison oracle
from simulation.hyperparameters import BERNOULLI_VERIFICATION_TOLERANCE, PARAMETER_SWEEP_LAMBDAS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GNN_DIR = PROJECT_ROOT / "gnn"
TOY = GNN_DIR / "bernoulli_toy.gnn.md"
TOL = float(BERNOULLI_VERIFICATION_TOLERANCE)


def _grid() -> np.ndarray:
    g = PARAMETER_SWEEP_LAMBDAS
    return np.linspace(g.start, g.stop, g.num)


def test_round_trip_matches_closed_form_to_tolerance() -> None:
    """GNN-reconstructed MI == closed-form MI on the canonical lambda grid."""
    model = parse_gnn_file(TOY)
    lambdas = _grid()
    mi_gnn = reconstruct_mi_curve(model, lambdas)
    mi_closed = np.array([ising_mutual_information(float(x)) for x in lambdas])
    max_resid = float(np.abs(mi_gnn - mi_closed).max())
    assert max_resid <= TOL, f"round-trip residual {max_resid} exceeds tolerance {TOL}"


def test_round_trip_negative_control_zero_coupling_fails() -> None:
    """NON-VACUITY: a zero-coupling GNN spec must DIVERGE from the closed form.

    This simultaneously proves (a) the round-trip gate is not vacuous and
    (b) the bridge genuinely sources the coupling from the parsed model
    (a hardcoded Ising matrix would be unaffected by zeroing the file's J).
    """
    model = parse_gnn_file(TOY)
    lambdas = _grid()
    mi_closed = np.array([ising_mutual_information(float(x)) for x in lambdas])

    zero_j = replace(model.variable("J"), value=np.zeros((2, 2)))
    model_zero = replace(model, variables={**model.variables, "J": zero_j})
    mi_zero = reconstruct_mi_curve(model_zero, lambdas)
    max_resid = float(np.abs(mi_zero - mi_closed).max())
    assert max_resid > TOL, "zero-coupling control did not diverge — the round-trip gate is vacuous"
    # Zero coupling decouples the streams: MI is ~0 everywhere.
    assert float(np.abs(mi_zero).max()) < 1e-9


def test_mutual_information_is_sign_invariant_so_sign_flip_is_not_a_control() -> None:
    """J -> -J leaves the mutual information unchanged (only relabels preferred
    configs); pinned so a future contributor does not mistake it for a control."""
    model = parse_gnn_file(TOY)
    lambdas = _grid()
    flipped = replace(model.variable("J"), value=-model.variable("J").matrix())
    model_flip = replace(model, variables={**model.variables, "J": flipped})
    mi_flip = reconstruct_mi_curve(model_flip, lambdas)
    mi_gnn = reconstruct_mi_curve(model, lambdas)
    assert float(np.abs(mi_flip - mi_gnn).max()) <= TOL


def test_wrong_magnitude_coupling_also_diverges() -> None:
    """A coupling of the wrong magnitude (2x) gives the wrong curve."""
    model = parse_gnn_file(TOY)
    lambdas = _grid()
    mi_closed = np.array([ising_mutual_information(float(x)) for x in lambdas])
    doubled = replace(model.variable("J"), value=2.0 * model.variable("J").matrix())
    model_2x = replace(model, variables={**model.variables, "J": doubled})
    mi_2x = reconstruct_mi_curve(model_2x, lambdas)
    assert float(np.abs(mi_2x - mi_closed).max()) > TOL


def test_parsed_coupling_matrix_is_pinned_entrywise_not_just_gap() -> None:
    """The round-trip certifies the gauge-invariant coupling GAP; the literal
    Ising matrix is pinned ENTRYWISE here (Verifier-specialist Q4).

    A gap-equivalent but wrong matrix (e.g. the identity) reproduces the MI
    curve to tolerance — so the MI round-trip alone cannot distinguish it — but
    it is NOT the documented Ising matrix and must be caught at the matrix level.
    """
    from lean.bernoulli_toy import ising_coupling

    model = parse_gnn_file(TOY)
    parsed_j = model.variable("J").matrix()
    # Entrywise commitment: the parsed coupling IS the documented Ising matrix.
    np.testing.assert_allclose(parsed_j, ising_coupling())

    # A gap-equivalent wrong matrix (identity: aligned-minus-anti gap also 1.0)
    # passes the MI round-trip but is provably NOT the documented matrix.
    lambdas = _grid()
    mi_closed = np.array([ising_mutual_information(float(x)) for x in lambdas])
    identity = replace(model.variable("J"), value=np.array([[1.0, 0.0], [0.0, 1.0]]))
    model_id = replace(model, variables={**model.variables, "J": identity})
    mi_id = reconstruct_mi_curve(model_id, lambdas)
    assert float(np.abs(mi_id - mi_closed).max()) <= TOL  # MI cannot distinguish (gauge invariance)
    assert not np.allclose(identity.matrix(), ising_coupling())  # but the matrix check can


def test_reconstructed_posterior_is_normalized() -> None:
    """Every reconstructed joint posterior is a valid PMF."""
    from gnn.bridge import entangled_joint

    model = parse_gnn_file(TOY)
    for lam in (0.0, 1.0, 3.0, 6.0):
        q = entangled_joint(model, lam)
        assert abs(float(q.sum()) - 1.0) < 1e-12
        assert float(q.min()) >= 0.0


def test_k3_chain_joint_coupling_composes_additively() -> None:
    """The K=3 chain coupling = J12 (broadcast) + J23 (broadcast)."""
    model = parse_gnn_file(GNN_DIR / "k_stream_ensemble.gnn.md")
    jc = build_joint_coupling(model)
    assert jc.shape == (2, 2, 2)
    # All-aligned (0,0,0): J12[0,0] + J23[0,0] = 0.5 + 0.5 = 1.0
    assert jc[0, 0, 0] == 1.0
    # (0,1,0): J12[0,1] + J23[1,0] = -0.5 + -0.5 = -1.0
    assert jc[0, 1, 0] == -1.0
    assert len(per_stream_priors(model)) == 3


def test_to_pymdp_config_sources_from_gnn() -> None:
    """The GNN->pymdp config dict reflects the parsed declarations."""
    cfg = to_pymdp_config(parse_gnn_file(TOY))
    assert cfg["num_streams"] == 2
    assert cfg["policy_cardinality_per_stream"] == 2
    assert cfg["joint_coupling"] == [[0.5, -0.5], [-0.5, 0.5]]
    assert cfg["gamma"] == 0.0


def test_compute_roundtrip_payload_records_negative_control() -> None:
    """The sidecar payload embeds the non-vacuity negative-control evidence."""
    payload = compute_roundtrip(GNN_DIR)
    assert payload["round_trip_passes"] is True
    assert payload["max_abs_residual"] <= TOL
    assert payload["negative_control_discriminates"] is True
    assert payload["negative_control_zero_coupling_max_residual"] > TOL
    assert len(payload["rows"]) == PARAMETER_SWEEP_LAMBDAS.num
