"""Branching-Time Active Inference (BTAI) baseline for head-to-head comparison.

This module implements a Branching-Time AIF agent that operates on the same
finite POMDP task family as the lambda-coupled harness in this project, so the
two can be compared at matched compute against the analytic closed-form
Bernoulli posterior of `src.lean.bernoulli_toy`.

BTAI [@champion-2022] expands the policy tree under expected free energy (EFE)
and prunes it with Monte Carlo tree search (MCTS). The agent's per-step joint
policy posterior is recovered from the visitation counts of the MCTS root,
normalized over the joint action space.

Design follows the shipped comparison protocol in §13 (Empirical Suite):

  Observables compared
  --------------------
  (i)   per-step joint policy posterior q(pi^1, pi^2)
  (ii)  total correlation I(q) over the lambda sweep
  (iii) wall-clock cost

  Budgets swept
  -------------
  B_MCTS in {1e2, 1e3, 1e4}

  Predictions
  -----------
  - BTAI converges to the analytic exact posterior as B_MCTS -> infty.
  - The lambda-coupled harness reaches the same posterior at fixed
    sweep-independent cost.
  - Falsification gate: measured BTAI sample-complexity exponent < 1 against
    B_MCTS would indicate BTAI dominates at low budgets.

The BTAI agent is implemented against the standard `pymdp.agent.Agent`
interface so it shares prior preferences `C`, observation likelihood `A`, and
transition tensor `B` with the coupled harness. No reimplementation of pymdp
mathematics; per-stream inference uses the bare pymdp engine and BTAI's MCTS
loops over expected-free-energy estimates of the joint policy.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .specs import CoupledEnsembleSpec

from .hyperparameters import (
    BTAI_DEFAULT_BUDGETS,
    BTAI_UCB_EXPLORATION,
    LONG_HORIZON_STEPS,
    PYMDP_ROLLOUT_SEED,
    PYMDP_ROLLOUT_STEPS,
)


@dataclass(frozen=True)
class BTAIScenario:
    """A single BTAI comparison scenario.

    Attributes:
        horizon: Branching horizon T (matches the coupled rollout's T).
        mcts_budget: MCTS expansion budget B_MCTS per decision step.
        seed: Deterministic seed for the MCTS UCB tie-breaker.
        lambda_value: Coupling parameter of the reference lambda-harness run
            this BTAI scenario is being compared against. Used only for
            bookkeeping; BTAI does not consume lambda.
    """

    horizon: int
    mcts_budget: int
    seed: int
    lambda_value: float


@dataclass(frozen=True)
class BTAIObservable:
    """Per-step observables emitted by a BTAI run.

    Attributes:
        joint_posterior: q(pi^1, pi^2) shape (|Pi^1|, |Pi^2|) at the step.
        total_correlation: Total correlation I(q) in nats at the step.
        wall_clock_seconds: Cumulative wall-clock cost up to this step.
        step_index: Zero-based step index within the rollout.
        kl_against_reference: KL(joint_posterior || reference_posterior) if a
            reference posterior was supplied to `run_btai_scenario`; ``None``
            when no reference posterior was provided.
    """

    joint_posterior: np.ndarray
    total_correlation: float
    wall_clock_seconds: float
    step_index: int
    kl_against_reference: float | None = None


@dataclass
class BTAIRunResult:
    """Aggregate result of a single BTAI scenario run."""

    scenario: BTAIScenario
    per_step: list[BTAIObservable] = field(default_factory=list)
    final_posterior: np.ndarray | None = None
    final_total_correlation: float | None = None
    wall_clock_total_seconds: float | None = None


@dataclass
class BTAITreeNode:
    """One node of the BTAI search tree (joint action subtree)."""

    visits: int = 0
    value_estimate: float = 0.0
    children: dict[tuple[int, ...], BTAITreeNode] = field(default_factory=dict)
    expected_free_energy: float = 0.0


def joint_marginals(joint: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute per-stream marginals of a joint posterior on two streams."""
    if joint.ndim != 2:
        raise ValueError(f"joint must be 2-D for K=2 streams, got ndim={joint.ndim}")
    return joint.sum(axis=1), joint.sum(axis=0)


def total_correlation(joint: np.ndarray) -> float:
    """Total correlation I(q) = sum_k H(q^k) - H(q) for a 2-stream joint."""
    if joint.ndim != 2:
        raise ValueError(f"joint must be 2-D for K=2 streams, got ndim={joint.ndim}")
    marginal_1, marginal_2 = joint_marginals(joint)

    def shannon_entropy(probabilities: np.ndarray) -> float:
        clipped = np.clip(probabilities, 1e-300, 1.0)
        return float(-np.sum(probabilities * np.log(clipped)))

    return shannon_entropy(marginal_1) + shannon_entropy(marginal_2) - shannon_entropy(joint)


def ucb_score(parent_visits: int, child: BTAITreeNode, exploration: float) -> float:
    """UCB1 score for MCTS node selection.

    Following Champion (2022), expected free energy enters as the value
    estimate (lower EFE -> higher preference), so we negate it.
    """
    if child.visits == 0:
        return float("inf")
    exploitation = -child.expected_free_energy
    exploration_bonus = exploration * math.sqrt(math.log(max(parent_visits, 1)) / child.visits)
    return exploitation + exploration_bonus


def _expand_node(
    node: BTAITreeNode,
    joint_action_space: tuple[int, ...],
    seed_rng: np.random.Generator,
) -> tuple[int, ...]:
    """Add one unvisited child to a tree node and return the action chosen."""
    untried = [action for action in _enumerate_joint_actions(joint_action_space) if action not in node.children]
    if not untried:
        return _select_existing_child(node, seed_rng)
    chosen = untried[int(seed_rng.integers(0, len(untried)))]
    node.children[chosen] = BTAITreeNode()
    return chosen


def _select_existing_child(node: BTAITreeNode, seed_rng: np.random.Generator) -> tuple[int, ...]:
    """Select the existing child with the best UCB score, ties broken by RNG."""
    best_score = -float("inf")
    best_actions: list[tuple[int, ...]] = []
    for action, child in node.children.items():
        score = ucb_score(node.visits, child, exploration=BTAI_UCB_EXPLORATION)
        if score > best_score:
            best_score = score
            best_actions = [action]
        elif score == best_score:
            best_actions.append(action)
    return best_actions[int(seed_rng.integers(0, len(best_actions)))]


def _enumerate_joint_actions(joint_action_space: tuple[int, ...]) -> Iterable[tuple[int, ...]]:
    """Enumerate every joint action across the product space of K streams."""
    if not joint_action_space:
        return [()]
    sizes = list(joint_action_space)
    result: list[tuple[int, ...]] = [()]
    for size in sizes:
        result = [tuple(list(prefix) + [a]) for prefix in result for a in range(size)]
    return result


def run_btai_scenario(
    scenario: BTAIScenario,
    joint_action_space: tuple[int, ...],
    expected_free_energy_fn: Callable[[tuple[int, ...]], float],
    reference_posterior: np.ndarray | None = None,
) -> BTAIRunResult:
    """Run one BTAI scenario and return per-step observables.

    Args:
        scenario: Scenario configuration (horizon, MCTS budget, seed, lambda).
        joint_action_space: Per-stream action support sizes,
            e.g. (2, 2) for the K=2 Ising task.
        expected_free_energy_fn: Function returning EFE for a joint action
            tuple. Provided by the caller (pymdp-grounded estimator).
        reference_posterior: Optional reference posterior for scoring; when
            provided, the per-step observables include KL against this
            reference posterior. Shape must match the joint action space.

    Returns:
        A `BTAIRunResult` aggregating per-step observables. The final
        posterior is constructed from the MCTS root's visitation counts.

    The implementation is deterministic given `scenario.seed`; the MCTS
    UCB tie-breaker and the expansion order both consume RNG draws from
    the same seeded generator.
    """
    rng = np.random.default_rng(scenario.seed)
    start_time = time.monotonic()
    per_step: list[BTAIObservable] = []

    for step_index in range(scenario.horizon):
        root = BTAITreeNode()
        for _ in range(scenario.mcts_budget):
            action = _expand_node(root, joint_action_space, rng)
            child = root.children[action]
            efe = expected_free_energy_fn(action)
            child.expected_free_energy = efe
            child.visits += 1
            child.value_estimate = -efe
            root.visits += 1

        joint_shape = joint_action_space
        joint_counts = np.zeros(joint_shape, dtype=np.float64)
        for action, child in root.children.items():
            joint_counts[action] = float(child.visits)

        total_count = float(joint_counts.sum())
        if total_count > 0.0:
            joint_posterior = joint_counts / total_count
        else:
            joint_posterior = np.full(joint_shape, 1.0 / float(np.prod(joint_shape)))

        wall_clock_seconds = time.monotonic() - start_time
        if reference_posterior is not None:
            if reference_posterior.shape != joint_posterior.shape:
                raise ValueError(
                    f"reference_posterior shape {reference_posterior.shape} "
                    f"does not match the joint action space shape {joint_posterior.shape}"
                )
            kl_against_ref: float | None = kl_against_reference(joint_posterior, reference_posterior)
        else:
            kl_against_ref = None
        per_step.append(
            BTAIObservable(
                joint_posterior=joint_posterior,
                total_correlation=total_correlation(joint_posterior),
                wall_clock_seconds=wall_clock_seconds,
                step_index=step_index,
                kl_against_reference=kl_against_ref,
            )
        )

    final_observable = per_step[-1] if per_step else None
    return BTAIRunResult(
        scenario=scenario,
        per_step=per_step,
        final_posterior=None if final_observable is None else final_observable.joint_posterior,
        final_total_correlation=None if final_observable is None else final_observable.total_correlation,
        wall_clock_total_seconds=None if final_observable is None else final_observable.wall_clock_seconds,
    )


def kl_against_reference(measured: np.ndarray, reference: np.ndarray) -> float:
    """KL(measured || reference); both must be non-negative and sum to 1."""
    if measured.shape != reference.shape:
        raise ValueError(f"shapes differ: measured={measured.shape} reference={reference.shape}")
    measured_clipped = np.clip(measured, 1e-300, 1.0)
    reference_clipped = np.clip(reference, 1e-300, 1.0)
    return float(np.sum(measured * (np.log(measured_clipped) - np.log(reference_clipped))))


def sample_complexity_exponent(budgets: list[int], kl_curve: list[float]) -> float:
    """Fit KL(B) ~ B^{-exponent} on a log-log plot; returns the exponent.

    Returns the negative slope of log(KL) versus log(B); a value of 1 is the
    standard MCTS sample-complexity scaling, < 1 is faster, > 1 is slower.
    """
    if len(budgets) != len(kl_curve) or len(budgets) < 2:
        raise ValueError("need >= 2 budget/kl pairs to fit an exponent")
    log_budgets = np.log(np.asarray(budgets, dtype=np.float64))
    log_kl = np.log(np.clip(np.asarray(kl_curve, dtype=np.float64), 1e-300, None))
    slope, _intercept = np.polyfit(log_budgets, log_kl, 1)
    return float(-slope)


def default_mcts_budgets() -> list[int]:
    """Pre-registered MCTS budget grid.

    Reads from :data:`simulation.hyperparameters.BTAI_DEFAULT_BUDGETS`
    so a single source-of-truth edit propagates to every caller and to
    the figure / report VAR-token substitutions downstream.
    """
    return list(BTAI_DEFAULT_BUDGETS)


def default_btai_scenarios(lambda_value: float = 1.0) -> list[BTAIScenario]:
    """Pre-registered BTAI comparison scenarios across the budget grid.

    Reads the standard rollout horizons from the project hyperparameters
    so a single change to `PYMDP_ROLLOUT_STEPS` or `LONG_HORIZON_STEPS`
    propagates here.
    """
    horizons = (int(PYMDP_ROLLOUT_STEPS), int(LONG_HORIZON_STEPS))
    seed = int(PYMDP_ROLLOUT_SEED)
    return [
        BTAIScenario(
            horizon=horizon,
            mcts_budget=budget,
            seed=seed,
            lambda_value=lambda_value,
        )
        for horizon in horizons
        for budget in default_mcts_budgets()
    ]


def pymdp_grounded_efe_fn(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
) -> Callable[[tuple[int, ...]], float]:
    """Build a joint-action EFE function from real ``pymdp.agent.Agent`` per-stream EFEs.

    Args:
        spec: A :class:`simulation.specs.CoupledEnsembleSpec` naming the
            per-stream POMDP primitives the BTAI baseline is run
            against. The same spec object is used by
            :func:`simulation.inference.per_stream_efe` to drive real
            pymdp 1.0.1 inference once per stream.
        observations: Per-stream observations passed into pymdp's
            policy-posterior step (length ``num_streams``).

    Returns:
        A callable ``efe(joint_action) -> float`` that BTAI's MCTS
        expansion can consume. The joint EFE is the sum of per-stream
        EFEs at the indicated control indices — the standard EFE
        composition under the project's per-stream factorized generative
        model. No pymdp re-implementation; the per-stream EFEs come
        straight from
        :func:`simulation.inference.per_stream_efe`, which calls real
        ``pymdp.agent.Agent``.
    """
    # Late import: keeps the static `simulation.btai_baseline` module
    # graph free of the pymdp-requiring `inference` module — the
    # `expected_free_energy_fn` argument in `run_btai_scenario` is
    # deliberately external so callers without pymdp installed can pass
    # a hand-built EFE.  Callers with pymdp use this helper to wire the
    # real per-stream EFE through.
    from .inference import per_stream_efe

    per_stream = per_stream_efe(spec, observations)

    def joint_efe(joint_action: tuple[int, ...]) -> float:
        if len(joint_action) != len(per_stream):
            raise ValueError(f"joint_action length {len(joint_action)} does not match stream count {len(per_stream)}")
        return float(sum(per_stream[k][a] for k, a in enumerate(joint_action)))

    return joint_efe
