"""Resolve every token in a manuscript section.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from registry import CitationRegistry, LabelsRegistry, Registry, load_registry
from tokens import (
    CITATION_RE,
    CITELIST_RE,
    EQ_RE,
    EQREF_RE,
    FIG_RE,
    FIGREF_RE,
    LEAN_RE,
    SEC_RE,
    SECREF_RE,
    THM_RE,
    THMREF_RE,
    VAR_RE,
)
from lean_extract import (
    LeanSnippet,
    load_lean_snippets,
    render_lean_snippet,
)
from bibliography import auto_bibliography


@dataclass
class RenderResult:
    """Outcome of rendering one Markdown body."""
    text: str
    missing_figures: list[str] = field(default_factory=list)
    missing_equations: list[str] = field(default_factory=list)
    missing_citations: list[str] = field(default_factory=list)
    missing_variables: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    missing_theorems: list[str] = field(default_factory=list)
    missing_lean: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not (
            self.missing_figures or self.missing_equations
            or self.missing_citations or self.missing_variables
            or self.missing_sections or self.missing_theorems
            or self.missing_lean
        )


def _format_var(value: Any, fmt: str | None) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
    if isinstance(value, (int, float)):
        if fmt:
            return format(value, fmt)
        # Default: 6-significant-digit float, integer-friendly.
        if isinstance(value, float) and value.is_integer():
            return f"{int(value)}"
        if isinstance(value, float):
            return f"{value:.6g}"
        return str(value)
    return str(value)


def _figure_block(label: str, fig, manuscript_dir: Path) -> str:
    """Markdown image directive with the caption text only.

    Figure numbering / "Figure N:" prefixing is delegated to the
    downstream renderer (pandoc + pandoc-crossref), which auto-numbers
    every embedded image.  Emitting our own "Figure N:" here would
    produce a double-prefix like "Figure 1: Figure 9: …" in the PDF.
    """
    rel = Path(fig.path)
    # Make the path relative to the manuscript directory so the renderer
    # can resolve it from a section file (`../output/figures/...`).
    rel_to_manuscript = Path("..") / rel
    caption = fig.caption.strip().replace("\n", " ")
    return f"![{caption}]({rel_to_manuscript.as_posix()})"


def _figref(fig) -> str:
    return f"Fig. {fig.number}"


def _equation_block(eq) -> str:
    body = eq.latex.strip().rstrip("\\").rstrip()
    return f"$$\n{body}\n\\tag{{{eq.number}}}\n$$"


def _eqref(eq) -> str:
    return f"Eq. ({eq.number})"


def render_section(
    text: str,
    *,
    registry: Registry,
    variables: Mapping[str, Any],
    manuscript_dir: Path,
    lean_snippets: Mapping[tuple[str, str], LeanSnippet] | None = None,
) -> RenderResult:
    """Resolve every token in `text`.

    Unknown labels / keys are recorded in the result and the token is
    replaced with a visible ``[[MISSING:…]]`` marker so the rendered
    output is still well-formed Markdown.
    """
    result = RenderResult(text=text)

    def _fig(m: re.Match[str]) -> str:
        label = m.group("label")
        fig = registry.labels.figures.get(label)
        if fig is None:
            result.missing_figures.append(label)
            return f"[[MISSING:FIG:{label}]]"
        return _figure_block(label, fig, manuscript_dir)

    def _figref_sub(m: re.Match[str]) -> str:
        label = m.group("label")
        fig = registry.labels.figures.get(label)
        if fig is None:
            result.missing_figures.append(label)
            return f"[[MISSING:FIGREF:{label}]]"
        return _figref(fig)

    def _eq(m: re.Match[str]) -> str:
        label = m.group("label")
        eq = registry.labels.equations.get(label)
        if eq is None:
            result.missing_equations.append(label)
            return f"[[MISSING:EQ:{label}]]"
        return _equation_block(eq)

    def _eqref_sub(m: re.Match[str]) -> str:
        label = m.group("label")
        eq = registry.labels.equations.get(label)
        if eq is None:
            result.missing_equations.append(label)
            return f"[[MISSING:EQREF:{label}]]"
        return _eqref(eq)

    def _var(m: re.Match[str]) -> str:
        key = m.group("key")
        fmt = m.group("fmt")
        if key not in variables:
            result.missing_variables.append(key)
            return f"[[MISSING:VAR:{key}]]"
        return _format_var(variables[key], fmt)

    def _cite(m: re.Match[str]) -> str:
        # Pandoc-style citations support both `[@key]` and
        # `[@k1; @k2; @k3]` multi-citations.  Resolve every key inside
        # the bracket body and join the rendered forms with `; `,
        # wrapping in a single pair of parentheses (Pandoc convention).
        keys = re.findall(r"@([A-Za-z0-9_-]+)", m.group("inner"))
        rendered: list[str] = []
        for key in keys:
            c = registry.citations.entries.get(key)
            if c is None:
                result.missing_citations.append(key)
                rendered.append(f"[[MISSING:CITE:{key}]]")
                continue
            # render_inline returns "(Author year)" — strip parens so
            # they aggregate cleanly into a single outer pair below.
            inline = c.render_inline()
            if inline.startswith("(") and inline.endswith(")"):
                inline = inline[1:-1]
            rendered.append(inline)
        return "(" + "; ".join(rendered) + ")"

    def _citelist(m: re.Match[str]) -> str:
        topic = m.group("topic")
        return auto_bibliography(registry.citations, topic).rstrip()

    def _sec(m: re.Match[str]) -> str:
        label = m.group("label")
        s = registry.labels.sections.get(label)
        if s is None:
            result.missing_sections.append(label)
            return f"[[MISSING:SEC:{label}]]"
        return f"§{s.number} {s.title}"

    def _secref(m: re.Match[str]) -> str:
        label = m.group("label")
        s = registry.labels.sections.get(label)
        if s is None:
            result.missing_sections.append(label)
            return f"[[MISSING:SECREF:{label}]]"
        return f"§{s.number}"

    def _thm(m: re.Match[str]) -> str:
        label = m.group("label")
        t = registry.labels.theorems.get(label)
        if t is None:
            result.missing_theorems.append(label)
            return f"[[MISSING:THM:{label}]]"
        return t.render_block()

    def _thmref(m: re.Match[str]) -> str:
        label = m.group("label")
        t = registry.labels.theorems.get(label)
        if t is None:
            result.missing_theorems.append(label)
            return f"[[MISSING:THMREF:{label}]]"
        return t.render_inline()

    def _lean(m: re.Match[str]) -> str:
        label = m.group("label")
        t = registry.labels.theorems.get(label)
        if t is None:
            result.missing_lean.append(label)
            return f"[[MISSING:LEAN:{label}]]"
        if not t.has_lean_companion:
            result.missing_lean.append(label)
            return (
                f"[[MISSING:LEAN:{label} "
                f"(no lean_module/lean_name in registry)]]"
            )
        if lean_snippets is None:
            result.missing_lean.append(label)
            return f"[[MISSING:LEAN:{label} (no snippet cache supplied)]]"
        snip = lean_snippets.get((t.lean_module, t.lean_name))
        if snip is None:
            result.missing_lean.append(label)
            return (
                f"[[MISSING:LEAN:{label} "
                f"({t.lean_module}.{t.lean_name} not found in source)]]"
            )
        return render_lean_snippet(snip, status=t.status)

    text = FIG_RE.sub(_fig, text)
    text = FIGREF_RE.sub(_figref_sub, text)
    text = EQ_RE.sub(_eq, text)
    text = EQREF_RE.sub(_eqref_sub, text)
    text = VAR_RE.sub(_var, text)
    text = CITATION_RE.sub(_cite, text)
    text = CITELIST_RE.sub(_citelist, text)
    text = SEC_RE.sub(_sec, text)
    text = SECREF_RE.sub(_secref, text)
    text = THM_RE.sub(_thm, text)
    text = THMREF_RE.sub(_thmref, text)
    text = LEAN_RE.sub(_lean, text)

    result.text = text
    return result


def render_all(
    *,
    manuscript_dir: Path,
    output_dir: Path,
    registry: Registry,
    variables_path: Path,
    lean_dir: Path | None = None,
) -> dict[str, RenderResult]:
    """Render every ``manuscript/*.md`` section into `output_dir`.

    Subdirectories under `manuscript/` are *not* recursed — the
    rendering pipeline only consumes flat numbered files.  YAML files
    (refs/) are skipped explicitly.

    If `lean_dir` is supplied, every Lean file under it is parsed once
    and the resulting `(module, qualified_name) → snippet` map is
    threaded through every `render_section` call so `[[LEAN:label]]`
    tokens can embed live Lean source.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    variables: dict[str, Any] = {}
    if variables_path.exists():
        variables = json.loads(variables_path.read_text())

    lean_snippets: dict[tuple[str, str], LeanSnippet] | None = None
    if lean_dir is not None and lean_dir.is_dir():
        lean_snippets = load_lean_snippets(lean_dir)

    skip_names = {"README.md", "AGENTS.md", "INDEX.md"}
    out: dict[str, RenderResult] = {}
    for src in sorted(manuscript_dir.glob("*.md")):
        if src.name in skip_names:
            continue
        text = src.read_text()
        result = render_section(
            text,
            registry=registry,
            variables=variables,
            manuscript_dir=manuscript_dir,
            lean_snippets=lean_snippets,
        )
        target = output_dir / src.name
        target.write_text(result.text)
        out[src.name] = result
    return out
