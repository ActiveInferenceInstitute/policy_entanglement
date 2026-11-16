"""Tests for pure statistical functions in simulation.statistics.

These functions depend only on numpy; no pymdp installation is required.
FreeEnergyBundle objects are constructed synthetically from numpy arrays.
"""

from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pytest

from lean.coupling import entangled_posterior
from lean.free_energy import shannon_entropy, total_correlation
from lean.joint_dist import joint_marginals
from simulation.inference import FreeEnergyBundle
from simulation.statistics import (
    BundleSummary,
    QuantileEnvelope,
    _aligned_mass,
    _half_saturation,
    _kl,
    _shannon,
    is_monotone_nondecreasing,
    kl_to_lambda_zero_curve,
    pymdp_summary_statistics,
    quantile_envelope_over_sweeps,
    summary_to_var_dict,
    total_correlation_saturation_index,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_bundle(
    lam: float,
    tc: float = 0.0,
    vfe: float = 0.0,
    coup: float = 0.0,
    joint_ent: float = 1.0,
    action_dist: np.ndarray | None = None,
) -> FreeEnergyBundle:
    """Construct a minimal FreeEnergyBundle for unit testing."""
    if action_dist is None:
        action_dist = np.array([0.25, 0.25, 0.25, 0.25])  # K=2 uniform
    return FreeEnergyBundle(
        lam=lam,
        vfe_per_stream=np.array([vfe / 2, vfe / 2]),
        vfe_total=vfe,
        efe_per_stream=(np.array([0.0, 0.0]), np.array([0.0, 0.0])),
        efe_under_posterior=np.array([0.0, 0.0]),
        joint_entropy=joint_ent,
        marginal_entropies=np.array([math.log(2), math.log(2)]),
        total_correlation=tc,
        coupling_term=coup,
        action_distribution=action_dist,
    )


def _gibbs_bundle(lam: float, interaction: np.ndarray) -> FreeEnergyBundle:
    """Coherent records computed from real Gibbs PMFs and their marginals."""
    k = interaction.ndim
    zero_costs = [np.zeros(2) for _ in range(k)]
    q = entangled_posterior(
        [np.full(2, 0.5) for _ in range(k)],
        zero_costs,
        interaction,
        np.zeros_like(interaction),
        lam=lam,
        gamma=1.0,
    )
    marginals = joint_marginals(q)
    vfe = np.array([np.sum(m * np.log(m / 0.5)) for m in marginals])
    return FreeEnergyBundle(
        lam=lam,
        vfe_per_stream=vfe,
        vfe_total=float(vfe.sum()),
        efe_per_stream=tuple(zero_costs),
        efe_under_posterior=np.zeros(k),
        joint_entropy=shannon_entropy(q),
        marginal_entropies=np.array([shannon_entropy(m) for m in marginals]),
        total_correlation=total_correlation(q),
        coupling_term=float(lam * np.sum(q * interaction)),
        action_distribution=q.reshape(-1),
    )


# ---------------------------------------------------------------------------
# _kl
# ---------------------------------------------------------------------------


def test_kl_zero_for_identical_distributions() -> None:
    p = np.array([0.5, 0.3, 0.2])
    assert _kl(p, p) == pytest.approx(0.0, abs=1e-12)


def test_kl_positive_for_different_distributions() -> None:
    p = np.array([0.5, 0.5])
    q = np.array([0.25, 0.75])
    assert _kl(p, q) > 0.0


def test_kl_handles_zero_mass_in_p() -> None:
    p = np.array([1.0, 0.0])
    q = np.array([0.5, 0.5])
    # p has zero mass on second element — KL is finite (0 * log(...) = 0)
    val = _kl(p, q)
    assert val == pytest.approx(math.log(2.0), abs=1e-10)


# ---------------------------------------------------------------------------
# _shannon
# ---------------------------------------------------------------------------


def test_shannon_uniform_binary() -> None:
    p = np.array([0.5, 0.5])
    assert _shannon(p) == pytest.approx(math.log(2), abs=1e-12)


def test_shannon_delta_is_zero() -> None:
    p = np.array([1.0, 0.0, 0.0])
    assert _shannon(p) == pytest.approx(0.0, abs=1e-12)


def test_shannon_handles_multidim() -> None:
    p = np.array([[0.25, 0.25], [0.25, 0.25]])
    assert _shannon(p) == pytest.approx(math.log(4), abs=1e-12)


# ---------------------------------------------------------------------------
# _aligned_mass
# ---------------------------------------------------------------------------


def test_aligned_mass_uniform_k2() -> None:
    dist = np.array([0.25, 0.25, 0.25, 0.25])  # K=2, uniform
    assert _aligned_mass(dist) == pytest.approx(0.5, abs=1e-12)


def test_aligned_mass_fully_aligned() -> None:
    dist = np.array([0.5, 0.0, 0.0, 0.5])  # all mass on aligned corners
    assert _aligned_mass(dist) == pytest.approx(1.0, abs=1e-12)


def test_aligned_mass_non_power_of_two_returns_nan() -> None:
    dist = np.array([0.33, 0.33, 0.34])
    assert math.isnan(_aligned_mass(dist))


def test_aligned_mass_k3_eight_elements() -> None:
    dist = np.ones(8) / 8.0
    # K=3 uniform: aligned = index 0 + index 7
    assert _aligned_mass(dist) == pytest.approx(2 / 8, abs=1e-12)


# ---------------------------------------------------------------------------
# _half_saturation
# ---------------------------------------------------------------------------


def test_half_saturation_finds_midpoint() -> None:
    lams = [0.0, 1.0, 2.0, 3.0, 4.0]
    tcs = [0.0, 0.1, 0.5, 0.9, 1.0]
    lam_h, tc_h = _half_saturation(lams, tcs)
    assert tc_h == pytest.approx(0.5, abs=1e-9)
    # lam_h should be near 2 (first point >= 0.5 is index 2)
    assert lam_h == pytest.approx(2.0, abs=1e-6)


def test_half_saturation_zero_tc_returns_zeros() -> None:
    lam_h, tc_h = _half_saturation([0.0, 1.0, 2.0], [0.0, 0.0, 0.0])
    assert lam_h == 0.0
    assert tc_h == 0.0


def test_half_saturation_all_above_target_returns_first() -> None:
    lam_h, tc_h = _half_saturation([1.0, 2.0, 3.0], [0.8, 0.9, 1.0])
    # All >= 0.5 * 1.0 = 0.5; first index 0
    assert lam_h == pytest.approx(1.0, abs=1e-9)


def test_half_saturation_interpolated_length_mismatch_raises() -> None:
    """The interpolated half-saturation helper indexes lams[j]/tcs[j] directly,
    so a length mismatch must fail loudly rather than mis-pair values
    (RedTeam C7, 2026-08-01)."""
    with pytest.raises(ValueError, match="equal length"):
        _half_saturation([0.0, 1.0, 2.0], [0.0, 0.5])


def test_half_saturation_interpolated_single_point_raises() -> None:
    """Interpolation needs at least two sweep points."""
    with pytest.raises(ValueError, match="at least 2"):
        _half_saturation([0.0], [0.0])


# ---------------------------------------------------------------------------
# pymdp_summary_statistics
# ---------------------------------------------------------------------------


def test_summary_statistics_minimal_two_bundles() -> None:
    bundles = [
        _make_bundle(lam=0.0, tc=0.0, vfe=0.5),
        _make_bundle(lam=1.0, tc=0.2, vfe=0.3),
    ]
    s = pymdp_summary_statistics(bundles, zero_reference=bundles[0])
    assert isinstance(s, BundleSummary)
    assert s.n_lambda_points == 2
    assert s.lambda_min == pytest.approx(0.0)
    assert s.lambda_max == pytest.approx(1.0)
    assert s.tc_min == pytest.approx(0.0)
    assert s.tc_max == pytest.approx(0.2)
    assert s.vfe_total_min == pytest.approx(0.3)
    assert s.vfe_total_max == pytest.approx(0.5)


def test_summary_statistics_requires_two_bundles() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        pymdp_summary_statistics([_make_bundle(0.0)], zero_reference=_make_bundle(0.0))


@pytest.mark.parametrize("grid", [[2.0, 0.0], [2.0, 0.0, 1.0], [1.0, 3.0, 0.0, 2.0], [3.0, 1.0]])
def test_summary_statistics_preserves_requested_order_and_uses_lambda_extrema(grid: list[float]) -> None:
    interaction = np.array([[2.0, 0.0], [0.0, 1.0]])
    reference = _gibbs_bundle(0.0, interaction)
    bundles = [_gibbs_bundle(lam, interaction) for lam in grid]
    summary = pymdp_summary_statistics(bundles, zero_reference=reference)
    endpoint = bundles[grid.index(max(grid))]
    assert summary.lambda_min == min(grid)
    assert summary.lambda_max == max(grid)
    assert summary.aligned_mass_at_lambda_max == pytest.approx(
        endpoint.action_distribution[0] + endpoint.action_distribution[-1]
    )
    assert summary.action_mode_prob_at_lambda_max == pytest.approx(endpoint.action_distribution.max())
    assert [bundle.lam for bundle in bundles] == grid
    q0 = reference.action_distribution
    expected_kl = [float(np.sum(b.action_distribution * np.log(b.action_distribution / q0))) for b in bundles]
    np.testing.assert_allclose(kl_to_lambda_zero_curve(bundles, zero_reference=reference), expected_kl, atol=1e-12)
    assert summary.kl_to_lambda_zero_min == pytest.approx(min(expected_kl), abs=1e-12)
    if grid == [1.0, 3.0, 0.0, 2.0]:
        assert max(bundles, key=lambda bundle: bundle.total_correlation).lam != max(grid)


def test_summary_statistics_aligned_mass_at_lambda_max() -> None:
    dist_uniform = np.array([0.25, 0.25, 0.25, 0.25])
    dist_aligned = np.array([0.5, 0.0, 0.0, 0.5])
    bundles = [
        _make_bundle(lam=0.0, action_dist=dist_uniform),
        _make_bundle(lam=2.0, action_dist=dist_aligned),
    ]
    s = pymdp_summary_statistics(bundles, zero_reference=bundles[0])
    assert s.aligned_mass_at_lambda_max == pytest.approx(1.0, abs=1e-12)
    assert s.aligned_mass_min == pytest.approx(0.5, abs=1e-12)


# ---------------------------------------------------------------------------
# summary_to_var_dict
# ---------------------------------------------------------------------------


def test_summary_to_var_dict_keys_have_prefix() -> None:
    bundles = [_make_bundle(0.0), _make_bundle(1.0)]
    s = pymdp_summary_statistics(bundles, zero_reference=bundles[0])
    d = summary_to_var_dict(s, prefix="test")
    assert all(k.startswith("test_summary_") for k in d)
    assert len(d) == len(s.__dataclass_fields__)


def test_summary_to_var_dict_all_floats() -> None:
    bundles = [_make_bundle(0.0), _make_bundle(1.0)]
    s = pymdp_summary_statistics(bundles, zero_reference=bundles[0])
    d = summary_to_var_dict(s)
    for k, v in d.items():
        assert isinstance(v, float), f"{k} is {type(v)}"


# ---------------------------------------------------------------------------
# quantile_envelope_over_sweeps
# ---------------------------------------------------------------------------


def _make_sweep(lams: list[float], tc_values: list[float]) -> list[FreeEnergyBundle]:
    return [_make_bundle(lam=l, tc=tc) for l, tc in zip(lams, tc_values, strict=True)]


def test_quantile_envelope_basic() -> None:
    lams = [0.0, 1.0, 2.0]
    sweeps = [
        _make_sweep(lams, [0.0, 0.5, 1.0]),
        _make_sweep(lams, [0.0, 0.4, 0.8]),
        _make_sweep(lams, [0.0, 0.6, 1.2]),
    ]
    env = quantile_envelope_over_sweeps(sweeps)
    assert isinstance(env, QuantileEnvelope)
    assert env.n_runs == 3
    assert len(env.lams) == 3
    # Median at lam=1: median of [0.5, 0.4, 0.6] = 0.5
    assert env.median[1] == pytest.approx(0.5, abs=1e-10)


def test_quantile_envelope_empty_sweeps_raises() -> None:
    with pytest.raises(ValueError, match="at least one sweep"):
        quantile_envelope_over_sweeps([])


def test_quantile_envelope_single_grid_point_raises() -> None:
    with pytest.raises(ValueError, match="at least 2 grid points"):
        quantile_envelope_over_sweeps([[_make_bundle(0.0)]])


def test_quantile_envelope_mismatched_grid_raises() -> None:
    lams = [0.0, 1.0, 2.0]
    sweeps = [
        _make_sweep(lams, [0.0, 0.5, 1.0]),
        _make_sweep([0.0, 1.0], [0.0, 0.5]),  # wrong length
    ]
    with pytest.raises(ValueError, match="grid points"):
        quantile_envelope_over_sweeps(sweeps)


def test_quantile_envelope_lambda_mismatch_raises() -> None:
    sweeps = [
        _make_sweep([0.0, 1.0, 2.0], [0.0, 0.5, 1.0]),
        _make_sweep([0.0, 1.0, 3.0], [0.0, 0.5, 1.0]),  # λ=3 not 2
    ]
    with pytest.raises(ValueError, match="λ-grid disagrees"):
        quantile_envelope_over_sweeps(sweeps)


def test_quantile_envelope_invalid_quantile_bounds_raises() -> None:
    sweeps = [_make_sweep([0.0, 1.0], [0.0, 1.0])]
    with pytest.raises(ValueError, match="quantile_lower"):
        quantile_envelope_over_sweeps(sweeps, quantile_lower=0.8, quantile_upper=0.3)


def test_quantile_envelope_vfe_field() -> None:
    lams = [0.0, 1.0, 2.0]
    sweeps = [
        _make_sweep(lams, [0.0, 0.5, 1.0]),
        _make_sweep(lams, [0.0, 0.4, 0.8]),
    ]
    env = quantile_envelope_over_sweeps(sweeps, field="vfe_total")
    # vfe_total is 0 for all bundles (default), so median should be 0
    assert np.allclose(env.median, 0.0, atol=1e-12)


# ---------------------------------------------------------------------------
# is_monotone_nondecreasing
# ---------------------------------------------------------------------------


def test_monotone_nondecreasing_strictly_increasing() -> None:
    assert is_monotone_nondecreasing([1.0, 2.0, 3.0, 4.0])


def test_monotone_nondecreasing_flat() -> None:
    assert is_monotone_nondecreasing([5.0, 5.0, 5.0])


def test_monotone_nondecreasing_decreasing_returns_false() -> None:
    assert not is_monotone_nondecreasing([3.0, 2.0, 1.0])


def test_monotone_nondecreasing_single_element() -> None:
    assert is_monotone_nondecreasing([42.0])


def test_monotone_nondecreasing_with_tolerance() -> None:
    # Small decrease within atol → still passes
    vals = [0.0, 1.0, 1.0 - 1e-10, 2.0]
    assert is_monotone_nondecreasing(vals, atol=1e-9)
    # Large decrease → fails
    assert not is_monotone_nondecreasing([0.0, 1.0, 0.0])


# ---------------------------------------------------------------------------
# total_correlation_saturation_index
# ---------------------------------------------------------------------------


def test_saturation_index_returns_correct_lambda() -> None:
    lams = [0.0, 1.0, 2.0, 3.0, 4.0]
    tcs = [0.0, 0.2, 0.8, 0.95, 1.0]
    bundles = [_make_bundle(l, tc=tc) for l, tc in zip(lams, tcs, strict=True)]
    # 90% of max(1.0) = 0.9; first point >= 0.9 is index 3 (tc=0.95)
    idx = total_correlation_saturation_index(bundles, saturation_fraction=0.9)
    assert idx == pytest.approx(3.0, abs=1e-12)


def test_saturation_index_zero_tc_returns_inf() -> None:
    bundles = [_make_bundle(float(l), tc=0.0) for l in range(5)]
    result = total_correlation_saturation_index(bundles)
    assert result == float("inf")


def test_saturation_index_requires_two_bundles() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        total_correlation_saturation_index([_make_bundle(0.0)])


def test_saturation_index_invalid_fraction_raises() -> None:
    bundles = [_make_bundle(float(l)) for l in range(3)]
    with pytest.raises(ValueError, match="saturation_fraction"):
        total_correlation_saturation_index(bundles, saturation_fraction=0.0)
    with pytest.raises(ValueError, match="saturation_fraction"):
        total_correlation_saturation_index(bundles, saturation_fraction=1.5)


@pytest.mark.parametrize("k", [2, 3, 4, 6])
def test_positive_only_kl_uses_actual_zero_reference(k: int) -> None:
    interaction = np.zeros((2,) * k)
    interaction[(0,) * k] = interaction[(1,) * k] = 1.0
    reference = _gibbs_bundle(0.0, interaction)
    grid = [math.log(9.0), math.log(3.0)]
    bundles = [_gibbs_bundle(lam, interaction) for lam in grid]
    expected = []
    for lam in grid:
        partition = 2.0 * math.exp(lam) + 2**k - 2
        aligned = 2.0 * math.exp(lam) / partition
        expected.append(lam * aligned - math.log(partition / 2**k))
    curve = kl_to_lambda_zero_curve(bundles, zero_reference=reference)
    np.testing.assert_allclose(curve, expected, atol=1e-12)
    assert np.all(curve > 0.0)
    summary = pymdp_summary_statistics(bundles, zero_reference=reference)
    assert summary.n_lambda_points == 2
    assert summary.lambda_min == min(grid)
    assert summary.kl_to_lambda_zero_min == pytest.approx(min(expected))
    assert [bundle.lam for bundle in bundles] == grid


def test_zero_reference_requires_exact_zero_and_matching_policy_dimensions() -> None:
    reference = _gibbs_bundle(0.0, np.zeros((2, 2)))
    with pytest.raises(ValueError, match="lam == 0"):
        kl_to_lambda_zero_curve([reference], zero_reference=replace(reference, lam=1e-12))
    wrong_k = _gibbs_bundle(1.0, np.zeros((2, 2, 2)))
    with pytest.raises(ValueError, match="policy dimensions"):
        kl_to_lambda_zero_curve([wrong_k], zero_reference=reference)


def test_saturation_selects_smallest_qualifying_lambda_not_first_row() -> None:
    interaction = np.eye(2)
    bundles = [_gibbs_bundle(lam, interaction) for lam in [4.0, 0.0, 3.0]]
    assert bundles[2].total_correlation >= 0.8 * bundles[0].total_correlation
    assert total_correlation_saturation_index(bundles, saturation_fraction=0.8) == 3.0
