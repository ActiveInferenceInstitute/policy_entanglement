"""One builder per dashboard panel."""

from __future__ import annotations

import argparse

from dashboard_types.payload import DashboardPayload
from dashboard_types.plotly_traces import axis_layout, heatmap, scatter_line, scatter_markers
from dashboard_types.types import Panel

_PALETTE = ["#38bdf8", "#fb923c", "#a78bfa", "#22c55e", "#ef4444", "#facc15"]
_PHASE_COLORS = {"disordered": "#22c55e", "mixed": "#facc15", "frozen": "#ef4444"}
_PHASE_ORDINAL = {"disordered": 0, "mixed": 1, "frozen": 2}


def mi_curves_panel(payload: DashboardPayload) -> Panel:
    return Panel(
        panel_id="mi_curves",
        title="Mutual information: closed-form vs empirical",
        description=(
            "Closed-form I(λ) = log 2 − H_b(σ(λ)) (orange) overlaid with the "
            "empirical total correlation of the λ-entangled joint (blue). "
            "Residual is plotted on the secondary axis."
        ),
        traces=[
            scatter_line(
                name="closed-form I(λ)",
                x=payload.lambdas,
                y=payload.mi_closed,
                color="#fb923c",
            ),
            scatter_line(
                name="empirical TC(q_λ)",
                x=payload.lambdas,
                y=payload.mi_empirical,
                color="#38bdf8",
                dash="dash",
            ),
            scatter_line(
                name="residual (×1e9)",
                x=payload.lambdas,
                y=[r * 1e9 for r in payload.mi_residual],
                color="#94a3b8",
                yaxis="y2",
            ),
        ],
        layout={
            **axis_layout(x_title="λ", y_title="MI / TC (nats)"),
            "yaxis2": {
                "title": "residual ×1e-9",
                "overlaying": "y",
                "side": "right",
                "showgrid": False,
            },
        },
    )


def fe_curves_panel(payload: DashboardPayload) -> Panel:
    traces = [
        scatter_line(
            name=f"F(λ; {label})",
            x=payload.lambdas,
            y=vals,
            color=_PALETTE[i % len(_PALETTE)],
        )
        for i, (label, vals) in enumerate(payload.fe_curves.items())
    ]
    first_curve = next(iter(payload.fe_curves.values()))
    traces.append(
        scatter_line(
            name="F(λ; u=slider)",
            x=payload.lambdas,
            y=first_curve,
            color="#f5f5f5",
            dash="dot",
            width=3,
        )
    )
    return Panel(
        panel_id="fe_curves",
        title="Free-energy curves F(λ; u)",
        description=(
            "Each curve is monotone-decreasing in |λ| for u ≥ 0 "
            "(invariant: free_energy_monotone_decreasing_u={...}). "
            "Move the utility slider to redraw the live trace."
        ),
        traces=traces,
        layout=axis_layout(x_title="λ", y_title="F(λ; u)"),
        driven_by=["utility"],
        update_fn=r"""
const u = controls.utility;
const bucket = (Math.round(u / 0.05) * 0.05).toFixed(2);
const fe = payload.fe_slider_grid[bucket];
const liveIdx = Object.keys(payload.fe_curves).length;
Plotly.restyle(panelId, {y: [fe], name: ['F(λ; u=' + u.toFixed(2) + ')']}, [liveIdx]);
""",
    )


def entropy_decomp_panel(args: argparse.Namespace, payload: DashboardPayload) -> Panel:
    default_lam = (args.lam_min + args.lam_max) / 2.0
    return Panel(
        panel_id="entropy_decomp",
        title="Entropy decomposition: H(q^k), H(q), TC",
        description=(
            "TC(q_λ) = Σ_k H(q^k) − H(q) ≥ 0, equals zero iff q is mean-field. Vertical line tracks the slider λ."
        ),
        traces=[
            scatter_line(name="H(q^0)", x=payload.lambdas, y=payload.H_marg_0, color="#38bdf8"),
            scatter_line(name="H(q^1)", x=payload.lambdas, y=payload.H_marg_1, color="#fb923c"),
            scatter_line(name="H(q)", x=payload.lambdas, y=payload.H_joint, color="#a78bfa"),
            scatter_line(name="TC", x=payload.lambdas, y=payload.tc, color="#22c55e", dash="dash"),
        ],
        layout={
            **axis_layout(x_title="λ", y_title="entropy (nats)"),
            "shapes": [
                {
                    "type": "line",
                    "x0": default_lam,
                    "x1": default_lam,
                    "y0": 0,
                    "y1": 1.5,
                    "line": {"color": "#94a3b8", "dash": "dot"},
                }
            ],
        },
        driven_by=["lam_probe"],
        update_fn=r"""
const lam = controls.lam_probe;
Plotly.relayout(panelId, {
  'shapes[0].x0': lam,
  'shapes[0].x1': lam,
});
""",
    )


def joint_heatmap_panel(payload: DashboardPayload) -> Panel:
    initial = payload.joint_grid[0] if payload.joint_grid else [[0.25, 0.25], [0.25, 0.25]]
    return Panel(
        panel_id="joint_heatmap",
        title="Joint posterior q_λ(π) at slider λ",
        description=(
            "Live K=2 heatmap of the entangled joint over (π_0, π_1). "
            "λ=0 is bit-exact mean-field; λ → ∞ collapses onto the "
            "alignment subspace."
        ),
        traces=[
            heatmap(
                z=initial,
                x_labels=["π_1=0", "π_1=1"],
                y_labels=["π_0=0", "π_0=1"],
            )
        ],
        layout={
            "xaxis": {"title": "stream 1"},
            "yaxis": {"title": "stream 0"},
            "annotations": [],
        },
        driven_by=["lam_probe"],
        update_fn=r"""
const lam = controls.lam_probe;
let best = 0;
let bestDist = Infinity;
for (let i = 0; i < payload.lambdas.length; i++) {
  const dist = Math.abs(payload.lambdas[i] - lam);
  if (dist < bestDist) {
    bestDist = dist;
    best = i;
  }
}
Plotly.restyle(panelId, {z: [payload.joint_grid[best]]}, [0]);
""",
    )


def schmidt_panel(payload: DashboardPayload) -> Panel:
    return Panel(
        panel_id="schmidt_panel",
        title="Schmidt rank & entanglement entropy",
        description=(
            "Schmidt rank is 1 at λ=0 (pure mean-field) and 2 elsewhere; "
            "entanglement entropy grows from 0 with |λ|."
        ),
        traces=[
            scatter_markers(
                name="Schmidt rank",
                x=payload.lambdas,
                y=[float(v) for v in payload.schmidt_rank],
                color="#fb923c",
                size=4,
            ),
            scatter_line(
                name="entanglement entropy",
                x=payload.lambdas,
                y=payload.entanglement_entropy,
                color="#a78bfa",
                yaxis="y2",
            ),
        ],
        layout={
            **axis_layout(x_title="λ", y_title="Schmidt rank"),
            "yaxis": {"title": "Schmidt rank", "rangemode": "tozero"},
            "yaxis2": {
                "title": "entanglement entropy (nats)",
                "overlaying": "y",
                "side": "right",
                "showgrid": False,
            },
        },
    )


def phase_panel(args: argparse.Namespace, payload: DashboardPayload) -> Panel:
    return Panel(
        panel_id="phase_panel",
        title="Coupling phases (configurable thresholds)",
        description=(
            f"phase classifier with critical couplings (λ_c1, λ_c2) = "
            f"({args.lam_c1}, {args.lam_c2}). Disordered: λ < λ_c1; "
            f"mixed: λ_c1 ≤ λ ≤ λ_c2; frozen: λ > λ_c2."
        ),
        traces=[
            scatter_markers(
                name="phase",
                x=payload.lambdas,
                y=[float(_PHASE_ORDINAL[p]) for p in payload.phases],
                color=[_PHASE_COLORS[p] for p in payload.phases],
            )
        ],
        layout={
            "xaxis": {"title": "λ"},
            "yaxis": {
                "title": "phase",
                "tickmode": "array",
                "tickvals": [0, 1, 2],
                "ticktext": ["disordered", "mixed", "frozen"],
                "range": [-0.5, 2.5],
            },
            "shapes": [
                {
                    "type": "line",
                    "x0": args.lam_c1,
                    "x1": args.lam_c1,
                    "y0": -0.5,
                    "y1": 2.5,
                    "line": {"color": "#94a3b8", "dash": "dot"},
                },
                {
                    "type": "line",
                    "x0": args.lam_c2,
                    "x1": args.lam_c2,
                    "y0": -0.5,
                    "y1": 2.5,
                    "line": {"color": "#94a3b8", "dash": "dot"},
                },
            ],
        },
    )
