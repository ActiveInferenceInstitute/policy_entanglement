"""Dashboard datatypes plus the actinf_policy_entanglement_lean dashboard builder.

Top section: shared :class:`Panel` / :class:`Control` / :class:`Invariant` datatypes
imported by :mod:`reporting.interactive_dashboard` and the project's invariants
modules.

Bottom section: :func:`build_dashboard_payload` and :func:`build_dashboard` —
the importable equivalents of the historical ``scripts/build_dashboard.py``
orchestration so the script stays a thin CLI wrapper.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast


def _is_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _as_float(value: object) -> float:
    return float(cast(Any, value))


def _as_float_sequence(value: object) -> list[float]:
    if _is_sequence(value):
        return [_as_float(v) for v in cast(Sequence[object], value)]
    return [_as_float(value)]


@dataclass
class Panel:
    """One Plotly figure on the dashboard."""

    panel_id: str
    title: str
    traces: list[dict[str, Any]]
    layout: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    driven_by: list[str] = field(default_factory=list)
    update_fn: str = ""
    preview_rows: int = 10


@dataclass
class Control:
    """One interactive control."""

    control_id: str
    label: str
    kind: Literal["slider", "dropdown", "toggle", "number"] = "slider"
    min: float | None = None
    max: float | None = None
    step: float | None = None
    default: Any = 0.0
    options: list[Any] = field(default_factory=list)
    option_labels: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class Invariant:
    """A single numerical invariant to validate."""

    name: str
    actual: float | Sequence[float]
    expected: float | tuple[float, float] | Sequence[float] | None = None
    tol: float = 1e-9
    kind: Literal[
        "equal",
        "le",
        "ge",
        "in_range",
        "monotone_increasing",
        "monotone_decreasing",
        "finite",
        "nonneg",
        "array_close",
    ] = "equal"
    description: str = ""

    def evaluate(self) -> tuple[bool, str]:
        """Return ``(passed, witness)``."""
        try:
            if self.kind == "equal":
                a = _as_float(self.actual)
                e = _as_float(self.expected)
                diff = abs(a - e)
                return diff <= self.tol, f"|{a:.6g} - {e:.6g}| = {diff:.3e} (tol={self.tol:.1e})"
            if self.kind == "le":
                a = _as_float(self.actual)
                e = _as_float(self.expected)
                return a <= e + self.tol, f"{a:.6g} <= {e:.6g} + {self.tol:.1e}"
            if self.kind == "ge":
                a = _as_float(self.actual)
                e = _as_float(self.expected)
                return a >= e - self.tol, f"{a:.6g} >= {e:.6g} - {self.tol:.1e}"
            if self.kind == "in_range":
                a = _as_float(self.actual)
                lo, hi = _as_float_sequence(self.expected)[:2]
                ok = (lo - self.tol) <= a <= (hi + self.tol)
                return ok, f"{lo:.6g} <= {a:.6g} <= {hi:.6g} (tol={self.tol:.1e})"
            if self.kind in ("monotone_increasing", "monotone_decreasing"):
                seq = _as_float_sequence(self.actual)
                worst = 0.0
                inc = self.kind == "monotone_increasing"
                for x, y in zip(seq, seq[1:], strict=False):
                    delta = (y - x) if inc else (x - y)
                    if delta < -self.tol:
                        worst = min(worst, delta)
                ok = worst >= -self.tol
                arrow = "<=" if inc else ">="
                return ok, (
                    f"worst out-of-order step = {worst:.3e} (tol={self.tol:.1e}, "
                    f"sequence length {len(seq)}, expect a_i {arrow} a_{{i+1}})"
                )
            if self.kind == "finite":
                if _is_sequence(self.actual):
                    vals = _as_float_sequence(self.actual)
                    bad = [i for i, v in enumerate(vals) if not math.isfinite(v)]
                    ok = not bad
                    return (
                        ok,
                        (
                            f"all finite ({len(vals)} values)"
                            if ok
                            else f"non-finite at indices {bad[:8]}{'...' if len(bad) > 8 else ''}"
                        ),
                    )
                a = _as_float(self.actual)
                ok = math.isfinite(a)
                return ok, f"value = {a!r}"
            if self.kind == "nonneg":
                if _is_sequence(self.actual):
                    vals = _as_float_sequence(self.actual)
                    worst = min(vals) if vals else 0.0
                    ok = worst >= -self.tol
                    return ok, f"min = {worst:.6g} (tol={self.tol:.1e})"
                a = _as_float(self.actual)
                return a >= -self.tol, f"value = {a:.6g} (tol={self.tol:.1e})"
            if self.kind == "array_close":
                actual_values = _as_float_sequence(self.actual)
                expected_values = _as_float_sequence(self.expected)
                if len(actual_values) != len(expected_values):
                    return False, f"length mismatch: actual={len(actual_values)}, expected={len(expected_values)}"
                worst = 0.0
                bad_idx = -1
                for i, (av, ev) in enumerate(zip(actual_values, expected_values, strict=True)):
                    d = abs(av - ev)
                    if d > worst:
                        worst, bad_idx = d, i
                return worst <= self.tol, (
                    f"max |delta| = {worst:.3e} at index {bad_idx} (tol={self.tol:.1e}, length {len(actual_values)})"
                )
        except Exception as exc:  # pragma: no cover - defensive
            return False, f"evaluation error: {exc!r}"
        return False, f"unknown kind {self.kind!r}"


_DASHBOARD_SRC_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_PROJECT_ROOT = _DASHBOARD_SRC_DIR.parent

OUTPUT = DASHBOARD_PROJECT_ROOT / "output"
WEB_DIR = OUTPUT / "web"
DATA_DIR = OUTPUT / "data"
REP_DIR = OUTPUT / "reports"


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def parse_dashboard_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the dashboard CLI argument set.

    Defaults reproduce the canonical manuscript sweep so existing pipeline runs
    are unaffected.
    """
    p = argparse.ArgumentParser(
        description=("Build the interactive simulation dashboard for actinf_policy_entanglement_lean."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--lam-min", type=float, default=0.0)
    p.add_argument("--lam-max", type=float, default=6.0)
    p.add_argument("--num", type=int, default=121)
    p.add_argument(
        "--utilities",
        type=float,
        nargs="+",
        default=[0.0, 1.0, 2.0],
        help="utility surplus levels for the FE curve panel",
    )
    p.add_argument("--lam-c1", type=float, default=0.5)
    p.add_argument("--lam-c2", type=float, default=2.5)
    p.add_argument("--schmidt-atol", type=float, default=1e-9)
    p.add_argument(
        "--probe-lambdas",
        type=float,
        nargs="+",
        default=[0.0, 1.0, 2.0, 4.0],
        help="λ values offered as joint-heatmap snapshots",
    )
    p.add_argument("--html-out", type=Path, default=WEB_DIR / "dashboard.html")
    p.add_argument("--json-out", type=Path, default=DATA_DIR / "dashboard_payload.json")
    p.add_argument("--invariants-out", type=Path, default=REP_DIR / "dashboard_invariants.txt")
    p.add_argument("--summary-out", type=Path, default=REP_DIR / "dashboard_summary.txt")
    args = p.parse_args(argv)
    if args.num < 2:
        p.error("--num must be ≥ 2")
    if args.lam_max <= args.lam_min:
        p.error("--lam-max must be > --lam-min")
    return args


# ---------------------------------------------------------------------------
# Payload computation
# ---------------------------------------------------------------------------


def build_dashboard_payload(args: argparse.Namespace) -> dict[str, Any]:
    """Compute the full numerical payload that drives the dashboard panels."""
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


# ---------------------------------------------------------------------------
# Dashboard assembly
# ---------------------------------------------------------------------------


def build_dashboard(args: argparse.Namespace, payload: dict[str, Any]) -> Any:
    """Assemble the populated :class:`InteractiveDashboard` instance."""
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


__all__ = [
    "Control",
    "DASHBOARD_PROJECT_ROOT",
    "DATA_DIR",
    "Invariant",
    "OUTPUT",
    "Panel",
    "REP_DIR",
    "WEB_DIR",
    "build_dashboard",
    "build_dashboard_payload",
    "main",
    "parse_dashboard_args",
    "write_dashboard",
]
