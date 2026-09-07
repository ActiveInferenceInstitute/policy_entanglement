from __future__ import annotations

import argparse
from typing import Any

from dashboard_types.panel_builders import (
    entropy_decomp_panel,
    fe_curves_panel,
    joint_heatmap_panel,
    mi_curves_panel,
    phase_panel,
    schmidt_panel,
)
from dashboard_types.payload import DashboardPayload
from dashboard_types.paths import DASHBOARD_PROJECT_ROOT
from dashboard_types.types import Invariant
from lean.bernoulli_toy import ising_joint_posterior
from lean.free_energy import kl_divergence, total_correlation
from lean.joint_dist import m_projection
from reporting.interactive_dashboard import InteractiveDashboard


def _payload_view(payload: DashboardPayload | dict[str, Any]) -> DashboardPayload:
    if isinstance(payload, DashboardPayload):
        return payload
    return DashboardPayload(**payload)


def build_dashboard(args: argparse.Namespace, payload: DashboardPayload | dict[str, Any]) -> InteractiveDashboard:
    data = _payload_view(payload)
    d = InteractiveDashboard(
        title="Policy Entanglement — Interactive Simulation Suite",
        subtitle=(
            "Closed-form Ising mirror of the Lean boundary fragment. "
            "All grids, utilities, and phase thresholds are CLI-configurable."
        ),
        project_name="actinf_policy_entanglement_lean",
        repo_root=DASHBOARD_PROJECT_ROOT,
    )

    d.set_hyperparameters(
        {
            "lam_min": args.lam_min,
            "lam_max": args.lam_max,
            "num": args.num,
            "utilities": list(args.utilities),
            "lam_c1": args.lam_c1,
            "lam_c2": args.lam_c2,
            "schmidt_atol": args.schmidt_atol,
            "probe_lambdas": list(args.probe_lambdas),
        }
    )
    d.set_payload(data.to_dict())
    d.add_note(
        "All numerical values are computed live from `src/lean/` analytical "
        "mirrors of the Lean 4 boundary fragment (no pymdp dependency)."
    )
    d.add_note(
        "Dashboard payload is mirrored to `output/data/dashboard_payload.json`; "
        "invariants to `output/reports/dashboard_invariants.txt`."
    )

    d.add_slider(
        control_id="lam_probe",
        label="λ (joint-heatmap probe)",
        min=args.lam_min,
        max=args.lam_max,
        step=(args.lam_max - args.lam_min) / max(args.num - 1, 1),
        default=(args.lam_min + args.lam_max) / 2.0,
        description="moves the joint heatmap and TC pointer",
    )
    d.add_slider(
        control_id="utility",
        label="utility surplus u",
        min=0.0,
        max=4.0,
        step=0.05,
        default=1.0,
        description="re-evaluates the F(λ; u) curve live",
    )
    d.add_dropdown(
        control_id="phase_view",
        label="phase classifier",
        options=["lambdas", "phases"],
        default="lambdas",
        option_labels=["λ axis (numeric)", "phase classifier (categorical)"],
        description="x-axis basis for the rank/entropy panel",
    )

    for panel in (
        mi_curves_panel(data),
        fe_curves_panel(data),
        entropy_decomp_panel(args, data),
        joint_heatmap_panel(data),
        schmidt_panel(data),
        phase_panel(args, data),
    ):
        d.add_panel(panel)

    from lean.invariants import SweepGrid, all_invariants

    grid = SweepGrid(args.lam_min, args.lam_max, args.num)
    for inv in all_invariants(
        grid,
        utilities=tuple(args.utilities),
        lam_c1=args.lam_c1,
        lam_c2=args.lam_c2,
    ):
        d.add_invariant(inv)

    revert_residuals: list[float] = []
    for lam in args.probe_lambdas:
        q = ising_joint_posterior(float(lam))
        kl_val = kl_divergence(q, m_projection(q))
        I_val = total_correlation(q)  # noqa: N806 — I = multi-information (manuscript symbol).
        revert_residuals.append(float(abs(kl_val - I_val)))
    d.add_invariant(
        Invariant(
            name="revertibility_kl_equals_multiinformation",
            actual=float(max(revert_residuals)) if revert_residuals else 0.0,
            expected=0.0,
            tol=1e-9,
            kind="equal",
            description=(
                "For every probe λ on the dashboard grid: "
                "max |KL(q_λ ‖ m(q_λ)) − I(q_λ)| ≤ 1e-9 — Prop 7.3 / "
                "Theorem 5.1 numerical witness on the K=2 Ising joint."
            ),
        )
    )

    head_n = min(15, len(data.lambdas))
    d.add_table(
        "first_15_rows",
        [
            {
                "lambda": data.lambdas[i],
                "mi_closed": data.mi_closed[i],
                "mi_empirical": data.mi_empirical[i],
                "mi_residual": data.mi_residual[i],
                "tc": data.tc[i],
                "phase": data.phases[i],
            }
            for i in range(head_n)
        ],
    )

    return d


__all__ = ["build_dashboard"]
