"""Auto-generate the Markdown bibliography from `citations.yaml`."""

from __future__ import annotations

import re
from pathlib import Path

from .registry import Citation, CitationRegistry


def _sorted_keys(reg: CitationRegistry, topic: str) -> list[str]:
    if topic == "all":
        return sorted(reg.entries.keys())
    return sorted(k for k, c in reg.entries.items() if c.topic == topic)


def auto_bibliography(reg: CitationRegistry, topic: str = "all") -> str:
    """Render every citation entry of `topic` as a Markdown bullet list."""
    if topic == "all":
        # Group by the configured topic order, then any remaining topics.
        seen: set[str] = set()
        out: list[str] = []
        for t in reg.topic_order:
            keys = _sorted_keys(reg, t)
            if not keys:
                continue
            seen.add(t)
            title = reg.topic_titles.get(t, t.replace("_", " ").title())
            out.append(f"## {title}\n")
            for k in keys:
                out.append(reg.entries[k].render_bibliography())
            out.append("")
        # Catch any topic not in `topic_order`.
        leftover_topics = sorted({c.topic for c in reg.entries.values()} - seen)
        for t in leftover_topics:
            keys = _sorted_keys(reg, t)
            if not keys:
                continue
            title = reg.topic_titles.get(t, t.replace("_", " ").title() if t else "Other")
            out.append(f"## {title}\n")
            for k in keys:
                out.append(reg.entries[k].render_bibliography())
            out.append("")
        return "\n".join(out).rstrip() + "\n"
    keys = _sorted_keys(reg, topic)
    if not keys:
        return ""
    title = reg.topic_titles.get(topic, topic.replace("_", " ").title())
    body = [f"## {title}\n"]
    for k in keys:
        body.append(reg.entries[k].render_bibliography())
    body.append("")
    return "\n".join(body)


def _format_bibtex_authors(authors: str) -> str:
    """Join YAML author list into a BibTeX ``author`` field (`` and ``-separated)."""
    text = authors.strip()
    if not text:
        return ""
    parts = re.split(r"(?<=\.), (?=[A-Z])", text)
    return " and ".join(p.strip() for p in parts if p.strip())


def _bibtex_brace_value(value: str) -> str:
    """Brace-wrap and escape LaTeX-special characters for a BibTeX field value.

    BibTeX hands field values to LaTeX verbatim, so unescaped specials
    (``&`` ``%`` ``#`` ``_`` ``$``) crash the bibliography pass with
    "Misplaced alignment tab character", "Use of \\@@ doesn't match its
    definition" etc. We escape conservatively: literal braces and the
    five common active characters. Backslashes are left alone because
    YAML authors may legitimately embed LaTeX (``\\KL{p}{q}``,
    ``$\\lambda$``) in titles / venues / notes.
    """
    inner = value.replace("{", "\\{").replace("}", "\\}")
    # Escape `&`, `%`, `#`, `_`, `$` only when they aren't already
    # backslash-escaped. A look-behind keeps existing ``\&`` intact.
    inner = re.sub(r"(?<!\\)([&%#_$])", r"\\\1", inner)
    return "{" + inner + "}"


def _infer_entry_type(c: Citation) -> tuple[str, dict[str, str]]:
    """Map a registry :class:`Citation` to BibTeX entry type and fields."""
    fields: dict[str, str] = {}
    author = _format_bibtex_authors(c.authors)
    if author:
        fields["author"] = author
    fields["title"] = c.title
    fields["year"] = str(c.year)
    venue = c.venue.strip()
    if c.doi:
        fields["doi"] = c.doi
    if c.url:
        fields["url"] = c.url
    if c.note:
        fields["note"] = c.note

    if venue.lower().startswith("http"):
        fields["howpublished"] = venue
        return "misc", fields

    if c.volume:
        fields["journal"] = venue
        fields["volume"] = c.volume
        if c.pages:
            fields["pages"] = c.pages.replace("–", "--").replace("—", "--")
        return "article", fields

    if venue:
        fields["howpublished"] = venue
    if c.pages:
        fields["pages"] = c.pages.replace("–", "--").replace("—", "--")
    return "misc", fields


def _ordered_bib_fields(entry_type: str, fields: dict[str, str]) -> list[tuple[str, str]]:
    pref: tuple[str, ...]
    if entry_type == "article":
        pref = (
            "author",
            "title",
            "journal",
            "volume",
            "pages",
            "year",
            "doi",
            "url",
            "note",
        )
    else:
        pref = (
            "author",
            "title",
            "howpublished",
            "pages",
            "year",
            "doi",
            "url",
            "note",
        )
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for k in pref:
        v = str(fields.get(k, "")).strip()
        if v:
            out.append((k, v))
            seen.add(k)
    for k in sorted(fields.keys()):
        if k in seen:
            continue
        v = str(fields[k]).strip()
        if v:
            out.append((k, v))
    return out


def write_references_bib(reg: CitationRegistry, path: Path) -> None:
    """Emit ``references.bib`` for Pandoc/BibTeX from ``citations.yaml``.

    Used by ``scripts/inject_manuscript_variables.py`` (written under
    ``output/manuscript/``) so the Layer-1 PDF pipeline resolves ``[@citekey]``
    without hand-maintaining a second ``.bib`` file.
    """
    lines = [
        "% Auto-generated from manuscript/refs/citations.yaml.",
        "% Do not edit; change the YAML and re-run inject_manuscript_variables.py.",
        "",
    ]
    for key in sorted(reg.entries.keys()):
        c = reg.entries[key]
        entry_type, flds = _infer_entry_type(c)
        lines.append(f"@{entry_type}{{{key},")
        for field_name, val in _ordered_bib_fields(entry_type, flds):
            lines.append(f"  {field_name} = {_bibtex_brace_value(val)},")
        lines.append("}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
