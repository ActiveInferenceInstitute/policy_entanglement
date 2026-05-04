#!/usr/bin/env python3
"""Validate every artefact under ``output/`` after the figure /
variable / sweep scripts have run.

Checks:

* Every PNG figure exists, is non-empty, and is a valid PNG header.
* The manuscript-variables JSON parses, has every required key, and
  the values are finite floats in plausible ranges.
* The parameter-sweep CSV (if present) parses, has the right columns,
  and the closed-form / empirical MI columns agree to floating
  tolerance.

Thin orchestrator — exits non-zero on any failure, suitable as a
post-pipeline gate in CI.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

REQUIRED_FIGURES = [
    # Legacy 6 (manuscript core).
    "ising_mi_curve.png",
    "free_energy_curve.png",
    "coupling_tax_quadratic.png",
    "phase_diagram.png",
    "optimal_lambda.png",
    "schmidt_rank.png",
    # New visualizations subpackage figures.
    "phase_landscape.png",
    "schmidt_entropy_surface.png",
    "joint_heatmap_lambda2.png",
    "archetype_dendrogram.png",
    "tensor_train_rank_surface.png",
    "log_weight_flow.png",
    "kl_geodesic_simplex.png",
    "lambda_star_locus.png",
]

# Optional figures that exist only when their generator runs (sim / viz groups).
OPTIONAL_FIGURES = [
    "coupling_graph.png",
    "pymdp_total_correlation_curve.png",
    "pymdp_coupled_rollout.png",
    "pymdp_joint_lambda_0.00.png",
    "pymdp_joint_lambda_2.00.png",
    "pymdp_joint_lambda_4.00.png",
]

REQUIRED_VARIABLES = {
    # Bernoulli / Ising closed-form
    "ising_mi_at_lam_05": (0.0, 0.05),
    "ising_mi_at_lam_1": (0.05, 0.20),
    "ising_mi_at_lam_2": (0.20, 0.45),
    "ising_mi_saturation": (0.69, 0.70),
    "lambda_star_delta_05": (1.0, 1.2),
    "lambda_star_delta_09": (2.8, 3.1),
    # Spectral facts (added in v0.2)
    "ising_S_E_at_lam_0": (-1e-9, 1e-9),
    "ising_S_E_at_lam_1": (0.0, 0.5),
    "ising_S_E_at_lam_3": (0.0, 0.7),
    "ising_schmidt_rank_at_lam_0": (1.0, 1.0),
    "ising_schmidt_rank_at_lam_1": (2.0, 2.0),
}

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _fail(msg: str) -> None:
    print(f"  ✗ {msg}", file=sys.stderr)


def _ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def _check_png(path: Path, *, optional: bool = False) -> int:
    if not path.exists():
        if optional:
            _ok(f"(optional, not present): {path.name}")
            return 0
        _fail(f"missing: {path}")
        return 1
    size = path.stat().st_size
    if size <= 0:
        _fail(f"empty: {path}")
        return 1
    with path.open("rb") as fh:
        header = fh.read(8)
    if header != PNG_HEADER:
        _fail(f"not a PNG: {path}")
        return 1
    _ok(f"{path.relative_to(PROJECT_ROOT)} ({size} bytes)")
    return 0


def validate_figures() -> int:
    print("[figures]")
    fail = 0
    figdir = OUTPUT_DIR / "figures"
    for name in REQUIRED_FIGURES:
        fail += _check_png(figdir / name)
    print("[optional figures]")
    for name in OPTIONAL_FIGURES:
        fail += _check_png(figdir / name, optional=True)
    return fail


def validate_variables() -> int:
    print("[manuscript variables]")
    fail = 0
    path = OUTPUT_DIR / "data" / "manuscript_variables.json"
    if not path.exists():
        _fail(f"missing: {path}")
        return 1
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        _fail(f"invalid JSON: {exc}")
        return 1
    for key, (lo, hi) in REQUIRED_VARIABLES.items():
        if key not in data:
            _fail(f"missing key: {key}")
            fail += 1
            continue
        val = data[key]
        if not isinstance(val, (int, float)):
            _fail(f"{key} is not numeric: {val!r}")
            fail += 1
            continue
        if not (lo <= val <= hi):
            _fail(f"{key} = {val} out of range [{lo}, {hi}]")
            fail += 1
            continue
        _ok(f"{key} = {val:.6g} ∈ [{lo}, {hi}]")
    # TT rank profiles (added in v0.2): just check shape and integer-ness.
    for K in (2, 3, 4, 5):
        key = f"tt_ranks_K{K}"
        prof = data.get(key)
        if prof is None:
            _fail(f"missing key: {key}")
            fail += 1
            continue
        if not isinstance(prof, list) or len(prof) != K - 1:
            _fail(f"{key} must be a list of length {K-1}, got {prof!r}")
            fail += 1
            continue
        if not all(isinstance(r, int) and r >= 1 for r in prof):
            _fail(f"{key} entries must be positive integers: {prof!r}")
            fail += 1
            continue
        _ok(f"{key} = {prof}")
    return fail


def validate_sweep() -> int:
    print("[parameter sweep]")
    path = OUTPUT_DIR / "data" / "parameter_sweep.csv"
    if not path.exists():
        _ok("(optional, not present)")
        return 0
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        required = {
            "lambda", "mi_closed_form", "mi_empirical", "mi_residual",
            "free_energy_u0", "free_energy_u1", "free_energy_u2",
            "schmidt_rank", "entanglement_entropy", "phase",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            _fail(f"missing columns: {sorted(missing)}")
            return 1
        rows = list(reader)
    if len(rows) < 2:
        _fail("fewer than 2 rows")
        return 1
    fail = 0
    for r in rows:
        diff = float(r["mi_closed_form"]) - float(r["mi_empirical"])
        if abs(diff) > 1e-6:
            _fail(f"λ={r['lambda']}: closed-form vs empirical MI differ by {diff:.3e}")
            fail += 1
    if fail == 0:
        _ok(f"{len(rows)} rows, closed-form / empirical MI agree to 1e-6")
    return fail


def main() -> int:
    total = 0
    total += validate_figures()
    total += validate_variables()
    total += validate_sweep()
    print()
    if total == 0:
        print("All output validations passed.")
        return 0
    print(f"FAILED: {total} issue(s)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
