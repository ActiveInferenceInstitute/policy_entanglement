#!/usr/bin/env python3
"""Render every manuscript section into ``output/manuscript/``.

The output directory matches the parent template's rendering pipeline
convention (`infrastructure.rendering.RenderManager` reads from
`output/manuscript/` when present, otherwise falls back to the source
`manuscript/` directory).  Tokens like ``[[FIG:label]]`` /
``[[SECREF:label]]`` / ``[[THMREF:label]]`` / ``[@citekey]`` /
``[[VAR:key]]`` are resolved against the registry under
``manuscript/refs/`` and the variables JSON under
``output/data/``.

Resolves the full token set documented in
[`src/manuscript/tokens.py`](../src/manuscript/tokens.py):
``[[FIG:...]]``, ``[[FIGREF:...]]``, ``[[EQ:...]]``, ``[[EQREF:...]]``,
``[[VAR:key]]``, ``[[VAR:key:fmt]]``, ``[@citekey]``, and
``[[CITELIST:topic]]``.

Sources:
* `manuscript/refs/labels.yaml`        — figure + equation registry
* `manuscript/refs/citations.yaml`     — citation registry
* `output/data/manuscript_variables.json` — numeric values

Failures are reported on stderr and propagate as a non-zero exit code,
so this script can run as a CI gate.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
for _sub in ("", "lean", "simulation", "visualizations", "manuscript"):
    sys.path.insert(0, str(SRC_DIR / _sub if _sub else SRC_DIR))

from registry import load_registry  # noqa: E402
from renderer import render_all  # noqa: E402


def main() -> int:
    manuscript_dir = PROJECT_ROOT / "manuscript"
    refs_dir = manuscript_dir / "refs"
    output_dir = PROJECT_ROOT / "output" / "manuscript"
    variables_path = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"

    registry = load_registry(refs_dir)
    lean_dir = PROJECT_ROOT / "lean" / "ActinfPolicyEntanglement"
    results = render_all(
        manuscript_dir=manuscript_dir,
        output_dir=output_dir,
        registry=registry,
        variables_path=variables_path,
        lean_dir=lean_dir,
    )
    incomplete: list[str] = []
    for name, r in sorted(results.items()):
        if r.is_complete:
            print(f"  ✓ {name}")
        else:
            incomplete.append(name)
            print(f"  ✗ {name}", file=sys.stderr)
            for kind, items in (
                ("figures", r.missing_figures),
                ("equations", r.missing_equations),
                ("citations", r.missing_citations),
                ("variables", r.missing_variables),
            ):
                if items:
                    print(f"      missing {kind}: {sorted(set(items))}", file=sys.stderr)

    output_dir.mkdir(parents=True, exist_ok=True)
    for support in ("config.yaml", "preamble.md"):
        src = manuscript_dir / support
        if src.exists():
            shutil.copy2(src, output_dir / support)
    bib_files = list(manuscript_dir.glob("*.bib"))
    for bib in bib_files:
        shutil.copy2(bib, output_dir / bib.name)

    out_count = len(results)
    print(f"\nWrote {out_count} sections to {output_dir.relative_to(PROJECT_ROOT)}")
    if incomplete:
        print(
            f"FAILED: {len(incomplete)} section(s) had unresolved tokens",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
