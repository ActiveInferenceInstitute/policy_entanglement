"""End-to-end pipeline runner (library implementation).

Business logic for :doc:`scripts/run_all.py </scripts/run_all>`. Runs every
project script in the correct order, then runs the validators as a final gate.

The canonical stage order is the module-level :data:`SCRIPTS` list. Two opt-in
extension lists exist:

* :data:`PDF_SCRIPTS` — inserted just before ``regression_gate.py`` when the
  ``--with-pdf`` flag (or an ``--only build_pdf`` / ``--only validate_pdf``
  request) is passed; runs the project-local PDF build and validation gates.
* :data:`MATHLIB_PROOF_SCRIPTS` — inserted just after ``build_lean.py`` when
  ``--with-mathlib`` is passed; builds the optional additive MathlibProofs
  package without disturbing the Mathlib-free boundary build.

**Round-5 P1-1 parallelism.** The empirical producer batch
(``dump_archetypes`` through ``simulate_adversarial``) is mutually
write-isolated and CPU-bound; it executes in a 6-way
:class:`~concurrent.futures.ThreadPoolExecutor` pool by default. Pass
``--serial`` to fall back to the legacy in-order execution.
Stages 1–2 (build_lean, figures) and the post-empirical tail
(manuscript variables, dashboard, generators, validators, regression gate)
remain sequential because they each depend on prior-stage outputs.

The module also writes ``output/MANIFEST.md`` summarising stage timings and
hashing every generated artifact (round-5 P3-2) unless ``--no-manifest`` is
passed.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import NamedTuple, TypedDict, cast

# Round-5 P3-2: SHA-256 only for files at or below this size; larger
# artifacts (combined PDFs, intermediate TeX builds) get a size-only
# entry to keep the manifest write cheap.
_SHA256_MAX_BYTES = 8 * 1024 * 1024  # 8 MB
_MANIFEST_EXCLUDED_FILENAMES = frozenset({"MANIFEST.md", ".DS_Store"})

# Ordered (name, description) tuples.  The final entry is the regression
# gate so test/coverage/invariant/Lean-budget drift propagates correctly.
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
    ("generate_index.py", "auto-generate manuscript/INDEX.md from registry"),
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

# Backward-compatible union (build/validate before regression; readiness after).
PDF_SCRIPTS: list[tuple[str, str]] = PDF_BUILD_SCRIPTS + PDF_READINESS_SCRIPTS

MATHLIB_PROOF_SCRIPTS: list[tuple[str, str]] = [
    ("build_mathlib_proofs.py", "build optional additive MathlibProofs package"),
]

# Validators that abort the pipeline immediately on non-zero exit (derived
# from the post-empirical tail plus optional PDF/readiness gates).
FAIL_FAST_VALIDATORS: frozenset[str] = frozenset(
    name for name, _ in (
        ("validate_outputs.py", ""),
        ("validate_manuscript.py", ""),
        *PDF_BUILD_SCRIPTS,
        *PDF_READINESS_SCRIPTS,
    )
)

# Names of the stages that are *mutually write-isolated* and may run
# concurrently (round-5 P1-1).  Every other stage runs serially.  Adding
# a stage here without first verifying isolated outputs is dangerous;
# the conservative default for new stages is to keep them serial.
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


class StageResult(NamedTuple):
    """Outcome of running one orchestrator stage.

    Implemented as a :class:`NamedTuple` (not :class:`dataclasses.dataclass`)
    because some import paths used by the test suite — e.g.
    ``importlib.util.spec_from_file_location`` — leave ``cls.__module__``
    unresolved in :data:`sys.modules`, which trips
    :func:`dataclasses._is_type` at class-creation time.  NamedTuple has
    no such dependency.
    """

    script: str
    returncode: int
    duration_s: float
    stdout: str
    stderr: str


class StageSummary(TypedDict):
    script: str
    duration_s: float
    returncode: int


def _spawn(
    script: str,
    *,
    capture: bool,
    scripts_dir: Path,
    project_root: Path,
) -> StageResult:
    """Run a script; capture stdout/stderr iff ``capture`` is True.

    Capturing is required when the orchestrator runs stages in
    parallel (so their output can be interleaved cleanly afterwards);
    serial mode inherits the parent's stdio for live progress.
    """
    cmd = [sys.executable, str(scripts_dir / script)]
    env = {**os.environ, "MPLBACKEND": "Agg"}
    started = time.perf_counter()
    if capture:
        proc = subprocess.run(
            cmd,
            cwd=str(project_root),
            env=env,
            capture_output=True,
            text=True,
        )
        return StageResult(
            script=script,
            returncode=proc.returncode,
            duration_s=time.perf_counter() - started,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
    proc_raw = subprocess.run(cmd, cwd=str(project_root), env=env)
    return StageResult(
        script=script,
        returncode=proc_raw.returncode,
        duration_s=time.perf_counter() - started,
        stdout="",
        stderr="",
    )


def _run_serial(script: str, *, scripts_dir: Path, project_root: Path) -> int:
    """Legacy serial path: inherit stdio, print header, return exit code."""
    print(f"\n>>> {script}")
    result = _spawn(script, capture=False, scripts_dir=scripts_dir, project_root=project_root)
    return result.returncode


def _run_parallel_batch(
    scripts: list[str],
    *,
    max_workers: int,
    scripts_dir: Path,
    project_root: Path,
) -> list[StageResult]:
    """Run a batch of scripts concurrently; emit their stdout/stderr
    serially in completion order so the log remains readable.

    Returns the list of :class:`StageResult` records in completion
    order (not necessarily input order).  The caller decides how to
    treat non-zero return codes.
    """
    print(f"\n>>> running {len(scripts)} stages concurrently (pool size {max_workers}):")
    for s in scripts:
        print(f"    · {s}")
    results: list[StageResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(
                _spawn,
                s,
                capture=True,
                scripts_dir=scripts_dir,
                project_root=project_root,
            ): s
            for s in scripts
        }
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            print(f"\n>>> [parallel] {res.script}  (returncode={res.returncode}, {res.duration_s:.1f}s)")
            if res.stdout:
                print(res.stdout, end="" if res.stdout.endswith("\n") else "\n")
            if res.stderr:
                print(res.stderr, end="" if res.stderr.endswith("\n") else "\n", file=sys.stderr)
    return results


def _write_manifest(*, project_root: Path, run_summary: dict[str, object]) -> Path:
    """Emit ``output/MANIFEST.md`` listing every artifact and stage timing.

    Round-5 P2-2 enhancement: gives auditors a single page that
    inventories the full pipeline state (timing, output paths, sizes).
    """
    output_dir = project_root / "output"
    manifest_path = output_dir / "MANIFEST.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Pipeline output manifest")
    lines.append("")
    lines.append(f"*Auto-generated by `scripts/run_all.py` at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.*")
    lines.append("")
    lines.append("## Stage timings")
    lines.append("")
    lines.append("| Stage | Wall time (s) | Status |")
    lines.append("|---|---:|---|")
    stages = cast(list[StageSummary], run_summary.get("stages", []))
    for stage in stages:
        lines.append(
            f"| `{stage['script']}` | {stage['duration_s']:.2f} | {'OK' if stage['returncode'] == 0 else 'FAIL'} |"
        )
    lines.append("")
    total = float(run_summary.get("total_wall_s", 0.0))  # type: ignore[arg-type]
    lines.append(f"**Total wall-clock**: {total:.2f}s")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(
        "*Round-5 P3-2 addition*: SHA-256 columns enable a "
        "*re-run-and-bit-match* determinism audit.  Files larger than "
        f"{_SHA256_MAX_BYTES // (1024 * 1024)} MB list size only "
        "(checksumming them would dominate the manifest write)."
    )
    lines.append("")
    lines.append("| Path | Size (bytes) | SHA-256 |")
    lines.append("|---|---:|---|")
    for path in sorted(output_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in _MANIFEST_EXCLUDED_FILENAMES:
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        rel = path.relative_to(project_root)
        if size <= _SHA256_MAX_BYTES:
            try:
                hasher = hashlib.sha256()
                with path.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 16), b""):
                        hasher.update(chunk)
                digest = hasher.hexdigest()
            except OSError:
                digest = "(unreadable)"
        else:
            digest = "(skipped: >8 MB)"
        lines.append(f"| `{rel.as_posix()}` | {size} | `{digest}` |")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


def build_parser() -> argparse.ArgumentParser:
    """Build the orchestrator argparse parser (extracted for testing)."""
    parser = argparse.ArgumentParser(description="Run every project script end-to-end.")
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="NAME",
        help="Skip a script by name (basename, no .py); may be repeated.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="NAME",
        help="Run only the named scripts (no .py); may be repeated.",
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        default=False,
        help=(
            "Disable round-5 parallel execution of the empirical producer batch; fall "
            "back to fully sequential mode (legacy behavior)."
        ),
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=6,
        help="Max worker threads for the parallel empirical producer batch (default 6).",
    )
    parser.add_argument(
        "--no-manifest",
        action="store_true",
        default=False,
        help="Skip writing output/MANIFEST.md at end (round-5 P2-2).",
    )
    parser.add_argument(
        "--with-pdf",
        action="store_true",
        default=False,
        help="Run project-local PDF build/validation gates before regression_gate.py.",
    )
    parser.add_argument(
        "--with-mathlib",
        action="store_true",
        default=False,
        help=(
            "Run the optional additive lean/MathlibProofs package build after the "
            "Mathlib-free boundary Lean gate. Default pipeline behavior is unchanged."
        ),
    )
    return parser


def main(
    argv: list[str] | None = None,
    *,
    project_root: Path,
    scripts_dir: Path,
) -> int:
    """Run the full pipeline. Returns 0 on success, 1 on any failure."""
    parser = build_parser()
    args = parser.parse_args(argv)

    skip = set(args.skip)
    only = set(args.only)
    parallel = not args.serial
    max_workers = max(1, int(args.max_workers))

    def _included(stem: str) -> bool:
        if stem in skip:
            return False
        return not (only and stem not in only)

    failures: list[str] = []
    stage_summaries: list[StageSummary] = []
    started_total = time.perf_counter()

    pending = list(SCRIPTS)
    requested_mathlib = args.with_mathlib or bool({"build_mathlib_proofs"} & only)
    if requested_mathlib:
        boundary_idx = next(
            (idx for idx, row in enumerate(pending) if row[0] == "build_lean.py"),
            -1,
        )
        insert_idx = boundary_idx + 1 if boundary_idx >= 0 else 0
        pending[insert_idx:insert_idx] = MATHLIB_PROOF_SCRIPTS
    requested_pdf = args.with_pdf or bool({"build_pdf", "validate_pdf", "readiness_report"} & only)
    if requested_pdf:
        regression_idx = next(
            (idx for idx, row in enumerate(pending) if row[0] == "regression_gate.py"),
            len(pending),
        )
        pending[regression_idx:regression_idx] = PDF_BUILD_SCRIPTS
        after_regression = regression_idx + len(PDF_BUILD_SCRIPTS) + 1
        pending[after_regression:after_regression] = PDF_READINESS_SCRIPTS
    i = 0
    while i < len(pending):
        script, descr = pending[i]
        stem = script[:-3] if script.endswith(".py") else script
        if not _included(stem):
            print(f"--- skipping {script} ({descr})")
            i += 1
            continue

        # Detect a maximal contiguous run of *parallel-eligible* stages
        # starting at ``i``; if found and ``parallel`` is on, batch them.
        if parallel and stem in PARALLEL_STAGE_STEMS:
            batch: list[str] = []
            j = i
            while j < len(pending):
                cand_stem = pending[j][0][:-3] if pending[j][0].endswith(".py") else pending[j][0]
                if cand_stem not in PARALLEL_STAGE_STEMS:
                    break
                if not _included(cand_stem):
                    j += 1
                    continue
                batch.append(pending[j][0])
                j += 1
            if batch:
                results = _run_parallel_batch(
                    batch,
                    max_workers=max_workers,
                    scripts_dir=scripts_dir,
                    project_root=project_root,
                )
                for res in results:
                    stage_summaries.append(
                        {
                            "script": res.script,
                            "duration_s": res.duration_s,
                            "returncode": res.returncode,
                        }
                    )
                    if res.returncode != 0:
                        print(
                            f"!!! {res.script} exited with code {res.returncode}",
                            file=sys.stderr,
                        )
                        failures.append(res.script)
                i = j
                continue
            i = j
            continue

        # Serial path (the Lean/figure prelude, variable/render/validation
        # tail, or any parallel-eligible stage
        # when --serial is set or only one stage is queued).
        if script == "regression_gate.py" and not args.no_manifest and stage_summaries:
            try:
                manifest_path = _write_manifest(
                    project_root=project_root,
                    run_summary={
                        "stages": stage_summaries,
                        "total_wall_s": time.perf_counter() - started_total,
                    },
                )
                print(f"\n>>> wrote pre-regression {manifest_path.relative_to(project_root)}")
            except OSError as exc:
                print(f"!!! could not write pre-regression MANIFEST.md: {exc}", file=sys.stderr)

        stage_start = time.perf_counter()
        rc = _run_serial(script, scripts_dir=scripts_dir, project_root=project_root)
        elapsed = time.perf_counter() - stage_start
        stage_summaries.append(
            {
                "script": script,
                "duration_s": elapsed,
                "returncode": rc,
            }
        )
        if rc != 0:
            print(f"!!! {script} exited with code {rc}", file=sys.stderr)
            failures.append(script)
            # If a validator failed, propagate immediately; for earlier
            # scripts continue so the user sees the full failure surface.
            if script in FAIL_FAST_VALIDATORS:
                break
        i += 1

    total_wall = time.perf_counter() - started_total

    # Round-5 P2-2: write the manifest unless the user opted out (or the
    # build is clearly busted — at least one successful run-step is
    # required for there to be artifacts worth inventorying).
    if not args.no_manifest and stage_summaries:
        try:
            manifest_path = _write_manifest(
                project_root=project_root,
                run_summary={"stages": stage_summaries, "total_wall_s": total_wall},
            )
            print(
                f"\n>>> wrote {manifest_path.relative_to(project_root)} "
                f"({len(stage_summaries)} stages, {total_wall:.1f}s total)"
            )
        except OSError as exc:
            print(f"!!! could not write MANIFEST.md: {exc}", file=sys.stderr)

    if not failures and stage_summaries:
        readiness_ran = any(row.get("script") == "readiness_report.py" for row in stage_summaries)
        if readiness_ran:
            from manuscript.readiness import refresh_release_readiness_runtime_budget  # noqa: WPS433

            try:
                refresh_release_readiness_runtime_budget(project_root)
            except OSError as exc:
                print(
                    f"!!! could not refresh release_readiness.json runtime budget: {exc}",
                    file=sys.stderr,
                )

    print()
    if failures:
        print(
            f"FAILED: {len(failures)} script(s): {', '.join(failures)}",
            file=sys.stderr,
        )
        return 1
    print(f"All scripts succeeded; outputs validated. Total: {total_wall:.1f}s")
    return 0


__all__ = [
    "MATHLIB_PROOF_SCRIPTS",
    "PARALLEL_STAGE_STEMS",
    "PDF_SCRIPTS",
    "SCRIPTS",
    "StageResult",
    "StageSummary",
    "_MANIFEST_EXCLUDED_FILENAMES",
    "_SHA256_MAX_BYTES",
    "_run_parallel_batch",
    "_run_serial",
    "_spawn",
    "_write_manifest",
    "build_parser",
    "main",
]
