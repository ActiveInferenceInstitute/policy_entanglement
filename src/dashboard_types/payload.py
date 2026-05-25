from __future__ import annotations

import argparse
from typing import Any

from dashboard_types.paths import DASHBOARD_PROJECT_ROOT  # noqa: F401 — re-export contract for tests


def build_dashboard_payload(args: argparse.Namespace) -> dict[str, Any]:
    import numpy as np

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

    fe_curves = {f"u={u:g}": [ising_free_energy_curve(lam, float(u)) for lam in lams] for u in args.utilities}

    H_joint: list[float] = []  # noqa: N806 — H = entropy (manuscript symbol).
    H_marg_0: list[float] = []  # noqa: N806
    H_marg_1: list[float] = []  # noqa: N806
    sr: list[int] = []
    ent_ent: list[float] = []
    phases: list[str] = []
    for lam in lams:
        q = ising_joint_posterior(lam)
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

    return {
        "lambdas": lams,
        "mi_closed": closed,
        "mi_empirical": empirical,
        "mi_residual": residual,
        "fe_curves": fe_curves,
        "H_joint": H_joint,
        "H_marg_0": H_marg_0,
        "H_marg_1": H_marg_1,
        "tc": tc,
        "schmidt_rank": sr,
        "entanglement_entropy": ent_ent,
        "phases": phases,
        "joint_snapshots": snapshots,
    }


__all__ = ["build_dashboard_payload"]
