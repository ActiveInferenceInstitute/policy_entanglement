"""Long-horizon replicate sidecars, diagnostics, and Wilson summaries."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

from . import hyperparameters as H  # noqa: N812
from .long_horizon import LongHorizonResult, long_horizon_rollout
from .robustness_scenarios import (
    LongHorizonReplicateRecord,
    LongHorizonSeedDiagnostic,
    LongHorizonThresholdSensitivityRow,
    _fmt_float,
)
from .robustness_stats import _z_95_two_sided, wilson_score_interval


def run_long_horizon_replicates(
    seeds: Sequence[int] | None = None,
    *,
    progress_callback: Callable[[int, int, int], None] | None = None,
) -> list[LongHorizonResult]:
    """Run long-horizon replicate sidecars for configured seeds."""

    seed_values = [int(seed) for seed in (H.LONG_HORIZON_REPLICATE_SEEDS if seeds is None else seeds)]
    results: list[LongHorizonResult] = []
    for idx, seed in enumerate(seed_values, start=1):
        if progress_callback is not None:
            progress_callback(idx, len(seed_values), seed)
        results.append(
            long_horizon_rollout(
                coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
                gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
                num_streams=int(H.PYMDP_ENSEMBLE_K),
                horizon=int(H.LONG_HORIZON_STEPS),
                lam=float(H.LONG_HORIZON_LAMBDA),
                seed=seed,
                tail_window=int(H.LONG_HORIZON_TAIL_WINDOW),
                steady_state_tol=float(H.LONG_HORIZON_STEADY_STATE_TOL),
            )
        )
    return results


def long_horizon_replicate_record(result: LongHorizonResult) -> LongHorizonReplicateRecord:
    """Scalar summary for one long-horizon replicate."""

    return LongHorizonReplicateRecord(
        seed=int(result.seed),
        habit_accumulation=bool(result.habit_accumulation),
        tc_initial=float(result.total_correlations[0]),
        tc_final=float(result.total_correlations[-1]),
        tc_mean=float(np.mean(result.total_correlations)),
        tc_max=float(np.max(result.total_correlations)),
        tail_kl_window_max=float(max(result.tail_kl_max_per_stream)),
        adjacent_kl_max=float(max(result.adjacent_kl_max_per_stream)),
    )


def long_horizon_seed_diagnostic(result: LongHorizonResult) -> LongHorizonSeedDiagnostic:
    """Interpret one replicate against the configured tail-window tolerance."""

    tail_kl = float(max(result.tail_kl_max_per_stream))
    steady_state_tol = float(getattr(result, "steady_state_tol", H.LONG_HORIZON_STEADY_STATE_TOL))
    margin = steady_state_tol - tail_kl
    return LongHorizonSeedDiagnostic(
        seed=int(result.seed),
        habit_accumulation=bool(result.habit_accumulation),
        tc_final=float(result.total_correlations[-1]),
        tc_max=float(np.max(result.total_correlations)),
        tail_kl_window_max=tail_kl,
        adjacent_kl_max=float(max(result.adjacent_kl_max_per_stream)),
        margin_to_tolerance=margin,
        failure_mode="passes" if result.habit_accumulation else "tail_window_kl_above_tol",
    )


def long_horizon_seed_diagnostics(results: Sequence[LongHorizonResult]) -> list[LongHorizonSeedDiagnostic]:
    """Return per-seed long-horizon diagnostic rows."""

    if not results:
        raise ValueError("results must be non-empty")
    return [long_horizon_seed_diagnostic(result) for result in results]


def long_horizon_threshold_pass_rates(
    records: Sequence[LongHorizonSeedDiagnostic],
    thresholds: Sequence[float] | None = None,
) -> dict[str, float]:
    """Pass-rate sensitivity under alternative tail-window KL thresholds."""

    rows = long_horizon_threshold_sensitivity(records, thresholds)
    return {f"long_horizon_replicate_pass_rate_tol_{_fmt_float(r.threshold)}": r.pass_rate for r in rows}


def long_horizon_threshold_sensitivity(
    records: Sequence[LongHorizonSeedDiagnostic],
    thresholds: Sequence[float] | None = None,
) -> list[LongHorizonThresholdSensitivityRow]:
    """Structured pass-rate sensitivity under tail-window KL thresholds."""

    if not records:
        raise ValueError("records must be non-empty")
    probes = [float(x) for x in (H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS if thresholds is None else thresholds)]
    rows: list[LongHorizonThresholdSensitivityRow] = []
    for threshold in probes:
        pass_count = int(sum(1 for r in records if r.tail_kl_window_max <= threshold))
        total = len(records)
        ci_low, ci_high = wilson_score_interval(pass_count, total)
        rows.append(
            LongHorizonThresholdSensitivityRow(
                threshold=threshold,
                pass_rate=float(pass_count / total),
                pass_count=pass_count,
                fail_count=int(total - pass_count),
                ci_low=ci_low,
                ci_high=ci_high,
            )
        )
    return rows


def long_horizon_threshold_sensitivity_summary(
    records: Sequence[LongHorizonSeedDiagnostic],
    thresholds: Sequence[float] | None = None,
) -> dict[str, float]:
    """Compact summary of pass-rate sensitivity across thresholds."""

    rows = long_horizon_threshold_sensitivity(records, thresholds)
    rates = [r.pass_rate for r in rows]
    return {
        "long_horizon_replicate_threshold_count": float(len(rows)),
        "long_horizon_replicate_threshold_pass_rate_min": float(min(rates)),
        "long_horizon_replicate_threshold_pass_rate_max": float(max(rates)),
        "long_horizon_replicate_threshold_pass_rate_range": float(max(rates) - min(rates)),
    }


def long_horizon_tc_envelope(results: Sequence[LongHorizonResult]) -> dict[str, list[float]]:
    """Quantile envelope over replicate total-correlation trajectories."""

    if not results:
        raise ValueError("results must be non-empty")
    horizon = int(results[0].T)
    for result in results:
        if int(result.T) != horizon:
            raise ValueError("all replicate results must share the same horizon")
    arr = np.stack([np.asarray(r.total_correlations, dtype=np.float64) for r in results], axis=0)
    return {
        "t": [float(x) for x in range(horizon)],
        "q25": [float(x) for x in np.quantile(arr, 0.25, axis=0)],
        "median": [float(x) for x in np.quantile(arr, 0.50, axis=0)],
        "q75": [float(x) for x in np.quantile(arr, 0.75, axis=0)],
        "min": [float(x) for x in np.min(arr, axis=0)],
        "max": [float(x) for x in np.max(arr, axis=0)],
    }


def summarize_long_horizon_replicates(
    results: Sequence[LongHorizonResult],
) -> tuple[list[LongHorizonReplicateRecord], dict[str, float]]:
    """Per-seed records plus flat manuscript-variable summary."""

    if not results:
        raise ValueError("results must be non-empty")
    records = [long_horizon_replicate_record(result) for result in results]
    diagnostics = long_horizon_seed_diagnostics(results)
    success_count = int(sum(1 for r in records if r.habit_accumulation))
    pass_rate = float(success_count / len(records))
    ci_low, ci_high = wilson_score_interval(success_count, len(records))
    finals = np.array([r.tc_final for r in records], dtype=np.float64)
    flat = {
        "long_horizon_replicate_seed_count": float(len(records)),
        "long_horizon_replicate_success_count": float(success_count),
        "long_horizon_replicate_habit_pass_rate": pass_rate,
        "long_horizon_replicate_habit_pass_rate_ci_low": ci_low,
        "long_horizon_replicate_habit_pass_rate_ci_high": ci_high,
        "long_horizon_replicate_habit_pass_rate_ci_z": _z_95_two_sided(),
        "long_horizon_replicate_tc_final_mean": float(np.mean(finals)),
        "long_horizon_replicate_tc_final_min": float(np.min(finals)),
        "long_horizon_replicate_tc_final_max": float(np.max(finals)),
        "long_horizon_replicate_tail_kl_window_max": float(max(r.tail_kl_window_max for r in records)),
        "long_horizon_replicate_adjacent_kl_max": float(max(r.adjacent_kl_max for r in records)),
        "long_horizon_replicate_failure_count": float(sum(1 for r in diagnostics if not r.habit_accumulation)),
        "long_horizon_replicate_margin_to_tol_min": float(min(r.margin_to_tolerance for r in diagnostics)),
        "long_horizon_replicate_margin_to_tol_mean": float(np.mean([r.margin_to_tolerance for r in diagnostics])),
    }
    flat.update(long_horizon_threshold_pass_rates(diagnostics))
    flat.update(long_horizon_threshold_sensitivity_summary(diagnostics))
    return records, flat
