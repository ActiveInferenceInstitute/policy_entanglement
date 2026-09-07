"""Pipeline stage graph and resolution."""

from __future__ import annotations

from dataclasses import dataclass

SCRIPTS: list[tuple[str, str]] = [
    ("build_lean.py", "lake build + sorry/axiom/unsafe budget gate"),
    ("generate_figures.py", "render every manuscript figure"),
    ("dump_archetypes.py", "dump K=2 Schmidt archetypes"),
    ("parameter_sweep.py", "fine-grained parameter sweep"),
    ("simulate_pymdp.py", "pymdp 1.0.1 POMDP simulation harness"),
    ("simulate_multi_k.py", "configured multi-K ensemble experiments"),
    ("simulate_long_horizon.py", "configured long-horizon habit-accumulation rollout"),
    ("simulate_revertibility.py", "m-projection back-to-mean-field witness"),
    ("simulate_robustness.py", "robustness, ablation, and replicate sidecars"),
    ("simulate_btai.py", "shipped BTAI head-to-head baseline worked run"),
    ("simulate_adversarial.py", "shipped adversarial-perturbation (epsilon, lambda)-grid sweep"),
    ("simulate_gnn.py", "GNN fifth-track round-trip (reconstruct I(lambda) from gnn/bernoulli_toy.gnn.md)"),
    ("manuscript_variables.py", "compute in-text variable substitutions"),
    ("build_dashboard.py", "interactive multi-view dashboard + plaintext invariants"),
    ("generate_index.py", "auto-generate docs/manuscript/INDEX.md from registry"),
    ("generate_theorem_map.py", "auto-generate per-theorem four-track wiring table"),
    ("inject_manuscript_variables.py", "render manuscript with auto-injected tokens"),
    ("validate_outputs.py", "validate every artifact"),
    ("validate_manuscript.py", "validate manuscript completeness (tokens + links)"),
    ("regression_gate.py", "compare current run vs scripts/regression_baseline.json"),
]

PDF_BUILD_SCRIPTS: list[tuple[str, str]] = [
    ("build_pdf.py", "render combined PDF with local Pandoc/XeLaTeX tooling"),
    ("validate_pdf.py", "validate PDF text, TeX, log, and margins"),
]

PDF_READINESS_SCRIPTS: list[tuple[str, str]] = [
    ("readiness_report.py", "write reviewer-facing release-readiness summary"),
]

PDF_SCRIPTS: list[tuple[str, str]] = PDF_BUILD_SCRIPTS + PDF_READINESS_SCRIPTS

MATHLIB_PROOF_SCRIPTS: list[tuple[str, str]] = [
    ("build_mathlib_proofs.py", "build optional additive MathlibProofs package"),
]

FAIL_FAST_VALIDATORS: frozenset[str] = frozenset(
    name
    for name, _ in (
        ("validate_outputs.py", ""),
        ("validate_manuscript.py", ""),
        *PDF_BUILD_SCRIPTS,
        *PDF_READINESS_SCRIPTS,
    )
)

PARALLEL_STAGE_STEMS: frozenset[str] = frozenset(
    {
        "dump_archetypes",
        "parameter_sweep",
        "simulate_pymdp",
        "simulate_multi_k",
        "simulate_long_horizon",
        "simulate_revertibility",
        "simulate_robustness",
        "simulate_btai",
        "simulate_adversarial",
    }
)


@dataclass(frozen=True)
class StageFlags:
    skip: frozenset[str]
    only: frozenset[str]
    with_pdf: bool
    with_mathlib: bool


def stage_stem(script: str) -> str:
    return script[:-3] if script.endswith(".py") else script


def included(stem: str, flags: StageFlags) -> bool:
    if stem in flags.skip:
        return False
    return not (flags.only and stem not in flags.only)


def resolve_stages(
    flags: StageFlags,
    scripts: list[tuple[str, str]] | None = None,
) -> list[tuple[str, str]]:
    """Return the ordered stage list after opt-in PDF/Mathlib extensions."""
    pending = list(SCRIPTS if scripts is None else scripts)
    requested_mathlib = flags.with_mathlib or bool({"build_mathlib_proofs"} & flags.only)
    if requested_mathlib:
        boundary_idx = next(
            (idx for idx, row in enumerate(pending) if row[0] == "build_lean.py"),
            -1,
        )
        insert_idx = boundary_idx + 1 if boundary_idx >= 0 else 0
        pending[insert_idx:insert_idx] = MATHLIB_PROOF_SCRIPTS

    requested_pdf = flags.with_pdf or bool({"build_pdf", "validate_pdf", "readiness_report"} & flags.only)
    if requested_pdf:
        regression_idx = next(
            (idx for idx, row in enumerate(pending) if row[0] == "regression_gate.py"),
            len(pending),
        )
        pending[regression_idx:regression_idx] = PDF_BUILD_SCRIPTS
        after_regression = regression_idx + len(PDF_BUILD_SCRIPTS) + 1
        pending[after_regression:after_regression] = PDF_READINESS_SCRIPTS
    return pending
