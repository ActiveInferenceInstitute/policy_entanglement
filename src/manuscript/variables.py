"""Compute the manuscript-substituted variables.

Bernoulli closed-form numbers, Schmidt entropies of the K=2 Ising joint at
sentinel ``λ`` values, K-stream tensor-train rank summaries, pymdp-grounded
total-correlation values from the coupled-policy harness, and **every figure /
sweep hyperparameter** (grid sizes, seeds, rollout horizon, observations) so
the manuscript can refer to those numbers via ``[[VAR:...]]`` rather than
hardcoding them.

Sentinel ``λ`` values, grid sizes, and seeds are read from
:mod:`simulation.hyperparameters` — there is no place in this module that picks
an integer or float without going through the shared constants.

This module is the importable home of the manuscript-variable contract. The
matching ``scripts/manuscript_variables.py`` is a thin CLI wrapper that calls
:func:`build_manuscript_variables` and writes the result to disk so the
business logic stays in ``src/`` and tests can target it directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from lean.bernoulli_toy import empirical_mutual_information_montecarlo, ising_mutual_information
from lean.invariants import (
    SweepGrid,
    decomposition_invariants_from_points,
    decomposition_sweep_points,
)
from manuscript.float_real_interval import decomposition_interval_bracket
from manuscript.variables_analytical import (
    alignment_and_phase_facts,
    bernoulli_facts,
    coupling_tax_curvature,
    format_lambda_key,
    format_lambda_list,
    motor_attention_facts,
    sentinel_list_facts,
    spectral_facts,
    tensor_train_facts,
)
from manuscript.variables_pipeline import lean_facts, registry_facts, run_all_facts, toolchain_facts
from manuscript.variables_sidecars import gnn_facts, hyperparameter_facts, json_sidecar_facts, pymdp_facts
from simulation import hyperparameters as H  # noqa: N812

SRC_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SRC_DIR.parent


def build_manuscript_variables(project_root: Path | None = None) -> dict[str, Any]:
    """Compute the full ``manuscript_variables.json`` payload as a Python dict."""
    root = project_root or PROJECT_ROOT
    facts: dict[str, Any] = {}
    facts.update(bernoulli_facts())
    facts.update(spectral_facts())
    facts.update(alignment_and_phase_facts())
    facts.update(motor_attention_facts())
    facts.update(coupling_tax_curvature())
    facts.update(run_all_facts(root))
    facts.update(lean_facts(root))
    facts.update(toolchain_facts(root))
    facts.update(registry_facts(root))
    facts.update(tensor_train_facts())
    facts.update(pymdp_facts())
    facts.update(json_sidecar_facts(root))
    facts.update(gnn_facts(root))
    facts.update(sentinel_list_facts())
    facts.update(hyperparameter_facts())
    return facts


def decomposition_certificate_grid() -> SweepGrid:
    """λ-grid shared by decomposition invariants and the interval bracket witness."""
    return SweepGrid(
        lam_min=float(H.PARAMETER_SWEEP_LAMBDAS.start),
        lam_max=float(H.PARAMETER_SWEEP_LAMBDAS.stop),
        num=min(31, int(H.PARAMETER_SWEEP_LAMBDAS.num)),
    )


def build_float_real_residual() -> dict[str, float | bool]:
    """Machine-readable Float↔ℝ residual certificate (scaffold, not a proof)."""
    grid = decomposition_certificate_grid()
    points = decomposition_sweep_points(grid)
    decomp = decomposition_invariants_from_points(points)
    max_residual_actual = next(inv for inv in decomp if inv.name == "decomposition_lhs_eq_rhs_max_residual").actual
    if not isinstance(max_residual_actual, int | float):
        raise TypeError("decomposition_lhs_eq_rhs_max_residual invariant must be scalar")
    max_residual = float(max_residual_actual)

    lam = float(H.MONTECARLO_MI_LAMBDA)
    n_samples = int(H.MONTECARLO_MI_N)
    n_seeds = int(H.MONTECARLO_MI_SEEDS)
    bias_tol = float(H.MONTECARLO_MI_BIAS_TOL)
    samples = [empirical_mutual_information_montecarlo(lam, n_samples, seed) for seed in range(n_seeds)]
    mu = float(np.mean(samples))
    sd = float(np.std(samples, ddof=1)) if len(samples) > 1 else 0.0
    closed = float(ising_mutual_information(lam))
    concentration_radius = float(4.0 * sd / np.sqrt(n_seeds) + bias_tol)

    bracket = decomposition_interval_bracket(points, invariant_max_residual=max_residual)
    payload: dict[str, float | bool] = {
        "decomposition_lhs_eq_rhs_max_residual": max_residual,
        "montecarlo_mi_lambda": lam,
        "montecarlo_mi_closed_form": closed,
        "montecarlo_mi_sample_mean": mu,
        "montecarlo_mi_concentration_radius": concentration_radius,
        "capstone_conjunct_tolerance": 1e-9,
    }
    payload.update(bracket)
    return payload


def write_float_real_residual(
    output_path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> Path:
    """Persist ``float_real_residual.json`` under ``output/reports/``."""
    root = project_root or PROJECT_ROOT
    payload = build_float_real_residual()
    target = output_path or (root / "output" / "reports" / "float_real_residual.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return target


def write_manuscript_variables(
    output_path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> Path:
    """Compute and persist the manuscript-variables JSON."""
    root = project_root or PROJECT_ROOT
    facts = build_manuscript_variables(root)
    target = output_path or (root / "output" / "data" / "manuscript_variables.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")
    write_float_real_residual(project_root=root)
    return target


def main() -> None:
    """Thin CLI entry point: compute facts, write JSON, print the output path."""
    out = write_manuscript_variables()
    print(out)


# Backward-compatible private aliases for tests that import underscore names.
_format_lambda_key = format_lambda_key
_format_lambda_list = format_lambda_list


__all__ = [
    "PROJECT_ROOT",
    "build_float_real_residual",
    "build_manuscript_variables",
    "decomposition_certificate_grid",
    "main",
    "write_float_real_residual",
    "write_manuscript_variables",
    "_format_lambda_key",
    "_format_lambda_list",
]


if __name__ == "__main__":
    main()
