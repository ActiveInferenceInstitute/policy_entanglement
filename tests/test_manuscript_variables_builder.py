"""Tests for :mod:`manuscript.variables` (importable manuscript-variable builder)."""

from __future__ import annotations

import json
from pathlib import Path

from manuscript.variables import (
    PROJECT_ROOT,
    _format_lambda_key,
    build_manuscript_variables,
    write_manuscript_variables,
)
from simulation import hyperparameters as H


def test_format_lambda_key_stable_shapes() -> None:
    assert _format_lambda_key(1.0) == "1"
    assert _format_lambda_key(0.5) == "05"
    assert _format_lambda_key(10.5) == "10_5"


def test_build_manuscript_variables_core_keys() -> None:
    facts = build_manuscript_variables(PROJECT_ROOT)
    assert isinstance(facts, dict)
    assert facts

    for lam in H.ISING_MI_SENTINEL_LAMBDAS:
        key = f"ising_mi_at_lam_{_format_lambda_key(lam)}"
        assert key in facts
        assert isinstance(facts[key], (int, float))

    for k in H.TT_RANK_STREAM_COUNTS:
        prof = facts.get(f"tt_ranks_K{int(k)}")
        assert isinstance(prof, list)
        assert len(prof) == int(k) - 1

    assert "lean_submodule_count" in facts
    assert facts["lean_submodule_count"] >= 10
    assert "theorem_registry_count" in facts
    assert "run_all_script_count" in facts
    assert facts["lean_toolchain_version"] == "v4.29.0"
    assert facts["pymdp_distribution_version"] == "1.0.1"
    assert "leanprover/lean4:" in facts["lean_toolchain_pin"]


def test_build_manuscript_variables_pymdp_branch() -> None:
    facts = build_manuscript_variables(PROJECT_ROOT)
    if isinstance(facts.get("pymdp"), str):
        assert facts["pymdp"] in {"not-installed", "import-failed", "not-run"}
    else:
        for lam in H.PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS:
            key = f"pymdp_total_correlation_lam_{_format_lambda_key(lam)}"
            assert key in facts
            assert isinstance(facts[key], (int, float))


def test_write_manuscript_variables_round_trip(tmp_path: Path) -> None:
    out = tmp_path / "data" / "manuscript_variables.json"
    written = write_manuscript_variables(out, project_root=PROJECT_ROOT)
    assert written == out.resolve()
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload == build_manuscript_variables(PROJECT_ROOT)
