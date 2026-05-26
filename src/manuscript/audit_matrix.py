"""Claim audit matrix rows for pymdp / Lean / manuscript cross-check."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Any

import yaml

from manuscript.registry import load_labels
from manuscript.theorem_map import TEST_GATE

AUDIT_MATRIX_COLUMNS = (
    "claim_area",
    "public_surface",
    "generating_source",
    "config_or_var_key",
    "artifact_or_sidecar",
    "verification_gate",
    "verdict",
    "remediation",
)

EXTRA_TRACK_ROWS: tuple[dict[str, str], ...] = (
    {
        "claim_area": "pymdp free-energy bundle",
        "public_surface": "manuscript/4C_pymdp_harness.md; manuscript/4E_pymdp_validation.md",
        "generating_source": "scripts/simulate_pymdp.py",
        "config_or_var_key": "simulation.hyperparameters_pymdp",
        "artifact_or_sidecar": "output/simulations/pymdp_free_energy_bundle.csv",
        "verification_gate": "scripts/validate_outputs.py; tests/test_pymdp_pipeline.py",
        "verdict": "empirical",
        "remediation": "none",
    },
    {
        "claim_area": "pymdp robustness suite",
        "public_surface": "manuscript/4B_empirical_suite.md",
        "generating_source": "scripts/simulate_robustness.py",
        "config_or_var_key": "[[VAR:robustness_scenario_count]]",
        "artifact_or_sidecar": "output/simulations/pymdp_robustness.csv",
        "verification_gate": "scripts/validate_outputs.py; tests/test_robustness.py",
        "verdict": "empirical",
        "remediation": "none",
    },
    {
        "claim_area": "GNN fifth track (Bernoulli round-trip)",
        "public_surface": "manuscript/S08_gnn_generalized_notation_extension.md",
        "generating_source": "scripts/simulate_gnn.py; src/gnn/runner.py",
        "config_or_var_key": "[[VAR:gnn_roundtrip_max_residual]]",
        "artifact_or_sidecar": "output/data/gnn_bernoulli_roundtrip.json",
        "verification_gate": "tests/test_gnn_round_trip.py; tests/test_gnn_concordance.py",
        "verdict": "empirical",
        "remediation": "none",
    },
    {
        "claim_area": "MathlibProofs headline real-valued decomposition",
        "public_surface": "manuscript/2D_decomposition.md; docs/reference/methods_and_assumptions.md",
        "generating_source": "scripts/build_mathlib_proofs.py",
        "config_or_var_key": "labels.yaml::thm_4_1::mathlib_analytic_proof",
        "artifact_or_sidecar": "lean/MathlibProofs/MathlibProofs.lean",
        "verification_gate": "tests/test_mathlib_proofs_integrity.py; tests/test_mathlib_axiom_audit.py",
        "verdict": "proved-in-R",
        "remediation": "none",
    },
    {
        "claim_area": "Publication DOI and source repository",
        "public_surface": "README.md; AGENTS.md; manuscript/config.yaml; CITATION.cff",
        "generating_source": "src/manuscript/publication_metadata.py",
        "config_or_var_key": "publication.doi; publication.repository_url",
        "artifact_or_sidecar": "manuscript/config.yaml; CITATION.cff",
        "verification_gate": "tests/test_status_docs.py::publication_metadata_issues",
        "verdict": "canonical",
        "remediation": "none",
    },
    {
        "claim_area": "Regression and release readiness",
        "public_surface": "README.md; output/reports/release_readiness.md",
        "generating_source": "scripts/regression_gate.py; scripts/readiness_report.py",
        "config_or_var_key": "output/reports/test_results.json",
        "artifact_or_sidecar": "output/reports/test_results.json; output/reports/dashboard_invariants.txt",
        "verification_gate": "scripts/regression_gate.py; tests/test_regression_gate.py",
        "verdict": "47/47 invariants + 95% coverage gate",
        "remediation": "none",
    },
    {
        "claim_area": "Manuscript variable injection",
        "public_surface": "manuscript/SYNTAX.md; [[VAR:...]] tokens across manuscript",
        "generating_source": "scripts/manuscript_variables.py; src/manuscript/variables.py",
        "config_or_var_key": "output/data/manuscript_variables.json",
        "artifact_or_sidecar": "output/data/manuscript_variables.json",
        "verification_gate": "tests/test_manuscript_variables.py; tests/test_manuscript_validation.py",
        "verdict": "generated",
        "remediation": "none",
    },
)


def _resolve_test_gate(label: str, raw: dict[str, Any]) -> str:
    explicit = raw.get("tests")
    if isinstance(explicit, str) and explicit.strip():
        gate = explicit.strip()
        if gate.startswith("tests/"):
            return gate
        if gate.endswith(".py"):
            return f"tests/{gate}"
        return f"tests/test_{gate}.py"
    name = TEST_GATE.get(label, "")
    if not name:
        return "tests/test_veridical_status_doc.py"
    if name.startswith("tests/"):
        return name
    if name.endswith(".py"):
        return f"tests/{name}" if not name.startswith("tests/") else name
    if name.startswith("test_"):
        return f"tests/{name}.py"
    return f"tests/test_{name}.py"


def _theorem_row(label: str, entry: Any, raw: dict[str, Any]) -> dict[str, str]:
    lean_path = (
        f"lean/ActinfPolicyEntanglement/{entry.lean_module}.lean"
        if entry.lean_module
        else "manuscript/refs/labels.yaml"
    )
    artifacts: list[str] = [lean_path]
    artifact_field = raw.get("artifact")
    if artifact_field:
        artifacts.append(str(artifact_field))
    if label in {"thm_11_1", "prop_11_2"}:
        artifacts.append("docs/reference/_theorem_map.md")

    test_gate = _resolve_test_gate(label, raw)

    faithfulness = raw.get("faithfulness", "")
    verdict = entry.status
    if faithfulness:
        verdict = f"{entry.status}/{faithfulness}"

    remediation = "none"
    if entry.status in {"witness", "boundary"}:
        remediation = "MathlibProofs row-specific discharge or witness payload"
    elif entry.status == "roadmap":
        remediation = "Flocq/interval formal bridge or interval-bracket witness expansion"

    return {
        "claim_area": f"{label} ({entry.kind} {entry.number}: {entry.name})",
        "public_surface": f"[[THMREF:{label}]]; manuscript/refs/labels.yaml",
        "generating_source": lean_path,
        "config_or_var_key": f"manuscript/refs/labels.yaml::theorems::{label}",
        "artifact_or_sidecar": "; ".join(artifacts),
        "verification_gate": test_gate,
        "verdict": verdict,
        "remediation": remediation,
    }


def build_audit_matrix_rows(project_root: Path) -> list[dict[str, str]]:
    """Return ordered audit-matrix rows for the project."""
    labels_path = project_root / "manuscript" / "refs" / "labels.yaml"
    labels = load_labels(labels_path)
    raw_theorems = yaml.safe_load(labels_path.read_text(encoding="utf-8")).get("theorems") or {}
    rows: list[dict[str, str]] = []
    for label, entry in labels.theorems.items():
        rows.append(_theorem_row(label, entry, raw_theorems.get(label, {})))
    rows.extend(dict(row) for row in EXTRA_TRACK_ROWS)
    return rows


def render_audit_matrix_csv(project_root: Path) -> str:
    """Render the audit matrix CSV text."""
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=AUDIT_MATRIX_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in build_audit_matrix_rows(project_root):
        writer.writerow(row)
    return buffer.getvalue()


def write_audit_matrix(project_root: Path, output_path: Path | None = None) -> Path:
    """Write the audit matrix CSV and return its path."""
    target = output_path or (project_root / "docs" / "_audit" / "pymdp_lean_manuscript_matrix_2026-05-21.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_audit_matrix_csv(project_root), encoding="utf-8")
    return target


__all__ = [
    "AUDIT_MATRIX_COLUMNS",
    "build_audit_matrix_rows",
    "render_audit_matrix_csv",
    "write_audit_matrix",
]
