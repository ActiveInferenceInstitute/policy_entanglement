"""Tests for src/lean/spectral.py."""

from __future__ import annotations

import numpy as np
import pytest

from lean.joint_dist import mean_field_to_joint
from lean.spectral import (
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
    # Uniform joint factorizes perfectly -> rank 1 across each cut
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
    from lean.spectral import schmidt_decomposition

    mf = np.array([[0.5, 0.0], [0.5, 0.0]])  # column-stochastic outer prod
    archs = schmidt_decomposition(mf, atol=1e-9)
    # Exactly one non-zero singular value above atol.
    assert len(archs) == 1


def test_entanglement_entropy_zero_total_short_circuit():
    """A degenerate all-zero matrix has total singular-value mass 0;
    the function should short-circuit to 0.0 (covers the
    `if total <= atol: return 0.0` branch)."""
    from lean.spectral import entanglement_entropy

    q = np.zeros((2, 2))
    assert entanglement_entropy(q) == 0.0


# --- entanglement_entropy_per_cut (S06 symbol S_k) — analytic-value tests ---


def test_per_cut_matches_entanglement_entropy_for_K2():
    """For K=2 the only cut (k=0) must equal the all-streams entropy."""
    from lean.spectral import entanglement_entropy, entanglement_entropy_per_cut

    q = np.array([[0.4, 0.1], [0.2, 0.3]])
    assert entanglement_entropy_per_cut(q, 0) == pytest.approx(entanglement_entropy(q))


def test_per_cut_zero_for_mean_field_product_K3():
    """A rank-1 product (mean-field) joint has zero bond entropy at every cut."""
    from lean.spectral import entanglement_entropy_per_cut

    a, b, c = np.array([0.6, 0.4]), np.array([0.3, 0.7]), np.array([0.5, 0.5])
    q = np.einsum("i,j,k->ijk", a, b, c)
    assert entanglement_entropy_per_cut(q, 0) == pytest.approx(0.0, abs=1e-9)
    assert entanglement_entropy_per_cut(q, 1) == pytest.approx(0.0, abs=1e-9)


def test_per_cut_maximally_correlated_bell_is_log2():
    """The maximally-correlated 2x2 joint has two equal singular values
    (0.5, 0.5) -> p=(0.5,0.5) -> S = -2*0.5*ln 0.5 = ln 2."""
    from lean.spectral import entanglement_entropy_per_cut

    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    assert entanglement_entropy_per_cut(q, 0) == pytest.approx(np.log(2.0))


def test_per_cut_raises_on_out_of_range_cut():
    from lean.spectral import entanglement_entropy_per_cut

    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    with pytest.raises(ValueError):
        entanglement_entropy_per_cut(q, 1)  # K=2 -> only k=0 valid
    with pytest.raises(ValueError):
        entanglement_entropy_per_cut(np.array([0.5, 0.5]), 0)  # ndim<2


# --- mps_decomposition (S06 symbol A^{(k)}) — reconstruction is the invariant ---


def _contract_mps(factors):
    cur = factors[0].reshape(factors[0].shape[1], factors[0].shape[2])
    for a in factors[1:]:
        cur = np.tensordot(cur, a, axes=([cur.ndim - 1], [0]))
    return cur.reshape(cur.shape[:-1])


def test_mps_reconstructs_general_K3_tensor():
    """Load-bearing invariant: contracting the MPS factors returns `q`."""
    from lean.spectral import mps_decomposition

    rng = np.random.default_rng(20260518)
    q = rng.random((2, 3, 2))
    q = q / q.sum()
    factors = mps_decomposition(q)
    assert len(factors) == 3
    assert factors[0].shape[0] == 1 and factors[-1].shape[2] == 1
    np.testing.assert_allclose(_contract_mps(factors), q, atol=1e-10)


def test_mps_rank1_product_has_unit_bond_and_reconstructs():
    from lean.joint_dist import mean_field_to_joint
    from lean.spectral import mps_decomposition

    q = mean_field_to_joint((np.array([0.6, 0.4]), np.array([0.3, 0.7])))
    factors = mps_decomposition(q)
    assert factors[0].shape[2] == 1  # bond dim 1 for a product
    np.testing.assert_allclose(_contract_mps(factors), q, atol=1e-12)


def test_mps_K2_middle_bond_equals_schmidt_rank():
    """Convention anchor: for K=2 the single bond dim == schmidt_rank(q)."""
    from lean.spectral import mps_decomposition, schmidt_rank

    q = np.array([[0.5, 0.0], [0.0, 0.5]])  # schmidt rank 2
    factors = mps_decomposition(q)
    assert factors[0].shape[2] == schmidt_rank(q) == 2
