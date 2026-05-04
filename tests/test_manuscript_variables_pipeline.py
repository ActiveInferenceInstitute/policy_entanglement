"""Schema and range tests for `output/data/manuscript_variables.json`.

Runs only when the JSON has been generated (skips otherwise).  The
tests assert that every key the manuscript references is present and
in-range, so a regression in `manuscript_variables.py` is caught
before the manuscript renderer runs.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
JSON_PATH = PROJECT / "output" / "data" / "manuscript_variables.json"


@pytest.fixture(scope="module")
def variables() -> dict[str, object]:
    if not JSON_PATH.exists():
        pytest.skip(
            "output/data/manuscript_variables.json missing; "
            "run scripts/manuscript_variables.py first"
        )
    return json.loads(JSON_PATH.read_text())


def test_variables_json_is_well_formed(variables: dict[str, object]) -> None:
    assert isinstance(variables, dict)
    assert variables  # non-empty


@pytest.mark.parametrize("key,lo,hi", [
    ("ising_mi_at_lam_05", 0.0, 0.05),
    ("ising_mi_at_lam_1", 0.05, 0.20),
    ("ising_mi_at_lam_2", 0.20, 0.45),
    ("ising_mi_saturation", 0.69, 0.70),
    ("lambda_star_delta_05", 1.0, 1.2),
    ("lambda_star_delta_09", 2.8, 3.1),
    ("ising_S_E_at_lam_0", -1e-9, 1e-9),
    ("ising_S_E_at_lam_1", 0.0, 0.5),
    ("ising_S_E_at_lam_3", 0.0, 0.7),
    ("ising_schmidt_rank_at_lam_0", 1.0, 1.0),
    ("ising_schmidt_rank_at_lam_1", 2.0, 2.0),
    ("ising_alignment_at_lam_05", 0.0, 0.30),
    ("ising_alignment_at_lam_1", 0.40, 0.55),
    ("ising_alignment_at_lam_2", 0.70, 0.80),
    ("ising_alignment_at_lam_3", 0.85, 0.95),
    ("phase_lambda_c1", 0.5, 0.5),
    ("phase_lambda_c2", 2.5, 2.5),
    ("motor_attention_aligned_prob_lam_0", 0.0, 1.0),
    ("motor_attention_aligned_prob_lam_1", 0.0, 1.0),
    ("motor_attention_aligned_prob_lam_2", 0.0, 1.0),
    ("coupling_tax_curvature_C", 0.0, 1.0),
])
def test_variables_in_range(
    variables: dict[str, object], key: str, lo: float, hi: float
) -> None:
    assert key in variables, f"missing key {key}"
    v = variables[key]
    assert isinstance(v, (int, float)), f"{key} must be numeric, got {type(v).__name__}"
    assert lo <= v <= hi, f"{key} = {v} out of range [{lo}, {hi}]"


@pytest.mark.parametrize("K", [2, 3, 4, 5])
def test_tt_rank_profiles(variables: dict[str, object], K: int) -> None:
    key = f"tt_ranks_K{K}"
    assert key in variables, f"missing {key}"
    profile = variables[key]
    assert isinstance(profile, list)
    assert len(profile) == K - 1
    for r in profile:
        assert isinstance(r, int)
        assert r >= 1
