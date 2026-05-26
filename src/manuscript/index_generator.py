"""Auto-generated manuscript TOC (library implementation).

Business logic for :doc:`scripts/generate_index.py </scripts/generate_index>`.
Walks the manuscript/ directory, groups files by IMRAD Part (encoded in the
filename prefix `<digit><letter>_`), and emits a TOC table that pairs each
file with its registry title (when registered) or the heading from the file
itself (for Part divider files that intentionally have no registry entry).
"""

from __future__ import annotations

import re
from pathlib import Path

from .meta_files import MANUSCRIPT_NON_BODY_MD
from .registry import load_registry

# Hand-curated subject text shown in the ToC. Titles themselves come from
# the registry; only the description column is editorial.
DESCRIPTIONS: dict[str, str] = {
    "motivation": "Problem statement, six independent reasons, position relative to alternatives",
    "background": "Antecedents in active inference, variational coupling, information geometry, tensor networks",
    "setup": "Single-stream POMDP recap; multi-stream extension; mean-field baseline",
    "notation": "Symbol-by-symbol reference for the body and appendices",
    "lambda_deformation": "Coupling potentials, λ-entangled prior + posterior",
    "decomposition": "Theorem 5.1 (the load-bearing identity), verdicts, MF limit",
    "examples": "K=2 Bernoulli toy, motor + attention example, multi-timescale",
    "geometry": "e/m flatness, m-projection, e-geodesic (Theorem 7.4), Pythagorean (Prop 7.5)",
    "spectral": "Schmidt decomposition, archetypes, tensor-train ranks (Theorem 8.3)",
    "heterogeneous": "Three-level hierarchy, coupling tax (Theorem 9.1), precision-on-coupling",
    "phase": "Disordered / mixed / frozen phases, order parameters, behavioral signatures",
    "comparative": "Coupling-pays-for-itself verdicts under parameter sweeps",
    "connections": "Classical AIF connections — pymdp / SPM, hierarchical / deep AIF, sophisticated inference, branching-time AIF",
    "connections_control_rl": "Control + RL connections — KL / path-integral control, options framework, PoE/MoE, copula VI",
    "connections_multi_agent_geometry": "Multi-agent + geometric connections — interactive inference, RG-AIF, Markov blankets, CEREBRUM",
    "lean_plan": "Boundary-fragment status table, witness payloads, MathlibProofs trajectory",
    "empirical": "Closed-form Bernoulli + heterogeneous tax + phase + spectral + e-geodesic + coupling graph; pymdp content split into §14–§16",
    "pymdp_harness": "pymdp 1.0.1 POMDP harness — layered architecture, λ-sweep, deterministic rollout",
    "pymdp_free_energy": "Free-energy bundle — VFE / EFE / entropy / coupling-term / TC observables + 5 dashboards",
    "pymdp_validation": "Three-tier validation gate + JSONL run log + reproducibility contract",
    "open_questions": "Q1–Q15: analytical, identifiability, empirical, conceptual, practical",
    "discussion": "Worldview, live artifact state, alignment implications, limitations, open directions",
    "bibliography": "Auto-generated from [`refs/citations.yaml`](refs/citations.yaml)",
    "app.proof_decomp": "Full proof of Theorem 5.1 (entanglement decomposition)",
    "app.convexity": "Convexity of $F[q_\\lambda]$ in $\\lambda$",
    "app.bernoulli": "K=2 Bernoulli toy — complete derivation",
    "app.tt_inference": "Tensor-train inference algorithm sketch",
    "app.lean_skeleton": "Lean code skeleton (registry-backed submodule count; witness contracts)",
    "app.reference_tables": "Lean module inventory, pymdp bundle stats, JSONL run-log schema",
}


_FIRST_HEADING_RE = re.compile(r"^#\s+(.+?)(?:\s*\{[-\s#a-z0-9_:.]*\})?\s*$", re.MULTILINE)


def _file_title(file_path: Path) -> str:
    """Extract the first level-1 heading text from a markdown file."""
    text = file_path.read_text(encoding="utf-8")
    m = _FIRST_HEADING_RE.search(text)
    return m.group(1).strip() if m else file_path.stem


def build_index_text(*, manuscript_dir: Path) -> str:
    """Build the full text of ``manuscript/INDEX.md``.

    Args:
        manuscript_dir: Path to the manuscript directory containing the
            section files and the ``refs/`` registry directory.

    Returns:
        The full INDEX.md body as a string (newline-terminated).
    """
    refs = manuscript_dir / "refs"
    reg = load_registry(refs)
    sections = reg.labels.sections

    file_to_section = {s.file: s for s in sections.values() if s.file and not s.parent}

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
        "The manuscript is organized into six parts (Introduction, Theory, "
        "Formal Verification, Empirical Grounding, Connections, and "
        "Discussion).  Each body file uses a `<digit><letter>_*` prefix "
        "(e.g. `2D_decomposition.md`) so the renderer's lexical-sort "
        "discovery places it correctly within its part; supplementary "
        "appendices use an `S0N_*` prefix."
    )
    body.append("")
    body.append("| File | Title | Subject |")
    body.append("|---|---|---|")
    body.append("| [`preamble.md`](preamble.md) | Preamble | LaTeX preamble + author front-matter |")

    body_files = sorted(
        p
        for p in manuscript_dir.glob("*.md")
        if p.name not in MANUSCRIPT_NON_BODY_MD and (p.name[0].isdigit() and not p.name.startswith("99_"))
    )
    for p in body_files:
        if p.name in file_to_section:
            sec = file_to_section[p.name]
            desc = DESCRIPTIONS.get(sec.label, "")
            body.append(f"| [`{p.name}`]({p.name}) | §{sec.number} {sec.title} | {desc} |")
        else:
            title = _file_title(p)
            body.append(f"| [`{p.name}`]({p.name}) | {title} | _(part divider — unnumbered)_ |")

    bib = manuscript_dir / "99_bibliography.md"
    if bib.exists():
        body.append(
            f"| [`{bib.name}`]({bib.name}) | Bibliography | "
            "Auto-generated from [`refs/citations.yaml`](refs/citations.yaml) |"
        )

    supp_files = sorted(manuscript_dir.glob("S0*.md"))
    if supp_files:
        body.append("")
        body.append("## Supplementary appendices")
        body.append("")
        body.append("| File | Title | Subject |")
        body.append("|---|---|---|")
        for p in supp_files:
            if p.name in file_to_section:
                sec = file_to_section[p.name]
                desc = DESCRIPTIONS.get(sec.label, "")
                body.append(f"| [`{p.name}`]({p.name}) | §{sec.number} {sec.title} | {desc} |")
            else:
                title = _file_title(p)
                body.append(f"| [`{p.name}`]({p.name}) | {title} | |")

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
    body.append("| [`refs/README.md`](refs/README.md) | How the registry feeds the auto-injection pipeline |")
    body.append("")
    body.append("## Render the manuscript")
    body.append("")
    body.append("```bash")
    body.append("uv run python scripts/manuscript_variables.py        # JSON of every numeric value")
    body.append("uv run python scripts/inject_manuscript_variables.py # resolves all tokens, auto-numbers eqs")
    body.append("uv run python scripts/validate_manuscript.py         # gates: tokens, citations, ranges")
    body.append("uv run python scripts/generate_index.py              # refresh this file")
    body.append("```")
    body.append("")
    body.append("## Authoring rules — required reading")
    body.append("")
    body.append(
        "The manuscript ↔ code contract is documented in "
        "[`../docs/guides/styleguide.md`](../docs/guides/styleguide.md):"
    )
    body.append("")
    body.append("* every numeric value reaches the prose via `[[VAR:key]]` (no hardcoded numbers);")
    body.append(
        "* every figure is registered in "
        "[`refs/labels.yaml`](refs/labels.yaml) with a caption that "
        "names the generation method + grid hyperparameter;"
    )
    body.append(
        "* every display equation is auto-numbered as `S.K`; cross-refs use `[[EQ:label]]` / `[[EQREF:label]]`;"
    )
    body.append("* every `[@citekey]` resolves through [`refs/citations.yaml`](refs/citations.yaml);")
    body.append(
        "* simulation hyperparameters live in "
        "[`../src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py) "
        "— never as a literal in a script or in prose."
    )
    body.append("")

    return "\n".join(body)


def write_index(*, manuscript_dir: Path) -> Path:
    """Write ``manuscript/INDEX.md`` and return its path."""
    text = build_index_text(manuscript_dir=manuscript_dir)
    out_path = manuscript_dir / "INDEX.md"
    out_path.write_text(text)
    return out_path


__all__ = [
    "DESCRIPTIONS",
    "build_index_text",
    "write_index",
]
