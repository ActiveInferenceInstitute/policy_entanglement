"""Tests for the pymdp-grounded free-energy methods.

Every test runs *real* pymdp 1.0.1 inference (no mocks) and asserts
numerical contracts on the resulting :class:`FreeEnergyBundle`:

* shapes are correct,
* λ = 0 reproduces the mean-field baseline (TC = 0, joint = product of
  marginals, coupling term = 0, joint entropy = sum of marginals),
* total correlation is non-negative everywhere,
* total correlation grows monotonically with |λ| under symmetric
  Ising coupling and zero EFE drift,
* Theorem 5.1 pymdp baseline: at λ = 0, ``vfe_total = Σ F[q^k_0]`` with
  vanishing coupling term and total correlation (manuscript §15 bundle).

Skips entirely when the ``sim`` group is missing.
"""

from __future__ import annotations

import numpy as np
import pytest

from simulation.agents import pymdp_available

if not pymdp_available():
    pytestmark = pytest.mark.skip(
        reason="pymdp 1.0.1 not installed (uv sync --group sim)",
    )
else:
    pytestmark = pytest.mark.requires_pymdp


from simulation.builders import make_ising_ensemble
from simulation.inference import (
    DecompositionWitness,
    FreeEnergyBundle,
    coupling_energy,
    decomposition_witness_curve,
    expected_free_energy_under_posterior,
    free_energy_bundle,
    free_energy_curve,
    variational_free_energy,
)


def _spec(K: int = 2):
    return make_ising_ensemble(num_streams=K, gamma=1.0, coupling_amplitude=1.0)


def test_variational_free_energy_returns_per_stream_array() -> None:
    spec = _spec(K=2)
    F = variational_free_energy(spec, [0, 0], lam=0.5)
    assert F.shape == (2,)
    assert np.isfinite(F).all()


def test_variational_free_energy_finite_across_lambda() -> None:
    spec = _spec(K=2)
    for lam in (0.0, 0.5, 1.0, 2.0, 4.0):
        F = variational_free_energy(spec, [0, 0], lam)
        assert np.isfinite(F).all(), f"non-finite VFE at λ={lam}: {F}"


def test_expected_efe_under_posterior_per_stream_shape() -> None:
    spec = _spec(K=2)
    G = expected_free_energy_under_posterior(spec, [0, 0], lam=1.0)
    assert G.shape == (2,)
    assert np.isfinite(G).all()


def test_coupling_energy_zero_at_lambda_zero() -> None:
    spec = _spec(K=2)
    assert abs(coupling_energy(spec, [0, 0], 0.0)) < 1e-12


def test_free_energy_bundle_returns_dataclass() -> None:
    spec = _spec(K=2)
    b = free_energy_bundle(spec, [0, 0], lam=1.5)
    assert isinstance(b, FreeEnergyBundle)
    assert b.lam == 1.5
    assert b.vfe_per_stream.shape == (2,)
    assert len(b.efe_per_stream) == 2
    assert b.efe_under_posterior.shape == (2,)
    assert b.marginal_entropies.shape == (2,)
    assert b.action_distribution.shape == (4,)


def test_free_energy_bundle_lambda_zero_baseline() -> None:
    """At λ = 0 the joint is the outer product of mean-field marginals,
    so total correlation, coupling term, and joint–marginal entropy gap
    are all zero (within float tolerance).
    """
    spec = _spec(K=2)
    b = free_energy_bundle(spec, [0, 0], lam=0.0)
    assert b.total_correlation < 1e-10
    assert abs(b.coupling_term) < 1e-12
    assert abs(b.joint_entropy - b.marginal_entropies.sum()) < 1e-10


def test_total_correlation_non_negative_across_grid() -> None:
    spec = _spec(K=2)
    for lam in np.linspace(0.0, 4.0, 9):
        b = free_energy_bundle(spec, [0, 0], float(lam))
        assert b.total_correlation >= -1e-9


def test_total_correlation_monotone_under_symmetric_coupling() -> None:
    """Under the symmetric Ising coupling at observations (0, 0), total
    correlation is monotone-increasing in λ (the empirical witness of
    Prop 7.3 inside a real POMDP).
    """
    spec = _spec(K=2)
    bundles = free_energy_curve(spec, [0, 0], np.linspace(0.0, 4.0, 9))
    tcs = [b.total_correlation for b in bundles]
    for i in range(len(tcs) - 1):
        assert tcs[i + 1] >= tcs[i] - 1e-9, f"non-monotone: {tcs}"


def test_action_distribution_is_a_pmf_at_every_lambda() -> None:
    spec = _spec(K=2)
    for lam in (0.0, 0.5, 1.0, 2.0, 4.0):
        b = free_energy_bundle(spec, [0, 0], lam)
        assert (b.action_distribution >= -1e-12).all()
        assert abs(b.action_distribution.sum() - 1.0) < 1e-7


def test_free_energy_decomposition_witness_at_lambda_zero() -> None:
    """At λ = 0: vfe_total ≈ Σ_k F[q^k_0]; coupling term and TC are zero.

    This is the Theorem 5.1 baseline — when the joint is mean-field,
    the per-stream sum is the whole free energy.
    """
    spec = _spec(K=2)
    b = free_energy_bundle(spec, [0, 0], lam=0.0)
    assert abs(b.vfe_total - float(b.vfe_per_stream.sum())) < 1e-10
    assert abs(b.coupling_term) < 1e-12
    assert b.total_correlation < 1e-10


def test_pymdp_decomposition_witness_holds_across_positive_lambda_grid() -> None:
    """The pymdp-backed posterior satisfies the full decomposition at λ > 0.

    pymdp already absorbs per-stream EFE into its policy posterior, so
    the witness curve uses zero-G analytical bookkeeping to avoid
    double-counting while still checking LHS = RHS over the sweep.
    """
    spec = _spec(K=2)
    witnesses = decomposition_witness_curve(spec, [0, 0], np.linspace(0.0, 4.0, 9))
    assert all(isinstance(w, DecompositionWitness) for w in witnesses)
    assert any(w.lam > 0.0 for w in witnesses)
    assert max(w.residual for w in witnesses) < 1e-9
    assert all(np.isfinite([w.lhs, w.rhs, w.residual]).all() for w in witnesses)


def test_free_energy_curve_length_matches_lambda_grid() -> None:
    spec = _spec(K=2)
    lams = np.linspace(0.0, 3.0, 7)
    bundles = free_energy_curve(spec, [0, 0], lams)
    assert len(bundles) == 7
    for b, l in zip(bundles, lams, strict=False):
        assert b.lam == float(l)


@pytest.mark.parametrize("K", [2, 3])
def test_free_energy_bundle_scales_with_K(K: int) -> None:
    spec = make_ising_ensemble(num_streams=K, gamma=1.0, coupling_amplitude=1.0)
    b = free_energy_bundle(spec, [0] * K, lam=1.0)
    assert b.vfe_per_stream.shape == (K,)
    assert b.marginal_entropies.shape == (K,)
    assert b.action_distribution.shape == (2**K,)
    assert len(b.efe_per_stream) == K


def test_coupling_term_positive_for_aligned_observations() -> None:
    """With observations $(0,0)$ favoring the aligned policy and
    positive λ, the coupling term ⟨J⟩ should be positive (the
    posterior places more mass on $J > 0$ corners).
    """
    spec = _spec(K=2)
    b = free_energy_bundle(spec, [0, 0], lam=2.0)
    assert b.coupling_term > 0.0


def test_joint_entropy_le_sum_marginal_entropies() -> None:
    """Sub-additivity: $H(q_λ) ≤ Σ_k H(q^k_λ)$ at every λ."""
    spec = _spec(K=2)
    for lam in (0.0, 1.0, 2.0, 4.0):
        b = free_energy_bundle(spec, [0, 0], lam)
        assert b.joint_entropy <= b.marginal_entropies.sum() + 1e-9


def test_efe_under_posterior_matches_explicit_helper() -> None:
    """``free_energy_bundle.efe_under_posterior`` agrees with the
    standalone ``expected_free_energy_under_posterior`` helper."""
    spec = _spec(K=2)
    for lam in (0.0, 1.0, 2.0):
        b = free_energy_bundle(spec, [0, 0], lam)
        explicit = expected_free_energy_under_posterior(spec, [0, 0], lam)
        assert np.allclose(b.efe_under_posterior, explicit, atol=1e-9)


def test_coupling_energy_matches_bundle_term() -> None:
    spec = _spec(K=2)
    for lam in (0.5, 1.5, 3.0):
        b = free_energy_bundle(spec, [0, 0], lam)
        assert np.isclose(b.coupling_term, coupling_energy(spec, [0, 0], lam))


# ---------------------------------------------------------------------------
# Aggregation statistics: quantile envelope, monotonicity witness,
# saturation index.
# ---------------------------------------------------------------------------

from simulation.statistics import (  # noqa: E402  (after pymdp guard above)
    QuantileEnvelope,
    is_monotone_nondecreasing,
    quantile_envelope_over_sweeps,
    total_correlation_saturation_index,
)


@pytest.fixture
def small_sweep():
    """A small λ sweep used for aggregation tests."""
    spec = _spec(K=2)
    lams = np.linspace(0.0, 3.0, 7)
    return free_energy_curve(spec, [0, 0], lams)


def test_quantile_envelope_aligns_with_sweep_grid(small_sweep) -> None:
    env = quantile_envelope_over_sweeps([small_sweep, small_sweep])
    assert isinstance(env, QuantileEnvelope)
    assert env.lams.shape == (7,)
    # Identical sweeps → median = lower = upper = minimum = maximum.
    assert np.allclose(env.median, env.lower)
    assert np.allclose(env.median, env.upper)
    assert np.allclose(env.minimum, env.maximum)
    assert env.n_runs == 2


def test_quantile_envelope_separates_low_and_high_runs(small_sweep) -> None:
    """Build a synthetic perturbed sweep by scaling TC and verify the
    envelope brackets it. Uses the bundle dataclass replace pattern.
    """
    from dataclasses import replace

    perturbed = [replace(b, total_correlation=b.total_correlation * 1.5) for b in small_sweep]
    env = quantile_envelope_over_sweeps([small_sweep, perturbed], field="total_correlation")
    # Median sits between the two runs.
    assert np.all(env.minimum <= env.median + 1e-12)
    assert np.all(env.median <= env.maximum + 1e-12)
    # Range spans both runs at every grid point with positive TC.
    positive = env.maximum > 1e-9
    if positive.any():
        assert np.any(env.maximum[positive] > env.minimum[positive])


def test_quantile_envelope_rejects_misaligned_grids(small_sweep) -> None:
    spec = _spec(K=2)
    other = free_energy_curve(spec, [0, 0], np.linspace(0.0, 3.0, 11))  # different grid
    with pytest.raises(ValueError, match="grid"):
        quantile_envelope_over_sweeps([small_sweep, other])


def test_quantile_envelope_rejects_invalid_quantiles(small_sweep) -> None:
    with pytest.raises(ValueError, match="quantile"):
        quantile_envelope_over_sweeps([small_sweep], quantile_lower=0.6, quantile_upper=0.4)


def test_quantile_envelope_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least one sweep"):
        quantile_envelope_over_sweeps([])


def test_is_monotone_nondecreasing_witnesses_total_correlation(small_sweep) -> None:
    """For the symmetric K=2 Ising toy with zero EFE drift, TC is
    monotone-nondecreasing across a non-negative λ sweep — a direct
    numerical witness for the manuscript's monotone-in-|λ| claim.
    """
    tcs = [b.total_correlation for b in small_sweep]
    assert is_monotone_nondecreasing(tcs)


def test_is_monotone_nondecreasing_rejects_decreasing_sequence() -> None:
    assert not is_monotone_nondecreasing([0.0, 1.0, 0.5, 2.0])


def test_is_monotone_nondecreasing_handles_short_input() -> None:
    assert is_monotone_nondecreasing([])
    assert is_monotone_nondecreasing([3.14])


def test_total_correlation_saturation_index_positive(small_sweep) -> None:
    idx = total_correlation_saturation_index(small_sweep, saturation_fraction=0.5)
    assert np.isfinite(idx)
    assert 0.0 <= idx <= small_sweep[-1].lam


def test_total_correlation_saturation_index_full_saturation(small_sweep) -> None:
    """At ``saturation_fraction = 1`` the index is the λ where TC is
    maximized; for a monotone-non-decreasing TC sweep that's the
    final grid point.
    """
    idx = total_correlation_saturation_index(small_sweep, saturation_fraction=1.0)
    assert np.isclose(idx, small_sweep[-1].lam)


def test_total_correlation_saturation_index_rejects_invalid() -> None:
    with pytest.raises(ValueError, match="saturation_fraction"):
        total_correlation_saturation_index([], saturation_fraction=0.0)
    with pytest.raises(ValueError, match="saturation_fraction"):
        total_correlation_saturation_index([], saturation_fraction=1.5)


def test_total_correlation_saturation_index_returns_inf_for_flat_zero(small_sweep) -> None:
    """When every TC is zero (degenerate sweep), saturation is
    undefined; the helper returns +∞ to signal this."""
    from dataclasses import replace

    flat = [replace(b, total_correlation=0.0) for b in small_sweep]
    assert total_correlation_saturation_index(flat) == float("inf")


def test_total_correlation_saturation_index_rejects_single_bundle(small_sweep) -> None:
    """A single-element list is too short; needs at least 2 grid points."""
    with pytest.raises(ValueError, match="at least 2"):
        total_correlation_saturation_index([small_sweep[0]], saturation_fraction=0.5)


def test_quantile_envelope_rejects_single_point_sweep(small_sweep) -> None:
    """A sweep containing only one bundle has no interpolation support."""
    one_point = [small_sweep[0]]
    with pytest.raises(ValueError, match="at least 2 grid points"):
        quantile_envelope_over_sweeps([one_point, one_point])


def test_quantile_envelope_rejects_same_length_different_lambdas(small_sweep) -> None:
    """Same grid length but different λ values triggers the allclose guard."""
    from dataclasses import replace

    # Shift all λ values by 0.1 to produce a same-length but misaligned grid.
    shifted = [replace(b, lam=b.lam + 0.1) for b in small_sweep]
    with pytest.raises(ValueError, match="grid"):
        quantile_envelope_over_sweeps([small_sweep, shifted])


def test_aligned_mass_generic_k3_path(small_sweep) -> None:
    """_aligned_mass is exercised indirectly via pymdp_summary_statistics
    when action_distribution has size 8 (K=3, 2^3 = 8)."""
    from dataclasses import replace

    from simulation.statistics import pymdp_summary_statistics

    # Construct a synthetic K=3 bundle by swapping in an 8-element action dist.
    k3_dist = np.array([0.125] * 8, dtype=np.float64)  # uniform K=3 joint
    b = small_sweep[0]
    k3_bundle = replace(
        b,
        vfe_per_stream=np.array([0.0, 0.0, 0.0]),
        marginal_entropies=np.array([np.log(2), np.log(2), np.log(2)]),
        action_distribution=k3_dist,
    )
    # Should not raise; aligned mass = k3_dist[0] + k3_dist[7] = 0.25.
    summary = pymdp_summary_statistics([k3_bundle] * 3)
    assert np.isfinite(summary.aligned_mass_max)
