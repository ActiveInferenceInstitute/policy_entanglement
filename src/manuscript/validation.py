"""Pure-function manuscript validators.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from registry import Registry
from tokens import iter_tokens


@dataclass
class ManuscriptValidationReport:
    section_files: list[str]
    undefined_tokens: dict[str, list[tuple[str, str]]] = field(default_factory=dict)
    broken_links: dict[str, list[str]] = field(default_factory=dict)
    missing_figure_files: dict[str, list[str]] = field(default_factory=dict)
    out_of_range_variables: dict[str, str] = field(default_factory=dict)
    missing_headings: list[str] = field(default_factory=list)
    empty_captions: list[str] = field(default_factory=list)
    bad_section_refs: dict[str, list[str]] = field(default_factory=dict)
    hardcoded_refs: dict[str, list[str]] = field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        return not (
            self.undefined_tokens
            or self.broken_links
            or self.missing_figure_files
            or self.out_of_range_variables
            or self.missing_headings
            or self.empty_captions
            or self.bad_section_refs
            or self.hardcoded_refs
        )


HYPERLINK_RE = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<href>[^)]+)\)")
HEADING_RE = re.compile(r"^#\s+\S")
SECTION_FILES_RE = re.compile(r"^(\d{2}|S\d{2}|preamble)")

# `§N(.M)` mentioned anywhere in body prose.  We treat top-level §N as
# always-resolvable when the corresponding `0N_*.md` exists, and §N.M
# as resolvable when the target file actually contains a heading
# `## §N.M ...`.
SECTION_REF_RE = re.compile(r"§\s*(\d+)(?:\.(\d+))?")

# Hardcoded-reference detectors that flag prose like `§4` / `Theorem 4.1` /
# `Prop 6.2` outside of their permitted sites (headings, the bold theorem
# block label that introduces the statement, and inline code spans).
HARDCODED_SEC_RE = re.compile(r"§\s*\d+(?:\.\d+[a-z]?)?\b")
HARDCODED_THM_RE = re.compile(
    r"\b(Theorem|Proposition|Prop\.?|Corollary|Cor\.?|Lemma|Definition|Def\.?)\s+\d+(?:\.\d+)?\b"
)


def _is_external(href: str) -> bool:
    return href.startswith(("http://", "https://", "mailto:"))


def _strip_anchor(href: str) -> str:
    return href.split("#", 1)[0]


def section_paths(manuscript_dir: Path) -> list[Path]:
    return sorted(
        p for p in manuscript_dir.glob("*.md")
        if SECTION_FILES_RE.match(p.name) or p.name == "99_bibliography.md"
    )


def collect_section_subheadings(manuscript_dir: Path) -> dict[int, set[int]]:
    """Return `{N: {M, M', ...}}` of subsection numbers `§N.M` defined
    in the registry under `manuscript/refs/labels.yaml`.

    Section numbering is owned by the registry (single source of truth);
    headings in the markdown are intentionally clean (`## Title`) so LaTeX
    can auto-number them.
    """
    refs_file = manuscript_dir / "refs" / "labels.yaml"
    out: dict[int, set[int]] = {}
    if not refs_file.exists():
        return out
    try:
        import yaml
        data = yaml.safe_load(refs_file.read_text()) or {}
    except (OSError, ImportError):
        return out
    sub_re = re.compile(r"^(\d+)\.(\d+)$")
    for entry in (data.get("sections") or {}).values():
        if not isinstance(entry, dict):
            continue
        m = sub_re.match(str(entry.get("number", "")))
        if m:
            N, M = int(m.group(1)), int(m.group(2))
            out.setdefault(N, set()).add(M)
    return out


def collect_top_level_sections(manuscript_dir: Path) -> set[int]:
    """Return `{N}` for which `0N_*.md` exists."""
    out: set[int] = set()
    for p in manuscript_dir.glob("[0-9][0-9]_*.md"):
        try:
            out.add(int(p.name[:2]))
        except ValueError:
            pass
    return out


def _strip_protected_regions(text: str) -> str:
    """Remove regions where hardcoded refs are *allowed*: ``## §N.M ...``
    headings, fenced code blocks, inline code spans, the bold-label
    block of a theorem statement (`**Theorem 4.1.**` … through end of
    that paragraph), and `[[…]]` token bodies.  Leaves a string in
    which any remaining `§N` / `Theorem N.N` is genuinely hardcoded.
    """
    # Remove fenced code blocks (``` … ```).
    text = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.DOTALL)
    # Remove inline code spans `...`.
    text = re.sub(r"`[^`\n]*`", "", text)
    # Remove markdown headings (lines starting with #).
    text = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    # Remove the bold theorem-block label `**Theorem N (Name).**` and
    # the entire paragraph it leads (a paragraph is a non-blank-line run).
    paragraphs = re.split(r"\n\s*\n", text)
    keep = []
    for p in paragraphs:
        if re.match(
            r"\s*\*\*(Theorem|Proposition|Corollary|Lemma|Definition)\s+",
            p,
        ):
            continue
        keep.append(p)
    text = "\n\n".join(keep)
    # Strip [[ ... ]] token bodies entirely.
    text = re.sub(r"\[\[[^\]]+\]\]", "", text)
    return text


def find_hardcoded_refs(text: str) -> list[str]:
    """Return any hardcoded `§N(.M)` or `Theorem N.M` reference that
    appears *outside* protected regions (headings / theorem statements /
    code spans / tokens).  An empty list means every reference flows
    through the registry.
    """
    cleaned = _strip_protected_regions(text)
    out: list[str] = []
    for m in HARDCODED_SEC_RE.finditer(cleaned):
        out.append(m.group(0))
    for m in HARDCODED_THM_RE.finditer(cleaned):
        out.append(m.group(0))
    return out


def validate_section_references(
    text: str,
    *,
    top_level: set[int],
    subsections: dict[int, set[int]],
) -> list[str]:
    """Return any `§N.M` reference whose target subsection is not
    defined.  Top-level `§N` references are accepted whenever
    `0N_*.md` exists (or `N == 99` for the bibliography).
    """
    bad: list[str] = []
    for m in SECTION_REF_RE.finditer(text):
        N = int(m.group(1))
        M = m.group(2)
        if M is None:
            if N not in top_level and N != 99:
                bad.append(f"§{N} (top-level file 0{N}_*.md not found)")
            continue
        Mn = int(M)
        if N not in subsections or Mn not in subsections[N]:
            bad.append(f"§{N}.{Mn} (no `## §{N}.{Mn} …` heading found)")
    return bad


def validate_undefined_tokens(
    text: str, registry: Registry, variables: Mapping[str, Any]
) -> list[tuple[str, str]]:
    """Return ``(kind, label)`` pairs for tokens not in the registry."""
    out: list[tuple[str, str]] = []
    fig_keys = set(registry.labels.figures.keys())
    eq_keys = set(registry.labels.equations.keys())
    sec_keys = set(registry.labels.sections.keys())
    thm_keys = set(registry.labels.theorems.keys())
    cite_keys = set(registry.citations.entries.keys())
    var_keys = set(variables.keys())
    valid_topics = (
        set(registry.citations.topic_titles.keys())
        | {c.topic for c in registry.citations.entries.values()}
        | {"all"}
    )
    for kind, label, _span in iter_tokens(text):
        if kind in {"FIG", "FIGREF"} and label not in fig_keys:
            out.append((kind, label))
        elif kind in {"EQ", "EQREF"} and label not in eq_keys:
            out.append((kind, label))
        elif kind in {"SEC", "SECREF"} and label not in sec_keys:
            out.append((kind, label))
        elif kind in {"THM", "THMREF"} and label not in thm_keys:
            out.append((kind, label))
        elif kind == "LEAN" and label not in thm_keys:
            out.append((kind, label))
        elif kind == "VAR" and label not in var_keys:
            out.append((kind, label))
        elif kind == "CITE" and label not in cite_keys:
            out.append((kind, label))
        elif kind == "CITELIST" and label not in valid_topics:
            out.append((kind, label))
    return out


def _is_generated_output_path(target_str: str) -> bool:
    """Treat any path that points into a project's `output/` tree as a
    *generated artefact* — its existence at validation time is not
    required because the parent template cleans `output/` at Stage 0 and
    repopulates it during Stages 4–7.  The path's *registration* is
    still validated through other channels (`scripts/validate_outputs.py`
    once the pipeline reaches the validate stage).
    """
    # Resolve the canonical components without requiring the path to exist.
    norm = target_str.replace("\\", "/")
    parts = [p for p in norm.split("/") if p not in ("", ".")]
    return "output" in parts


def validate_hyperlinks(text: str, base: Path) -> list[str]:
    """Return relative-link targets that don't exist on disk.

    Generated artefacts under any `output/` subtree are exempt — they
    are produced by later pipeline stages and need not exist when the
    project test suite runs.
    """
    broken: list[str] = []
    for m in HYPERLINK_RE.finditer(text):
        href = m.group("href").strip()
        if not href or _is_external(href) or href.startswith("#"):
            continue
        target_str = _strip_anchor(href)
        # Skip data URIs / token markers
        if target_str.startswith(("data:", "[[")):
            continue
        # Skip generated-output paths.
        if _is_generated_output_path(target_str):
            continue
        target = (base / target_str).resolve()
        if not target.exists():
            broken.append(target_str)
    return broken


def validate_figure_files(
    text: str, manuscript_dir: Path
) -> list[str]:
    """Return image references whose target PNG / SVG is missing."""
    out: list[str] = []
    for m in HYPERLINK_RE.finditer(text):
        # Image syntax is `![alt](src)`.
        if not m.string[max(0, m.start() - 1)] == "!":
            # cheaper: look for a leading `!`
            pass
    # The cheaper traversal — restart and look for the literal `![`.
    image_re = re.compile(r"!\[[^\]]*\]\((?P<href>[^)]+)\)")
    for m in image_re.finditer(text):
        href = _strip_anchor(m.group("href").strip())
        if _is_external(href) or href.startswith("[["):
            continue
        target = (manuscript_dir / href).resolve()
        if not target.exists():
            out.append(href)
    return out


def validate_variables_against_ranges(
    variables: Mapping[str, Any], ranges: Mapping[str, tuple[float, float]]
) -> dict[str, str]:
    """Return ``{key: explanation}`` for every range violation."""
    bad: dict[str, str] = {}
    for key, (lo, hi) in ranges.items():
        if key not in variables:
            bad[key] = f"missing key (expected in [{lo}, {hi}])"
            continue
        v = variables[key]
        if not isinstance(v, (int, float)):
            bad[key] = f"non-numeric value: {v!r}"
            continue
        if not (lo <= v <= hi):
            bad[key] = f"value {v} out of range [{lo}, {hi}]"
    return bad


def validate_manuscript_tree(
    *,
    manuscript_dir: Path,
    registry: Registry,
    variables: Mapping[str, Any],
    variable_ranges: Mapping[str, tuple[float, float]] | None = None,
) -> ManuscriptValidationReport:
    """Walk the manuscript and aggregate all checks."""
    paths = section_paths(manuscript_dir)
    report = ManuscriptValidationReport(section_files=[p.name for p in paths])
    top_level = collect_top_level_sections(manuscript_dir)
    subsections = collect_section_subheadings(manuscript_dir)
    for path in paths:
        text = path.read_text()
        # Headings — accept the first non-blank line that is not a
        # Pandoc raw block (```{=latex}…``` or ```{=html}…```) or a
        # YAML front-matter delimiter (---).
        first_heading = ""
        in_raw = False
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("---"):
                continue
            if stripped.startswith("```"):
                # toggle raw block; the body of a raw block is
                # ignored for the heading check
                in_raw = not in_raw
                continue
            if in_raw:
                continue
            first_heading = stripped
            break
        if not HEADING_RE.match(first_heading):
            report.missing_headings.append(path.name)
        # Tokens.
        bad_tokens = validate_undefined_tokens(text, registry, variables)
        if bad_tokens:
            report.undefined_tokens[path.name] = bad_tokens
        # Hyperlinks.
        bad_links = validate_hyperlinks(text, base=manuscript_dir)
        if bad_links:
            report.broken_links[path.name] = bad_links
        # Image refs.
        bad_imgs = validate_figure_files(text, manuscript_dir)
        if bad_imgs:
            report.missing_figure_files[path.name] = bad_imgs
        # Captions: every `![]()` must have a non-empty alt-text.
        for m in re.finditer(r"!\[(?P<alt>[^\]]*)\]\(", text):
            if not m.group("alt").strip():
                report.empty_captions.append(f"{path.name}: empty alt before col {m.start()}")
        # Section cross-references (§N or §N.M).
        bad_refs = validate_section_references(
            text, top_level=top_level, subsections=subsections,
        )
        if bad_refs:
            report.bad_section_refs[path.name] = bad_refs
        # Hardcoded refs outside permitted sites.
        hard = find_hardcoded_refs(text)
        if hard:
            report.hardcoded_refs[path.name] = hard
    # Numeric ranges (full set).
    if variable_ranges:
        report.out_of_range_variables.update(
            validate_variables_against_ranges(variables, variable_ranges)
        )
    return report
