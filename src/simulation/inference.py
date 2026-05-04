"""Per-stream POMDP inference plus the λ-coupled joint policy posterior.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from coupling import entangled_posterior
from joint_dist import normalize

from agents import _require_pymdp, build_pymdp_agents
from specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]

try:
    import jax.numpy as jnp  # type: ignore[import-not-found]

    _HAS_JAX = True
except Exception:  # pragma: no cover
    jnp = None  # type: ignore[assignment]
    _HAS_JAX = False


def _validate_observations(spec: CoupledEnsembleSpec, observations: Sequence[int]) -> None:
    if len(observations) != spec.K():
        raise ValueError(
            f"observations length {len(observations)} != K={spec.K()}"
        )


def per_stream_efe(
    spec: CoupledEnsembleSpec, observations: Sequence[int]
) -> list[ArrayF]:
    """Per-stream EFE vectors `(G_0, G_1, ..., G_{K-1})` from running
    pymdp's policy inference once per stream.

    Each `G_k` is a 1-D ndarray of length ``num_controls_k``; signs
    follow pymdp's convention where smaller `G` is preferred.
    """
    _require_pymdp()
    _validate_observations(spec, observations)
    agents = build_pymdp_agents(spec)
    out: list[ArrayF] = []
    for k, (agent, obs) in enumerate(zip(agents, observations)):
        D_list = [jnp.asarray(spec.streams[k].D, dtype=jnp.float32)[None, ...]]
        qs = agent.infer_states([jnp.asarray([obs])], D_list)
        _q_pi, G = agent.infer_policies(qs)
        out.append(np.asarray(G, dtype=np.float64).reshape(-1))
    return out


def per_stream_policy_posterior(
    spec: CoupledEnsembleSpec, observations: Sequence[int]
) -> list[ArrayF]:
    """Per-stream policy posterior `(q_0, q_1, ..., q_{K-1})` from
    running pymdp's `infer_policies` once per stream.

    Returns a list of 1-D PMFs of length ``num_controls_k``.  These are
    the mean-field marginals of the *uncoupled* (λ=0) joint policy
    posterior — the input to the project's analytical coupling layer.
    """
    _require_pymdp()
    _validate_observations(spec, observations)
    agents = build_pymdp_agents(spec)
    out: list[ArrayF] = []
    for k, (agent, obs) in enumerate(zip(agents, observations)):
        D_list = [jnp.asarray(spec.streams[k].D, dtype=jnp.float32)[None, ...]]
        qs = agent.infer_states([jnp.asarray([obs])], D_list)
        q_pi, _G = agent.infer_policies(qs)
        q_pi_np = np.asarray(q_pi, dtype=np.float64).reshape(-1)
        out.append(normalize(q_pi_np))
    return out


def coupled_policy_posterior(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lam: float,
) -> ArrayF:
    """λ-coupled joint policy posterior.

    Layered design: pymdp owns the per-stream mean-field policy
    posterior (which already absorbs the EFE via its internal
    ``γ·G`` softmax); the analytical coupling layer
    (:func:`coupling.entangled_posterior`) adds the cross-stream
    `λ·J` / `γ·λ·K_c` factors on top.  At ``lam=0`` the joint is
    therefore *exactly* the outer product of the pymdp posteriors
    — the mean-field baseline.

    Returns a normalised joint policy tensor of shape
    ``spec.policy_shape()``.
    """
    _require_pymdp()
    spec.validate()
    mf = per_stream_policy_posterior(spec, observations)
    # `entangled_posterior` re-applies γ to the per-stream G; pass zeros so we
    # do not double-count the EFE that pymdp has already baked into `mf`.
    zero_G = [np.zeros_like(m, dtype=np.float64) for m in mf]
    return entangled_posterior(
        mf_prior=mf,
        per_stream_G=zero_G,
        coupling_J=spec.coupling_J,
        coupling_Kc=spec.coupling_Kc,
        gamma=spec.gamma,
        lam=float(lam),
    )
