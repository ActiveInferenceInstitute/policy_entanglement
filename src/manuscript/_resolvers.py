"""Token-resolution helpers for :mod:`manuscript.renderer`.

Each ``_resolve_<token>`` function takes a regex match plus the
ambient context (the active :class:`RenderResult`, the registry, etc.)
and returns the LaTeX / Markdown substitution string.  Missing labels
mutate ``result`` in place and emit a visible ``[[MISSING:...]]``
marker so the rendered output is still well-formed Markdown.

Splitting the resolvers out of ``renderer.py`` keeps
:func:`renderer.render_section` as a thin orchestrator over the dozen
token regexes; each resolver is independently testable and reusable.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .bibliography import auto_bibliography
from .lean_extract import LeanSnippet, render_lean_snippet

if TYPE_CHECKING:  # pragma: no cover -- typing-only imports
    from .registry import Registry
    from .renderer import RenderResult


# ---------------------------------------------------------------------------
# Format helpers (pure: take a registry record, return a fragment)
# ---------------------------------------------------------------------------


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


UNCERTAINTY_CAPTION_TEXT = {
    "deterministic_grid": "deterministic grid or deterministic construction; no stochastic error bars are implied",
    "canonical_seed": "canonical fixed-seed trajectory; seed sensitivity is reported only where a replicate sidecar is registered",
    "replicate_envelope": "configured replicate-seed sidecar; envelope width reflects seed sensitivity",
    "confidence_interval": "configured replicate sidecar with confidence interval reported from the generated summary",
    "analytical_schematic": "analytical schematic or structural visualization; no stochastic uncertainty interval is implied",
}


def _caption_with_uncertainty(fig) -> str:
    caption = str(fig.caption).strip()
    if "uncertainty semantics:" in caption.lower():
        return caption
    uncertainty = str(getattr(fig, "uncertainty", "")).strip()
    if not uncertainty:
        return caption
    detail = UNCERTAINTY_CAPTION_TEXT.get(uncertainty, uncertainty.replace("_", " "))
    return f"{caption}  Uncertainty semantics: {detail}."


def _figure_block(label: str, fig, manuscript_dir: Path) -> str:
    """Pandoc figure with a ``{#fig:LABEL}`` attribute.

    pandoc-crossref converts this into a numbered ``\\begin{figure}``
    environment with ``\\label{fig:LABEL}`` and an auto-numbered
    "Figure N:" caption prefix. The caption itself stays in Markdown
    so inline code (`` ` ``code`` ` ``), math (``$...$``), and bold
    formatting are converted by Pandoc as in any other prose context
    — emitting the caption inside a raw-LaTeX ``\\caption{}`` would
    leave Markdown idioms uninterpreted and the literal backticks
    would then trigger ``! Missing $ inserted`` in xelatex.
    """
    rel = Path(fig.path)
    rel_to_manuscript = (Path("..") / rel).as_posix()
    # Caption: keep Markdown formatting, but collapse newlines so the
    # whole image directive sits on one line (Pandoc requires that).
    caption = " ".join(_caption_with_uncertainty(fig).split())
    return f"\n![{caption}]({rel_to_manuscript}){{#fig:{label}}}\n"


def _figref(label: str, fig) -> str:
    """Inline clickable cross-reference: ``\\hyperref[fig:LABEL]{Fig.~N}``."""
    return f"`\\hyperref[fig:{label}]{{Fig.~{fig.number}}}`{{=latex}}"


def _equation_block(label: str, eq, *, number: str | None = None) -> str:
    """Pandoc display-math with a ``{#eq:LABEL}`` attribute.

    pandoc-crossref converts ``$$..$$ {#eq:LABEL}`` into a numbered
    ``\\begin{equation}\\label{eq:LABEL}..\\end{equation}`` environment.
    A ``\\tag{...}`` is appended inside the body so the visible
    number matches the registry-assigned ``S.K`` (or the
    registry-defined ``A.K`` for appendices) instead of pandoc-crossref's
    sequential 1, 2, 3 counter.
    """
    body = eq.latex.strip().rstrip("\\").rstrip()
    tag = number if number is not None else str(eq.number)
    return f"\n$$\n{body}\n\\tag{{{tag}}}\n$${{#eq:{label}}}\n"


def _eqref(label: str, eq, *, number: str | None = None) -> str:
    tag = number if number is not None else str(eq.number)
    return f"`\\hyperref[eq:{label}]{{Eq.~({tag})}}`{{=latex}}"


def _secref_inline(label: str, sec) -> str:
    return f"`\\hyperref[sec:{label}]{{§{sec.number}}}`{{=latex}}"


def _sec_full(label: str, sec) -> str:
    title = sec.title.strip()
    return f"`\\hyperref[sec:{label}]{{§{sec.number} {title}}}`{{=latex}}"


def _thmref_inline(label: str, t) -> str:
    return f"`\\hyperref[thm:{label}]{{{t.kind} {t.number}}}`{{=latex}}"


def _thm_block(label: str, t) -> str:
    """Bold theorem-block label preceded by a ``\\phantomsection\\label`` anchor.

    The Markdown ``**Kind N (Name).**`` form is preserved so
    prose-style assertions in tests remain valid; the LaTeX
    ``\\phantomsection\\label{thm:LABEL}`` provides the clickable anchor
    that every ``\\hyperref[thm:LABEL]`` resolves to. ``\\phantomsection``
    is required by hyperref so the label takes effect outside a
    sectioning context.
    """
    block_md = t.render_block()
    return f"`\\phantomsection\\label{{thm:{label}}}`{{=latex}}{block_md}"


def _cite_keys(inner: str) -> list[str]:
    return re.findall(r"@([A-Za-z0-9_-]+)", inner)


# ---------------------------------------------------------------------------
# Token resolvers (mutate ``result`` on missing labels)
# ---------------------------------------------------------------------------


def _resolve_fig(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
    manuscript_dir: Path,
) -> str:
    label = m.group("label")
    fig = registry.labels.figures.get(label)
    if fig is None:
        result.missing_figures.append(label)
        return f"[[MISSING:FIG:{label}]]"
    return _figure_block(label, fig, manuscript_dir)


def _resolve_figref(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
) -> str:
    label = m.group("label")
    fig = registry.labels.figures.get(label)
    if fig is None:
        result.missing_figures.append(label)
        return f"[[MISSING:FIGREF:{label}]]"
    return _figref(label, fig)


def _resolve_eq(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
    equation_label_map: Mapping[str, str] | None,
) -> str:
    label = m.group("label")
    eq = registry.labels.equations.get(label)
    if eq is None:
        result.missing_equations.append(label)
        return f"[[MISSING:EQ:{label}]]"
    number = equation_label_map.get(label) if equation_label_map else None
    return _equation_block(label, eq, number=number)


def _resolve_eqref(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
    equation_label_map: Mapping[str, str] | None,
) -> str:
    label = m.group("label")
    eq = registry.labels.equations.get(label)
    if eq is None:
        result.missing_equations.append(label)
        return f"[[MISSING:EQREF:{label}]]"
    number = equation_label_map.get(label) if equation_label_map else None
    return _eqref(label, eq, number=number)


def _resolve_var(
    m: re.Match[str],
    *,
    result: RenderResult,
    variables: Mapping[str, Any],
) -> str:
    key = m.group("key")
    fmt = m.group("fmt")
    if key not in variables:
        result.missing_variables.append(key)
        return f"[[MISSING:VAR:{key}]]"
    return _format_var(variables[key], fmt)


def _resolve_cite(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
) -> str:
    """Pandoc-style citations: ``[@key]`` and ``[@k1; @k2; @k3]``."""
    keys = _cite_keys(m.group("inner"))
    good: list[str] = []
    for key in keys:
        if key in registry.citations.entries:
            good.append(key)
        else:
            result.missing_citations.append(key)
    if not good and keys:
        # Every key was missing: emit a visible MISSING marker.
        return "[" + " ".join(f"[[MISSING:CITE:{k}]]" for k in keys) + "]"
    # Emit raw LaTeX \citep{...} so natbib formats clickable
    # author-year citations against references.bib.
    return f"`\\citep{{{','.join(good)}}}`{{=latex}}"


def _resolve_citelist(
    m: re.Match[str],
    *,
    registry: Registry,
) -> str:
    topic = m.group("topic")
    return auto_bibliography(registry.citations, topic).rstrip()


def _resolve_sec(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
) -> str:
    label = m.group("label")
    s = registry.labels.sections.get(label)
    if s is None:
        result.missing_sections.append(label)
        return f"[[MISSING:SEC:{label}]]"
    return _sec_full(label, s)


def _resolve_secref(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
) -> str:
    label = m.group("label")
    s = registry.labels.sections.get(label)
    if s is None:
        result.missing_sections.append(label)
        return f"[[MISSING:SECREF:{label}]]"
    return _secref_inline(label, s)


def _resolve_thm(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
) -> str:
    label = m.group("label")
    t = registry.labels.theorems.get(label)
    if t is None:
        result.missing_theorems.append(label)
        return f"[[MISSING:THM:{label}]]"
    return _thm_block(label, t)


def _resolve_thmref(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
) -> str:
    label = m.group("label")
    t = registry.labels.theorems.get(label)
    if t is None:
        result.missing_theorems.append(label)
        return f"[[MISSING:THMREF:{label}]]"
    return _thmref_inline(label, t)


def _resolve_lean(
    m: re.Match[str],
    *,
    result: RenderResult,
    registry: Registry,
    lean_snippets: Mapping[tuple[str, str], LeanSnippet] | None,
) -> str:
    label = m.group("label")
    t = registry.labels.theorems.get(label)
    if t is None:
        result.missing_lean.append(label)
        return f"[[MISSING:LEAN:{label}]]"
    if not t.has_lean_companion:
        result.missing_lean.append(label)
        return f"[[MISSING:LEAN:{label} (no lean_module/lean_name in registry)]]"
    if lean_snippets is None:
        result.missing_lean.append(label)
        return f"[[MISSING:LEAN:{label} (no snippet cache supplied)]]"
    snip = lean_snippets.get((t.lean_module, t.lean_name))
    if snip is None:
        result.missing_lean.append(label)
        return f"[[MISSING:LEAN:{label} ({t.lean_module}.{t.lean_name} not found in source)]]"
    return render_lean_snippet(snip, status=t.status)
