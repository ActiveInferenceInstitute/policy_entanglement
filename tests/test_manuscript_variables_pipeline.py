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
        pytest.skip("output/data/manuscript_variables.json missing; run scripts/manuscript_variables.py first")
    return json.loads(JSON_PATH.read_text())


def test_variables_json_is_well_formed(variables: dict[str, object]) -> None:
    assert isinstance(variables, dict)
    assert variables  # non-empty


@pytest.mark.parametrize(
    "key,lo,hi",
    [
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
    ],
)
def test_variables_in_range(variables: dict[str, object], key: str, lo: float, hi: float) -> None:
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


# ---------------------------------------------------------------------------
# Round-1 invariants: `_run_all_facts` + Lean declaration arithmetic.
#
# These pin the contract introduced when:
#   * `_run_all_facts()` was added to `scripts/manuscript_variables.py`
#     (exports `run_all_script_count` driven by `scripts.run_all.SCRIPTS`).
#   * The JSON key was renamed `lean_inductive_count` → `lean_structure_count`.
#   * `lean_total_declarations` became a live sum of defs + theorems +
#     structures (no hardcoded total).
# ---------------------------------------------------------------------------


def test_run_all_script_count_present_and_matches_scripts_module(
    variables: dict[str, object],
) -> None:
    """`run_all_script_count` must equal `len(scripts.run_all.SCRIPTS)`.

    Pins the round-1 invariant that `_run_all_facts()` derives the count
    from the source-of-truth `SCRIPTS` list rather than a hand-typed
    integer. If a maintainer adds or removes an entry from `SCRIPTS`,
    the manuscript variable must flow automatically.
    """
    import importlib.util

    assert "run_all_script_count" in variables, (
        "manuscript_variables.json missing `run_all_script_count` — did `_run_all_facts()` get dropped from main()?"
    )
    run_all_path = PROJECT / "scripts" / "run_all.py"
    spec = importlib.util.spec_from_file_location("run_all", run_all_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert variables["run_all_script_count"] == len(mod.SCRIPTS)
    assert "build_pdf.py" not in [script for script, _ in mod.SCRIPTS]
    assert "build_mathlib_proofs.py" not in [script for script, _ in mod.SCRIPTS]
    assert [script for script, _ in mod.PDF_SCRIPTS] == [
        "build_pdf.py",
        "validate_pdf.py",
        "readiness_report.py",
    ]
    assert [script for script, _ in mod.MATHLIB_PROOF_SCRIPTS] == ["build_mathlib_proofs.py"]


def test_lean_structure_count_is_eleven(
    variables: dict[str, object],
) -> None:
    """`lean_structure_count` must be 11 (FloatRealResidualWitness scaffold):
    BoundedQuadraticTax + SmallLambdaTolerance in `Heterogeneous.lean`,
    FreeEnergyConvexityWitness + LocalConcavityAtZero in `Convexity.lean`,
    MarkovBlanketSeparationWitness in `MarkovBlanket.lean`, plus the
    round-3 witnesses UpperSemicontinuousRankWitness + SparsityRankEnvelope
    in `SpectralWitnesses.lean` and HierarchicalConcentrationWitness +
    SophisticatedInferenceEmbedding in `ConnectionsWitnesses.lean`, plus
    the round-5 PythagoreanWitness in `Geometry.lean`, plus
    FloatRealResidualWitness in `FloatRealResidualWitness.lean`.

    Pins the round-1 key rename (`lean_inductive_count` →
    `lean_structure_count`) and locks the count so an accidental
    deletion of one of the witness structures is caught here.
    """
    assert "lean_structure_count" in variables, "manuscript_variables.json missing `lean_structure_count`"
    assert variables["lean_structure_count"] == 11, (
        f"expected 11 structure declarations, got {variables['lean_structure_count']}"
    )


def test_lean_total_declarations_equals_sum_of_components(
    variables: dict[str, object],
) -> None:
    """`lean_total_declarations == lean_def_count + lean_theorem_count
    + lean_structure_count`.

    Pins the round-1 invariant that the total is *derived* live from
    its three components (so bumping any one part keeps the total
    honest), rather than being hand-typed.
    """
    for k in ("lean_def_count", "lean_theorem_count", "lean_structure_count", "lean_total_declarations"):
        assert k in variables, f"manuscript_variables.json missing `{k}`"
    expected = (
        int(variables["lean_def_count"]) + int(variables["lean_theorem_count"]) + int(variables["lean_structure_count"])
    )
    assert variables["lean_total_declarations"] == expected, (
        f"lean_total_declarations={variables['lean_total_declarations']} "
        f"≠ {variables['lean_def_count']} (def) + "
        f"{variables['lean_theorem_count']} (theorem) + "
        f"{variables['lean_structure_count']} (structure) = {expected}"
    )


def test_lean_inductive_count_absent_regression_guard(
    variables: dict[str, object],
) -> None:
    """`lean_inductive_count` must NOT exist (renamed to
    `lean_structure_count` in round 1).

    Regression guard so a future patch that re-introduces the old key
    (e.g. via a stale merge) is caught immediately rather than leaving
    two parallel keys drifting out of sync.
    """
    assert "lean_inductive_count" not in variables, (
        "Old key `lean_inductive_count` reappeared — it was renamed to `lean_structure_count`; remove the legacy entry."
    )
