"""Deterministic, framework-independent records for coupled POMDP ensembles."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class StreamSpec:
    """One POMDP stream within a coupled ensemble.

    Tensors follow the canonical pymdp shape conventions for a
    single-modality / single-factor model:

    * ``A`` — ``(num_obs, num_states)`` likelihood (column-stochastic).
    * ``B`` — ``(num_states, num_states, num_controls)`` transition
      tensor (each ``B[..., u]`` column-stochastic).
    * ``C`` — ``(num_obs,)`` log-preference vector.
    * ``D`` — ``(num_states,)`` prior over states (sums to 1).

    All arrays are ``float64``; the pymdp adapter casts to JAX
    ``float32`` and adds a batch axis at construction time.
    """

    A: ArrayF
    B: ArrayF
    C: ArrayF
    D: ArrayF
    name: str = ""

    def num_obs(self) -> int:
        return int(self.A.shape[0])

    def num_states(self) -> int:
        return int(self.A.shape[1])

    def num_controls(self) -> int:
        return int(self.B.shape[2])

    def validate(self) -> None:
        """Raise ``ValueError`` if any tensor is malformed."""
        if self.A.ndim != 2:
            raise ValueError(f"A must be 2-D, got {self.A.shape}")
        if self.B.ndim != 3 or self.B.shape[0] != self.B.shape[1]:
            raise ValueError(f"B must be (S,S,U), got {self.B.shape}")
        if self.A.shape[1] != self.B.shape[0]:
            raise ValueError(f"A num_states {self.A.shape[1]} != B num_states {self.B.shape[0]}")
        if self.C.shape != (self.A.shape[0],):
            raise ValueError(f"C shape {self.C.shape} != ({self.A.shape[0]},)")
        if self.D.shape != (self.A.shape[1],):
            raise ValueError(f"D shape {self.D.shape} != ({self.A.shape[1]},)")
        col_sums = self.A.sum(axis=0)
        if not np.allclose(col_sums, 1.0, atol=1e-8):
            raise ValueError(f"A columns must sum to 1: {col_sums}")
        for u in range(self.num_controls()):
            cs = self.B[:, :, u].sum(axis=0)
            if not np.allclose(cs, 1.0, atol=1e-8):
                raise ValueError(f"B[:,:,{u}] columns must sum to 1: {cs}")
        if not np.isclose(self.D.sum(), 1.0, atol=1e-8):
            raise ValueError(f"D must sum to 1: {self.D.sum()}")


@dataclass(frozen=True)
class CoupledEnsembleSpec:
    """K-stream coupled ensemble.

    ``streams`` carries one :class:`StreamSpec` per stream; ``coupling_j``
    and ``coupling_kc`` are dense ndarrays of shape
    ``(num_controls_0, num_controls_1, ..., num_controls_{K-1})`` —
    matching the project's analytical convention.
    """

    streams: tuple[StreamSpec, ...]
    coupling_j: ArrayF
    coupling_kc: ArrayF
    gamma: float = 1.0

    def num_streams(self) -> int:
        return len(self.streams)

    def policy_shape(self) -> tuple[int, ...]:
        return tuple(s.num_controls() for s in self.streams)

    def validate(self) -> None:
        if not self.streams:
            raise ValueError("CoupledEnsembleSpec.streams must be non-empty")
        for k, s in enumerate(self.streams):
            try:
                s.validate()
            except ValueError as exc:
                raise ValueError(f"stream[{k}] {s.name!r}: {exc}") from exc
        shape = self.policy_shape()
        if self.coupling_j.shape != shape:
            raise ValueError(f"coupling_j shape {self.coupling_j.shape} != policy_shape {shape}")
        if self.coupling_kc.shape != shape:
            raise ValueError(f"coupling_kc shape {self.coupling_kc.shape} != policy_shape {shape}")
        if self.gamma < 0.0:
            raise ValueError(f"gamma must be ≥0, got {self.gamma}")
