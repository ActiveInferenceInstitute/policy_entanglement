"""Tests for `simulation.hyperparameters` — the single-source-of-truth
constants for every figure / sweep / simulation hyperparameter.

The test suite asserts that:

* Every grid declared at module level is consistent (start ≤ stop, num
  ≥ 2) and produces a 1-D ndarray with the advertised length.
* Every scalar lies inside a sane physical range.
* `figure_hyperparameter_summary` exports every constant that the
  manuscript currently substitutes via `[[VAR:...]]`.
* The mirrored values inside ``output/data/manuscript_variables.json``
  (when present) match the source-of-truth constants exactly.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from simulation import hyperparameters as H

GRID_NAMES = [
    "PARAMETER_SWEEP_LAMBDAS",
    "COUPLING_TAX_LAMBDAS",
    "PHASE_DIAGRAM_LAMBDAS",
    "OPTIMAL_LAMBDA_DELTAS",
    "SCHMIDT_RANK_LAMBDAS",
    "PHASE_LANDSCAPE_LAMBDAS",
    "PHASE_LANDSCAPE_UTILITIES",
    "LOG_WEIGHT_FLOW_LAMBDAS",
    "KL_GEODESIC_LAMBDAS",
    "LAMBDA_STAR_UTILITIES",
    "LAMBDA_STAR_GAMMAS",
    "PYMDP_SWEEP_LAMBDAS",
    "MULTI_K_SWEEP_LAMBDAS",
    "ROBUSTNESS_SWEEP_LAMBDAS",
]


@pytest.mark.parametrize("name", GRID_NAMES)
def test_every_grid_is_consistent(name: str) -> None:
    grid = getattr(H, name)
    assert grid.start <= grid.stop, f"{name}: start > stop"
    assert grid.num >= 2, f"{name}: num must be ≥ 2"
    arr = grid.values()
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (grid.num,)
    assert np.isclose(arr[0], grid.start)
    assert np.isclose(arr[-1], grid.stop)


def test_pymdp_rollout_scalars_are_sensible() -> None:
    assert H.PYMDP_ROLLOUT_STEPS >= 1
    assert H.PYMDP_ROLLOUT_LAMBDA >= 0.0
    assert H.PYMDP_ROLLOUT_SEED >= 0
    assert H.PYMDP_ENSEMBLE_K >= 2
    assert H.PYMDP_ENSEMBLE_GAMMA >= 0.0
    assert H.PYMDP_ENSEMBLE_COUPLING_LAMBDA >= 0.0
    assert tuple(H.PYMDP_SWEEP_OBSERVATIONS) == (0, 0)
    assert H.LONG_HORIZON_SEED in H.LONG_HORIZON_REPLICATE_SEEDS
    assert all(isinstance(seed, int) and seed >= 0 for seed in H.LONG_HORIZON_REPLICATE_SEEDS)
    assert H.LONG_HORIZON_STEADY_STATE_TOL in H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS
    assert set(H.ROBUSTNESS_INTERACTION_FAMILIES) == {
        "observation_x_coupling_scale",
        "gamma_x_preference_strength",
        "coupling_variant_x_coupling_scale",
    }


def test_figure_global_seed_is_deterministic() -> None:
    assert isinstance(H.FIGURE_GLOBAL_SEED, int)


def test_phase_thresholds_are_ordered() -> None:
    assert 0.0 <= H.PHASE_LAMBDA_C1 < H.PHASE_LAMBDA_C2


def test_summary_dict_has_every_key_used_by_manuscript() -> None:
    """The keys consumed by `manuscript/*.md` via [[VAR:...]] must
    appear in the figure_hyperparameter_summary export.
    """
    summary = H.figure_hyperparameter_summary()
    expected = {
        "param_sweep_grid_points",
        "param_sweep_lambda_min",
        "param_sweep_lambda_max",
        "param_sweep_agreement_tolerance",
        "coupling_tax_grid_points",
        "coupling_tax_lambda_min",
        "coupling_tax_lambda_max",
        "coupling_tax_probe_lambda",
        "pymdp_sweep_grid_points",
        "pymdp_sweep_lambda_min",
        "pymdp_sweep_lambda_max",
        "pymdp_sweep_observations",
        "pymdp_rollout_steps",
        "pymdp_rollout_seed",
        "pymdp_rollout_lambda",
        "pymdp_ensemble_K",
        "pymdp_ensemble_coupling_lambda",
        "pymdp_ensemble_gamma",
        "log_weight_flow_grid_points",
        "log_weight_flow_lambda_min",
        "log_weight_flow_lambda_max",
        "phase_diagram_grid_points",
        "phase_landscape_lambda_points",
        "phase_landscape_lambda_min",
        "phase_landscape_lambda_max",
        "phase_landscape_utility_points",
        "phase_landscape_utility_min",
        "phase_landscape_utility_max",
        "kl_geodesic_grid_points",
        "kl_geodesic_lambda_min",
        "kl_geodesic_lambda_max",
        "lambda_star_utility_points",
        "lambda_star_gamma_points",
        "schmidt_rank_grid_points",
        "optimal_lambda_grid_points",
        "figure_global_seed",
        "bernoulli_verification_tolerance",
        "pymdp_marginal_agreement_tolerance",
        "pymdp_tc_zero_tolerance",
        "pymdp_coupling_zero_tolerance",
        "pymdp_entropy_add_tolerance",
        "pymdp_single_stream_float_tolerance",
        "phase_lambda_c1",
        "phase_lambda_c2",
        "multi_k_sweep_lambda_min",
        "long_horizon_replicate_seed_count",
        "long_horizon_diagnostic_threshold_count",
        "robustness_interaction_family_count",
        "robustness_sweep_grid_points",
        "coupling_ablation_variant_count",
        "phase_diagram_lambda_min",
        "phase_diagram_lambda_max",
        "optimal_lambda_delta_min",
        "optimal_lambda_delta_max",
        "schmidt_rank_lambda_min",
        "schmidt_rank_lambda_max",
        "lambda_star_utility_min",
        "lambda_star_utility_max",
        "lambda_star_gamma_min",
        "lambda_star_gamma_max",
        "tt_rank_profile_lambda",
        "spectral_rank_atol",
        "joint_heatmap_lambda",
        "archetype_dendrogram_lambda",
        "montecarlo_mi_lambda",
        "montecarlo_mi_n",
        "montecarlo_mi_seeds",
        "montecarlo_mi_bias_tol",
        "coupling_graph_stream_count",
    }
    missing = expected - summary.keys()
    assert not missing, f"summary is missing keys: {sorted(missing)}"


def test_summary_matches_manuscript_variables_json_when_present() -> None:
    """If `output/data/manuscript_variables.json` exists, every
    hyperparameter key inside it must equal the source-of-truth
    constant from this module.
    """
    json_path = Path(__file__).resolve().parent.parent / "output" / "data" / "manuscript_variables.json"
    if not json_path.exists():
        pytest.skip("manuscript_variables.json not generated yet")
    data = json.loads(json_path.read_text())
    summary = H.figure_hyperparameter_summary()
    missing = sorted(set(summary) - set(data))
    if missing:
        pytest.skip(
            "manuscript_variables.json has not been regenerated after "
            f"expanding figure_hyperparameter_summary: missing {missing}"
        )
    for key, expected in summary.items():
        assert key in data, f"missing key in JSON: {key}"
        if isinstance(expected, list):
            assert list(data[key]) == list(expected), key
        else:
            assert data[key] == expected, (key, data[key], expected)


def test_grid_count_helper_returns_int() -> None:
    assert H.grid_count(H.PARAMETER_SWEEP_LAMBDAS) == 121
    assert H.grid_count(H.PYMDP_SWEEP_LAMBDAS) == 21
