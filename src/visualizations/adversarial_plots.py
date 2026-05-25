"""Adversarial-perturbation sweep plotting and orchestration.

Business logic for ``scripts/simulate_adversarial.py``. The script is a
thin wrapper that exposes ``DATA_DIR`` / ``FIG_DIR`` as patchable
module-level attributes; this module reads them through call arguments.

Runs the configured (epsilon, lambda)-grid on the K=2 Ising task
across all three adversary classes (rank-one worst case, uniform-random,
sparse single-cell). The harness is pure-numpy and fully deterministic
(the only randomness is the seeded uniform/sparse adversary
construction), so the sidecar is byte-identical across runs.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

from lean.bernoulli_toy import ising_coupling, ising_joint_posterior
from simulation import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).
from simulation.adversarial import (
    AdversarialObservable,
    empirical_lipschitz_constant,
    run_full_sweep,
)
from visualizations._io import _save_with_metadata
from visualizations.metadata import figure_metadata
from visualizations.setup import PUBLICATION_STYLE, deterministic_setup, ensure_outdir

_ADVERSARY_CLASSES = ("rank_one", "uniform_random", "sparse_single")
_CLASS_TITLES = {
    "rank_one": "(a) Worst-case rank-one",
    "uniform_random": "(b) Uniform-random",
    "sparse_single": "(c) Sparse single-cell",
}


def _plot_adversarial(
    *,
    observables: list[AdversarialObservable],
    bound_holds_fraction: float,
    max_bound_ratio: float,
    out_path: Path,
) -> Path:
    """Three-panel bound-ratio heatmap over the (epsilon, lambda>0) grid per class.

    Diverging colormap centered at ratio = 1: blue where the first-order
    Lipschitz bound holds (measured <= bound), red where it is exceeded.
    """
    style = PUBLICATION_STYLE
    epsilons = sorted({obs.scenario.epsilon for obs in observables})
    lambdas = sorted({obs.scenario.lambda_value for obs in observables if obs.scenario.lambda_value > 0.0})
    norm = TwoSlopeNorm(vcenter=1.0, vmin=0.0, vmax=max(max_bound_ratio, 1.0 + 1e-6))

    fig, axes = plt.subplots(1, 3, figsize=(16.0, 4.8), sharey=True, constrained_layout=True)
    im = None
    for ax, cls in zip(axes, _ADVERSARY_CLASSES, strict=True):
        grid = np.full((len(epsilons), len(lambdas)), np.nan)
        for obs in observables:
            if obs.scenario.adversary_class != cls or obs.scenario.lambda_value <= 0.0:
                continue
            i = epsilons.index(obs.scenario.epsilon)
            j = lambdas.index(obs.scenario.lambda_value)
            grid[i, j] = obs.bound_ratio
        im = ax.imshow(grid, cmap="RdBu_r", norm=norm, aspect="auto", origin="lower")
        ax.set_xticks(range(len(lambdas)))
        ax.set_xticklabels([f"{v:g}" for v in lambdas], fontsize=style.tick_size)
        ax.set_yticks(range(len(epsilons)))
        if ax is axes[0]:
            ax.set_yticklabels([f"$10^{{{np.log10(v):.1f}}}$" for v in epsilons], fontsize=style.label_size)
        else:
            ax.set_yticklabels([])
            ax.tick_params(labelleft=False)
        ax.set_xlabel("$\\lambda$", fontsize=style.label_size)
        ax.set_title(_CLASS_TITLES[cls], fontsize=style.title_size)
        ax.tick_params(labelsize=style.tick_size)
    axes[0].set_ylabel("$\\varepsilon$ ($L^\\infty$ budget)", fontsize=style.label_size)
    fig.suptitle("Adversarial bound-ratio sweep", fontsize=style.title_size, y=1.03)
    assert im is not None  # at least one panel was drawn
    cbar = fig.colorbar(im, ax=axes, fraction=0.024, pad=0.025, shrink=0.92)
    cbar.set_label("bound ratio", fontsize=style.label_size)
    cbar.ax.tick_params(labelsize=style.tick_size)

    return Path(
        _save_with_metadata(
            fig,
            out_path,
            metadata=figure_metadata(
                source_script="scripts/simulate_adversarial.py",
                source_function="_plot_adversarial",
                uncertainty_semantics="deterministic_grid",
                hyperparameters={
                    "epsilon_grid": list(H.ADVERSARIAL_EPSILON_GRID),
                    "lambda_grid": list(H.ADVERSARIAL_LAMBDA_GRID),
                },
                statistics={"bound_holds_fraction": bound_holds_fraction, "max_bound_ratio": max_bound_ratio},
            ),
        )
    )


def run(*, data_dir: Path, fig_dir: Path) -> int:
    """Run the adversarial sweep; emit JSON sidecar and PNG figure."""
    data_dir.mkdir(parents=True, exist_ok=True)
    summary_path = data_dir / "adversarial_sweep.json"

    coupling = np.asarray(ising_coupling((2, 2)), dtype=np.float64)

    def q_lambda_provider(lambda_value: float) -> np.ndarray:
        return np.asarray(ising_joint_posterior(lambda_value), dtype=np.float64)

    observables = run_full_sweep(
        q_lambda_provider=q_lambda_provider,
        coupling=coupling,
        seed=int(H.ADVERSARIAL_DEFAULT_SEED),
    )

    rows: list[dict[str, object]] = []
    finite_ratios: list[float] = []
    bound_holds_flags: list[bool] = []
    for obs in observables:
        ratio = float(obs.bound_ratio)
        rows.append(
            {
                "lambda": float(obs.scenario.lambda_value),
                "epsilon": float(obs.scenario.epsilon),
                "adversary_class": obs.scenario.adversary_class,
                "measured_kl_drift": float(obs.measured_kl_drift),
                "analytical_bound": float(obs.analytical_bound),
                "bound_ratio": ratio,
                "bound_holds": bool(obs.bound_holds),
            }
        )
        bound_holds_flags.append(bool(obs.bound_holds))
        if math.isfinite(ratio):
            finite_ratios.append(ratio)

    bound_holds_fraction = float(np.mean([1.0 if f else 0.0 for f in bound_holds_flags])) if bound_holds_flags else 0.0
    max_bound_ratio = float(max(finite_ratios)) if finite_ratios else 0.0
    empirical_lipschitz = float(empirical_lipschitz_constant(observables))

    deterministic_setup()
    ensure_outdir(fig_dir)
    fig_path = _plot_adversarial(
        observables=observables,
        bound_holds_fraction=bound_holds_fraction,
        max_bound_ratio=max_bound_ratio,
        out_path=fig_dir / "adversarial_sweep.png",
    )

    payload: dict[str, object] = {
        # scalar manuscript-variable mirror —
        "adversarial_num_scenarios": float(len(observables)),
        "adversarial_epsilon_grid_points": float(len(H.ADVERSARIAL_EPSILON_GRID)),
        "adversarial_lambda_grid_points": float(len(H.ADVERSARIAL_LAMBDA_GRID)),
        "adversarial_adversary_classes": 3.0,
        "adversarial_bound_holds_fraction": bound_holds_fraction,
        "adversarial_max_bound_ratio": max_bound_ratio,
        "adversarial_empirical_lipschitz": empirical_lipschitz,
        "adversarial_status": "ok",
        # full per-scenario observable rows (lists ignored by the scalar VAR loader) —
        "rows": rows,
    }
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    for p in (summary_path, fig_path):
        print(str(p))
    return 0


__all__ = ["_plot_adversarial", "run"]
