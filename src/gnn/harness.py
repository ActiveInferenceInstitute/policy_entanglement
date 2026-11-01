"""GNN -> pymdp-harness binding for the production K-stream ensemble.

This module realizes the *executable view* for the **production** simulation
harness, complementing :mod:`gnn.bridge` (which binds the policy-level toy).
The production ensemble that ``scripts/simulate_pymdp.py`` and the multi-K /
long-horizon / revertibility / robustness stages materialize is built by
:func:`simulation.builders.make_ising_ensemble` under the
:mod:`simulation.hyperparameters` constants.

:func:`ensemble_from_gnn` reconstructs
:class:`~simulation.specs.StreamSpec` /
:class:`~simulation.specs.CoupledEnsembleSpec` objects from the declarations of
``gnn/production_ensemble.gnn.md`` alone (per-stream ``A{k}``/``B{k}``/``C{k}``/
``D{k}`` factors, the joint coupling ``J``, and ``gamma``).  :func:`conformance_report`
compares that reconstruction elementwise against the production build, so the
GNN specification and the harness arrays cannot silently drift apart;
:func:`conformance_negative_control` proves the comparison is sensitive (a
control-slice swap in the spec must produce a non-zero difference).

The comparison is exact (zero tolerance): every production array is a small
rational matrix, so the GNN declaration and the builder must agree bit for bit.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from numpy.typing import NDArray

from gnn.bridge import build_joint_coupling, stream_cardinality
from gnn.model import GnnModel, GnnVariable
from simulation.builders import make_ising_ensemble
from simulation.hyperparameters import (
    PYMDP_ENSEMBLE_COUPLING_LAMBDA,
    PYMDP_ENSEMBLE_GAMMA,
    PYMDP_ENSEMBLE_K,
)
from simulation.specs import CoupledEnsembleSpec, StreamSpec

ArrayF = NDArray[np.float64]


def _factor(model: GnnModel, kind: str, stream: int) -> GnnVariable:
    """Look up the ``A{k}``/``B{k}``/``C{k}``/``D{k}`` factor declaration.

    Raises:
        ValueError: if the model declares no such factor.
    """
    name = f"{kind}{stream}"
    if not model.has(name):
        raise ValueError(f"GNN model {model.section!r} declares no per-stream factor {name!r}")
    return model.variable(name)


def per_stream_specs(model: GnnModel) -> list[StreamSpec]:
    """Build one :class:`~simulation.specs.StreamSpec` per declared stream.

    Stream ``k`` (1-indexed in GNN) is assembled from ``A{k}``, ``B{k}``,
    ``C{k}``, and ``D{k}`` and validated with the harness's own
    :meth:`~simulation.specs.StreamSpec.validate` shape/PMF contract.

    Raises:
        ValueError: if no streams are declared, a factor is missing, or a
            factor violates the :class:`StreamSpec` contract.
    """
    k = model.num_streams
    if k == 0:
        raise ValueError(f"GNN model {model.section!r} declares no policy streams (pi1, pi2, ...)")
    specs: list[StreamSpec] = []
    for i in range(1, k + 1):
        spec = StreamSpec(
            A=_factor(model, "A", i).matrix(),
            B=_factor(model, "B", i).matrix(),
            C=_factor(model, "C", i).vector(),
            D=_factor(model, "D", i).vector(),
            name=f"stream_{i - 1}",
        )
        try:
            spec.validate()
        except ValueError as exc:
            raise ValueError(f"GNN stream {i}: {exc}") from exc
        specs.append(spec)
    return specs


def ensemble_from_gnn(model: GnnModel) -> CoupledEnsembleSpec:
    """Build the coupled ensemble from the GNN declarations alone.

    Combines :func:`per_stream_specs` with the joint coupling assembled by
    :func:`gnn.bridge.build_joint_coupling` (single ``J`` for K=2, additive
    pairwise ``Jab`` for K>2), a zero ``K_c`` matrix, and the declared
    ``gamma`` scalar.

    Raises:
        ValueError: if the declared factors, coupling shape, or gamma violate
            the :class:`~simulation.specs.CoupledEnsembleSpec` contract.
    """
    streams = tuple(per_stream_specs(model))
    coupling_j = build_joint_coupling(model)
    shape = tuple(s.num_controls() for s in streams)
    if coupling_j.shape != shape:
        raise ValueError(f"GNN coupling shape {coupling_j.shape} != policy shape {shape}")
    gamma = model.variable("gamma").scalar() if model.has("gamma") else 0.0
    spec = CoupledEnsembleSpec(
        streams=streams,
        coupling_j=np.asarray(coupling_j, dtype=np.float64),
        coupling_kc=np.zeros(shape, dtype=np.float64),
        gamma=float(gamma),
    )
    spec.validate()
    return spec


def production_ensemble(
    *,
    num_streams: int | None = None,
    coupling_amplitude: float | None = None,
    gamma: float | None = None,
) -> CoupledEnsembleSpec:
    """The harness's production ensemble, built from :mod:`simulation.hyperparameters`.

    Defaults are the production constants
    (:data:`~simulation.hyperparameters.PYMDP_ENSEMBLE_K`,
    :data:`~simulation.hyperparameters.PYMDP_ENSEMBLE_COUPLING_LAMBDA`,
    :data:`~simulation.hyperparameters.PYMDP_ENSEMBLE_GAMMA`); the keyword
    overrides exist so the multi-K family (``MULTI_K_VALUES``) can be checked
    against the same GNN specification.
    """
    return make_ising_ensemble(
        coupling_amplitude=(
            float(PYMDP_ENSEMBLE_COUPLING_LAMBDA) if coupling_amplitude is None else float(coupling_amplitude)
        ),
        gamma=float(PYMDP_ENSEMBLE_GAMMA) if gamma is None else float(gamma),
        num_streams=int(PYMDP_ENSEMBLE_K) if num_streams is None else int(num_streams),
    )


def _max_abs_diff(left: ArrayF, right: ArrayF) -> float:
    """Largest absolute elementwise difference; ``inf`` on a shape mismatch."""
    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)
    if a.shape != b.shape:
        return float("inf")
    return float(np.abs(a - b).max()) if a.size else 0.0


@dataclass(frozen=True)
class EnsembleConformance:
    """Elementwise comparison of a GNN-declared ensemble against a reference build.

    Attributes:
        gnn_num_streams: Stream count declared by the GNN model.
        reference_num_streams: Stream count of the reference build.
        gnn_policy_shape: Per-stream control cardinalities from the GNN model.
        reference_policy_shape: Per-stream control cardinalities of the reference.
        per_stream_max_abs_diff: ``(A, B, C, D)`` max-abs-diff tuples, one per
            compared stream (in stream order, truncated to the shorter side).
        coupling_max_abs_diff: Max-abs-diff of the joint coupling tensors.
        gamma_abs_diff: Absolute difference of the sophistication weights.
    """

    gnn_num_streams: int
    reference_num_streams: int
    gnn_policy_shape: tuple[int, ...]
    reference_policy_shape: tuple[int, ...]
    per_stream_max_abs_diff: tuple[tuple[float, float, float, float], ...]
    coupling_max_abs_diff: float
    gamma_abs_diff: float

    @property
    def max_abs_diff(self) -> float:
        """Largest difference across every compared array."""
        values = [diff for row in self.per_stream_max_abs_diff for diff in row]
        values.extend([self.coupling_max_abs_diff, self.gamma_abs_diff])
        return float(max(values)) if values else 0.0

    @property
    def conformant(self) -> bool:
        """Whether the GNN-declared ensemble matches the reference exactly."""
        return (
            self.gnn_num_streams == self.reference_num_streams
            and self.gnn_policy_shape == self.reference_policy_shape
            and self.max_abs_diff == 0.0
        )

    def to_payload(self) -> dict[str, object]:
        """JSON-serializable evidence record for the pipeline sidecar."""
        return {
            "gnn_num_streams": int(self.gnn_num_streams),
            "reference_num_streams": int(self.reference_num_streams),
            "gnn_policy_shape": [int(d) for d in self.gnn_policy_shape],
            "reference_policy_shape": [int(d) for d in self.reference_policy_shape],
            "per_stream_max_abs_diff": [
                {"A": row[0], "B": row[1], "C": row[2], "D": row[3]} for row in self.per_stream_max_abs_diff
            ],
            "coupling_max_abs_diff": float(self.coupling_max_abs_diff),
            "gamma_abs_diff": float(self.gamma_abs_diff),
            "max_abs_diff": self.max_abs_diff,
            "conformant": self.conformant,
        }


def conformance_report(model: GnnModel, reference: CoupledEnsembleSpec) -> EnsembleConformance:
    """Compare a GNN-declared ensemble against a reference harness build.

    Every production array is compared elementwise with zero tolerance: the
    per-stream likelihoods/transitions/preferences/priors, the joint coupling,
    the sophistication weight, and the stream/control cardinalities.
    """
    gnn_spec = ensemble_from_gnn(model)
    per_stream: list[tuple[float, float, float, float]] = []
    for gnn_stream, ref_stream in zip(gnn_spec.streams, reference.streams, strict=False):
        per_stream.append(
            (
                _max_abs_diff(gnn_stream.A, ref_stream.A),
                _max_abs_diff(gnn_stream.B, ref_stream.B),
                _max_abs_diff(gnn_stream.C, ref_stream.C),
                _max_abs_diff(gnn_stream.D, ref_stream.D),
            )
        )
    return EnsembleConformance(
        gnn_num_streams=gnn_spec.num_streams(),
        reference_num_streams=reference.num_streams(),
        gnn_policy_shape=gnn_spec.policy_shape(),
        reference_policy_shape=reference.policy_shape(),
        per_stream_max_abs_diff=tuple(per_stream),
        coupling_max_abs_diff=_max_abs_diff(gnn_spec.coupling_j, reference.coupling_j),
        gamma_abs_diff=abs(float(gnn_spec.gamma) - float(reference.gamma)),
    )


def conformance_negative_control(model: GnnModel, reference: CoupledEnsembleSpec) -> float:
    """Max-abs-diff after swapping stream 1's control slices (non-vacuity control).

    The swap leaves every array shape and the column-stochastic contract intact
    but exchanges the declared "hold" and "swap" controls, so a conformance
    check that actually reads the declared transitions must report a non-zero
    difference.  Returns the resulting :attr:`EnsembleConformance.max_abs_diff`.
    """
    variable = _factor(model, "B", 1)
    swapped = replace(variable, value=variable.matrix()[:, :, ::-1])
    mutated = replace(model, variables={**model.variables, variable.name: swapped})
    return conformance_report(mutated, reference).max_abs_diff


def harness_config(model: GnnModel) -> dict[str, object]:
    """Emit the full pymdp-harness configuration from a GNN model.

    This is the production-harness counterpart of
    :func:`gnn.bridge.to_pymdp_config`: per-stream ``A``/``B``/``C``/``D``
    arrays, the joint coupling tensor, ``gamma``, stream count, and control
    cardinalities, sourced entirely from the ``.gnn`` declarations (consumed by
    ``scripts/gnn_to_pymdp.py --harness``).
    """
    spec = ensemble_from_gnn(model)
    return {
        "model_section": model.section,
        "num_streams": spec.num_streams(),
        "policy_cardinality_per_stream": stream_cardinality(model),
        "joint_coupling": spec.coupling_j.tolist(),
        "gamma": float(spec.gamma),
        "streams": [
            {
                "name": stream.name,
                "num_obs": stream.num_obs(),
                "num_states": stream.num_states(),
                "num_controls": stream.num_controls(),
                "A": stream.A.tolist(),
                "B": stream.B.tolist(),
                "C": stream.C.tolist(),
                "D": stream.D.tolist(),
            }
            for stream in spec.streams
        ],
    }
