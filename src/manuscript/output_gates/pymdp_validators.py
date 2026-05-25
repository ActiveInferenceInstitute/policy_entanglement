"""pymdp simulation CSV artifact validators."""

from __future__ import annotations

import csv
import json

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates._reporting import ok as report_ok
from manuscript.output_gates.constants import OUTPUT_DIR
from manuscript.output_gates.csv_helpers import (
    parameter_sweep_required_columns,
    read_csv_rows,
    rows_match_grid,
)
from manuscript.output_gates.sweep_validation import (
    finite,
    validate_lambda_zero_mean_field_row,
    validate_tc_decomposition_group,
)
from simulation import hyperparameters as H  # noqa: N812


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
        report_fail(f"parameter sweep rows {len(rows)} != H.PARAMETER_SWEEP_LAMBDAS.num {H.PARAMETER_SWEEP_LAMBDAS.num}")
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
    fail += rows_match_grid(rows, H.PYMDP_SWEEP_LAMBDAS, label="pymdp free-energy bundle")
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
    for r in rows:
        tc = finite(r["total_correlation"])
        h_gap = finite(r["marginal_entropy_sum"]) - finite(r["joint_entropy"])
        if tc < -zero_tol:
            report_fail(f"λ={r['lambda']}: TC = {r['total_correlation']} < 0")
            fail += 1
        if abs(h_gap - tc) > entropy_tol:
            report_fail(f"λ={r['lambda']}: H-gap {h_gap} != TC {tc}")
            fail += 1
        lhs = finite(r["decomposition_lhs"])
        rhs = finite(r["decomposition_rhs"])
        residual = finite(r["decomposition_residual"])
        if abs(lhs - rhs) > decomp_tol:
            report_fail(f"λ={r['lambda']}: decomposition lhs/rhs gap {abs(lhs - rhs)}")
            fail += 1
        if residual > decomp_tol:
            report_fail(f"λ={r['lambda']}: decomposition residual {residual}")
            fail += 1
        for col in (
            "vfe_total",
            "joint_entropy",
            "marginal_entropy_sum",
            "coupling_term",
            "decomposition_lhs",
            "decomposition_rhs",
        ):
            try:
                finite(r[col])
            except ValueError as exc:
                report_fail(f"λ={r['lambda']}: {col} invalid ({exc})")
                fail += 1
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
        fail += rows_match_grid(rows, H.MULTI_K_SWEEP_LAMBDAS, label=f"K={K} multi-K sweep")
        # TC must be non-negative everywhere and finite.
        prev_tc = -float("inf")
        for r in rows:
            tc = finite(r["total_correlation"])
            h_gap = finite(r["marginal_entropy_sum"]) - finite(r["joint_entropy"])
            if tc < -float(H.PYMDP_COUPLING_ZERO_TOLERANCE):
                report_fail(f"K={K}: λ={r['lambda']} TC = {tc} < 0")
                fail += 1
            if abs(h_gap - tc) > float(H.PYMDP_ENTROPY_ADD_TOLERANCE):
                report_fail(f"K={K}: λ={r['lambda']} H-gap {h_gap} != TC {tc}")
                fail += 1
            if tc + 1e-9 < prev_tc:
                report_fail(f"K={K}: λ={r['lambda']} TC non-monotone ({tc} < {prev_tc})")
                fail += 1
            prev_tc = tc
            aligned = finite(r["aligned_mass"])
            if not (0.0 <= aligned <= 1.0 + 1e-9):
                report_fail(f"K={K}: λ={r['lambda']} aligned_mass {aligned} outside [0, 1]")
                fail += 1
            # tt_ranks: `|`-separated positive integers, length K-1.
            tts = r["tt_ranks"].split("|") if r["tt_ranks"] else []
            if len(tts) != K - 1:
                report_fail(f"K={K}: λ={r['lambda']} tt_ranks length {len(tts)} != K-1 = {K - 1}")
                fail += 1
                continue
            for x in tts:
                try:
                    if int(x) < 1:
                        report_fail(f"K={K}: λ={r['lambda']} tt_ranks entry < 1: {x}")
                        fail += 1
                except ValueError:
                    report_fail(f"K={K}: λ={r['lambda']} tt_ranks not integer: {x}")
                    fail += 1
        zero_tol = float(H.PYMDP_COUPLING_ZERO_TOLERANCE)
        tc_zero_tol = float(H.PYMDP_TC_ZERO_TOLERANCE)
        entropy_tol = float(H.PYMDP_ENTROPY_ADD_TOLERANCE)
        r0 = next((r for r in rows if abs(float(r["lambda"])) < zero_tol), None)
        if r0 is not None:
            fail += validate_lambda_zero_mean_field_row(
                r0,
                label=f"K={K} multi-K sweep",
                zero_tol=zero_tol,
                tc_zero_tol=tc_zero_tol,
                entropy_tol=entropy_tol,
            )
        if fail == 0:
            report_ok(f"K={K}: {len(rows)} rows; λ=0 mean-field + TC ≥ 0 everywhere")
    return fail


def validate_long_horizon() -> int:
    """Validate the configured long-horizon rollout CSV."""
    print("[pymdp long-horizon]")
    path = OUTPUT_DIR / "simulations" / "pymdp_long_horizon.csv"
    if not path.exists():
        report_ok("(optional, not present)")
        return 0
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        required = {"t", "total_correlation"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            report_fail(f"missing columns: {sorted(missing)}")
            return 1
        rows = list(reader)
    expected_steps = int(H.LONG_HORIZON_STEPS)
    if len(rows) != expected_steps:
        report_fail(f"long-horizon CSV length {len(rows)} != expected {expected_steps}")
        return 1
    fail = 0
    for idx, r in enumerate(rows):
        if int(r["t"]) != idx:
            report_fail(f"long-horizon row {idx}: t={r['t']} not sequential")
            fail += 1
        tc = finite(r["total_correlation"])
        if tc < -float(H.PYMDP_COUPLING_ZERO_TOLERANCE):
            report_fail(f"t={r['t']} TC = {tc} invalid")
            fail += 1
        marg_cols = [c for c in r if c.startswith("q") and "_u" in c]
        for prefix in sorted({c.split("_", 1)[0] for c in marg_cols}):
            mass = sum(finite(r[c]) for c in marg_cols if c.startswith(prefix + "_"))
            if abs(mass - 1.0) > 1e-6:
                report_fail(f"t={r['t']} {prefix} marginal mass {mass} != 1")
                fail += 1
    summary_path = OUTPUT_DIR / "data" / "long_horizon_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        diff = float(summary.get("long_horizon_tc_recomputed_max_abs_diff", float("inf")))
        if diff > 1e-9:
            report_fail(f"long-horizon recomputed TC max abs diff {diff} > 1e-9")
            fail += 1
        if int(summary.get("long_horizon_tail_window", -1)) != int(H.LONG_HORIZON_TAIL_WINDOW):
            report_fail("long-horizon summary tail window does not match hyperparameters")
            fail += 1
        required_summary = {
            "long_horizon_tail_kl_first_max",
            "long_horizon_tail_kl_mean_max",
            "long_horizon_tail_kl_window_max",
            "long_horizon_adjacent_kl_mean_max",
            "long_horizon_adjacent_kl_max",
        }
        missing_summary = required_summary - set(summary)
        if missing_summary:
            report_fail(f"long-horizon summary missing keys {sorted(missing_summary)}")
            fail += 1
        else:
            tail_window_max = float(summary["long_horizon_tail_kl_window_max"])
            if tail_window_max > float(H.LONG_HORIZON_STEADY_STATE_TOL):
                report_fail(f"long-horizon tail-window max KL {tail_window_max} > {float(H.LONG_HORIZON_STEADY_STATE_TOL)}")
                fail += 1
            if float(summary["long_horizon_adjacent_kl_max"]) < 0.0:
                report_fail("long-horizon adjacent-step KL max is negative")
                fail += 1
    if fail == 0:
        report_ok(f"{len(rows)} steps; TC finite and ≥ 0 throughout")
    return fail


def validate_revertibility() -> int:
    """Validate the m-projection / revertibility CSV."""
    print("[pymdp revertibility]")
    path = OUTPUT_DIR / "simulations" / "pymdp_revertibility.csv"
    if not path.exists():
        report_ok("(optional, not present)")
        return 0
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        required = {
            "lambda",
            "multi_information",
            "kl_q_to_mproj",
            "kl_identity_residual",
            "marginal_max_abs_diff",
            "marginals_match",
            "kl_identity_holds",
            "revertible",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            report_fail(f"missing columns: {sorted(missing)}")
            return 1
        rows = list(reader)
    if len(rows) != len(H.REVERTIBILITY_LAMBDAS):
        report_fail(f"revertibility rows {len(rows)} != expected {len(H.REVERTIBILITY_LAMBDAS)}")
        return 1
    fail = 0
    # Identity must hold to floating tolerance and marginal recovery must be exact.
    kl_tol = float(H.REVERTIBILITY_KL_IDENTITY_TOLERANCE)
    marginal_tol = float(H.REVERTIBILITY_TOLERANCE)
    for idx, (r, expected_lam) in enumerate(zip(rows, H.REVERTIBILITY_LAMBDAS, strict=True)):
        if abs(float(r["lambda"]) - float(expected_lam)) > 1e-9:
            report_fail(f"revertibility row {idx}: λ={r['lambda']} != expected {expected_lam}")
            fail += 1
        I_q = float(r["multi_information"])  # noqa: N806 — I = multi-information (manuscript symbol).
        kl = float(r["kl_q_to_mproj"])
        residual = float(r["kl_identity_residual"])
        marg_diff = float(r["marginal_max_abs_diff"])
        if residual > kl_tol:
            report_fail(f"λ={r['lambda']}: KL identity residual = {residual} > {kl_tol:.0e}")
            fail += 1
        if marg_diff > marginal_tol:
            report_fail(f"λ={r['lambda']}: marginal max diff = {marg_diff} > {marginal_tol:.0e}")
            fail += 1
        # KL ≈ I (sanity recompute against the dedicated columns).
        if abs(I_q - kl) > kl_tol:
            report_fail(f"λ={r['lambda']}: |I - KL| = {abs(I_q - kl)} > {kl_tol:.0e} (I={I_q}, KL={kl})")
            fail += 1
        if int(r["revertible"]) != 1:
            report_fail(f"λ={r['lambda']}: revertible flag = 0")
            fail += 1
        if int(r["marginals_match"]) != 1 or int(r["kl_identity_holds"]) != 1:
            report_fail(f"λ={r['lambda']}: boolean witness flags not all true")
            fail += 1
    if fail == 0:
        report_ok(f"{len(rows)} λ values; KL≡I + marginal recovery hold throughout")
    return fail


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
        report_ok(f"{len(rows)} rows across {len(expected_scenarios)} scenarios; decomposition residuals within tolerance")
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


def validate_long_horizon_replicates() -> int:
    """Validate long-horizon replicate sidecars."""

    print("[pymdp long-horizon replicates]")
    path = OUTPUT_DIR / "simulations" / "pymdp_long_horizon_replicates.csv"
    required = {
        "seed",
        "t",
        "total_correlation",
        "habit_accumulation",
        "tail_kl_window_max",
        "adjacent_kl_max",
    }
    rows, fail = read_csv_rows(path, required)
    if fail or not rows:
        return fail
    expected_seeds = {int(s) for s in H.LONG_HORIZON_REPLICATE_SEEDS}
    got_seeds = {int(r["seed"]) for r in rows}
    if got_seeds != expected_seeds:
        report_fail(f"replicate seeds {sorted(got_seeds)} != expected {sorted(expected_seeds)}")
        fail += 1
    expected_rows = len(expected_seeds) * int(H.LONG_HORIZON_STEPS)
    if len(rows) != expected_rows:
        report_fail(f"replicate rows {len(rows)} != expected {expected_rows}")
        fail += 1
    for seed in sorted(got_seeds):
        group = sorted((r for r in rows if int(r["seed"]) == seed), key=lambda r: int(r["t"]))
        if len(group) != int(H.LONG_HORIZON_STEPS):
            report_fail(f"seed {seed}: {len(group)} rows != {int(H.LONG_HORIZON_STEPS)}")
            fail += 1
        for idx, r in enumerate(group):
            if int(r["t"]) != idx:
                report_fail(f"seed {seed}: row {idx} has t={r['t']}")
                fail += 1
            tc = finite(r["total_correlation"])
            if tc < -float(H.PYMDP_COUPLING_ZERO_TOLERANCE):
                report_fail(f"seed {seed}: t={r['t']} TC {tc} < 0")
                fail += 1
            if int(r["habit_accumulation"]) not in {0, 1}:
                report_fail(f"seed {seed}: habit_accumulation flag {r['habit_accumulation']} not 0/1")
                fail += 1
            finite(r["tail_kl_window_max"])
            finite(r["adjacent_kl_max"])
    summary_path = OUTPUT_DIR / "data" / "long_horizon_replicates_summary.json"
    if not summary_path.exists():
        report_fail("missing long_horizon_replicates_summary.json")
        fail += 1
    else:
        summary = json.loads(summary_path.read_text())
        if int(float(summary.get("long_horizon_replicate_seed_count", -1))) != len(expected_seeds):
            report_fail("long-horizon replicate summary seed count does not match hyperparameters")
            fail += 1
        pass_rate = float(summary.get("long_horizon_replicate_habit_pass_rate", float("nan")))
        if not (0.0 <= pass_rate <= 1.0):
            report_fail(f"long-horizon replicate pass rate {pass_rate} outside [0, 1]")
            fail += 1
        finite(summary.get("long_horizon_replicate_tc_final_mean", "nan"))
        finite(summary.get("long_horizon_replicate_tail_kl_window_max", "nan"))
    if fail == 0:
        report_ok(f"{len(rows)} rows across {len(expected_seeds)} seeds; TC trajectories finite")
    return fail


def validate_long_horizon_seed_diagnostics() -> int:
    """Validate per-seed long-horizon diagnostic CSV."""

    print("[pymdp long-horizon seed diagnostics]")
    path = OUTPUT_DIR / "simulations" / "pymdp_long_horizon_seed_diagnostics.csv"
    required = {
        "seed",
        "habit_accumulation",
        "tc_final",
        "tc_max",
        "tail_kl_window_max",
        "adjacent_kl_max",
        "margin_to_tolerance",
        "failure_mode",
    }
    rows, fail = read_csv_rows(path, required)
    if fail or not rows:
        return fail
    expected_seeds = {int(s) for s in H.LONG_HORIZON_REPLICATE_SEEDS}
    got_seeds = {int(r["seed"]) for r in rows}
    if got_seeds != expected_seeds:
        report_fail(f"seed diagnostics {sorted(got_seeds)} != expected {sorted(expected_seeds)}")
        fail += 1
    if len(rows) != len(expected_seeds):
        report_fail(f"seed diagnostics rows {len(rows)} != expected {len(expected_seeds)}")
        fail += 1
    for r in rows:
        habit = int(r["habit_accumulation"])
        if habit not in {0, 1}:
            report_fail(f"seed {r['seed']}: habit flag {habit} not 0/1")
            fail += 1
        tail_kl = finite(r["tail_kl_window_max"])
        margin = finite(r["margin_to_tolerance"])
        expected_margin = float(H.LONG_HORIZON_STEADY_STATE_TOL) - tail_kl
        if abs(margin - expected_margin) > 1e-8:
            report_fail(f"seed {r['seed']}: margin {margin} != tolerance-tail_kl {expected_margin}")
            fail += 1
        mode = r["failure_mode"]
        if habit == 1 and mode != "passes":
            report_fail(f"seed {r['seed']}: passing replicate has failure_mode={mode!r}")
            fail += 1
        if habit == 0 and mode != "tail_window_kl_above_tol":
            report_fail(f"seed {r['seed']}: failing replicate has failure_mode={mode!r}")
            fail += 1
        finite(r["tc_final"])
        finite(r["tc_max"])
        finite(r["adjacent_kl_max"])
    if fail == 0:
        report_ok(f"{len(rows)} seed diagnostics; failure modes match threshold semantics")
    return fail


def validate_long_horizon_threshold_sensitivity() -> int:
    """Validate pass-rate sensitivity rows for long-horizon diagnostics."""

    print("[pymdp long-horizon threshold sensitivity]")
    path = OUTPUT_DIR / "simulations" / "pymdp_long_horizon_threshold_sensitivity.csv"
    required = {"threshold", "pass_rate", "pass_count", "fail_count", "ci_low", "ci_high"}
    rows, fail = read_csv_rows(path, required)
    if fail or not rows:
        return fail
    expected = [float(x) for x in H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS]
    if len(rows) != len(expected):
        report_fail(f"threshold sensitivity rows {len(rows)} != expected {len(expected)}")
        fail += 1
    seed_count = len(H.LONG_HORIZON_REPLICATE_SEEDS)
    rates: list[float] = []
    for idx, (row, threshold) in enumerate(zip(rows, expected, strict=False)):
        got_threshold = finite(row["threshold"])
        if abs(got_threshold - threshold) > 1e-12:
            report_fail(f"threshold row {idx}: {got_threshold} != expected {threshold}")
            fail += 1
        rate = finite(row["pass_rate"])
        rates.append(rate)
        if not (0.0 <= rate <= 1.0):
            report_fail(f"threshold row {idx}: pass_rate {rate} outside [0, 1]")
            fail += 1
        ci_low = finite(row["ci_low"])
        ci_high = finite(row["ci_high"])
        if not (0.0 <= ci_low <= rate <= ci_high <= 1.0):
            report_fail(f"threshold row {idx}: Wilson CI [{ci_low}, {ci_high}] does not bracket rate {rate}")
            fail += 1
        passed = int(row["pass_count"])
        failed = int(row["fail_count"])
        if passed + failed != seed_count:
            report_fail(f"threshold row {idx}: pass/fail count {passed}+{failed} != {seed_count}")
            fail += 1
        expected_rate = passed / seed_count if seed_count else 0.0
        if abs(rate - expected_rate) > 1e-12:
            report_fail(f"threshold row {idx}: pass_rate {rate} != pass_count/seed_count {expected_rate}")
            fail += 1
    if any(rates[i + 1] + 1e-12 < rates[i] for i in range(len(rates) - 1)):
        report_fail("threshold pass rates should be nondecreasing as the KL threshold loosens")
        fail += 1
    if fail == 0:
        report_ok(f"{len(rows)} thresholds; pass rates monotone and count-consistent")
    return fail


def validate_run_log() -> int:
    print("[pymdp run log]")
    path = OUTPUT_DIR / "logs" / "pymdp_runs.jsonl"
    if not path.exists():
        report_ok("(optional, not present)")
        return 0
    fail = 0
    n_records = n_ok = n_main_start = n_main_end = 0
    sections_seen: set[str] = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            report_fail(f"malformed JSONL line: {exc}")
            fail += 1
            continue
        n_records += 1
        if "timestamp" not in rec:
            report_fail(f"record missing timestamp: {rec}")
            fail += 1
        if rec.get("status") == "ok":
            n_ok += 1
        if rec.get("event") == "main_start":
            n_main_start += 1
        if rec.get("event") == "main_end":
            n_main_end += 1
        if "section" in rec:
            sections_seen.add(str(rec["section"]))
    if n_records < 3:
        report_fail(f"expected ≥3 records (main_start + section + main_end), got {n_records}")
        fail += 1
    expected_sections = {
        "figure_pymdp_lambda_sweep",
        "figure_pymdp_rollout",
        "figure_pymdp_free_energies",
    }
    missing = expected_sections - sections_seen
    if missing:
        report_fail(f"run log missing sections: {sorted(missing)}")
        fail += 1
    if fail == 0:
        report_ok(
            f"{n_records} records ({n_ok} ok, {n_main_start} main_start, "
            f"{n_main_end} main_end); sections={sorted(sections_seen)}"
        )
    return fail


