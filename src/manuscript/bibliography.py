"""Auto-generate the Markdown bibliography from `citations.yaml`.
"""

from __future__ import annotations

from registry import CitationRegistry


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
        leftover_topics = sorted(
            {c.topic for c in reg.entries.values()} - seen
        )
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
