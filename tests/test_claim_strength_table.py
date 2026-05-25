from __future__ import annotations

from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CLAIM_STRENGTHS = ("proved", "witness", "empirical", "hypothesis", "roadmap")


def test_claim_strength_legend_and_evidence_ladder_are_complete() -> None:
    text = (PROJECT / "manuscript" / "S07_reference_tables.md").read_text(encoding="utf-8")
    assert "## Claim-Strength Legend" in text
    assert "## Evidence Ladder and Claim Provenance" in text
    for strength in CLAIM_STRENGTHS:
        assert f"| `{strength}` |" in text
        assert f"`{strength}`" in text.split("## Evidence Ladder and Claim Provenance", 1)[1]


def test_reproducibility_checklist_links_release_note_and_claim_strengths() -> None:
    text = (PROJECT / "docs" / "reference" / "reproducibility_checklist.md").read_text(encoding="utf-8")
    assert "output/reports/release_note.md" in text
    for strength in CLAIM_STRENGTHS:
        assert f"| `{strength}` |" in text
    proved_row = next(line for line in text.splitlines() if line.startswith("| `proved` |"))
    assert "faithfulness" in proved_row
    assert "statement-restricted" in proved_row
