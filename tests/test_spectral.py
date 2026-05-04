"""Tests for src/spectral.py."""
from __future__ import annotations

import numpy as np
import pytest

from joint_dist import mean_field_to_joint
from spectral import (
    Archetype,
    archetype_marginal_pattern,
    entanglement_entropy,
    entanglement_spectrum,
    schmidt_decomposition,
    schmidt_rank,
    schmidt_rank_one_iff_mean_field,
    tensor_train_ranks,
)


def test_schmidt_rank_one_for_outer_product():
    m = (np.array([0.6, 0.4]), np.array([0.3, 0.7]))
    q = mean_field_to_joint(m)
    assert schmidt_rank(q) == 1


def test_schmidt_rank_two_for_correlated_joint():
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    assert schmidt_rank(q) == 2


def test_schmidt_rank_requires_K2():
    q = np.full((2, 2, 2), 0.125)
    with pytest.raises(ValueError, match="K=2"):
        schmidt_rank(q)


def test_schmidt_decomposition_returns_archetype_modes():
    q = np.array([[0.3, 0.1], [0.2, 0.4]])
    modes = schmidt_decomposition(q)
    assert all(isinstance(m, Archetype) for m in modes)
    # Reconstruct the matrix from the SVD modes; should equal q
    reconstructed = sum(m.weight * np.outer(m.u, m.v) for m in modes)
    assert np.allclose(reconstructed, q, atol=1e-12)


def test_schmidt_decomposition_K2_requirement():
    with pytest.raises(ValueError, match="K=2"):
        schmidt_decomposition(np.zeros((2, 2, 2)))


def test_entanglement_entropy_zero_for_outer_product():
    m = (np.array([0.5, 0.5]), np.array([0.5, 0.5]))
    q = mean_field_to_joint(m)
    assert abs(entanglement_entropy(q)) < 1e-12


def test_entanglement_entropy_positive_for_correlated():
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    S = entanglement_entropy(q)
    assert S > 0.0
    # Two equal singular values -> p = (0.5, 0.5) -> S = log 2
    assert abs(S - np.log(2.0)) < 1e-12


def test_entanglement_entropy_K2_requirement():
    with pytest.raises(ValueError, match="K=2"):
        entanglement_entropy(np.zeros((2, 2, 2)))


def test_schmidt_rank_one_iff_mean_field_holds_for_outer_product():
    m = (np.array([0.7, 0.3]), np.array([0.4, 0.6]))
    q = mean_field_to_joint(m)
    assert schmidt_rank_one_iff_mean_field(q)


def test_schmidt_rank_one_iff_mean_field_holds_for_correlated():
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    assert schmidt_rank_one_iff_mean_field(q)


def test_tensor_train_ranks_3_stream_uniform():
    q = np.full((2, 2, 2), 0.125)
    ranks = tensor_train_ranks(q)
    # Uniform joint factorises perfectly -> rank 1 across each cut
    assert ranks == [1, 1]


def test_tensor_train_ranks_K1_returns_empty():
    q = np.array([0.6, 0.4])
    assert tensor_train_ranks(q) == []


def test_entanglement_spectrum_alias_matches_tt_ranks():
    q = np.full((2, 2, 2), 0.125)
    assert entanglement_spectrum(q) == tensor_train_ranks(q)


def test_archetype_marginal_pattern_returns_unit_vectors():
    q = np.array([[0.4, 0.1], [0.2, 0.3]])
    modes = schmidt_decomposition(q)
    u, v = archetype_marginal_pattern(modes[0])
    assert abs(np.linalg.norm(u) - 1.0) < 1e-12
    assert abs(np.linalg.norm(v) - 1.0) < 1e-12


def test_schmidt_decomposition_descending_weights():
    q = np.array([[0.4, 0.1], [0.2, 0.3]])
    modes = schmidt_decomposition(q)
    weights = [m.weight for m in modes]
    assert weights == sorted(weights, reverse=True)


def test_tensor_train_ranks_correlated_K3():
    """Pure entangled K=3 joint should have higher TT rank."""
    q = np.zeros((2, 2, 2))
    q[0, 0, 0] = 0.5
    q[1, 1, 1] = 0.5
    ranks = tensor_train_ranks(q)
    assert ranks[0] == 2


def test_schmidt_decomposition_breaks_on_subthreshold_singular_value():
    """A rank-1 K=2 joint has a single positive singular value; the
    `if sv <= atol: break` path covers the second iteration."""
    from spectral import schmidt_decomposition
    mf = np.array([[0.5, 0.0], [0.5, 0.0]])  # column-stochastic outer prod
    archs = schmidt_decomposition(mf, atol=1e-9)
    # Exactly one non-zero singular value above atol.
    assert len(archs) == 1


def test_entanglement_entropy_zero_total_short_circuit():
    """A degenerate all-zero matrix has total singular-value mass 0;
    the function should short-circuit to 0.0 (covers the
    `if total <= atol: return 0.0` branch)."""
    from spectral import entanglement_entropy
    q = np.zeros((2, 2))
    assert entanglement_entropy(q) == 0.0
