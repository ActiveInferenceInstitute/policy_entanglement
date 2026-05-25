"""Per-stream POMDP inference plus the λ-coupled joint policy posterior."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from lean.coupling import entangled_posterior
from lean.decomposition import (
    entanglement_decomposition_rhs,
    free_energy_against_entangled_prior,
)
from lean.free_energy import shannon_entropy, total_correlation
from lean.joint_dist import joint_marginals, normalize

from .agents import _require_pymdp, build_pymdp_agents
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]
# Callers pass either Python lists or numpy float arrays as 1-D grids.
FloatGrid = Sequence[float] | NDArray[np.float64]
jnp: Any

try:
    import jax.numpy

    # Assignment (not ``import ... as jnp``) so the optional dep does not
    # re-bind the ``jnp: Any`` declaration above — mypy ``no-redef`` clean
    # without an inline ``# type: ignore`` (the repo's lint hooks strip those).
    jnp = jax.numpy
except Exception:  # pragma: no cover
    jnp = None


def _validate_observations(spec: CoupledEnsembleSpec, observations: Sequence[int]) -> None:
    if len(observations) != spec.num_streams():
        raise ValueError(f"observations length {len(observations)} != K={spec.num_streams()}")


def _run_pymdp_per_stream(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
) -> tuple[list[ArrayF], list[ArrayF]]:
    """Run pymdp's per-stream ``infer_states → infer_policies`` once per
    stream and return ``(q_pi_list, G_list)``.

    * ``q_pi_list[k]`` is the normalized policy posterior of stream ``k``
      (1-D PMF of length ``num_controls_k``).
    * ``G_list[k]`` is the EFE vector of stream ``k`` (1-D ndarray of
      length ``num_controls_k``; pymdp's convention, smaller is preferred).

    Single source of truth for both :func:`per_stream_efe` and
    :func:`per_stream_policy_posterior`; preserves the K pymdp calls each
    of those public helpers makes individually.
    """
    _require_pymdp()
    _validate_observations(spec, observations)
    agents = build_pymdp_agents(spec)
    q_pi_list: list[ArrayF] = []
    G_list: list[ArrayF] = []
    for k, (agent, obs) in enumerate(zip(agents, observations, strict=True)):
        D_list = [jnp.asarray(spec.streams[k].D, dtype=jnp.float32)[None, ...]]
        qs = agent.infer_states([jnp.asarray([obs])], D_list)
        q_pi, G = agent.infer_policies(qs)
        q_pi_list.append(normalize(np.asarray(q_pi, dtype=np.float64).reshape(-1)))
        G_list.append(np.asarray(G, dtype=np.float64).reshape(-1))
    return q_pi_list, G_list


def per_stream_efe(spec: CoupledEnsembleSpec, observations: Sequence[int]) -> list[ArrayF]:
    """Per-stream EFE vectors `(G_0, G_1, ..., G_{K-1})` from running
    pymdp's policy inference once per stream.

    Each `G_k` is a 1-D ndarray of length ``num_controls_k``; signs
    follow pymdp's convention where smaller `G` is preferred.
    """
    _q_pi_list, G_list = _run_pymdp_per_stream(spec, observations)
    return G_list


def per_stream_policy_posterior(spec: CoupledEnsembleSpec, observations: Sequence[int]) -> list[ArrayF]:
    """Per-stream policy posterior `(q_0, q_1, ..., q_{K-1})` from
    running pymdp's `infer_policies` once per stream.

    Returns a list of 1-D PMFs of length ``num_controls_k``.  These are
    the mean-field marginals of the *uncoupled* (λ=0) joint policy
    posterior — the input to the project's analytical coupling layer.
    """
    q_pi_list, _G_list = _run_pymdp_per_stream(spec, observations)
    return q_pi_list


@dataclass(frozen=True)
class FreeEnergyBundle:
    """Every free-energy / information observable we read off the
    λ-coupled posterior at a single ``lam``.

    All quantities are derived from real ``pymdp.agent.Agent`` outputs
    plus the analytical λ-coupling layer; nothing is mocked.

    * ``vfe_per_stream``     — variational free energy
      $F[q^k] = \\langle \\log q^k - \\log E_k - (-\\gamma G_k) \\rangle_{q^k}$
      computed from the *coupled* marginals (length-K array).
    * ``vfe_total``          — sum of ``vfe_per_stream``.
    * ``efe_per_stream``     — pymdp's own EFE vector for each stream
      (length-K list of arrays of length ``num_controls_k``).
    * ``efe_under_posterior`` — expected EFE under the coupled posterior:
      $\\langle G_k \\rangle_{q^k_\\lambda}$ per stream.
    * ``joint_entropy``      — $H(q_\\lambda)$ in nats.
    * ``marginal_entropies`` — $H(q^k_\\lambda)$ per stream.
    * ``total_correlation``  — $I(q_\\lambda) = \\sum_k H(q^k) - H(q)$.
    * ``coupling_term``      — $\\lambda \\langle J \\rangle_{q_\\lambda}$,
      i.e. the policy-coupling contribution to the free energy.
    * ``action_distribution`` — probability of each joint policy
      $\\pi \\in \\prod_k \\Pi^k$ (the joint posterior reshaped to flat).
    """

    lam: float
    vfe_per_stream: ArrayF
    vfe_total: float
    efe_per_stream: tuple[ArrayF, ...]
    efe_under_posterior: ArrayF
    joint_entropy: float
    marginal_entropies: ArrayF
    total_correlation: float
    coupling_term: float
    action_distribution: ArrayF


@dataclass(frozen=True)
class DecompositionWitness:
    """Positive-λ decomposition identity witness for a pymdp-backed posterior.

    ``lhs`` is :func:`lean.decomposition.free_energy_against_entangled_prior`;
    ``rhs`` is
    :func:`lean.decomposition.entanglement_decomposition_rhs(...).total`.
    The per-stream G vectors are zeroed because pymdp has already
    folded those EFE terms into its per-stream policy posteriors before
    the analytical coupling layer is applied.
    """

    lam: float
    lhs: float
    rhs: float
    residual: float


def _variational_free_energy_from_parts(
    spec: CoupledEnsembleSpec,
    margs: list[ArrayF],
    G_per_stream: list[ArrayF],  # noqa: N803 — G = expected free energy (manuscript symbol).
) -> ArrayF:
    """Compute per-stream VFE from pre-computed marginals and EFE vectors.

    Avoids redundant pymdp calls when the caller already holds ``q``
    and ``G_per_stream``.  ``F[q^k] = ⟨log q^k⟩ − ⟨log E_k⟩ + γ⟨G_k⟩``.
    """
    out = np.zeros(spec.num_streams(), dtype=np.float64)
    for k, (m, G_k) in enumerate(zip(margs, G_per_stream, strict=True)):
        s = spec.streams[k]
        log_E = np.log(np.where(s.D > 0.0, s.D, 1e-300))
        log_q = np.log(np.where(m > 0.0, m, 1e-300))
        out[k] = float((m * log_q).sum() - (m * log_E).sum() + spec.gamma * float((m * G_k).sum()))
    return out


def variational_free_energy(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lam: float,
) -> ArrayF:
    """Per-stream variational free energy under the λ-coupled posterior.

    For each stream `k`, ``F[q^k_λ] = E_q[log q^k] - E_q[log E_k] +
    γ · E_q[G_k]`` where the marginals come from the λ-coupled joint.
    Returns a length-K array of floats.

    The decomposition is structurally identical to pymdp's per-factor
    VFE; we evaluate it directly on the coupled marginals so the
    λ-deformation's effect on free energy is observable.
    """
    _require_pymdp()
    spec.validate()
    q = coupled_policy_posterior(spec, observations, lam)
    margs = joint_marginals(q)
    G_per_stream = per_stream_efe(spec, observations)
    return _variational_free_energy_from_parts(spec, margs, G_per_stream)


def expected_free_energy_under_posterior(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lam: float,
) -> ArrayF:
    """``⟨G_k⟩_{q^k_λ}`` per stream — the EFE evaluated under the
    coupled posterior's marginals (rather than at a single policy).

    Returns a length-K array of floats.  Useful for plotting how
    coupling shifts the agent's *expected* EFE: at small λ this
    matches the mean-field EFE, at large λ it bends toward the EFE
    of the dominant archetype.
    """
    _require_pymdp()
    spec.validate()
    q = coupled_policy_posterior(spec, observations, lam)
    margs = joint_marginals(q)
    G = per_stream_efe(spec, observations)
    return np.array(
        [float((m * g).sum()) for m, g in zip(margs, G, strict=True)],
        dtype=np.float64,
    )


def coupling_energy(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lam: float,
) -> float:
    """``λ · ⟨J(π)⟩_{q_λ}`` — the policy-coupling contribution to
    the free energy of the coupled posterior.  At ``lam = 0`` this is zero.
    """
    _require_pymdp()
    spec.validate()
    q = coupled_policy_posterior(spec, observations, lam)
    return float(lam) * float((q * spec.coupling_j).sum())


def free_energy_bundle(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lam: float,
) -> FreeEnergyBundle:
    """One-shot computation of every observable in :class:`FreeEnergyBundle`.

    Calls pymdp exactly once (K agents for EFE) and the analytical coupling
    layer once (for the joint posterior).  All derived quantities reuse those
    two results — no redundant forward passes.
    """
    _require_pymdp()
    spec.validate()
    q = coupled_policy_posterior(spec, observations, lam)
    margs = joint_marginals(q)
    G_per_stream = per_stream_efe(spec, observations)

    vfe = _variational_free_energy_from_parts(spec, margs, G_per_stream)
    efe_post = np.array(
        [float((m * g).sum()) for m, g in zip(margs, G_per_stream, strict=True)],
        dtype=np.float64,
    )
    H_joint = shannon_entropy(q.reshape(-1))
    H_marg = np.array(
        [shannon_entropy(m) for m in margs],
        dtype=np.float64,
    )
    return FreeEnergyBundle(
        lam=float(lam),
        vfe_per_stream=vfe,
        vfe_total=float(vfe.sum()),
        efe_per_stream=tuple(np.asarray(g, dtype=np.float64) for g in G_per_stream),
        efe_under_posterior=efe_post,
        joint_entropy=float(H_joint),
        marginal_entropies=H_marg,
        total_correlation=float(total_correlation(q)),
        coupling_term=float(lam) * float((q * spec.coupling_j).sum()),
        action_distribution=q.reshape(-1).copy(),
    )


def free_energy_curve(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lams: FloatGrid,
) -> list[FreeEnergyBundle]:
    """Apply :func:`free_energy_bundle` across a λ grid."""
    return [free_energy_bundle(spec, observations, float(lam_val)) for lam_val in lams]


def decomposition_witness_curve(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lams: FloatGrid,
) -> list[DecompositionWitness]:
    """Evaluate Theorem 5.1's numerical LHS/RHS residual on a pymdp sweep.

    The function runs pymdp once to obtain the uncoupled per-stream
    policy posterior, then evaluates the analytical entangled posterior
    and the four-term decomposition on every configured λ.  We pass
    zero per-stream ``G`` vectors to the decomposition layer for the
    same reason as :func:`coupled_policy_posterior`: pymdp's
    ``infer_policies`` has already baked expected free energy into the
    mean-field posterior, so reusing the raw EFE vectors here would
    double-count them.
    """
    _require_pymdp()
    spec.validate()
    _validate_observations(spec, observations)
    mf = per_stream_policy_posterior(spec, observations)
    zero_g = [np.zeros_like(m, dtype=np.float64) for m in mf]
    out: list[DecompositionWitness] = []
    for lam_val in lams:
        lam = float(lam_val)
        q = entangled_posterior(
            mf_prior=mf,
            per_stream_G=zero_g,
            coupling_j=spec.coupling_j,
            coupling_kc=spec.coupling_kc,
            gamma=spec.gamma,
            lam=lam,
        )
        lhs = free_energy_against_entangled_prior(
            q,
            mf,
            zero_g,
            spec.coupling_j,
            spec.coupling_kc,
            spec.gamma,
            lam,
        )
        rhs = entanglement_decomposition_rhs(
            q,
            mf,
            zero_g,
            spec.coupling_j,
            spec.coupling_kc,
            spec.gamma,
            lam,
        ).total
        out.append(
            DecompositionWitness(
                lam=lam,
                lhs=float(lhs),
                rhs=float(rhs),
                residual=float(abs(lhs - rhs)),
            )
        )
    return out


def coupled_policy_posterior(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lam: float,
    *,
    precomputed_mf: Sequence[ArrayF] | None = None,
) -> ArrayF:
    """λ-coupled joint policy posterior.

    Layered design: pymdp owns the per-stream mean-field policy
    posterior (which already absorbs the EFE via its internal
    ``γ·G`` softmax); the analytical coupling layer
    (:func:`coupling.entangled_posterior`) adds the cross-stream
    `λ·J` / `γ·λ·K_c` factors on top.  At ``lam=0`` the joint is
    therefore *exactly* the outer product of the pymdp posteriors
    — the mean-field baseline.

    **Implementation note:**  The per-stream EFE vectors ``G`` are
    *zeroed* when passed to the analytical coupling layer because
    pymdp has already applied ``γ·G`` inside its own softmax.  The
    coupling layer only adds the ``γ·λ·K_c`` cross-stream term that
    pymdp does not know about.

    Returns a normalized joint policy tensor of shape
    ``spec.policy_shape()``.
    """
    _require_pymdp()
    spec.validate()
    # RedTeam Methods C6 (2026-05-20): accept an optional precomputed
    # `mf` to avoid re-running pymdp inference in rollout loops that
    # already computed it.  Backward-compatible default: pass `None`
    # to trigger a fresh `per_stream_policy_posterior` call.
    mf: list[ArrayF] = (
        per_stream_policy_posterior(spec, observations) if precomputed_mf is None else list(precomputed_mf)
    )
    # `entangled_posterior` re-applies γ to the per-stream G; pass zeros so we
    # do not double-count the EFE that pymdp has already baked into `mf`.
    zero_g = [np.zeros_like(m, dtype=np.float64) for m in mf]
    q = entangled_posterior(
        mf_prior=mf,
        per_stream_G=zero_g,
        coupling_j=spec.coupling_j,
        coupling_kc=spec.coupling_kc,
        gamma=spec.gamma,
        lam=float(lam),
    )
    return np.asarray(q, dtype=np.float64)
