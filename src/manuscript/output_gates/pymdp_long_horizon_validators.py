"""pymdp simulation CSV artifact validators — long-horizon rollout and replicates."""

from __future__ import annotations

import csv
import json

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates._reporting import ok as report_ok
from manuscript.output_gates.constants import OUTPUT_DIR
from manuscript.output_gates.csv_helpers import (
    read_csv_rows,
)
from manuscript.output_gates.sweep_validation import (
    finite,
)
from simulation import hyperparameters as H  # noqa: N812


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
                report_fail(
                    f"long-horizon tail-window max KL {tail_window_max} > {float(H.LONG_HORIZON_STEADY_STATE_TOL)}"
                )
                fail += 1
            if float(summary["long_horizon_adjacent_kl_max"]) < 0.0:
                report_fail("long-horizon adjacent-step KL max is negative")
                fail += 1
    if fail == 0:
        report_ok(f"{len(rows)} steps; TC finite and ≥ 0 throughout")
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
