#!/usr/bin/env python3
"""Manuscript completeness validator (token-aware).

Runs the full :mod:`manuscript.validation` suite over ``manuscript/``:

* Every section starts with a level-1 heading.
* Every ``[[FIG:label]]``, ``[[FIGREF:label]]``, ``[[EQ:label]]``,
  ``[[EQREF:label]]`` resolves to an entry in ``manuscript/refs/labels.yaml``.
* Every ``[@citekey]`` resolves to ``manuscript/refs/citations.yaml``.
* Every ``[[VAR:key]]`` resolves to ``output/data/manuscript_variables.json``.
* Every ``![alt](path)`` image references a file that exists on disk.
* Every relative Markdown ``[text](href)`` link resolves on disk.
* Every numeric variable lies inside the published expected range.

Exit code is non-zero on any failure — suitable as a CI gate.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
for _sub in ("", "lean", "simulation", "visualizations", "manuscript"):
    sys.path.insert(0, str(SRC_DIR / _sub if _sub else SRC_DIR))

from registry import load_registry  # noqa: E402
from validation import validate_manuscript_tree  # noqa: E402


# Numeric-range expectations for `output/data/manuscript_variables.json`.
EXPECTED_RANGES: dict[str, tuple[float, float]] = {
    "ising_mi_at_lam_05": (0.0, 0.05),
    "ising_mi_at_lam_1": (0.05, 0.20),
    "ising_mi_at_lam_2": (0.20, 0.45),
    "ising_mi_saturation": (0.69, 0.70),
    "lambda_star_delta_05": (1.0, 1.2),
    "lambda_star_delta_09": (2.8, 3.1),
    "ising_S_E_at_lam_0": (-1e-9, 1e-9),
    "ising_S_E_at_lam_1": (0.0, 0.5),
    "ising_S_E_at_lam_3": (0.0, 0.7),
    "ising_schmidt_rank_at_lam_0": (1.0, 1.0),
    "ising_schmidt_rank_at_lam_1": (2.0, 2.0),
    # Alignment + phase thresholds (added in v0.2.1)
    "ising_alignment_at_lam_05": (0.0, 0.30),
    "ising_alignment_at_lam_1": (0.40, 0.55),
    "ising_alignment_at_lam_2": (0.70, 0.80),
    "ising_alignment_at_lam_3": (0.85, 0.95),
    "phase_lambda_c1": (0.5, 0.5),
    "phase_lambda_c2": (2.5, 2.5),
    # Motor + attention worked numerics
    "motor_attention_aligned_prob_lam_0": (0.0, 1.0),
    "motor_attention_aligned_prob_lam_1": (0.0, 1.0),
    "motor_attention_aligned_prob_lam_2": (0.0, 1.0),
    # Coupling-tax curvature C estimate
    "coupling_tax_curvature_C": (0.0, 1.0),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate manuscript completeness.")
    parser.add_argument(
        "--manuscript-dir", type=Path, default=PROJECT_ROOT / "manuscript",
    )
    parser.add_argument(
        "--variables", type=Path,
        default=PROJECT_ROOT / "output" / "data" / "manuscript_variables.json",
    )
    args = parser.parse_args(argv)

    registry = load_registry(args.manuscript_dir / "refs")
    variables: dict[str, object] = {}
    if args.variables.exists():
        variables = json.loads(args.variables.read_text())

    report = validate_manuscript_tree(
        manuscript_dir=args.manuscript_dir,
        registry=registry,
        variables=variables,
        variable_ranges=EXPECTED_RANGES,
    )

    issues = 0
    print(f"[manuscript validation] {len(report.section_files)} section files")
    if report.missing_headings:
        for name in report.missing_headings:
            print(f"  ✗ {name}: missing leading heading")
            issues += 1
    if report.empty_captions:
        for ec in report.empty_captions:
            print(f"  ✗ {ec}")
            issues += 1
    if report.undefined_tokens:
        for name, tokens in report.undefined_tokens.items():
            for kind, label in tokens:
                print(f"  ✗ {name}: undefined {kind}:{label}")
                issues += 1
    if report.broken_links:
        for name, links in report.broken_links.items():
            for href in links:
                print(f"  ✗ {name}: broken link {href}")
                issues += 1
    if report.missing_figure_files:
        for name, imgs in report.missing_figure_files.items():
            for href in imgs:
                print(f"  ✗ {name}: missing image {href}")
                issues += 1
    if report.out_of_range_variables:
        for key, msg in report.out_of_range_variables.items():
            print(f"  ✗ variable {key}: {msg}")
            issues += 1
    if report.bad_section_refs:
        for name, refs in report.bad_section_refs.items():
            for r in refs:
                print(f"  ✗ {name}: undefined section reference {r}")
                issues += 1
    if report.hardcoded_refs:
        for name, refs in report.hardcoded_refs.items():
            for r in refs:
                print(f"  ✗ {name}: hardcoded reference {r!r} (use [[SECREF:...]] / [[THMREF:...]])")
                issues += 1

    if issues == 0:
        print("All manuscript validations passed.")
        return 0
    print(f"FAILED: {issues} issue(s)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
