"""POMDP simulation harness for coupled-policy active-inference ensembles.
"""

from __future__ import annotations

from specs import CoupledEnsembleSpec, StreamSpec  # noqa: F401
from builders import (  # noqa: F401
    ising_coupling_tensor,
    make_bernoulli_stream,
    make_ising_ensemble,
    two_action_swap_transitions,
    two_state_identity_likelihood,
)
from agents import (  # noqa: F401
    PYMDP_INSTALL_HINT,
    build_pymdp_agent,
    build_pymdp_agents,
    pymdp_available,
)
from inference import (  # noqa: F401
    coupled_policy_posterior,
    per_stream_efe,
    per_stream_policy_posterior,
)
from rollout import (  # noqa: F401
    Rollout,
    RolloutStep,
    simulate_coupled_rollout,
)
from sweep import (  # noqa: F401
    LambdaSweepResult,
    lambda_sweep,
    marginal_trajectory,
    total_correlation_curve,
)

__all__ = [
    # specs
    "StreamSpec",
    "CoupledEnsembleSpec",
    # builders
    "ising_coupling_tensor",
    "make_bernoulli_stream",
    "make_ising_ensemble",
    "two_action_swap_transitions",
    "two_state_identity_likelihood",
    # agents
    "PYMDP_INSTALL_HINT",
    "build_pymdp_agent",
    "build_pymdp_agents",
    "pymdp_available",
    # inference
    "coupled_policy_posterior",
    "per_stream_efe",
    "per_stream_policy_posterior",
    # rollout
    "Rollout",
    "RolloutStep",
    "simulate_coupled_rollout",
    # sweep
    "LambdaSweepResult",
    "lambda_sweep",
    "marginal_trajectory",
    "total_correlation_curve",
]
