#!/usr/bin/env python3
"""Dump the K=2 Ising archetypes (Schmidt modes) at a sweep of λ values
to a CSV table.

Each row is one archetype `(lambda, mode_index, weight, u_0, u_1, v_0, v_1)`
where `(u, v)` are the unit-norm marginal patterns and `weight` is the
singular value.  The CSV is downstream-friendly for inclusion in the
manuscript's archetype-sparsity table or for plotting in external tools.

Thin orchestrator — imports compute helpers from
``projects/actinf_policy_entanglement_lean/src/`` and only handles
I/O / serialisation / stdout-path emission.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

import numpy as np  # noqa: E402

from lean.bernoulli_toy import ising_joint_posterior  # noqa: E402
from lean.spectral import schmidt_decomposition  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "output" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    lams = np.linspace(0.0, 4.0, 17)  # 0.0, 0.25, 0.5, ... 4.0
    out_path = OUTPUT_DIR / "ising_archetypes.csv"
    with out_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "lambda",
                "mode_index",
                "weight",
                "u_0",
                "u_1",
                "v_0",
                "v_1",
            ]
        )
        for lam in lams:
            q = ising_joint_posterior(float(lam))
            modes = schmidt_decomposition(q, atol=1e-12)
            for idx, m in enumerate(modes):
                writer.writerow(
                    [
                        f"{float(lam):.4f}",
                        idx,
                        f"{m.weight:.10g}",
                        f"{m.u[0]:.10g}",
                        f"{m.u[1]:.10g}",
                        f"{m.v[0]:.10g}",
                        f"{m.v[1]:.10g}",
                    ]
                )
    print(out_path)


if __name__ == "__main__":
    main()
