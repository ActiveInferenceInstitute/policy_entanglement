"""Tests for src/joint_dist.py.

Real numerical examples; no mocks per the project's no-mocks policy.
"""
from __future__ import annotations

import numpy as np
import pytest

from joint_dist import (
    is_mean_field,
    is_non_negative,
    is_pmf,
    joint_marginal,
    joint_marginals,
    m_projection,
    mean_field_to_joint,
    normalize,
)


def test_is_pmf_accepts_uniform_2x2():
    q = np.full((2, 2), 0.25, dtype=np.float64)
    assert is_pmf(q)
    assert is_non_negative(q)


def test_is_pmf_rejects_unnormalised():
    q = np.full((2, 2), 0.3, dtype=np.float64)
    assert not is_pmf(q)


def test_is_pmf_rejects_negative_entries():
    q = np.array([[0.6, -0.1], [0.3, 0.2]])
    assert not is_pmf(q)
    assert not is_non_negative(q)


def test_normalize_scales_to_one():
    q = np.array([1.0, 2.0, 3.0, 4.0])
    out = normalize(q)
    assert is_pmf(out)
    assert abs(out.sum() - 1.0) < 1e-12


def test_normalize_raises_on_zero():
    with pytest.raises(ValueError, match="non-positive mass"):
        normalize(np.zeros(3))


def test_mean_field_to_joint_outer_product_2_streams():
    m = (np.array([0.6, 0.4]), np.array([0.7, 0.3]))
    q = mean_field_to_joint(m)
    expected = np.array([[0.42, 0.18], [0.28, 0.12]])
    assert np.allclose(q, expected, atol=1e-12)
    assert is_pmf(q)


def test_mean_field_to_joint_outer_product_3_streams():
    m = (
        np.array([0.5, 0.5]),
        np.array([0.5, 0.5]),
        np.array([0.5, 0.5]),
    )
    q = mean_field_to_joint(m)
    assert q.shape == (2, 2, 2)
    assert np.allclose(q, np.full((2, 2, 2), 0.125), atol=1e-12)
    assert is_pmf(q)


def test_mean_field_to_joint_empty_raises():
    with pytest.raises(ValueError, match="at least one stream"):
        mean_field_to_joint([])


def test_joint_marginal_recovers_factor():
    m = (np.array([0.6, 0.4]), np.array([0.7, 0.3]))
    q = mean_field_to_joint(m)
    assert np.allclose(joint_marginal(q, 0), np.array([0.6, 0.4]))
    assert np.allclose(joint_marginal(q, 1), np.array([0.7, 0.3]))


def test_joint_marginal_invalid_index():
    q = np.full((2, 2), 0.25)
    with pytest.raises(IndexError, match="out of range"):
        joint_marginal(q, 5)


def test_joint_marginal_1d_returns_copy():
    q = np.array([0.3, 0.7])
    m = joint_marginal(q, 0)
    assert np.allclose(m, q)
    m[0] = 0.9
    assert q[0] == 0.3  # original untouched


def test_is_mean_field_true_for_outer_product():
    m = (np.array([0.6, 0.4]), np.array([0.5, 0.5]))
    q = mean_field_to_joint(m)
    assert is_mean_field(q)


def test_is_mean_field_false_for_correlated_joint():
    # Perfectly correlated: q(0,0) = q(1,1) = 0.5
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    assert not is_mean_field(q)


def test_m_projection_is_outer_product_of_marginals():
    q = np.array([[0.4, 0.1], [0.2, 0.3]])
    p = m_projection(q)
    assert is_pmf(p)
    assert np.allclose(joint_marginal(p, 0), joint_marginal(q, 0))
    assert np.allclose(joint_marginal(p, 1), joint_marginal(q, 1))


def test_joint_marginals_returns_correct_count():
    q = np.full((2, 3, 4), 1.0 / 24.0)
    margs = joint_marginals(q)
    assert len(margs) == 3
    assert margs[0].shape == (2,)
    assert margs[1].shape == (3,)
    assert margs[2].shape == (4,)


def test_mean_field_roundtrip_idempotent():
    """For a true mean-field, m_projection is the identity."""
    m = (np.array([0.7, 0.2, 0.1]), np.array([0.4, 0.6]))
    q = mean_field_to_joint(m)
    proj = m_projection(q)
    assert np.allclose(q, proj, atol=1e-12)
