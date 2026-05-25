"""CSV grid matching helpers for output gates."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates._reporting import ok as report_ok
from simulation import hyperparameters as H  # noqa: N812


def parameter_sweep_required_columns(
    utilities: Sequence[float] | None = None,
) -> set[str]:
    """Column schema for ``output/data/parameter_sweep.csv``.

    Matches :func:`simulation.parameter_sweep.run` header generation and the
    canonical ``scripts/parameter_sweep.py`` default utility grid.
    """
    utils = H.PARAMETER_SWEEP_DEFAULT_UTILITIES if utilities is None else tuple(utilities)
    base = {
        "lambda",
        "mi_closed_form",
        "mi_empirical",
        "mi_residual",
        "schmidt_rank",
        "entanglement_entropy",
        "phase",
    }
    for u in utils:
        base.add(f"free_energy_u{u:g}")
    return base


def grid_values(grid) -> list[float]:
    return [float(v) for v in grid.values()]


def rows_match_grid(rows: list[dict[str, str]], grid, *, label: str, tol: float = 1e-9) -> int:
    expected = grid_values(grid)
    if len(rows) != len(expected):
        report_fail(f"{label}: {len(rows)} rows != expected grid length {len(expected)}")
        return 1
    failures = 0
    for idx, (row, exp) in enumerate(zip(rows, expected, strict=True)):
        got = float(row["lambda"])
        if abs(got - exp) > tol:
            report_fail(f"{label}: row {idx} λ={got} != expected {exp}")
            failures += 1
    return failures


def read_csv_rows(path: Path, required: set[str]) -> tuple[list[dict[str, str]], int]:
    """Read a CSV and verify required columns."""

    if not path.exists():
        report_ok(f"(optional, not present): {path.name}")
        return [], 0
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        missing = required - set(reader.fieldnames or [])
        if missing:
            report_fail(f"{path.name}: missing columns: {sorted(missing)}")
            return [], 1
        return list(reader), 0
