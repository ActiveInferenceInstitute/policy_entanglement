"""Drift test: every public Python identifier in `src/` must be
referenced in `docs/reference/python_api.md`.

We catch the most common documentation drift — an author adds a new
public function or class but forgets to surface it in the API
reference — by string-matching identifiers against the docs file.

Sanctioned exceptions are listed in :data:`UNDOCUMENTED_OK`; everything
else fails the test.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
SRC = PROJECT / "src"
API_DOC = PROJECT / "docs" / "reference" / "python_api.md"

PUBLIC_DEF_RE = re.compile(
    r"^(?:def\s+|class\s+|@dataclass[^\n]*\nclass\s+)([A-Za-z][A-Za-z0-9_]*)",
    re.MULTILINE,
)
ASSIGN_PUBLIC_RE = re.compile(r"^([A-Z][A-Z0-9_]+)\s*=", re.MULTILINE)


# Identifiers that need not surface in the API reference (private
# helpers leaking through, internal regex constants, deprecated paths).
UNDOCUMENTED_OK: set[str] = {
    # Private helpers (leading underscore handled by the regex; this
    # set captures public-named helpers that are nevertheless internal).
    "mathlib_proofs_lock_path",
    "mathlib_proofs_lock",
    # Token regexes — documented at the level of the regex names list
    # in `tokens.py`, individual constants don't need their own entry.
    "FIG_RE",
    "FIGREF_RE",
    "EQ_RE",
    "EQREF_RE",
    "VAR_RE",
    "CITATION_RE",
    "CITELIST_RE",
    "SEC_RE",
    "SECREF_RE",
    "THM_RE",
    "THMREF_RE",
    "LEAN_RE",
    "DISPLAY_MATH_RE",
    "EQ_TOKEN_RE",
    "TAG_RE",
    "HYPERLINK_RE",
    "HEADING_RE",
    "SECTION_FILES_RE",
    "SECTION_REF_RE",
    "HARDCODED_SEC_RE",
    "HARDCODED_THM_RE",
    "HARDCODED_GRID_RE",
    "HARDCODED_GRID_RE_2",
    "HARDCODED_SEED_RE",
    "HARDCODED_TSTEPS_RE",
    "HARDCODED_RESULT_RE",
    "HARDCODED_HORIZON_RE",
    "HARDCODED_ENSEMBLE_RE",
    # Module-level format / install string constants.
    "PYMDP_INSTALL_HINT",
    # Internal Lean-extract constants.
    "_DECL_KEYWORDS",
    "_LOG_FLOOR",
    # Sentinel-λ / hyperparameter tuples are documented as a list of
    # symbols; individual tuple constants need not be listed by name.
    "ISING_MI_SATURATION_LAMBDA",
    "ISING_MI_SENTINEL_LAMBDAS",
    "OPTIMAL_LAMBDA_SENTINEL_DELTAS",
    "SPECTRAL_SENTINEL_LAMBDAS",
    "ISING_ALIGNMENT_SENTINEL_LAMBDAS",
    "MOTOR_ATTENTION_SENTINEL_LAMBDAS",
    "TT_RANK_STREAM_COUNTS",
    "PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS",
}


def _public_names_in(path: Path) -> set[str]:
    text = path.read_text()
    out: set[str] = set()
    for m in PUBLIC_DEF_RE.finditer(text):
        name = m.group(1)
        if not name.startswith("_"):
            out.add(name)
    for m in ASSIGN_PUBLIC_RE.finditer(text):
        name = m.group(1)
        out.add(name)
    return out


@pytest.fixture(scope="module")
def api_doc_text() -> str:
    """Concatenate the API index page with each per-subpackage page so
    tests can string-match identifiers regardless of which page hosts
    the canonical signature.
    """
    parts = [API_DOC.read_text()]
    for sub in ("lean", "simulation", "visualizations", "manuscript", "gnn"):
        path = API_DOC.parent / f"python_api_{sub}.md"
        if path.exists():
            parts.append(path.read_text())
    return "\n".join(parts)


@pytest.fixture(scope="module")
def public_identifiers() -> dict[str, set[str]]:
    """Map module-relative-path → set of public identifier names."""
    out: dict[str, set[str]] = {}
    for p in sorted(SRC.rglob("*.py")):
        if p.name == "__init__.py" or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(SRC).as_posix()
        out[rel] = _public_names_in(p)
    return out


def test_public_identifiers_collected(public_identifiers) -> None:
    """Sanity: at least 50 public identifiers across the four
    subpackages.
    """
    total = sum(len(v) for v in public_identifiers.values())
    assert total >= 50, f"only {total} public identifiers collected"


def test_every_public_identifier_documented(public_identifiers, api_doc_text) -> None:
    """For every public function / class / module-level constant in
    `src/`, its name must appear at least once in
    `docs/reference/python_api.md`.
    """
    missing: dict[str, set[str]] = {}
    for module, names in public_identifiers.items():
        for name in names:
            if name in UNDOCUMENTED_OK:
                continue
            if name not in api_doc_text:
                missing.setdefault(module, set()).add(name)
    assert not missing, f"undocumented public identifiers (not in python_api.md): {missing}"


def test_every_subpackage_has_a_section(api_doc_text) -> None:
    """Each of the four subpackages must have a header section in
    the API reference.
    """
    for hdr in (
        "## Subpackage `lean/`",
        "## Subpackage `simulation/`",
        "## Subpackage `visualizations/`",
        "## Subpackage `manuscript/`",
    ):
        assert hdr in api_doc_text, f"missing API doc section: {hdr!r}"


def test_new_modules_have_subsections(api_doc_text) -> None:
    """The new modules we added in recent passes must have their own
    `### <module>` subsection.
    """
    for sub in (
        "### `hyperparameters.py`",
        "### `statistics.py`",
        "### `logging_utils.py`",
        "### `equation_numbering.py`",
        "### `free_energy_plots.py`",
        "### `pymdp_extras.py`",
        "### `metadata.py`",
        "### `build_gate.py`",
        "### `index_generator.py`",
        "### `validation_cli.py`",
        "### `orchestration/run_all.py`",
        "### `orchestration/build_pdf.py`",
        "### `gates/regression_gate.py`",
        "### `gates/regression_baseline.py`",
        "### `gates/regression_pytest.py`",
        "### `variables_analytical.py`",
        "### `variables_pipeline.py`",
        "### `variables_sidecars.py`",
        "### `publication_metadata.py`",
        "### `readiness_audit.py`",
    ):
        assert sub in api_doc_text, f"new-module subsection missing: {sub!r}"


def test_hardcoded_numeric_literal_helper_documented(api_doc_text) -> None:
    """The CI-gated `find_hardcoded_numeric_literals` validator must
    surface in the API reference with its purpose flagged.
    """
    assert "find_hardcoded_numeric_literals" in api_doc_text


def test_visualization_facade_exports_documented_annotation_helpers() -> None:
    """The package facade should expose the annotation helpers that the
    public API page documents under `visualizations.annotations`.
    """
    import visualizations

    for name in (
        "add_stats_box",
        "add_mean_field_baseline",
        "add_tolerance_band",
        "add_saturation_marker",
        "add_claim_strength_tag",
    ):
        assert hasattr(visualizations, name), f"visualizations facade missing {name}"
