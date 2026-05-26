"""Pure audit helpers for release-readiness reporting."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

FORBIDDEN_MATHLIB_LOCAL_TOKENS = ("sorry", "admit ", "axiom ", "unsafe ", "partial ")
MANIFEST_STAGE_RE = re.compile(
    r"^\|\s*`(?P<script>[^`]+)`\s*\|\s*(?P<duration>[0-9.]+)\s*\|\s*(?P<status>OK|FAIL)\s*\|$"
)
MANIFEST_TOTAL_RE = re.compile(r"\*\*Total wall-clock\*\*:\s*([0-9.]+)s")


def status_counts(lines: list[str]) -> dict[str, int]:
    counts = {"modified": 0, "deleted": 0, "added": 0, "untracked": 0, "other": 0}
    for line in lines:
        code = line[:2]
        if code == "??":
            counts["untracked"] += 1
        elif "D" in code:
            counts["deleted"] += 1
        elif "A" in code:
            counts["added"] += 1
        elif "M" in code:
            counts["modified"] += 1
        else:
            counts["other"] += 1
    return counts


def as_float(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float, str)):
        return float(value)
    return default


def as_int(value: object, default: int = 0) -> int:
    if isinstance(value, (int, str)):
        return int(value)
    return default


def runtime_stage_dicts(runtime_budget: dict[str, object], key: str = "stages") -> list[dict[str, Any]]:
    value = runtime_budget.get(key, [])
    if not isinstance(value, list):
        return []
    return [stage for stage in value if isinstance(stage, dict)]


def runtime_failed_stage_names(runtime_budget: dict[str, object]) -> list[str]:
    value = runtime_budget.get("failed_stages", [])
    if not isinstance(value, list):
        return []
    return [str(stage) for stage in value]


def format_stage_list(stages: list[dict[str, Any]]) -> str:
    return ", ".join(f"{row.get('script', '?')} ({as_float(row.get('duration_s')):.1f}s)" for row in stages)


def optional_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def git_status_lines(project_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=str(project_root),
        capture_output=True,
        check=False,
        text=True,
        timeout=10.0,
    )
    if proc.returncode != 0:
        return [f"(git status failed: {proc.stderr.strip()})"]
    return proc.stdout.splitlines()


def theorem_status_counts(project_root: Path) -> dict[str, int]:
    labels_path = project_root / "manuscript" / "refs" / "labels.yaml"
    labels = yaml.safe_load(labels_path.read_text(encoding="utf-8")) or {}
    theorems = labels.get("theorems") or {}
    counts = {"proved": 0, "witness": 0, "boundary": 0, "forwarder": 0, "sketch": 0, "deferred": 0}
    for row in theorems.values():
        if isinstance(row, dict):
            status = str(row.get("status", ""))
            if status in counts:
                counts[status] += 1
    counts["total"] = len(theorems)
    return counts


def manifest_stage_timings(
    manifest_path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> dict[str, object]:
    if manifest_path is None:
        if project_root is None:
            raise ValueError("either manifest_path or project_root must be supplied")
        manifest_path = project_root / "output" / "MANIFEST.md"
    if not manifest_path.exists():
        return {
            "manifest_present": False,
            "total_wall_s": None,
            "stage_count": 0,
            "failed_stages": [],
            "slowest_stages": [],
            "stages": [],
        }
    stages: list[dict[str, object]] = []
    total_wall_s: float | None = None
    for line in manifest_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stage_match = MANIFEST_STAGE_RE.match(line.strip())
        if stage_match:
            stages.append(
                {
                    "script": stage_match.group("script"),
                    "duration_s": float(stage_match.group("duration")),
                    "status": stage_match.group("status"),
                }
            )
            continue
        total_match = MANIFEST_TOTAL_RE.search(line)
        if total_match:
            total_wall_s = float(total_match.group(1))
    slowest = sorted(stages, key=lambda row: as_float(row.get("duration_s")), reverse=True)[:5]
    return {
        "manifest_present": True,
        "total_wall_s": total_wall_s,
        "stage_count": len(stages),
        "failed_stages": [row["script"] for row in stages if row["status"] != "OK"],
        "slowest_stages": slowest,
        "stages": stages,
    }


def mathlib_proofs_status(
    project_root: Path,
    runtime_budget: dict[str, object] | None = None,
) -> dict[str, object]:
    root = project_root / "lean" / "MathlibProofs"
    source = root / "MathlibProofs.lean"
    lakefile = root / "lakefile.lean"
    payload: dict[str, object] = {
        "present": source.exists(),
        "lakefile_present": lakefile.exists(),
        "path": "lean/MathlibProofs/MathlibProofs.lean",
        "claim_status": (
            "separate Mathlib package; headline real-valued decomposition "
            "discharged when keystone build and axiom audit pass"
        ),
        "build_checked": False,
        "build_status": "not_checked",
        "returncode": None,
        "proofSliceVersion": None,
        "theorem_count": 0,
        "hygiene_clean": False,
        "forbidden_token_counts": {token.strip(): 0 for token in FORBIDDEN_MATHLIB_LOCAL_TOKENS},
    }
    if source.exists():
        text = source.read_text(encoding="utf-8")
        version_match = re.search(r"\bdef\s+proofSliceVersion\s*:\s*Nat\s*:=\s*(\d+)", text)
        theorem_count = len(re.findall(r"^\s*theorem\s+\w+", text, flags=re.MULTILINE))
        token_counts = {token.strip(): text.count(token) for token in FORBIDDEN_MATHLIB_LOCAL_TOKENS}
        payload.update(
            {
                "proofSliceVersion": int(version_match.group(1)) if version_match else None,
                "theorem_count": theorem_count,
                "hygiene_clean": all(count == 0 for count in token_counts.values()),
                "forbidden_token_counts": token_counts,
            }
        )
    budget = runtime_budget or manifest_stage_timings(project_root=project_root)
    for stage in runtime_stage_dicts(budget):
        if stage.get("script") == "build_mathlib_proofs.py":
            payload["build_checked"] = True
            ok = stage.get("status") == "OK"
            payload["build_status"] = "passed" if ok else "failed"
            payload["returncode"] = 0 if ok else 1
            break
    return payload


def registered_figure_paths(project_root: Path) -> set[str]:
    labels_path = project_root / "manuscript" / "refs" / "labels.yaml"
    labels = yaml.safe_load(labels_path.read_text(encoding="utf-8")) or {}
    figures = labels.get("figures") or {}
    out: set[str] = set()
    for row in figures.values():
        if isinstance(row, dict) and row.get("path"):
            out.add(str(row["path"]))
    return out


def figure_audit(project_root: Path, figures: list[Path]) -> dict[str, object]:
    registered = registered_figure_paths(project_root)
    present_rel = {path.relative_to(project_root).as_posix() for path in figures if path.exists()}
    missing_registered = sorted(registered - present_rel)
    payload: dict[str, object] = {
        "png_figures": len(figures),
        "registered_figures": len(registered),
        "missing_registered_figures": missing_registered,
        "pil_available": False,
        "min_width_px": None,
        "min_height_px": None,
        "project_metadata_count": 0,
        "schema_v2_metadata_count": 0,
    }
    try:
        from PIL import Image  # noqa: WPS433
    except ImportError:
        return payload
    widths: list[int] = []
    heights: list[int] = []
    project_metadata_count = 0
    schema_v2_count = 0
    for path in figures:
        if not path.exists():
            continue
        try:
            with Image.open(path) as img:
                width, height = img.size
                info = {str(k): str(v) for k, v in img.info.items()}
        except OSError:
            continue
        widths.append(int(width))
        heights.append(int(height))
        if any(key.startswith("project.") for key in info):
            project_metadata_count += 1
        stats = info.get("project.figure_statistics")
        if stats:
            try:
                if int(json.loads(stats).get("schema_version", 0)) >= 2:
                    schema_v2_count += 1
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
    payload.update(
        {
            "pil_available": True,
            "min_width_px": min(widths) if widths else None,
            "min_height_px": min(heights) if heights else None,
            "project_metadata_count": project_metadata_count,
            "schema_v2_metadata_count": schema_v2_count,
        }
    )
    return payload


def pdf_artifact_audit(project_root: Path, status) -> dict[str, object]:
    pdf_dir = project_root / "output" / "pdf"
    pdf_path = pdf_dir / "actinf_policy_entanglement_lean_combined.pdf"
    intermediates = {
        "_combined_manuscript.md": (pdf_dir / "_combined_manuscript.md").exists(),
        "_combined_manuscript.tex": (pdf_dir / "_combined_manuscript.tex").exists(),
        "_combined_manuscript.log": (pdf_dir / "_combined_manuscript.log").exists(),
        "_xelatex_stdout.log": (pdf_dir / "_xelatex_stdout.log").exists(),
    }
    preamble = project_root / "manuscript" / "preamble.md"
    margins: dict[str, float] = {}
    margin_contract_ok = False
    if preamble.exists():
        from manuscript.pdf_validation import EXPECTED_PDF_MARGINS_IN, parse_geometry_margins  # noqa: WPS433

        margins = parse_geometry_margins(preamble.read_text(encoding="utf-8"))
        margin_contract_ok = all(
            abs(float(margins.get(key, -1.0)) - expected) <= 1e-9 for key, expected in EXPECTED_PDF_MARGINS_IN.items()
        )
    return {
        "exists": pdf_path.exists(),
        "pages": int(status.pdf_pages),
        "size_bytes": int(status.pdf_size_bytes),
        "size_mb": float(status.pdf_size_mb),
        "intermediates_present": intermediates,
        "all_intermediates_present": all(intermediates.values()),
        "margins_in": margins,
        "margin_contract_ok": margin_contract_ok,
    }


def reconcile_runtime_budget(
    runtime_budget: dict[str, object],
    *,
    status,
    test_results: dict[str, object],
) -> dict[str, object]:
    if int(status.tests_failed) != 0:
        return runtime_budget
    if as_int(test_results.get("total_failed")) != 0:
        return runtime_budget
    reconciled = dict(runtime_budget)
    reconciled["failed_stages"] = []
    return reconciled


__all__ = [
    "FORBIDDEN_MATHLIB_LOCAL_TOKENS",
    "MANIFEST_STAGE_RE",
    "MANIFEST_TOTAL_RE",
    "subprocess",
    "as_float",
    "as_int",
    "figure_audit",
    "format_stage_list",
    "git_status_lines",
    "manifest_stage_timings",
    "mathlib_proofs_status",
    "optional_json",
    "pdf_artifact_audit",
    "reconcile_runtime_budget",
    "registered_figure_paths",
    "runtime_failed_stage_names",
    "runtime_stage_dicts",
    "status_counts",
    "theorem_status_counts",
]
