"""Tests for the K>2 multi-K ensemble experiments (T1).

All numerical computations route through real pymdp.agent.Agent
instances and the analytical coupling layer — no mocks, in keeping
with the project's no-mocks policy.
"""

from __future__ import annotations

import numpy as np
import pytest

from simulation.agents import pymdp_available

if not pymdp_available():
    pytestmark = pytest.mark.skip(reason="pymdp 1.0.1 not installed (uv sync --group sim)")
else:
    pytestmark = pytest.mark.requires_pymdp


from lean.joint_dist import is_pmf  # noqa: E402
from simulation import hyperparameters as H  # noqa: E402
from simulation.multi_k_experiments import (  # noqa: E402
    MultiKResult,
    multi_k_joint_snapshot,
    multi_k_summary,
    run_multi_k_sweep,
)


@pytest.mark.parametrize("K", list(H.MULTI_K_VALUES))
def test_run_multi_k_sweep_returns_one_result_per_lambda(K: int) -> None:
    lams = list(H.MULTI_K_SWEEP_LAMBDAS.values())
    results = run_multi_k_sweep(
        K,
        lams,
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    assert len(results) == len(lams)
    for r, lam in zip(results, lams, strict=True):
        assert isinstance(r, MultiKResult)
        assert r.K == K
        assert pytest.approx(r.lam) == float(lam)
        assert len(r.marginal_entropies) == K
        assert len(r.tt_ranks) == K - 1
        assert r.total_correlation >= -1e-9
        assert np.isfinite(r.total_correlation)
        assert np.isfinite(r.joint_entropy)


def test_run_multi_k_sweep_rejects_k_below_two() -> None:
    with pytest.raises(ValueError, match="K>=2"):
        run_multi_k_sweep(
            1,
            [0.0, 1.0],
            coupling_lambda_gen=1.0,
            gamma=1.0,
        )


def test_run_multi_k_sweep_obs_length_validates() -> None:
    with pytest.raises(ValueError, match="observations length"):
        run_multi_k_sweep(
            3,
            [0.0],
            coupling_lambda_gen=1.0,
            gamma=1.0,
            observations=[0, 0],  # wrong length
        )


@pytest.mark.parametrize("K", list(H.MULTI_K_VALUES))
def test_multi_k_joint_snapshot_shape_and_pmf(K: int) -> None:
    q = multi_k_joint_snapshot(
        K,
        lam=float(H.MULTI_K_SENTINEL_LAMBDA),
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    assert q.shape == tuple(2 for _ in range(K))
    assert is_pmf(q, atol=1e-6)


def test_multi_k_joint_snapshot_rejects_k_below_two() -> None:
    with pytest.raises(ValueError):
        multi_k_joint_snapshot(
            1,
            lam=1.0,
            coupling_lambda_gen=1.0,
            gamma=1.0,
        )


@pytest.mark.parametrize("K", list(H.MULTI_K_VALUES))
def test_multi_k_total_correlation_monotone_in_lambda(K: int) -> None:
    """I(q_λ) should be non-decreasing in λ on the Ising K-stream
    ensemble under the configured aligned coupling."""
    lams = list(H.MULTI_K_SWEEP_LAMBDAS.values())
    results = run_multi_k_sweep(
        K,
        lams,
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    tcs = [r.total_correlation for r in results]
    for i in range(len(tcs) - 1):
        assert tcs[i + 1] >= tcs[i] - 1e-9, f"K={K}: non-monotone at i={i}: {tcs}"


@pytest.mark.parametrize("K", list(H.MULTI_K_VALUES))
def test_multi_k_lambda_zero_total_correlation_is_zero(K: int) -> None:
    results = run_multi_k_sweep(
        K,
        [0.0],
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    assert abs(results[0].total_correlation) <= 1e-7
    assert abs(results[0].coupling_term) <= 1e-9


def test_multi_k_summary_keys_present() -> None:
    K = 3
    results = run_multi_k_sweep(
        K,
        list(H.MULTI_K_SWEEP_LAMBDAS.values()),
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    summary = multi_k_summary(results)
    expected_keys = {
        "K",
        "lambda_min",
        "lambda_max",
        "tc_min",
        "tc_max",
        "tc_at_lambda_max",
        "coupling_term_min",
        "coupling_term_max",
        "aligned_mass_at_lambda_zero",
        "aligned_mass_at_lambda_max",
        "tt_rank_max_at_lambda_max",
        "tt_rank_sum_at_lambda_max",
    }
    assert expected_keys.issubset(summary.keys())
    assert summary["K"] == float(K)
    assert summary["tc_max"] >= summary["tc_min"]


def test_multi_k_summary_rejects_empty() -> None:
    with pytest.raises(ValueError):
        multi_k_summary([])


@pytest.mark.parametrize("K", list(H.MULTI_K_VALUES))
def test_multi_k_tt_ranks_at_lambda_zero_are_all_one(K: int) -> None:
    """At λ=0 the joint is the outer product of marginals, so every TT
    bond dimension must equal 1.
    """
    results = run_multi_k_sweep(
        K,
        [0.0],
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    assert results[0].tt_ranks == tuple(1 for _ in range(K - 1))
