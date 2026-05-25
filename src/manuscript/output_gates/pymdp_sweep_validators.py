"""pymdp simulation CSV artifact validators — sweep and free-energy bundle."""

from __future__ import annotations

import csv
from functools import partial

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates._reporting import ok as report_ok
from manuscript.output_gates.constants import OUTPUT_DIR
from manuscript.output_gates.csv_helpers import (
    parameter_sweep_required_columns,
)
from manuscript.output_gates.sweep_validation import (
    finite,
    validate_lambda_zero_mean_field_row,
    validate_tc_decomposition_group,
)
from simulation import hyperparameters as H  # noqa: N812


def _multi_k_sweep_row_extras(group: list[dict[str, str]], *, k: int) -> int:
    """Validate aligned_mass and tt_ranks columns for one multi-K sweep group."""
    fail = 0
    for r in group:
        aligned = finite(r["aligned_mass"])
        if not (0.0 <= aligned <= 1.0 + 1e-9):
            report_fail(f"K={k}: λ={r['lambda']} aligned_mass {aligned} outside [0, 1]")
            fail += 1
        tts = r["tt_ranks"].split("|") if r["tt_ranks"] else []
        if len(tts) != k - 1:
            report_fail(f"K={k}: λ={r['lambda']} tt_ranks length {len(tts)} != K-1 = {k - 1}")
            fail += 1
            continue
        for x in tts:
            try:
                if int(x) < 1:
                    report_fail(f"K={k}: λ={r['lambda']} tt_ranks entry < 1: {x}")
                    fail += 1
            except ValueError:
                report_fail(f"K={k}: λ={r['lambda']} tt_ranks not integer: {x}")
                fail += 1
    return fail


def _multi_k_after(group: list[dict[str, str]], _tcs: list[float], *, k: int) -> int:
    return _multi_k_sweep_row_extras(group, k=k)


def validate_sweep() -> int:
    print("[parameter sweep]")
    path = OUTPUT_DIR / "data" / "parameter_sweep.csv"
    if not path.exists():
        report_ok("(optional, not present)")
        return 0
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        required = parameter_sweep_required_columns()
        missing = required - set(reader.fieldnames or [])
        if missing:
            report_fail(f"missing columns: {sorted(missing)}")
            return 1
        rows = list(reader)
    if len(rows) < 2:
        report_fail("fewer than 2 rows")
        return 1
    fail = 0
    if len(rows) != int(H.PARAMETER_SWEEP_LAMBDAS.num):
        report_fail(
            f"parameter sweep rows {len(rows)} != H.PARAMETER_SWEEP_LAMBDAS.num {H.PARAMETER_SWEEP_LAMBDAS.num}"
        )
        fail += 1
    tol = float(H.PARAMETER_SWEEP_AGREEMENT_TOLERANCE)
    for r in rows:
        diff = float(r["mi_closed_form"]) - float(r["mi_empirical"])
        if abs(diff) > tol:
            report_fail(f"λ={r['lambda']}: closed-form vs empirical MI differ by {diff:.3e}")
            fail += 1
    if fail == 0:
        report_ok(f"{len(rows)} rows, closed-form / empirical MI agree to {tol:.0e}")
    return fail


def validate_free_energy_bundle() -> int:
    print("[pymdp free-energy bundle]")
    path = OUTPUT_DIR / "simulations" / "pymdp_free_energy_bundle.csv"
    if not path.exists():
        report_ok("(optional, not present)")
        return 0
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        required = {
            "lambda",
            "vfe_total",
            "joint_entropy",
            "marginal_entropy_sum",
            "total_correlation",
            "coupling_term",
            "decomposition_lhs",
            "decomposition_rhs",
            "decomposition_residual",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            report_fail(f"missing columns: {sorted(missing)}")
            return 1
        rows = list(reader)
    if len(rows) < 2:
        report_fail("fewer than 2 rows")
        return 1
    fail = 0
    zero_tol = float(H.PYMDP_COUPLING_ZERO_TOLERANCE)
    tc_zero_tol = float(H.PYMDP_TC_ZERO_TOLERANCE)
    entropy_tol = float(H.PYMDP_ENTROPY_ADD_TOLERANCE)
    decomp_tol = float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)
    r0 = next((r for r in rows if abs(float(r["lambda"])) < zero_tol), None)
    if r0 is not None:
        fail += validate_lambda_zero_mean_field_row(
            r0,
            label="pymdp free-energy bundle",
            zero_tol=zero_tol,
            tc_zero_tol=tc_zero_tol,
            entropy_tol=entropy_tol,
        )
    fail += validate_tc_decomposition_group(
        rows,
        label="pymdp free-energy bundle",
        grid=H.PYMDP_SWEEP_LAMBDAS,
        tol=decomp_tol,
        entropy_tol=entropy_tol,
        zero_tol=zero_tol,
        check_lhs_rhs=True,
        finite_columns=(
            "vfe_total",
            "joint_entropy",
            "marginal_entropy_sum",
            "coupling_term",
            "decomposition_lhs",
            "decomposition_rhs",
        ),
    )
    if fail == 0:
        report_ok(f"{len(rows)} rows; λ=0 baseline + TC ≥ 0 everywhere")
    return fail


def validate_multi_k_sweep() -> int:
    """Validate the configured multi-K sweep CSVs (one per K)."""
    print("[pymdp multi-K sweep]")
    fail = 0
    for K in H.MULTI_K_VALUES:  # noqa: N806 — K = number of streams (manuscript symbol).
        path = OUTPUT_DIR / "simulations" / f"pymdp_K{K}_sweep.csv"
        if not path.exists():
            report_ok(f"(optional, not present): {path.name}")
            continue
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            required = {
                "lambda",
                "total_correlation",
                "joint_entropy",
                "marginal_entropy_sum",
                "coupling_term",
                "aligned_mass",
                "tt_ranks",
            }
            missing = required - set(reader.fieldnames or [])
            if missing:
                report_fail(f"K={K}: missing columns: {sorted(missing)}")
                fail += 1
                continue
            rows = list(reader)
        if len(rows) < 2:
            report_fail(f"K={K}: fewer than 2 rows in {path}")
            fail += 1
            continue
        zero_tol = float(H.PYMDP_COUPLING_ZERO_TOLERANCE)
        tc_zero_tol = float(H.PYMDP_TC_ZERO_TOLERANCE)
        entropy_tol = float(H.PYMDP_ENTROPY_ADD_TOLERANCE)
        decomp_tol = float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)
        label = f"K={K} multi-K sweep"
        fail += validate_tc_decomposition_group(
            rows,
            label=label,
            grid=H.MULTI_K_SWEEP_LAMBDAS,
            tol=decomp_tol,
            entropy_tol=entropy_tol,
            zero_tol=zero_tol,
            monotonic_tc=True,
            check_decomposition=False,
            finite_columns=("coupling_term", "aligned_mass"),
            after_group=partial(_multi_k_after, k=K),
        )
        r0 = next((r for r in rows if abs(float(r["lambda"])) < zero_tol), None)
        if r0 is not None:
            fail += validate_lambda_zero_mean_field_row(
                r0,
                label=label,
                zero_tol=zero_tol,
                tc_zero_tol=tc_zero_tol,
                entropy_tol=entropy_tol,
            )
        if fail == 0:
            report_ok(f"K={K}: {len(rows)} rows; λ=0 mean-field + TC ≥ 0 everywhere")
    return fail
