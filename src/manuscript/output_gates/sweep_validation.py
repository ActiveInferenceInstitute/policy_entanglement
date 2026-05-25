"""Shared TC / decomposition validation helpers for pymdp CSV gates."""

from __future__ import annotations

import math
from collections.abc import Callable

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates.csv_helpers import rows_match_grid


def finite(value: str | float) -> float:
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"{value!r} is not finite")
    return x


def validate_lambda_zero_mean_field_row(
    row: dict[str, str],
    *,
    label: str,
    zero_tol: float,
    tc_zero_tol: float,
    entropy_tol: float,
    check_coupling_term: bool = True,
) -> int:
    """Validate λ≈0 mean-field baseline on a single sweep row."""
    fail = 0
    if abs(float(row["total_correlation"])) > tc_zero_tol:
        report_fail(f"{label}: λ=0 total_correlation = {row['total_correlation']}")
        fail += 1
    if check_coupling_term and abs(float(row["coupling_term"])) > zero_tol:
        report_fail(f"{label}: λ=0 coupling_term = {row['coupling_term']}")
        fail += 1
    gap = float(row["marginal_entropy_sum"]) - float(row["joint_entropy"])
    if abs(gap) > entropy_tol:
        report_fail(f"{label}: λ=0 H-gap = {gap}")
        fail += 1
    return fail


def validate_tc_decomposition_group(
    group: list[dict[str, str]],
    *,
    label: str,
    grid,
    tol: float,
    entropy_tol: float,
    zero_tol: float,
    monotonic_tc: bool = False,
    after_group: Callable[[list[dict[str, str]], list[float]], int] | None = None,
) -> int:
    """Validate one λ-sweep group for TC, entropy gap, and decomposition residual."""
    fail = rows_match_grid(group, grid, label=label)
    tcs = [finite(r["total_correlation"]) for r in group]
    if abs(tcs[0]) > zero_tol:
        report_fail(f"{label}: λ=0 TC {tcs[0]} != 0")
        fail += 1
    if monotonic_tc and any(tcs[i + 1] + 1e-9 < tcs[i] for i in range(len(tcs) - 1)):
        report_fail(f"{label}: TC is non-monotone")
        fail += 1
    for r, tc in zip(group, tcs, strict=True):
        if tc < -zero_tol:
            report_fail(f"{label}: λ={r['lambda']} TC {tc} < 0")
            fail += 1
        gap = finite(r["marginal_entropy_sum"]) - finite(r["joint_entropy"])
        if abs(gap - tc) > entropy_tol:
            report_fail(f"{label}: λ={r['lambda']} H-gap {gap} != TC {tc}")
            fail += 1
        residual = finite(r["decomposition_residual"])
        if residual > tol:
            report_fail(f"{label}: λ={r['lambda']} residual {residual} > {tol}")
            fail += 1
    if after_group is not None:
        fail += after_group(group, tcs)
    return fail
