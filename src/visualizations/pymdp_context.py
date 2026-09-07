"""Shared execution context for pymdp figure emitters."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from simulation import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).
from simulation.logging_utils import RunLogger, default_logger
from visualizations.metadata import figure_metadata
from visualizations.setup import ensure_outdir

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_SCRIPT = "scripts/simulate_pymdp.py"


@dataclass(frozen=True)
class PymdpFigureContext:
    project_root: Path
    fig_dir: Path
    sim_dir: Path
    logger: RunLogger
    source_script: str = SOURCE_SCRIPT

    @classmethod
    def default(cls, project_root: Path | None = None) -> PymdpFigureContext:
        root = project_root or PROJECT_ROOT
        return cls(
            project_root=root,
            fig_dir=ensure_outdir(root / "output" / "figures"),
            sim_dir=ensure_outdir(root / "output" / "simulations"),
            logger=default_logger(root),
        )

    def metadata_factory(self) -> Callable[..., dict[str, Any]]:
        def build_metadata(source_function: str, **extra: object) -> dict[str, str]:
            return figure_metadata(
                source_script=self.source_script,
                source_function=source_function,
                hyperparameters={
                    "K": int(H.PYMDP_ENSEMBLE_K),
                    "gamma": float(H.PYMDP_ENSEMBLE_GAMMA),
                    "coupling_lambda_gen": float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
                },
                extra=dict(extra) if extra else None,
                project_root=self.project_root,
            )

        return build_metadata
