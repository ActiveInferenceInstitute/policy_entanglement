"""Core release artifact validators (figures and manuscript variables)."""

from __future__ import annotations

import json

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates._reporting import ok as report_ok
from manuscript.output_gates.constants import (
    OPTIONAL_FIGURES,
    OUTPUT_DIR,
    REQUIRED_FIGURES,
    REQUIRED_VARIABLES,
)
from manuscript.output_gates.png_validation import check_png


def validate_figures() -> int:
    print("[figures]")
    fail = 0
    figdir = OUTPUT_DIR / "figures"
    for name in REQUIRED_FIGURES:
        fail += check_png(figdir / name)
    print("[optional figures]")
    for name in OPTIONAL_FIGURES:
        fail += check_png(figdir / name, optional=True)
    return fail


def validate_variables() -> int:
    print("[manuscript variables]")
    fail = 0
    path = OUTPUT_DIR / "data" / "manuscript_variables.json"
    if not path.exists():
        report_fail(f"missing: {path}")
        return 1
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        report_fail(f"invalid JSON: {exc}")
        return 1
    for key, (lo, hi) in REQUIRED_VARIABLES.items():
        if key not in data:
            report_fail(f"missing key: {key}")
            fail += 1
            continue
        val = data[key]
        if not isinstance(val, (int, float)):
            report_fail(f"{key} is not numeric: {val!r}")
            fail += 1
            continue
        if not (lo <= val <= hi):
            report_fail(f"{key} = {val} out of range [{lo}, {hi}]")
            fail += 1
            continue
        report_ok(f"{key} = {val:.6g} ∈ [{lo}, {hi}]")
    # TT rank profiles (added in v0.2): just check shape and integer-ness.
    for K in (2, 3, 4, 5):  # noqa: N806 — K = number of streams (manuscript symbol).
        key = f"tt_ranks_K{K}"
        prof = data.get(key)
        if prof is None:
            report_fail(f"missing key: {key}")
            fail += 1
            continue
        if not isinstance(prof, list) or len(prof) != K - 1:
            report_fail(f"{key} must be a list of length {K - 1}, got {prof!r}")
            fail += 1
            continue
        if not all(isinstance(r, int) and r >= 1 for r in prof):
            report_fail(f"{key} entries must be positive integers: {prof!r}")
            fail += 1
            continue
        report_ok(f"{key} = {prof}")
    return fail
