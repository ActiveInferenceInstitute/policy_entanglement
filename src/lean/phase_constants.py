"""Illustrative Bernoulli-toy phase-band thresholds.

These defaults make the K=2 phase boundaries non-degenerate in figures
and dashboard panels.  Real values are model-dependent; simulation
hyperparameters re-export them for pymdp-sidecar mirrors.
"""

from __future__ import annotations

PHASE_LAMBDA_C1: float = 0.5
PHASE_LAMBDA_C2: float = 2.5

__all__ = ["PHASE_LAMBDA_C1", "PHASE_LAMBDA_C2"]
