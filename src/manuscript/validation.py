"""Manuscript validation — tree orchestrator."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .registry import Registry
from .validation_checks import (
    _is_generated_output_path,
    find_hardcoded_numeric_literals,
    find_hardcoded_rendered_source_literals,
    validate_figure_files,
    validate_hyperlinks,
    validate_lean_wiring,
    validate_registry_source_fields,
    validate_section_references,
    validate_undefined_tokens,
    validate_variables_against_ranges,
)
from .validation_patterns import (
    FENCED_CODE_RE,
    FORBIDDEN_CODE_FENCE_TOKEN_RE,
    HARDCODED_APPENDIX_RE,
    HARDCODED_FIG_EQ_RE,
    HARDCODED_SEC_RE,
    HARDCODED_SEC_WORD_RE,
    HARDCODED_TABLE_RE,
    HARDCODED_THM_RE,
    HEADING_RE,
    HYPERLINK_RE,
    SECTION_FILES_RE,
    SECTION_REF_RE,
)
from .validation_report import (
    VARIABLE_PROVENANCE_CLASSES,
    ManuscriptValidationReport,
)
from .validation_scan import (
    classify_variable_provenance,
    collect_section_subheadings,
    collect_top_level_sections,
    find_hardcoded_refs,
    find_registry_tokens_in_code_fences,
    find_rendered_token_leaks,
    section_paths,
    validate_rendered_token_leaks,
    variable_provenance_summary,
)


def validate_manuscript_tree(
    *,
    manuscript_dir: Path,
    registry: Registry,
    variables: Mapping[str, Any],
    variable_ranges: Mapping[str, tuple[float, float]] | None = None,
    lean_dir: Path | None = None,
) -> ManuscriptValidationReport:
    """Walk the manuscript and aggregate all checks."""
    paths = section_paths(manuscript_dir)
    report = ManuscriptValidationReport(section_files=[p.name for p in paths])
    top_level = collect_top_level_sections(manuscript_dir)
    subsections = collect_section_subheadings(manuscript_dir)
    for path in paths:
        text = path.read_text()
        # Headings — accept the first non-blank line that is not a
        # Pandoc raw block (```{=latex}…```, ~~~{=latex}~~~ or HTML
        # equivalents) or a
        # YAML front-matter delimiter (---).
        first_heading = ""
        in_raw = False
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("---"):
                continue
            if stripped.startswith(("```", "~~~")):
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
        # Strict source gate: headings render directly into the PDF, so
        # they must not hand-write theorem / section / figure numbers.
        heading_lines: list[str] = []
        in_heading_code = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("```", "~~~")):
                in_heading_code = not in_heading_code
                continue
            if in_heading_code:
                continue
            if stripped.startswith("#"):
                heading_lines.append(stripped)
        strict_heading_hits = find_hardcoded_rendered_source_literals("\n".join(heading_lines))
        if strict_heading_hits:
            report.hardcoded_rendered_source_fields[path.name] = strict_heading_hits
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
            text,
            top_level=top_level,
            subsections=subsections,
        )
        if bad_refs:
            report.bad_section_refs[path.name] = bad_refs
        # Hardcoded refs outside permitted sites.
        hard = find_hardcoded_refs(text)
        if hard:
            report.hardcoded_refs[path.name] = hard
        # Hardcoded numeric literals (grid counts, seeds, T values).
        hard_nums = find_hardcoded_numeric_literals(text)
        if hard_nums:
            report.hardcoded_numeric_literals[path.name] = hard_nums
        fenced_tokens = find_registry_tokens_in_code_fences(text)
        if fenced_tokens:
            report.tokens_in_code_fences[path.name] = fenced_tokens
    # Numeric ranges (full set).
    if variable_ranges:
        report.out_of_range_variables.update(validate_variables_against_ranges(variables, variable_ranges))
    # Four-track wiring: every theorem with a registered Lean companion
    # must resolve to a real Lean declaration. This is the CI-gate that
    # makes the prose ↔ Lean coherence a "show not tell" artifact.
    if lean_dir is not None:
        report.broken_lean_wiring.update(validate_lean_wiring(registry, lean_dir))
    strict_registry_hits = validate_registry_source_fields(registry)
    if strict_registry_hits:
        report.hardcoded_rendered_source_fields.update(strict_registry_hits)
    return report


__all__ = [
    "FENCED_CODE_RE",
    "FORBIDDEN_CODE_FENCE_TOKEN_RE",
    "HARDCODED_APPENDIX_RE",
    "HARDCODED_FIG_EQ_RE",
    "HARDCODED_SEC_RE",
    "HARDCODED_SEC_WORD_RE",
    "HARDCODED_TABLE_RE",
    "HARDCODED_THM_RE",
    "HEADING_RE",
    "HYPERLINK_RE",
    "ManuscriptValidationReport",
    "SECTION_FILES_RE",
    "SECTION_REF_RE",
    "VARIABLE_PROVENANCE_CLASSES",
    "_is_generated_output_path",
    "classify_variable_provenance",
    "collect_section_subheadings",
    "collect_top_level_sections",
    "find_hardcoded_numeric_literals",
    "find_hardcoded_refs",
    "find_hardcoded_rendered_source_literals",
    "find_registry_tokens_in_code_fences",
    "find_rendered_token_leaks",
    "section_paths",
    "validate_figure_files",
    "validate_hyperlinks",
    "validate_lean_wiring",
    "validate_manuscript_tree",
    "validate_registry_source_fields",
    "validate_rendered_token_leaks",
    "validate_section_references",
    "validate_undefined_tokens",
    "validate_variables_against_ranges",
    "variable_provenance_summary",
]
