"""Manuscript completeness validator (library implementation).

Business logic for :doc:`scripts/validate_manuscript.py
</scripts/validate_manuscript>`. Runs the full
:func:`manuscript.validation.validate_manuscript_tree` suite over
``manuscript/`` and checks:

* Every section starts with a level-1 heading.
* Every ``[[FIG:label]]``, ``[[FIGREF:label]]``, ``[[EQ:label]]``,
  ``[[EQREF:label]]`` resolves to an entry in ``manuscript/refs/labels.yaml``.
* Every ``[@citekey]`` resolves to ``manuscript/refs/citations.yaml``.
* Every ``[[VAR:key]]`` resolves to ``output/data/manuscript_variables.json``.
* Every ``![alt](path)`` image references a file that exists on disk.
* Every relative Markdown ``[text](href)`` link resolves on disk.
* Every numeric variable lies inside the published expected range.

Returns 0 on a clean tree and a non-zero exit code on any failure
(suitable for use as a CI gate).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from manuscript.publication_metadata import publication_metadata_issues
from manuscript.registry import load_registry
from manuscript.status import (
    load_project_status,
    mathlibproofs_claim_issues,
    stale_reference_issues,
    stale_status_issues,
)
from manuscript.validation import (
    VARIABLE_PROVENANCE_CLASSES,
    validate_manuscript_tree,
    validate_rendered_token_leaks,
    variable_provenance_summary,
)
from manuscript.variable_ranges import ANALYTICAL_VARIABLE_RANGES
from simulation import hyperparameters as H  # noqa: N812 — manuscript convention

# Numeric-range expectations for `output/data/manuscript_variables.json`.
EXPECTED_RANGES: dict[str, tuple[float, float]] = ANALYTICAL_VARIABLE_RANGES


def build_parser(*, project_root: Path) -> argparse.ArgumentParser:
    """Build the validator argparse parser bound to ``project_root``."""
    parser = argparse.ArgumentParser(description="Validate manuscript completeness.")
    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        default=project_root / "manuscript",
    )
    parser.add_argument(
        "--variables",
        type=Path,
        default=project_root / "output" / "data" / "manuscript_variables.json",
    )
    parser.add_argument(
        "--rendered-dir",
        type=Path,
        default=project_root / "output" / "manuscript",
        help="Rendered manuscript directory to scan for unresolved post-injection tokens.",
    )
    return parser


def _report_issues(report) -> int:
    """Print every issue captured in ``report``; return the issue count."""
    issues = 0
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
    if report.hardcoded_numeric_literals:
        for name, refs in report.hardcoded_numeric_literals.items():
            for r in refs:
                print(
                    f"  ✗ {name}: hardcoded numeric literal {r!r} "
                    f"(use [[VAR:<key>]] sourced from output/data/manuscript_variables.json)"
                )
                issues += 1
    if report.hardcoded_rendered_source_fields:
        for name, refs in report.hardcoded_rendered_source_fields.items():
            for r in refs:
                print(
                    f"  ✗ {name}: hardcoded paper-facing source field {r!r} "
                    f"(use registry tokens or neutral wording; rendered output may contain resolved labels)"
                )
                issues += 1
    if report.tokens_in_code_fences:
        for name, refs in report.tokens_in_code_fences.items():
            for r in refs:
                print(
                    f"  ✗ {name}: cross-reference token {r!r} inside fenced code "
                    f"(move the reference outside the code block; only [[VAR:...]] is allowed there)"
                )
                issues += 1
    if report.broken_lean_wiring:
        for label, explanation in report.broken_lean_wiring.items():
            print(f"  ✗ four-track wiring [{label}]: {explanation}")
            issues += 1
    return issues


def _report_rendered_leaks(rendered_dir: Path, *, project_root: Path) -> int:
    """Scan rendered output dir for unresolved tokens; return issue count."""
    if not rendered_dir.exists():
        try:
            rendered_label = rendered_dir.relative_to(project_root)
        except ValueError:
            rendered_label = rendered_dir
        print(
            f"  • rendered token leak check skipped: {rendered_label} "
            "does not exist; run scripts/inject_manuscript_variables.py or scripts/run_all.py"
        )
        return 0
    rendered_files = sorted(rendered_dir.glob("*.md"))
    leaks = validate_rendered_token_leaks(rendered_dir)
    if not leaks:
        print(f"  ✓ rendered token leak check: {len(rendered_files)} rendered section files")
        return 0
    issues = 0
    for name, refs in leaks.items():
        for r in refs:
            print(
                f"  ✗ {name}: unresolved rendered token {r!r} outside code "
                "(rerun injection or move syntax examples into code spans)"
            )
            issues += 1
    return issues


def _report_status(project_root: Path) -> int:
    """Check status docs + stale-reference + MathlibProofs gates."""
    issues = 0
    try:
        live_status = load_project_status(project_root)
    except (FileNotFoundError, RuntimeError, json.JSONDecodeError, KeyError) as exc:
        for issue in stale_status_issues(project_root, require_live=False):
            print(f"  ✗ status docs: {issue}")
            issues += 1
        if issues == 0:
            print(f"  • status docs: live status artifacts unavailable; skipped live-count comparison ({exc})")
    else:
        for issue in stale_status_issues(project_root, live_status):
            print(f"  ✗ status docs: {issue}")
            issues += 1

    for issue in stale_reference_issues(project_root):
        print(f"  ✗ stale references: {issue}")
        issues += 1
    for issue in mathlibproofs_claim_issues(project_root):
        print(f"  ✗ MathlibProofs scope: {issue}")
        issues += 1
    for issue in publication_metadata_issues(project_root):
        print(f"  ✗ publication metadata: {issue}")
        issues += 1
    return issues


def main(
    argv: Sequence[str] | None = None,
    *,
    project_root: Path,
) -> int:
    """Run the validator gate. Returns 0 if clean; non-zero on issues."""
    parser = build_parser(project_root=project_root)
    args = parser.parse_args(list(argv) if argv is not None else None)

    registry = load_registry(args.manuscript_dir / "refs")
    variables: dict[str, object] = {}
    if args.variables.exists():
        variables = json.loads(args.variables.read_text())

    provenance = variable_provenance_summary(
        variables,
        hyperparameter_keys=frozenset(H.figure_hyperparameter_summary()),
    )

    report = validate_manuscript_tree(
        manuscript_dir=args.manuscript_dir,
        registry=registry,
        variables=variables,
        variable_ranges=EXPECTED_RANGES,
        lean_dir=project_root / "lean" / "ActinfPolicyEntanglement",
    )

    print(f"[manuscript validation] {len(report.section_files)} section files")
    if variables:
        summary_bits = [f"{name}: {provenance[name]}" for name in VARIABLE_PROVENANCE_CLASSES]
        print(f"[variable provenance] {', '.join(summary_bits)}")

    issues = _report_issues(report)
    issues += _report_rendered_leaks(args.rendered_dir, project_root=project_root)
    issues += _report_status(project_root)

    if issues == 0:
        print("All manuscript validations passed.")
        return 0
    print(f"FAILED: {issues} issue(s)", file=sys.stderr)
    return 1


__all__ = [
    "EXPECTED_RANGES",
    "build_parser",
    "main",
]
