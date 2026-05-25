#!/usr/bin/env python3
"""Run the revertibility / m-projection back-to-mean-field witness.

For each λ in
:data:`simulation.hyperparameters.REVERTIBILITY_LAMBDAS`:

  1. Compute the coupled joint $q_\\lambda$ via pymdp + the
     analytical coupling layer.
  2. Compute its m-projection $\\hat m(q_\\lambda) = \\prod_k q^k_\\lambda$.
  3. Verify the marginals match (revertibility) and the
     ``KL(q_λ ‖ m(q_λ)) == I(q_λ)`` identity (Prop 7.3 / Theorem 5.1).

Emits:

* ``output/simulations/pymdp_revertibility.csv`` — one row per λ.
* ``output/figures/revertibility_witness.png`` — KL=I overlay and
  marginal-diff curve.
* ``output/data/revertibility_summary.json`` — flat scalar
  manuscript-variable mirror.

Skipped (with a stdout note, exit 0) when the ``sim`` group is not
installed.
"""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from simulation import hyperparameters as H  # noqa: E402,N812 — H = hyperparameters (manuscript convention).
from simulation.agents import pymdp_available  # noqa: E402
from simulation.revertibility import (  # noqa: E402
    revertibility_summary,
    revertibility_test,
)
from visualizations.metadata import figure_metadata  # noqa: E402
from visualizations.multi_k_plots import plot_revertibility_witness  # noqa: E402
from visualizations.setup import deterministic_setup, ensure_outdir  # noqa: E402

FIG_DIR = PROJECT_ROOT / "output" / "figures"
SIM_DIR = PROJECT_ROOT / "output" / "simulations"
DATA_DIR = PROJECT_ROOT / "output" / "data"


def _md(source_function: str, **extra) -> dict[str, str]:
    """Build the figure-metadata dict snapshot for this script.

    Captures the full revertibility sweep configuration (λ grid,
    tolerances, K, γ) so the witness PNG retains its own provenance.
    """
    snapshot = {
        "lambdas": list(float(x) for x in H.REVERTIBILITY_LAMBDAS),
        "tolerance": float(H.REVERTIBILITY_TOLERANCE),
        "kl_identity_tolerance": float(H.REVERTIBILITY_KL_IDENTITY_TOLERANCE),
        "K": int(H.PYMDP_ENSEMBLE_K),
        "gamma": float(H.PYMDP_ENSEMBLE_GAMMA),
        "coupling_lambda_gen": float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
    }
    return figure_metadata(
        source_script="scripts/simulate_revertibility.py",
        source_function=source_function,
        hyperparameters=snapshot,
        extra=dict(extra) if extra else None,
        project_root=PROJECT_ROOT,
    )


def main() -> int:
    """Run the revertibility witness sweep and emit CSV + JSON + figure.

    Returns 0 on success (including the pymdp-unavailable skip path);
    any underlying simulation exception is allowed to propagate.
    """
    if not pymdp_available():  # pragma: no cover
        print("pymdp not installed; skipping simulate_revertibility.py")
        print("Install via: uv sync --group sim")
        return 0
    ensure_outdir(FIG_DIR)
    ensure_outdir(SIM_DIR)
    ensure_outdir(DATA_DIR)
    deterministic_setup(seed=int(H.FIGURE_GLOBAL_SEED))

    print(
        f"[revertibility] testing {len(H.REVERTIBILITY_LAMBDAS)} λ values "
        f"(K={int(H.PYMDP_ENSEMBLE_K)}, γ={float(H.PYMDP_ENSEMBLE_GAMMA):.2f})",
        flush=True,
    )
    records = revertibility_test(
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        lambda_values=H.REVERTIBILITY_LAMBDAS,
        tolerance=float(H.REVERTIBILITY_TOLERANCE),
        kl_identity_tolerance=float(H.REVERTIBILITY_KL_IDENTITY_TOLERANCE),
    )
    for r in records:
        flag = "OK" if r.revertible else "FAIL"
        print(
            f"[revertibility] λ={r.lam:.3f}: I={r.multi_information:.6g}, "
            f"KL={r.kl_q_to_mproj:.6g}, |Δ|max={r.marginal_max_abs_diff:.2e}, "
            f"residual={r.kl_identity_residual:.2e}  {flag}",
            flush=True,
        )

    # CSV
    csv_path = SIM_DIR / "pymdp_revertibility.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "lambda",
                "multi_information",
                "kl_q_to_mproj",
                "kl_identity_residual",
                "marginal_max_abs_diff",
                "marginals_match",
                "kl_identity_holds",
                "revertible",
            ]
        )
        for r in records:
            writer.writerow(
                [
                    f"{r.lam:.6f}",
                    f"{r.multi_information:.10g}",
                    f"{r.kl_q_to_mproj:.10g}",
                    f"{r.kl_identity_residual:.10g}",
                    f"{r.marginal_max_abs_diff:.10g}",
                    int(r.marginals_match),
                    int(r.kl_identity_holds),
                    int(r.revertible),
                ]
            )

    # Figure
    fig_path = plot_revertibility_witness(
        records,
        out_path=FIG_DIR / "revertibility_witness.png",
        metadata=_md("plot_revertibility_witness"),
    )

    # JSON summary
    summary = revertibility_summary(records)
    summary_path = DATA_DIR / "revertibility_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    for p in (csv_path, fig_path, summary_path):
        print(str(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
