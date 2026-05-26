from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, cast

from dashboard_types.cli import parse_dashboard_args
from dashboard_types.paths import DASHBOARD_PROJECT_ROOT
from dashboard_types.payload import build_dashboard_payload
from dashboard_types.types import Invariant


def build_dashboard(args: argparse.Namespace, payload: dict[str, Any]) -> Any:
    from lean.bernoulli_toy import ising_joint_posterior
    from lean.free_energy import kl_divergence, total_correlation
    from lean.invariants import SweepGrid, all_invariants
    from lean.joint_dist import m_projection
    from reporting.interactive_dashboard import InteractiveDashboard, Panel

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
    d.set_payload(payload)
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

    d.add_panel(
        Panel(
            panel_id="mi_curves",
            title="Mutual information: closed-form vs empirical",
            description=(
                "Closed-form I(λ) = log 2 − H_b(σ(λ)) (orange) overlaid with the "
                "empirical total correlation of the λ-entangled joint (blue). "
                "Residual is plotted on the secondary axis."
            ),
            traces=[
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "closed-form I(λ)",
                    "x": payload["lambdas"],
                    "y": payload["mi_closed"],
                    "line": {"color": "#fb923c"},
                },
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "empirical TC(q_λ)",
                    "x": payload["lambdas"],
                    "y": payload["mi_empirical"],
                    "line": {"color": "#38bdf8", "dash": "dash"},
                },
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "residual (×1e9)",
                    "x": payload["lambdas"],
                    "y": [r * 1e9 for r in payload["mi_residual"]],
                    "yaxis": "y2",
                    "line": {"color": "#94a3b8"},
                },
            ],
            layout={
                "xaxis": {"title": "λ"},
                "yaxis": {"title": "MI / TC (nats)"},
                "yaxis2": {
                    "title": "residual ×1e-9",
                    "overlaying": "y",
                    "side": "right",
                    "showgrid": False,
                },
                "legend": {"orientation": "h", "y": -0.2},
            },
        )
    )

    fe_traces: list[dict[str, Any]] = []
    palette = ["#38bdf8", "#fb923c", "#a78bfa", "#22c55e", "#ef4444", "#facc15"]
    for i, (label, vals) in enumerate(payload["fe_curves"].items()):
        fe_traces.append(
            {
                "type": "scatter",
                "mode": "lines",
                "name": f"F(λ; {label})",
                "x": payload["lambdas"],
                "y": vals,
                "line": {"color": palette[i % len(palette)]},
            }
        )
    fe_traces.append(
        {
            "type": "scatter",
            "mode": "lines",
            "name": "F(λ; u=slider)",
            "x": payload["lambdas"],
            "y": payload["fe_curves"][next(iter(payload["fe_curves"]))],
            "line": {"color": "#f5f5f5", "dash": "dot", "width": 3},
        }
    )
    d.add_panel(
        Panel(
            panel_id="fe_curves",
            title="Free-energy curves F(λ; u)",
            description=(
                "Each curve is monotone-decreasing in |λ| for u ≥ 0 "
                "(invariant: free_energy_monotone_decreasing_u={...}). "
                "Move the utility slider to redraw the live trace."
            ),
            traces=fe_traces,
            layout={
                "xaxis": {"title": "λ"},
                "yaxis": {"title": "F(λ; u)"},
                "legend": {"orientation": "h", "y": -0.2},
            },
            driven_by=["utility"],
            update_fn=r"""
const lams = payload.lambdas;
const u = controls.utility;
// F(λ; u) = -u * (2σ(|λ|) - 1) - I(λ); reuse precomputed I(λ) from payload.
const fe = lams.map((l, i) => {
  const a = 2.0 / (1.0 + Math.exp(-Math.abs(l))) - 1.0;
  return -u * a - payload.mi_closed[i];
});
// The live trace was appended last; its index = number of named u-curves.
const liveIdx = Object.keys(payload.fe_curves).length;
Plotly.restyle(panelId, {y: [fe], name: ['F(λ; u=' + u.toFixed(2) + ')']}, [liveIdx]);
""",
        )
    )

    d.add_panel(
        Panel(
            panel_id="entropy_decomp",
            title="Entropy decomposition: H(q^k), H(q), TC",
            description=(
                "TC(q_λ) = Σ_k H(q^k) − H(q) ≥ 0, equals zero iff q is mean-field. Vertical line tracks the slider λ."
            ),
            traces=[
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "H(q^0)",
                    "x": payload["lambdas"],
                    "y": payload["H_marg_0"],
                    "line": {"color": "#38bdf8"},
                },
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "H(q^1)",
                    "x": payload["lambdas"],
                    "y": payload["H_marg_1"],
                    "line": {"color": "#fb923c"},
                },
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "H(q)",
                    "x": payload["lambdas"],
                    "y": payload["H_joint"],
                    "line": {"color": "#a78bfa"},
                },
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "TC",
                    "x": payload["lambdas"],
                    "y": payload["tc"],
                    "line": {"color": "#22c55e", "dash": "dash"},
                },
            ],
            layout={
                "xaxis": {"title": "λ"},
                "yaxis": {"title": "entropy (nats)"},
                "shapes": [
                    {
                        "type": "line",
                        "x0": (args.lam_min + args.lam_max) / 2.0,
                        "x1": (args.lam_min + args.lam_max) / 2.0,
                        "y0": 0,
                        "y1": 1.5,
                        "line": {"color": "#94a3b8", "dash": "dot"},
                    }
                ],
                "legend": {"orientation": "h", "y": -0.2},
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
    )

    d.add_panel(
        Panel(
            panel_id="joint_heatmap",
            title="Joint posterior q_λ(π) at slider λ",
            description=(
                "Live K=2 heatmap of the entangled joint over (π_0, π_1). "
                "λ=0 is bit-exact mean-field; λ → ∞ collapses onto the "
                "alignment subspace."
            ),
            traces=[
                {
                    "type": "heatmap",
                    "z": list(payload["joint_snapshots"].values())[0],
                    "x": ["π_1=0", "π_1=1"],
                    "y": ["π_0=0", "π_0=1"],
                    "colorscale": "Cividis",
                    "showscale": True,
                    "zmin": 0.0,
                    "zmax": 1.0,
                }
            ],
            layout={
                "xaxis": {"title": "stream 1"},
                "yaxis": {"title": "stream 0"},
                "annotations": [],
            },
            driven_by=["lam_probe"],
            update_fn=r"""
const lam = controls.lam_probe;
// Closed-form K=2 Ising joint: aligned mass σ(λ)/2 each, misaligned (1−σ(λ))/2 each.
const sigma = 1.0 / (1.0 + Math.exp(-lam));
const a = sigma / 2.0;
const b = (1.0 - sigma) / 2.0;
const Z = [[a, b], [b, a]];
Plotly.restyle(panelId, {z: [Z]}, [0]);
""",
        )
    )

    d.add_panel(
        Panel(
            panel_id="schmidt_panel",
            title="Schmidt rank & entanglement entropy",
            description=(
                "Schmidt rank is 1 at λ=0 (pure mean-field) and 2 elsewhere; "
                "entanglement entropy grows from 0 with |λ|."
            ),
            traces=[
                {
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Schmidt rank",
                    "x": payload["lambdas"],
                    "y": payload["schmidt_rank"],
                    "line": {"color": "#fb923c"},
                    "marker": {"size": 4},
                },
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "entanglement entropy",
                    "x": payload["lambdas"],
                    "y": payload["entanglement_entropy"],
                    "yaxis": "y2",
                    "line": {"color": "#a78bfa"},
                },
            ],
            layout={
                "xaxis": {"title": "λ"},
                "yaxis": {"title": "Schmidt rank", "rangemode": "tozero"},
                "yaxis2": {
                    "title": "entanglement entropy (nats)",
                    "overlaying": "y",
                    "side": "right",
                    "showgrid": False,
                },
                "legend": {"orientation": "h", "y": -0.2},
            },
        )
    )

    d.add_panel(
        Panel(
            panel_id="phase_panel",
            title="Coupling phases (configurable thresholds)",
            description=(
                f"phase classifier with critical couplings (λ_c1, λ_c2) = "
                f"({args.lam_c1}, {args.lam_c2}). Disordered: λ < λ_c1; "
                f"mixed: λ_c1 ≤ λ ≤ λ_c2; frozen: λ > λ_c2."
            ),
            traces=[
                {
                    "type": "scatter",
                    "mode": "markers",
                    "x": payload["lambdas"],
                    "y": [{"disordered": 0, "mixed": 1, "frozen": 2}[p] for p in payload["phases"]],
                    "marker": {
                        "color": [
                            {"disordered": "#22c55e", "mixed": "#facc15", "frozen": "#ef4444"}[p]
                            for p in payload["phases"]
                        ],
                        "size": 6,
                    },
                    "name": "phase",
                }
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
    )

    grid = SweepGrid(args.lam_min, args.lam_max, args.num)
    for inv in all_invariants(
        grid,
        utilities=tuple(args.utilities),
        lam_c1=args.lam_c1,
        lam_c2=args.lam_c2,
    ):
        d.add_invariant(inv)

    # Revertibility / m-projection invariant (T3 witness):
    # ``KL(q_λ ‖ m(q_λ)) == I(q_λ)`` (Prop 7.3 / Theorem 5.1).
    # Computed analytically on the Ising joint over the dashboard's probe-λ grid
    # so the invariant is independent of the pymdp run.
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

    head_n = min(15, len(payload["lambdas"]))
    d.add_table(
        "first_15_rows",
        [
            {
                "lambda": payload["lambdas"][i],
                "mi_closed": payload["mi_closed"][i],
                "mi_empirical": payload["mi_empirical"][i],
                "mi_residual": payload["mi_residual"][i],
                "tc": payload["tc"][i],
                "phase": payload["phases"][i],
            }
            for i in range(head_n)
        ],
    )

    return d


def write_dashboard(args: argparse.Namespace) -> dict[str, Path]:
    """Compute, build, and persist all dashboard artifacts.

    Returns a mapping with keys ``"html"``, ``"json"``, ``"invariants"`` and
    ``"summary"`` pointing at the emitted files.
    """
    payload = build_dashboard_payload(args)
    d = build_dashboard(args, payload)
    return cast(
        dict[str, Path],
        d.write(
            html_path=args.html_out,
            json_path=args.json_out,
            invariants_path=args.invariants_out,
            txt_path=args.summary_out,
        ),
    )


def main(argv: list[str] | None = None) -> None:
    """CLI entry point: parse args, build, persist, exit non-zero on invariant fail."""
    args = parse_dashboard_args(argv)
    payload = build_dashboard_payload(args)
    d = build_dashboard(args, payload)
    out = d.write(
        html_path=args.html_out,
        json_path=args.json_out,
        invariants_path=args.invariants_out,
        txt_path=args.summary_out,
    )
    for k in ("html", "json", "invariants", "summary"):
        if k in out:
            print(out[k])

    failed = [i for i in d.evaluate_invariants() if not i["passed"]]
    if failed:
        names = ", ".join(i["name"] for i in failed)
        print(f"FAILED INVARIANTS: {names}", file=sys.stderr)
        sys.exit(1)


__all__ = ["build_dashboard", "main", "write_dashboard"]
