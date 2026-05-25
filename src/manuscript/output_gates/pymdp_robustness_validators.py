"""pymdp simulation CSV artifact validators — robustness and ablation sweeps."""

from __future__ import annotations

import json

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates._reporting import ok as report_ok
from manuscript.output_gates.constants import OUTPUT_DIR
from manuscript.output_gates.csv_helpers import (
    read_csv_rows,
    rows_match_grid,
)
from manuscript.output_gates.sweep_validation import (
    finite,
    validate_tc_decomposition_group,
)
from simulation import hyperparameters as H  # noqa: N812


def validate_robustness_suite() -> int:
    """Validate robustness one-axis stress-test outputs."""

    print("[pymdp robustness suite]")
    path = OUTPUT_DIR / "simulations" / "pymdp_robustness.csv"
    required = {
        "scenario_id",
        "axis",
        "level",
        "observations",
        "gamma",
        "preference_strength",
        "coupling_scale",
        "lambda",
        "total_correlation",
        "joint_entropy",
        "marginal_entropy_sum",
        "coupling_term",
        "aligned_mass",
        "decomposition_lhs",
        "decomposition_rhs",
        "decomposition_residual",
    }
    rows, fail = read_csv_rows(path, required)
    if fail or not rows:
        return fail
    from simulation.robustness import robustness_scenarios  # noqa: WPS433

    expected_scenarios = {s.scenario_id for s in robustness_scenarios()}
    got_scenarios = {r["scenario_id"] for r in rows}
    if got_scenarios != expected_scenarios:
        report_fail(f"robustness scenarios {sorted(got_scenarios)} != expected {sorted(expected_scenarios)}")
        fail += 1
    expected_rows = len(expected_scenarios) * int(H.ROBUSTNESS_SWEEP_LAMBDAS.num)
    if len(rows) != expected_rows:
        report_fail(f"robustness rows {len(rows)} != expected {expected_rows}")
        fail += 1
    tol = float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)
    entropy_tol = float(H.PYMDP_ENTROPY_ADD_TOLERANCE)
    zero_tol = float(H.PYMDP_TC_ZERO_TOLERANCE)
    for scenario in sorted(got_scenarios):
        group = sorted((r for r in rows if r["scenario_id"] == scenario), key=lambda r: float(r["lambda"]))
        fail += validate_tc_decomposition_group(
            group,
            label=f"robustness {scenario}",
            grid=H.ROBUSTNESS_SWEEP_LAMBDAS,
            tol=tol,
            entropy_tol=entropy_tol,
            zero_tol=zero_tol,
            monotonic_tc=True,
        )
    null_rows = [r for r in rows if r["scenario_id"] == "coupling_0"]
    null_tc = max((finite(r["total_correlation"]) for r in null_rows), default=0.0)
    if null_tc > zero_tol:
        report_fail(f"robustness null-coupling flatline TC max {null_tc} > {zero_tol}")
        fail += 1
    summary_path = OUTPUT_DIR / "data" / "robustness_summary.json"
    if not summary_path.exists():
        report_fail("missing robustness_summary.json")
        fail += 1
    if fail == 0:
        report_ok(
            f"{len(rows)} rows across {len(expected_scenarios)} scenarios; decomposition residuals within tolerance"
        )
    return fail


def validate_coupling_ablation() -> int:
    """Validate fixed coupling-ablation outputs."""

    print("[pymdp coupling ablation]")
    path = OUTPUT_DIR / "simulations" / "pymdp_coupling_ablation.csv"
    required = {
        "variant",
        "lambda",
        "total_correlation",
        "joint_entropy",
        "marginal_entropy_sum",
        "coupling_term",
        "aligned_mass",
        "decomposition_lhs",
        "decomposition_rhs",
        "decomposition_residual",
    }
    rows, fail = read_csv_rows(path, required)
    if fail or not rows:
        return fail
    expected_variants = set(H.COUPLING_ABLATION_VARIANTS)
    got_variants = {r["variant"] for r in rows}
    if got_variants != expected_variants:
        report_fail(f"ablation variants {sorted(got_variants)} != expected {sorted(expected_variants)}")
        fail += 1
    expected_rows = len(expected_variants) * int(H.ROBUSTNESS_SWEEP_LAMBDAS.num)
    if len(rows) != expected_rows:
        report_fail(f"ablation rows {len(rows)} != expected {expected_rows}")
        fail += 1
    tol = float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)
    entropy_tol = float(H.PYMDP_ENTROPY_ADD_TOLERANCE)
    zero_tol = float(H.PYMDP_TC_ZERO_TOLERANCE)

    def _ablation_after(group: list[dict[str, str]], tcs: list[float]) -> int:
        variant = group[0]["variant"]
        local_fail = 0
        if variant == "null" and max(tcs, default=0.0) > zero_tol:
            report_fail(f"ablation null: TC max {max(tcs)} > {zero_tol}")
            local_fail += 1
        if variant != "null" and max(tcs, default=0.0) <= zero_tol:
            report_fail(f"ablation {variant}: expected positive TC somewhere on the sweep")
            local_fail += 1
        return local_fail

    for variant in sorted(got_variants):
        group = sorted((r for r in rows if r["variant"] == variant), key=lambda r: float(r["lambda"]))
        fail += validate_tc_decomposition_group(
            group,
            label=f"ablation {variant}",
            grid=H.ROBUSTNESS_SWEEP_LAMBDAS,
            tol=tol,
            entropy_tol=entropy_tol,
            zero_tol=zero_tol,
            after_group=_ablation_after,
        )
    summary_path = OUTPUT_DIR / "data" / "coupling_ablation_summary.json"
    if not summary_path.exists():
        report_fail("missing coupling_ablation_summary.json")
        fail += 1
    if fail == 0:
        report_ok(f"{len(rows)} rows across {len(expected_variants)} variants; null flatline and residual bounds hold")
    return fail


def validate_marginal_null_control() -> int:
    """Validate the fixed-marginal independence-control sidecar."""

    print("[pymdp marginal null control]")
    path = OUTPUT_DIR / "simulations" / "pymdp_marginal_null_control.csv"
    required = {
        "lambda",
        "original_total_correlation",
        "null_total_correlation",
        "original_aligned_mass",
        "null_aligned_mass",
        "tc_removed",
        "aligned_mass_shift",
    }
    rows, fail = read_csv_rows(path, required)
    if fail or not rows:
        return fail
    fail += rows_match_grid(rows, H.ROBUSTNESS_SWEEP_LAMBDAS, label="marginal null control")
    zero_tol = float(H.PYMDP_TC_ZERO_TOLERANCE)
    for row in rows:
        original_tc = finite(row["original_total_correlation"])
        null_tc = finite(row["null_total_correlation"])
        removed = finite(row["tc_removed"])
        if null_tc > zero_tol:
            report_fail(f"marginal null control λ={row['lambda']}: null TC {null_tc} > {zero_tol}")
            fail += 1
        if abs((original_tc - null_tc) - removed) > 1e-9:
            report_fail(f"marginal null control λ={row['lambda']}: tc_removed mismatch")
            fail += 1
        for key in ("original_aligned_mass", "null_aligned_mass"):
            value = finite(row[key])
            if not (0.0 <= value <= 1.0):
                report_fail(f"marginal null control λ={row['lambda']}: {key}={value} outside [0, 1]")
                fail += 1
    summary_path = OUTPUT_DIR / "data" / "marginal_null_control_summary.json"
    if not summary_path.exists():
        report_fail("missing marginal_null_control_summary.json")
        fail += 1
    else:
        summary = json.loads(summary_path.read_text())
        null_tc_max = finite(summary.get("robustness_null_control_max_tc", "nan"))
        if null_tc_max > zero_tol:
            report_fail(f"marginal null-control summary max TC {null_tc_max} > {zero_tol}")
            fail += 1
    if fail == 0:
        report_ok(f"{len(rows)} λ values; fixed-marginal product control removes TC")
    return fail


def validate_interaction_robustness() -> int:
    """Validate targeted two-axis robustness outputs."""

    print("[pymdp interaction robustness]")
    path = OUTPUT_DIR / "simulations" / "pymdp_interaction_robustness.csv"
    required = {
        "family",
        "scenario_id",
        "level_a",
        "level_b",
        "observations",
        "gamma",
        "preference_strength",
        "coupling_scale",
        "variant",
        "lambda",
        "total_correlation",
        "joint_entropy",
        "marginal_entropy_sum",
        "coupling_term",
        "aligned_mass",
        "decomposition_lhs",
        "decomposition_rhs",
        "decomposition_residual",
    }
    rows, fail = read_csv_rows(path, required)
    if fail or not rows:
        return fail
    from simulation.robustness import interaction_robustness_scenarios  # noqa: WPS433

    expected = interaction_robustness_scenarios()
    expected_ids = {s.scenario_id for s in expected}
    got_ids = {r["scenario_id"] for r in rows}
    if got_ids != expected_ids:
        report_fail(f"interaction scenarios {sorted(got_ids)} != expected {sorted(expected_ids)}")
        fail += 1
    expected_rows = len(expected_ids) * int(H.ROBUSTNESS_SWEEP_LAMBDAS.num)
    if len(rows) != expected_rows:
        report_fail(f"interaction rows {len(rows)} != expected {expected_rows}")
        fail += 1
    expected_families = set(H.ROBUSTNESS_INTERACTION_FAMILIES)
    got_families = {r["family"] for r in rows}
    if got_families != expected_families:
        report_fail(f"interaction families {sorted(got_families)} != expected {sorted(expected_families)}")
        fail += 1
    tol = float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)
    entropy_tol = float(H.PYMDP_ENTROPY_ADD_TOLERANCE)
    zero_tol = float(H.PYMDP_TC_ZERO_TOLERANCE)

    def _interaction_after(group: list[dict[str, str]], tcs: list[float]) -> int:
        if group[0]["variant"] == "null" and max(tcs, default=0.0) > zero_tol:
            report_fail(f"interaction {group[0]['scenario_id']}: null variant TC max {max(tcs)} > {zero_tol}")
            return 1
        return 0

    for scenario in sorted(got_ids):
        group = sorted((r for r in rows if r["scenario_id"] == scenario), key=lambda r: float(r["lambda"]))
        fail += validate_tc_decomposition_group(
            group,
            label=f"interaction {scenario}",
            grid=H.ROBUSTNESS_SWEEP_LAMBDAS,
            tol=tol,
            entropy_tol=entropy_tol,
            zero_tol=zero_tol,
            after_group=_interaction_after,
        )
    summary_path = OUTPUT_DIR / "data" / "interaction_robustness_summary.json"
    if not summary_path.exists():
        report_fail("missing interaction_robustness_summary.json")
        fail += 1
    if fail == 0:
        report_ok(f"{len(rows)} rows across {len(expected_ids)} two-axis scenarios")
    return fail
