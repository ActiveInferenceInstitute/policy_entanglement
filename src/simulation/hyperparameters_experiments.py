"""Revertibility, agent, BTAI, and adversarial experiment hyperparameters."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Revertibility / m-projection (T3)
# ---------------------------------------------------------------------------

#: λ grid on which :mod:`simulation.revertibility` evaluates the
#: m-projection witness. Five sentinel values: zero baseline, three
#: interior probes, and a saturating high-coupling probe.
REVERTIBILITY_LAMBDAS: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0, 4.0)

#: Floating-point tolerance for the "m-projection marginals match the
#: original posterior's marginals" identity. This is an exact algebraic
#: equality (marginals are linear in the joint), so the tolerance is
#: a floating-point round-off budget rather than a modeling slack.
REVERTIBILITY_TOLERANCE: float = 1e-12

#: Tolerance for the ``KL(q_λ ‖ m(q_λ)) == I(q_λ)`` identity. Slightly
#: looser than :data:`REVERTIBILITY_TOLERANCE` because both sides of
#: the equation involve sums of safe-log terms.
REVERTIBILITY_KL_IDENTITY_TOLERANCE: float = 1e-9

# ---------------------------------------------------------------------------
# pymdp 1.0.1 Agent construction knobs
# ---------------------------------------------------------------------------

#: Default policy lookahead horizon passed to ``pymdp.agent.Agent``. A
#: value of 1 corresponds to the single-step posterior on which the
#: manuscript's coupled-policy derivation is anchored (§4); larger values
#: extend pymdp's own internal lookahead — orthogonal to the framework's
#: λ-coupling layer.
PYMDP_AGENT_POLICY_LEN: int = 1

#: Inference algorithm. ``"fpi"`` (fixed-point iteration) is pymdp's
#: deterministic default and the only algorithm currently exercised by
#: this harness; ``"vmp"`` (variational message passing) is available for
#: alternative experimentation but not validated against the §13 numeric
#: witnesses.
PYMDP_AGENT_INFERENCE_ALGO: str = "fpi"

#: FPI iteration count. pymdp's default is 16; we lift to 32 so the
#: per-stream posterior is converged to a tighter tolerance, matching
#: the analytical layer's ``1e-12`` agreement floor on
#: ``PYMDP_MARGINAL_AGREEMENT_TOLERANCE``.
PYMDP_AGENT_NUM_ITER: int = 32

#: Action-selection mode for ``Agent.sample_action``. ``"deterministic"``
#: pins the rollout to the argmax-policy at every step (the manuscript's
#: §14 long-horizon trace claims deterministic seeding; the alternative
#: ``"stochastic"`` is documented but not currently exercised).
PYMDP_AGENT_ACTION_SELECTION: str = "deterministic"

#: Inverse-temperature on the action-selection policy. Higher values
#: sharpen toward the argmax; the default 16 matches pymdp's library
#: default and keeps the argmax-policy effectively deterministic.
PYMDP_AGENT_ALPHA: float = 16.0

#: Whether to include the *states* info-gain term in EFE. Disabled by
#: default in the K=2 Ising setting because the observation likelihood
#: is identity (no state information to gain).
PYMDP_AGENT_USE_STATES_INFO_GAIN: bool = False

#: Whether to include the *parameter* info-gain term in EFE. Off by
#: default because the K=2 Ising A/B/D matrices are fixed (no parameter
#: learning).
PYMDP_AGENT_USE_PARAM_INFO_GAIN: bool = False

# ---------------------------------------------------------------------------
# BTAI baseline (shipped §13 empirical harness) — central knobs
# ---------------------------------------------------------------------------

#: Pre-registered MCTS budgets used by the BTAI head-to-head baseline.
#: Log-spaced over three orders of magnitude (10², 10³, 10⁴) — the same
#: schedule embedded in the §13 shipped worked-run design.
BTAI_DEFAULT_BUDGETS: tuple[int, ...] = (100, 1000, 10000)

#: UCB1 exploration constant for the BTAI MCTS tree policy.
#: ``sqrt(2)`` is the classical UCB1 constant; it controls the trade-off
#: between exploring novel branches and exploiting the lowest-EFE arms,
#: and is the only knob in MCTS that materially changes the empirical
#: sample-complexity exponent the falsification gate measures.
BTAI_UCB_EXPLORATION: float = 2.0**0.5

#: Representative coupled operating point whose closed-form K=2 Bernoulli
#: posterior is the analytic reference the BTAI visitation posterior is
#: scored against. Matches the canonical sweep's unit-coupling point.
BTAI_REFERENCE_LAMBDA: float = 1.0

#: Decision horizon for the BTAI worked run. A single decision step
#: yields the cleanest per-step joint policy posterior — the observable
#: the head-to-head comparison is about.
BTAI_HORIZON: int = 1

#: Ising-ensemble knobs for the BTAI pymdp-grounded EFE landscape (the
#: K=2 unit-coupling reference ensemble). ``gamma`` is intentionally
#: shared with :data:`PYMDP_ENSEMBLE_GAMMA` so the BTAI run cannot
#: silently drift from the canonical ensemble precision.
BTAI_ENSEMBLE_COUPLING_AMPLITUDE: float = 1.0
BTAI_ENSEMBLE_PREFERENCE_STRENGTH: float = 1.0
BTAI_NUM_STREAMS: int = 2

# ---------------------------------------------------------------------------
# Adversarial-perturbation harness (§20 Q11) — central knobs
# ---------------------------------------------------------------------------

#: Pre-registered L^∞ perturbation budgets for the adversarial sweep.
#: Log-spaced 10⁻³ … 10⁰ over seven half-decade steps.
ADVERSARIAL_EPSILON_GRID: tuple[float, ...] = tuple(10.0 ** (-3.0 + 0.5 * step) for step in range(7))

#: Pre-registered λ values for the adversarial sweep. Matches the
#: revertibility sweep so the two harnesses can be cross-compared at
#: the same grid points.
ADVERSARIAL_LAMBDA_GRID: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0, 4.0)

#: Default base seed for the adversarial sweep — used to initialize per
#: scenario the uniform and sparse adversaries; the analytical rank-one
#: adversary is deterministic given (q, J).
ADVERSARIAL_DEFAULT_SEED: int = 12345
