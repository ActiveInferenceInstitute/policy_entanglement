"""K>2 multi-stream ensemble experiments.

The default pymdp harness in :mod:`simulation.inference` was sized
around the K=2 Ising toy (so the K=2 ↔ closed-form Ising channel
remains the canonical witness for §6 of the manuscript).  This module
is the implemented K=3 / K=4 generalization, built directly on the existing
:class:`simulation.specs.CoupledEnsembleSpec` infrastructure.

Each experiment:

  1. Builds a real K-stream Ising ensemble via
     :func:`simulation.builders.make_ising_ensemble`.
  2. Runs the pymdp 1.0.1 agents and the λ-coupling layer at every
     λ in :data:`simulation.hyperparameters.MULTI_K_SWEEP_LAMBDAS`.
  3. Records, for each λ: the joint policy posterior, its per-stream
     marginals, the total correlation $I(q_\\lambda)$ (multi-
     information), and the K-stream tensor-train rank profile.

No mocks: every number flows from pymdp's deterministic FPI on the
analytical layer.  The returned record type is JSON / CSV-friendly so
:mod:`scripts.simulate_multi_k` can emit witness CSVs directly.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from lean.free_energy import joint_entropy, shannon_entropy, total_correlation
from lean.joint_dist import joint_marginals
from lean.spectral import tensor_train_ranks

from . import hyperparameters as H  # noqa: N812
from .agents import _require_pymdp
from .builders import make_ising_ensemble
from .inference import coupled_policy_posterior
from .metrics import aligned_hypercube_mass as _aligned_mass
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class MultiKResult:
    """One (K, λ) experiment row.

    * ``K``                   — number of streams in the ensemble.
    * ``lam``                 — coupling strength at this sample.
    * ``total_correlation``   — multi-information $I(q_\\lambda)$ in nats.
    * ``marginal_entropies``  — $H(q_\\lambda^k)$ per stream.
    * ``joint_entropy``       — $H(q_\\lambda)$ in nats.
    * ``coupling_term``       — $\\lambda \\cdot \\langle J\\rangle_{q_\\lambda}$.
    * ``tt_ranks``            — tensor-train bond dimensions
      $(r_1, \\dots, r_{K-1})$ across canonical left-to-right cuts.
    * ``aligned_mass``        — joint probability mass on the two
      fully-aligned policies (``(0,..,0)`` and ``(1,..,1)``); a
      simple low-dimensional summary of "coupling tax".
    """

    K: int
    lam: float
    total_correlation: float
    marginal_entropies: tuple[float, ...]
    joint_entropy: float
    coupling_term: float
    tt_ranks: tuple[int, ...]
    aligned_mass: float


def run_multi_k_sweep(
    K: int,  # noqa: N803 — K = number of streams (manuscript symbol).
    lams: Sequence[float],
    *,
    coupling_lambda_gen: float,
    gamma: float,
    observations: Sequence[int] | None = None,
) -> list[MultiKResult]:
    """Run the full λ-sweep for a K-stream Ising ensemble.

    ``coupling_lambda_gen`` is the coupling strength baked into
    :func:`make_ising_ensemble` (it scales the Ising J tensor);
    ``lams`` is the λ probe grid driving
    :func:`coupled_policy_posterior`.  These are independent: the
    generator scale fixes the *shape* of the coupling and the probe
    sweeps the deformation strength.
    """
    if K < 2:
        raise ValueError(f"multi-K experiment requires K>=2, got K={K}")
    _require_pymdp()
    spec: CoupledEnsembleSpec = make_ising_ensemble(
        coupling_amplitude=float(coupling_lambda_gen),
        num_streams=int(K),
        gamma=float(gamma),
    )
    if observations is None:
        observations = tuple(0 for _ in range(K))
    if len(observations) != K:
        raise ValueError(f"observations length {len(observations)} != K={K}")
    obs = list(observations)
    out: list[MultiKResult] = []
    for lam in lams:
        lam_f = float(lam)
        q = coupled_policy_posterior(spec, obs, lam=lam_f)
        margs = joint_marginals(q)
        # Use the canonical Shannon-entropy primitive from
        # `free_energy` so the K>2 paths share semantics with K=2
        # (RedTeam Methods M1, 2026-05-20: the prior inline `m[m>0] *
        # log(m[m>0])` form was a copy of `shannon_entropy` that
        # silently failed to propagate any future change to the
        # primitive — e.g. a log-floor swap).
        H_marg = tuple(shannon_entropy(m) for m in margs)  # noqa: N806
        H_joint = joint_entropy(q)  # noqa: N806
        out.append(
            MultiKResult(
                K=int(K),
                lam=lam_f,
                total_correlation=float(total_correlation(q)),
                marginal_entropies=H_marg,
                joint_entropy=H_joint,
                coupling_term=lam_f * float((q * spec.coupling_j).sum()),
                tt_ranks=tuple(int(r) for r in tensor_train_ranks(q, atol=float(H.SPECTRAL_RANK_ATOL))),
                aligned_mass=_aligned_mass(q),
            )
        )
    return out


def multi_k_joint_snapshot(
    K: int,  # noqa: N803 — K = number of streams (manuscript symbol).
    lam: float,
    *,
    coupling_lambda_gen: float,
    gamma: float,
    observations: Sequence[int] | None = None,
) -> ArrayF:
    """Single ``(2,2,...,2)`` joint policy snapshot at one (K, λ) point."""
    if K < 2:
        raise ValueError(f"K must be ≥ 2, got {K}")
    _require_pymdp()
    spec = make_ising_ensemble(
        coupling_amplitude=float(coupling_lambda_gen),
        num_streams=int(K),
        gamma=float(gamma),
    )
    if observations is None:
        observations = tuple(0 for _ in range(K))
    return coupled_policy_posterior(spec, list(observations), lam=float(lam))


def multi_k_summary(results: Sequence[MultiKResult]) -> dict[str, float]:
    """Per-experiment summary used to populate manuscript variables.

    Returns a flat dict of `<prefix>_<stat>` keys.  Stable shape; the
    caller is expected to prefix the keys with the corresponding K
    when merging into the global variables JSON.
    """
    if not results:
        raise ValueError("multi_k_summary requires at least one result")
    tcs = np.array([r.total_correlation for r in results], dtype=np.float64)
    lams = np.array([r.lam for r in results], dtype=np.float64)
    coup = np.array([r.coupling_term for r in results], dtype=np.float64)
    aligned = np.array([r.aligned_mass for r in results], dtype=np.float64)
    # Maximum TT bond dimension at the saturating λ (last entry).
    tt_last = results[-1].tt_ranks
    return {
        "K": float(results[0].K),
        "lambda_min": float(lams.min()),
        "lambda_max": float(lams.max()),
        "tc_min": float(tcs.min()),
        "tc_max": float(tcs.max()),
        "tc_at_lambda_max": float(tcs[-1]),
        "coupling_term_min": float(coup.min()),
        "coupling_term_max": float(coup.max()),
        "aligned_mass_at_lambda_zero": float(aligned[0]),
        "aligned_mass_at_lambda_max": float(aligned[-1]),
        "tt_rank_max_at_lambda_max": float(max(tt_last) if tt_last else 0),
        "tt_rank_sum_at_lambda_max": float(sum(tt_last)),
    }


__all__ = [
    "MultiKResult",
    "multi_k_joint_snapshot",
    "multi_k_summary",
    "run_multi_k_sweep",
]
