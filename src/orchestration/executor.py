"""Pipeline stage execution (serial and parallel batches)."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from orchestration.manifest import StageSummary, write_manifest
from orchestration.stages import (
    FAIL_FAST_VALIDATORS,
    PARALLEL_STAGE_STEMS,
    StageFlags,
    included,
    resolve_stages,
    stage_stem,
)


class StageResult(NamedTuple):
    script: str
    returncode: int
    duration_s: float
    stdout: str
    stderr: str


@dataclass
class ExecutionOutcome:
    failures: list[str]
    stage_summaries: list[StageSummary]
    total_wall_s: float


def spawn(
    script: str,
    *,
    capture: bool,
    scripts_dir: Path,
    project_root: Path,
) -> StageResult:
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


def run_serial(script: str, *, scripts_dir: Path, project_root: Path) -> int:
    print(f"\n>>> {script}")
    result = spawn(script, capture=False, scripts_dir=scripts_dir, project_root=project_root)
    return result.returncode


def run_parallel_batch(
    scripts: list[str],
    *,
    max_workers: int,
    scripts_dir: Path,
    project_root: Path,
) -> list[StageResult]:
    print(f"\n>>> running {len(scripts)} stages concurrently (pool size {max_workers}):")
    for script in scripts:
        print(f"    · {script}")
    results: list[StageResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(
                spawn,
                script,
                capture=True,
                scripts_dir=scripts_dir,
                project_root=project_root,
            ): script
            for script in scripts
        }
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            print(
                f"\n>>> [parallel] {res.script}  "
                f"(returncode={res.returncode}, {res.duration_s:.1f}s)"
            )
            if res.stdout:
                print(res.stdout, end="" if res.stdout.endswith("\n") else "\n")
            if res.stderr:
                print(res.stderr, end="" if res.stderr.endswith("\n") else "\n", file=sys.stderr)
    return results


def _append_summary(
    summaries: list[StageSummary],
    *,
    script: str,
    duration_s: float,
    returncode: int,
) -> None:
    summaries.append({"script": script, "duration_s": duration_s, "returncode": returncode})


def execute_pipeline(
    *,
    flags: StageFlags,
    project_root: Path,
    scripts_dir: Path,
    parallel: bool,
    max_workers: int,
    write_pre_regression_manifest: bool,
    scripts: list[tuple[str, str]] | None = None,
    parallel_stems: frozenset[str] | None = None,
) -> ExecutionOutcome:
    failures: list[str] = []
    stage_summaries: list[StageSummary] = []
    started_total = time.perf_counter()
    pending = resolve_stages(flags, scripts)
    stems = PARALLEL_STAGE_STEMS if parallel_stems is None else parallel_stems
    index = 0

    while index < len(pending):
        script, descr = pending[index]
        stem = stage_stem(script)
        if not included(stem, flags):
            print(f"--- skipping {script} ({descr})")
            index += 1
            continue

        if parallel and stem in stems:
            batch: list[str] = []
            scan = index
            while scan < len(pending):
                candidate = stage_stem(pending[scan][0])
                if candidate not in stems:
                    break
                if not included(candidate, flags):
                    scan += 1
                    continue
                batch.append(pending[scan][0])
                scan += 1
            if batch:
                for res in run_parallel_batch(
                    batch,
                    max_workers=max_workers,
                    scripts_dir=scripts_dir,
                    project_root=project_root,
                ):
                    _append_summary(
                        stage_summaries,
                        script=res.script,
                        duration_s=res.duration_s,
                        returncode=res.returncode,
                    )
                    if res.returncode != 0:
                        print(
                            f"!!! {res.script} exited with code {res.returncode}",
                            file=sys.stderr,
                        )
                        failures.append(res.script)
                index = scan
                continue
            index = scan
            continue

        if (
            write_pre_regression_manifest
            and script == "regression_gate.py"
            and stage_summaries
        ):
            try:
                manifest_path = write_manifest(
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
        returncode = run_serial(script, scripts_dir=scripts_dir, project_root=project_root)
        elapsed = time.perf_counter() - stage_start
        _append_summary(
            stage_summaries,
            script=script,
            duration_s=elapsed,
            returncode=returncode,
        )
        if returncode != 0:
            print(f"!!! {script} exited with code {returncode}", file=sys.stderr)
            failures.append(script)
            if script in FAIL_FAST_VALIDATORS:
                break
        index += 1

    return ExecutionOutcome(
        failures=failures,
        stage_summaries=stage_summaries,
        total_wall_s=time.perf_counter() - started_total,
    )
