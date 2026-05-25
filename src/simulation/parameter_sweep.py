"""λ-sweep over manuscript quantities — pure compute + CSV writer.

Business logic for ``scripts/parameter_sweep.py``. The script is a thin
CLI wrapper that parses arguments and forwards them to :func:`run`.

The sweep evaluates, at each ``λ`` on a configurable grid:

* closed-form and empirical mutual information,
* free-energy curve at one or more utility-surplus levels,
* joint and marginal entropies of the K=2 Ising posterior,
* Schmidt rank with a configurable truncation tolerance,
* entanglement entropy and the coupling-phase classification.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Protocol

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


class _CsvWriter(Protocol):
    def writerow(self, row: Sequence[object]) -> object: ...


def _write_header(writer: _CsvWriter, utilities: Sequence[float]) -> None:
    fe_cols = [f"free_energy_u{u:g}" for u in utilities]
    writer.writerow(
        [
            "lambda",
            "mi_closed_form",
            "mi_empirical",
            "mi_residual",
            *fe_cols,
            "joint_entropy",
            "marginal_entropy_0",
            "marginal_entropy_1",
            "schmidt_rank",
            "entanglement_entropy",
            "phase",
        ]
    )


def _row(lam: float, utilities: Sequence[float], *, lam_c1: float, lam_c2: float, schmidt_atol: float) -> list[object]:
    q = ising_joint_posterior(lam)
    mi_closed = ising_mutual_information(lam)
    mi_empirical = empirical_mutual_information(lam)
    return [
        f"{lam:.6f}",
        f"{mi_closed:.10g}",
        f"{mi_empirical:.10g}",
        f"{mi_closed - mi_empirical:.3e}",
        *(f"{ising_free_energy_curve(lam, float(u)):.10g}" for u in utilities),
        f"{joint_entropy(q):.10g}",
        f"{marginal_entropy(q, 0):.10g}",
        f"{marginal_entropy(q, 1):.10g}",
        schmidt_rank(q, atol=schmidt_atol),
        f"{entanglement_entropy(q):.10g}",
        coupling_phase_at(lam, lam_c1=lam_c1, lam_c2=lam_c2),
    ]


def run(
    *,
    lams: Iterable[float],
    utilities: Sequence[float],
    lam_c1: float,
    lam_c2: float,
    schmidt_atol: float,
    output_path: Path,
) -> Path:
    """Run the sweep and write ``output_path``. Returns the written path."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    lam_array = np.asarray(list(lams), dtype=np.float64)
    with output_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        _write_header(writer, utilities)
        for lam in lam_array:
            writer.writerow(
                _row(
                    float(lam),
                    utilities,
                    lam_c1=lam_c1,
                    lam_c2=lam_c2,
                    schmidt_atol=schmidt_atol,
                )
            )
    return output_path


__all__ = ["run"]
