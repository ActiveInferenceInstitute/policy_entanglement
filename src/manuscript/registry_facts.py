"""Manuscript registry structural facts and count gates."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

VALID_FAITHFULNESS = frozenset(
    {
        "substantive",
        "definitional",
        "statement-restricted",
        "typed-witness",
        "forwarder",
        "numerical_corroboration_only",
    }
)

THEOREM_STATUS_KEYS = ("proved", "witness", "boundary", "forwarder", "sketch", "deferred", "roadmap")


def registry_structural_facts(project_root: Path) -> dict[str, int]:
    """Counts derived from manuscript registries and section files."""

    manuscript_dir = project_root / "manuscript"
    labels_path = manuscript_dir / "refs" / "labels.yaml"
    citations_path = manuscript_dir / "refs" / "citations.yaml"
    labels = yaml.safe_load(labels_path.read_text(encoding="utf-8")) or {}
    citations = yaml.safe_load(citations_path.read_text(encoding="utf-8")) or {}

    theorems = labels.get("theorems") or {}
    theorem_status_counts = dict.fromkeys(THEOREM_STATUS_KEYS, 0)
    proved_faithfulness_counts = {
        "substantive": 0,
        "definitional": 0,
        "statement-restricted": 0,
    }
    for label, row in theorems.items():
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", ""))
        if status in theorem_status_counts:
            theorem_status_counts[status] += 1
        faith = str(row.get("faithfulness", ""))
        if faith not in VALID_FAITHFULNESS:
            raise ValueError(
                f"theorem registry row {label!r} (status: {status!r}) "
                f"has faithfulness={faith!r}; every row must declare a "
                f"valid faithfulness ({sorted(VALID_FAITHFULNESS)})."
            )
        if status == "proved":
            proved_faithfulness_counts[faith] += 1

    section_re = re.compile(r"^(\d[A-Z]_|\d{2}_|S\d{2}|preamble)")
    section_files = [
        p for p in manuscript_dir.glob("*.md") if section_re.match(p.name) or p.name == "99_bibliography.md"
    ]
    body_files = [p for p in section_files if re.match(r"^\d[A-Z]_", p.name)]
    supplement_files = [p for p in section_files if re.match(r"^S\d{2}", p.name)]
    citation_entries = [k for k in citations if k not in {"topic_order", "topic_titles"}]

    out = {
        "manuscript_section_file_count": len(section_files),
        "manuscript_body_section_count": len(body_files),
        "manuscript_supplement_count": len(supplement_files),
        "citation_registry_yaml_entries": len(citations),
        "citation_registry_actual_entries": len(citation_entries),
        "bibliography_rendered_entries": len(citation_entries),
        "theorem_registry_count": len(theorems),
    }
    for status, count in theorem_status_counts.items():
        out[f"theorem_status_{status}_count"] = count
    out["theorem_proved_substantive_count"] = proved_faithfulness_counts["substantive"]
    out["theorem_proved_definitional_count"] = proved_faithfulness_counts["definitional"]
    out["theorem_proved_restricted_count"] = proved_faithfulness_counts["statement-restricted"]
    return out


def registry_structural_count_gates(project_root: Path) -> dict[str, tuple[float, float]]:
    """Pin each registry-derived VAR to an independently recomputed count."""

    facts = registry_structural_facts(project_root)

    def _pin(value: int) -> tuple[float, float]:
        return (float(value), float(value))

    gates: dict[str, tuple[float, float]] = {"theorem_registry_count": _pin(facts["theorem_registry_count"])}
    for status in THEOREM_STATUS_KEYS:
        gates[f"theorem_status_{status}_count"] = _pin(facts[f"theorem_status_{status}_count"])
    gates["theorem_proved_substantive_count"] = _pin(facts["theorem_proved_substantive_count"])
    gates["theorem_proved_definitional_count"] = _pin(facts["theorem_proved_definitional_count"])
    gates["theorem_proved_restricted_count"] = _pin(facts["theorem_proved_restricted_count"])
    return gates


__all__ = [
    "THEOREM_STATUS_KEYS",
    "VALID_FAITHFULNESS",
    "registry_structural_count_gates",
    "registry_structural_facts",
]
