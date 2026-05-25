"""Tests for the round-3 multi-K, long-horizon, and revertibility plots.

The plot helpers in :mod:`visualizations.multi_k_plots` only consume
record attributes (no numerical work happens in viz), so these tests
build synthetic dataclass records by hand to keep the tests cheap and
independent of pymdp.  Each test asserts the PNG is written, is non-
empty, and starts with the PNG header — matching the conventions in
``tests/test_visualizations.py``.
"""

from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from visualizations.multi_k_plots import (
    plot_long_horizon_marginals,
    plot_long_horizon_steady_state,
    plot_multi_k_aligned_mass,
    plot_multi_k_total_correlation,
    plot_multi_k_tt_rank_profile,
    plot_revertibility_witness,
)

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _assert_png(path: Path) -> None:
    assert path.exists(), f"missing: {path}"
    assert path.stat().st_size > 0, f"empty: {path}"
    with path.open("rb") as fh:
        assert fh.read(8) == PNG_HEADER


# ---------------------------------------------------------------------------
# Synthetic-record fixtures (no pymdp dependency)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _FakeMultiKResult:
    """Minimal duck-type compatible with :class:`MultiKResult`."""

    K: int
    lam: float
    total_correlation: float
    aligned_mass: float
    tt_ranks: tuple[int, ...]


def _make_multi_k_results(k: int, n_lams: int = 5, max_lam: float = 4.0) -> list[_FakeMultiKResult]:
    """Generate a monotone-in-λ synthetic sweep for one K."""
    lams = np.linspace(0.0, max_lam, n_lams).tolist()
    return [
        _FakeMultiKResult(
            K=k,
            lam=float(lam),
            total_correlation=0.5 * float(lam),  # monotone in λ
            aligned_mass=0.5 + 0.4 * float(lam) / max_lam,
            tt_ranks=tuple(2 for _ in range(k - 1)),
        )
        for lam in lams
    ]


@dataclass(frozen=True)
class _FakeLongHorizon:
    """Minimal duck-type compatible with :class:`LongHorizonResult`."""

    T: int
    lam: float
    total_correlations: np.ndarray
    marginal_trajectories: tuple[np.ndarray, ...]
    tail_marginal_means: tuple[np.ndarray, ...]
    tail_kl_per_stream: tuple[float, ...]
    tail_kl_first_per_stream: tuple[float, ...]
    tail_kl_mean_per_stream: tuple[float, ...]
    tail_kl_max_per_stream: tuple[float, ...]
    habit_accumulation: bool
    steady_state_tol: float
    seed: int = 0
    tail_window: int = field(default=4)


def _make_long_horizon(t: int = 20, k: int = 2) -> _FakeLongHorizon:
    rng = np.random.default_rng(0)
    margs = tuple(rng.dirichlet(alpha=[1.0, 1.0], size=t).astype(np.float64) for _ in range(k))
    means = tuple(np.array([0.4, 0.6], dtype=np.float64) for _ in range(k))
    return _FakeLongHorizon(
        T=t,
        lam=1.5,
        total_correlations=np.linspace(0.05, 0.4, t).astype(np.float64),
        marginal_trajectories=margs,
        tail_marginal_means=means,
        tail_kl_per_stream=tuple(1e-5 for _ in range(k)),
        tail_kl_first_per_stream=tuple(1e-5 for _ in range(k)),
        tail_kl_mean_per_stream=tuple(1e-5 for _ in range(k)),
        tail_kl_max_per_stream=tuple(1e-5 for _ in range(k)),
        habit_accumulation=True,
        steady_state_tol=1e-4,
    )


@dataclass(frozen=True)
class _FakeRevertRecord:
    """Minimal duck-type compatible with :class:`RevertibilityRecord`."""

    lam: float
    multi_information: float
    kl_q_to_mproj: float
    marginal_max_abs_diff: float


def _make_revert_records(n: int = 4) -> list[_FakeRevertRecord]:
    lams = np.linspace(0.0, 3.0, n)
    return [
        _FakeRevertRecord(
            lam=float(lam),
            multi_information=0.3 * float(lam),
            kl_q_to_mproj=0.3 * float(lam),  # KL == I (identity holds).
            marginal_max_abs_diff=1e-12,
        )
        for lam in lams
    ]


# ---------------------------------------------------------------------------
# T1: multi-K plots
# ---------------------------------------------------------------------------


def test_plot_multi_k_total_correlation_writes_png(tmp_path: Path) -> None:
    results_by_k = {
        2: _make_multi_k_results(2),
        3: _make_multi_k_results(3),
    }
    out = plot_multi_k_total_correlation(results_by_k, out_path=tmp_path / "tc.png", metadata={"k": "test"})
    _assert_png(out)


def test_plot_multi_k_aligned_mass_writes_png(tmp_path: Path) -> None:
    results_by_k = {2: _make_multi_k_results(2), 4: _make_multi_k_results(4)}
    out = plot_multi_k_aligned_mass(results_by_k, out_path=tmp_path / "mass.png")
    _assert_png(out)


def test_plot_multi_k_tt_rank_profile_writes_png(tmp_path: Path) -> None:
    results_by_k = {
        3: _make_multi_k_results(3),
        4: _make_multi_k_results(4),
    }
    out = plot_multi_k_tt_rank_profile(results_by_k, out_path=tmp_path / "tt.png", lam_index=-1)
    _assert_png(out)


def test_plot_multi_k_tt_rank_profile_honours_lam_index(tmp_path: Path) -> None:
    """Selecting the first λ index must also render without crashing."""
    results_by_k = {3: _make_multi_k_results(3, n_lams=6)}
    out = plot_multi_k_tt_rank_profile(results_by_k, out_path=tmp_path / "tt0.png", lam_index=0)
    _assert_png(out)


# ---------------------------------------------------------------------------
# T2: long-horizon plots
# ---------------------------------------------------------------------------


def test_plot_long_horizon_marginals_writes_png(tmp_path: Path) -> None:
    result = _make_long_horizon()
    out = plot_long_horizon_marginals(result, out_path=tmp_path / "marg.png", metadata={"horizon": "20"})
    _assert_png(out)


def test_plot_long_horizon_steady_state_writes_png(tmp_path: Path) -> None:
    result = _make_long_horizon()
    out = plot_long_horizon_steady_state(result, out_path=tmp_path / "ss.png")
    _assert_png(out)


def test_plot_long_horizon_steady_state_handles_failed_habit(tmp_path: Path) -> None:
    """Cover the ``habit_accumulation=False`` title branch."""
    base = _make_long_horizon()
    failing = _FakeLongHorizon(
        T=base.T,
        lam=base.lam,
        total_correlations=base.total_correlations,
        marginal_trajectories=base.marginal_trajectories,
        tail_marginal_means=base.tail_marginal_means,
        tail_kl_per_stream=tuple(1e-2 for _ in base.tail_kl_per_stream),
        tail_kl_first_per_stream=tuple(1e-2 for _ in base.tail_kl_per_stream),
        tail_kl_mean_per_stream=tuple(1e-2 for _ in base.tail_kl_per_stream),
        tail_kl_max_per_stream=tuple(1e-2 for _ in base.tail_kl_per_stream),
        habit_accumulation=False,
        steady_state_tol=base.steady_state_tol,
        seed=0,
    )
    out = plot_long_horizon_steady_state(failing, out_path=tmp_path / "ss_fail.png")
    _assert_png(out)


# ---------------------------------------------------------------------------
# T3: revertibility plot
# ---------------------------------------------------------------------------


def test_plot_revertibility_witness_writes_png(tmp_path: Path) -> None:
    records = _make_revert_records()
    out = plot_revertibility_witness(records, out_path=tmp_path / "rev.png", metadata={"who": "tests"})
    _assert_png(out)


def test_plot_revertibility_witness_with_single_lambda(tmp_path: Path) -> None:
    """Degenerate length-1 record sequence must still render."""
    records = _make_revert_records(n=1)
    out = plot_revertibility_witness(records, out_path=tmp_path / "rev1.png")
    _assert_png(out)
