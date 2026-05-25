from __future__ import annotations

import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MANUSCRIPT = PROJECT / "manuscript"
DOCS = PROJECT / "docs"

RECOVERY_CLASSES = {"exact", "parametric", "analogical", "out-of-scope"}
HISTORICAL_DOC_PATHS = {
    DOCS / "CHANGELOG.md",
    DOCS / "reference" / "veridical_status.md",
}


def _table_rows_after(text: str, heading: str) -> list[str]:
    _, tail = text.split(heading, 1)
    rows = []
    for line in tail.splitlines():
        if line.startswith("## ") and rows:
            break
        if line.startswith("|") and not re.match(r"^\|\s*-", line):
            rows.append(line)
    return rows


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def test_active_inference_recovery_ledger_classifies_every_row() -> None:
    text = (MANUSCRIPT / "S07_reference_tables.md").read_text(encoding="utf-8")
    rows = _table_rows_after(text, "## Active-Inference Variant Recovery Ledger")
    assert rows, "missing active-inference recovery ledger table"

    data_rows = [row for row in rows if "Relationship class" not in row]
    assert len(data_rows) >= 8
    for row in data_rows:
        normalized = _cells(row)[2].lower()
        classes = {cls for cls in RECOVERY_CLASSES if f"`{cls}`" in normalized}
        assert len(classes) == 1, row
        assert "do not overclaim" not in row.lower()


def test_active_inference_synthesis_table_keeps_relationship_classes() -> None:
    text = (MANUSCRIPT / "5B_connections_aif.md").read_text(encoding="utf-8")
    rows = _table_rows_after(text, "| Framework | $J$ structure | $\\lambda$ regime | Recovery type |")
    data_rows = [row for row in rows if "Framework" not in row]
    assert any("Factor-graph / RxInfer-style message passing" in row for row in data_rows)
    assert any(
        "Factor-graph / RxInfer-style message passing" in row and _cells(row)[3] == "parametric" for row in data_rows
    )

    for row in data_rows:
        normalized = _cells(row)[3].lower()
        classes = {cls for cls in RECOVERY_CLASSES if cls in normalized}
        assert len(classes) == 1, row


def _current_markdown_text() -> str:
    manuscript_paths = [path for path in MANUSCRIPT.glob("*.md") if not path.name.startswith("99_")]
    doc_paths = [
        path for path in DOCS.rglob("*.md") if path not in HISTORICAL_DOC_PATHS and "CHANGELOG" not in path.name
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in manuscript_paths + doc_paths)


def test_current_sources_forbid_variant_overclaim_phrases() -> None:
    current_text = _current_markdown_text().lower()
    forbidden = (
        "exactly recovers hierarchical AIF",
        "exactly recovers deep AIF",
        "exactly the structure of hierarchical AIF",
        "proves the limit equivalence formally",
        "Recovers hierarchical AIF / deep temporal AIF",
        "exactly habit formation in standard AIF",
        "proves sophisticated inference",
        "recovers each of the architectures above as a limit",
        "hierarchical AIF, sophisticated inference, branching-time AIF, copula VI, products of experts, options, KL / path-integral control, and renormalization-group AIF as a structural analogy",
    )
    for phrase in forbidden:
        assert phrase.lower() not in current_text


def test_current_sources_forbid_lambda_precision_and_clinical_overclaims() -> None:
    current_text = _current_markdown_text().lower()
    forbidden = (
        "λ is policy precision",
        "lambda is policy precision",
        "λ is neural precision",
        "lambda is neural precision",
        "validated in humans",
        "clinical proof",
        "proves a clinical",
        "demonstrates a biological implementation",
    )
    for phrase in forbidden:
        assert phrase.lower() not in current_text


def test_message_passing_citations_are_registered_and_used() -> None:
    citations = (MANUSCRIPT / "refs" / "citations.yaml").read_text(encoding="utf-8")
    current_text = _current_markdown_text()
    for key in (
        "friston-parr-devries-2017-graphical-brain",
        "parr-markovic-kiebel-friston-2019-message-passing",
    ):
        assert f"{key}:" in citations
        assert f"@{key}" in current_text
