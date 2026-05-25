"""Tests for :mod:`simulation.pymdp_pipeline` CLI override layer."""

from __future__ import annotations

import argparse

import pytest

from simulation import hyperparameters as H
from simulation.pymdp_pipeline import apply_overrides, parse_args


def test_parse_args_defaults_match_hyperparameters() -> None:
    args = parse_args([])
    assert args.ensemble_K == int(H.PYMDP_ENSEMBLE_K)
    assert args.gamma == pytest.approx(float(H.PYMDP_ENSEMBLE_GAMMA))
    assert args.sweep_num == int(H.PYMDP_SWEEP_LAMBDAS.num)
    assert list(args.observations) == list(H.PYMDP_SWEEP_OBSERVATIONS)


def test_parse_args_custom_overrides() -> None:
    args = parse_args(
        [
            "--ensemble-K",
            "3",
            "--observations",
            "0",
            "1",
            "0",
            "--sweep-num",
            "5",
            "--sweep-lambda-min",
            "0",
            "--sweep-lambda-max",
            "2",
        ]
    )
    assert args.ensemble_K == 3
    assert args.sweep_num == 5
    assert args.sweep_lambda_max == pytest.approx(2.0)


@pytest.mark.parametrize(
    "argv,fragment",
    [
        (["--ensemble-K", "1"], "ensemble-K"),
        (["--sweep-num", "1"], "sweep-num"),
        (["--sweep-lambda-min", "2", "--sweep-lambda-max", "1"], "sweep-lambda-max"),
        (["--rollout-steps", "0"], "rollout-steps"),
        (["--ensemble-K", "2", "--observations", "0"], "observations length"),
    ],
)
def test_parse_args_rejects_invalid_grid(argv: list[str], fragment: str) -> None:
    with pytest.raises(SystemExit):
        parse_args(argv)


def test_apply_overrides_patches_hyperparameters() -> None:
    snapshot = {
        "PYMDP_ENSEMBLE_K": int(H.PYMDP_ENSEMBLE_K),
        "PYMDP_ENSEMBLE_GAMMA": float(H.PYMDP_ENSEMBLE_GAMMA),
        "PYMDP_ENSEMBLE_COUPLING_LAMBDA": float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        "PYMDP_ROLLOUT_STEPS": int(H.PYMDP_ROLLOUT_STEPS),
        "PYMDP_ROLLOUT_LAMBDA": float(H.PYMDP_ROLLOUT_LAMBDA),
        "PYMDP_ROLLOUT_SEED": int(H.PYMDP_ROLLOUT_SEED),
        "PYMDP_SWEEP_OBSERVATIONS": tuple(H.PYMDP_SWEEP_OBSERVATIONS),
        "FIGURE_GLOBAL_SEED": int(H.FIGURE_GLOBAL_SEED),
        "PYMDP_SWEEP_LAMBDAS": H.PYMDP_SWEEP_LAMBDAS,
    }
    args = argparse.Namespace(
        ensemble_K=3,
        gamma=1.5,
        coupling_lambda=2.0,
        sweep_lambda_min=0.0,
        sweep_lambda_max=3.0,
        sweep_num=7,
        rollout_steps=16,
        rollout_lambda=1.25,
        rollout_seed=42,
        observations=[0, 1, 0],
        figure_seed=99,
    )
    try:
        apply_overrides(args)
        assert int(H.PYMDP_ENSEMBLE_K) == 3
        assert float(H.PYMDP_ENSEMBLE_GAMMA) == pytest.approx(1.5)
        assert int(H.PYMDP_SWEEP_LAMBDAS.num) == 7
        assert int(H.FIGURE_GLOBAL_SEED) == 99
        assert tuple(H.PYMDP_SWEEP_OBSERVATIONS) == (0, 1, 0)
    finally:
        H.PYMDP_ENSEMBLE_K = snapshot["PYMDP_ENSEMBLE_K"]
        H.PYMDP_ENSEMBLE_GAMMA = snapshot["PYMDP_ENSEMBLE_GAMMA"]
        H.PYMDP_ENSEMBLE_COUPLING_LAMBDA = snapshot["PYMDP_ENSEMBLE_COUPLING_LAMBDA"]
        H.PYMDP_ROLLOUT_STEPS = snapshot["PYMDP_ROLLOUT_STEPS"]
        H.PYMDP_ROLLOUT_LAMBDA = snapshot["PYMDP_ROLLOUT_LAMBDA"]
        H.PYMDP_ROLLOUT_SEED = snapshot["PYMDP_ROLLOUT_SEED"]
        H.PYMDP_SWEEP_OBSERVATIONS = snapshot["PYMDP_SWEEP_OBSERVATIONS"]
        H.FIGURE_GLOBAL_SEED = snapshot["FIGURE_GLOBAL_SEED"]
        H.PYMDP_SWEEP_LAMBDAS = snapshot["PYMDP_SWEEP_LAMBDAS"]
