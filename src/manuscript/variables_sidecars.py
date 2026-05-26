"""Sidecar JSON and pymdp-grounded manuscript-variable producers."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path

import numpy as np

from simulation import hyperparameters as H  # noqa: N812

SCALAR_SIDECAR_SENTINEL_RE = re.compile(
    r"^\s*(not[-_]run|not[-_]installed|import[-_]failed|invalid[-_][a-z]+|not[-_]present)\s*$",
    re.IGNORECASE,
)

SidecarReader = Callable[[Path, str], dict[str, object]]


def scalar_json_sidecar(path: Path, sentinel_key: str) -> dict[str, object]:
    if not path.exists():
        return {sentinel_key: "not-run"}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {sentinel_key: "invalid-json"}
    if not isinstance(data, dict):
        return {sentinel_key: "invalid-payload"}
    out: dict[str, object] = {}
    for key, value in data.items():
        if isinstance(value, bool):
            out[str(key)] = value
            continue
        if isinstance(value, (int, float)):
            out[str(key)] = float(value)
            continue
        if isinstance(value, str) and SCALAR_SIDECAR_SENTINEL_RE.match(value):
            out[str(key)] = value
    return out


def numeric_only_json_sidecar(path: Path, sentinel_key: str) -> dict[str, object]:
    if not path.exists():
        return {sentinel_key: "not-run"}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {sentinel_key: "invalid-json"}
    if not isinstance(data, dict):
        return {sentinel_key: "invalid-payload"}
    out: dict[str, object] = {}
    for k, v in data.items():
        try:
            out[str(k)] = float(v)
        except (TypeError, ValueError):
            out[str(k)] = v
    return out


JSON_SIDECAR_REGISTRY: tuple[tuple[str, str, SidecarReader], ...] = (
    ("multi_k", "output/data/multi_k_summary.json", numeric_only_json_sidecar),
    ("long_horizon", "output/data/long_horizon_summary.json", numeric_only_json_sidecar),
    ("revertibility", "output/data/revertibility_summary.json", numeric_only_json_sidecar),
    ("robustness", "output/data/robustness_summary.json", scalar_json_sidecar),
    ("coupling_ablation", "output/data/coupling_ablation_summary.json", scalar_json_sidecar),
    ("marginal_null_control", "output/data/marginal_null_control_summary.json", scalar_json_sidecar),
    ("long_horizon_replicates", "output/data/long_horizon_replicates_summary.json", scalar_json_sidecar),
    ("interaction_robustness", "output/data/interaction_robustness_summary.json", scalar_json_sidecar),
    ("btai", "output/data/btai_baseline.json", scalar_json_sidecar),
    ("adversarial", "output/data/adversarial_sweep.json", scalar_json_sidecar),
)


def json_sidecar_facts(project_root: Path) -> dict[str, object]:
    facts: dict[str, object] = {}
    for sentinel_key, rel_path, reader in JSON_SIDECAR_REGISTRY:
        facts.update(reader(project_root / rel_path, sentinel_key))
    return facts


def pymdp_facts() -> dict[str, float] | dict[str, str]:
    try:
        from simulation.agents import pymdp_available
    except Exception:  # pragma: no cover - import shape only
        return {"pymdp": "import-failed"}
    if not pymdp_available():
        return {"pymdp": "not-installed"}

    from lean.free_energy import total_correlation
    from simulation.builders import make_ising_ensemble
    from simulation.inference import (
        coupled_policy_posterior,
        decomposition_witness_curve,
        free_energy_curve,
    )
    from simulation.statistics import pymdp_summary_statistics, summary_to_var_dict

    spec = make_ising_ensemble(
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        coupling_amplitude=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
    )
    facts: dict[str, float] = {}
    for lam in H.PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS:
        q = coupled_policy_posterior(
            spec,
            observations=list(H.PYMDP_SWEEP_OBSERVATIONS),
            lam=float(lam),
        )
        facts[f"pymdp_total_correlation_lam_{lam:g}".replace(".", "_")] = float(total_correlation(q))

    bundles = free_energy_curve(
        spec,
        observations=list(H.PYMDP_SWEEP_OBSERVATIONS),
        lams=H.PYMDP_SWEEP_LAMBDAS.values(),
    )
    summary = pymdp_summary_statistics(bundles)
    facts.update(summary_to_var_dict(summary))
    witnesses = decomposition_witness_curve(
        spec,
        observations=list(H.PYMDP_SWEEP_OBSERVATIONS),
        lams=H.PYMDP_SWEEP_LAMBDAS.values(),
    )
    facts["pymdp_decomposition_residual_max"] = float(max(w.residual for w in witnesses))
    facts["pymdp_decomposition_residual_mean"] = float(np.mean([w.residual for w in witnesses]))
    zero_bundle = min(bundles, key=lambda b: abs(float(b.lam)))
    facts["pymdp_coupling_term_at_lambda_zero"] = float(zero_bundle.coupling_term)
    facts["pymdp_joint_entropy_at_lambda_zero"] = float(zero_bundle.joint_entropy)
    facts["pymdp_marginal_entropy_sum_at_lambda_zero"] = float(zero_bundle.marginal_entropies.sum())
    return facts


def gnn_facts(project_root: Path) -> dict[str, object]:
    path = project_root / "output" / "data" / "gnn_bernoulli_roundtrip.json"
    if not path.exists():
        return {"gnn": "not-run"}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"gnn": "invalid-json"}
    if not isinstance(data, dict):
        return {"gnn": "invalid-payload"}
    grid = data.get("lambda_grid", {})
    return {
        "gnn_roundtrip_max_residual": float(data["max_abs_residual"]),
        "gnn_negative_control_max_residual": float(data["negative_control_zero_coupling_max_residual"]),
        "gnn_round_trip_lambda_points": float(grid.get("num", 0)),
        "gnn_num_streams": float(data["num_streams"]),
    }


def hyperparameter_facts() -> dict[str, object]:
    return H.figure_hyperparameter_summary()


__all__ = [
    "JSON_SIDECAR_REGISTRY",
    "SCALAR_SIDECAR_SENTINEL_RE",
    "gnn_facts",
    "hyperparameter_facts",
    "json_sidecar_facts",
    "numeric_only_json_sidecar",
    "pymdp_facts",
    "scalar_json_sidecar",
]
