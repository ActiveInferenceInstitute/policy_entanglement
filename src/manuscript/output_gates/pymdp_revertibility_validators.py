"""pymdp simulation CSV artifact validators — revertibility witness and run log."""

from __future__ import annotations

import csv
import json

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates._reporting import ok as report_ok
from manuscript.output_gates.constants import OUTPUT_DIR
from simulation import hyperparameters as H  # noqa: N812


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
