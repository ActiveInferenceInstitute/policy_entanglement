"""pymdp 1.0.1 :class:`Agent` adapters.
"""

from __future__ import annotations

from typing import Any

from specs import CoupledEnsembleSpec, StreamSpec

PYMDP_INSTALL_HINT = (
    "pymdp 1.0.1 is required for the POMDP simulation harness. "
    "Install with: `uv sync --group sim`"
)

try:
    import warnings

    import jax  # noqa: F401
    import jax.numpy as jnp

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
except Exception:  # pragma: no cover - covered by skip in tests
    _HAS_PYMDP = False
    Agent = None  # type: ignore[assignment]
    jnp = None  # type: ignore[assignment]


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
    policy_len: int = 1,
    gamma: float = 1.0,
    inference_algo: str = "fpi",
) -> Any:
    """Materialise a :class:`pymdp.agent.Agent` from a :class:`StreamSpec`.

    Returns a pymdp 1.0.1 ``Agent`` (JAX-backed).  The caller drives
    inference via ``agent.infer_states(obs, prior)`` and
    ``agent.infer_policies(qs)``.
    """
    _require_pymdp()
    spec.validate()
    A, B, C, D = _to_jax_pymdp_arrays(spec)
    return Agent(  # type: ignore[misc]
        A=A, B=B, C=C, D=D,
        batch_size=1,
        policy_len=policy_len,
        gamma=gamma,
        inference_algo=inference_algo,
    )


def build_pymdp_agents(spec: CoupledEnsembleSpec, **kwargs: Any) -> list[Any]:
    """Build one pymdp Agent per stream in `spec`."""
    _require_pymdp()
    spec.validate()
    return [build_pymdp_agent(s, gamma=spec.gamma, **kwargs) for s in spec.streams]
