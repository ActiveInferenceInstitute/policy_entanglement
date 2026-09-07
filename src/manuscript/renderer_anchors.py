from __future__ import annotations

import re

from manuscript.registry import Registry, Section

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
