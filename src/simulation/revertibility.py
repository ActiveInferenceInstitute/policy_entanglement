"""Revertibility / m-projection back-to-mean-field witness.

Manuscript §9.4 / §9.5 introduce **revertibility**: the property that
from any λ-entangled joint posterior $q_\\lambda$ over the joint
policy space, an agent can dual-flat m-project back onto the mean-
field submanifold and *exactly* recover its per-stream marginals.

Formally, with $q_\\lambda$ the entangled posterior and
$\\hat m(q_\\lambda) = \\prod_k q^k_\\lambda$ the m-projection:

  1. ``marginals(q_λ) == marginals(m(q_λ))`` exactly (revertibility).
  2. ``KL(q_λ ‖ m(q_λ)) == I(q_λ)`` (Prop 7.3 / Theorem 5.1).

Both identities are checked here on the K=2 Ising harness as well as
on the K>2 generalization via :mod:`simulation.multi_k_experiments`.
No mocks: the functions run real pymdp agents and the analytical
coupling layer, then verify the algebraic identities to floating
tolerance.

Two-line interpretation: the second identity says "the multi-
information $I(q_\\lambda)$ is the KL cost of *replacing* $q_\\lambda$
by its mean-field projection".  When this identity holds to floating
tolerance, the agent can revert without information loss except for
the multi-information it must pay back to coupling.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from lean.free_energy import kl_divergence, total_correlation
from lean.joint_dist import joint_marginals, m_projection
from simulation.hyperparameters import REVERTIBILITY_KL_IDENTITY_TOLERANCE

from .agents import _require_pymdp
from .builders import make_ising_ensemble
from .inference import coupled_policy_posterior
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class RevertibilityRecord:
    """Outcome of the m-projection witness at one λ.

    * ``lam``                 — coupling strength.
    * ``multi_information``   — $I(q_\\lambda)$ (multi-information).
    * ``kl_q_to_mproj``       — $D_{\\text{KL}}(q_\\lambda \\,\\|\\, \\hat m(q_\\lambda))$.
    * ``kl_identity_residual``— |KL − I|, ought to be 0.
    * ``marginal_max_abs_diff``— Per-stream max $|q^k_\\lambda(\\pi) -
      \\hat m(q_\\lambda)^k(\\pi)|$ across all $\\pi$ and $k$.
    * ``marginals_match``     — True iff
      ``marginal_max_abs_diff <= tol``.
    * ``kl_identity_holds``   — True iff
      ``kl_identity_residual <= kl_identity_tol``.
    * ``revertible``          — Conjunction of the two booleans.
    """

    lam: float
    multi_information: float
    kl_q_to_mproj: float
    kl_identity_residual: float
    marginal_max_abs_diff: float
    marginals_match: bool
    kl_identity_holds: bool
    revertible: bool


def _spec(
    *,
    num_streams: int,
    coupling_lambda_gen: float,
    gamma: float,
) -> CoupledEnsembleSpec:
    """Build the K-stream Ising ensemble spec for a revertibility run.

    Thin convenience wrapper around :func:`make_ising_ensemble` that
    factors the call site for :func:`revertibility_test`.
    """
    return make_ising_ensemble(
        coupling_amplitude=float(coupling_lambda_gen),
        num_streams=int(num_streams),
        gamma=float(gamma),
    )


def m_projection_witness(
    q: ArrayF,
    *,
    tolerance: float,
    kl_identity_tolerance: float,
    lam: float,
) -> RevertibilityRecord:
    """Run the revertibility identities on a *given* joint policy posterior.

    Decoupled from pymdp so the same function is reusable across the
    analytical Ising mirror and the pymdp-grounded ensemble.
    """
    margs = joint_marginals(q)
    mproj = m_projection(q)
    mproj_margs = joint_marginals(mproj)

    max_diff = 0.0
    for q_k, mp_k in zip(margs, mproj_margs, strict=True):
        max_diff = max(max_diff, float(np.max(np.abs(q_k - mp_k))))

    I_q = float(total_correlation(q))  # noqa: N806 — I = multi-information (manuscript symbol).
    kl_q_m = float(kl_divergence(q, mproj))
    residual = float(abs(kl_q_m - I_q))

    marg_match = bool(max_diff <= float(tolerance))
    kl_match = bool(residual <= float(kl_identity_tolerance))
    return RevertibilityRecord(
        lam=float(lam),
        multi_information=I_q,
        kl_q_to_mproj=kl_q_m,
        kl_identity_residual=residual,
        marginal_max_abs_diff=max_diff,
        marginals_match=marg_match,
        kl_identity_holds=kl_match,
        revertible=bool(marg_match and kl_match),
    )


def revertibility_test(
    *,
    num_streams: int,
    coupling_lambda_gen: float,
    gamma: float,
    lambda_values: Sequence[float],
    tolerance: float,
    kl_identity_tolerance: float,
    observations: Sequence[int] | None = None,
) -> list[RevertibilityRecord]:
    """For every λ in ``lambda_values``: compute the coupled joint via
    pymdp + the analytical coupling layer, m-project it back, and run
    the two revertibility identities.

    Returns one :class:`RevertibilityRecord` per λ.
    """
    _require_pymdp()
    spec = _spec(
        num_streams=int(num_streams),
        coupling_lambda_gen=float(coupling_lambda_gen),
        gamma=float(gamma),
    )
    if observations is None:
        observations = tuple(0 for _ in range(int(num_streams)))
    if len(observations) != int(num_streams):
        raise ValueError(f"observations length {len(observations)} != num_streams={num_streams}")
    obs = list(observations)
    out: list[RevertibilityRecord] = []
    for lam in lambda_values:
        q = coupled_policy_posterior(spec, obs, lam=float(lam))
        out.append(
            m_projection_witness(
                q,
                tolerance=float(tolerance),
                kl_identity_tolerance=float(kl_identity_tolerance),
                lam=float(lam),
            )
        )
    return out


def revertibility_summary(records: Sequence[RevertibilityRecord]) -> dict[str, float]:
    """Manuscript-variable-ready scalars from a revertibility sweep."""
    if not records:
        raise ValueError("revertibility_summary requires at least one record")
    kl_residuals = np.array([r.kl_identity_residual for r in records], dtype=np.float64)
    marg_diffs = np.array([r.marginal_max_abs_diff for r in records], dtype=np.float64)
    # Is = list of I(q_λ) values; I = multi-information (manuscript symbol).
    Is = np.array(  # noqa: N806
        [r.multi_information for r in records], dtype=np.float64
    )
    kls = np.array([r.kl_q_to_mproj for r in records], dtype=np.float64)
    return {
        "revertibility_num_lambdas": float(len(records)),
        "revertibility_max_kl_residual": float(kl_residuals.max()),
        "revertibility_mean_kl_residual": float(kl_residuals.mean()),
        "revertibility_max_marginal_diff": float(marg_diffs.max()),
        "revertibility_all_revertible": (1.0 if all(r.revertible for r in records) else 0.0),
        "revertibility_all_kl_identity_holds": (1.0 if all(r.kl_identity_holds for r in records) else 0.0),
        "revertibility_all_marginals_match": (1.0 if all(r.marginals_match for r in records) else 0.0),
        "revertibility_multi_info_max": float(Is.max()),
        "revertibility_kl_to_mproj_max": float(kls.max()),
    }


# ---------------------------------------------------------------------------
# Dashboard invariant helper
# ---------------------------------------------------------------------------


def revertibility_kl_equals_multiinformation_witness(
    records: Sequence[RevertibilityRecord],
) -> dict[str, object]:
    """Return a structured witness for the
    ``KL(q_λ ‖ m(q_λ)) == I(q_λ)`` identity.

    Shape mirrors the witness dicts consumed by
    :class:`reporting.interactive_dashboard.Invariant`: ``name`` /
    ``actual`` / ``expected`` / ``tol`` / ``kind`` / ``description``.
    """
    residuals = [float(r.kl_identity_residual) for r in records]
    return {
        "name": "revertibility_kl_equals_multiinformation",
        "actual": float(max(residuals)) if residuals else 0.0,
        "expected": 0.0,
        # FIXED, observation-independent tolerance (RedTeam 2026-05-19
        # C2): the prior `max(residuals) + 1e-9` set the threshold equal
        # to the observed value, so `actual <= tol` held BY CONSTRUCTION
        # — an unfailable gate (the purest shape-test-doesn't-bind-truth
        # defect). The gate now genuinely discriminates: it fails iff the
        # worst residual exceeds the same fixed constant the per-record
        # check (`_record`, kl_identity_tolerance) uses.
        "tol": float(REVERTIBILITY_KL_IDENTITY_TOLERANCE),
        "kind": "equal",
        "description": (
            "For every λ in the revertibility sweep, "
            "KL(q_λ ‖ m(q_λ)) equals the multi-information I(q_λ) to "
            "floating-point tolerance — Prop 7.3 / Theorem 5.1 numerical "
            "witness on the pymdp K-stream ensemble."
        ),
    }


__all__ = [
    "RevertibilityRecord",
    "m_projection_witness",
    "revertibility_kl_equals_multiinformation_witness",
    "revertibility_summary",
    "revertibility_test",
]
