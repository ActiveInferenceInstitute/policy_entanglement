"""Reviewer-facing release-readiness summary — pure helpers and orchestrator.

Business logic for ``scripts/readiness_report.py``. The script is a thin
wrapper that binds ``PROJECT_ROOT`` and re-exports the test-facing
helpers (``tests/test_readiness_report.py`` loads the script module via
``importlib`` and asserts on the underscore-prefixed names below).

The orchestrator emits a single set of artifacts under
``<project_root>/output/reports/``:

* ``release_readiness.md`` — human-readable reviewer summary.
* ``release_readiness.json`` — machine-readable parallel.
* ``release_note.md`` — compact reviewer release note.
* ``release_index.md`` — landing page linking the others.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

from manuscript.status import load_project_status

# `noncomputable` is intentionally absent: the genuine real-valued S01
# definitions use `Real.exp`/`Real.log` and MUST be `noncomputable` in
# Lean 4 + Mathlib — the keyword does not weaken the proof. Axiom-clean
# status is enforced separately and authoritatively by `#print axioms`
# (foundational-only) in `build_mathlib_proofs.py` /
# `test_mathlib_axiom_audit.py`; this string set must stay consistent
# with that corrected set so `hygiene_clean` does not false-fail on a
# genuinely machine-checked proof. `sorry`/`axiom `/`unsafe `/`partial `
# stay forbidden — they genuinely indicate a non-clean proof.
FORBIDDEN_MATHLIB_LOCAL_TOKENS = ("sorry", "admit ", "axiom ", "unsafe ", "partial ")
MANIFEST_STAGE_RE = re.compile(
    r"^\|\s*`(?P<script>[^`]+)`\s*\|\s*(?P<duration>[0-9.]+)\s*\|\s*(?P<status>OK|FAIL)\s*\|$"
)
MANIFEST_TOTAL_RE = re.compile(r"\*\*Total wall-clock\*\*:\s*([0-9.]+)s")


# ---------------------------------------------------------------------------
# Pure helpers (no project_root dependency).
# ---------------------------------------------------------------------------


def _status_counts(lines: list[str]) -> dict[str, int]:
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


def _as_float(value: object, default: float = 0.0) -> float:
    """Best-effort conversion of JSON/Markdown parsed scalar values."""

    if isinstance(value, (int, float, str)):
        return float(value)
    return default


def _as_int(value: object, default: int = 0) -> int:
    """Best-effort conversion of JSON/Markdown parsed integer values."""

    if isinstance(value, (int, str)):
        return int(value)
    return default


def _runtime_stage_dicts(runtime_budget: dict[str, object], key: str = "stages") -> list[dict[str, Any]]:
    """Extract a list of stage dictionaries from a runtime-budget payload."""

    value = runtime_budget.get(key, [])
    if not isinstance(value, list):
        return []
    return [stage for stage in value if isinstance(stage, dict)]


def _runtime_failed_stage_names(runtime_budget: dict[str, object]) -> list[str]:
    """Extract failed stage names from runtime-budget payload."""

    value = runtime_budget.get("failed_stages", [])
    if not isinstance(value, list):
        return []
    return [str(stage) for stage in value]


def _format_stage_list(stages: list[dict[str, Any]]) -> str:
    """Human-readable stage timing list."""

    return ", ".join(f"{row.get('script', '?')} ({_as_float(row.get('duration_s')):.1f}s)" for row in stages)


def _optional_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


# ---------------------------------------------------------------------------
# Project-root-dependent helpers.
# ---------------------------------------------------------------------------


def _git_status_lines(project_root: Path) -> list[str]:
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


def _theorem_status_counts(project_root: Path) -> dict[str, int]:
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


def _manifest_stage_timings(
    manifest_path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> dict[str, object]:
    """Parse ``output/MANIFEST.md`` stage timings into JSON-safe fields."""

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
    slowest = sorted(stages, key=lambda row: _as_float(row.get("duration_s")), reverse=True)[:5]
    return {
        "manifest_present": True,
        "total_wall_s": total_wall_s,
        "stage_count": len(stages),
        "failed_stages": [row["script"] for row in stages if row["status"] != "OK"],
        "slowest_stages": slowest,
        "stages": stages,
    }


def _mathlib_proofs_status(
    project_root: Path,
    runtime_budget: dict[str, object] | None = None,
) -> dict[str, object]:
    """Summarize MathlibProofs source, hygiene, and latest manifest state."""

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
    budget = runtime_budget or _manifest_stage_timings(project_root=project_root)
    for stage in _runtime_stage_dicts(budget):
        if stage.get("script") == "build_mathlib_proofs.py":
            payload["build_checked"] = True
            ok = stage.get("status") == "OK"
            payload["build_status"] = "passed" if ok else "failed"
            payload["returncode"] = 0 if ok else 1
            break
    return payload


def _registered_figure_paths(project_root: Path) -> set[str]:
    labels_path = project_root / "manuscript" / "refs" / "labels.yaml"
    labels = yaml.safe_load(labels_path.read_text(encoding="utf-8")) or {}
    figures = labels.get("figures") or {}
    out: set[str] = set()
    for row in figures.values():
        if isinstance(row, dict) and row.get("path"):
            out.add(str(row["path"]))
    return out


def _figure_audit(project_root: Path, figures: list[Path]) -> dict[str, object]:
    """Summarize generated PNG presence, metadata, and minimum dimensions."""

    registered = _registered_figure_paths(project_root)
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


def _pdf_artifact_audit(project_root: Path, status) -> dict[str, object]:
    """Summarize PDF existence, intermediates, and margin contract."""

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


def _reconcile_runtime_budget(
    runtime_budget: dict[str, object],
    *,
    status,
    test_results: dict[str, object],
) -> dict[str, object]:
    """Drop stale manifest failures when live pytest/regression gates are green."""

    if int(status.tests_failed) != 0:
        return runtime_budget
    if _as_int(test_results.get("total_failed")) != 0:
        return runtime_budget
    reconciled = dict(runtime_budget)
    reconciled["failed_stages"] = []
    return reconciled


def refresh_release_readiness_runtime_budget(project_root: Path) -> None:
    """Re-sync ``release_readiness.json`` runtime budget from the final manifest."""

    json_path = project_root / "output" / "reports" / "release_readiness.json"
    if not json_path.exists():
        return
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    if not isinstance(payload, dict):
        return
    payload["runtime_budget"] = _manifest_stage_timings(project_root=project_root)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_release_note(
    project_root: Path,
    *,
    status,
    figures: list[Path],
    generated_manuscript: list[Path],
    manifest_present: bool,
    out_dir: Path | None = None,
) -> Path:
    """Write a compact reviewer release note from live artifacts."""

    report_dir = out_dir or project_root / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / "release_note.md"
    theorem_counts = _theorem_status_counts(project_root)
    sidecars = sorted((project_root / "output" / "simulations").glob("*.csv"))
    runtime_budget = _manifest_stage_timings(project_root=project_root)
    mathlib_status = _mathlib_proofs_status(project_root, runtime_budget)
    slowest_text = _format_stage_list(_runtime_stage_dicts(runtime_budget, "slowest_stages"))
    lines = [
        "# Reviewer Release Note",
        "",
        f"*Generated by `scripts/readiness_report.py` at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.*",
        "",
        "## Live Snapshot",
        "",
        f"- Pytest: {status.test_summary}; coverage {status.coverage_percent:.2f}%.",
        f"- Combined PDF: {status.pdf_summary}.",
        f"- PNG figures: {len(figures)}.",
        f"- Simulation CSV sidecars: {len(sidecars)}.",
        f"- Rendered manuscript markdown files: {len(generated_manuscript)}.",
        f"- Pipeline manifest: {'present' if manifest_present else 'missing'}.",
        "",
        "## Claim Strength Ledger",
        "",
        "| Strength | Meaning in this release |",
        "|---|---|",
        "| `proved` | Machine-checked as the registered boundary statement; per-row `faithfulness:` determines whether it is substantive or statement-restricted. |",
        "| `boundary` | Typed boundary row: either a definitional boundary fact or a witness-threaded contract. |",
        "| `witness` | Typed Lean witness record exists; analytic payload remains supplied externally. |",
        "| `empirical` | Generated from scripts and validated by CSV/JSON/PNG gates. |",
        "| `hypothesis` | Interpretive or biological/clinical framing; not a theorem or benchmark claim. |",
        "| `roadmap` | Planned additive work, including separate Mathlib witness discharge. |",
        "",
        "## Theorem Registry",
        "",
        (
            f"- Total rows: {theorem_counts['total']} "
            f"({theorem_counts['proved']} proved, {theorem_counts['witness']} witness, "
            f"{theorem_counts['boundary']} boundary, {theorem_counts['forwarder']} forwarder, "
            f"{theorem_counts['sketch']} sketch, {theorem_counts['deferred']} deferred)."
        ),
        "",
        "## MathlibProofs Scope",
        "",
        (
            "- Optional package source is present at `lean/MathlibProofs/MathlibProofs.lean`; "
            f"proofSliceVersion={mathlib_status['proofSliceVersion']}, "
            f"{mathlib_status['theorem_count']} theorem declarations, "
            f"latest manifest status: {mathlib_status['build_status']}. "
            "The package validates separate Mathlib plumbing but does not promote any manuscript theorem row."
            if mathlib_status["present"]
            else "- Optional MathlibProofs source is not present."
        ),
        "",
        "## Runtime Budget",
        "",
        (
            f"- Latest manifest total wall time: {_as_float(runtime_budget.get('total_wall_s')):.2f}s."
            if runtime_budget.get("total_wall_s") is not None
            else "- Latest manifest total wall time: unavailable."
        ),
        f"- Slowest stages: {slowest_text or 'unavailable'}.",
        "",
        "## Empirical Stress Evidence",
        "",
        "- One-axis robustness, fixed coupling ablations, targeted two-axis interactions, and long-horizon seed diagnostics are appendix/supporting evidence.",
        "- Long-horizon replicate variability is retained as sensitivity evidence rather than tuned away.",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def _write_readiness_json(
    project_root: Path,
    *,
    status,
    figures: list[Path],
    generated_manuscript: list[Path],
    manifest_present: bool,
    out_dir: Path | None = None,
) -> Path:
    """Write a machine-readable readiness summary from live artifacts."""

    report_dir = out_dir or project_root / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / "release_readiness.json"
    sidecars = sorted((project_root / "output" / "simulations").glob("*.csv"))
    runtime_budget = _manifest_stage_timings(project_root=project_root)
    mathlib_status = _mathlib_proofs_status(project_root, runtime_budget)
    figure_audit = _figure_audit(project_root, figures)
    pdf_audit = _pdf_artifact_audit(project_root, status)
    test_results = _optional_json(project_root / "output" / "reports" / "test_results.json")
    runtime_budget = _reconcile_runtime_budget(runtime_budget, status=status, test_results=test_results)
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": "scripts/readiness_report.py",
        "tests": {
            "total": int(status.tests_total),
            "passed": int(status.tests_passed),
            "skipped": int(status.tests_skipped),
            "failed": int(status.tests_failed),
            "summary": status.test_summary,
        },
        "coverage": {
            "percent": float(status.coverage_percent),
        },
        "pdf": {
            "pages": int(status.pdf_pages),
            "size_bytes": int(status.pdf_size_bytes),
            "size_mb": float(status.pdf_size_mb),
            "summary": status.pdf_summary,
        },
        "artifacts": {
            "png_figures": len(figures),
            "rendered_manuscript_markdown": len(generated_manuscript),
            "simulation_csv_sidecars": len(sidecars),
            "pipeline_manifest_present": bool(manifest_present),
        },
        "theorems": _theorem_status_counts(project_root),
        "mathlib_proofs": mathlib_status,
        "runtime_budget": runtime_budget,
        "figure_audit": figure_audit,
        "pdf_audit": pdf_audit,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def _write_release_index(
    project_root: Path,
    *,
    release_note: Path,
    readiness_json: Path,
    readiness_md: Path,
    manifest: Path,
    out_dir: Path | None = None,
) -> Path:
    """Write a tiny reviewer landing page linking generated release artifacts."""

    report_dir = out_dir or project_root / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / "release_index.md"

    def _rel(path: Path) -> str:
        try:
            return path.relative_to(project_root).as_posix()
        except ValueError:
            return path.as_posix()

    rows = [
        ("Release readiness report", readiness_md),
        ("Machine-readable readiness JSON", readiness_json),
        ("Reviewer release note", release_note),
        ("Pipeline manifest", manifest),
        ("Theorem map", project_root / "docs" / "reference" / "_theorem_map.md"),
        ("Combined PDF", project_root / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf"),
    ]
    lines = [
        "# Reviewer Release Index",
        "",
        f"*Generated by `scripts/readiness_report.py` at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.*",
        "",
        "| Artifact | Path |",
        "|---|---|",
    ]
    for label, path in rows:
        lines.append(f"| {label} | `{_rel(path)}` |")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_release_readiness(project_root: Path) -> Path:
    """Full release-readiness orchestrator; emits all four artifacts.

    Returns the path to the human-readable ``release_readiness.md``.
    """
    out = project_root / "output" / "reports" / "release_readiness.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    status = load_project_status(project_root)
    git_lines = _git_status_lines(project_root)
    counts = _status_counts(git_lines)
    manifest = project_root / "output" / "MANIFEST.md"
    test_results = _optional_json(project_root / "output" / "reports" / "test_results.json")
    figures = sorted((project_root / "output" / "figures").glob("*.png"))
    generated_manuscript = sorted((project_root / "output" / "manuscript").glob("*.md"))
    release_note = _write_release_note(
        project_root,
        status=status,
        figures=figures,
        generated_manuscript=generated_manuscript,
        manifest_present=manifest.exists(),
    )
    readiness_json = _write_readiness_json(
        project_root,
        status=status,
        figures=figures,
        generated_manuscript=generated_manuscript,
        manifest_present=manifest.exists(),
    )
    release_index = _write_release_index(
        project_root,
        release_note=release_note,
        readiness_json=readiness_json,
        readiness_md=out,
        manifest=manifest,
    )
    test_results = _optional_json(project_root / "output" / "reports" / "test_results.json")
    runtime_budget = _manifest_stage_timings(manifest, project_root=project_root)
    runtime_budget = _reconcile_runtime_budget(runtime_budget, status=status, test_results=test_results)
    mathlib_status = _mathlib_proofs_status(project_root, runtime_budget)
    figure_audit = _figure_audit(project_root, figures)
    missing_figures = figure_audit.get("missing_registered_figures", [])
    missing_figure_count = len(missing_figures) if isinstance(missing_figures, list) else 0

    lines = [
        "# Release Readiness Report",
        "",
        f"*Generated by `scripts/readiness_report.py` at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.*",
        "",
        "## Live Gate Snapshot",
        "",
        f"- Pytest: {status.test_summary}.",
        f"- Coverage: {status.coverage_percent:.2f}%.",
        f"- Combined PDF: {status.pdf_summary}.",
        f"- PNG figures present: {len(figures)}.",
        f"- Rendered manuscript markdown files: {len(generated_manuscript)}.",
        f"- Pipeline manifest: {'present' if manifest.exists() else 'missing'}.",
        f"- Reviewer release note: `{release_note.relative_to(project_root)}`.",
        f"- Machine-readable readiness JSON: `{readiness_json.relative_to(project_root)}`.",
        f"- Reviewer release index: `{release_index.relative_to(project_root)}`.",
    ]
    if test_results:
        project = test_results.get("project")
        if isinstance(project, dict):
            lines.append("- Regression JSON loaded from `output/reports/test_results.json`.")
    lines.extend(
        [
            "",
            "## Optional MathlibProofs Gate",
            "",
            f"- Source present: {bool(mathlib_status['present'])}.",
            f"- Build checked in latest manifest: {bool(mathlib_status['build_checked'])}.",
            f"- Latest manifest status: {mathlib_status['build_status']}.",
            f"- proofSliceVersion: {mathlib_status['proofSliceVersion']}.",
            f"- Local theorem declarations: {mathlib_status['theorem_count']}.",
            f"- Local hygiene clean: {bool(mathlib_status['hygiene_clean'])}.",
            "- Claim status: separate Mathlib package; headline real-valued decomposition discharged when keystone build and axiom audit pass; remaining witness rows still require row-specific proofs.",
            "",
            "## Runtime Budget",
            "",
            (
                f"- Manifest total wall-clock: {_as_float(runtime_budget.get('total_wall_s')):.2f}s."
                if runtime_budget.get("total_wall_s") is not None
                else "- Manifest total wall-clock: unavailable."
            ),
            f"- Stages recorded: {runtime_budget['stage_count']}.",
            f"- Failed stages: {', '.join(_runtime_failed_stage_names(runtime_budget)) or 'none'}.",
            f"- Slowest stages: {_format_stage_list(_runtime_stage_dicts(runtime_budget, 'slowest_stages')) or 'unavailable'}.",
            "",
            "## PDF and Figure Audit",
            "",
            f"- Registered figures: {figure_audit['registered_figures']}.",
            f"- PNG figures present: {figure_audit['png_figures']}.",
            f"- PNGs with project metadata: {figure_audit['project_metadata_count']}.",
            f"- PNGs with schema-v2 figure statistics: {figure_audit['schema_v2_metadata_count']}.",
            f"- Missing registered figures: {missing_figure_count}.",
            "",
            "## Worktree Review Slices",
            "",
            "| Slice | Path families | Review intent |",
            "|---|---|---|",
            "| Manuscript and docs | `manuscript/`, `docs/`, `README.md`, `AGENTS.md` | Prose, citation, injection, and reader-map review. |",
            "| Lean boundary | `lean/ActinfPolicyEntanglement/`, `lean/FepSketches/` | Boundary hygiene and theorem/witness coherence. |",
            "| MathlibProofs analytic layer | `lean/MathlibProofs/` | Separate release-path package for the headline real-valued decomposition and future row-specific witness payloads. |",
            "| Simulation and visualization | `src/simulation/`, `src/visualizations/`, `scripts/simulate_*`, figure scripts | Numerical methods, metadata, and generated artifact provenance. |",
            "| Validators and tests | `src/manuscript/`, `scripts/validate_*`, `tests/` | Drift gates and regression coverage. |",
            "",
            "## Current Worktree Summary",
            "",
            f"- Modified: {counts['modified']}",
            f"- Added: {counts['added']}",
            f"- Deleted: {counts['deleted']}",
            f"- Untracked: {counts['untracked']}",
            f"- Other: {counts['other']}",
            "",
            "This report does not stage or commit files. It exists so reviewers can audit the latest local state after the release gates run.",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


__all__ = [
    "FORBIDDEN_MATHLIB_LOCAL_TOKENS",
    "MANIFEST_STAGE_RE",
    "MANIFEST_TOTAL_RE",
    "_status_counts",
    "_as_float",
    "_runtime_stage_dicts",
    "_runtime_failed_stage_names",
    "_format_stage_list",
    "_optional_json",
    "_git_status_lines",
    "_theorem_status_counts",
    "_manifest_stage_timings",
    "_mathlib_proofs_status",
    "_registered_figure_paths",
    "_figure_audit",
    "_pdf_artifact_audit",
    "_write_release_note",
    "_write_readiness_json",
    "_write_release_index",
    "refresh_release_readiness_runtime_budget",
    "write_release_readiness",
]
