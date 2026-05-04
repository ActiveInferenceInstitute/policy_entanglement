#!/usr/bin/env python3
"""Auto-generate `manuscript/INDEX.md` from the section registry.

Replaces every hand-maintained section number with the registry's
canonical value, so that adding or renumbering a section requires only
a `manuscript/refs/labels.yaml` edit.
"""
from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
for _sub in ("", "lean", "simulation", "visualizations", "manuscript"):
    sys.path.insert(0, str(SRC_DIR / _sub if _sub else SRC_DIR))

from registry import load_registry  # noqa: E402

# Per-section descriptions: hand-curated subject text shown in the ToC.
# (The titles themselves come from the registry; only the description
# column is editorial.)
DESCRIPTIONS: dict[str, str] = {
    "motivation": "Problem statement, six independent reasons, position relative to alternatives",
    "setup": "Single-stream POMDP recap; multi-stream extension; mean-field baseline",
    "notation": "Symbol-by-symbol reference for the body and appendices",
    "lambda_deformation": "Coupling potentials, λ-entangled prior + posterior",
    "decomposition": "Theorem 4.1 (the load-bearing identity), verdicts, MF limit",
    "examples": "K=2 Bernoulli toy, motor + attention example, multi-timescale",
    "geometry": "e/m flatness, m-projection, e-geodesic (Theorem 6.4), Pythagorean (Prop 6.5)",
    "spectral": "Schmidt decomposition, archetypes, tensor-train ranks (Theorem 7.3)",
    "heterogeneous": "Three-level hierarchy, coupling tax (Theorem 8.1), precision-on-coupling",
    "phase": "Disordered / mixed / frozen phases, order parameters, clinical phenomenology",
    "comparative": "Coupling-pays-for-itself verdicts under parameter sweeps",
    "connections": "pymdp, hierarchical AIF, BTAI, KL control, options, PoE/MoE, copula VI, RG-AIF, CEREBRUM",
    "lean_plan": "Phase 0 status table (16/16 jobs), Phase 1–7 roadmap",
    "empirical": "Closed-form numerics + pymdp 1.0.1 grounded harness, every figure",
    "open_questions": "Q1–Q12",
    "companion_paper": "Future work tracked in a separate manuscript",
    "discussion": "Implications",
    "closing": "Take-aways",
    "bibliography": "Auto-generated from [`refs/citations.yaml`](refs/citations.yaml)",
    "app.proof_decomp": "Full proof of Theorem 4.1",
    "app.convexity": "Convexity of $F[q_\\lambda]$",
    "app.bernoulli": "K=2 Bernoulli derivation",
    "app.tt_inference": "Tensor-train inference algorithm",
    "app.lean_skeleton": "Lean code skeleton",
}


def _row(section, description: str, file_link: str) -> str:
    title = section.title
    return f"| [`{file_link}`]({file_link}) | §{section.number} {title} | {description} |"


def main() -> int:
    refs = PROJECT_ROOT / "manuscript" / "refs"
    out_path = PROJECT_ROOT / "manuscript" / "INDEX.md"
    reg = load_registry(refs)
    sections = reg.labels.sections

    # Header.
    body: list[str] = []
    body.append("# Manuscript Table of Contents")
    body.append("")
    body.append(
        "Authoritative section ordering, **auto-generated** from "
        "[`refs/labels.yaml`](refs/labels.yaml) by "
        "[`../scripts/generate_index.py`](../scripts/generate_index.py).  "
        "Do not hand-edit — modify the registry instead."
    )
    body.append("")
    body.append(
        "The *physical* layout is intentionally flat: the parent template "
        "rendering pipeline concatenates files in alphanumeric order, so "
        "every body section uses a `00_…`–`17_…` prefix and every "
        "supplementary appendix uses an `S0N_…` prefix."
    )
    body.append("")
    body.append("| File | Title | Subject |")
    body.append("|---|---|---|")

    # Static rows that have no registry section (front-matter).
    body.append(
        "| [`preamble.md`](preamble.md) | Preamble | LaTeX preamble + author front-matter |"
    )
    body.append(
        "| [`00_abstract.md`](00_abstract.md) | Abstract | One-page summary |"
    )

    # Sort top-level sections by their `file:` field (numerical prefix).
    top_levels = [s for s in sections.values() if s.file and not s.parent]
    top_levels.sort(key=lambda s: s.file)
    for s in top_levels:
        desc = DESCRIPTIONS.get(s.label, "")
        body.append(_row(s, desc, s.file))

    # Footer pointing at the registry directory.
    body.append("")
    body.append("## Registry directory ([`refs/`](refs/))")
    body.append("")
    body.append("| File | Purpose |")
    body.append("|---|---|")
    body.append(
        "| [`refs/labels.yaml`](refs/labels.yaml) | "
        "Single source of truth for every figure, equation, **section**, "
        "and **theorem** referenced via `[[FIG:...]]` / `[[EQ:...]]` / "
        "`[[SEC:...]]` / `[[THM:...]]` tokens |"
    )
    body.append(
        "| [`refs/citations.yaml`](refs/citations.yaml) | "
        "Single source of truth for every Pandoc-style citation token |"
    )
    body.append(
        "| [`refs/README.md`](refs/README.md) | "
        "How the registry feeds the auto-injection pipeline |"
    )
    body.append("")
    body.append("## Render the manuscript")
    body.append("")
    body.append("```bash")
    body.append("uv run python scripts/manuscript_variables.py")
    body.append("uv run python scripts/inject_manuscript_variables.py")
    body.append("uv run python scripts/validate_manuscript.py")
    body.append("uv run python scripts/generate_index.py     # refresh this file")
    body.append("```")
    body.append("")

    out_path.write_text("\n".join(body))
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
