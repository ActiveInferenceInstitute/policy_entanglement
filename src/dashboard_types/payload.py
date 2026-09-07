from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

import numpy as np

from dashboard_types.paths import DASHBOARD_PROJECT_ROOT  # noqa: F401 — re-export contract for tests

_FE_SLIDER_STEP = 0.05
_FE_SLIDER_MAX = 4.0


@dataclass(frozen=True)
class DashboardPayload:
    """Precomputed dashboard series consumed by panel builders and JSON export."""

    lambdas: list[float]
    mi_closed: list[float]
    mi_empirical: list[float]
    mi_residual: list[float]
    fe_curves: dict[str, list[float]]
    fe_slider_grid: dict[str, list[float]]
    H_joint: list[float]
    H_marg_0: list[float]
    H_marg_1: list[float]
    tc: list[float]
    schmidt_rank: list[int]
    entanglement_entropy: list[float]
    phases: list[str]
    joint_snapshots: dict[str, list[list[float]]]
    joint_grid: list[list[list[float]]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "lambdas": self.lambdas,
            "mi_closed": self.mi_closed,
            "mi_empirical": self.mi_empirical,
            "mi_residual": self.mi_residual,
            "fe_curves": self.fe_curves,
            "fe_slider_grid": self.fe_slider_grid,
            "H_joint": self.H_joint,
            "H_marg_0": self.H_marg_0,
            "H_marg_1": self.H_marg_1,
            "tc": self.tc,
            "schmidt_rank": self.schmidt_rank,
            "entanglement_entropy": self.entanglement_entropy,
            "phases": self.phases,
            "joint_snapshots": self.joint_snapshots,
            "joint_grid": self.joint_grid,
        }

    def __contains__(self, key: str) -> bool:
        return key in self.to_dict()

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


def build_dashboard_payload(args: argparse.Namespace) -> DashboardPayload:
    from lean.bernoulli_toy import (
        coupling_phase_at,
        empirical_mutual_information,
        ising_free_energy_curve,
        ising_joint_posterior,
        ising_mutual_information,
    )
    from lean.free_energy import joint_entropy, marginal_entropy
    from lean.spectral import entanglement_entropy, schmidt_rank

    lams = np.linspace(args.lam_min, args.lam_max, args.num).tolist()

    closed = [ising_mutual_information(lam) for lam in lams]
    empirical = [empirical_mutual_information(lam) for lam in lams]
    residual = [c - e for c, e in zip(closed, empirical, strict=True)]

    fe_curves = {
        f"u={u:g}": [ising_free_energy_curve(lam, float(u)) for lam in lams] for u in args.utilities
    }
    slider_utilities = np.arange(0.0, _FE_SLIDER_MAX + _FE_SLIDER_STEP / 2, _FE_SLIDER_STEP)
    fe_slider_grid = {
        f"{float(u):.2f}": [ising_free_energy_curve(lam, float(u)) for lam in lams]
        for u in slider_utilities
    }

    H_joint: list[float] = []  # noqa: N806 — H = entropy (manuscript symbol).
    H_marg_0: list[float] = []  # noqa: N806
    H_marg_1: list[float] = []  # noqa: N806
    sr: list[int] = []
    ent_ent: list[float] = []
    phases: list[str] = []
    joint_grid: list[list[list[float]]] = []
    for lam in lams:
        q = ising_joint_posterior(lam)
        joint_grid.append(q.tolist())
        H_joint.append(joint_entropy(q))
        H_marg_0.append(marginal_entropy(q, 0))
        H_marg_1.append(marginal_entropy(q, 1))
        sr.append(int(schmidt_rank(q, atol=args.schmidt_atol)))
        ent_ent.append(entanglement_entropy(q))
        phases.append(coupling_phase_at(lam, lam_c1=args.lam_c1, lam_c2=args.lam_c2))

    tc = [m0 + m1 - hj for m0, m1, hj in zip(H_marg_0, H_marg_1, H_joint, strict=True)]

    snapshots: dict[str, list[list[float]]] = {}
    for lam in args.probe_lambdas:
        q = ising_joint_posterior(float(lam))
        snapshots[f"{float(lam):.4f}"] = q.tolist()

    return DashboardPayload(
        lambdas=lams,
        mi_closed=closed,
        mi_empirical=empirical,
        mi_residual=residual,
        fe_curves=fe_curves,
        fe_slider_grid=fe_slider_grid,
        H_joint=H_joint,
        H_marg_0=H_marg_0,
        H_marg_1=H_marg_1,
        tc=tc,
        schmidt_rank=sr,
        entanglement_entropy=ent_ent,
        phases=phases,
        joint_snapshots=snapshots,
        joint_grid=joint_grid,
    )


__all__ = ["DashboardPayload", "build_dashboard_payload"]
