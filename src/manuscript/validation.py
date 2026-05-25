"""Pure-function manuscript validators."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .registry import Registry
from .tokens import iter_tokens

VARIABLE_PROVENANCE_CLASSES = (
    "hyperparameter-derived",
    "source-scan-derived",
    "registry-derived",
    "analytic-computation",
    "sidecar-derived",
    "uncategorized",
)


_HYPERPARAMETER_LIST_KEYS = frozenset(
    {
        "bernoulli_verification_lambdas",
        "bernoulli_verification_lambdas_count",
        "coupling_ablation_variants_list",
        "ising_alignment_sentinel_lambdas",
        "ising_mi_saturation_lambda",
        "ising_mi_sentinel_lambdas",
        "ising_mi_sentinel_lambdas_count",
        "long_horizon_diagnostic_thresholds_list",
        "long_horizon_replicate_seeds_list",
        "motor_attention_sentinel_lambdas",
        "multi_k_values_list",
        "optimal_lambda_sentinel_deltas",
        "pymdp_total_correlation_sentinel_lambdas",
        "pymdp_total_correlation_sentinel_lambdas_count",
        "robustness_interaction_families_list",
        "spectral_sentinel_lambdas",
        "tt_rank_stream_counts",
    }
)


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
    hardcoded_numeric_literals: dict[str, list[str]] = field(default_factory=dict)
    hardcoded_rendered_source_fields: dict[str, list[str]] = field(default_factory=dict)
    tokens_in_code_fences: dict[str, list[str]] = field(default_factory=dict)
    # Four-track wiring: theorems whose registered ``lean_module`` /
    # ``lean_name`` does not actually resolve to a declaration in the
    # boundary fragment.  Empty when wiring is coherent.
    broken_lean_wiring: dict[str, str] = field(default_factory=dict)

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
            or self.hardcoded_numeric_literals
            or self.hardcoded_rendered_source_fields
            or self.tokens_in_code_fences
            or self.broken_lean_wiring
        )


HYPERLINK_RE = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<href>[^)]+)\)")
HEADING_RE = re.compile(r"^#\s+\S")
SECTION_FILES_RE = re.compile(r"^(\d[A-Z]_|\d{2}_|S\d{2}|preamble)")

# `§N(.M)` mentioned anywhere in body prose.  We treat top-level §N as
# always-resolvable when the corresponding `0N_*.md` exists, and §N.M
# as resolvable when the target file actually contains a heading
# `## §N.M ...`.
SECTION_REF_RE = re.compile(r"§\s*(\d+)(?:\.(\d+))?")

# Hardcoded-reference detectors that flag prose like `§5` / `Theorem 5.1` /
# `Prop 7.2` outside of their permitted sites (headings, the bold theorem
# block label that introduces the statement, and inline code spans).
HARDCODED_SEC_RE = re.compile(r"§\s*\d+(?:\.\d+[a-z]?)?\b")
HARDCODED_THM_RE = re.compile(
    r"\b(Theorem|Proposition|Prop\.?|Corollary|Cor\.?|Lemma|Definition|Def\.?)\s+\d+(?:\.\d+)?\b"
)
HARDCODED_FIG_EQ_RE = re.compile(r"\b(Figure|Fig\.?|Equation|Eq\.?)\s+\(?\d+(?:\.\d+)?\)?\b")
HARDCODED_APPENDIX_RE = re.compile(r"\bAppendix\s+[A-Z]\b")
# Word-form section/table references (the `§` symbol is caught by
# HARDCODED_SEC_RE, but spelled-out "Section 7" / "section 7" and
# "Table 2" slip past it). Manuscript-internal cross-references must
# flow through `[[SECREF:...]]` / registry tokens, and even an external
# "see doc section 7" pointer is brittle — use a stable anchor instead.
HARDCODED_SEC_WORD_RE = re.compile(r"\b[Ss]ection\s+\d+(?:\.\d+)?\b")
HARDCODED_TABLE_RE = re.compile(r"\b[Tt]able\s+\d+\b")
FENCED_CODE_RE = re.compile(r"(```|~~~)[^\n]*\n.*?\1", re.DOTALL)
FORBIDDEN_CODE_FENCE_TOKEN_RE = re.compile(
    r"\[\[(?:EQ|EQREF|FIG|FIGREF|THM|THMREF|SEC|SECREF|LEAN|CITE|CITELIST):[^\]]+\]\]"
)
_INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")
_RENDERED_TOKEN_LEAK_RE = re.compile(
    r"\[\[(?:VAR|SEC|SECREF|THM|THMREF|FIG|FIGREF|EQ|EQREF|LEAN|CITELIST):[^\]]+\]\]"
    r"|\[\[MISSING:[^\]]+\]\]"
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
