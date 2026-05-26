"""Tests for :mod:`manuscript.variables` (importable manuscript-variable builder)."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from manuscript import variables as facade
from manuscript.variables import (
    PROJECT_ROOT,
    _format_lambda_key,
    build_manuscript_variables,
    write_manuscript_variables,
)
from simulation import hyperparameters as H


@pytest.mark.parametrize(
    ("facade_name", "submodule", "submodule_name"),
    [
        ("_format_lambda_key", "manuscript.variables_analytical", "format_lambda_key"),
        ("_format_lambda_list", "manuscript.variables_analytical", "format_lambda_list"),
    ],
)
def test_facade_reexports_match_submodules(facade_name: str, submodule: str, submodule_name: str) -> None:
    """Public facade aliases must mirror their domain submodule source."""
    mod = importlib.import_module(submodule)
    assert getattr(facade, facade_name) is getattr(mod, submodule_name)


def test_build_manuscript_variables_uses_domain_modules() -> None:
    from manuscript import variables_analytical, variables_pipeline, variables_sidecars

    root = PROJECT_ROOT
    merged: dict[str, object] = {}
    merged.update(variables_analytical.bernoulli_facts())
    merged.update(variables_analytical.spectral_facts())
    merged.update(variables_analytical.alignment_and_phase_facts())
    merged.update(variables_analytical.motor_attention_facts())
    merged.update(variables_analytical.coupling_tax_curvature())
    merged.update(variables_pipeline.run_all_facts(root))
    merged.update(variables_pipeline.lean_facts(root))
    merged.update(variables_pipeline.toolchain_facts(root))
    merged.update(variables_pipeline.registry_facts(root))
    merged.update(variables_analytical.tensor_train_facts())
    merged.update(variables_sidecars.pymdp_facts())
    merged.update(variables_sidecars.json_sidecar_facts(root))
    merged.update(variables_sidecars.gnn_facts(root))
    merged.update(variables_analytical.sentinel_list_facts())
    merged.update(variables_sidecars.hyperparameter_facts())
    assert build_manuscript_variables(root) == merged


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
