"""Tests for manuscript registry structural facts."""

from __future__ import annotations

from pathlib import Path

import pytest

from manuscript.registry_facts import (
    THEOREM_STATUS_KEYS,
    VALID_FAITHFULNESS,
    registry_structural_count_gates,
    registry_structural_facts,
)

PROJECT = Path(__file__).resolve().parent.parent


def test_registry_structural_facts_positive_counts() -> None:
    facts = registry_structural_facts(PROJECT)
    assert facts["theorem_registry_count"] >= 1
    assert facts["manuscript_section_file_count"] >= 1
    assert facts["citation_registry_actual_entries"] >= 1
    assert (
        sum(facts[f"theorem_status_{status}_count"] for status in THEOREM_STATUS_KEYS)
        == facts["theorem_registry_count"]
    )


def test_registry_structural_count_gates_pin_facts() -> None:
    facts = registry_structural_facts(PROJECT)
    gates = registry_structural_count_gates(PROJECT)
    assert gates["theorem_registry_count"] == (
        float(facts["theorem_registry_count"]),
        float(facts["theorem_registry_count"]),
    )
    for status in THEOREM_STATUS_KEYS:
        key = f"theorem_status_{status}_count"
        assert gates[key] == (float(facts[key]), float(facts[key]))


def test_valid_faithfulness_is_frozen_set() -> None:
    assert "substantive" in VALID_FAITHFULNESS
    assert isinstance(VALID_FAITHFULNESS, frozenset)


def test_registry_facts_rejects_bad_faithfulness(tmp_path: Path) -> None:
    manuscript = tmp_path / "manuscript"
    refs = manuscript / "refs"
    refs.mkdir(parents=True)
    (refs / "labels.yaml").write_text(
        "theorems:\n  thm_bad:\n    status: proved\n    faithfulness: not-a-real-tag\n",
        encoding="utf-8",
    )
    (refs / "citations.yaml").write_text("topic_order: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="faithfulness"):
        registry_structural_facts(tmp_path)
