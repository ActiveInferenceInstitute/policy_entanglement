"""Resolve every token in a manuscript section.

Cross-reference tokens (`[[FIGREF:...]]`, `[[EQREF:...]]`,
`[[SECREF:...]]`, `[[THMREF:...]]`, `[[SEC:...]]`) emit raw LaTeX
``\\hyperref[...]{label}`` so the rendered combined PDF gets clickable,
color-coded internal links (the rendering pipeline patches the
hyperref preamble to ``colorlinks=true,linkcolor=red,citecolor=red,
urlcolor=blue,anchorcolor=red``). Citation tokens (``[@key]``,
``[@k1; @k2]``) emit raw LaTeX ``\\citep{...}`` so natbib resolves
them against the auto-generated ``output/manuscript/references.bib``.

Pandoc is invoked with ``markdown+raw_tex``, so the inline LaTeX
fragments pass through verbatim into the combined .tex.

Anchors planted at the targets:
* Equations  → ``\\begin{equation}\\label{eq:<label>}\\tag{S.K} ... \\end{equation}``
* Figures    → ``\\begin{figure}[H]...\\label{fig:<label>}\\end{figure}``
* Theorems   → ``\\hypertarget{thm:<label>}{}**Kind N (Name).**``
  (The Markdown bold prefix is preserved so existing prose-style
  assertions on the rendered text still pass; the hypertarget gives
  ``\\hyperref[thm:...]`` something to resolve to.)
* Sections   → ``{#sec:<label>}`` Pandoc header attribute injected
  onto the file's ``# ...`` and matching ``## ...`` headings; Pandoc
  emits a ``\\label{sec:<label>}`` next to the corresponding
  ``\\section`` / ``\\subsection``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ._resolvers import (
    _format_var,  # noqa: F401  -- re-exported for tests/test_manuscript_renderer.py
    _resolve_cite,
    _resolve_citelist,
    _resolve_eq,
    _resolve_eqref,
    _resolve_fig,
    _resolve_figref,
    _resolve_lean,
    _resolve_sec,
    _resolve_secref,
    _resolve_thm,
    _resolve_thmref,
    _resolve_var,
)
from .equation_numbering import (
    file_to_section_number,
    precompute_equation_numbers,
    retag_display_math,
)
from .lean_extract import (
    LeanSnippet,
    load_lean_snippets,
)
from .registry import Registry, Section
from .renderer_anchors import (
    _dedupe_anchor_labels,
    _ensure_theorem_anchors,
    _plant_theorem_anchors,
)
from .renderer_headings import _inject_section_anchors
from .tokens import (
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
            self.missing_figures
            or self.missing_equations
            or self.missing_citations
            or self.missing_variables
            or self.missing_sections
            or self.missing_theorems
            or self.missing_lean
        )


def render_section(
    text: str,
    *,
    registry: Registry,
    variables: Mapping[str, Any],
    manuscript_dir: Path,
    lean_snippets: Mapping[tuple[str, str], LeanSnippet] | None = None,
    equation_label_map: Mapping[str, str] | None = None,
    section_number: str | None = None,
    file_name: str | None = None,
) -> RenderResult:
    """Resolve every token in `text`.

    Unknown labels / keys are recorded in the result and the token is
    replaced with a visible ``[[MISSING:…]]`` marker so the rendered
    output is still well-formed Markdown.

    Token-level resolution lives in :mod:`manuscript._resolvers`; this
    function is the orchestrator that drives each regex through the
    matching resolver, then runs the post-processing passes (theorem
    anchors, equation auto-numbering, section heading attributes).
    """
    result = RenderResult(text=text)

    text = FIG_RE.sub(
        lambda m: _resolve_fig(m, result=result, registry=registry, manuscript_dir=manuscript_dir),
        text,
    )
    text = FIGREF_RE.sub(
        lambda m: _resolve_figref(m, result=result, registry=registry),
        text,
    )
    text = EQ_RE.sub(
        lambda m: _resolve_eq(m, result=result, registry=registry, equation_label_map=equation_label_map),
        text,
    )
    text = EQREF_RE.sub(
        lambda m: _resolve_eqref(m, result=result, registry=registry, equation_label_map=equation_label_map),
        text,
    )
    text = VAR_RE.sub(
        lambda m: _resolve_var(m, result=result, variables=variables),
        text,
    )
    text = CITATION_RE.sub(
        lambda m: _resolve_cite(m, result=result, registry=registry),
        text,
    )
    text = CITELIST_RE.sub(
        lambda m: _resolve_citelist(m, registry=registry),
        text,
    )
    text = SEC_RE.sub(
        lambda m: _resolve_sec(m, result=result, registry=registry),
        text,
    )
    text = SECREF_RE.sub(
        lambda m: _resolve_secref(m, result=result, registry=registry),
        text,
    )
    text = THM_RE.sub(
        lambda m: _resolve_thm(m, result=result, registry=registry),
        text,
    )
    text = THMREF_RE.sub(
        lambda m: _resolve_thmref(m, result=result, registry=registry),
        text,
    )
    text = LEAN_RE.sub(
        lambda m: _resolve_lean(m, result=result, registry=registry, lean_snippets=lean_snippets),
        text,
    )

    # Plant ``\phantomsection\label{thm:LABEL}`` at every theorem-statement
    # bold label. The canonical statement form in this manuscript is
    # ``**[[THMREF:label]] (Name).**`` (or without the parenthetical),
    # which after substitution is
    # ``**`\hyperref[thm:label]{Kind N}`{=latex} (Name).**``. We strip
    # the self-link (a hyperref pointing at the very text it labels is
    # circular) and replace it with a ``\phantomsection\label`` so every
    # other ``\hyperref[thm:label]`` in the document resolves here.
    text = _plant_theorem_anchors(text)

    # Auto-number every BARE display-math block (`$$..$$`) within the
    # section. Registry-backed equations are emitted as raw-LaTeX
    # ``equation`` envs with their own ``\\label`` and ``\\tag`` and are
    # skipped by the retagger.
    if section_number:
        text = retag_display_math(text, section_number)

    # Inject Pandoc heading attributes for section anchors so each
    # ``# Title`` and matching ``## Subtitle`` becomes a numbered
    # ``\\section{Title}\\label{sec:LABEL}`` in the LaTeX output.
    if file_name:
        text = _inject_section_anchors(text, file_name, registry)

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
    """Render every ``docs/manuscript/*.md`` section into `output_dir`.

    Subdirectories under `docs/manuscript/` are *not* recursed — the
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

    # Pre-pass: walk every section in source order, assign each
    # display equation a number S.K, and build a global label → S.K map
    # for [[EQREF:label]] cross-references that point into other sections.
    equation_label_map = precompute_equation_numbers(
        manuscript_dir=manuscript_dir,
        registry=registry,
    )
    file_to_sec = file_to_section_number(registry)

    from manuscript.meta_files import MANUSCRIPT_NON_BODY_MD

    skip_names = set(MANUSCRIPT_NON_BODY_MD) - {"preamble.md"}
    out: dict[str, RenderResult] = {}
    rendered_texts: dict[str, str] = {}
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
            equation_label_map=equation_label_map,
            section_number=file_to_sec.get(src.name),
            file_name=src.name,
        )
        rendered_texts[src.name] = result.text
        out[src.name] = result

    # Ensure every theorem in the registry has at least one
    # ``\hypertarget{thm:LABEL}`` somewhere in the rendered corpus —
    # otherwise ``\hyperref[thm:LABEL]`` cross-references would point
    # at nothing and emit "undefined reference" warnings during
    # LaTeX. Theorems referenced only inline (e.g. in §1's "six
    # reasons" paragraph) live in a section; we inject the anchor on
    # the line where that section heading appears.
    rendered_texts = _ensure_theorem_anchors(rendered_texts, registry)

    # Also dedupe figure / equation labels: when the same registry
    # token is dropped into multiple sections, only the first
    # occurrence carries the ``\label`` — subsequent occurrences emit
    # the same body without ``\label`` so LaTeX doesn't see a
    # multiply-defined warning.
    rendered_texts = _dedupe_anchor_labels(rendered_texts)

    for fname, body in rendered_texts.items():
        (output_dir / fname).write_text(body)
    return out


__all__ = [
    "RenderResult",
    "render_section",
    "render_all",
    "Section",
]
