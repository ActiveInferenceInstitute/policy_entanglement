"""Claim audit matrix rows for pymdp / Lean / manuscript cross-check."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

import yaml

from manuscript.registry import TheoremEntry, load_labels
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


def _normalize_test_path(gate: str) -> str:
    """Map registry or TEST_GATE shorthand to a tests/ path."""
    normalized = gate.strip()
    if normalized.startswith("tests/"):
        return normalized
    if normalized.endswith(".py"):
        return normalized if normalized.startswith("tests/") else f"tests/{normalized}"
    if normalized.startswith("test_"):
        return f"tests/{normalized}.py"
    return f"tests/test_{normalized}.py"


def _resolve_test_gate(label: str, entry: TheoremEntry) -> str:
    if entry.tests.strip():
        return _normalize_test_path(entry.tests)
    name = TEST_GATE.get(label, "")
    if not name:
        return "tests/test_veridical_status_doc.py"
    return _normalize_test_path(name)


def _theorem_row(label: str, entry: TheoremEntry) -> dict[str, str]:
    lean_path = (
        f"lean/ActinfPolicyEntanglement/{entry.lean_module}.lean"
        if entry.lean_module
        else "manuscript/refs/labels.yaml"
    )
    artifacts: list[str] = [lean_path]
    if entry.artifact:
        artifacts.append(entry.artifact)
    if label in {"thm_11_1", "prop_11_2"}:
        artifacts.append("docs/reference/_theorem_map.md")

    test_gate = _resolve_test_gate(label, entry)

    verdict = entry.status
    if entry.faithfulness:
        verdict = f"{entry.status}/{entry.faithfulness}"

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


def _load_audit_track_rows(project_root: Path) -> list[dict[str, str]]:
    tracks_path = project_root / "manuscript" / "refs" / "audit_tracks.yaml"
    payload = yaml.safe_load(tracks_path.read_text(encoding="utf-8")) or {}
    tracks = payload.get("tracks") or []
    rows: list[dict[str, str]] = []
    for index, track in enumerate(tracks):
        if not isinstance(track, dict):
            raise TypeError(f"audit_tracks.yaml tracks[{index}] must be a mapping")
        missing = [column for column in AUDIT_MATRIX_COLUMNS if column not in track]
        if missing:
            raise ValueError(f"audit_tracks.yaml tracks[{index}] missing columns: {missing}")
        rows.append({column: str(track[column]) for column in AUDIT_MATRIX_COLUMNS})
    return rows


def build_audit_matrix_rows(project_root: Path) -> list[dict[str, str]]:
    """Return ordered audit-matrix rows for the project."""
    labels_path = project_root / "manuscript" / "refs" / "labels.yaml"
    labels = load_labels(labels_path)
    rows: list[dict[str, str]] = []
    for label, entry in labels.theorems.items():
        rows.append(_theorem_row(label, entry))
    rows.extend(_load_audit_track_rows(project_root))
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
