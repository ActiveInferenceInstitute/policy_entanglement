#!/usr/bin/env python3
"""Sweep coupling λ over a fine grid and emit a CSV with every key
quantity from the manuscript: mutual information, free energy,
Schmidt rank, entanglement entropy, optimal λ check.

Useful both as an independent reproducibility artefact and as a
sanity rail when tightening proofs in the Lean module.

Thin orchestrator — imports compute helpers from
``projects/actinf_policy_entanglement_lean/src/`` and only handles
I/O / serialisation / stdout-path emission.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
for _sub in ("", "lean", "simulation", "visualizations"):
    sys.path.insert(0, str(SRC_DIR / _sub if _sub else SRC_DIR))

import numpy as np  # noqa: E402

from bernoulli_toy import (  # noqa: E402
    coupling_phase_at,
    empirical_mutual_information,
    ising_free_energy_curve,
    ising_joint_posterior,
    ising_mutual_information,
)
from free_energy import joint_entropy, marginal_entropy  # noqa: E402
from spectral import entanglement_entropy, schmidt_rank  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "output" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    lams = np.linspace(0.0, 6.0, 121)
    out_path = OUTPUT_DIR / "parameter_sweep.csv"
    with out_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "lambda",
            "mi_closed_form", "mi_empirical", "mi_residual",
            "free_energy_u0", "free_energy_u1", "free_energy_u2",
            "joint_entropy", "marginal_entropy_0", "marginal_entropy_1",
            "schmidt_rank", "entanglement_entropy",
            "phase",
        ])
        for lam in lams:
            lam_f = float(lam)
            q = ising_joint_posterior(lam_f)
            mi_closed = ising_mutual_information(lam_f)
            mi_empirical = empirical_mutual_information(lam_f)
            row = [
                f"{lam_f:.6f}",
                f"{mi_closed:.10g}",
                f"{mi_empirical:.10g}",
                f"{mi_closed - mi_empirical:.3e}",
                f"{ising_free_energy_curve(lam_f, 0.0):.10g}",
                f"{ising_free_energy_curve(lam_f, 1.0):.10g}",
                f"{ising_free_energy_curve(lam_f, 2.0):.10g}",
                f"{joint_entropy(q):.10g}",
                f"{marginal_entropy(q, 0):.10g}",
                f"{marginal_entropy(q, 1):.10g}",
                schmidt_rank(q, atol=1e-9),
                f"{entanglement_entropy(q):.10g}",
                coupling_phase_at(lam_f, lam_c1=0.5, lam_c2=2.5),
            ]
            writer.writerow(row)
    print(out_path)


if __name__ == "__main__":
    main()
