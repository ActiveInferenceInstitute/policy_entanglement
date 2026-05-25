"""Tests that ``docs/reference/veridical_status.md`` Theorem-status table
mirrors the truth in ``manuscript/refs/labels.yaml``.

These tests are the structural sanity rail that prevents the per-theorem
status table from silently drifting away from the registry. The doc is
hand-authored (not auto-generated), so a human can add explanatory text
and rationale around the table; this test only checks the table itself.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

PROJ = Path(__file__).resolve().parent.parent
LABELS_PATH = PROJ / "manuscript" / "refs" / "labels.yaml"
DOC_PATH = PROJ / "docs" / "reference" / "veridical_status.md"
CURRENT_STATUSES = frozenset({"proved", "forwarder", "witness", "boundary", "roadmap"})
STATUS_RE = "|".join(sorted(CURRENT_STATUSES))

# Match a markdown row of the form `| `key` | Kind N.M | ... | status |`
ROW_RE = re.compile(
    r"^\|\s*`(?P<label>[a-z_0-9]+)`"
    r"\s*\|\s*(?P<kind>Theorem|Proposition|Corollary|Lemma|Roadmap)\s+(?P<number>[0-9]+\.[0-9]+(?:[a-z])?)"
    r"\s*\|\s*(?P<lean_cell>[^|]*)"
    rf"\s*\|\s*(?P<status>{STATUS_RE})\s*\|",
    re.MULTILINE,
)


@pytest.fixture(scope="module")
def registry_thms() -> dict[str, dict]:
    return yaml.safe_load(LABELS_PATH.read_text())["theorems"]


@pytest.fixture(scope="module")
def doc_rows() -> dict[str, dict]:
    text = DOC_PATH.read_text()
    rows: dict[str, dict] = {}
    for m in ROW_RE.finditer(text):
        rows[m.group("label")] = {
            "kind": m.group("kind"),
            "number": m.group("number"),
            "lean_cell": m.group("lean_cell").strip(),
            "status": m.group("status"),
        }
    return rows


def test_doc_table_covers_every_registered_theorem(registry_thms: dict[str, dict], doc_rows: dict[str, dict]) -> None:
    missing = sorted(set(registry_thms) - set(doc_rows))
    assert not missing, (
        "veridical_status.md is missing rows for theorems that exist in "
        f"manuscript/refs/labels.yaml: {missing}. Add the missing rows "
        "or update the doc table."
    )


def test_doc_table_does_not_invent_theorems(registry_thms: dict[str, dict], doc_rows: dict[str, dict]) -> None:
    extra = sorted(set(doc_rows) - set(registry_thms))
    assert not extra, (
        "veridical_status.md lists theorem labels that are not in "
        f"manuscript/refs/labels.yaml: {extra}. Either add them to the "
        "registry or remove the rows."
    )


def test_doc_table_kinds_match_registry(registry_thms: dict[str, dict], doc_rows: dict[str, dict]) -> None:
    bad = []
    for label, row in doc_rows.items():
        reg = registry_thms.get(label, {})
        if row["kind"] != reg.get("kind"):
            bad.append((label, row["kind"], reg.get("kind")))
    assert not bad, f"Kind mismatch (label, doc, registry): {bad}"


def test_doc_table_numbers_match_registry(registry_thms: dict[str, dict], doc_rows: dict[str, dict]) -> None:
    bad = []
    for label, row in doc_rows.items():
        reg = registry_thms.get(label, {})
        if row["number"] != str(reg.get("number")):
            bad.append((label, row["number"], reg.get("number")))
    assert not bad, f"Doc table numbers drift from the registry — update docs/reference/veridical_status.md: {bad}"


def test_doc_table_statuses_match_registry(registry_thms: dict[str, dict], doc_rows: dict[str, dict]) -> None:
    bad = []
    for label, row in doc_rows.items():
        reg = registry_thms.get(label, {})
        if row["status"] != reg.get("status"):
            bad.append((label, row["status"], reg.get("status")))
    assert not bad, f"Doc table statuses drift from the registry — update docs/reference/veridical_status.md: {bad}"


def test_registry_uses_only_current_statuses(registry_thms: dict[str, dict]) -> None:
    bad = [
        (label, payload.get("status"))
        for label, payload in registry_thms.items()
        if payload.get("status") not in CURRENT_STATUSES
    ]
    assert not bad, (
        "The theorem registry must use only current public statuses "
        f"{sorted(CURRENT_STATUSES)}; retired sketch/deferred/sorry statuses: {bad}"
    )


def test_doc_lean_module_cell_matches_registry(registry_thms: dict[str, dict], doc_rows: dict[str, dict]) -> None:
    """The ``Lean module . name`` cell must mention the registered Lean
    declaration. All current theorem rows have live Lean companions; a
    missing companion would be a registry regression, not a table style.
    """
    bad: list[tuple[str, str, str]] = []
    for label, row in doc_rows.items():
        reg = registry_thms.get(label, {})
        lean_module = reg.get("lean_module")
        lean_name = reg.get("lean_name")
        cell = row["lean_cell"]
        if lean_module is None or lean_name is None:
            bad.append((label, cell, "expected live Lean module/name"))
        else:
            qualified = f"{lean_module}.{lean_name}"
            if qualified not in cell:
                bad.append((label, cell, f"expected to mention {qualified}"))
    assert not bad, f"Lean module/name drift — update docs/reference/veridical_status.md: {bad}"
