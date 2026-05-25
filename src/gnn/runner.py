"""Runner for the GNN round-trip pipeline stage (executable Triple-Play view).

Thin-orchestrator compliant: this module holds the GNN round-trip *logic*
(parse -> reconstruct -> compare -> emit), while ``scripts/simulate_gnn.py``
only binds output directories and forwards here.

The round-trip reconstructs the K=2 Bernoulli/Ising mutual-information curve
from ``gnn/bernoulli_toy.gnn.md`` via the framework's general machinery
(:mod:`gnn.bridge`, which never touches the closed form) and compares it to the
closed-form ``ising_mutual_information`` — the comparison oracle imported *here*
in the runner, never in the bridge.  This is an integration / internal-
consistency check (the general machinery reduces to the closed form for this
toy), not an independent re-derivation; its witness value is that the
GNN-sourced spec, through the general code path, reproduces the analytic
prediction.  The emitted sidecar ``output/data/gnn_bernoulli_roundtrip.json``
carries both the agreement residual and an embedded **zero-coupling
negative-control** residual (proving the bridge responds to the declared
coupling), so that evidence is a durable artifact, not just a test-time
assertion.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from gnn.bridge import reconstruct_mi_curve
from gnn.lean_emit import emit_lean_structure
from gnn.parser import parse_gnn_file
from lean.bernoulli_toy import ising_mutual_information  # INDEPENDENT comparison oracle (closed form)
from simulation.hyperparameters import (
    BERNOULLI_VERIFICATION_TOLERANCE,
    PARAMETER_SWEEP_LAMBDAS,
)

ArrayF = NDArray[np.float64]

TOY_GNN = "bernoulli_toy.gnn.md"
SIDECAR_NAME = "gnn_bernoulli_roundtrip.json"
FIGURE_NAME = "gnn_bernoulli_roundtrip.png"
LEAN_NAME = "BernoulliToyGnn.lean"


def _closed_form_curve(lambdas: ArrayF) -> ArrayF:
    """The manuscript's closed-form MI curve (the comparison oracle)."""
    return np.array([ising_mutual_information(float(lam)) for lam in lambdas], dtype=np.float64)


def compute_roundtrip(gnn_dir: Path) -> dict[str, object]:
    """Parse the toy, reconstruct the MI curve, compare, and build the payload.

    Returns a JSON-serializable dict (deterministic given the GNN source).
    """
    model = parse_gnn_file(gnn_dir / TOY_GNN)
    grid = PARAMETER_SWEEP_LAMBDAS
    lambdas = np.linspace(grid.start, grid.stop, grid.num)

    mi_gnn = reconstruct_mi_curve(model, lambdas)
    mi_closed = _closed_form_curve(lambdas)
    resid = np.abs(mi_gnn - mi_closed)
    tol = float(BERNOULLI_VERIFICATION_TOLERANCE)

    # Embedded non-vacuity negative control: zero the parsed coupling and
    # confirm the reconstruction diverges from the closed form.  (Sign-flip is
    # NOT a valid control: mutual information is invariant under J -> -J, since
    # flipping the coupling only relabels which configuration is preferred.)
    zero_coupling = replace(model.variable("J"), value=np.zeros((2, 2), dtype=np.float64))
    model_zero = replace(model, variables={**model.variables, "J": zero_coupling})
    mi_zero = reconstruct_mi_curve(model_zero, lambdas)
    neg_ctrl_resid = float(np.abs(mi_zero - mi_closed).max())

    rows = [
        {
            "lambda": float(lambdas[i]),
            "mi_gnn": float(mi_gnn[i]),
            "mi_closed_form": float(mi_closed[i]),
            "abs_residual": float(resid[i]),
        }
        for i in range(len(lambdas))
    ]
    return {
        "model_section": model.section,
        "model_version": model.version,
        "num_streams": model.num_streams,
        "coupling_matrix": model.variable("J").matrix().tolist(),
        "lambda_grid": {"start": float(grid.start), "stop": float(grid.stop), "num": int(grid.num)},
        "tolerance": tol,
        "max_abs_residual": float(resid.max()),
        "round_trip_passes": bool(resid.max() <= tol),
        "negative_control_zero_coupling_max_residual": neg_ctrl_resid,
        "negative_control_discriminates": bool(neg_ctrl_resid > tol),
        "rows": rows,
    }


def _plot(payload: dict[str, object], fig_path: Path) -> None:
    """Two-panel figure: MI-curve overlay + round-trip residual."""
    import matplotlib.pyplot as plt

    from visualizations._io import _save_with_metadata
    from visualizations.metadata import figure_metadata

    rows = payload["rows"]
    assert isinstance(rows, list)
    lam = [r["lambda"] for r in rows]
    gnn = [r["mi_gnn"] for r in rows]
    closed = [r["mi_closed_form"] for r in rows]
    resid = [r["abs_residual"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.plot(lam, closed, "-", lw=2.4, color="#1f77b4", label="closed form $I(\\lambda)$")
    ax1.plot(lam, gnn, "--", lw=1.6, color="#d62728", label="GNN-reconstructed")
    ax1.axhline(np.log(2.0), color="0.6", ls=":", lw=1.0, label="$\\log 2$ saturation")
    ax1.set_xlabel("coupling $\\lambda$")
    ax1.set_ylabel("mutual information (nats)")
    ax1.set_title("GNN fifth-track round-trip: $I(\\lambda)$")
    ax1.legend(loc="lower right", fontsize=10)
    ax1.grid(alpha=0.3)

    ax2.semilogy(lam, np.maximum(resid, 1e-18), "-", color="#2ca02c", lw=1.6)
    ax2.axhline(payload["tolerance"], color="#d62728", ls="--", lw=1.2, label="tolerance")
    ax2.set_xlabel("coupling $\\lambda$")
    ax2.set_ylabel("|GNN − closed form| (nats)")
    ax2.set_title(f"round-trip residual (max {payload['max_abs_residual']:.2e})")
    ax2.legend(loc="upper right", fontsize=10)
    ax2.grid(alpha=0.3)

    _save_with_metadata(
        fig,
        fig_path,
        metadata=figure_metadata(
            source_script="scripts/simulate_gnn.py",
            source_function="gnn.runner.run",
            hyperparameters={
                "lambda_grid": payload["lambda_grid"],
                "coupling": "ising_symmetric",
            },
            statistics={
                "max_abs_residual": payload["max_abs_residual"],
                "tolerance": payload["tolerance"],
                "negative_control_zero_coupling_max_residual": payload[
                    "negative_control_zero_coupling_max_residual"
                ],
            },
            uncertainty_semantics="deterministic_grid",
        ),
    )


def run(*, data_dir: Path, fig_dir: Path, gnn_dir: Path, lean_out: Path | None = None) -> int:
    """Execute the GNN round-trip stage and emit sidecar + figure + Lean.

    Args:
        data_dir: ``output/data`` for the JSON sidecar.
        fig_dir: ``output/figures`` for the PNG.
        gnn_dir: the ``gnn/`` source directory.
        lean_out: optional path for the emitted Lean typed-contract file.

    Returns:
        Process exit code (0 on success / round-trip pass).
    """
    from visualizations.setup import ensure_outdir

    ensure_outdir(data_dir)
    ensure_outdir(fig_dir)

    payload = compute_roundtrip(gnn_dir)

    sidecar = data_dir / SIDECAR_NAME
    sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    _plot(payload, fig_dir / FIGURE_NAME)

    # Emit the GNN -> Lean typed-structure contract for provenance.
    model = parse_gnn_file(gnn_dir / TOY_GNN)
    lean_path = lean_out or (gnn_dir / "generated" / LEAN_NAME)
    ensure_outdir(lean_path.parent)
    lean_path.write_text(emit_lean_structure(model), encoding="utf-8")

    print(str(sidecar))
    print(str(fig_dir / FIGURE_NAME))
    print(str(lean_path))
    if not payload["round_trip_passes"]:
        print(f"GNN round-trip FAILED: max residual {payload['max_abs_residual']} > tol {payload['tolerance']}")
        return 1
    if not payload["negative_control_discriminates"]:  # pragma: no cover - defensive: the fixed non-trivial lambda grid makes zero-coupling always diverge
        print("GNN round-trip negative control is VACUOUS (zero-coupling did not diverge)")
        return 1
    print(
        f"GNN round-trip OK: max residual {payload['max_abs_residual']:.3e} <= tol {payload['tolerance']:.1e}; "
        f"neg-control (J=0) residual {payload['negative_control_zero_coupling_max_residual']:.3e}"
    )
    return 0
