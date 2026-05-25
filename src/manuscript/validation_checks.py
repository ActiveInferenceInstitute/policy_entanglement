"""Manuscript validation — field validators."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .registry import Registry
from .tokens import iter_tokens
from .validation_patterns import (
    FENCED_CODE_RE,
    HARDCODED_APPENDIX_RE,
    HARDCODED_FIG_EQ_RE,
    HARDCODED_SEC_RE,
    HARDCODED_THM_RE,
    HYPERLINK_RE,
    SECTION_REF_RE,
)
from .validation_scan import (
    HARDCODED_ENSEMBLE_RE,
    HARDCODED_GRID_RE,
    HARDCODED_GRID_RE_2,
    HARDCODED_HORIZON_RE,
    HARDCODED_LINSPACE_RE,
    HARDCODED_RESULT_RE,
    HARDCODED_RESULT_WITH_UNIT_RE,
    HARDCODED_SCI_TOL_RE,
    HARDCODED_SEED_RE,
    HARDCODED_T_VALUE_RE,
    HARDCODED_THEOREM_COUNT_RE,
    HARDCODED_TSTEPS_RE,
    _is_external,
    _strip_anchor,
    _strip_protected_regions,
)


def find_hardcoded_numeric_literals(text: str) -> list[str]:
    """Return any inline numeric literal that looks like it should
    have come from a `[[VAR:...]]` substitution (grid counts, seeds,
    rollout horizons, empirical results).

    Inspects the same protected-region-stripped text as
    `find_hardcoded_refs`, so legitimate uses inside code spans,
    headings, and `[[...]]` token bodies are exempt.
    """
    cleaned = _strip_protected_regions(text)
    out: list[str] = []
    for rx in (
        HARDCODED_GRID_RE,
        HARDCODED_GRID_RE_2,
        HARDCODED_SEED_RE,
        HARDCODED_TSTEPS_RE,
        HARDCODED_RESULT_RE,
        HARDCODED_RESULT_WITH_UNIT_RE,
        HARDCODED_SCI_TOL_RE,
        HARDCODED_LINSPACE_RE,
        HARDCODED_THEOREM_COUNT_RE,
        HARDCODED_HORIZON_RE,
        HARDCODED_T_VALUE_RE,
        HARDCODED_ENSEMBLE_RE,
    ):
        for m in rx.finditer(cleaned):
            out.append(m.group(0))
    return out


def _strip_strict_field_protected_regions(text: str) -> str:
    """Strip tokens and code while preserving headings / registry prose.

    The ordinary body-prose detectors deliberately exempt headings and
    theorem statement labels because rendered Markdown needs those forms
    after token resolution.  The strict source-field gate is harsher:
    paper-facing source headings, section titles, captions, and short
    labels should not contain display numbers by hand.
    """
    text = FENCED_CODE_RE.sub("", text)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"\[\[[^\]]+\]\]", "", text)
    return text


def find_hardcoded_rendered_source_literals(text: str) -> list[str]:
    """Return hardcoded references / tunable numerics in paper-facing
    source fields such as headings, registry titles, captions, and
    figure short names.

    This is intentionally stricter than :func:`find_hardcoded_refs`:
    headings are scanned, and figure / equation / appendix display
    labels are included.  Rendered output may contain numbers because
    tokens resolve to display labels; source fields must use tokens or
    neutral wording.
    """
    cleaned = _strip_strict_field_protected_regions(text)
    out: list[str] = []
    for rx in (
        HARDCODED_SEC_RE,
        HARDCODED_THM_RE,
        HARDCODED_FIG_EQ_RE,
        HARDCODED_APPENDIX_RE,
        HARDCODED_GRID_RE,
        HARDCODED_GRID_RE_2,
        HARDCODED_SEED_RE,
        HARDCODED_TSTEPS_RE,
        HARDCODED_HORIZON_RE,
        HARDCODED_T_VALUE_RE,
        HARDCODED_LINSPACE_RE,
    ):
        for m in rx.finditer(cleaned):
            out.append(m.group(0))
    return out


def validate_registry_source_fields(registry: Registry) -> dict[str, list[str]]:
    """Scan rendered registry fields for source-level hardcoded labels.

    The scanned fields are the ones that render into the paper:
    section titles, figure captions / short names, equation names /
    LaTeX, and theorem names.  Metadata fields such as ``sections:`` are
    not scanned here because they are discovery metadata rather than
    paper prose.
    """
    out: dict[str, list[str]] = {}

    def _check(key: str, value: str) -> None:
        hits = find_hardcoded_rendered_source_literals(value)
        if hits:
            out[key] = hits

    for label, fig in registry.labels.figures.items():
        _check(f"labels.yaml::figures.{label}.caption", fig.caption)
        _check(f"labels.yaml::figures.{label}.short", fig.short)
    for label, section in registry.labels.sections.items():
        _check(f"labels.yaml::sections.{label}.title", section.title)
    for label, theorem in registry.labels.theorems.items():
        _check(f"labels.yaml::theorems.{label}.name", theorem.name)
    for label, equation in registry.labels.equations.items():
        _check(f"labels.yaml::equations.{label}.name", equation.name)
        _check(f"labels.yaml::equations.{label}.latex", equation.latex)
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


def validate_undefined_tokens(text: str, registry: Registry, variables: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Return ``(kind, label)`` pairs for tokens not in the registry."""
    out: list[tuple[str, str]] = []
    fig_keys = set(registry.labels.figures.keys())
    eq_keys = set(registry.labels.equations.keys())
    sec_keys = set(registry.labels.sections.keys())
    thm_keys = set(registry.labels.theorems.keys())
    cite_keys = set(registry.citations.entries.keys())
    var_keys = set(variables.keys())
    valid_topics = (
        set(registry.citations.topic_titles.keys()) | {c.topic for c in registry.citations.entries.values()} | {"all"}
    )
    # RedTeam 2026-05-19 H3 — sentinel-string laundering guard. A VAR
    # whose KEY exists but whose VALUE is a producer sentinel
    # (`not-run`/`not-installed`/`import-failed`/`invalid-*`, emitted by
    # scripts/manuscript_variables.py when pymdp/a sidecar is absent or
    # malformed) would otherwise render straight into published prose
    # with NO gate failing. Such a VAR is effectively undefined-for-
    # publication: flag it exactly like an undefined token so the build
    # fails rather than ship a sentinel as a scientific number.
    _SENTINEL_RE = re.compile(
        r"^\s*(not[-_]run|not[-_]installed|import[-_]failed|invalid[-_][a-z]+|not[-_]present)\s*$",
        re.IGNORECASE,
    )

    def _is_sentinel(v: Any) -> bool:
        return isinstance(v, str) and bool(_SENTINEL_RE.match(v))

    for kind, label, _span in iter_tokens(text):
        if kind == "VAR" and label in var_keys and _is_sentinel(variables.get(label)):
            out.append((kind, label))
            continue
        if (
            (kind in {"FIG", "FIGREF"} and label not in fig_keys)
            or (kind in {"EQ", "EQREF"} and label not in eq_keys)
            or (kind in {"SEC", "SECREF"} and label not in sec_keys)
            or (kind in {"THM", "THMREF"} and label not in thm_keys)
            or (kind == "LEAN" and label not in thm_keys)
            or (kind == "VAR" and label not in var_keys)
            or (kind == "CITE" and label not in cite_keys)
            or (kind == "CITELIST" and label not in valid_topics)
        ):
            out.append((kind, label))
    return out


def _is_generated_output_path(target_str: str) -> bool:
    """Treat any path that points into a project's `output/` tree as a
    *generated artifact* — its existence at validation time is not
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

    Generated artifacts under any `output/` subtree are exempt — they
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


def validate_figure_files(text: str, manuscript_dir: Path) -> list[str]:
    """Return image references whose target PNG / SVG is missing."""
    out: list[str] = []
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


def validate_lean_wiring(
    registry: Registry,
    lean_dir: Path | None,
) -> dict[str, str]:
    """For every theorem in the registry that declares a Lean companion
    (``lean_module`` / ``lean_name`` fields populated), verify that the
    qualified name actually resolves to a declaration in the live
    boundary fragment under ``lean_dir``.

    Returns ``{label: explanation}`` for every broken wiring. Empty
    when every registered Lean companion exists.

    Skipped (returns empty) when ``lean_dir`` is ``None`` or missing.
    The four-track coherence gate that prevents silent drift between
    the manuscript theorem table, the Lean source, and the auto-injected
    ``[[LEAN:...]]`` blocks.
    """
    if lean_dir is None or not lean_dir.is_dir():
        return {}
    # Defer import: lean_extract has its own dependencies.
    from .lean_extract import load_lean_snippets

    snippets = load_lean_snippets(lean_dir)
    broken: dict[str, str] = {}
    for label, theorem in registry.labels.theorems.items():
        if not theorem.has_lean_companion:
            continue
        module = theorem.lean_module
        qname = theorem.lean_name
        # Module file existence check.
        module_file = lean_dir / f"{module}.lean"
        if not module_file.is_file():
            broken[label] = (
                f"registry says lean_module='{module}' but file '{module_file.name}' is missing under {lean_dir}"
            )
            continue
        # Snippet existence check (qualified name resolves).
        if (module, qname) not in snippets:
            broken[label] = (
                f"registry says lean_name='{qname}' in module '{module}' but no "
                f"such declaration was found in the live source"
            )
    return broken

