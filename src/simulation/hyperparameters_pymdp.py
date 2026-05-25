"""pymdp harness, multi-K, and long-horizon hyperparameters."""

from __future__ import annotations

from simulation.hyperparameters_grids import FigureGrid

#: 21-point λ-sweep on $[0, 4]$ that drives `simulate_pymdp.py`'s
#: total-correlation curve and the four sentinel-λ heatmaps.
PYMDP_SWEEP_LAMBDAS = FigureGrid(0.0, 4.0, 21, label="pymdp_sweep")

#: Deterministic rollout horizon (steps) and seed used by
#: `simulate_coupled_rollout` in the figure pipeline.
PYMDP_ROLLOUT_STEPS: int = 10
PYMDP_ROLLOUT_SEED: int = 0
PYMDP_ROLLOUT_LAMBDA: float = 2.0

#: Observations driving the static λ-sweep (both streams see "0").
PYMDP_SWEEP_OBSERVATIONS: tuple[int, ...] = (0, 0)

#: Coupling strength baked into the K=2 ensemble shipped to pymdp.
PYMDP_ENSEMBLE_COUPLING_LAMBDA: float = 1.0
PYMDP_ENSEMBLE_GAMMA: float = 1.0
PYMDP_ENSEMBLE_K: int = 2

#: Stream counts at which the K>2 multi-K experiment runs the full
#: ``free_energy_curve`` sweep. ``K=2`` is already covered by
#: :data:`PYMDP_ENSEMBLE_K`; this tuple drives the additional CSV / figure
#: outputs in :mod:`simulation.multi_k_experiments`.
MULTI_K_VALUES: tuple[int, ...] = (3, 4, 5)

#: 9-point λ-sweep on $[0, 4]$ used by the multi-K experiment. Sparser
#: than :data:`PYMDP_SWEEP_LAMBDAS` because the K=5 ensemble has a
#: 2^5 = 32-cell joint and a larger Agent construction cost; 9 grid
#: points is sufficient to resolve the monotone TC growth in λ.
MULTI_K_SWEEP_LAMBDAS = FigureGrid(0.0, 4.0, 9, label="multi_k_sweep")

#: Sentinel λ at which each multi-K experiment emits a single joint
#: heatmap snapshot for the manuscript figure.
MULTI_K_SENTINEL_LAMBDA: float = 2.0

#: Horizon (steps) of the long-horizon rollout used to verify habit
#: accumulation under the coupled dynamics.
LONG_HORIZON_STEPS: int = 100

#: Coupling strength of the long-horizon rollout. We pick a moderate
#: value so the marginals are non-trivially deformed by coupling
#: without being saturated.
LONG_HORIZON_LAMBDA: float = 2.0

#: Deterministic seed for the long-horizon rollout.
LONG_HORIZON_SEED: int = 0

#: Optional replicate seeds for robustness summaries. The canonical
#: manuscript figure uses :data:`LONG_HORIZON_SEED`; these additional
#: seeds let future scripts build quantile envelopes without changing
#: the main deterministic artifact.
LONG_HORIZON_REPLICATE_SEEDS: tuple[int, ...] = (0, 7, 13, 29, 41)

#: How many trailing steps to average over when computing the marginal
#: steady-state. The marginal at horizon - LONG_HORIZON_TAIL_WINDOW
#: should be close (within :data:`LONG_HORIZON_STEADY_STATE_TOL`) to
#: the time-averaged marginal across the trailing window.
LONG_HORIZON_TAIL_WINDOW: int = 20

#: Tolerance on the trailing-vs-tail KL divergence used to mark the
#: marginal as ``converged``. Set loosely because the long-horizon
#: rollout includes stochastic sampling of actions and observations:
#: the realized per-step marginal fluctuates around the steady-state
#: by a finite-sample KL of ~0.1 even after habit accumulation.
LONG_HORIZON_STEADY_STATE_TOL: float = 1.5e-1

#: Threshold probes for long-horizon replicate diagnostics.  The
#: canonical habit flag continues to use
#: :data:`LONG_HORIZON_STEADY_STATE_TOL`; these probes expose how
#: sensitive the pass rate is to stricter or looser tail-window KL
#: criteria.
LONG_HORIZON_DIAGNOSTIC_THRESHOLDS: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20, 0.25)
