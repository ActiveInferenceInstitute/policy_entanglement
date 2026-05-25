"""Adversarial-perturbation harness for §20 Q11 (cognitive integrity).

This module implements the shipped adversarial design from §20 Q11
(Open Questions) and §13 (Empirical Suite):

  Worst-case drift
  ----------------
  Delta q(epsilon, lambda) := sup_{||Delta J||_inf <= epsilon}
      D_KL( q_lambda || q_lambda^{J + Delta J} )

  Analytical bound (first-order Lipschitz)
  ---------------------------------------
  Delta q(epsilon, lambda) <= lambda * epsilon * Var_{q_lambda}(J)^{1/2}

  derived from the cumulant-generating function used in §20 Q1's convexity
  reformulation.

  Three adversary classes
  -----------------------
  (i)   analytical worst-case rank-one (leading eigenvector of coupling
        covariance under q_lambda)
  (ii)  uniformly random norm-epsilon perturbation
  (iii) sparse single-cell perturbation (one entry of J set to +/- epsilon)

  Falsification gate
  ------------------
  The robustness gate is: the *empirical Lipschitz constant* across the
  sweep matches the *analytical bound* to within the dashboard invariant
  tolerance. A regime in which the empirical Lipschitz constant *exceeds*
  the analytical bound is a regime in which the framework's robustness
  guarantee breaks, and must be surfaced at the dashboard layer rather
  than absorbed.

The harness takes the coupled posterior `q_lambda` and the coupling
potential `J` as numpy arrays, both produced by the existing
`src.lean.bernoulli_toy` and `src.simulation.*` machinery; it does not
reimplement pymdp inference.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import cast

import numpy as np

from .hyperparameters import (
    ADVERSARIAL_DEFAULT_SEED,
    ADVERSARIAL_EPSILON_GRID,
    ADVERSARIAL_LAMBDA_GRID,
)


@dataclass(frozen=True)
class AdversarialScenario:
    """A single adversarial-perturbation scenario.

    Attributes:
        lambda_value: Coupling parameter at which the perturbation is applied.
        epsilon: L^infty perturbation budget on Delta J.
        adversary_class: One of "rank_one", "uniform_random", "sparse_single".
        seed: Deterministic seed.
    """

    lambda_value: float
    epsilon: float
    adversary_class: str
    seed: int


@dataclass
class AdversarialObservable:
    """Per-scenario observables emitted by an adversarial sweep."""

    scenario: AdversarialScenario
    measured_kl_drift: float
    analytical_bound: float
    bound_ratio: float
    bound_holds: bool


def coupling_covariance(q_lambda: np.ndarray, coupling: np.ndarray) -> np.ndarray:
    """Coupling covariance Cov_{q_lambda}(J_ij, J_kl) flattened to matrix form.

    For a joint posterior `q_lambda` on the joint action space of K=2 with
    shape (n1, n2) and a coupling potential `J` of the same shape, returns
    the covariance of the indicator-vector representation under q_lambda.
    """
    if q_lambda.shape != coupling.shape:
        raise ValueError(f"shapes differ: q_lambda={q_lambda.shape} J={coupling.shape}")
    flat_q = q_lambda.flatten()
    flat_j = coupling.flatten()
    mean_j = float(np.sum(flat_q * flat_j))
    centered = flat_j - mean_j
    covariance_matrix = np.outer(flat_q * centered, centered)
    return covariance_matrix


def variance_under_q(q_lambda: np.ndarray, coupling: np.ndarray) -> float:
    """Scalar Var_{q_lambda}(J) = E_q[J^2] - (E_q[J])^2."""
    if q_lambda.shape != coupling.shape:
        raise ValueError(f"shapes differ: q_lambda={q_lambda.shape} J={coupling.shape}")
    flat_q = q_lambda.flatten()
    flat_j = coupling.flatten()
    mean_j = float(np.sum(flat_q * flat_j))
    second_moment = float(np.sum(flat_q * flat_j**2))
    return second_moment - mean_j**2


def analytical_lipschitz_bound(
    lambda_value: float, epsilon: float, q_lambda: np.ndarray, coupling: np.ndarray
) -> float:
    """First-order Lipschitz bound on Delta q(epsilon, lambda).

    Returns lambda * epsilon * Var_{q_lambda}(J)^{1/2}, the closed-form
    bound derived from the cumulant-generating function in §20 Q1.
    """
    variance = variance_under_q(q_lambda, coupling)
    return float(lambda_value) * float(epsilon) * float(np.sqrt(max(variance, 0.0)))


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """KL(p || q); both arrays sum to 1 and are non-negative."""
    if p.shape != q.shape:
        raise ValueError(f"shapes differ: p={p.shape} q={q.shape}")
    p_clipped = np.clip(p, 1e-300, 1.0)
    q_clipped = np.clip(q, 1e-300, 1.0)
    return float(np.sum(p * (np.log(p_clipped) - np.log(q_clipped))))


def rank_one_adversary(q_lambda: np.ndarray, coupling: np.ndarray, epsilon: float) -> np.ndarray:
    """Construct the worst-case rank-one adversary aligned with leading covariance eigenvector.

    Returns a Delta J of shape J.shape with ||Delta J||_inf == epsilon.
    """
    covariance_matrix = coupling_covariance(q_lambda, coupling)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    leading_eigenvector = eigenvectors[:, np.argmax(np.abs(eigenvalues))]
    reshaped = leading_eigenvector.reshape(coupling.shape)
    max_abs = float(np.max(np.abs(reshaped)))
    if max_abs <= 0.0:
        return np.zeros_like(coupling)
    return epsilon * reshaped / max_abs


def uniform_random_adversary(coupling_shape: tuple[int, ...], epsilon: float, seed: int) -> np.ndarray:
    """Uniformly random sign-pattern adversary at norm exactly epsilon."""
    rng = np.random.default_rng(seed)
    delta = rng.choice(np.array([-1.0, 1.0]), size=coupling_shape) * epsilon
    return delta.astype(np.float64)


def sparse_single_adversary(coupling_shape: tuple[int, ...], epsilon: float, seed: int) -> np.ndarray:
    """Sparse single-cell adversary: one entry set to +/- epsilon."""
    rng = np.random.default_rng(seed)
    delta = np.zeros(coupling_shape, dtype=np.float64)
    flat_index = int(rng.integers(0, int(np.prod(coupling_shape))))
    coords = np.unravel_index(flat_index, coupling_shape)
    sign = float(rng.choice(np.array([-1.0, 1.0])))
    delta[coords] = sign * epsilon
    return delta


def build_adversary(scenario: AdversarialScenario, q_lambda: np.ndarray, coupling: np.ndarray) -> np.ndarray:
    """Construct the Delta J adversary for a scenario."""
    if scenario.adversary_class == "rank_one":
        return rank_one_adversary(q_lambda, coupling, scenario.epsilon)
    if scenario.adversary_class == "uniform_random":
        return uniform_random_adversary(coupling.shape, scenario.epsilon, scenario.seed)
    if scenario.adversary_class == "sparse_single":
        return sparse_single_adversary(coupling.shape, scenario.epsilon, scenario.seed)
    raise ValueError(
        f"unknown adversary_class={scenario.adversary_class!r}; "
        "expected one of: rank_one, uniform_random, sparse_single"
    )


def perturbed_posterior(
    q_lambda: np.ndarray, coupling: np.ndarray, delta_j: np.ndarray, lambda_value: float
) -> np.ndarray:
    """Compute q_lambda^{J + Delta J} via reweighting.

    Uses the closed-form relationship q_lambda^{J+dJ}(pi) propto
    q_lambda(pi) * exp(lambda * dJ(pi)), so the perturbed posterior is a
    geometric tilt of q_lambda by lambda * delta_J.
    """
    if q_lambda.shape != coupling.shape or coupling.shape != delta_j.shape:
        raise ValueError(f"shapes differ: q_lambda={q_lambda.shape} J={coupling.shape} delta_J={delta_j.shape}")
    log_tilt = float(lambda_value) * delta_j
    unnormalised = q_lambda * np.exp(log_tilt - np.max(log_tilt))
    total = float(unnormalised.sum())
    if total <= 0.0:
        return cast(np.ndarray, np.asarray(q_lambda, dtype=np.float64).copy())
    return np.asarray(unnormalised / total, dtype=np.float64)


def measure_drift(scenario: AdversarialScenario, q_lambda: np.ndarray, coupling: np.ndarray) -> AdversarialObservable:
    """Run a single adversarial scenario and return measured drift + bound."""
    delta_j = build_adversary(scenario, q_lambda, coupling)
    q_perturbed = perturbed_posterior(q_lambda, coupling, delta_j, scenario.lambda_value)
    measured_kl = kl_divergence(q_lambda, q_perturbed)
    analytical = analytical_lipschitz_bound(scenario.lambda_value, scenario.epsilon, q_lambda, coupling)
    ratio = measured_kl / analytical if analytical > 0.0 else float("inf")
    return AdversarialObservable(
        scenario=scenario,
        measured_kl_drift=measured_kl,
        analytical_bound=analytical,
        bound_ratio=ratio,
        bound_holds=measured_kl <= analytical + 1e-12,
    )


def default_epsilon_grid() -> list[float]:
    """Pre-registered epsilon budget grid (log-spaced 1e-3 … 1e0).

    Single source of truth at
    :data:`simulation.hyperparameters.ADVERSARIAL_EPSILON_GRID`.
    """
    return list(ADVERSARIAL_EPSILON_GRID)


def default_lambda_grid() -> list[float]:
    """Pre-registered lambda grid (matches the revertibility sweep).

    Single source of truth at
    :data:`simulation.hyperparameters.ADVERSARIAL_LAMBDA_GRID`.
    """
    return list(ADVERSARIAL_LAMBDA_GRID)


def default_adversarial_scenarios(
    seed: int = ADVERSARIAL_DEFAULT_SEED,
) -> Iterable[AdversarialScenario]:
    """Pre-registered (lambda, epsilon, adversary_class) scenario grid."""
    classes = ("rank_one", "uniform_random", "sparse_single")
    counter = 0
    for lambda_value in default_lambda_grid():
        for epsilon in default_epsilon_grid():
            for adversary_class in classes:
                yield AdversarialScenario(
                    lambda_value=float(lambda_value),
                    epsilon=float(epsilon),
                    adversary_class=adversary_class,
                    seed=seed + counter,
                )
                counter += 1


def run_full_sweep(
    q_lambda_provider: Callable[[float], np.ndarray],
    coupling: np.ndarray,
    seed: int = ADVERSARIAL_DEFAULT_SEED,
) -> list[AdversarialObservable]:
    """Run the full configured adversarial sweep.

    Args:
        q_lambda_provider: Callable mapping lambda_value -> q_lambda joint
            posterior of the same shape as J. Provided by the caller from
            the existing bernoulli_toy or pymdp harness.
        coupling: Coupling potential array, shape (n1, n2) for K=2 Ising.
        seed: Deterministic base seed.

    Returns:
        List of AdversarialObservable, one per scenario.
    """
    observables: list[AdversarialObservable] = []
    for scenario in default_adversarial_scenarios(seed=seed):
        q_lambda = q_lambda_provider(scenario.lambda_value)
        observable = measure_drift(scenario, q_lambda, coupling)
        observables.append(observable)
    return observables


def empirical_lipschitz_constant(observables: list[AdversarialObservable]) -> float:
    """Empirical Lipschitz constant = max over scenarios of measured / (lambda * epsilon).

    Compared against the analytical bound's coefficient
    `Var_{q_lambda}(J)^{1/2}` to detect bound violations.
    """
    if not observables:
        return 0.0
    ratios: list[float] = []
    for observable in observables:
        denominator = float(observable.scenario.lambda_value) * float(observable.scenario.epsilon)
        if denominator > 0.0:
            ratios.append(observable.measured_kl_drift / denominator)
    return float(max(ratios)) if ratios else 0.0
