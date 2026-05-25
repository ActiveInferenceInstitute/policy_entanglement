"""Tests for pure statistical functions in simulation.statistics.

These functions depend only on numpy; no pymdp installation is required.
FreeEnergyBundle objects are constructed synthetically from numpy arrays.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from simulation.inference import FreeEnergyBundle
from simulation.statistics import (
    BundleSummary,
    QuantileEnvelope,
    _aligned_mass,
    _half_saturation,
    _kl,
    _shannon,
    is_monotone_nondecreasing,
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


# ---------------------------------------------------------------------------
# pymdp_summary_statistics
# ---------------------------------------------------------------------------


def test_summary_statistics_minimal_two_bundles() -> None:
    bundles = [
        _make_bundle(lam=0.0, tc=0.0, vfe=0.5),
        _make_bundle(lam=1.0, tc=0.2, vfe=0.3),
    ]
    s = pymdp_summary_statistics(bundles)
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
        pymdp_summary_statistics([_make_bundle(0.0)])


def test_summary_statistics_aligned_mass_at_lambda_max() -> None:
    dist_uniform = np.array([0.25, 0.25, 0.25, 0.25])
    dist_aligned = np.array([0.5, 0.0, 0.0, 0.5])
    bundles = [
        _make_bundle(lam=0.0, action_dist=dist_uniform),
        _make_bundle(lam=2.0, action_dist=dist_aligned),
    ]
    s = pymdp_summary_statistics(bundles)
    assert s.aligned_mass_at_lambda_max == pytest.approx(1.0, abs=1e-12)
    assert s.aligned_mass_min == pytest.approx(0.5, abs=1e-12)


# ---------------------------------------------------------------------------
# summary_to_var_dict
# ---------------------------------------------------------------------------


def test_summary_to_var_dict_keys_have_prefix() -> None:
    bundles = [_make_bundle(0.0), _make_bundle(1.0)]
    s = pymdp_summary_statistics(bundles)
    d = summary_to_var_dict(s, prefix="test")
    assert all(k.startswith("test_summary_") for k in d)
    assert len(d) == len(s.__dataclass_fields__)


def test_summary_to_var_dict_all_floats() -> None:
    bundles = [_make_bundle(0.0), _make_bundle(1.0)]
    s = pymdp_summary_statistics(bundles)
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
