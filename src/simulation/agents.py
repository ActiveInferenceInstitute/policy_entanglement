"""pymdp 1.0.1 :class:`Agent` adapters."""

from __future__ import annotations

from typing import Any

from .specs import CoupledEnsembleSpec, StreamSpec

PYMDP_INSTALL_HINT = "pymdp 1.0.1 is required for the POMDP simulation harness. Install with: `uv sync --group sim`"
jnp: Any

try:
    import warnings

    import jax
    import jax.numpy

    # Bind via assignment (not ``import ... as jnp``) so the optional dep does
    # not re-bind the module-level ``jnp: Any`` declaration — keeps mypy's
    # ``no-redef`` quiet without an inline ``# type: ignore`` (which the repo's
    # lint hooks strip).
    jnp = jax.numpy

    # pymdp 1.0.1 stores some JAX arrays as Equinox static fields and emits a
    # benign UserWarning at Agent construction time.  Silence only that single
    # message so we do not mask other JAX warnings.
    warnings.filterwarnings(
        "ignore",
        message=r"A JAX array is being set as static!.*",
        category=UserWarning,
    )
    from pymdp.agent import Agent  # pymdp 1.0.1 (JAX-based)

    _HAS_PYMDP = True
except ImportError:  # pragma: no cover - covered by skip in tests
    _HAS_PYMDP = False
    Agent = None
    jnp = None


def pymdp_available() -> bool:
    """Return True iff `inferactively-pymdp` 1.0.1 is importable."""
    return _HAS_PYMDP


def _require_pymdp() -> None:
    if not _HAS_PYMDP:
        raise ModuleNotFoundError(PYMDP_INSTALL_HINT)


def _to_jax_pymdp_arrays(spec: StreamSpec) -> tuple[Any, Any, Any, Any]:
    """Convert numpy arrays to the (batched) JAX list-of-arrays format
    pymdp 1.0.1 expects.  Returns ``(A_list, B_list, C_list, D_list)``.
    """
    _require_pymdp()
    A_list = [jnp.asarray(spec.A, dtype=jnp.float32)[None, ...]]
    B_list = [jnp.asarray(spec.B, dtype=jnp.float32)[None, ...]]
    C_list = [jnp.asarray(spec.C, dtype=jnp.float32)[None, ...]]
    D_list = [jnp.asarray(spec.D, dtype=jnp.float32)[None, ...]]
    return A_list, B_list, C_list, D_list


def build_pymdp_agent(
    spec: StreamSpec,
    *,
    policy_len: int | None = None,
    gamma: float = 1.0,
    inference_algo: str | None = None,
    num_iter: int | None = None,
    action_selection: str | None = None,
    alpha: float | None = None,
    use_states_info_gain: bool | None = None,
    use_param_info_gain: bool | None = None,
) -> Any:
    """Materialise a :class:`pymdp.agent.Agent` from a :class:`StreamSpec`.

    Returns a pymdp 1.0.1 ``Agent`` (JAX-backed).  The caller drives
    inference via ``agent.infer_states(obs, prior)`` and
    ``agent.infer_policies(qs)``.

    All keyword arguments default to the central hyperparameters
    (:mod:`simulation.hyperparameters`) so a single edit there
    propagates to every Agent built by the harness. Pass an explicit
    value to override per call (e.g. for ablation experiments).

    Args:
        spec: Per-stream POMDP primitives (A, B, C, D).
        policy_len: pymdp policy lookahead horizon. Default
            :data:`PYMDP_AGENT_POLICY_LEN` = 1 (matches the manuscript's
            single-step coupled-policy derivation in §4).
        gamma: EFE precision (inverse temperature on expected free
            energy). Caller-supplied (matches ``CoupledEnsembleSpec.gamma``).
        inference_algo: ``"fpi"`` (default) or ``"vmp"``. Default
            :data:`PYMDP_AGENT_INFERENCE_ALGO`.
        num_iter: FPI iteration count. Default
            :data:`PYMDP_AGENT_NUM_ITER` = 32 (tighter than pymdp's
            internal default of 16 so per-stream marginals converge to
            the analytical layer's ``1e-12`` agreement tolerance).
        action_selection: ``"deterministic"`` or ``"stochastic"``. Default
            :data:`PYMDP_AGENT_ACTION_SELECTION` = ``"deterministic"``
            (matches §14 long-horizon deterministic-seeding contract).
        alpha: Inverse-temperature on action selection. Default
            :data:`PYMDP_AGENT_ALPHA` = 16.0.
        use_states_info_gain: Include state-info-gain in EFE. Default
            :data:`PYMDP_AGENT_USE_STATES_INFO_GAIN` = False (no
            state info to gain in the K=2 identity-likelihood toy).
        use_param_info_gain: Include parameter-info-gain in EFE.
            Default :data:`PYMDP_AGENT_USE_PARAM_INFO_GAIN` = False
            (A/B/D matrices fixed; no parameter learning).
    """
    _require_pymdp()
    from .hyperparameters import (
        PYMDP_AGENT_ACTION_SELECTION,
        PYMDP_AGENT_ALPHA,
        PYMDP_AGENT_INFERENCE_ALGO,
        PYMDP_AGENT_NUM_ITER,
        PYMDP_AGENT_POLICY_LEN,
        PYMDP_AGENT_USE_PARAM_INFO_GAIN,
        PYMDP_AGENT_USE_STATES_INFO_GAIN,
    )

    spec.validate()
    A, B, C, D = _to_jax_pymdp_arrays(spec)
    return Agent(
        A=A,
        B=B,
        C=C,
        D=D,
        batch_size=1,
        policy_len=int(PYMDP_AGENT_POLICY_LEN if policy_len is None else policy_len),
        gamma=gamma,
        inference_algo=str(PYMDP_AGENT_INFERENCE_ALGO if inference_algo is None else inference_algo),
        num_iter=int(PYMDP_AGENT_NUM_ITER if num_iter is None else num_iter),
        action_selection=str(PYMDP_AGENT_ACTION_SELECTION if action_selection is None else action_selection),
        alpha=float(PYMDP_AGENT_ALPHA if alpha is None else alpha),
        use_states_info_gain=bool(
            PYMDP_AGENT_USE_STATES_INFO_GAIN if use_states_info_gain is None else use_states_info_gain
        ),
        use_param_info_gain=bool(
            PYMDP_AGENT_USE_PARAM_INFO_GAIN if use_param_info_gain is None else use_param_info_gain
        ),
    )


def build_pymdp_agents(spec: CoupledEnsembleSpec, **kwargs: Any) -> list[Any]:
    """Build one pymdp Agent per stream in `spec`."""
    _require_pymdp()
    spec.validate()
    return [build_pymdp_agent(s, gamma=spec.gamma, **kwargs) for s in spec.streams]
