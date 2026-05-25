"""Tests for simulation/specs.py.

These tests exercise the framework-independent record types and do
*not* require the pymdp ``sim`` group — they run on every CI matrix
entry.
"""

from __future__ import annotations

import numpy as np
import pytest

from simulation.builders import (
    ising_coupling_tensor,
    make_bernoulli_stream,
    make_ising_ensemble,
    two_action_swap_transitions,
    two_state_identity_likelihood,
)
from simulation.specs import CoupledEnsembleSpec, StreamSpec


def _good_stream(name: str = "s0") -> StreamSpec:
    return make_bernoulli_stream(name=name)


def test_two_state_identity_likelihood_columns_sum_to_one() -> None:
    A = two_state_identity_likelihood(3)
    assert A.shape == (3, 3)
    assert np.allclose(A.sum(axis=0), 1.0)


def test_two_action_swap_transitions_preserves_and_swaps() -> None:
    B = two_action_swap_transitions(2)
    assert B.shape == (2, 2, 2)
    assert np.allclose(B[:, :, 0], np.eye(2))
    # Action 1 maps state 0 -> state 1.
    assert np.argmax(B[:, 0, 1]) == 1


def test_two_action_swap_transitions_rejects_singleton() -> None:
    with pytest.raises(ValueError):
        two_action_swap_transitions(1)


def test_make_bernoulli_stream_validates() -> None:
    s = _good_stream()
    s.validate()
    assert s.num_obs() == 2
    assert s.num_states() == 2
    assert s.num_controls() == 2


def test_stream_validate_rejects_bad_A_shape() -> None:
    bad = StreamSpec(
        A=np.array([1.0, 0.0]),  # 1-D
        B=two_action_swap_transitions(2),
        C=np.zeros(2),
        D=np.array([0.5, 0.5]),
    )
    with pytest.raises(ValueError, match="A must be 2-D"):
        bad.validate()


def test_stream_validate_rejects_non_stochastic_A() -> None:
    bad = StreamSpec(
        A=np.array([[0.5, 0.4], [0.5, 0.5]]),  # cols don't sum to 1
        B=two_action_swap_transitions(2),
        C=np.zeros(2),
        D=np.array([0.5, 0.5]),
    )
    with pytest.raises(ValueError, match="A columns must sum to 1"):
        bad.validate()


def test_stream_validate_rejects_non_stochastic_D() -> None:
    bad = StreamSpec(
        A=two_state_identity_likelihood(2),
        B=two_action_swap_transitions(2),
        C=np.zeros(2),
        D=np.array([0.5, 0.4]),
    )
    with pytest.raises(ValueError, match="D must sum to 1"):
        bad.validate()


def test_stream_validate_rejects_C_shape_mismatch() -> None:
    bad = StreamSpec(
        A=two_state_identity_likelihood(2),
        B=two_action_swap_transitions(2),
        C=np.zeros(3),
        D=np.array([0.5, 0.5]),
    )
    with pytest.raises(ValueError, match="C shape"):
        bad.validate()


def test_stream_validate_rejects_D_shape_mismatch() -> None:
    bad = StreamSpec(
        A=two_state_identity_likelihood(2),
        B=two_action_swap_transitions(2),
        C=np.zeros(2),
        D=np.array([1.0]),
    )
    with pytest.raises(ValueError, match="D shape"):
        bad.validate()


def test_stream_validate_rejects_non_stochastic_B_action() -> None:
    B_bad = two_action_swap_transitions(2).copy()
    B_bad[:, 0, 1] = [0.5, 0.4]  # column 0 of action 1 doesn't sum to 1
    bad = StreamSpec(
        A=two_state_identity_likelihood(2),
        B=B_bad,
        C=np.zeros(2),
        D=np.array([0.5, 0.5]),
    )
    with pytest.raises(ValueError, match="columns must sum to 1"):
        bad.validate()


def test_stream_validate_rejects_3d_B_with_mismatched_states() -> None:
    bad = StreamSpec(
        A=two_state_identity_likelihood(2),
        B=np.eye(3)[..., None],  # ndim=3 but mismatched
        C=np.zeros(2),
        D=np.array([0.5, 0.5]),
    )
    with pytest.raises(ValueError, match="A num_states"):
        bad.validate()


def test_stream_validate_rejects_non_square_B() -> None:
    """Cover the `B.shape[0] != B.shape[1]` early-out branch in
    `StreamSpec.validate` (line 56)."""
    bad = StreamSpec(
        A=two_state_identity_likelihood(2),
        B=np.zeros((2, 3, 2)),  # ndim=3 but not square
        C=np.zeros(2),
        D=np.array([0.5, 0.5]),
    )
    with pytest.raises(ValueError, match="B must be"):
        bad.validate()


def test_ising_coupling_tensor_K2_matches_manuscript() -> None:
    Kp = ising_coupling_tensor((2, 2), scale=1.0)
    # Mean zero, max abs 1, alignment-promoting.
    assert np.isclose(Kp.mean(), 0.0)
    assert np.isclose(np.abs(Kp).max(), 1.0)
    assert Kp[0, 0] > 0 and Kp[1, 1] > 0
    assert Kp[0, 1] < 0 and Kp[1, 0] < 0


def test_ising_coupling_tensor_K3_alignment_pattern() -> None:
    Kp = ising_coupling_tensor((2, 2, 2), scale=1.0)
    assert Kp.shape == (2, 2, 2)
    # All-zero or all-one corner should be a maximum.
    assert Kp[0, 0, 0] == np.max(Kp)
    assert Kp[1, 1, 1] == np.max(Kp)


def test_ising_coupling_tensor_rejects_K1() -> None:
    with pytest.raises(ValueError):
        ising_coupling_tensor((2,), scale=1.0)


def test_ising_coupling_tensor_zero_scale_returns_zero() -> None:
    Kp = ising_coupling_tensor((2, 2), scale=0.0)
    assert np.allclose(Kp, 0.0)


def test_make_ising_ensemble_default_k2() -> None:
    spec = make_ising_ensemble()
    assert spec.num_streams() == 2
    assert spec.policy_shape() == (2, 2)
    spec.validate()


def test_make_ising_ensemble_K3() -> None:
    spec = make_ising_ensemble(num_streams=3, gamma=0.5, coupling_amplitude=2.0)
    assert spec.num_streams() == 3
    assert spec.policy_shape() == (2, 2, 2)
    assert spec.gamma == 0.5
    assert spec.coupling_j.shape == (2, 2, 2)


def test_coupled_ensemble_validate_rejects_empty_streams() -> None:
    bad = CoupledEnsembleSpec(
        streams=tuple(),
        coupling_j=np.zeros((2,)),
        coupling_kc=np.zeros((2,)),
    )
    with pytest.raises(ValueError, match="non-empty"):
        bad.validate()


def test_coupled_ensemble_validate_rejects_negative_gamma() -> None:
    bad = CoupledEnsembleSpec(
        streams=(_good_stream(),),
        coupling_j=np.zeros((2,)),
        coupling_kc=np.zeros((2,)),
        gamma=-0.5,
    )
    with pytest.raises(ValueError, match="gamma"):
        bad.validate()


def test_coupled_ensemble_validate_rejects_J_shape_mismatch() -> None:
    bad = CoupledEnsembleSpec(
        streams=(_good_stream(), _good_stream("s1")),
        coupling_j=np.zeros((3, 2)),
        coupling_kc=np.zeros((2, 2)),
    )
    with pytest.raises(ValueError, match="coupling_j shape"):
        bad.validate()


def test_coupled_ensemble_validate_rejects_Kc_shape_mismatch() -> None:
    bad = CoupledEnsembleSpec(
        streams=(_good_stream(), _good_stream("s1")),
        coupling_j=np.zeros((2, 2)),
        coupling_kc=np.zeros((2, 3)),
    )
    with pytest.raises(ValueError, match="coupling_kc shape"):
        bad.validate()


def test_coupled_ensemble_validate_propagates_stream_errors() -> None:
    bad_stream = StreamSpec(
        A=np.array([[0.5, 0.4], [0.5, 0.5]]),  # bad cols
        B=two_action_swap_transitions(2),
        C=np.zeros(2),
        D=np.array([0.5, 0.5]),
        name="broken",
    )
    bad = CoupledEnsembleSpec(
        streams=(bad_stream,),
        coupling_j=np.zeros((2,)),
        coupling_kc=np.zeros((2,)),
    )
    with pytest.raises(ValueError, match="stream\\[0\\] 'broken'"):
        bad.validate()
