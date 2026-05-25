"""Auto-number every display equation in the manuscript.

Within each section, both ``[[EQ:label]]`` registry tokens and bare
``$$ ... $$`` display blocks are walked in source order and assigned a
sequential number ``S.K`` where:

* ``S`` is the section's registry number (``"5"``, ``"6"``,
  ``"A"``, …); top-level files like ``1B_motivation.md``
  inherit ``S = "1"`` via :func:`file_to_section_number`.
* ``K`` is the within-section position of the equation.

The output of :func:`precompute_equation_numbers` is a *global* map
from registered-equation label → assigned ``"S.K"``; it is the
single source of truth that powers both ``\\tag{S.K}`` injection in
the rendered Markdown and ``[[EQREF:label]]`` cross-references.
"""

from __future__ import annotations

import re
from pathlib import Path

from .meta_files import MANUSCRIPT_NON_BODY_MD
from .registry import Registry

# A non-greedy display-math match — anchored on `$$` pairs.
# We also recognize the LaTeX-style `\[ ... \]` and the `equation*`
# environment so a prose author who reaches for those alternatives
# still gets auto-numbering.  All three forms are normalized to
# `$$ ... $$` shape at rewrite time.
DISPLAY_MATH_RE = re.compile(
    r"(?:\$\$(?P<body>.+?)\$\$)"
    r"|(?:\\\[(?P<bracket>.+?)\\\])"
    r"|(?:\\begin\{equation\*?\}(?P<env>.+?)\\end\{equation\*?\})",
    re.DOTALL,
)
EQ_TOKEN_RE = re.compile(r"\[\[EQ:(?P<label>[A-Za-z0-9_]+)\]\]")
TAG_RE = re.compile(r"\\tag\s*\{[^}]*\}")


def file_to_section_number(registry: Registry) -> dict[str, str]:
    """Return ``{file_name: registry_section_number}`` from
    ``manuscript/refs/labels.yaml``.

    Only sections with a non-empty ``file`` field are recorded; sub-
    sections inherit numbering through their parent's file.
    """
    out: dict[str, str] = {}
    for s in registry.labels.sections.values():
        if s.file:
            out[s.file] = s.number
    return out


def _equation_events(text: str) -> list[tuple[int, str, str | None]]:
    """Yield ``(position, kind, label)`` triples in source order.

    ``kind`` is one of ``"eq"`` (a ``[[EQ:label]]`` token) or
    ``"math"`` (a bare ``$$..$$`` block).  ``label`` is set only for
    ``eq`` events.  Bare math blocks that occur *inside* a token's
    expansion are not double-counted because we read the *raw* text
    before any substitution.
    """
    events: list[tuple[int, str, str | None]] = []
    for m in EQ_TOKEN_RE.finditer(text):
        events.append((m.start(), "eq", m.group("label")))
    for m in DISPLAY_MATH_RE.finditer(text):
        events.append((m.start(), "math", None))
    events.sort()
    return events


def precompute_equation_numbers(
    *,
    manuscript_dir: Path,
    registry: Registry,
) -> dict[str, str]:
    """Walk every section in ``manuscript_dir`` and return a map
    ``{registered_equation_label: "S.K"}``.

    Sections are processed in filename-sorted order so the numbering
    is stable across runs and matches the order the renderer emits.
    First-occurrence wins: a label is assigned its canonical number
    from the first section that introduces it; later appearances in
    other sections (proofs, appendices) do not overwrite that number,
    so cross-references always point back to the defining section.
    """
    file_to_sec = file_to_section_number(registry)
    label_to_number: dict[str, str] = {}
    for src in sorted(manuscript_dir.glob("*.md")):
        if src.name in MANUSCRIPT_NON_BODY_MD:
            continue
        section_num = file_to_sec.get(src.name)
        if section_num is None:
            # Unregistered file (e.g., preamble.md) — skip numbering.
            continue
        text = src.read_text()
        k = 0
        for _pos, kind, label in _equation_events(text):
            k += 1
            if kind == "eq" and label and label not in label_to_number:
                label_to_number[label] = f"{section_num}.{k}"
    return label_to_number


def section_equation_count(text: str) -> int:
    """Number of display-math + ``[[EQ:label]]`` events in `text`.

    Used by tests to assert auto-numbering is exhaustive.
    """
    return len(_equation_events(text))


def assign_within_section_numbers(text: str) -> list[tuple[int, int, str, str | None]]:
    """Return ``[(within_section_index, position, kind, label?), …]``.

    Useful for tests that want to assert the K assignment directly.
    """
    out = []
    for k, (pos, kind, label) in enumerate(_equation_events(text), start=1):
        out.append((k, pos, kind, label))
    return out


def retag_display_math(text: str, section_number: str) -> str:
    """Inject / overwrite ``\\tag{S.K}`` on every ``$$..$$`` block in
    `text`, where K is the 1-indexed source-order count of display
    blocks within the text.

    Existing ``\\tag{…}`` payloads on bare blocks are *replaced* — the
    registry's ``_equation_block`` emits a placeholder tag that the
    position-based auto-numbering then overwrites.

    Registered-equation blocks emitted by ``_equation_block`` carry a
    Pandoc-crossref attribute ``{#eq:LABEL}`` immediately after the
    closing ``$$``. Those blocks are *not* rewritten — they already
    carry the correct ``\\tag`` from
    :func:`precompute_equation_numbers`, and rewriting would strip
    the ``{#eq:LABEL}`` attribute and break the cross-ref anchor.
    The K counter still increments past these blocks so bare display
    math after a registered equation gets the right within-section
    number.

    Raw-LaTeX ``\\begin{equation}\\label{eq:...}...\\end{equation}``
    blocks (legacy form) are likewise preserved.
    """
    if not section_number:
        return text
    out_parts: list[str] = []
    cursor = 0
    counter = 0
    for m in DISPLAY_MATH_RE.finditer(text):
        out_parts.append(text[cursor : m.start()])
        # Pick the body from whichever alternation matched
        # (`$$..$$`, `\[..\]`, or `\begin{equation}..\end{equation}`).
        body = m.group("body") or m.group("bracket") or m.group("env") or ""
        counter += 1
        # Look ahead for a Pandoc-crossref attribute `{#eq:LABEL}` that
        # immediately follows the closing `$$` (optionally separated
        # by a single space).
        tail = text[m.end() : m.end() + 80]
        attr_match = re.match(r"\s*\{#eq:[A-Za-z0-9_]+\}", tail)
        registered_via_attr = attr_match is not None
        registered_via_env = m.group("env") is not None and "\\label{eq:" in body
        if registered_via_attr or registered_via_env:
            # Registered-equation block: leave the env intact.
            out_parts.append(m.group(0))
        else:
            # Strip any pre-existing `\tag{...}` so we own the numbering.
            body_clean = TAG_RE.sub("", body).rstrip()
            new_block = "$$\n" + body_clean.lstrip("\n") + f"\n\\tag{{{section_number}.{counter}}}\n" + "$$"
            out_parts.append(new_block)
        cursor = m.end()
    out_parts.append(text[cursor:])
    return "".join(out_parts)
