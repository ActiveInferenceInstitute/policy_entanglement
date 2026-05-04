"""Tests for src/heterogeneous.py — coupling tax for mixed VFE/EFE ensembles."""
from __future__ import annotations

import numpy as np
import pytest

from heterogeneous import (
    InferenceMode,
    coupling_norm_sq,
    coupling_tax,
    coupling_tax_within_quadratic_bound,
    fixed_reflexive_posterior,
    is_heterogeneous,
    is_planning_stream,
    is_purely_planning,
    is_purely_reflexive,
    is_reflexive_stream,
    quadratic_bound_curvature,
)
from joint_dist import is_pmf


def _ising_J():
    return np.array([[0.5, -0.5], [-0.5, 0.5]])


def _Kc_nonzero():
    return np.array([[0.2, -0.1], [-0.1, 0.2]])


def _setup_K2():
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]
    return mf, G


def test_inference_mode_predicates():
    assert is_planning_stream(InferenceMode.EFE)
    assert is_planning_stream(InferenceMode.SOPHISTICATED)
    assert not is_planning_stream(InferenceMode.VFE)
    assert is_reflexive_stream(InferenceMode.VFE)
    assert not is_reflexive_stream(InferenceMode.EFE)


def test_is_purely_reflexive_true():
    assert is_purely_reflexive([InferenceMode.VFE, InferenceMode.VFE])


def test_is_purely_reflexive_false_with_efe():
    assert not is_purely_reflexive([InferenceMode.VFE, InferenceMode.EFE])


def test_is_purely_planning_true():
    assert is_purely_planning([InferenceMode.EFE, InferenceMode.SOPHISTICATED])


def test_is_heterogeneous_requires_both():
    assert is_heterogeneous([InferenceMode.VFE, InferenceMode.EFE])
    assert not is_heterogeneous([InferenceMode.VFE, InferenceMode.VFE])
    assert not is_heterogeneous([InferenceMode.EFE, InferenceMode.EFE])


def test_coupling_norm_sq_nonneg():
    K = _Kc_nonzero()
    assert coupling_norm_sq(K) >= 0.0
    assert coupling_norm_sq(np.zeros((2, 2))) == 0.0


def test_coupling_norm_sq_value():
    K = np.array([[1.0, -1.0], [2.0, 0.0]])
    assert abs(coupling_norm_sq(K) - 6.0) < 1e-12


def test_fixed_reflexive_posterior_empty_modes_raises():
    mf, G = _setup_K2()
    with pytest.raises(ValueError, match="non-empty"):
        fixed_reflexive_posterior(
            mf, G, _ising_J(), _Kc_nonzero(), gamma=1.0, lam=0.5, modes=[]
        )


def test_fixed_reflexive_posterior_returns_pmf():
    mf, G = _setup_K2()
    out = fixed_reflexive_posterior(
        mf, G, _ising_J(), _Kc_nonzero(),
        gamma=1.0, lam=0.5,
        modes=[InferenceMode.VFE, InferenceMode.EFE],
    )
    assert is_pmf(out)
    assert out.shape == (2, 2)


def test_coupling_tax_zero_for_purely_reflexive():
    mf, G = _setup_K2()
    tax = coupling_tax(
        mf, G, _ising_J(), _Kc_nonzero(),
        gamma=1.0, lam=1.0,
        modes=[InferenceMode.VFE, InferenceMode.VFE],
    )
    assert tax == 0.0


def test_coupling_tax_zero_for_purely_planning():
    mf, G = _setup_K2()
    tax = coupling_tax(
        mf, G, _ising_J(), _Kc_nonzero(),
        gamma=1.0, lam=1.0,
        modes=[InferenceMode.EFE, InferenceMode.EFE],
    )
    assert tax == 0.0


def test_coupling_tax_positive_for_heterogeneous_at_nonzero_lambda():
    mf, G = _setup_K2()
    tax = coupling_tax(
        mf, G, _ising_J(), _Kc_nonzero(),
        gamma=1.0, lam=1.0,
        modes=[InferenceMode.VFE, InferenceMode.EFE],
    )
    assert tax > 0.0


def test_coupling_tax_zero_at_lambda_zero():
    mf, G = _setup_K2()
    tax = coupling_tax(
        mf, G, _ising_J(), _Kc_nonzero(),
        gamma=1.0, lam=0.0,
        modes=[InferenceMode.VFE, InferenceMode.EFE],
    )
    assert abs(tax) < 1e-9


def test_quadratic_bound_curvature_zero_when_kc_zero():
    mf, G = _setup_K2()
    C = quadratic_bound_curvature(
        mf, G, _ising_J(), np.zeros((2, 2)),
        gamma=1.0,
        modes=[InferenceMode.VFE, InferenceMode.EFE],
    )
    assert C == 0.0


def test_quadratic_bound_curvature_zero_when_homogeneous():
    mf, G = _setup_K2()
    C = quadratic_bound_curvature(
        mf, G, _ising_J(), _Kc_nonzero(),
        gamma=1.0,
        modes=[InferenceMode.VFE, InferenceMode.VFE],
    )
    assert C == 0.0


def test_quadratic_bound_curvature_nonzero_for_heterogeneous():
    mf, G = _setup_K2()
    C = quadratic_bound_curvature(
        mf, G, _ising_J(), _Kc_nonzero(),
        gamma=1.0,
        modes=[InferenceMode.VFE, InferenceMode.EFE],
    )
    assert C > 0.0


def test_quadratic_bound_curvature_invalid_probe_raises():
    mf, G = _setup_K2()
    with pytest.raises(ValueError, match="non-zero"):
        quadratic_bound_curvature(
            mf, G, _ising_J(), _Kc_nonzero(),
            gamma=1.0,
            modes=[InferenceMode.VFE, InferenceMode.EFE],
            lam_probe=0.0,
        )


def test_coupling_tax_within_quadratic_bound_holds_for_small_lambda():
    mf, G = _setup_K2()
    assert coupling_tax_within_quadratic_bound(
        mf, G, _ising_J(), _Kc_nonzero(),
        gamma=1.0, lam=0.05,
        modes=[InferenceMode.VFE, InferenceMode.EFE],
        safety_factor=2.0,
    )
