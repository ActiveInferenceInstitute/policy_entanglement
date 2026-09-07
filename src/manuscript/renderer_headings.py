from __future__ import annotations

import re

from manuscript.registry import Registry, Section

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
