"""Parse `manuscript/refs/{labels,citations}.yaml` into typed records."""

from __future__ import annotations

from dataclasses import dataclass, field  # noqa: F401
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Figure:
    label: str
    path: str
    caption: str
    short: str
    sections: tuple[str, ...]
    source: str
    number: int
    uncertainty: str = ""


@dataclass(frozen=True)
class Equation:
    label: str
    latex: str
    name: str
    sections: tuple[str, ...]
    number: int


@dataclass(frozen=True)
class Citation:
    key: str
    authors: str
    year: int
    title: str
    venue: str
    volume: str = ""
    pages: str = ""
    doi: str = ""
    url: str = ""
    note: str = ""
    topic: str = ""

    def render_inline(self) -> str:
        """``(Author year)`` form used in body text."""
        first_author = self.authors.split(",")[0].strip().split()[-1]
        return f"({first_author} {self.year})"

    @staticmethod
    def _with_terminal_period(text: str) -> str:
        """Return ``text`` with exactly one terminal sentence mark."""
        stripped = text.rstrip()
        if stripped.endswith((".", "?", "!")):
            return stripped
        return stripped + "."

    def render_bibliography(self) -> str:
        """Markdown bullet line for the bibliography body."""
        parts = [self.authors, f"({self.year})", self._with_terminal_period(self.title)]
        venue = f"*{self.venue}*"
        if self.volume:
            venue += f" **{self.volume}**"
        if self.pages:
            venue += f", {self.pages}"
        venue += "."
        parts.append(venue)
        if self.url:
            parts.append(f"<{self.url}>")
        if self.doi:
            parts.append(f"doi:{self.doi}")
        line = " ".join(parts)
        if self.note:
            line += f" *{self.note}*"
        return f"- {line}"


@dataclass(frozen=True)
class Section:
    label: str
    number: str
    title: str
    file: str
    parent: str


@dataclass(frozen=True)
class TheoremEntry:
    label: str
    kind: str
    number: str
    name: str
    section: str
    # Optional Lean companion + Mathlib-readiness status.
    lean_module: str = ""  # e.g. "Decomposition" / "Geometry"
    lean_name: str = ""  # e.g. "entanglement_decomposition"
    # Current public statuses. Historical `sketch` / `deferred` rows were
    # retired in round 3 and are rejected by the status-table tests.
    status: str = ""  # one of: proved | boundary | forwarder | witness

    def render_block(self) -> str:
        if self.name:
            return f"**{self.kind} {self.number} ({self.name}).**"
        return f"**{self.kind} {self.number}.**"

    def render_inline(self) -> str:
        return f"{self.kind} {self.number}"

    @property
    def has_lean_companion(self) -> bool:
        return bool(self.lean_module and self.lean_name)


@dataclass(frozen=True)
class LabelsRegistry:
    figures: dict[str, Figure]
    equations: dict[str, Equation]
    sections: dict[str, Section] = field(default_factory=dict)
    theorems: dict[str, TheoremEntry] = field(default_factory=dict)


@dataclass(frozen=True)
class CitationRegistry:
    entries: dict[str, Citation]
    topic_order: tuple[str, ...]
    topic_titles: dict[str, str]


@dataclass(frozen=True)
class Registry:
    labels: LabelsRegistry
    citations: CitationRegistry


def _seq(value) -> tuple[str, ...]:
    if value is None:
        return tuple()
    if isinstance(value, str):
        return (value,)
    return tuple(str(v) for v in value)


def load_labels(path: Path) -> LabelsRegistry:
    data = yaml.safe_load(path.read_text())
    figures: dict[str, Figure] = {}
    for n, (label, payload) in enumerate((data.get("figures") or {}).items(), start=1):
        figures[label] = Figure(
            label=label,
            path=str(payload["path"]),
            caption=str(payload.get("caption", "")).strip(),
            short=str(payload.get("short", "")),
            sections=_seq(payload.get("sections")),
            source=str(payload.get("source", "")),
            number=int(payload.get("number") or n),
            uncertainty=str(payload.get("uncertainty", "") or ""),
        )
    equations: dict[str, Equation] = {}
    for n, (label, payload) in enumerate((data.get("equations") or {}).items(), start=1):
        equations[label] = Equation(
            label=label,
            latex=str(payload["latex"]).strip(),
            name=str(payload.get("name", "")),
            sections=_seq(payload.get("sections")),
            number=int(payload.get("number") or n),
        )
    sections: dict[str, Section] = {}
    for label, payload in (data.get("sections") or {}).items():
        if not isinstance(payload, dict):
            continue
        sections[label] = Section(
            label=label,
            number=str(payload.get("number", "")),
            title=str(payload.get("title", "")),
            file=str(payload.get("file", "") or ""),
            parent=str(payload.get("parent", "") or ""),
        )
    theorems: dict[str, TheoremEntry] = {}
    for label, payload in (data.get("theorems") or {}).items():
        if not isinstance(payload, dict):
            continue
        theorems[label] = TheoremEntry(
            label=label,
            kind=str(payload.get("kind", "Theorem")),
            number=str(payload.get("number", "")),
            name=str(payload.get("name", "") or ""),
            section=str(payload.get("section", "") or ""),
            lean_module=str(payload.get("lean_module", "") or ""),
            lean_name=str(payload.get("lean_name", "") or ""),
            status=str(payload.get("status", "") or ""),
        )
    return LabelsRegistry(
        figures=figures,
        equations=equations,
        sections=sections,
        theorems=theorems,
    )


def load_citations(path: Path) -> CitationRegistry:
    data = yaml.safe_load(path.read_text())
    topic_order = tuple(data.pop("topic_order", []) or [])
    topic_titles = dict(data.pop("topic_titles", {}) or {})
    entries: dict[str, Citation] = {}
    for key, payload in data.items():
        if not isinstance(payload, dict):
            continue
        entries[key] = Citation(
            key=key,
            authors=str(payload.get("authors", "")),
            year=int(payload.get("year", 0)),
            title=str(payload.get("title", "")),
            venue=str(payload.get("venue", "")),
            volume=str(payload.get("volume", "") or ""),
            pages=str(payload.get("pages", "") or ""),
            doi=str(payload.get("doi", "") or ""),
            url=str(payload.get("url", "") or ""),
            note=str(payload.get("note", "") or ""),
            topic=str(payload.get("topic", "") or ""),
        )
    return CitationRegistry(
        entries=entries,
        topic_order=topic_order,
        topic_titles=topic_titles,
    )


def load_registry(refs_dir: Path) -> Registry:
    """Load both registries from `manuscript/refs/`."""
    return Registry(
        labels=load_labels(refs_dir / "labels.yaml"),
        citations=load_citations(refs_dir / "citations.yaml"),
    )
