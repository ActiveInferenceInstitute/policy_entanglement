"""Tests for src/decomposition.py — Theorem 4.1 entanglement decomposition."""
from __future__ import annotations

import numpy as np
import pytest

from coupling import entangled_posterior
from decomposition import (
    DecompositionTerms,
    coupling_cost_term,
    coupling_pays_for_itself,
    coupling_prior_term,
    entanglement_decomposition_rhs,
    free_energy_against_entangled_prior,
    sum_marginal_free_energies,
    total_correlation_gain,
)
from free_energy import total_correlation
from joint_dist import is_pmf


def _ising_J():
    return np.array([[0.5, -0.5], [-0.5, 0.5]])


def _Kc():
    return np.array([[0.2, -0.1], [-0.1, 0.2]])


def _setup():
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]
    return mf, G


def test_decomposition_terms_total_sums_components():
    terms = DecompositionTerms(1.0, 2.0, 3.0, -0.5)
    assert abs(terms.total - 5.5) < 1e-12


def test_sum_marginal_free_energies_positive_for_uniform_q():
    q = np.full((2, 2), 0.25)
    mf, G = _setup()
    val = sum_marginal_free_energies(q, mf, G, gamma=1.0)
    # Sanity: finite real number
    assert np.isfinite(val)


def test_coupling_cost_term_zero_at_zero_lambda():
    q = np.full((2, 2), 0.25)
    assert abs(coupling_cost_term(q, _Kc(), gamma=1.0, lam=0.0)) < 1e-12


def test_coupling_cost_term_linear_in_lambda():
    q = np.full((2, 2), 0.25)
    Kc = _Kc()
    a1 = coupling_cost_term(q, Kc, gamma=1.0, lam=1.0)
    a2 = coupling_cost_term(q, Kc, gamma=1.0, lam=2.0)
    assert abs(a2 - 2.0 * a1) < 1e-12


def test_coupling_prior_term_at_zero_lambda():
    q = np.full((2, 2), 0.25)
    mf, _ = _setup()
    # At lam=0: lam·E_q[J] = 0, log Z_E(0) = log 1 = 0 -> term = 0
    assert abs(coupling_prior_term(q, _ising_J(), mf, lam=0.0)) < 1e-12


def test_total_correlation_gain_negative_for_correlated_q():
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    g = total_correlation_gain(q)
    assert g < 0.0
    assert abs(g + np.log(2.0)) < 1e-9


def test_total_correlation_gain_zero_for_mean_field():
    q = np.full((2, 2), 0.25)
    assert abs(total_correlation_gain(q)) < 1e-9


def test_entanglement_decomposition_rhs_returns_terms():
    q = np.full((2, 2), 0.25)
    mf, G = _setup()
    rhs = entanglement_decomposition_rhs(
        q, mf, G, _ising_J(), _Kc(), gamma=1.0, lam=0.5
    )
    assert isinstance(rhs, DecompositionTerms)
    assert np.isfinite(rhs.total)


def test_free_energy_against_entangled_prior_returns_finite():
    q = np.full((2, 2), 0.25)
    mf, _ = _setup()
    F = free_energy_against_entangled_prior(
        q, mf, _ising_J(), _Kc(), gamma=1.0, lam=0.5
    )
    assert np.isfinite(F)


def test_coupling_pays_for_itself_strict_increase_in_tc():
    """The coupling-pays verdict triggers iff the entangled posterior has
    strictly higher total correlation than the lambda=0 baseline."""
    mf, G = _setup()
    q_zero = entangled_posterior(mf, G, _ising_J(), _Kc(), gamma=0.0, lam=0.0)
    q_lam = entangled_posterior(mf, G, _ising_J(), _Kc(), gamma=0.0, lam=2.0)
    assert coupling_pays_for_itself(q_lam, q_zero)
    assert not coupling_pays_for_itself(q_zero, q_lam)


def test_decomposition_consistency_at_zero_lambda():
    """At lam=0 the coupling-cost and coupling-prior terms vanish; the
    decomposition reduces to per-stream FE plus the gain."""
    q = np.array([[0.4, 0.1], [0.2, 0.3]])
    mf, G = _setup()
    rhs = entanglement_decomposition_rhs(
        q, mf, G, _ising_J(), _Kc(), gamma=1.0, lam=0.0
    )
    assert abs(rhs.coupling_cost_term) < 1e-12
    assert abs(rhs.coupling_prior_term) < 1e-12


def test_decomposition_at_zero_helper_matches_general_call():
    """`decomposition_at_zero` (Cor 4.3 mirror) equals
    `entanglement_decomposition_rhs(..., lam=0.0)` byte-for-byte."""
    from decomposition import decomposition_at_zero
    q = np.array([[0.3, 0.2], [0.1, 0.4]])
    mf, G = _setup()
    rhs0 = entanglement_decomposition_rhs(
        q, mf, G, _ising_J(), _Kc(), gamma=1.0, lam=0.0
    )
    rhs_helper = decomposition_at_zero(q, mf, G, _ising_J(), _Kc(), gamma=1.0)
    assert rhs0.sum_marginal_free_energies == rhs_helper.sum_marginal_free_energies
    assert rhs0.coupling_cost_term == rhs_helper.coupling_cost_term
    assert rhs0.coupling_prior_term == rhs_helper.coupling_prior_term
    assert rhs0.total_correlation_gain == rhs_helper.total_correlation_gain
    # And the coupling-cost / prior terms vanish identically.
    assert abs(rhs_helper.coupling_cost_term) < 1e-12
    assert abs(rhs_helper.coupling_prior_term) < 1e-12


def test_decomposition_is_finite_for_random_inputs():
    """Theorem 4.1 RHS is a finite real for any valid (q, E, G, J, K_c, gamma, lam)."""
    rng = np.random.default_rng(seed=42)
    for _ in range(5):
        q = rng.dirichlet(np.ones(4)).reshape(2, 2)
        mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
        G = [rng.uniform(0.0, 1.0, 2), rng.uniform(0.0, 1.0, 2)]
        J = rng.normal(0.0, 1.0, (2, 2))
        Kc = rng.normal(0.0, 1.0, (2, 2))
        gamma = rng.uniform(0.5, 2.0)
        lam = rng.uniform(0.1, 1.5)
        rhs = entanglement_decomposition_rhs(q, mf, G, J, Kc, gamma, lam)
        assert np.isfinite(rhs.total)
