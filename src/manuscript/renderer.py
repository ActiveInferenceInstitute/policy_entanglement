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
import re
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


# Matches the bold theorem-statement label form left behind by THMREF
# substitution, e.g.:
#   **`\hyperref[thm:thm_4_1]{Theorem 5.1}`{=latex} (Entanglement Decomp).**
#   **`\hyperref[thm:cor_4_3]{Corollary 5.3}`{=latex}.**
# The closing ``**`` may be on a later line if the label spans more
# than one line, so the trailing prose is matched non-greedily.
_THM_STATEMENT_RE = re.compile(
    r"\*\*`\\hyperref\[thm:(?P<label>[A-Za-z0-9_]+)\]\{(?P<text>[^}]+)\}`\{=latex\}"
    r"(?P<rest>[^*\n]*)\*\*",
)


def _plant_theorem_anchors(text: str) -> str:
    """Convert the first bold-style THMREF occurrence per label into a
    ``\\phantomsection\\label{thm:LABEL}`` anchor + plain bold label.

    Subsequent occurrences (e.g. references to the same theorem in
    later prose) stay as clickable ``\\hyperref`` links.
    """
    seen: set[str] = set()

    def _sub(m: re.Match[str]) -> str:
        label = m.group("label")
        kind_n = m.group("text")
        rest = m.group("rest")
        if label in seen:
            # Leave the hyperref intact: this is not the canonical
            # statement label, just another reference rendered in bold.
            return m.group(0)
        seen.add(label)
        return f"`\\phantomsection\\label{{thm:{label}}}`{{=latex}}**{kind_n}{rest}**"

    return _THM_STATEMENT_RE.sub(_sub, text)


def _inject_section_anchors(text: str, file_name: str, registry: Registry) -> str:
    """Append ``{#sec:LABEL}`` to ``# ...`` and ``## ...`` headings.

    Top-level ``# ...`` headings are matched to the registry section
    whose ``file == file_name`` and ``parent == ""``.

    ``## ...`` subsection headings are paired by *order*: the first
    ``##`` in source order maps to the first registry subsection whose
    ``parent == top_level_label`` (sorted by registry number), the
    second to the second, etc. This is robust to lightly-edited
    titles (e.g. heading reads "## The K=2 Bernoulli toy: full closed
    form" vs registry title "K=2 Bernoulli toy: full closed form")
    because the registry order is the single source of truth.

    ``### …`` and deeper headings are not anchored automatically.
    Headings that already carry a ``{#…}`` attribute are left alone;
    a ``{-}`` marker (Pandoc's ``unnumbered`` flag, used on
    ``# Abstract`` / ``# Bibliography``) is preserved alongside the
    new anchor.
    """

    secs = registry.labels.sections
    # Find the top-level entry for this file.
    top_label: str | None = None
    for sec_label, sec in secs.items():
        if sec.file == file_name and not sec.parent:
            top_label = sec_label
            break

    # Subsections of top_label, in registry-defined order.
    sub_labels: list[str] = []
    if top_label is not None:

        def _key(item: tuple[str, Section]) -> tuple[int, ...]:
            num = item[1].number or ""
            parts: list[int] = []
            for p in num.split("."):
                try:
                    parts.append(int(p))
                except ValueError:
                    parts.append(0)
            return tuple(parts)

        sub_labels = [label for label, sec in sorted(secs.items(), key=_key) if sec.parent == top_label]

    out_lines: list[str] = []
    sub_idx = 0
    in_fence = False
    fence_marker: str | None = None
    for line in text.splitlines():
        # Track fenced code blocks (``` or ~~~) so their lines, which often
        # start with a ``#`` shell comment, are not mistaken for headings.
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif fence_marker == marker:
                in_fence = False
                fence_marker = None
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        m = re.match(r"^(?P<hashes>#{1,2})\s+(?P<title>.+?)\s*$", line)
        if not m:
            out_lines.append(line)
            continue
        title = m.group("title")
        attr_m = re.search(r"\{(?P<attrs>[^}]*)\}\s*$", title)
        if attr_m and "#" in attr_m.group("attrs"):
            existing_ids = re.findall(r"#([A-Za-z0-9_.:-]+)", attr_m.group("attrs"))
            if m.group("hashes") == "##":
                for existing_id in existing_ids:
                    if not existing_id.startswith("sec:"):
                        continue
                    label = existing_id.removeprefix("sec:")
                    if label in sub_labels[sub_idx:]:
                        sub_idx = sub_labels.index(label) + 1
                        break
            out_lines.append(line)
            continue
        title_clean = re.sub(r"\s*\{[^}]*\}\s*$", "", title).strip()
        existing_attrs = attr_m.group("attrs").strip() if attr_m else ""

        heading_label: str | None = None
        if m.group("hashes") == "#" and top_label is not None:
            heading_label = top_label
        elif m.group("hashes") == "##" and sub_idx < len(sub_labels):
            heading_label = sub_labels[sub_idx]
            sub_idx += 1

        if heading_label is None:
            out_lines.append(line)
            continue

        attrs = f"#sec:{heading_label}"
        if existing_attrs == "-":
            attrs += " .unnumbered"
        elif existing_attrs:
            attrs += " " + existing_attrs
        new_title = f"{title_clean} {{{attrs}}}"
        out_lines.append(f"{m.group('hashes')} {new_title}")
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")


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


# Re-export Section for tooling that imports it from this module.
_HYPERTARGET_RE = re.compile(r"\\(?:hypertarget|label)\{thm:(?P<label>[A-Za-z0-9_]+)\}")


def _section_to_file(registry: Registry) -> dict[str, str]:
    """Return ``{section_label: file_name}`` resolving subsection
    parents transitively (e.g. ``decomposition.reading`` →
    ``2D_decomposition.md`` via parent
    ``decomposition``).
    """
    out: dict[str, str] = {}
    secs = registry.labels.sections
    for label, sec in secs.items():
        if sec.file:
            out[label] = sec.file
            continue
        # Walk up parent chain.
        cur = sec
        while cur.parent:
            parent = secs.get(cur.parent)
            if parent is None:
                break
            if parent.file:
                out[label] = parent.file
                break
            cur = parent
    return out


def _ensure_theorem_anchors(rendered_texts: dict[str, str], registry: Registry) -> dict[str, str]:
    """For every registered theorem with no ``\\label{thm:LABEL}`` planted
    by ``_plant_theorem_anchors``, inject one near the start of the
    section that owns it.

    This catches corollaries / propositions that are only referenced
    inline (no ``**[[THMREF:label]] (Name).**`` statement form) and
    would otherwise cause "Hyper reference undefined" warnings.
    """
    seen: set[str] = set()
    for body in rendered_texts.values():
        for m in _HYPERTARGET_RE.finditer(body):
            seen.add(m.group("label"))

    sec_to_file = _section_to_file(registry)
    pending: dict[str, list[str]] = {}
    for label, t in registry.labels.theorems.items():
        if label in seen:
            continue
        target_file = sec_to_file.get(t.section)
        if not target_file or target_file not in rendered_texts:
            continue
        pending.setdefault(target_file, []).append(label)

    if not pending:
        return rendered_texts

    out: dict[str, str] = {}
    for fname, body in rendered_texts.items():
        labels = pending.get(fname)
        if not labels:
            out[fname] = body
            continue
        anchors = "".join(f"`\\phantomsection\\label{{thm:{lbl}}}`{{=latex}}\n" for lbl in labels)
        # Inject after the first level-1 heading line so the anchors
        # land inside the correct section in the LaTeX output. If no
        # heading is found, prepend at the top.
        lines = body.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.startswith("# "):
                lines.insert(i + 1, "\n" + anchors + "\n")
                break
        else:
            lines.insert(0, anchors)
        out[fname] = "".join(lines)
    return out


_REG_FIG_ATTR_RE = re.compile(r"\{#fig:(?P<label>[A-Za-z0-9_]+)\}")
_REG_EQ_ATTR_RE = re.compile(r"\{#eq:(?P<label>[A-Za-z0-9_]+)\}")
_REG_THM_ANCHOR_RE = re.compile(r"`\\phantomsection\\label\{thm:(?P<label>[A-Za-z0-9_]+)\}`\{=latex\}")


def _dedupe_anchor_labels(rendered_texts: dict[str, str]) -> dict[str, str]:
    """Strip duplicate ``{#fig:..}`` / ``{#eq:..}`` Pandoc-crossref
    attributes and duplicate ``\\phantomsection\\label{thm:..}`` markers
    across the corpus.

    Only the *first* occurrence (across files in sorted order) keeps
    its anchor; later occurrences of the same registry token emit the
    same surrounding text without an anchor so LaTeX's
    ``multiply-defined labels`` warning stays silent. The first
    occurrence remains the canonical hyperref target.
    """
    seen_fig: set[str] = set()
    seen_eq: set[str] = set()
    seen_thm: set[str] = set()
    out: dict[str, str] = {}
    for fname in sorted(rendered_texts):
        body = rendered_texts[fname]

        def _strip_fig(m: re.Match[str]) -> str:
            lbl = m.group("label")
            if lbl in seen_fig:
                return ""
            seen_fig.add(lbl)
            return m.group(0)

        def _strip_eq(m: re.Match[str]) -> str:
            lbl = m.group("label")
            if lbl in seen_eq:
                return ""
            seen_eq.add(lbl)
            return m.group(0)

        def _strip_thm(m: re.Match[str]) -> str:
            lbl = m.group("label")
            if lbl in seen_thm:
                return ""
            seen_thm.add(lbl)
            return m.group(0)

        body = _REG_FIG_ATTR_RE.sub(_strip_fig, body)
        body = _REG_EQ_ATTR_RE.sub(_strip_eq, body)
        body = _REG_THM_ANCHOR_RE.sub(_strip_thm, body)
        out[fname] = body
    return out


__all__ = [
    "RenderResult",
    "render_section",
    "render_all",
    "Section",
]
