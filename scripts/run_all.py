#!/usr/bin/env python3
"""End-to-end orchestrator that runs every script in this directory in
the correct order, then runs the validator as a final gate.

Order:
  1. generate_figures.py       — render every PNG figure
  2. manuscript_variables.py   — emit JSON with in-text variable substitutions
  3. dump_archetypes.py        — emit Schmidt archetype CSV
  4. parameter_sweep.py        — emit fine-grained parameter sweep CSV
  5. validate_outputs.py       — check every artefact, exit non-zero on any failure

Usage::

    uv run python scripts/run_all.py
    # or for a specific script subset:
    uv run python scripts/run_all.py --skip parameter_sweep
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent

# Ordered (name, description) tuples.  The final entry must be the
# validator so that a non-zero exit propagates correctly.
SCRIPTS: list[tuple[str, str]] = [
    ("generate_figures.py",            "render every manuscript figure"),
    ("manuscript_variables.py",        "compute in-text variable substitutions"),
    ("dump_archetypes.py",             "dump K=2 Schmidt archetypes"),
    ("parameter_sweep.py",             "fine-grained parameter sweep"),
    ("simulate_pymdp.py",              "pymdp 1.0.1 POMDP simulation harness"),
    ("generate_index.py",              "auto-generate manuscript/INDEX.md from registry"),
    ("inject_manuscript_variables.py", "render manuscript with auto-injected tokens"),
    ("validate_outputs.py",            "validate every artefact"),
    ("validate_manuscript.py",         "validate manuscript completeness (tokens + links)"),
]


def _run(script: str) -> int:
    """Run a script and return its exit code."""
    print(f"\n>>> {script}")
    result = subprocess.run(
        [sys.executable, str(THIS_DIR / script)],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run every project script end-to-end.",
    )
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
    args = parser.parse_args(argv)

    skip = set(args.skip)
    only = set(args.only)

    failures: list[str] = []
    for script, descr in SCRIPTS:
        stem = script[:-3] if script.endswith(".py") else script
        if stem in skip:
            print(f"--- skipping {script} ({descr})")
            continue
        if only and stem not in only:
            print(f"--- skipping {script} (not in --only)")
            continue
        rc = _run(script)
        if rc != 0:
            print(f"!!! {script} exited with code {rc}", file=sys.stderr)
            failures.append(script)
            # If the validator failed, propagate immediately; for earlier
            # scripts, continue so the user sees the full failure surface.
            if script == "validate_outputs.py":
                break

    print()
    if failures:
        print(f"FAILED: {len(failures)} script(s): {', '.join(failures)}", file=sys.stderr)
        return 1
    print("All scripts succeeded; outputs validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
