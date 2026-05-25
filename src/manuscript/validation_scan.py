"""Manuscript validation — scanning helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .validation_patterns import (
    _INLINE_CODE_RE,
    _RENDERED_TOKEN_LEAK_RE,
    FENCED_CODE_RE,
    FORBIDDEN_CODE_FENCE_TOKEN_RE,
    HARDCODED_APPENDIX_RE,
    HARDCODED_FIG_EQ_RE,
    HARDCODED_SEC_RE,
    HARDCODED_SEC_WORD_RE,
    HARDCODED_TABLE_RE,
    HARDCODED_THM_RE,
    SECTION_FILES_RE,
)
from .validation_report import (
    _HYPERPARAMETER_LIST_KEYS,
    VARIABLE_PROVENANCE_CLASSES,
)


def _is_external(href: str) -> bool:
    return href.startswith(("http://", "https://", "mailto:"))


def _strip_anchor(href: str) -> str:
    return href.split("#", 1)[0]


def section_paths(manuscript_dir: Path) -> list[Path]:
    return sorted(
        p for p in manuscript_dir.glob("*.md") if SECTION_FILES_RE.match(p.name) or p.name == "99_bibliography.md"
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
    """Return `{N}` for top-level section number ``N`` registered in
    ``manuscript/refs/labels.yaml``.

    Section numbering is owned by the registry, not the filename — file
    prefixes encode IMRAD-part membership (``1B_``, ``2D_``, …) but the
    canonical *section number* lives under each registry entry's
    ``number:`` field.
    """
    refs_file = manuscript_dir / "refs" / "labels.yaml"
    out: set[int] = set()
    if not refs_file.exists():
        return out
    try:
        import yaml

        data = yaml.safe_load(refs_file.read_text()) or {}
    except (OSError, ImportError):
        return out
    top_re = re.compile(r"^(\d+)$")
    for entry in (data.get("sections") or {}).values():
        if not isinstance(entry, dict):
            continue
        m = top_re.match(str(entry.get("number", "")))
        if m and not entry.get("parent"):
            out.add(int(m.group(1)))
    return out


def _strip_protected_regions(text: str) -> str:
    """Remove regions where hardcoded refs are *allowed*: ``## §N.M ...``
    headings, fenced code blocks, inline code spans, the bold-label
    block of a theorem statement (`**Theorem 5.1.**` … through end of
    that paragraph), and `[[…]]` token bodies.  Leaves a string in
    which any remaining `§N` / `Theorem N.N` is genuinely hardcoded.
    """
    # Remove fenced code blocks (``` … ``` or ~~~ … ~~~).
    text = FENCED_CODE_RE.sub("", text)
    # Remove inline code spans `...`.
    text = re.sub(r"`[^`\n]*`", "", text)
    # Remove markdown headings (lines starting with #).
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
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
    for rx in (
        HARDCODED_SEC_RE,
        HARDCODED_SEC_WORD_RE,
        HARDCODED_THM_RE,
        HARDCODED_FIG_EQ_RE,
        HARDCODED_APPENDIX_RE,
        HARDCODED_TABLE_RE,
    ):
        for m in rx.finditer(cleaned):
            out.append(m.group(0))
    return out


def find_registry_tokens_in_code_fences(text: str) -> list[str]:
    """Return registry-rendering tokens that appear inside fenced code.

    `[[VAR:...]]` is allowed in code fences because the supplement uses it
    for JSON-schema examples whose numeric values should still be
    auto-injected.  Cross-reference and Lean-source tokens are disallowed:
    expanding `[[EQ:...]]` or `[[SECREF:...]]` inside a code fence can leak
    raw LaTeX delimiters into the rendered PDF.
    """
    hits: list[str] = []
    for block in FENCED_CODE_RE.finditer(text):
        hits.extend(m.group(0) for m in FORBIDDEN_CODE_FENCE_TOKEN_RE.finditer(block.group(0)))
    return hits


def _strip_rendered_code_examples(text: str) -> str:
    """Remove code regions before scanning rendered manuscript output.

    Rendered prose may legitimately *describe* token syntax inside inline
    code, for example ``[[VAR:<key>]]``.  Those examples should not be
    treated as unresolved runtime tokens.  Anything outside code remains
    paper-facing text and must not contain raw token or missing-marker
    syntax after injection.
    """
    return _INLINE_CODE_RE.sub("", FENCED_CODE_RE.sub("", text))


def find_rendered_token_leaks(text: str) -> list[str]:
    """Return raw token or ``[[MISSING:...]]`` markers outside code.

    This is a post-render guard: source files are allowed to contain
    ``[[VAR:...]]`` / ``[[SECREF:...]]`` tokens, but files under
    ``output/manuscript/`` must have resolved all runtime tokens except
    syntax examples protected inside code spans or fenced blocks.
    """
    cleaned = _strip_rendered_code_examples(text)
    return [m.group(0) for m in _RENDERED_TOKEN_LEAK_RE.finditer(cleaned)]


def validate_rendered_token_leaks(rendered_dir: Path) -> dict[str, list[str]]:
    """Return rendered Markdown files that still contain raw tokens.

    Missing ``rendered_dir`` is reported by the caller.  This helper only
    validates the directory when it exists, which keeps pure validation
    tests from depending on generated artifacts.
    """
    if not rendered_dir.is_dir():
        return {}
    out: dict[str, list[str]] = {}
    for path in sorted(rendered_dir.glob("*.md")):
        hits = find_rendered_token_leaks(path.read_text(encoding="utf-8"))
        if hits:
            out[path.name] = hits
    return out


def classify_variable_provenance(
    key: str,
    *,
    hyperparameter_keys: set[str] | frozenset[str] | None = None,
) -> str:
    """Classify a manuscript-variable key by its generating source."""
    if key in _HYPERPARAMETER_LIST_KEYS or (hyperparameter_keys is not None and key in hyperparameter_keys):
        return "hyperparameter-derived"
    if key.startswith("lean_") or key == "run_all_script_count":
        return "source-scan-derived"
    if key.startswith(("bibliography_", "citation_", "manuscript_", "theorem_")):
        return "registry-derived"
    if key.startswith(
        (
            "coupling_ablation_",
            "interaction_",
            "long_horizon_",
            "multi_k_",
            "pymdp_",
            "revertibility_",
            "robustness_",
        )
    ):
        return "sidecar-derived"
    if key.startswith(("ising_", "lambda_star_", "motor_attention_", "multi_information_", "tt_ranks_")):
        return "analytic-computation"
    if key == "coupling_tax_curvature_C":
        return "analytic-computation"
    return "uncategorized"


def variable_provenance_summary(
    variables: Mapping[str, Any],
    *,
    hyperparameter_keys: set[str] | frozenset[str] | None = None,
) -> dict[str, int]:
    """Return counts of manuscript variables by provenance class."""
    summary = dict.fromkeys(VARIABLE_PROVENANCE_CLASSES, 0)
    for key in variables:
        provenance = classify_variable_provenance(key, hyperparameter_keys=hyperparameter_keys)
        summary[provenance] += 1
    return summary


# Inline literal patterns that *should* come from a `[[VAR:...]]`
# substitution.  Each detector flags suspicious prose like
# "121-point grid", "21 grid points", "T = 10 steps", "seed 0".
#
# Mathematical constants (`\log 2`, `\pi`), generic float-noise floors
# (`1e-9`, `1e-12`), and general framework tolerances are *not* caught
# here — they are not tunable parameters and need not flow through the
# variables JSON. Tunable empirical values (sweep counts, seeds,
# rollout horizons, sentinel-derived MI / entropy / KL results) **are**
# caught.
HARDCODED_GRID_RE = re.compile(
    r"\b\d{2,4}-point\s+(?:grid|linspace|sweep|sample)\b",
    re.IGNORECASE,
)
HARDCODED_GRID_RE_2 = re.compile(
    r"\b\d{2,4}\s+(?:grid points|linspace points|sweep points|samples)\b",
    re.IGNORECASE,
)
HARDCODED_SEED_RE = re.compile(r"\bseed\s*=\s*\d+\b", re.IGNORECASE)
HARDCODED_TSTEPS_RE = re.compile(
    r"(?:\b(?:rollouts|rollout|horizon|trace|trajectory)[^.\n]{0,40}?\$?\bT\s*=\s*\d+\$?"
    r"|\$?\bT\s*=\s*\d+\$?[^.\n]{0,40}?\b(?:steps|step|rollouts|rollout|trajectory))",
    re.IGNORECASE,
)
# Empirical numerical results that look like they came from a
# computation: ``I(λ=0.5) = 0.0314``, ``MI ≈ 0.6931``,
# ``H = 1.4`` outside ``[[VAR:...]]`` brackets.  Three or more
# decimal digits is the heuristic for "this is a measurement, not a
# definition" — defining ``\lambda \in [0, 3]`` keeps short numerals
# unmolested.
HARDCODED_RESULT_RE = re.compile(r"\b(?:I|H|MI|TC|F|KL|S_E)\s*\([^)]{0,40}?\)\s*[=≈]\s*-?\d+\.\d{3,}\b")
HARDCODED_RESULT_WITH_UNIT_RE = re.compile(
    r"\b(?:I|H|MI|TC|F|KL|S_E|VFE|EFE|entropy|correlation|residual|mass|probability)"
    r"[^.\n]{0,80}?\b-?\d+\.\d{3,}\s*(?:nats?|nat|%|percent|residual|probability|mass)\b",
    re.IGNORECASE,
)
HARDCODED_SCI_TOL_RE = re.compile(
    r"(?:≤|<=|\\leq)\s*10\^\{-?\d+\}",
    re.IGNORECASE,
)
HARDCODED_LINSPACE_RE = re.compile(
    r"\blinspace\s*\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*,\s*\d+\s*\)",
    re.IGNORECASE,
)
HARDCODED_THEOREM_COUNT_RE = re.compile(
    r"\b(?:all\s+)?\d+\s+numbered\s+theorems\b",
    re.IGNORECASE,
)
# Closed-form rollout horizons / ensemble sizes spelled out in prose.
HARDCODED_HORIZON_RE = re.compile(
    r"\brollout\s+(?:of|with|horizon\s*=?)\s*\d+\s+(?:step|steps)\b",
    re.IGNORECASE,
)
HARDCODED_T_VALUE_RE = re.compile(r"\bT\s*=\s*\d+\b")
HARDCODED_ENSEMBLE_RE = re.compile(
    r"\$?\bK\s*=\s*\d+\$?\s+(?:streams|stream|stream\s+ensemble|ensemble|ensembles)\b",
    re.IGNORECASE,
)
